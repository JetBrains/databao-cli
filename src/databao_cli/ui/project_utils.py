import logging
from enum import Enum

from databao.integrations.dce import DatabaoContextApi

from databao_cli.project.layout import ProjectLayout

logger = logging.getLogger(__name__)


class DCEProjectStatus(Enum):
    """Status of a DCE project."""

    VALID = "valid"
    NO_BUILD = "no_build"
    NO_DATASOURCES = "no_datasources"


def dce_status(project: ProjectLayout) -> DCEProjectStatus:
    try:
        dce_project = DatabaoContextApi.get_dce_project(project.root_domain_dir)
    except ValueError:
        return DCEProjectStatus.NO_DATASOURCES

    configured = dce_project.get_configured_datasource_list()
    if not configured:
        return DCEProjectStatus.NO_DATASOURCES

    prepared = dce_project.get_introspected_datasource_list()
    if not prepared:
        return DCEProjectStatus.NO_BUILD

    return DCEProjectStatus.VALID
