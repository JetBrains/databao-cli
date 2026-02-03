"""databao ask command - Interactive CLI chat with the Databao agent."""

import io
import sys
from pathlib import Path

import click
import pandas as pd
from databao import Agent
from prettytable import PrettyTable
from databao.core.thread import Thread

# Default maximum number of rows to display in dataframe output
DEFAULT_MAX_DISPLAY_ROWS = 10


class CLIStreamingWriter(io.StringIO):
    """A writer that streams output to CLI in real-time.

    Extends StringIO to capture all output while simultaneously echoing
    every write to stdout immediately for real-time display.
    """

    def __init__(self) -> None:
        super().__init__()

    def write(self, text: str) -> int:
        """Write text to buffer and echo to stdout."""
        result = super().write(text)
        click.echo(text, nl=False)
        return result

    def clear(self) -> None:
        """Clear the buffer."""
        self.seek(0)
        self.truncate(0)


def dataframe_to_prettytable(df: pd.DataFrame, max_rows: int = DEFAULT_MAX_DISPLAY_ROWS) -> str:
    """Convert a pandas DataFrame to a prettytable string."""
    table = PrettyTable()
    table.field_names = list(df.columns)
    for _, row in df.head(max_rows).iterrows():
        table.add_row([str(v) for v in row])
    return str(table)


def initialize_agent_from_dce(project_path: Path, model: str | None, temperature: float) -> Agent:
    """Initialize the Databao agent using DCE project at the given path."""
    import databao
    from databao.configs.llm import LLMConfig, LLMConfigDirectory
    from databao.dce import (
        DCEProjectStatus,
        create_all_connections,
        get_all_context,
    )
    from databao.dce.project import validate_project

    # Validate DCE project
    project = validate_project(project_path)

    if project.status == DCEProjectStatus.NOT_FOUND:
        click.echo(f"No DCE project found at {project_path}. Run 'databao init' first.", err=True)
        sys.exit(1)

    if project.status == DCEProjectStatus.NO_BUILD:
        click.echo(f"DCE project found at {project.path} but no build output. Run 'databao build' first.", err=True)
        sys.exit(1)

    click.echo(f"Using DCE project: {project.path}")

    # Create LLM config
    if model:
        llm_config = LLMConfig(name=model, temperature=temperature)
    else:
        # Use default but with custom temperature if provided
        if temperature != 0.0:
            llm_config = LLMConfig(
                name=LLMConfigDirectory.DEFAULT.name,
                temperature=temperature,
            )
        else:
            llm_config = LLMConfigDirectory.DEFAULT

    # Create agent
    agent = databao.new_agent(llm_config=llm_config)

    # Connect to databases
    connections = create_all_connections(project.path)
    if not connections:
        click.echo("No datasource connections found in DCE project.", err=True)
        sys.exit(1)

    # Load context
    db_contexts: list[databao.dce.DatabaseContext] = []
    file_contexts: list[databao.dce.FileContext] = []
    if project.latest_run_dir:
        db_contexts, file_contexts = get_all_context(project.latest_run_dir)

    db_context_map = {ctx.database_id: ctx.context_text for ctx in db_contexts}

    # Add databases to agent
    for conn_info in connections:
        context = db_context_map.get(conn_info.name) or db_context_map.get(conn_info.db_type)
        agent.add_db(conn_info.connection, name=conn_info.name, context=context)

    # Add file contexts
    for file_ctx in file_contexts:
        agent.add_context(file_ctx.context_text)

    click.echo(f"Connected to {len(connections)} data source(s)")
    return agent


def display_result(thread: Thread) -> None:
    """Display the execution result from thread to CLI."""
    # Display text response
    text = thread.text()
    if text:
        click.echo(text)

    # Display SQL code if present
    code = thread.code()
    if code:
        click.echo(f"\n```sql\n{code}\n```")

    # Display dataframe if present
    df = thread.df()
    if df is not None:
        rows_shown = min(DEFAULT_MAX_DISPLAY_ROWS, len(df))
        click.echo(f"\n[DataFrame: {rows_shown} / {len(df)} rows]")
        click.echo(dataframe_to_prettytable(df))


def _print_help() -> None:
    """Print help message for interactive mode."""
    click.echo("Databao REPL")
    click.echo("Ask questions about your data in natural language.\n")
    click.echo("Commands:")
    click.echo("  \\help   - Show this help")
    click.echo("  \\clear  - Start a new conversation")
    click.echo("  \\q      - Exit\n")


def run_interactive_mode(agent: Agent, show_thinking: bool) -> None:
    """Run the interactive REPL mode."""
    click.echo("\nDatabao REPL")
    click.echo("\nType \\help for available commands.\n")

    if show_thinking:
        writer = CLIStreamingWriter()
    else:
        writer = None

    # Create thread with writer for streaming
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

        # Check if it's a command (starts with \)
        if user_input.startswith("\\"):
            command = user_input[1:].lower()

            if command in ("exit", "quit", "q"):
                break

            if command == "clear":
                # Clear writer and create new thread
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

        # Process as a question
        try:
            thread.ask(user_input, stream=show_thinking)

            # Clear writer buffer if present
            if writer:
                writer.clear()

            # Display result
            click.echo("\nAssistant:")
            display_result(thread)
            click.echo()

        except Exception as e:
            if writer:
                writer.clear()
            click.echo(f"\nError: {e}\n", err=True)


def run_one_shot_mode(agent: Agent, question: str, show_thinking: bool) -> None:
    """Run a single question and exit."""

    if show_thinking:
        writer = CLIStreamingWriter()
    else:
        writer = None

    # Create thread with writer for streaming
    thread = agent.thread(
        stream_ask=show_thinking,
        writer=writer,
    )

    try:
        # Execute with streaming enabled when showing thinking
        thread.ask(question, stream=show_thinking)

        # Display result
        display_result(thread)

    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


def ask_impl(
    ctx: click.Context,
    question: str | None,
    one_shot: bool,
    model: str | None,
    temperature: float,
    show_thinking: bool,
) -> None:
    # Validate arguments
    if one_shot and not question:
        click.echo("Error: QUESTION argument is required in one-shot mode.", err=True)
        sys.exit(1)

    # Get project path from CLI context
    project_path: Path = ctx.obj["project_dir"]

    # Initialize agent (with progress indicator if not showing thinking)
    if not show_thinking:
        click.echo("Initializing agent...")
    agent = initialize_agent_from_dce(project_path, model, temperature)

    # Run appropriate mode
    if one_shot:
        run_one_shot_mode(agent, question, show_thinking)
    else:
        run_interactive_mode(agent, show_thinking)
