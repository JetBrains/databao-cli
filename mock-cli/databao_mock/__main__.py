from pathlib import Path

import click
import questionary
from click import Context


def _databao_yml(project_dir: Path) -> Path:
    return project_dir / ".databao" / "databao.yml"


def _is_initialized(project_dir: Path) -> bool:
    databao_yml = _databao_yml(project_dir)
    if not databao_yml.exists():
        return False
    import yaml
    try:
        with open(databao_yml) as f:
            config = yaml.safe_load(f) or {}
    except Exception:
        return False
    return bool(config.get("dbt"))


def _interactive_menu(project_dir: Path) -> None:
    """Show interactive command menu, looping until the user quits."""
    while True:
        action = questionary.select(
            "What would you like to do?",
            choices=[
                questionary.Choice("Open Claude Code with Databao", value="claude"),
                questionary.Choice("Deploy Slack Bot", value="deploy"),
                questionary.Choice("Refresh metadata", value="sync"),
                questionary.Choice("Quit", value="quit"),
            ],
        ).ask()

        if action is None or action == "quit":
            return

        if action == "deploy":
            from databao_mock.commands.deploy import deploy_impl
            deploy_impl(project_dir)
        elif action == "claude":
            from databao_mock.commands.claude import claude_impl
            claude_impl(project_dir, on_exit=lambda: None)
        elif action == "sync":
            from databao_mock.commands.sync import sync_impl
            sync_impl(project_dir)



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

    project_dir = ctx.obj["project_dir"]

    if ctx.invoked_subcommand is None:
        from databao_mock.commands.login import is_logged_in, login_impl
        if not is_logged_in(project_dir):
            ctx.obj["pending_user"] = login_impl(project_dir)

        from databao_mock.header import print_header
        print_header(project_dir)

    if ctx.invoked_subcommand is None:
        if _is_initialized(project_dir):
            _interactive_menu(project_dir)
        else:
            from databao_mock.commands.init import init_impl
            init_impl(project_dir, pending_user=ctx.obj.get("pending_user"))
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


@cli.command()
@click.pass_context
def login(ctx: Context) -> None:
    """Log in to Databao."""
    from databao_mock.commands.login import login_impl
    login_impl(ctx.obj["project_dir"])


@cli.command()
@click.option("--skip-git-check", is_flag=True, default=False, hidden=True)
@click.pass_context
def deploy(ctx: Context, skip_git_check: bool) -> None:
    """Deploy the Databao Slack Bot."""
    from databao_mock.commands.deploy import deploy_impl
    deploy_impl(ctx.obj["project_dir"], skip_git_check=skip_git_check)


if __name__ == "__main__":
    cli()
