from pathlib import Path

from databao_context_engine import InitDomainError, init_dce_domain

from databao_cli.project.layout import ProjectLayout, find_project


class InitDatabaoProjectError(ValueError):
    def __init__(self, message: str | None):
        super().__init__(message or "")
        self.message = message


class DatabaoProjectDirAlreadyExistsError(InitDatabaoProjectError):
    def __init__(self, message) -> None:
        super().__init__(message)


class ParentDatabaoProjectAlreadyExistsError(InitDatabaoProjectError):
    def __init__(self, message) -> None:
        super().__init__(message)


class ProjectDirDoesnotExistError(InitDatabaoProjectError):
    def __init__(self, message) -> None:
        super().__init__(message)


class ProjectDirNotDirError(InitDatabaoProjectError):
    def __init__(self, message) -> None:
        super().__init__(message)


class DatabaoContextEngineProjectInitError(InitDatabaoProjectError):
    def __init__(self, message) -> None:
        super().__init__(message)


def init_impl(project_dir: Path) -> ProjectLayout:
    project_creator = _ProjectCreator(project_dir=project_dir)
    return project_creator.create()


class _ProjectCreator:
    def __init__(self, project_dir: Path):
        self.project_dir = project_dir

    def create(self) -> ProjectLayout:
        self.ensure_can_init_project()

        project_layout = ProjectLayout(self.project_dir)
        project_layout.root_domain_dir.mkdir(parents=True, exist_ok=False)
        project_layout.agents_dir.mkdir(parents=True, exist_ok=True)

        try:
            init_dce_domain(project_layout.root_domain_dir)
        except InitDomainError as e:
            raise DatabaoContextEngineProjectInitError() from e

        return project_layout

    def ensure_can_init_project(self) -> None:
        if not self.project_dir.exists():
            raise ProjectDirDoesnotExistError(f"The project directory doesn't exist: {self.project_dir.resolve()}")
        if not self.project_dir.is_dir():
            raise ProjectDirNotDirError(f"The project directory is not a directory: {self.project_dir.resolve()}")

        existing_project = find_project(self.project_dir)
        if existing_project is not None:
            raise DatabaoProjectDirAlreadyExistsError(
                f"Can't initialize Databao project. It already exists - {existing_project.databao_dir.resolve()}"
            )
