"""Welcome page -- two modes: Home (for valid projects) and Setup Wizard."""

import base64
import logging
from pathlib import Path

import streamlit as st

from databao_cli.project.layout import find_project
from databao_cli.ui.models.settings import LLMSettings
from databao_cli.ui.project_utils import DatabaoProjectStatus, databao_project_status

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Home mode (existing welcome page content, shown when project is VALID)
# ---------------------------------------------------------------------------


def render_welcome_page() -> None:
    """Render the welcome/home page for a fully configured project."""
    from databao_cli.ui.app import _create_new_chat

    _col1, col2, _col3 = st.columns([1, 2, 1])

    with col2:
        _render_logo_header()

        st.markdown(
            """
            <div style="text-align: center; color: #666; margin-bottom: 2rem;">
                <p style="font-size: 1.1rem;">
                    Your AI-powered data analysis assistant.
                    Ask questions about your data in natural language.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        chats = st.session_state.get("chats", {})
        agent = st.session_state.get("agent")

        stat_col1, stat_col2, stat_col3 = st.columns(3)

        with stat_col1:
            num_chats = len(chats)
            st.metric("Active Chats", num_chats)

        with stat_col2:
            num_sources = len(agent.dbs) + len(agent.dfs) if agent else 0
            st.metric("Data Sources", num_sources)

        with stat_col3:
            project = st.session_state.get("databao_project")
            status = "Ready" if project and agent else "Not ready"
            st.metric("Status", status)

        st.markdown("---")

        st.subheader("Quick Actions")

        action_col1, action_col2 = st.columns(2)

        with action_col1:
            if st.button("💬 Start New Chat", width="stretch", type="primary"):
                _create_new_chat()
                st.rerun()

        with action_col2:
            if st.button("⚙️ Settings", width="stretch"):
                context_settings_page = st.session_state.get("_page_context_settings")
                if context_settings_page:
                    st.switch_page(context_settings_page)

        st.markdown("---")
        st.subheader("Getting Started")

        with st.expander("📖 How to use Databao", expanded=False):
            st.markdown(
                """
                1. **Configure your data sources** in Context Settings
                2. **Start a new chat** to begin asking questions
                3. **Ask questions in natural language** - Databao will analyze your data
                4. **View results** as tables, charts, and explanations

                **Example questions:**
                - "What tables are in my database?"
                - "Show me the top 10 customers by revenue"
                - "What's the trend in sales over the last month?"
                """
            )

        if chats:
            st.markdown("---")
            st.subheader("Recent Chats")

            sorted_chats = sorted(
                chats.values(),
                key=lambda c: c.created_at,
                reverse=True,
            )[:5]

            for chat in sorted_chats:
                col_title, col_action = st.columns([4, 1])
                with col_title:
                    st.markdown(f"**{chat.display_title}**")
                    st.caption(chat.created_at.strftime("%b %d, %H:%M"))
                with col_action:
                    if st.button("Open", key=f"open_{chat.id}"):
                        st.session_state.current_chat_id = chat.id
                        st.session_state._navigate_to_chat = chat.id
                        st.rerun()


# ---------------------------------------------------------------------------
# Setup Wizard mode (shown when project is NOT valid)
# ---------------------------------------------------------------------------


def render_setup_wizard_page() -> None:
    """Render the setup wizard for first-time project configuration.

    The wizard is organized into up to five sections, which are disabled
    based on prerequisites:
    1. Initialize Project
    2. Configure Datasources
    3. Configure Agent
    4. Build Context (optional; can be hidden via feature flag)
    5. Start Using Databao

    When read-only-domain mode is active, editing sections are disabled with
    an explanation banner.
    """
    from databao_cli.ui.app import _create_new_chat, is_hide_build_context_hint, is_read_only_domain
    from databao_cli.ui.components.datasource_manager import render_datasource_manager
    from databao_cli.ui.services.build_service import (
        get_build_status,
        render_build_section,
    )
    from databao_cli.ui.services.dce_operations import init_project, list_datasources

    project_dir: Path = st.session_state.get("_project_dir", Path.cwd())
    read_only = is_read_only_domain()
    hide_build_context = is_hide_build_context_hint()

    _col1, col2, _col3 = st.columns([1, 3, 1])

    with col2:
        _render_logo_header()

        st.markdown(
            """
            <div style="text-align: center; color: #666; margin-bottom: 2rem;">
                <p style="font-size: 1.1rem;">
                    Let's set up your Databao project. Follow the steps below to get started.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        if read_only:
            st.info(
                "Domain is in read-only mode. "
                "Project initialization, datasource configuration, and context building are disabled."
            )

        project = find_project(project_dir)
        project_initialized = project is not None

        status = databao_project_status(project) if project else DatabaoProjectStatus.NOT_INITIALIZED

        has_datasources = False
        if project is not None and status != DatabaoProjectStatus.NOT_INITIALIZED:
            try:
                configured = list_datasources(project.root_domain_dir)
                has_datasources = len(configured) > 0
            except Exception:
                has_datasources = False

        build_status = get_build_status()
        build_started_or_done = build_status in ("running", "completed")

        # ---- Section 1: Initialize Project ----
        _render_section_header("1", "Initialize Project", completed=project_initialized)

        if project is not None:
            st.success(f"Project initialized at `{project.project_dir}`", icon="✅")
        elif read_only:
            st.caption("Project initialization is disabled in read-only mode.")
        else:
            st.markdown(
                "Databao needs a project directory to store configuration, datasources, "
                "and build output. This will create a `databao/` folder in your current directory."
            )
            st.markdown(f"**Project directory:** `{project_dir.resolve()}`")

            if st.button("Initialize Project", key="init_btn", type="primary"):
                try:
                    new_project = init_project(project_dir)
                    st.session_state.databao_project = new_project
                    st.success("Project initialized successfully!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Failed to initialize project: {e}")
                    logger.exception("Failed to initialize project")

        st.markdown("---")

        # ---- Section 2: Configure Datasources ----
        _render_section_header(
            "2",
            "Configure Datasources",
            completed=has_datasources,
            enabled=project_initialized,
        )

        if project is None:
            st.caption("Complete step 1 to configure datasources.")
        elif read_only:
            render_datasource_manager(project.root_domain_dir, read_only=True)
        else:
            st.markdown(
                "Datasources connect Databao to your data. Add at least one datasource "
                "so Databao knows what data you want to analyze. The available fields "
                "depend on the datasource type you select."
            )
            render_datasource_manager(project.root_domain_dir)

        st.markdown("---")

        # ---- Section 3: Configure Agent ----
        llm_settings: LLMSettings = st.session_state.get("llm_settings", LLMSettings())
        agent_configured = llm_settings.is_configured

        _render_section_header(
            "3",
            "Configure Agent",
            completed=agent_configured,
            enabled=has_datasources,
        )

        if not has_datasources:
            st.caption("Add at least one datasource first.")
        else:
            st.markdown(
                "Configure the execution engine and language model for the AI agent. "
                "You'll need an API key for your chosen LLM provider."
            )
            from databao_cli.ui.pages.agent_settings import render_agent_settings_page

            render_agent_settings_page(auto_apply=True)

        st.markdown("---")

        # ---- Section 4: Build Context ----
        if not hide_build_context:
            _render_section_header(
                "4",
                "Build Context (Optional)",
                completed=build_started_or_done,
                enabled=has_datasources,
            )

            if not has_datasources:
                st.caption("Complete the previous steps first.")
            elif project is None:
                st.caption("Add at least one datasource first.")
            elif read_only:
                render_build_section(project.root_domain_dir, read_only=True)
            else:
                st.markdown(
                    "Building the context indexes your datasources so Databao can better understand "
                    "your data structure and provide higher-quality answers."
                )
                render_build_section(project.root_domain_dir)

            st.markdown("---")

        # ---- Final Section: Start Using Databao ----
        final_step = "4" if hide_build_context else "5"
        _render_section_header(
            final_step,
            "Start Using Databao",
            completed=False,
            enabled=has_datasources,
        )

        if not has_datasources:
            st.caption("Add at least one datasource first.")
        else:
            if not hide_build_context and build_status == "running":
                st.info(
                    "The build is still in progress, but you can start exploring Databao. "
                    "Some features may not work until the build completes."
                )
            elif not hide_build_context and not build_started_or_done:
                st.markdown(
                    "You're ready to start using Databao! Consider building the context above for the best experience."
                )
            else:
                st.markdown("All configured! You're ready to start using Databao.")

            if st.button("Start New Chat", key="setup_start_chat", type="primary"):
                from databao_cli.ui.app import mark_welcome_completed

                mark_welcome_completed()
                _create_new_chat()
                st.rerun()


# ---------------------------------------------------------------------------
# Shared helpers
# ---------------------------------------------------------------------------


def _render_logo_header() -> None:
    """Render the centered logo and title."""
    logo_path = Path(__file__).parent.parent / "assets" / "bao.png"
    if logo_path.exists():
        with open(logo_path, "rb") as f:
            logo_b64 = base64.b64encode(f.read()).decode()
        st.markdown(
            f"""
            <div style="text-align: center; margin-bottom: 2rem;">
                <img src="data:image/png;base64,{logo_b64}" width="80" height="80">
                <h1 style="margin-top: 1rem;">Welcome to Databao</h1>
            </div>
            """,
            unsafe_allow_html=True,
        )
    else:
        st.title("Welcome to Databao")


def _render_section_header(
    number: str,
    title: str,
    completed: bool = False,
    enabled: bool = True,
) -> None:
    """Render a styled section header for the setup wizard."""
    if completed:
        icon = "✅"
        color = "green"
    elif enabled:
        icon = f"{number}"
        color = "inherit"
    else:
        icon = f"{number}"
        color = "gray"

    st.markdown(
        f'<h3 style="color: {color};">{icon} {title}</h3>',
        unsafe_allow_html=True,
    )
