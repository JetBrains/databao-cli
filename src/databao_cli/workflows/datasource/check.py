"""CLI display for datasource connection check results."""

import os

import click
from databao_context_engine import CheckDatasourceConnectionResult, DatasourceId


def print_connection_check_results(
    domain: str, datasource_results: dict[DatasourceId, CheckDatasourceConnectionResult]
) -> None:
    for result in datasource_results.values():
        fq_datasource_name = domain + os.pathsep + str(result.datasource_id)
        status = str(result.connection_status.value)
        if result.summary:
            status += f" - {result.summary}"
        if result.full_message:
            status += f": {result.full_message}"

        click.echo(f"{fq_datasource_name}: {status}")
