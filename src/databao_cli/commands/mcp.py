"""databao mcp command - Run an MCP server exposing Databao tools."""

from pathlib import Path

from databao_cli.mcp.server import McpContext, run_server


def mcp_impl(project_dir: Path, transport: str, host: str, port: int) -> None:
    context = McpContext(project_dir=project_dir)
    run_server(context, transport=transport, host=host, port=port)
