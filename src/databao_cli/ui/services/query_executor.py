"""Background query execution service for chat queries.

This module provides background execution of queries so that they continue
running when users switch between chats. The pattern follows suggestions.py.
"""

import logging
import threading
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, cast

from streamlit.runtime.scriptrunner import add_script_run_ctx, get_script_run_ctx

from databao_cli.ui.components.results import _extract_visualization_data

if TYPE_CHECKING:
    from databao.agent.core.thread import Thread

    from databao_cli.ui.models.chat_session import ChatSession
    from databao_cli.ui.streaming import StreamingWriter

logger = logging.getLogger(__name__)


@dataclass
class QueryResult:
    """Result of a background query execution."""

    text: str
    thinking: str
    result: Any
    has_visualization: bool
    visualization_data: dict[str, Any] | None = None
    error: str | None = None
    viz_pending: bool = False


class QueryThread(threading.Thread):
    """Custom thread for query execution that stores its result.

    The ``phase`` attribute tracks the current execution stage so the UI can
    display appropriate progress indicators.
    """

    def __init__(
        self,
        databao_thread: "Thread",
        query: str,
        writer: "StreamingWriter | None",
    ):
        super().__init__(name="query_worker", daemon=True)
        self.databao_thread = databao_thread
        self.query = query
        self.writer = writer
        self.result: QueryResult | None = None
        self.partial_result: QueryResult | None = None
        self.phase: str = "asking"

    def run(self) -> None:
        """Execute the query and store the result."""
        try:
            self.databao_thread._auto_output_modality = False
            self.databao_thread.ask(self.query, stream=True)
            result = self.databao_thread._data_result

            has_visualization = False
            viz_prompt: str | None = None
            if result and result.meta:
                hints = result.meta.get("output_modality_hints")
                if hints and getattr(hints, "should_visualize", False):
                    has_visualization = True
                    viz_prompt = (
                        f"Last question - {self.query}\nPlot instruction - {getattr(hints, 'visualization_prompt', None)}"
                    )

            if has_visualization:
                thinking_text = self.writer.getvalue() if self.writer else ""
                self.partial_result = QueryResult(
                    text=result.text if result else "",
                    thinking=thinking_text,
                    result=result,
                    has_visualization=False,
                    viz_pending=True,
                )
                self.phase = "visualizing"
                self.databao_thread.plot(viz_prompt)

            if self.databao_thread._visualization_result is not None:
                has_visualization = True

            visualization_data = _extract_visualization_data(self.databao_thread) if has_visualization else None

            thinking_text = self.writer.getvalue() if self.writer else ""

            self.result = QueryResult(
                text=result.text if result else "",
                thinking=thinking_text,
                result=result,
                has_visualization=has_visualization,
                visualization_data=visualization_data,
                error=None,
            )
        except Exception as e:
            logger.exception("Query execution failed")
            thinking_text = self.writer.getvalue() if self.writer else ""
            partial = self.partial_result
            self.result = QueryResult(
                text=partial.text if partial else "",
                thinking=thinking_text,
                result=partial.result if partial else None,
                has_visualization=False,
                error=str(e),
            )


def start_query_execution(chat: "ChatSession", thread: "Thread", query: str) -> bool:
    """Start background query execution for a chat.

    Following Streamlit's recommended pattern for multithreading:
    1. Create the Thread object
    2. Add script context BEFORE starting
    3. Start the thread

    Args:
        chat: The ChatSession to execute the query for.
        thread: The Thread object to use.
        query: The user's question.

    Returns:
        True if execution was started, False if already running.
    """
    if chat.query_status == "running":
        logger.warning(f"Query already running for chat {chat.id}")
        return False

    if chat.writer:
        chat.writer.clear()

    script_ctx = get_script_run_ctx()

    query_thread = QueryThread(thread, query, chat.writer)

    if script_ctx is not None:
        add_script_run_ctx(query_thread, script_ctx)

    query_thread.start()

    chat.query_thread = query_thread
    chat.query_status = "running"

    logger.info(f"Started background query execution for chat {chat.id}: {query[:50]}")
    return True


def check_query_completion(chat: "ChatSession") -> QueryResult | None:
    """Check if a chat's background query has progressed.

    Returns a ``QueryResult`` in two situations:

    1. **Partial** (``viz_pending=True``): the data phase finished but
       visualization is still running.  The UI should create the message
       immediately and show a placeholder for the chart.
    2. **Full**: the entire query (data + optional viz) finished.  If a
       partial message was already created, the UI should update it.

    Thread safety: ``partial_result`` is written once by the background thread
    before it starts the viz phase, and consumed (set to *None*) here.
    ``result`` is only read after confirming the thread is no longer alive.
    """
    if chat.query_status not in ("running", "visualizing"):
        return None

    query_thread: QueryThread | None = cast(QueryThread | None, chat.query_thread)
    if query_thread is None:
        chat.query_status = "idle"
        return None

    if not query_thread.is_alive():
        result = query_thread.result
        if result is None:
            result = QueryResult(
                text="",
                thinking="",
                result=None,
                has_visualization=False,
                error="Thread finished without result",
            )

        chat.query_thread = None
        chat.query_status = "completed" if result.error is None else "error"

        logger.info(f"Query completed for chat {chat.id}: success={result.error is None}")
        return result

    # Thread still alive — check for partial result (data done, viz in progress)
    if chat.query_status == "running" and query_thread.partial_result is not None:
        partial = query_thread.partial_result
        query_thread.partial_result = None
        chat.query_status = "visualizing"
        return partial

    return None


def is_query_running(chat: "ChatSession") -> bool:
    """Check if a chat has a query currently running (data or visualization phase).

    Args:
        chat: The ChatSession to check.

    Returns:
        True if a query is in progress.
    """
    return chat.query_status in ("running", "visualizing")


def get_query_phase(chat: "ChatSession") -> str | None:
    """Return the current execution phase of the running query, or None if idle.

    Possible phases: ``"asking"``, ``"visualizing"``.
    """
    qt = chat.query_thread
    if isinstance(qt, QueryThread):
        return qt.phase
    return None
