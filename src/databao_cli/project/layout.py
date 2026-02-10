from dataclasses import dataclass
from functools import cached_property
from pathlib import Path
from databao_context_engine.project.layout import ProjectLayout as DCEProjectLayout, validate_project_dir


def get_databao_project_dir(project_dir: Path) -> Path:
    return project_dir / "databao"


@dataclass(frozen=True)
class ProjectLayout:
    project_dir: Path

    @property
    def name(self) -> str:
        return self.project_dir.name

    @property
    def databao_dir(self) -> Path:
        return get_databao_project_dir(self.project_dir)

    @property
    def agents_dir(self) -> Path:
        return self.databao_dir / "agents"

    @property
    def domains_dir(self) -> Path:
        return self.databao_dir / "domains"

    @property
    def root_domain_dir(self) -> Path:
        """
        Root domain is the domain which is used by default unless domain parameter is specified
        """
        return self.domains_dir / "root"

    @cached_property
    def root_domain_project(self)-> DCEProjectLayout | None:
        return validate_project_dir(self.root_domain_dir)


def find_project(initial_dir: Path) -> ProjectLayout | None:
    dirs_to_check = [initial_dir] + list(initial_dir.parents)
    for project_dir_candidate in dirs_to_check:
        databao_project_dir = get_databao_project_dir(project_dir_candidate)
        if databao_project_dir.exists():
            return ProjectLayout(project_dir_candidate)
    return None
