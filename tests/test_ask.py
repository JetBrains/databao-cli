from click.testing import CliRunner

from databao_cli.__main__ import cli


def test_ask_help():
    """Test that the ask command shows help."""
    runner = CliRunner()
    result = runner.invoke(cli, ["ask", "--help"])

    assert result.exit_code == 0
    assert "Chat with the Databao agent" in result.output
