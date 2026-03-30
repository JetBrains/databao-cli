"""Databao MCP server setup and tool registration."""

from dataclasses import dataclass

from fastmcp import FastMCP

from databao_cli.features.mcp.tools import databao_ask
from databao_cli.features.mcp.tools import database_context as database_context_tools
from databao_cli.shared.project.layout import ProjectLayout


@dataclass(frozen=True)
class McpContext:
    """Shared context available to all MCP tools."""

    project_layout: ProjectLayout


def create_server(context: McpContext) -> FastMCP:
    """Create a FastMCP server with all registered tools."""
    mcp = FastMCP("databao")
    databao_ask.register(mcp, context)
    database_context_tools.register(mcp, context)
    return mcp


def run_server(
    context: McpContext,
    transport: str = "stdio",
    host: str = "localhost",
    port: int = 8765,
) -> None:
    """Create and run the MCP server with the given transport."""
    mcp = create_server(context)

    match transport:
        case "stdio":
            mcp.run(transport="stdio", show_banner=False)
        case "sse":
            mcp.run(transport="sse", host=host, port=port, show_banner=False)
        case _:
            raise ValueError(f"Unknown transport: {transport!r}. Supported: stdio, sse")


def mcp_impl(project_layout: ProjectLayout, transport: str, host: str, port: int) -> None:
    context = McpContext(project_layout=project_layout)
    run_server(context, transport=transport, host=host, port=port)
