"""Result display component with foldable sections and action buttons."""

import logging
from typing import TYPE_CHECKING, Any, cast

import nh3
import streamlit as st

from databao_cli.features.ui.services.chat_persistence import save_current_chat

if TYPE_CHECKING:
    from databao.agent.core.executor import ExecutionResult
    from databao.agent.core.thread import Thread

    from databao_cli.features.ui.models.chat_session import ChatSession

logger = logging.getLogger(__name__)

_ALLOWED_HTML_TAGS = {
    "div",
    "span",
    "svg",
    "g",
    "path",
    "rect",
    "circle",
    "line",
    "ellipse",
    "polygon",
    "polyline",
    "text",
    "tspan",
    "defs",
    "clipPath",
    "use",
    "symbol",
    "marker",
    "pattern",
    "linearGradient",
    "radialGradient",
    "stop",
    "style",
    "table",
    "tr",
    "td",
    "th",
    "thead",
    "tbody",
    "tfoot",
    "caption",
    "colgroup",
    "col",
    "p",
    "br",
    "h1",
    "h2",
    "h3",
    "h4",
    "h5",
    "h6",
    "ul",
    "ol",
    "li",
    "a",
    "img",
    "figure",
    "figcaption",
    "strong",
    "em",
    "b",
    "i",
    "code",
    "pre",
    "blockquote",
}

_ALLOWED_HTML_ATTRIBUTES: dict[str, set[str]] = {
    "*": {
        "class",
        "style",
        "id",
        "width",
        "height",
        "viewBox",
        "xmlns",
        "xmlns:xlink",
        "d",
        "fill",
        "stroke",
        "stroke-width",
        "stroke-dasharray",
        "stroke-linecap",
        "stroke-linejoin",
        "opacity",
        "fill-opacity",
        "stroke-opacity",
        "transform",
        "x",
        "y",
        "dx",
        "dy",
        "rx",
        "ry",
        "cx",
        "cy",
        "r",
        "x1",
        "y1",
        "x2",
        "y2",
        "font-size",
        "font-family",
        "font-weight",
        "text-anchor",
        "dominant-baseline",
        "clip-path",
        "clip-rule",
        "fill-rule",
        "marker-end",
        "marker-start",
        "marker-mid",
        "offset",
        "stop-color",
        "stop-opacity",
        "gradientUnits",
        "gradientTransform",
        "patternUnits",
        "patternTransform",
        "points",
        "preserveAspectRatio",
    },
    "a": {"href", "target", "rel"},
    "img": {"src", "alt"},
}


def _sanitize_html(html: str) -> str:
    """Sanitize HTML content to prevent XSS while preserving SVG chart rendering."""
    return nh3.clean(html, tags=_ALLOWED_HTML_TAGS, attributes=_ALLOWED_HTML_ATTRIBUTES)


def _extract_visualization_data(thread: "Thread") -> dict[str, Any] | None:
    """Extract serializable visualization data from thread._visualization_result.

    For VegaChatResult, this extracts the Vega-Lite spec (JSON) and spec_df (DataFrame).
    """
    vis_result = thread._visualization_result
    if vis_result is None:
        return None

    data: dict[str, Any] = {
        "text": vis_result.text,
        "code": vis_result.code,
    }

    if hasattr(vis_result, "spec") and hasattr(vis_result, "spec_df"):
        data["spec"] = vis_result.spec
        data["spec_df"] = vis_result.spec_df

    return data


def render_response_section(text: str, has_visualization: bool) -> None:
    """Render the response text section."""
    expanded = not has_visualization

    with st.expander("📝 Response", expanded=expanded):
        st.markdown(text)


def render_code_section(code: str) -> None:
    """Render the code section (collapsed by default)."""
    with st.expander("💻 Code", expanded=False):
        sql_keywords = ["SELECT", "FROM", "WHERE", "JOIN", "INSERT", "UPDATE", "DELETE"]
        if any(keyword in code.upper() for keyword in sql_keywords):
            st.code(code, language="sql")
        else:
            st.code(code, language="python")


