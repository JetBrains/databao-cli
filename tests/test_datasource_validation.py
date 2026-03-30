import pytest

from databao_cli.features.datasource.validation import (
    MAX_DATASOURCE_NAME_LENGTH,
    validate_datasource_name,
    validate_hostname,
    validate_port,
)


class TestValidateDatasourceName:
    """Tests for validate_datasource_name().

    The last segment must match the agent's pattern: ^[A-Za-z][A-Za-z0-9_]*$
    Folder segments (preceding the last) are more permissive.
    """

    @pytest.mark.parametrize(
        "name",
        [
            "my_datasource",
            "ds1",
            "a",
            "A",
            "SnowflakeProd",
            "test_db",
            "ab",
            "resources/my_db",
            "folder/sub/name",
            "my-folder/my_db",
            "v2.data/source1",
        ],
    )
    def test_valid_names(self, name: str) -> None:
        assert validate_datasource_name(name) is None

    @pytest.mark.parametrize(
        "name",
        [
            "my-datasource",
            "my.datasource",
            "Snowflake-Prod",
            "test_db.v2",
            "1startsWithDigit",
            "_leading_underscore",
        ],
    )
    def test_invalid_source_name_segment(self, name: str) -> None:
        """Last segment must match agent pattern: letter then [A-Za-z0-9_]*."""
        assert validate_datasource_name(name) is not None

    def test_empty_name(self) -> None:
        assert validate_datasource_name("") is not None

    def test_whitespace_only(self) -> None:
        assert validate_datasource_name("   ") is not None

    def test_name_with_spaces(self) -> None:
        error = validate_datasource_name("my datasource")
        assert error is not None
        assert "spaces" in error.lower()

    @pytest.mark.parametrize("name", ["my\tdatasource", "my\ndatasource", "my\u00a0datasource"])
    def test_name_with_non_space_whitespace(self, name: str) -> None:
        """Tabs, newlines, and non-breaking spaces should also be rejected."""
        error = validate_datasource_name(name)
        assert error is not None
        assert "spaces" in error.lower()

    @pytest.mark.parametrize("char", ["@", "#", "$", "%", "!", "?", "\\", ":", "*"])
    def test_forbidden_characters(self, char: str) -> None:
        assert validate_datasource_name(f"ds{char}name") is not None

    def test_double_slash_rejected(self) -> None:
        assert validate_datasource_name("a//b") is not None

    def test_leading_slash_rejected(self) -> None:
        assert validate_datasource_name("/a") is not None

    def test_trailing_slash_rejected(self) -> None:
        assert validate_datasource_name("a/") is not None

    def test_invalid_folder_segment(self) -> None:
        assert validate_datasource_name(".hidden/my_db") is not None

    def test_name_too_long(self) -> None:
        long_name = "a" * (MAX_DATASOURCE_NAME_LENGTH + 1)
        error = validate_datasource_name(long_name)
        assert error is not None
        assert "255" in error

    def test_name_at_max_length(self) -> None:
        name = "a" * MAX_DATASOURCE_NAME_LENGTH
        assert validate_datasource_name(name) is None


class TestValidatePort:
    """Tests for validate_port()."""

    @pytest.mark.parametrize("value", ["1", "80", "443", "5432", "65535"])
    def test_valid_ports(self, value: str) -> None:
        assert validate_port(value) is None

    @pytest.mark.parametrize("value", ["0", "-1", "65536", "99999"])
    def test_out_of_range(self, value: str) -> None:
        error = validate_port(value)
        assert error is not None
        assert "between" in error.lower()

    @pytest.mark.parametrize("value", ["abc", "12.5", "", "  "])
    def test_non_numeric(self, value: str) -> None:
        error = validate_port(value)
        assert error is not None
        assert "number" in error.lower()


class TestValidateHostname:
    """Tests for validate_hostname()."""

    @pytest.mark.parametrize(
        "value",
        [
            "localhost",
            "127.0.0.1",
            "192.168.1.1",
            "my-host",
            "db.example.com",
            "my-db.internal.corp.net",
            "::1",
            "2001:db8::1",
        ],
    )
    def test_valid_hostnames(self, value: str) -> None:
        assert validate_hostname(value) is None

    def test_empty_hostname(self) -> None:
        assert validate_hostname("") is not None
        assert validate_hostname("   ") is not None

    @pytest.mark.parametrize("value", ["-leading-hyphen", "trailing-hyphen-"])
    def test_invalid_hostnames(self, value: str) -> None:
        assert validate_hostname(value) is not None

    @pytest.mark.parametrize("value", ["not-an-ip:still-not", "db.example.com:5432"])
    def test_colon_strings_not_treated_as_ip(self, value: str) -> None:
        """Strings with colons that are not valid IPv6 should not pass as IPs."""
        assert validate_hostname(value) is not None
