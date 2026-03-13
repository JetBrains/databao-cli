import sys
from pathlib import Path

import click
from click import Context

from databao_cli.log.logging import configure_logging
from databao_cli.project.layout import ROOT_DOMAIN, ProjectLayout, find_project


@click.group()
@click.option(
    "-p",
    "--project-dir",
    type=click.Path(file_okay=False, path_type=Path),
    help="Location of your Databao project",
)
@click.pass_context
def cli(ctx: Context, project_dir: Path | None) -> None:
    """Databao Common CLI"""
    project_path = Path.cwd() if project_dir is None else project_dir.expanduser().resolve()

    configure_logging()

    ctx.ensure_object(dict)
    ctx.obj["project_dir"] = project_path


@cli.command()
@click.pass_context
def status(ctx: Context) -> None:
    """Display project status and system-wide information."""
    from databao_cli.commands.status import status_impl

    status_message = status_impl(ctx.obj["project_dir"])
    click.echo(status_message)


@cli.command()
@click.pass_context
def init(ctx: Context) -> None:
    """Create a new Databao project."""
    from databao_cli.commands.datasource.add_datasource_config import add_datasource_config_interactive_impl
    from databao_cli.commands.init import InitDatabaoProjectError, ProjectDirDoesnotExistError, init_impl

    project_dir = ctx.obj["project_dir"]
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

    # todo install ollama
    # try:
    #     install_ollama_if_needed()
    # except RuntimeError as e:
    #     click.echo(str(e), err=True)

    if not click.confirm("\nDo you want to configure a domain now?"):
        return

    add_datasource_config_interactive_impl(project_layout, ROOT_DOMAIN)

    while click.confirm("\nDo you want to add more datasources?"):
        add_datasource_config_interactive_impl(project_layout, ROOT_DOMAIN)


@cli.group()
def datasource() -> None:
    """Manage datasource configurations."""
    pass


@datasource.command(name="add")
@click.option(
    "-d",
    "--domain",
    type=click.STRING,
    default="root",
    help="Databao domain name",
)
@click.pass_context
def add_datasource_config(ctx: Context, domain: str) -> None:
    """Add a new datasource configuration.

    The command will ask all relevant information for that datasource and save it in a chosen Databao domain
    """
    from databao_cli.commands.datasource.add_datasource_config import add_datasource_config_interactive_impl

    project_layout = _get_project_or_exit(ctx.obj["project_dir"])
    add_datasource_config_interactive_impl(project_layout, domain)


@datasource.command(name="check")
@click.argument(
    "domains",
    type=click.STRING,
    nargs=-1,
)
@click.pass_context
def check_datasource_config(ctx: Context, domains: list[str] | None) -> None:
    """Check whether a datasource configuration is valid.

    The configuration is considered as valid if a connection with the datasource can be established.

    By default, all declared datasources across all domains in the project will be checked.
    You can explicitely list which domains to validate by using the [DOMAINS] argument.
    """
    from databao_cli.commands.datasource.check_datasource_connection import check_datasource_connection_impl

    project_layout = _get_project_or_exit(ctx.obj["project_dir"])
    check_datasource_connection_impl(project_layout, requested_domains=domains if domains else None)


@cli.command()
@click.option(
    "-d",
    "--domain",
    type=click.STRING,
    default="root",
    help="Databao domain name",
)
@click.option(
    "--should-index/--should-not-index",
    default=True,
    show_default=True,
    help="Whether to index the context. If disabled, the context will be built but not indexed.",
)
@click.pass_context
def build(ctx: Context, domain: str, should_index: bool) -> None:
    """Build context for all domain's datasources.

    The output of the build command will be saved in the domain's output directory.

    Internally, this indexes the context to be used by the MCP server and the "retrieve" command.
    """
    from databao_cli.commands.build import build_impl

    project_layout = _get_project_or_exit(ctx.obj["project_dir"])
    results = build_impl(project_layout, domain, should_index)
    click.echo(f"Build complete. Processed {len(results)} datasources.")


