import pytest
from click.testing import CliRunner

from databao_cli.__main__ import cli


@pytest.mark.skip(reason="Status is broken for now")
def test_databao_status():
    runner = CliRunner()
    result = runner.invoke(cli, ["status"], catch_exceptions=False)

    assert result.exit_code == 0, result
    plugins = ["'jetbrains/parquet'", "'jetbrains/duckdb'", "'jetbrains/snowflake'"]
    assert all(plugin in result.output for plugin in plugins)
