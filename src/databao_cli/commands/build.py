import click
from databao_context_engine import BuildDatasourceResult, DatabaoContextDomainManager

from databao_cli.project.layout import ProjectLayout


@click.command()
@click.option(
    "-d",
    "--domain",
    type=click.STRING,
    default="root",
    help="Databao domain name",
)
@click.option(
    "--should-index/--should-not-index",
    default=True,
    show_default=True,
    help="Whether to index the context. If disabled, the context will be built but not indexed.",
)
@click.pass_context
def build(ctx: click.Context, domain: str, should_index: bool) -> None:
    """Build context for all domain's datasources.

    The output of the build command will be saved in the domain's output directory.

    Internally, this indexes the context to be used by the MCP server and the "retrieve" command.
    """
    from databao_cli.commands._utils import get_project_or_exit

    project_layout = get_project_or_exit(ctx.obj["project_dir"])
    results = build_impl(project_layout, domain, should_index)
    click.echo(f"Build complete. Processed {len(results)} datasources.")


def build_impl(project_layout: ProjectLayout, domain: str, should_index: bool) -> list[BuildDatasourceResult]:
    dce_project_dir = project_layout.domains_dir / domain
    results: list[BuildDatasourceResult] = DatabaoContextDomainManager(domain_dir=dce_project_dir).build_context(
        datasource_ids=None, should_index=should_index
    )

    return results
