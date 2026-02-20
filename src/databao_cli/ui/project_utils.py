import logging
from enum import Enum

from databao.integrations.dce import DatabaoContextApi

from databao_cli.project.layout import ProjectLayout

logger = logging.getLogger(__name__)


class DatabaoProjectStatus(Enum):
    """Status of a Databao project (assessed via its root domain DCE project)."""

    VALID = "valid"
    NO_DATASOURCES = "no_datasources"
    NOT_INITIALIZED = "not_initialized"


def databao_project_status(project: ProjectLayout) -> DatabaoProjectStatus:
    """Determine the status of a Databao project.

    Checks whether the project is initialized and has datasources configured.
    Build output is not required -- projects with datasources are considered VALID.
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

    return DatabaoProjectStatus.VALID


def has_build_output(project: ProjectLayout) -> bool:
    """Check whether the project has any build output (introspected datasources).

    This is separate from project status because build is optional --
    a project without build output is still VALID.
    """
    try:
        dce_project = DatabaoContextApi.get_dce_project(project.root_domain_dir)
        return len(dce_project.get_introspected_datasource_list()) > 0
    except Exception:
        return False
