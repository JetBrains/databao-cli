import logging
from enum import Enum

from databao.integrations.dce import DatabaoContextApi

from databao_cli.project.layout import ProjectLayout

logger = logging.getLogger(__name__)


class DatabaoProjectStatus(Enum):
    """Status of a Databao project (assessed via its root domain DCE project)."""

    VALID = "valid"
    NO_BUILD = "no_build"
    NO_DATASOURCES = "no_datasources"
    NOT_INITIALIZED = "not_initialized"


def databao_project_status(project: ProjectLayout) -> DatabaoProjectStatus:
    """Determine the status of a Databao project.

    Checks whether the project is initialized, has datasources configured,
    and has been built.
    """
    if not project.databao_dir.exists():
        return DatabaoProjectStatus.NOT_INITIALIZED

    try:
        dce_project = DatabaoContextApi.get_dce_project(project.root_domain_dir)
    except ValueError:
        return DatabaoProjectStatus.NOT_INITIALIZED

    configured = dce_project.get_configured_datasource_list()
    if not configured:
        return DatabaoProjectStatus.NO_DATASOURCES

    prepared = dce_project.get_introspected_datasource_list()
    if not prepared:
        return DatabaoProjectStatus.NO_BUILD

    return DatabaoProjectStatus.VALID
