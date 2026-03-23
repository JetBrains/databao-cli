import sys
from pathlib import Path

import click
from databao_context_engine import InitDomainError, init_dce_domain

from databao_cli.project.layout import ROOT_DOMAIN, ProjectLayout, find_project


@click.command()
@click.pass_context
def init(ctx: click.Context) -> None:
    """Create a new Databao project."""
    from databao_cli.commands.datasource.add_datasource_config import add_datasource_config_interactive_impl

    project_dir: Path = ctx.obj["project_dir"]
    project_layout: ProjectLayout
    try:
        project_layout = init_impl(project_dir)
    except ProjectDirDoesnotExistError:
        if click.confirm(
            f"The directory {project_dir.resolve()} does not exist. Do you want to create it?",
            default=True,
        ):
            project_dir.mkdir(parents=True, exist_ok=False)
            project_layout = init_impl(project_dir)
        else:
            return
    except InitDatabaoProjectError as e:
        click.echo(e.message, err=True)
        sys.exit(1)

    click.echo(f"Project initialized successfully at {project_dir.resolve()}")

    if not click.confirm("\nDo you want to configure a domain now?"):
        return

    add_datasource_config_interactive_impl(project_layout, ROOT_DOMAIN)

    while click.confirm("\nDo you want to add more datasources?"):
        add_datasource_config_interactive_impl(project_layout, ROOT_DOMAIN)


class InitDatabaoProjectError(ValueError):
    def __init__(self, message: str | None):
        super().__init__(message or "")
        self.message = message


class DatabaoProjectDirAlreadyExistsError(InitDatabaoProjectError):
    def __init__(self, message: str) -> None:
        super().__init__(message)


class ParentDatabaoProjectAlreadyExistsError(InitDatabaoProjectError):
    def __init__(self, message: str) -> None:
        super().__init__(message)


class ProjectDirDoesnotExistError(InitDatabaoProjectError):
    def __init__(self, message: str) -> None:
        super().__init__(message)


class ProjectDirNotDirError(InitDatabaoProjectError):
    def __init__(self, message: str) -> None:
        super().__init__(message)


class DatabaoContextEngineProjectInitError(InitDatabaoProjectError):
    def __init__(self, message: str) -> None:
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
            raise DatabaoContextEngineProjectInitError(str(e)) from e

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
