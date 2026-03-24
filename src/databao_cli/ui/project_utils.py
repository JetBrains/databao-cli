import logging
from enum import Enum
from pathlib import Path

from databao.agent.integrations.dce import DatabaoContextApi

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


BUILD_SENTINEL = ".build_complete"


def get_build_fingerprint(domain_dir: Path) -> float:
    """Return a fingerprint representing the current build state.

    Reads the modification time of the sentinel file written after a
    successful build.  Returns 0.0 if the sentinel does not exist.
    """
    sentinel = domain_dir / "output" / BUILD_SENTINEL
    try:
        return sentinel.stat().st_mtime if sentinel.is_file() else 0.0
    except OSError:
        logger.debug("Failed to read build sentinel", exc_info=True)
        return 0.0


def write_build_sentinel(domain_dir: Path) -> None:
    """Write (or touch) the build sentinel after a successful build.

    The sentinel is a zero-byte marker file whose mtime is compared by
    ``get_build_fingerprint`` to detect new builds.
    """
    output_dir = domain_dir / "output"
    output_dir.mkdir(parents=True, exist_ok=True)
    sentinel = output_dir / BUILD_SENTINEL
    sentinel.touch()
    logger.debug("Wrote build sentinel: %s", sentinel)
