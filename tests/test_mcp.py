from click.testing import CliRunner

from databao_cli.__main__ import cli


def test_mcp_help() -> None:
    """Test that the mcp command shows help."""
    runner = CliRunner()
    result = runner.invoke(cli, ["mcp", "--help"])

    assert result.exit_code == 0
    assert "Run an MCP server exposing Databao tools" in result.output
