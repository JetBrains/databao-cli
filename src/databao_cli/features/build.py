from databao_context_engine import BuildDatasourceResult, DatabaoContextDomainManager

from databao_cli.shared.log.cli_progress import cli_progress
from databao_cli.shared.project.layout import ProjectLayout


def build_impl(project_layout: ProjectLayout, domain: str, should_index: bool) -> list[BuildDatasourceResult]:
    dce_project_dir = project_layout.domains_dir / domain
    manager = DatabaoContextDomainManager(domain_dir=dce_project_dir)

    datasources = manager.get_configured_datasource_list()
    with cli_progress(total=len(datasources), label="Building datasources"):
        results: list[BuildDatasourceResult] = manager.build_context(datasource_ids=None, should_index=should_index)
    return results
