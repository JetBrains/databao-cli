"""databao ask command - Interactive CLI chat with the Databao agent."""

import click

from databao_cli.shared.cli_utils import handle_feature_errors


@click.command()
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
@handle_feature_errors
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
    from databao_cli.features.ask.service import ask_impl
    from databao_cli.workflows.ask import run_interactive_mode, run_one_shot_mode

    if not show_thinking:
        click.echo("Initializing agent...")
    agent = ask_impl(ctx.obj["project_dir"], question, one_shot, model, temperature)

    if one_shot:
        assert question is not None
        run_one_shot_mode(agent, question, show_thinking)
    else:
        run_interactive_mode(agent, show_thinking)
