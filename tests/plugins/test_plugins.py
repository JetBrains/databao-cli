import ast
import subprocess
from pathlib import Path
from typing import cast


def load_plugin_ids(*uv_extra_args: str) -> set[str]:
    test_file_path = Path(__file__).parent.joinpath("get_loaded_plugins.py")
    p = subprocess.Popen(
        ["uv", "run", "--no-dev", "--isolated", *list(uv_extra_args), "-s", str(test_file_path)],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    lines = []

    assert p.stdout is not None
    for line in p.stdout.readlines():
        lines.append(line.decode())
    exit_code = p.wait()

    assert exit_code == 0, f"""
    out = {lines}
    err = {"".join([line.decode() for line in p.stderr.readlines()]) if p.stderr is not None else ""}
"""
    output = "".join(lines)
    plugin_ids = cast(set[str], ast.literal_eval(output))
    return plugin_ids


def test_loaded_plugins_no_extra() -> None:
    plugin_ids = load_plugin_ids()
    assert plugin_ids == {
        "jetbrains/dbt",
        "jetbrains/duckdb",
        # comes transitively from databao agents dependency
        "jetbrains/mysql",
        "jetbrains/parquet",
        # comes transitively from databao agents dependency
        "jetbrains/postgres",
        # comes transitively from databao agents dependency
        "jetbrains/snowflake",
        "jetbrains/sqlite",
        "jetbrains/unstructured_files",
    }


def test_loaded_plugins_all_extras() -> None:
    # dce[pdf] brings enourmously huge docling library, we don't even test it,
    # it might cause CI/CD agents to take all device space and build to fail.
    plugin_ids = load_plugin_ids("--all-extras", "--no-extra", "pdf")
    assert plugin_ids == {
        "jetbrains/athena",
        "jetbrains/bigquery",
        "jetbrains/clickhouse",
        "jetbrains/duckdb",
        "jetbrains/mssql",
        "jetbrains/mysql",
        "jetbrains/postgres",
        "jetbrains/snowflake",
        "jetbrains/parquet",
        "jetbrains/sqlite",
        "jetbrains/unstructured_files",
        "jetbrains/dbt",
    }