def render_dataframe_section(result: "ExecutionResult", has_visualization: bool) -> None:
    """Render the dataframe section."""
    df = result.df
    if df is None:
        return

    expanded = not has_visualization

    with st.expander(f"📊 Data ({len(df)} rows)", expanded=expanded):
        st.dataframe(df, width="stretch")


def render_visualization_section(thread: "Thread", visualization_data: dict[str, Any] | None = None) -> None:
    """Render the visualization section.

    Follows the same rendering logic as Jupyter notebooks:
    1. Vega-Lite/Altair charts: use st.vega_lite_chart for proper rendering
    2. HTML-capable objects: embed HTML
    3. PIL Images: render as images

    Per-message ``visualization_data`` takes priority over the shared
    ``thread._visualization_result`` so that each message renders its own
    chart even when the thread's live result belongs to a different query.

    Args:
        thread: The Thread object (may have _visualization_result)
        visualization_data: Optional persisted visualization data (takes priority over thread result)
    """
    vis_result = thread._visualization_result

    if visualization_data is not None:
        spec = visualization_data.get("spec")
        spec_df = visualization_data.get("spec_df")
        if spec is not None and spec_df is not None:
            with st.expander("📈 Visualization", expanded=True):
                try:
                    st.vega_lite_chart(spec_df, spec, width="stretch")
                    return
                except Exception as e:
                    st.warning(f"Failed to render persisted visualization: {e}")
                    return
        return

    if vis_result is None:
        return

    with st.expander("📈 Visualization", expanded=True):
        plot = vis_result.plot

        if plot is None:
            st.warning("No visualization generated")
            return

        plot_type = type(plot).__name__

        if hasattr(vis_result, "spec") and hasattr(vis_result, "spec_df"):
            spec = vis_result.spec
            spec_df = vis_result.spec_df
            if spec is not None and spec_df is not None:
                try:
                    st.vega_lite_chart(spec_df, spec, width="stretch")
                    return
                except Exception:
                    logger.debug("Failed to render Vega-Lite chart from spec, trying other methods", exc_info=True)

        if "altair" in plot_type.lower() or "Chart" in plot_type:
            try:
                st.altair_chart(plot, width="stretch")
                return
            except Exception:
                logger.debug("Failed to render Altair chart, trying other methods", exc_info=True)

        html_content = None

        if hasattr(plot, "_repr_mimebundle_"):
            try:
                bundle = plot._repr_mimebundle_()
                if isinstance(bundle, tuple):
                    format_dict, _metadata = bundle
                else:
                    format_dict = bundle
                if format_dict and "text/html" in format_dict:
                    html_content = format_dict["text/html"]
            except Exception:
                logger.debug("Failed to extract HTML from _repr_mimebundle_", exc_info=True)

        if html_content is None and hasattr(plot, "_repr_html_"):
            try:
                html_content = plot._repr_html_()
            except Exception:
                logger.debug("Failed to get HTML from _repr_html_", exc_info=True)

        if html_content is None and hasattr(vis_result, "_get_plot_html"):
            try:
                html_content = vis_result._get_plot_html()
            except Exception:
                logger.debug("Failed to get HTML from _get_plot_html()", exc_info=True)

        if html_content:
            html_content = _sanitize_html(html_content)
            st.components.v1.html(html_content, height=500, scrolling=False)
            return

        if "Image" in plot_type or hasattr(plot, "_repr_png_"):
            try:
                st.image(plot)
                return
            except Exception:
                logger.debug("Failed to render plot as image", exc_info=True)

        st.warning(f"Could not render visualization: {plot_type}")


def _get_current_chat() -> "ChatSession | None":
    """Get the current chat session from session state."""
    current_chat_id = st.session_state.get("current_chat_id")
    chats = st.session_state.get("chats", {})
    if current_chat_id and current_chat_id in chats:
        return cast("ChatSession", chats[current_chat_id])
    return None


