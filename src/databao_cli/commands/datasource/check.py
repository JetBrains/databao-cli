import os

import click
from databao_context_engine import (
    CheckDatasourceConnectionResult,
    DatabaoContextDomainManager,
    DatasourceId,
)

from databao_cli.commands._utils import get_project_or_exit
from databao_cli.project.layout import ProjectLayout


@click.command(name="check")
@click.argument(
    "domains",
    type=click.STRING,
    nargs=-1,
)
@click.pass_context
def check(ctx: click.Context, domains: tuple[str, ...]) -> None:
    """Check whether a datasource configuration is valid.

    The configuration is considered as valid if a connection with the datasource can be established.

    By default, all declared datasources across all domains in the project will be checked.
    You can explicitly list which domains to validate by using the [DOMAINS] argument.
    """
    project_layout = get_project_or_exit(ctx.obj["project_dir"])
    check_impl(project_layout, requested_domains=list(domains) if domains else None)


def check_impl(project_layout: ProjectLayout, requested_domains: list[str] | None) -> None:
    domains: list[str] = project_layout.get_domain_names() if requested_domains is None else requested_domains

    results = _check_domains(project_layout, domains)

    if all([len(domain_results) == 0 for domain_results in results.values()]):
        click.echo("No datasource found")
        return

    for domain, datasource_results in results.items():
        print_connection_check_results(domain, datasource_results)


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


def _check_domains(
    project_layout: ProjectLayout, domains: list[str]
) -> dict[str, dict[DatasourceId, CheckDatasourceConnectionResult]]:
    results: dict[str, dict[DatasourceId, CheckDatasourceConnectionResult]] = {}
    for domain in domains:
        domain_dir = project_layout.domains_dir / domain
        if not domain_dir.exists():
            raise ValueError(
                f"The specified {domain} domain does not exist. "
                f"Available domains: {', '.join(project_layout.get_domain_names())}"
            )
        domain_manager = DatabaoContextDomainManager(domain_dir=domain_dir)
        results[domain] = domain_manager.check_datasource_connection()
    return results
