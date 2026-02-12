from enum import Enum

from databao_cli.project.layout import ProjectLayout


class DCEProjectStatus(Enum):
    """Status of a DCE project."""

    VALID = "valid"
    NO_BUILD = "no_build"


def dce_status(project: ProjectLayout) -> DCEProjectStatus:
    root_domain = project.root_domain_project
    if root_domain is None:
        return DCEProjectStatus.NO_BUILD
    output_dir = root_domain.output_dir
    if output_dir.exists() and output_dir.is_dir():
        return DCEProjectStatus.VALID
    else:
        return DCEProjectStatus.NO_BUILD
