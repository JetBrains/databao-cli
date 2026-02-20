"""databao_ask MCP tool - one-shot query to the Databao agent."""

import json
import logging
from typing import TYPE_CHECKING, Annotated, Any

from databao.caches.in_mem_cache import InMemCache
from langchain_core.messages import AIMessage, HumanMessage
from pydantic import BaseModel, Field

from databao_cli.mcp.tools._agent_factory import create_agent_for_tool

if TYPE_CHECKING:
    from fastmcp import FastMCP

    from databao_cli.mcp.server import McpContext

logger = logging.getLogger(__name__)

DEFAULT_MAX_DATA_ROWS = 50
_CACHE_SCOPE = "mcp"


class Message(BaseModel):
    """OpenAI-compatible chat message."""

    role: str = Field(description="Message role: 'user' or 'assistant'")
    content: str = Field(description="Message text content")


def _to_langchain_messages(messages: list[Message]) -> list[HumanMessage | AIMessage]:
    """Convert OpenAI-format messages to LangChain message objects.

    Only user (HumanMessage) and assistant (AIMessage) roles are converted.
    """
    result: list[HumanMessage | AIMessage] = []
    for msg in messages:
        if msg.role == "user":
            result.append(HumanMessage(content=msg.content))
        elif msg.role == "assistant":
            result.append(AIMessage(content=msg.content))
    return result


def register(mcp: "FastMCP", context: "McpContext") -> None:
    """Register the databao_ask tool with the MCP server."""

    @mcp.tool()
    def databao_ask(
        messages: Annotated[
            list[Message],
            Field(description="Conversation history in OpenAI-compatible format. Last message must have role 'user'."),
        ],
        model: Annotated[
            str | None,
            Field(description="LLM model in provider:name format (e.g. 'openai:gpt-4o')."),
        ] = None,
        temperature: Annotated[
            float,
            Field(description="Sampling temperature, 0.0 to 1.0."),
        ] = 0.0,
        executor: Annotated[
            str,
            Field(description="Execution engine: 'lighthouse' (default) or 'react_duckdb'."),
        ] = "lighthouse",
        max_data_rows: Annotated[
            int,
            Field(description="Maximum number of data rows to return in the response."),
        ] = DEFAULT_MAX_DATA_ROWS,
    ) -> str:
        """Ask the Databao agent a question about your data.

        Sends a one-shot query to the Databao agent, which can answer questions
        about your configured data sources using natural language.

        The messages array carries conversation history. Pass the returned messages
        back on subsequent calls to maintain conversation context.
        """
        if not messages:
            return _error("messages must not be empty")

        last = messages[-1]
        if last.role != "user":
            return _error("Last message must have role 'user'")

        query = last.content
        history = messages[:-1]

        cache = InMemCache()
        if history:
            langchain_history = _to_langchain_messages(history)
            cache.scoped(_CACHE_SCOPE).put("state", {"messages": langchain_history})

        try:
            agent = create_agent_for_tool(
                project_dir=context.project_dir,
                model=model,
                temperature=temperature,
                executor=executor,
                cache=cache,
            )
        except Exception as e:
            logger.exception("Failed to initialize agent")
            return _error(f"Agent initialization failed: {e}")

        try:
            thread = agent.thread(stream_ask=False, cache_scope=_CACHE_SCOPE)
            thread.ask(query)

            text = thread.text() or ""
            sql = thread.code()
            df = thread.df()

            data_table: str | None = None
            if df is not None and not df.empty:
                data_table = df.head(max_data_rows).to_markdown(index=False)

            result: dict[str, Any] = {
                "text": text,
                "sql": sql,
                "data": data_table,
            }
            return json.dumps(result, default=str)

        except Exception as e:
            logger.exception("Query execution failed")
            return _error(f"Query failed: {e}")


def _error(message: str) -> str:
    return json.dumps({"error": message})
