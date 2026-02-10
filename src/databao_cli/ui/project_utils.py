from enum import Enum

from databao_cli.project.layout import ProjectLayout


class DCEProjectStatus(Enum):
    """Status of a DCE project."""

    VALID = "valid"  # Project found with build outputs
    NO_BUILD = "no_build"  # Project found but no output/run


def dce_status(project: ProjectLayout) -> DCEProjectStatus:
    output_dir = project.root_domain_project.output_dir
    if output_dir.exists() and output_dir.is_dir():
        return DCEProjectStatus.VALID
    else:
        return DCEProjectStatus.NO_BUILD

