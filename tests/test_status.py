from click.testing import CliRunner

from databao_cli.__main__ import cli
from tests.utils.project import within_dir


def test_databao_status(tmp_path):
    runner = CliRunner()
    with within_dir(tmp_path):
        result = runner.invoke(cli, ["status"], catch_exceptions=False)

    assert result.exit_code == 0, result
    plugins = ["'jetbrains/parquet'", "'jetbrains/duckdb'", "'jetbrains/snowflake'"]
    assert all(plugin in result.output for plugin in plugins)
