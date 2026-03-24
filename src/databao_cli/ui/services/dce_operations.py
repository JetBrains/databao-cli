"""DCE operations service layer for the UI.

Provides all DCE/datasource operations needed by the Streamlit UI,
using direct Python API calls (no subprocess/shell).
"""

import logging
import os
from pathlib import Path
from typing import Any

from databao_context_engine import (
    BuildDatasourceResult,
    CheckDatasourceConnectionResult,
    ConfiguredDatasource,
    DatabaoContextDomainManager,
    DatabaoContextPluginLoader,
    DatasourceId,
    DatasourceType,
)
from databao_context_engine.datasources.check_config import DatasourceConnectionStatus
from databao_context_engine.pluginlib.build_plugin import BuildDatasourcePlugin
from databao_context_engine.pluginlib.config import ConfigPropertyDefinition
from databao_context_engine.pluginlib.plugin_utils import check_connection_for_datasource

from databao_cli.commands.init import init_impl
from databao_cli.project.layout import ProjectLayout

logger = logging.getLogger(__name__)


def init_project(project_dir: Path) -> ProjectLayout:
    """Initialize a new Databao project at the given directory.

    Creates the project directory if it doesn't exist, then creates the
    Databao project structure and initializes the root domain DCE project.

    Raises:
        InitDatabaoProjectError: If the project cannot be initialized.
    """
    project_dir.mkdir(parents=True, exist_ok=True)
    return init_impl(project_dir)


def get_available_datasource_types() -> list[str]:
    """Return sorted list of available datasource type strings (excluding file plugins)."""
    loader = DatabaoContextPluginLoader()
    types = loader.get_all_supported_datasource_types(exclude_file_plugins=True)
    return sorted(ds_type.full_type for ds_type in types)


def get_datasource_config_fields(ds_type_str: str) -> list[ConfigPropertyDefinition]:
    """Return the config field definitions for a given datasource type string."""
    loader = DatabaoContextPluginLoader()
    ds_type = DatasourceType(full_type=ds_type_str)
    return loader.get_config_file_structure_for_datasource_type(ds_type)


def add_datasource(project_dir: Path, ds_type_str: str, ds_name: str, config: dict[str, Any]) -> ConfiguredDatasource:
    """Create a new datasource config in the DCE project.

    Args:
        project_dir: Path to the DCE project (e.g. root_domain_dir).
        ds_type_str: Full datasource type string (e.g. "database/postgresql").
        ds_name: Name for the datasource.
        config: Config dictionary (field values, excluding type and name).
    """
    manager = DatabaoContextDomainManager(domain_dir=project_dir)
    ds_type = DatasourceType(full_type=ds_type_str)
    return manager.create_datasource_config(ds_type, ds_name, config, overwrite_existing=False)


def save_datasource(project_dir: Path, ds_type_str: str, ds_name: str, config: dict[str, Any]) -> ConfiguredDatasource:
    """Save (overwrite) an existing datasource config in the DCE project."""
    manager = DatabaoContextDomainManager(domain_dir=project_dir)
    ds_type = DatasourceType(full_type=ds_type_str)
    return manager.create_datasource_config(ds_type, ds_name, config, overwrite_existing=True)


def remove_datasource(project_dir: Path, datasource_id: DatasourceId) -> None:
    """Remove a datasource config file from the DCE project."""
    manager = DatabaoContextDomainManager(domain_dir=project_dir)
    config_path = manager.get_config_file_path_for_datasource(datasource_id)
    if config_path.is_file():
        os.unlink(config_path)
        logger.info(f"Removed datasource config: {config_path}")
    else:
        logger.warning(f"Datasource config file not found: {config_path}")


def list_datasources(project_dir: Path) -> list[ConfiguredDatasource]:
    """List all configured data sources in the DCE project (reads from disk)."""
    try:
        manager = DatabaoContextDomainManager(domain_dir=project_dir)
        return manager.get_configured_datasource_list()
    except ValueError:
        return []


def verify_datasource(project_dir: Path, datasource_id: DatasourceId) -> CheckDatasourceConnectionResult:
    """Returns the connection check result for the given datasource_id.

    Raises:
        ValueError: If no connection check result is available for the given datasource.
    """
    manager = DatabaoContextDomainManager(domain_dir=project_dir)
    results = manager.check_datasource_connection(datasource_ids=[datasource_id])
    if datasource_id in results:
        return results[datasource_id]
    raise ValueError(f"No connection check result for datasource {datasource_id}")


def verify_datasource_config(ds_type_str: str, ds_name: str, config: dict[str, Any]) -> CheckDatasourceConnectionResult:
    """Verify a datasource connection from config values without writing to disk.

    Calls the plugin's check_connection directly with the provided config dict.
    """
    ds_type = DatasourceType(full_type=ds_type_str)
    full_config = {"type": ds_type_str, "name": ds_name, **config}

    loader = DatabaoContextPluginLoader()
    plugin = loader.get_plugin_for_datasource_type(ds_type)

    if plugin is None:
        return CheckDatasourceConnectionResult(
            datasource_id=DatasourceId.from_string_repr(f"{ds_name}.yaml"),
            connection_status=DatasourceConnectionStatus.INVALID,
            summary="No compatible plugin found",
        )

    if not isinstance(plugin, BuildDatasourcePlugin):
        return CheckDatasourceConnectionResult(
            datasource_id=DatasourceId.from_string_repr(f"{ds_name}.yaml"),
            connection_status=DatasourceConnectionStatus.UNKNOWN,
            summary="Plugin does not support connection verification",
        )

    dummy_id = DatasourceId.from_string_repr(f"{ds_name}.yaml")
    try:
        check_connection_for_datasource(
            plugin=plugin,
            datasource_type=ds_type,
            config=full_config,
        )
        return CheckDatasourceConnectionResult(
            datasource_id=dummy_id,
            connection_status=DatasourceConnectionStatus.VALID,
            summary=None,
        )
    except NotImplementedError:
        return CheckDatasourceConnectionResult(
            datasource_id=dummy_id,
            connection_status=DatasourceConnectionStatus.UNKNOWN,
            summary="Plugin doesn't support validating its config",
        )
    except Exception as e:
        return CheckDatasourceConnectionResult(
            datasource_id=dummy_id,
            connection_status=DatasourceConnectionStatus.INVALID,
            summary="Connection with the datasource can not be established",
            full_message=str(e),
        )


def build_context(project_dir: Path) -> list[BuildDatasourceResult]:
    """Build context for all datasources in the DCE project. This is a long-running operation."""
    manager = DatabaoContextDomainManager(domain_dir=project_dir)
    results = manager.build_context()
    write_build_sentinel_file(project_dir)
    return results


BUILD_SENTINEL = ".build_complete"


def write_build_sentinel_file(project_dir: Path) -> None:
    """Write a sentinel file to signal that a build has completed."""
    sentinel = project_dir / BUILD_SENTINEL
    sentinel.write_text("")
    logger.debug("Wrote build sentinel: %s", sentinel)


def get_status_info(project_dir: Path) -> str:
    """Return formatted status info string for display.

    Delegates to the CLI's status_impl which handles multi-domain iteration.
    """
    from databao_cli.commands.status import status_impl

    return status_impl(project_dir)
