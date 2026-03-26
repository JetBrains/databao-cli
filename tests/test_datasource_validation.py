import pytest

from databao_cli.features.datasource.validation import (
    MAX_DATASOURCE_NAME_LENGTH,
    validate_datasource_name,
)


class TestValidateDatasourceName:
    """Tests for validate_datasource_name()."""

    @pytest.mark.parametrize(
        "name",
        [
            "my-datasource",
            "my_datasource",
            "my.datasource",
            "ds1",
            "a",
            "A",
            "Snowflake-Prod",
            "test_db.v2",
            "ab",
            "resources/my_db",
            "folder/sub/name",
        ],
    )
    def test_valid_names(self, name: str) -> None:
        assert validate_datasource_name(name) is None

    def test_empty_name(self) -> None:
        assert validate_datasource_name("") is not None

    def test_whitespace_only(self) -> None:
        assert validate_datasource_name("   ") is not None

    def test_name_with_spaces(self) -> None:
        error = validate_datasource_name("my datasource")
        assert error is not None
        assert "spaces" in error.lower()

    def test_name_with_leading_space(self) -> None:
        error = validate_datasource_name(" leading")
        assert error is not None

    def test_name_with_trailing_space(self) -> None:
        error = validate_datasource_name("trailing ")
        assert error is not None

    @pytest.mark.parametrize("name", [".hidden", "-start", "end-", "end."])
    def test_name_starting_or_ending_with_special_char(self, name: str) -> None:
        assert validate_datasource_name(name) is not None

    @pytest.mark.parametrize("char", ["@", "#", "$", "%", "!", "?", "\\", ":", "*"])
    def test_forbidden_characters(self, char: str) -> None:
        assert validate_datasource_name(f"ds{char}name") is not None

    def test_double_slash_rejected(self) -> None:
        assert validate_datasource_name("a//b") is not None

    def test_leading_slash_rejected(self) -> None:
        assert validate_datasource_name("/a") is not None

    def test_trailing_slash_rejected(self) -> None:
        assert validate_datasource_name("a/") is not None

    def test_name_too_long(self) -> None:
        long_name = "a" * (MAX_DATASOURCE_NAME_LENGTH + 1)
        error = validate_datasource_name(long_name)
        assert error is not None
        assert "255" in error

    def test_name_at_max_length(self) -> None:
        name = "a" * MAX_DATASOURCE_NAME_LENGTH
        assert validate_datasource_name(name) is None
