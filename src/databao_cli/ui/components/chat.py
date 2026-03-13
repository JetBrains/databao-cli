"""Chat interface component with streaming support."""

from typing import TYPE_CHECKING, cast

import streamlit as st
from databao.agent.core.agent import Agent

from databao_cli.ui.components.results import render_execution_result
from databao_cli.ui.models.chat_session import ChatMessage
from databao_cli.ui.services import (
    check_query_completion,
    get_query_phase,
    is_query_running,
    save_current_chat,
    start_query_execution,
    stop_query,
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
        elif message.content:
            st.error(message.content)

        if message.metadata.get("stopped"):
            st.warning("Query was stopped by user")


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
    hide_suggested_questions = bool(st.session_state.get("_hide_suggested_questions"))

    if status == "not_started" and not hide_suggested_questions:
        agent: Agent | None = st.session_state.get("agent")
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

    if status == "loading" and not hide_suggested_questions:
        st.markdown(
            "<p style='text-align: center; color: #888; font-size: 0.9em; margin-top: 1em;'>"
            "🔄 Analyzing your data to suggest questions..."
            "</p>",
            unsafe_allow_html=True,
        )
        return

    questions: list[str] = st.session_state.get("suggested_questions", [])
    is_llm_generated: bool = st.session_state.get("suggestions_are_llm_generated", False)

    if questions and not hide_suggested_questions:
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
        return cast("ChatSession", chats[current_chat_id])
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
    """Check if query progressed and create/update the assistant message.

    Handles two transitions:
    - **Partial**: data phase done, viz in progress → create message with
      ``viz_pending=True`` so the UI can show text/code/data immediately.
    - **Full**: everything done → either update the pending message with viz
      data, or create a new message if there was no partial step.

    Returns:
        True if the UI should rerun to reflect the new state.
    """
    result = check_query_completion(chat)
    if result is None:
        return False

    if result.viz_pending:
        if chat.writer:
            chat.writer._on_write = None
            chat.writer.clear()

        chat.messages.append(
            ChatMessage(
                role="assistant",
                content=result.text,
                thinking=result.thinking,
                result=result.result,
                viz_pending=True,
            )
        )
        save_current_chat()
        return True

    # Full result — check if we need to update an existing pending message
    pending_msg = _find_pending_viz_message(chat)
    if pending_msg is not None:
        pending_msg.viz_pending = False
        if result.error:
            pending_msg.has_visualization = False
            pending_msg.visualization_data = None
            pending_msg.metadata["viz_error"] = str(result.error)
        else:
            pending_msg.has_visualization = result.has_visualization
            pending_msg.visualization_data = result.visualization_data
        save_current_chat()
        return True

    # No pending message — create normally (no auto-viz, or error)
    if chat.writer:
        chat.writer._on_write = None
        chat.writer.clear()

    if result.error:
        if result.result is not None:
            assistant_message = ChatMessage(
                role="assistant",
                content=result.text,
                thinking=result.thinking,
                result=result.result,
                has_visualization=False,
                metadata={"viz_error": str(result.error)},
            )
        else:
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


def _find_pending_viz_message(chat: "ChatSession") -> ChatMessage | None:
    """Return the last assistant message that is waiting for visualization, if any."""
    for msg in reversed(chat.messages):
        if msg.role == "assistant" and msg.viz_pending:
            return msg
    return None


def render_thinking_section(chat: "ChatSession") -> None:
    """Render the thinking section wrapper that contains the streaming fragment."""
    with st.chat_message("assistant"):
        _thinking_stream_fragment(chat)


@st.fragment(run_every=1.0)
def _thinking_stream_fragment(chat: "ChatSession") -> None:
    """Fragment that streams thinking updates at 1s intervals.

    This is the Streamlit-recommended pattern for streaming updates from
    background tasks. The fragment polls the writer's buffer rapidly.
    """
    phase = get_query_phase(chat)

    with st.expander("💭 Thinking...", expanded=phase != "visualizing"):
        current_text = chat.writer.getvalue() if chat.writer else ""
        if current_text:
            st.markdown(current_text)
        else:
            st.caption("Processing...")

    if phase == "visualizing":
        st.info("Generating visualization...", icon="📈")


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


def _has_stopped_exchange(chat: "ChatSession") -> bool:
    """Check if the last exchange was stopped *without* producing results.

    Returns False when the stop happened during the visualization phase,
    because the data result is already available and the conversation can
    continue normally.
    """
    if not chat.messages:
        return False
    last = chat.messages[-1]
    return last.role == "assistant" and bool(last.metadata.get("stopped")) and last.result is None


def _remove_stopped_exchange(chat: "ChatSession") -> None:
    """Remove the trailing user + stopped-assistant message pair."""
    if not chat.messages:
        return
    last = chat.messages[-1]
    if last.role == "assistant" and last.metadata.get("stopped"):
        chat.messages.pop()
    if chat.messages and chat.messages[-1].role == "user":
        chat.messages.pop()


@st.dialog("Overwrite previous request?")
def _confirm_overwrite_dialog() -> None:
    """Modal dialog asking whether to discard the stopped exchange."""
    st.markdown("The previous request was stopped. Sending a new request will remove it.")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("OK", use_container_width=True, type="primary"):
            st.session_state["overwrite_confirmed"] = True
            st.rerun()
    with col2:
        if st.button("Cancel", use_container_width=True):
            st.session_state.pop("pending_query", None)
            st.rerun()


def _handle_stop_click(chat: "ChatSession") -> None:
    """Stop the running query and record the partial result.

    If the data phase already produced a message (``viz_pending``), marks
    it as stopped.  Otherwise creates a new assistant message with
    whatever thinking text was captured so far.
    """
    thinking_text = stop_query(chat)
    if thinking_text is None:
        return

    pending = _find_pending_viz_message(chat)
    if pending is not None:
        pending.viz_pending = False
        pending.metadata["stopped"] = True
    else:
        chat.messages.append(
            ChatMessage(
                role="assistant",
                thinking=thinking_text or None,
                content="",
                metadata={"stopped": True},
            )
        )
    save_current_chat()


def _render_chat_input_bar(chat: "ChatSession", query_running: bool) -> None:
    """Render the chat input bar.

    When ``query_running`` is False, shows an enabled text input inside a
    form (so Enter submits) and a send button.

    When ``query_running`` is True (background query **or** manual plot
    in progress), the input is disabled and a stop button is shown
    instead.
    """
    if query_running:
        col1, col2 = st.columns([12, 1], vertical_alignment="bottom")
        with col1:
            st.text_input(
                "Message",
                placeholder="Query in progress...",
                disabled=True,
                label_visibility="collapsed",
                key="chat_input_disabled",
            )
        with col2:
            if st.button(
                ":material/stop_circle:",
                key="stop_btn",
                use_container_width=True,
                type="primary",
                help="Stop the running query",
            ):
                _handle_stop_click(chat)
                st.rerun()
    else:
        with st.form("chat_input_form", clear_on_submit=True, border=False):
            col1, col2 = st.columns([12, 1], vertical_alignment="bottom")
            with col1:
                user_input = st.text_input(
                    "Message",
                    placeholder="Ask a question about your data...",
                    label_visibility="collapsed",
                    key="chat_input",
                )
            with col2:
                submitted = st.form_submit_button(
                    ":material/send:",
                    use_container_width=True,
                )

            if submitted and user_input:
                if _has_stopped_exchange(chat):
                    st.session_state["pending_query"] = user_input
                    _confirm_overwrite_dialog()
                else:
                    user_message = ChatMessage(role="user", content=user_input)
                    chat.messages.append(user_message)
                    save_current_chat()
                    start_background_query(chat, user_input)
                    st.rerun()


def _process_pending_overwrite(chat: "ChatSession") -> None:
    """Process a confirmed overwrite of a stopped exchange.

    Called at the top of ``render_chat_interface`` (before any widgets are
    rendered), so no ``st.rerun()`` is needed — the updated state is
    picked up by the rendering that follows in the same script run.
    """
    if not st.session_state.pop("overwrite_confirmed", False):
        return

    pending = st.session_state.pop("pending_query", None)
    if not pending:
        return

    _remove_stopped_exchange(chat)
    user_message = ChatMessage(role="user", content=pending)
    chat.messages.append(user_message)
    save_current_chat()
    start_background_query(chat, pending)


def render_chat_interface(chat: "ChatSession") -> None:
    """Render the complete chat interface.

    Orchestrates, in order:
    1. Processing a confirmed overwrite of a stopped exchange.
    2. Chat history, thinking section, and polling fragments.
    3. The input bar (enabled or disabled).
    4. A pending manual "Generate Plot" execution (blocking, runs last
       so the disabled input bar is already visible).
    """
    _process_pending_overwrite(chat)

    agent: Agent | None = st.session_state.get("agent")
    hide_build_context_hint: bool = bool(st.session_state.get("_hide_build_context_hint"))
    if agent is not None and not agent.domain.is_context_built() and not chat.messages and not hide_build_context_hint:
        st.markdown(
            "⚠️ Context isn't built yet. "
            '<a href="/context-settings#build-context" target="_self">Build context</a> '
            "for better query results.",
            unsafe_allow_html=True,
        )

    query_running = is_query_running(chat) or "pending_plot_message_index" in st.session_state

    if handle_query_completion(chat):
        st.rerun()

    show_welcome = _should_show_welcome(chat)

    if show_welcome:
        render_welcome_component(chat)

        if is_suggestions_loading():
            _suggestions_polling_fragment()
    else:
        render_chat_history(chat)

        if chat.query_status == "running":
            render_thinking_section(chat)

        if query_running:
            _query_polling_fragment()

    st.markdown("<div style='height: 2em'></div>", unsafe_allow_html=True)
    _render_chat_input_bar(chat, query_running)

    if "pending_plot_message_index" in st.session_state:
        from databao_cli.ui.components.results import execute_pending_plot

        execute_pending_plot(chat)
