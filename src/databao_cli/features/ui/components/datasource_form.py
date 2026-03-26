"""Dynamic form renderer for DCE datasource config properties.

Renders Streamlit form fields from ConfigPropertyDefinition objects.
No datasource-specific logic is hardcoded -- all rendering is driven
by the property definitions provided by DCE plugins.
"""

from typing import Any

import streamlit as st
from databao_context_engine.pluginlib.config import (
    ConfigPropertyDefinition,
    ConfigSinglePropertyDefinition,
    ConfigUnionPropertyDefinition,
)

SKIP_TOP_LEVEL_KEYS = {"type", "name"}


def get_missing_required_fields(
    config_fields: list[ConfigPropertyDefinition],
    values: dict[str, Any],
) -> list[str]:
    """Return labels of required fields that are empty in *values*.

    Only checks top-level single (leaf) properties that are marked as
    required. Skips the ``type`` and ``name`` keys (handled separately).
    """
    missing: list[str] = []
    for prop in config_fields:
        if prop.property_key in SKIP_TOP_LEVEL_KEYS:
            continue
        if isinstance(prop, ConfigSinglePropertyDefinition) and not prop.nested_properties and prop.required:
            val = values.get(prop.property_key)
            if val is None or not str(val).strip():
                missing.append(prop.property_key)
    return missing


def render_datasource_config_form(
    config_fields: list[ConfigPropertyDefinition],
    existing_values: dict[str, Any] | None = None,
    key_prefix: str = "",
    is_top_level: bool = True,
    disabled: bool = False,
) -> dict[str, Any]:
    """Render form fields for a datasource config and return collected values.

    Args:
        config_fields: List of property definitions from DCE plugin.
        existing_values: Existing config dict to pre-fill fields (for editing).
        key_prefix: Prefix for Streamlit widget keys (for uniqueness).
        is_top_level: Whether this is the top-level call (to skip type/name fields).
        disabled: If True, all form fields are rendered as non-editable.

    Returns:
        Dictionary of field values collected from the form.
    """
    if existing_values is None:
        existing_values = {}

    result: dict[str, Any] = {}

    for prop in config_fields:
        if is_top_level and prop.property_key in SKIP_TOP_LEVEL_KEYS:
            continue

        if isinstance(prop, ConfigUnionPropertyDefinition):
            union_values = _render_union_property(prop, existing_values, key_prefix, disabled=disabled)
            if union_values is not None:
                result[prop.property_key] = union_values

        elif isinstance(prop, ConfigSinglePropertyDefinition):
            if prop.nested_properties:
                nested_existing = existing_values.get(prop.property_key, {})
                if not isinstance(nested_existing, dict):
                    nested_existing = {}
                nested_values = render_datasource_config_form(
                    config_fields=prop.nested_properties,
                    existing_values=nested_existing,
                    key_prefix=f"{key_prefix}{prop.property_key}.",
                    is_top_level=False,
                    disabled=disabled,
                )
                if nested_values:
                    result[prop.property_key] = nested_values
            else:
                value = _render_single_property(prop, existing_values, key_prefix, disabled=disabled)
                if value is not None and str(value).strip():
                    result[prop.property_key] = value

    return result


def _render_single_property(
    prop: ConfigSinglePropertyDefinition,
    existing_values: dict[str, Any],
    key_prefix: str,
    disabled: bool = False,
) -> Any:
    """Render a single (leaf) property as a Streamlit text input."""
    existing_value = existing_values.get(prop.property_key, "")
    if existing_value is None:
        existing_value = ""
    existing_value = str(existing_value)

    default = prop.default_value or ""

    display_value = existing_value if existing_value else default

    label = prop.property_key
    if not prop.required:
        label += " (Optional)"

    widget_key = f"{key_prefix}{prop.property_key}"

    if prop.secret:
        value = st.text_input(
            label,
            value=display_value,
            type="password",
            key=widget_key,
            disabled=disabled,
        )
    else:
        value = st.text_input(
            label,
            value=display_value,
            key=widget_key,
            disabled=disabled,
        )

    return value


def _infer_union_type(
    existing_union: dict[str, Any],
    type_choices: dict[str, type],
    type_properties: dict[type, list[ConfigPropertyDefinition]],
) -> str | None:
    """Infer which union variant best matches the existing config keys.

    YAML configs for union fields don't store a ``type`` discriminator, so we
    compare the keys present in the loaded dict against each variant's expected
    property keys and pick the variant with the highest overlap.
    """
    if not existing_union:
        return None

    existing_keys = set(existing_union.keys()) - {"type"}
    best_match: str | None = None
    best_score = 0

    for name, typ in type_choices.items():
        props = type_properties.get(typ, [])
        expected_keys = {p.property_key for p in props}
        overlap = len(existing_keys & expected_keys)
        if overlap > best_score:
            best_score = overlap
            best_match = name

    return best_match


def _render_union_property(
    prop: ConfigUnionPropertyDefinition,
    existing_values: dict[str, Any],
    key_prefix: str,
    disabled: bool = False,
) -> dict[str, Any] | None:
    """Render a union property: a type selector followed by the selected type's fields."""
    type_choices = {t.__name__: t for t in prop.types}
    choice_names = sorted(type_choices.keys())

    if not choice_names:
        return None

    existing_union = existing_values.get(prop.property_key, {})
    if not isinstance(existing_union, dict):
        existing_union = {}

    existing_type_name = existing_union.get("type", "")
    if existing_type_name not in choice_names:
        existing_type_name = _infer_union_type(existing_union, type_choices, prop.type_properties) or ""

    default_index = 0
    if existing_type_name in choice_names:
        default_index = choice_names.index(existing_type_name)

    widget_key = f"{key_prefix}{prop.property_key}.type"
    chosen_name = st.selectbox(
        f"{prop.property_key} type",
        options=choice_names,
        index=default_index,
        key=widget_key,
        disabled=disabled,
    )

    if chosen_name is None:
        return None

    chosen_type = type_choices[chosen_name]
    nested_props = prop.type_properties.get(chosen_type, [])

    nested_values = render_datasource_config_form(
        config_fields=nested_props,
        existing_values=existing_union,
        key_prefix=f"{key_prefix}{prop.property_key}.",
        is_top_level=False,
        disabled=disabled,
    )

    return nested_values
