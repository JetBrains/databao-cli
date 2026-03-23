"""databao mcp command - Run an MCP server exposing Databao tools."""

import click

from databao_cli.shared.cli_utils import handle_feature_errors


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
@handle_feature_errors
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
    from databao_cli.features.mcp.server import mcp_impl
    from databao_cli.shared.log.logging import configure_logging
    from databao_cli.shared.project.layout import find_project

    if transport == "stdio":
        configure_logging(find_project(ctx.obj["project_dir"]), quiet=True)
    mcp_impl(ctx.obj["project_dir"], transport, host, port)
