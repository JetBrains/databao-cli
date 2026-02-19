"""Sidebar component showing project info and sources."""

import streamlit as st

from databao_cli.project.layout import ProjectLayout
from databao_cli.ui.app import _clear_all_chat_threads
from databao_cli.ui.components.icons import get_db_type_and_icon
from databao_cli.ui.components.status import AppStatus, render_status_fragment, set_status
from databao_cli.ui.pages.agent_settings import EXECUTOR_TYPES
from databao_cli.ui.project_utils import DatabaoProjectStatus, databao_project_status
from databao_cli.ui.suggestions import reset_suggestions_state


@st.dialog("Delete Chat")
def _confirm_delete_chat(chat_id: str, chat_title: str) -> None:
    """Dialog to confirm deleting the current chat."""
    from databao_cli.ui.services.chat_persistence import delete_chat

    st.warning(f"⚠️ Delete chat: **{chat_title}**?")
    st.markdown("This will permanently remove the chat and its history.")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("Cancel", use_container_width=True):
            st.rerun()
    with col2:
        if st.button("🗑️ Delete", type="primary", use_container_width=True):
            delete_chat(chat_id)

            chats = st.session_state.get("chats", {})
            if chat_id in chats:
                del chats[chat_id]
                st.session_state.chats = chats

            st.session_state.current_chat_id = None

            st.session_state._navigate_to_chat = None
            st.rerun()


def render_project_info(project: ProjectLayout | None) -> None:
    """Render project information section with Reload button."""
    st.markdown("### 📊 Project")

    if project is None:
        st.caption("No project selected")
        if st.button("🔄 Reload", width="stretch", help="Reload DCE project"):
            st.session_state.databao_project = None
            st.session_state.agent = None
            _clear_all_chat_threads()
            set_status(AppStatus.INITIALIZING, "Reloading...")
            reset_suggestions_state()
            st.rerun()
        return

    st.markdown(f"**{project.name}**")
    st.caption(str(project.project_dir))

    status = databao_project_status(project)
    if status == DatabaoProjectStatus.VALID:
        st.success("✓ Ready", icon="✅")
    elif status == DatabaoProjectStatus.NOT_INITIALIZED:
        st.error("Not initialized", icon="❌")
    elif status == DatabaoProjectStatus.NO_DATASOURCES:
        st.warning("No datasources", icon="⚠️")
    elif status == DatabaoProjectStatus.NO_BUILD:
        st.warning("Build required", icon="⚠️")

    if st.button("🔄 Reload", width="stretch", help="Reload DCE project"):
        st.session_state.databao_project = None
        st.session_state.agent = None
        _clear_all_chat_threads()
        set_status(AppStatus.INITIALIZING, "Reloading project...")
        reset_suggestions_state()
        st.rerun()


def render_sources_info() -> None:
    """Render connected sources section."""
    st.markdown("### 🔗 Sources")

    agent = st.session_state.get("agent")
    if agent is None:
        st.caption("No sources connected")
        return

    dbs = agent.dbs
    dfs = agent.dfs

    if not dbs and not dfs:
        st.caption("No sources configured")
        return

    for name, source in dbs.items():
        db_type, icon = get_db_type_and_icon(source.config)
        st.markdown(f"{icon} **{name}** ({db_type})")

    for name in dfs:
        st.markdown(f"📊 **{name}** (DataFrame)")


def render_executor_selector() -> None:
    """Render executor type selector."""
    st.markdown("### ⚙️ Executor")

    current = st.session_state.get("executor_type", "lighthouse")

    selected = st.selectbox(
        "Executor type",
        options=list(EXECUTOR_TYPES.keys()),
        index=list(EXECUTOR_TYPES.keys()).index(current),
        format_func=lambda x: EXECUTOR_TYPES[x],
        label_visibility="collapsed",
        help="Choose the execution engine for queries",
    )

    if selected != current:
        st.session_state.executor_type = selected
        st.session_state.agent = None
        _clear_all_chat_threads()
        set_status(AppStatus.INITIALIZING, "Applying executor change...")
        st.rerun()


def render_sidebar_header() -> None:
    """Render shared sidebar header (logo + status).

    This is called on ALL pages from app.py to show consistent branding and status.
    Must be called within st.sidebar context.
    """
    import base64
    from pathlib import Path

    logo_path = Path(__file__).parent.parent / "assets" / "bao.png"
    if logo_path.exists():
        with open(logo_path, "rb") as f:
            logo_b64 = base64.b64encode(f.read()).decode()
        st.markdown(
            f"""
            <div style="display: flex; align-items: center; gap: 6px;">
                <img src="data:image/png;base64,{logo_b64}" width="32" height="32" style="vertical-align: middle;">
                <span style="font-size: 1.4rem; font-weight: 600; line-height: 32px;">Databao</span>
            </div>
            """,
            unsafe_allow_html=True,
        )
    else:
        st.markdown("## Databao")

    st.markdown("")

    render_status_fragment()


def render_sidebar_chat_content(project: ProjectLayout | None) -> None:
    """Render chat-specific sidebar content.

    This is called only on chat pages to show project info, sources, and executor.
    Must be called within st.sidebar context.
    """
    from databao_cli.ui.models.chat_session import ChatSession

    render_project_info(project)

    st.markdown("---")

    render_sources_info()

    st.markdown("---")

    render_executor_selector()

    st.markdown("---")

    current_chat_id = st.session_state.get("current_chat_id")
    chats: dict[str, ChatSession] = st.session_state.get("chats", {})

    if current_chat_id and current_chat_id in chats:
        chat = chats[current_chat_id]
        if st.button("🗑️ Remove Chat", use_container_width=True, type="primary"):
            _confirm_delete_chat(current_chat_id, chat.display_title)

    st.markdown("---")
    st.caption("Databao v0.1")
