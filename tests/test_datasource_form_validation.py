"""Tests for validate_config_fields() in datasource_form.py."""

from databao_context_engine.pluginlib.config import (
    ConfigPropertyDefinition,
    ConfigSinglePropertyDefinition,
    ConfigUnionPropertyDefinition,
)

from databao_cli.features.ui.components.datasource_form import validate_config_fields


def _single(
    key: str,
    *,
    required: bool = False,
    property_type: type = str,
    nested: list[ConfigPropertyDefinition] | None = None,
) -> ConfigSinglePropertyDefinition:
    return ConfigSinglePropertyDefinition(
        property_key=key,
        required=required,
        property_type=property_type,
        nested_properties=nested,
    )


def _fields(*props: ConfigPropertyDefinition) -> list[ConfigPropertyDefinition]:
    """Helper to build a correctly-typed field list."""
    return list(props)


class TestIntVsPortValidation:
    """Port range check only applies to port-named fields, not all int fields."""

    def test_non_port_int_field_accepts_large_number(self) -> None:
        fields = _fields(_single("timeout", property_type=int))
        errors = validate_config_fields(fields, {"timeout": "120000"})
        assert errors == []

    def test_non_port_int_field_rejects_non_numeric(self) -> None:
        fields = _fields(_single("retries", property_type=int))
        errors = validate_config_fields(fields, {"retries": "abc"})
        assert len(errors) == 1
        assert "integer" in errors[0].lower()

    def test_port_field_rejects_out_of_range(self) -> None:
        fields = _fields(_single("port", property_type=int))
        errors = validate_config_fields(fields, {"port": "99999"})
        assert len(errors) == 1
        assert "between" in errors[0].lower()

    def test_port_field_accepts_valid_port(self) -> None:
        fields = _fields(_single("port", property_type=int))
        errors = validate_config_fields(fields, {"port": "5432"})
        assert errors == []


class TestSkipTopLevelKeysScope:
    """SKIP_TOP_LEVEL_KEYS should only apply at the top level."""

    def test_top_level_type_is_skipped(self) -> None:
        fields = _fields(_single("type", required=True), _single("host", required=True))
        errors = validate_config_fields(fields, {"host": ""})
        # "type" should be skipped, only "host" error expected
        assert len(errors) == 1
        assert "host" in errors[0]

    def test_nested_name_field_is_validated(self) -> None:
        fields = _fields(
            _single(
                "connection",
                nested=[_single("name", required=True)],
            ),
        )
        errors = validate_config_fields(fields, {"connection": {"name": ""}})
        assert len(errors) == 1
        assert "connection.name" in errors[0]


class TestUnionPropertyValidation:
    """Union properties should be validated recursively."""

    def test_union_required_field_missing(self) -> None:
        class VariantA:
            pass

        union = ConfigUnionPropertyDefinition(
            property_key="auth",
            types=(VariantA,),
            type_properties={
                VariantA: [_single("username", required=True)],
            },
        )
        fields = _fields(union)
        errors = validate_config_fields(fields, {"auth": {"type": "VariantA", "username": ""}})
        assert len(errors) == 1
        assert "username" in errors[0]

    def test_union_valid_fields_pass(self) -> None:
        class VariantA:
            pass

        union = ConfigUnionPropertyDefinition(
            property_key="auth",
            types=(VariantA,),
            type_properties={
                VariantA: [_single("username", required=True)],
            },
        )
        fields = _fields(union)
        errors = validate_config_fields(fields, {"auth": {"type": "VariantA", "username": "admin"}})
        assert errors == []


class TestHostValidation:
    """Host field validation within config fields."""

    def test_hostname_with_port_rejected(self) -> None:
        fields = _fields(_single("host"))
        errors = validate_config_fields(fields, {"host": "db.example.com:5432"})
        assert len(errors) == 1
        assert "host" in errors[0]