@cli.command()
@click.argument("question", required=False)
@click.option(
    "--one-shot",
    is_flag=True,
    default=False,
    help="Run single question and exit (default: interactive mode)",
)
@click.option(
    "-m",
    "--model",
    type=str,
    default=None,
    help="LLM model in format provider:name (e.g., openai:gpt-4o, anthropic:claude-sonnet-4-6)",
)
@click.option(
    "-t",
    "--temperature",
    type=float,
    default=0.0,
    help="Temperature 0.0-1.0 (default: 0.0)",
)
@click.option(
    "--show-thinking/--no-show-thinking",
    default=True,
    help="Display reasoning/thinking output (streaming is implicit when enabled)",
)
@click.pass_context
def ask(
    ctx: click.Context,
    question: str | None,
    one_shot: bool,
    model: str | None,
    temperature: float,
    show_thinking: bool,
) -> None:
    """Chat with the Databao agent.

    By default, starts an interactive chat session. Use --one-shot with a
    QUESTION argument to run a single query and exit.

    \b
    Examples:
        databao ask                                          # Interactive mode
        databao ask --one-shot "What tables exist?"          # One-shot mode
        databao ask --model anthropic:claude-sonnet-4-6      # With custom model
        databao ask --no-show-thinking                       # Hide reasoning
    """
    from databao_cli.commands.ask import ask_impl

    ask_impl(ctx, question, one_shot, model, temperature, show_thinking)


@cli.command(
    context_settings={"ignore_unknown_options": True, "allow_extra_args": True},
)
@click.option(
    "--read-only-domain",
    is_flag=True,
    default=False,
    help="Disable all domain-editing operations (init, datasources, build) in the UI",
)
@click.option(
    "--hide-suggested-questions",
    is_flag=True,
    default=False,
    help="Hide the suggested questions on the empty chat screen",
)
@click.option(
    "--hide-build-context-hint",
    is_flag=True,
    default=False,
    help=(
        "Hide the 'Context isn't built yet' warning on the empty chat screen and "
        "remove the Build Context step from the setup wizard"
    ),
)
@click.pass_context
def app(ctx: click.Context, read_only_domain: bool, hide_suggested_questions: bool, hide_build_context_hint: bool) -> None:
    """Launch the Databao Streamlit web interface.

    All additional arguments are passed directly to streamlit run.

    \b
    Examples:
        databao app
        databao app --server.port 8502
        databao app --server.headless true
        databao app --read-only-domain
    """
    from databao_cli.commands.app import app_impl

    ctx.obj["read_only_domain"] = read_only_domain
    ctx.obj["hide_suggested_questions"] = hide_suggested_questions
    ctx.obj["hide_build_context_hint"] = hide_build_context_hint
    app_impl(ctx)


@cli.command()
@click.option(
    "--transport",
    type=click.Choice(["stdio", "sse"]),
    default="stdio",
    show_default=True,
    help="MCP transport type.",
)
@click.option(
    "--host",
    type=str,
    default="localhost",
    show_default=True,
    help="Host to bind to (SSE transport only).",
)
@click.option(
    "--port",
    type=int,
    default=8765,
    show_default=True,
    help="Port to listen on (SSE transport only).",
)
@click.pass_context
def mcp(ctx: click.Context, transport: str, host: str, port: int) -> None:
    """Run an MCP server exposing Databao tools.

    Starts a Model Context Protocol server that provides tools for
    interacting with your Databao project programmatically.

    \b
    Examples:
        databao mcp                              # stdio (default)
        databao mcp --transport sse              # SSE on localhost:8765
        databao mcp --transport sse --port 9000  # SSE on custom port
    """
    from databao_cli.commands.mcp import mcp_impl

    mcp_impl(ctx.obj["project_dir"], transport, host, port)


def _get_project_or_exit(project_dir: Path) -> ProjectLayout:
    project_layout = find_project(project_dir)
    if not project_layout:
        click.echo("No project found.")
        exit(1)
    return project_layout


if __name__ == "__main__":
    cli()
