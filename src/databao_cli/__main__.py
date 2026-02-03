from pathlib import Path

import click
from click import Context

from databao_cli.commands.app import app_impl
from databao_cli.commands.ask import ask_impl
from databao_cli.commands.status import status_impl


@click.group()
@click.option(
    "-p",
    "--project-dir",
    type=click.Path(file_okay=False, path_type=Path),
    help="Location of your Databao Context Engine project",
)
@click.pass_context
def cli(ctx: Context, project_dir: Path | None):
    """Databao Common CLI"""
    if project_dir is None:
        project_path = Path.cwd()
    else:
        project_path = project_dir.expanduser().resolve()

    ctx.ensure_object(dict)
    ctx.obj["project_dir"] = project_path


@cli.command()
@click.pass_context
def status(ctx: Context) -> None:
    """Display project status and system-wide information."""
    status_impl(ctx.obj["project_dir"])


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
    help="LLM model in format provider:name (e.g., openai:gpt-4o, anthropic:claude-3-5-sonnet)",
)
@click.option(
    "-t",
    "--temperature",
    type=float,
    default=0.0,
    help="Temperature 0.0-1.0 (default: 0.0)",
)
@click.option(
    "--show-thinking",
    is_flag=True,
    default=False,
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

    Examples:
        databao ask                                          # Interactive mode
        databao ask --one-shot "What tables exist?"          # One-shot mode
        databao ask --model anthropic:claude-3-5-sonnet      # With custom model
        databao ask --show-thinking                          # Show reasoning
    """
    ask_impl(ctx, question, one_shot, model, temperature, show_thinking)


@cli.command(
    context_settings={"ignore_unknown_options": True, "allow_extra_args": True},
)
@click.pass_context
def app(ctx: click.Context) -> None:
    """Launch the Databao Streamlit web interface.

    All additional arguments are passed directly to streamlit run.

    Examples:
        databao app
        databao app --server.port 8502
        databao app --server.headless true
    """
    app_impl(ctx)


if __name__ == "__main__":
    cli()
