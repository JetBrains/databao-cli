"""databao mcp command - Run an MCP server exposing Databao tools."""

from pathlib import Path

import click

from databao_cli.mcp.server import McpContext, run_server


@click.command()
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
    from databao_cli.log.logging import configure_logging
    from databao_cli.project.layout import find_project

    if transport == "stdio":
        configure_logging(find_project(ctx.obj["project_dir"]), quiet=True)
    mcp_impl(ctx.obj["project_dir"], transport, host, port)


def mcp_impl(project_dir: Path, transport: str, host: str, port: int) -> None:
    context = McpContext(project_dir=project_dir)
    run_server(context, transport=transport, host=host, port=port)
