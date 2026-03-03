from databao_context_engine import BuildDatasourceResult, DatabaoContextProjectManager

from databao_cli.project.layout import ProjectLayout


def build_impl(project_layout: ProjectLayout, domain: str, should_index: bool) -> list[BuildDatasourceResult]:
    dce_project_dir = project_layout.domains_dir / domain
    results: list[BuildDatasourceResult] = DatabaoContextProjectManager(project_dir=dce_project_dir).build_context(
        datasource_ids=None, should_index=should_index
    )

    return results
