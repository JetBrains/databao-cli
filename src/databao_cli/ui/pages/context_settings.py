"""Context Settings page - DCE project configuration."""

import streamlit as st
from databao import Agent

from databao_cli.project.layout import ProjectLayout
from databao_cli.ui.app import _clear_all_chat_threads
from databao_cli.ui.components.icons import get_db_type_and_icon
from databao_cli.ui.components.status import AppStatus, set_status
from databao_cli.ui.project_utils import DCEProjectStatus, dce_status


def render_context_settings_page() -> None:
    """Render the Context Settings page."""
    st.title("Context Settings")
    st.markdown("Configure your data context and sources.")

    st.markdown("---")

    st.subheader("📊 DCE Project")

    project: ProjectLayout | None = st.session_state.get("databao_project")
    reload_clicked = False

    if project is not None:
        reload_clicked = _render_project_info(project)
    else:
        st.info("No DCE project detected. Configure one below.")

    if reload_clicked:
        st.session_state.databao_project = None
        st.session_state.context = None
        st.session_state.agent = None
        _clear_all_chat_threads()
        set_status(AppStatus.INITIALIZING, "Reloading project...")
        st.rerun()

    st.markdown("---")

    st.subheader("🔗 Connected Sources")

    agent = st.session_state.get("agent")
    if agent is None:
        if project is None:
            st.caption("Configure a project to see available sources.")
        else:
            status = dce_status(project)
            if status == DCEProjectStatus.NO_DATASOURCES:
                st.warning("No datasources configured. Add datasources to your project.")
            elif status == DCEProjectStatus.NO_BUILD:
                st.warning("Project needs to be built first. Run `databao build`.")
            else:
                st.caption("Sources will appear after initialization.")
    else:
        _render_sources(agent)


def _render_project_info(project: ProjectLayout) -> bool:
    """
    Render project information.

    Returns:
        True if the project was reloaded, False otherwise.
    """
    st.markdown(f"**{project.name}**")
    st.code(str(project.project_dir), language=None)

    status = dce_status(project)
    if status == DCEProjectStatus.VALID:
        st.success("Project is ready", icon="✅")
    elif status == DCEProjectStatus.NO_DATASOURCES:
        st.warning("No datasources configured", icon="⚠️")
    elif status == DCEProjectStatus.NO_BUILD:
        st.warning("Build required - run `databao build`", icon="⚠️")
    else:
        st.error("Project not found", icon="❌")

    reload_clicked = st.button("🔄 Reload")

    return reload_clicked


def _render_sources(agent: Agent) -> None:
    """Render connected data sources."""
    dbs = agent.dbs
    dfs = agent.dfs

    if not dbs and not dfs:
        st.caption("No sources configured in this project.")
        return

    if dbs:
        st.markdown("**Databases:**")
        for name, source in dbs.items():
            db_type, icon = get_db_type_and_icon(source.db_connection)

            with st.container():
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.markdown(f"{icon} **{name}**")
                with col2:
                    st.caption(db_type)

                if source.context:
                    with st.expander("View context", expanded=False):
                        st.code(source.context[:500] + "..." if len(source.context) > 500 else source.context)

    if dfs:
        st.markdown("**DataFrames:**")
        for name in dfs:
            st.markdown(f"📊 **{name}**")
