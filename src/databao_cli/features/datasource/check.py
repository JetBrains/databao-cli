from databao_context_engine import (
    CheckDatasourceConnectionResult,
    DatabaoContextDomainManager,
    DatasourceId,
)

from databao_cli.shared.project.layout import ProjectLayout


def check_impl(
    project_layout: ProjectLayout, requested_domains: list[str] | None
) -> dict[str, dict[DatasourceId, CheckDatasourceConnectionResult]]:
    domains: list[str] = project_layout.get_domain_names() if requested_domains is None else requested_domains
    return _check_domains(project_layout, domains)


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
