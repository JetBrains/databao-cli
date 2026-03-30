import click

from databao_cli.shared.cli_utils import handle_feature_errors


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
@handle_feature_errors
def build(ctx: click.Context, domain: str, should_index: bool) -> None:
    """Build context for all domain's datasources.

    The output of the build command will be saved in the domain's output directory.

    Internally, this indexes the context to be used by the MCP server and the "retrieve" command.
    """
    from databao_cli.features.build import build_impl
    from databao_cli.shared.cli_utils import get_project_or_raise
    from databao_cli.shared.project.layout import write_build_sentinel

    project_layout = get_project_or_raise(ctx.obj["project_dir"])
    results = build_impl(project_layout, domain, should_index)
    write_build_sentinel(project_layout.domains_dir / domain)
    click.echo(f"Build complete. Processed {len(results)} datasources.")
