from pathlib import Path

import duckdb
import pytest
from click.testing import CliRunner

from databao_cli.__main__ import cli
from databao_cli.features.init.service import init_impl as init_databao_project


@pytest.fixture
def temp_parquet_file(request: pytest.FixtureRequest, tmp_path: Path) -> Path:
    name = request.function.__name__
    parquet_file_with_row_groups = tmp_path / f"{name}_with_row_groups.parquet"
    parquet_file = tmp_path / f"{name}.parquet"

    with duckdb.connect() as conn:
        conn.sql(
            f"""
            COPY
                (FROM (SELECT i as id, CAST(i AS VARCHAR) || '_test_name' AS name FROM generate_series(100) tbl(i)))
            TO '{parquet_file_with_row_groups}'
            (FORMAT parquet, ROW_GROUP_SIZE 4000);"""
        )

        conn.sql(
            f"""COPY (FROM  (SELECT i::DOUBLE as doubles FROM generate_series(100) tbl(i)))
                TO '{parquet_file}'
                (FORMAT parquet);"""
        )
    return parquet_file


def test_databao_datasource_add(tmp_path: Path, temp_parquet_file: Path) -> None:
    init_databao_project(tmp_path)

    inputs = [
        "parquet",
        "resources/my_parq",
        str(temp_parquet_file),
        "N",  # No. skip adding duckdb secret
        "y"  # Yes. Check connection
        "\n",
    ]

    runner = CliRunner()
    result = runner.invoke(
        cli,
        ["--project-dir", str(tmp_path), "datasource", "add"],
        input="\n".join(inputs),
        catch_exceptions=False,
    )

    assert result.exit_code == 0, result
    assert "root:resources/my_parq.yaml: Valid" in result.output, result
