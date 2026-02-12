"""Chat interface component with streaming support."""

from typing import TYPE_CHECKING

import streamlit as st

from databao_cli.ui.components.results import render_execution_result
from databao_cli.ui.models.chat_session import ChatMessage
from databao_cli.ui.services import (
    check_query_completion,
    is_query_running,
    save_current_chat,
    start_query_execution,
)
from databao_cli.ui.suggestions import (
    check_suggestions_completion,
    is_suggestions_loading,
    start_suggestions_generation,
)

if TYPE_CHECKING:
    from databao_cli.ui.models.chat_session import ChatSession

def render_user_message(message: ChatMessage) -> None:
    """Render a user message."""
    with st.chat_message("user"):
        st.markdown(message.content)

def render_assistant_message(
    message: ChatMessage, chat: "ChatSession", message_index: int, *, is_latest: bool = False
) -> None:
    """Render an assistant message with results."""
    with st.chat_message("assistant"):
        if message.thinking:
            with st.expander("💭 Thinking", expanded=False):
                st.markdown(message.thinking)

        if message.result and chat.thread is not None:
            render_execution_result(
                result=message.result,
                chat=chat,
                message_index=message_index,
                has_visualization=message.has_visualization,
                is_latest=is_latest,
                visualization_data=message.visualization_data,
            )

def _truncate_question(question: str, max_len: int = 60) -> tuple[str, bool]:
    """Truncate a question for display, returning (display_text, was_truncated)."""
    if len(question) <= max_len:
        return question, False
    return question[: max_len - 3] + "...", True

