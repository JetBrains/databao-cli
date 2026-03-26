"""Interactive CLI workflows for the ask command: REPL, one-shot, and result display."""

import click
from databao.agent import Agent
from databao.agent.core.thread import Thread

from databao_cli.features.ask.display import DEFAULT_MAX_DISPLAY_ROWS, dataframe_to_prettytable
from databao_cli.features.ui.streaming import StreamingWriter
from databao_cli.shared.errors import FeatureError
from databao_cli.shared.log.llm_errors import format_llm_error


def _create_cli_writer() -> StreamingWriter:
    return StreamingWriter(on_write=lambda text: click.echo(text, nl=False))


def _print_help() -> None:
    click.echo("Databao REPL")
    click.echo("Ask questions about your data in natural language.\n")
    click.echo("Commands:")
    click.echo("  \\help   - Show this help")
    click.echo("  \\clear  - Start a new conversation")
    click.echo("  \\q      - Exit\n")


def display_result(thread: Thread) -> None:
    """Display the execution result from a thread to the CLI."""
    text = thread.text()
    if text:
        click.echo(text)

    code = thread.code()
    if code:
        click.echo(f"\n```sql\n{code}\n```")

    df = thread.df()
    if df is not None:
        rows_shown = min(DEFAULT_MAX_DISPLAY_ROWS, len(df))
        click.echo(f"\n[DataFrame: {rows_shown} / {len(df)} rows]")
        click.echo(dataframe_to_prettytable(df))


def run_interactive_mode(agent: Agent, show_thinking: bool) -> None:
    """Run the interactive REPL mode."""
    click.echo("\nDatabao REPL")
    click.echo("\nType \\help for available commands.\n")

    writer = _create_cli_writer() if show_thinking else None

    thread = agent.thread(
        stream_ask=show_thinking,
        writer=writer,
    )

    while True:
        try:
            user_input = click.prompt("You", prompt_suffix="> ")
        except (EOFError, KeyboardInterrupt):
            click.echo()
            break

        user_input = user_input.strip()
        if not user_input:
            continue

        if user_input.startswith("\\"):
            command = user_input[1:].lower()

            if command in ("exit", "quit", "q"):
                break

            if command == "clear":
                if writer:
                    writer.clear()
                thread = agent.thread(
                    stream_ask=show_thinking,
                    writer=writer,
                )
                click.echo("Conversation cleared.\n")
                continue

            if command == "help":
                _print_help()
                continue

            click.echo(f"Unknown command: {user_input}. Type \\help for available commands.\n")
            continue

        try:
            thread.ask(user_input, stream=show_thinking)

            if writer:
                writer.clear()

            click.echo("\nAssistant:")
            display_result(thread)
            click.echo()

        except Exception as e:
            if writer:
                writer.clear()
            click.echo(f"\nError: {format_llm_error(e)}\n", err=True)


def run_one_shot_mode(agent: Agent, question: str, show_thinking: bool) -> None:
    """Run a single question and exit."""
    writer = _create_cli_writer() if show_thinking else None

    thread = agent.thread(
        stream_ask=show_thinking,
        writer=writer,
    )

    try:
        thread.ask(question, stream=show_thinking)
        display_result(thread)

    except Exception as e:
        raise FeatureError(f"Error: {format_llm_error(e)}") from e
