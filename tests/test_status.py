import pytest
from click.testing import CliRunner

from databao_cli.__main__ import cli


@pytest.mark.skip(reason="Status is broken for now")
def test_databao_status():
    runner = CliRunner()
    result = runner.invoke(cli, ["status"])

    assert result.exit_code == 0, result.output
    assert "Databao context engine plugins: ['jetbrains/duckdb', 'jetbrains/parquet'" in result.output
