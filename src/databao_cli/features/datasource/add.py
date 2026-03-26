from pathlib import Path

from databao_context_engine import (
    DatabaoContextDomainManager,
    DatasourceId,
    DatasourceType,
    UserInputCallback,
)

from databao_cli.shared.project.layout import ProjectLayout


def datasource_config_exists(project_layout: ProjectLayout, domain: str, datasource_name: str) -> DatasourceId | None:
    """Return the existing DatasourceId if a config already exists for this name, else None."""
    domain_dir = project_layout.domains_dir / domain
    domain_manager = DatabaoContextDomainManager(domain_dir=domain_dir)
    return domain_manager.datasource_config_exists(datasource_name=datasource_name)


def create_datasource_config(
    project_layout: ProjectLayout,
    domain: str,
    datasource_type: DatasourceType,
    datasource_name: str,
    user_input_callback: UserInputCallback,
    *,
    overwrite_existing: bool = False,
) -> tuple[DatasourceId, Path]:
    """Create a datasource config file. Returns (datasource_id, config_file_path)."""
    domain_dir = project_layout.domains_dir / domain
    domain_manager = DatabaoContextDomainManager(domain_dir=domain_dir)
    created_datasource = domain_manager.create_datasource_config_interactively(
        datasource_type, datasource_name, user_input_callback, overwrite_existing=overwrite_existing
    )
    datasource_id = created_datasource.datasource.id
    config_path = domain_manager.get_config_file_path_for_datasource(datasource_id)
    return datasource_id, config_path
