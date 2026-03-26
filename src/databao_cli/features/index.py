from databao_context_engine import ChunkEmbeddingMode, DatabaoContextDomainManager, DatasourceId, IndexDatasourceResult

from databao_cli.shared.project.layout import ProjectLayout


def index_impl(
    project_layout: ProjectLayout, domain: str, datasources_config_files: list[str] | None
) -> list[IndexDatasourceResult]:
    dce_project_dir = project_layout.domains_dir / domain

    datasource_ids = [DatasourceId.from_string_repr(p) for p in datasources_config_files] if datasources_config_files else None

    results: list[IndexDatasourceResult] = DatabaoContextDomainManager(domain_dir=dce_project_dir).index_built_contexts(
        datasource_ids=datasource_ids, chunk_embedding_mode=ChunkEmbeddingMode.EMBEDDABLE_TEXT_ONLY
    )

    return results
