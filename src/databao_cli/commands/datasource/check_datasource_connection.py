import os

import click
from databao_context_engine import (
    CheckDatasourceConnectionResult,
    DatabaoContextProjectManager,
)

from databao_cli.project.layout import ProjectLayout


def print_connection_check_results(domain: str, datasource_results: list[CheckDatasourceConnectionResult]):
    for result in datasource_results:
        fq_datasource_name = domain + os.pathsep + str(result.datasource_id)
        status = str(result.connection_status.value)
        if result.summary:
            status += f" - {result.summary}"
        if result.full_message:
            status += f": {result.full_message}"

        click.echo(f"{fq_datasource_name}: {status}")


def check_datasource_connection_impl(project_layout: ProjectLayout, requested_domains: list[str] | None) -> None:
    domains: list[str] = project_layout.get_domain_names() if requested_domains is None else requested_domains

    results = _check_domains(project_layout, domains)

    if all([len(domain_results) == 0 for domain_results in results.values()]):
        click.echo("No datasource found")
        return

    for domain, datasource_results in results.items():
        print_connection_check_results(domain, datasource_results)


def _check_domains(project_layout: ProjectLayout, domains: list[str]) -> dict[str, list[CheckDatasourceConnectionResult]]:
    results: dict[str, list[CheckDatasourceConnectionResult]] = {}
    for domain in domains:
        domain_dir = project_layout.domains_dir / domain
        if not domain_dir.exists():
            raise ValueError(
                f"The specified {domain} domain does not exist. "
                f"Avaiable domains: {', '.join(project_layout.get_domain_names())}"
            )
        domain_manager = DatabaoContextProjectManager(project_dir=domain_dir)
        results[domain] = domain_manager.check_datasource_connection()
    return results
