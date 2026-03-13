from pathlib import Path

import click
import questionary
from click import Context


def _is_initialized(project_dir: Path) -> bool:
    return (project_dir / "databao.yml").exists()


def _interactive_menu(project_dir: Path) -> None:
    """Show interactive command menu after initialization or when already initialized."""
    action = questionary.select(
        "What would you like to do?",
        choices=[
            questionary.Choice("Open Claude Code with Databao", value="claude"),
            questionary.Choice("Start web interface", value="app"),
            questionary.Choice("Sync introspections", value="sync"),
            questionary.Choice("Re-initialize project", value="init"),
        ],
    ).ask()

    if action is None:
        return

    if action == "app":
        from databao_mock.commands.app import app_impl
        app_impl(project_dir)
    elif action == "claude":
        from databao_mock.commands.claude import claude_impl
        claude_impl(project_dir)
    elif action == "sync":
        from databao_mock.commands.sync import sync_impl
        sync_impl(project_dir)
    elif action == "init":
        from databao_mock.commands.init import init_impl
        # Remove databao.yml so init_impl doesn't block re-init
        (project_dir / "databao.yml").unlink(missing_ok=True)
        init_impl(project_dir)
        _interactive_menu(project_dir)


@click.group(invoke_without_command=True)
@click.option(
    "-p",
    "--project-dir",
    type=click.Path(file_okay=False, path_type=Path),
    help="Location of your Databao project (default: current directory)",
)
@click.pass_context
def cli(ctx: Context, project_dir: Path | None) -> None:
    """Databao CLI"""
    ctx.ensure_object(dict)
    ctx.obj["project_dir"] = Path.cwd() if project_dir is None else project_dir.expanduser().resolve()

    from databao_mock.header import print_header
    print_header(ctx.obj["project_dir"])

    if ctx.invoked_subcommand is None:
        project_dir = ctx.obj["project_dir"]
        if _is_initialized(project_dir):
            _interactive_menu(project_dir)
        else:
            from databao_mock.commands.init import init_impl
            init_impl(project_dir)
            _interactive_menu(project_dir)


@cli.command()
@click.pass_context
def init(ctx: Context) -> None:
    """Initialize a Databao project."""
    from databao_mock.commands.init import init_impl
    init_impl(ctx.obj["project_dir"])


@cli.command()
@click.pass_context
def app(ctx: Context) -> None:
    """Start the Databao web interface."""
    from databao_mock.commands.app import app_impl
    app_impl(ctx.obj["project_dir"])


@cli.command()
@click.pass_context
def claude(ctx: Context) -> None:
    """Open Claude Code with Databao skill."""
    from databao_mock.commands.claude import claude_impl
    claude_impl(ctx.obj["project_dir"])


@cli.command()
@click.pass_context
def sync(ctx: Context) -> None:
    """Sync source schemas and introspections."""
    from databao_mock.commands.sync import sync_impl
    sync_impl(ctx.obj["project_dir"])


if __name__ == "__main__":
    cli()
