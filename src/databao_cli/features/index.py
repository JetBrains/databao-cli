from databao_context_engine import DatabaoContextDomainManager, DatasourceId, IndexDatasourceResult

from databao_cli.shared.log.cli_progress import cli_progress
from databao_cli.shared.project.layout import ProjectLayout


def index_impl(
    project_layout: ProjectLayout, domain: str, datasources_config_files: list[str] | None
) -> list[IndexDatasourceResult]:
    dce_project_dir = project_layout.domains_dir / domain

    datasource_ids = [DatasourceId.from_string_repr(p) for p in datasources_config_files] if datasources_config_files else None

    manager = DatabaoContextDomainManager(domain_dir=dce_project_dir)

    total = len(datasource_ids) if datasource_ids is not None else len(manager.get_configured_datasource_list())

    with cli_progress(total=total, label="Indexing datasources"):
        results: list[IndexDatasourceResult] = manager.index_built_contexts(datasource_ids=datasource_ids)

    return results
