import logging
from enum import Enum

from databao.agent.integrations.dce import DatabaoContextApi

from databao_cli.project.layout import BUILD_SENTINEL, ProjectLayout

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


def get_build_fingerprint(project: ProjectLayout) -> float:
    """Return a fingerprint representing the last completed build.

    Reads the modification time of the ``.build_complete`` sentinel file
    written by the build command after a successful build.  This avoids
    false positives from files being written *during* a build.

    Returns 0.0 if the sentinel does not exist.
    """
    sentinel = project.root_domain_dir / BUILD_SENTINEL
    try:
        return sentinel.stat().st_mtime
    except OSError:
        return 0.0


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