@st.fragment
def render_welcome_component(chat: "ChatSession") -> None:
    """Render the welcome component with greeting and suggested questions.

    This is a fragment so it has an independent render lifecycle from the main page.
    When the main page reruns for processing, this fragment can be cleanly removed
    without showing stale elements.

    It handles these states:
    - not_started: starts background generation, shows loading
    - loading: shows "Analyzing your data..." with no buttons (polls for completion)
    - ready: shows questions with appropriate subtitle
    """
    status = st.session_state.get("suggestions_status", "not_started")

    if status == "not_started":
        agent = st.session_state.get("agent")
        if agent is not None:
            start_suggestions_generation(agent)
            status = "loading"

    st.markdown("<div style='height: 15vh'></div>", unsafe_allow_html=True)

    st.markdown(
        """
        <div style='text-align: center;'>
            <h2>Welcome to Databao!</h2>
            <p style='color: gray; font-size: 1.1em;'>
                Ask questions about your data and get instant insights with tables and visualizations.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if status == "loading":
        st.markdown(
            "<p style='text-align: center; color: #888; font-size: 0.9em; margin-top: 1em;'>"
            "🔄 Analyzing your data to suggest questions..."
            "</p>",
            unsafe_allow_html=True,
        )
        return

    questions: list[str] = st.session_state.get("suggested_questions", [])
    is_llm_generated: bool = st.session_state.get("suggestions_are_llm_generated", False)

    if questions:
        if is_llm_generated:
            st.markdown(
                "<p style='text-align: center; color: #888; font-size: 0.9em; margin-top: 1em;'>"
                "✨ These questions were generated based on your data"
                "</p>",
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                "<p style='text-align: center; color: #888; font-size: 0.9em; margin-top: 1em;'>"
                "Try these questions to get started"
                "</p>",
                unsafe_allow_html=True,
            )

        st.markdown("<div style='height: 2em'></div>", unsafe_allow_html=True)

        cols = st.columns(len(questions))
        for i, (col, question) in enumerate(zip(cols, questions, strict=True)):
            with col:
                display_text, was_truncated = _truncate_question(question)

                help_text = question if was_truncated else None
                if st.button(display_text, key=f"suggested_q_{i}", width="stretch", help=help_text):
                    if chat.thread is not None:
                        user_message = ChatMessage(role="user", content=question)
                        chat.messages.append(user_message)
                        save_current_chat()
                        start_background_query(chat, question)
                    st.rerun(scope="app")
    else:
        st.markdown(
            "<p style='text-align: center; color: #888; font-size: 0.9em; margin-top: 1em;'>"
            "Type your question below to get started"
            "</p>",
            unsafe_allow_html=True,
        )

def _get_current_chat() -> "ChatSession | None":
    """Get the current chat session from session state."""
    current_chat_id = st.session_state.get("current_chat_id")
    chats = st.session_state.get("chats", {})
    if current_chat_id and current_chat_id in chats:
        return chats[current_chat_id]
    return None

def render_chat_history(chat: "ChatSession") -> None:
    """Render all messages in chat history."""
    messages: list[ChatMessage] = chat.messages

    is_processing = is_query_running(chat)

    last_assistant_idx = -1
    for i, msg in enumerate(messages):
        if msg.role == "assistant":
            last_assistant_idx = i

    for i, message in enumerate(messages):
        if message.role == "user":
            render_user_message(message)
        else:
            is_latest = (i == last_assistant_idx) and not is_processing
            render_assistant_message(message, chat, i, is_latest=is_latest)

def start_background_query(chat: "ChatSession", query: str) -> None:
    """Start a background query execution for the chat.

    Args:
        chat: The ChatSession to execute the query for (must have thread set).
        query: The user's question.
    """
    if is_query_running(chat):
        return

    if chat.thread is None:
        return

    start_query_execution(chat, chat.thread, query)

def handle_query_completion(chat: "ChatSession") -> bool:
    """Check if query completed and create assistant message if so.

    Args:
        chat: The ChatSession to check.

    Returns:
        True if query completed and message was created, False otherwise.
    """
    result = check_query_completion(chat)
    if result is None:
        return False

    if chat.writer:
        chat.writer._on_write = None
        chat.writer.clear()

    if result.error:
        assistant_message = ChatMessage(
            role="assistant",
            content=f"Error processing request: {result.error}",
        )
    else:
        assistant_message = ChatMessage(
            role="assistant",
            content=result.text,
            thinking=result.thinking,
            result=result.result,
            has_visualization=result.has_visualization,
            visualization_data=result.visualization_data,
        )

    chat.messages.append(assistant_message)

    save_current_chat()

    return True

def render_thinking_section(chat: "ChatSession") -> None:
    """Render the thinking section wrapper that contains the streaming fragment."""
    with st.chat_message("assistant"), st.expander("💭 Thinking...", expanded=True):
        _thinking_stream_fragment(chat)

@st.fragment(run_every=0.1)
def _thinking_stream_fragment(chat: "ChatSession") -> None:
    """Fragment that streams thinking updates at 100ms intervals.

    This is the Streamlit-recommended pattern for streaming updates from
    background tasks. The fragment polls the writer's buffer rapidly.
    """
    current_text = chat.writer.getvalue() if chat.writer else ""

    if current_text:
        st.markdown(current_text)
    else:
        st.caption("Processing...")

@st.fragment(run_every=1.0)
def _suggestions_polling_fragment() -> None:
    """Fragment that polls for suggestions completion every second.

    This runs independently from the main app, checking if the background
    suggestions generation has completed. When it completes, triggers a rerun
    to show the suggestions.

    The fragment automatically stops polling when suggestions are no longer loading
    (either completed, cancelled, or never started).
    """
    if not is_suggestions_loading():
        return

    if check_suggestions_completion():
        st.rerun()

@st.fragment(run_every=1.0)
def _query_polling_fragment() -> None:
    """Fragment that polls for query completion every second.

    This runs independently from the main app, checking if the background
    query execution has completed. When it completes, triggers a rerun
    to show the result.

    Note: Live streaming updates are handled by the _on_write callback on
    the writer, not by this polling fragment.
    """
    chat = _get_current_chat()
    if chat is None:
        return

    if not is_query_running(chat):
        return

    if handle_query_completion(chat):
        st.rerun()

def _should_show_welcome(chat: "ChatSession") -> bool:
    """Determine if we should show the welcome screen.

    Returns False if:
    - There are any messages in the chat
    - There's a query being processed for this chat
    """
    has_messages = len(chat.messages) > 0

    query_running = is_query_running(chat)

    return not has_messages and not query_running

def render_chat_interface(chat: "ChatSession") -> None:
    """Render the complete chat interface."""
    query_running = is_query_running(chat)

    user_input = st.chat_input("Ask a question about your data...", disabled=query_running)

    if user_input:
        user_message = ChatMessage(role="user", content=user_input)
        chat.messages.append(user_message)

        save_current_chat()

        start_background_query(chat, user_input)

        st.rerun()

    if handle_query_completion(chat):
        st.rerun()

    show_welcome = _should_show_welcome(chat)

    if show_welcome:
        render_welcome_component(chat)

        if is_suggestions_loading():
            _suggestions_polling_fragment()
    else:
        render_chat_history(chat)

        if query_running:
            render_thinking_section(chat)
            _query_polling_fragment()
