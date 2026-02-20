"""Shared executor creation utilities."""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from databao.core import Executor

EXECUTOR_TYPES = {
    "lighthouse": "LighthouseExecutor (recommended)",
    "react_duckdb": "ReactDuckDBExecutor (experimental)",
}


def create_executor(executor_type: str) -> "Executor":
    """Create a data executor instance from its type name.

    Supported types are defined in EXECUTOR_TYPES.
    """
    from databao.executors.lighthouse.executor import LighthouseExecutor
    from databao.executors.react_duckdb.executor import ReactDuckDBExecutor

    match executor_type:
        case "lighthouse":
            return LighthouseExecutor()
        case "react_duckdb":
            return ReactDuckDBExecutor()
        case _:
            raise ValueError(f"Unknown executor type: {executor_type!r}. Supported: {', '.join(EXECUTOR_TYPES)}")
