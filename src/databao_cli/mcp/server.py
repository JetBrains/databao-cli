"""Databao MCP server setup and tool registration."""

from dataclasses import dataclass
from pathlib import Path

from fastmcp import FastMCP

from databao_cli.mcp.tools import databao_ask


@dataclass(frozen=True)
class McpContext:
    """Shared context available to all MCP tools."""

    project_dir: Path


def create_server(context: McpContext) -> FastMCP:
    """Create a FastMCP server with all registered tools."""
    mcp = FastMCP("databao")
    databao_ask.register(mcp, context)
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
            mcp.run(transport="stdio")
        case "sse":
            mcp.run(transport="sse", host=host, port=port)
        case _:
            raise ValueError(f"Unknown transport: {transport!r}. Supported: stdio, sse")
