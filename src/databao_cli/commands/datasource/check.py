import click

from databao_cli.shared.cli_utils import get_project_or_raise, handle_feature_errors


@click.command(name="check")
@click.argument(
    "domains",
    type=click.STRING,
    nargs=-1,
)
@click.pass_context
@handle_feature_errors
def check(ctx: click.Context, domains: tuple[str, ...]) -> None:
    """Check whether a datasource configuration is valid.

    The configuration is considered as valid if a connection with the datasource can be established.

    By default, all declared datasources across all domains in the project will be checked.
    You can explicitly list which domains to validate by using the [DOMAINS] argument.
    """
    from databao_cli.features.datasource.check import check_impl
    from databao_cli.workflows.datasource.check import print_connection_check_results

    project_layout = get_project_or_raise(ctx.obj["project_dir"])
    results = check_impl(project_layout, requested_domains=list(domains) if domains else None)

    if all(len(v) == 0 for v in results.values()):
        click.echo("No datasource found")
    else:
        for domain, datasource_results in results.items():
            print_connection_check_results(domain, datasource_results)
