from databao_context_engine import BuildDatasourceResult, DatabaoContextDomainManager

from databao_cli.log.cli_progress import cli_progress
from databao_cli.project.layout import ProjectLayout


def build_impl(project_layout: ProjectLayout, domain: str, should_index: bool) -> list[BuildDatasourceResult]:
    dce_project_dir = project_layout.domains_dir / domain
    with cli_progress() as progress:
        results: list[BuildDatasourceResult] = DatabaoContextDomainManager(domain_dir=dce_project_dir).build_context(
            datasource_ids=None, should_index=should_index, progress=progress
        )

    return results
