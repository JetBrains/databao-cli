"""Context Settings page - DCE project configuration, datasource management, and build."""

import logging

import streamlit as st
from databao import Agent

from databao_cli.project.layout import ProjectLayout
from databao_cli.ui.app import _clear_all_chat_threads
from databao_cli.ui.components.datasource_manager import render_datasource_manager
from databao_cli.ui.components.icons import get_db_type_and_icon
from databao_cli.ui.components.status import AppStatus, set_status
from databao_cli.ui.project_utils import DatabaoProjectStatus, databao_project_status
from databao_cli.ui.services.build_service import render_build_section
from databao_cli.ui.services.dce_operations import get_status_info

logger = logging.getLogger(__name__)


def render_context_settings_page() -> None:
    """Render the Context Settings page."""
    st.title("Context Settings")
    st.markdown("Configure your data context and sources.")

    project: ProjectLayout | None = st.session_state.get("databao_project")

    # ---- DCE Status section ----
    st.markdown("---")
    st.subheader("📋 Status")

    if project is not None:
        try:
            status_text = get_status_info(project.root_domain_dir)
            st.code(status_text, language=None)
        except Exception as e:
            st.warning(f"Could not retrieve status info: {e}")
            logger.exception("Failed to get status info")
    else:
        st.caption("No project configured.")

    # ---- Project Info section ----
    st.markdown("---")
    st.subheader("📊 Project")

    reload_clicked = False

    if project is not None:
        reload_clicked = _render_project_info(project)
    else:
        st.info("No Databao project detected. Initialize one from the Setup page.")

    if reload_clicked:
        st.session_state.databao_project = None
        st.session_state.agent = None
        _clear_all_chat_threads()
        set_status(AppStatus.INITIALIZING, "Reloading project...")
        st.rerun()

    # ---- Datasource Management section ----
    st.markdown("---")
    st.subheader("🔗 Datasource Management")

    if project is not None:
        status = databao_project_status(project)
        if status == DatabaoProjectStatus.NOT_INITIALIZED:
            st.warning("Project is not initialized. Initialize it first.")
        else:
            render_datasource_manager(project.root_domain_dir)
    else:
        st.caption("Configure a project to manage datasources.")

    # ---- Build section ----
    st.markdown("---")
    st.subheader("🔨 Build Context")

    if project is not None:
        status = databao_project_status(project)
        if status in (DatabaoProjectStatus.NOT_INITIALIZED, DatabaoProjectStatus.NO_DATASOURCES):
            st.caption("Add at least one datasource before building.")
        else:
            st.markdown(
                "Build indexes your datasources so Databao can understand your data structure and answer questions about it."
            )
            render_build_section(project.root_domain_dir)
    else:
        st.caption("Configure a project to build context.")

    # ---- Connected Sources (from Agent) ----
    st.markdown("---")
    st.subheader("📡 Active Agent Sources")

    agent = st.session_state.get("agent")
    if agent is None:
        st.caption("Sources will appear after the agent is initialized.")
    else:
        _render_sources(agent)


def _render_project_info(project: ProjectLayout) -> bool:
    """Render project information.

    Returns:
        True if the reload button was clicked, False otherwise.
    """
    st.markdown(f"**{project.name}**")
    st.code(str(project.project_dir), language=None)

    status = databao_project_status(project)
    if status == DatabaoProjectStatus.VALID:
        st.success("Project is ready", icon="✅")
    elif status == DatabaoProjectStatus.NOT_INITIALIZED:
        st.error("Project not initialized", icon="❌")
    elif status == DatabaoProjectStatus.NO_DATASOURCES:
        st.warning("No datasources configured", icon="⚠️")
    elif status == DatabaoProjectStatus.NO_BUILD:
        st.warning("Build required", icon="⚠️")

    reload_clicked = st.button("🔄 Reload")

    return reload_clicked


def _render_sources(agent: Agent) -> None:
    """Render connected data sources from the active agent."""
    dbs = agent.dbs
    dfs = agent.dfs

    if not dbs and not dfs:
        st.caption("No sources configured in this project.")
        return

    if dbs:
        st.markdown("**Databases:**")
        for name, source in dbs.items():
            db_type, icon = get_db_type_and_icon(source.config)

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
