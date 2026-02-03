from click.testing import CliRunner

from databao_cli.__main__ import cli


def test_databao_status():
    runner = CliRunner()
    result = runner.invoke(cli, ["status"])

    assert result.exit_code == 0, result.output
    assert (
        "Databao context engine plugins: "
        "['jetbrains/duckdb', 'jetbrains/parquet', 'jetbrains/unstructured_files', 'jetbrains/unstructured_files']"
        "" in result.output
    )