@st.fragment
def render_visualization_and_actions(
    result: "ExecutionResult",
    chat: "ChatSession",
    message_index: int,
    *,
    is_latest: bool = False,
) -> None:
    """Fragment that renders visualization status and action buttons.

    Re-reads ``has_visualization``, ``visualization_data``, ``viz_pending``
    and ``viz_error`` from ``chat.messages[message_index]`` on every run so
    it reflects the latest state.

    When a manual "Generate Plot" is pending (flagged via session state),
    this fragment only renders a placeholder; the actual blocking
    ``thread.plot()`` call is executed by ``execute_pending_plot`` in the
    main script — after the input bar has been rendered — to keep the UI
    responsive and the input visibly disabled.
    """
    current_chat = _get_current_chat()
    if current_chat is None:
        return

    thread = current_chat.thread
    if thread is None:
        return

    messages = current_chat.messages
    if message_index < len(messages):
        msg = messages[message_index]
        has_visualization = msg.has_visualization
        visualization_data = msg.visualization_data
        viz_pending = msg.viz_pending
        viz_error = msg.metadata.get("viz_error")
    else:
        has_visualization = False
        visualization_data = None
        viz_pending = False
        viz_error = None

    if st.session_state.get("pending_plot_message_index") == message_index:
        st.info("Generating visualization...", icon="📈")
        return

    if viz_pending:
        st.info("Generating visualization...", icon="📈")
    elif viz_error:
        st.error(f"Failed to generate visualization: {viz_error}")
    elif has_visualization or visualization_data is not None or (is_latest and thread._visualization_result is not None):
        render_visualization_section(thread, visualization_data)

    if is_latest and not viz_pending and not viz_error:
        _render_and_handle_action_buttons(result, current_chat, message_index, has_visualization)


def _render_and_handle_action_buttons(
    result: "ExecutionResult",
    chat: "ChatSession",
    message_index: int,
    has_visualization: bool,
) -> None:
    """Render action buttons and handle clicks.

    "Generate Plot" sets a session-state flag and triggers a full app
    rerun so that the input bar is rendered as disabled before the
    blocking ``thread.plot()`` call begins.
    """
    from databao_cli.features.ui.services import is_query_running

    thread = chat.thread
    if thread is None:
        return

    is_processing = is_query_running(chat)

    has_data = result.df is not None

    if not (has_data and not has_visualization and thread._data_result is not None):
        return

    cols = st.columns(3)

    with cols[0]:
        button_key = f"action_generate_plot_{message_index}"
        clicked = st.button("📈 Generate Plot", key=button_key, width="stretch", disabled=is_processing)
        if clicked and not is_processing:
            st.session_state["pending_plot_message_index"] = message_index
            st.rerun(scope="app")


def execute_pending_plot(chat: "ChatSession") -> None:
    """Execute a pending manual "Generate Plot" request.

    Must be called **after** the input bar has been rendered (disabled)
    so the user sees a locked UI while the blocking ``thread.plot()``
    runs.  On completion (or error) triggers a full app rerun.
    """
    thread = chat.thread
    if thread is None:
        return

    message_index: int = st.session_state.pop("pending_plot_message_index")

    try:
        thread.plot()

        messages = chat.messages
        if message_index < len(messages):
            messages[message_index].has_visualization = True
            messages[message_index].visualization_data = _extract_visualization_data(thread)
            save_current_chat()
    except Exception as e:
        logger.exception("Failed to generate visualization")
        if message_index < len(chat.messages):
            chat.messages[message_index].metadata["viz_error"] = str(e)
            save_current_chat()

    st.rerun(scope="app")


def render_execution_result(
    result: "ExecutionResult",
    chat: "ChatSession",
    message_index: int,
    has_visualization: bool,
    *,
    is_latest: bool = False,
    visualization_data: dict[str, Any] | None = None,
) -> None:
    """Render the complete execution result with all sections."""
    if result.text:
        render_response_section(result.text, has_visualization)

    if result.code:
        render_code_section(result.code)

    if result.df is not None:
        render_dataframe_section(result, has_visualization)

    render_visualization_and_actions(result, chat, message_index, is_latest=is_latest)
