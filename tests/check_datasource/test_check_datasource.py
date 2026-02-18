from pathlib import Path

import duckdb
from click.testing import CliRunner

from databao_cli.__main__ import cli

TEST_PROJECT_DIR = Path(__file__).parent / "test_project"


def test_databao_datasource_check(tmp_path: Path):
    runner = CliRunner()
    test_duckdb = tmp_path / "test_db.duckdb"
    duckdb.connect(test_duckdb)
    result = runner.invoke(
        cli,
        ["--project-dir", str(TEST_PROJECT_DIR), "datasource", "check"],
        env={"TEST_DUCK_DB_PATH": str(test_duckdb)},
        catch_exceptions=False,
    )

    assert result.exit_code == 0, result
    assert "root:myduck.yaml: Valid" in result.output, result
