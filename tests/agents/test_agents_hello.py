from click.testing import CliRunner
from databao.__main__ import cli


def test_agents_hello():
    runner = CliRunner()
    result = runner.invoke(cli, ['agents', 'hello'])

    assert result.exit_code == 0
    assert "Hello from Agents!" in result.output
