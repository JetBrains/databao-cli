from click.testing import CliRunner
from databao.__main__ import cli


def test_dce_hello():
    runner = CliRunner()
    result = runner.invoke(cli, ['dce', 'hello'])

    assert result.exit_code == 0
    assert "Hello from DCE!" in result.output
