import click
from databao_context_engine import ChunkEmbeddingMode, DatabaoContextDomainManager, DatasourceId, IndexDatasourceResult

from databao_cli.project.layout import ProjectLayout


@click.command()
@click.option(
    "-d",
    "--domain",
    type=click.STRING,
    default="root",
    help="Databao domain name",
)
@click.argument(
    "datasources-config-files",
    nargs=-1,
    type=click.STRING,
)
@click.pass_context
def index(ctx: click.Context, domain: str, datasources_config_files: tuple[str, ...]) -> None:
    """Index built contexts into the embeddings database.

    If one or more datasource config file strings are provided, only those datasources will be indexed.
    If no values are provided, all built contexts for the selected domain will be indexed.
    """
    from databao_cli.commands._utils import get_project_or_exit

    project_layout = get_project_or_exit(ctx.obj["project_dir"])
    datasources = list(datasources_config_files) if datasources_config_files else None
    results = index_impl(project_layout, domain, datasources)
    click.echo(f"Index complete. Processed {len(results)} contexts.")


def index_impl(
    project_layout: ProjectLayout, domain: str, datasources_config_files: list[str] | None
) -> list[IndexDatasourceResult]:
    dce_project_dir = project_layout.domains_dir / domain

    datasource_ids = [DatasourceId.from_string_repr(p) for p in datasources_config_files] if datasources_config_files else None

    results: list[IndexDatasourceResult] = DatabaoContextDomainManager(domain_dir=dce_project_dir).index_built_contexts(
        datasource_ids=datasource_ids, chunk_embedding_mode=ChunkEmbeddingMode.EMBEDDABLE_TEXT_ONLY
    )

    return results
