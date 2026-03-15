"""Databao Streamlit Web Interface - Main Application with Multipage Navigation."""

import argparse
import logging
import os
from collections.abc import Callable
from pathlib import Path
from typing import cast

import streamlit as st
from databao.agent import domain as create_domain
from databao.agent.caches.disk_cache import DiskCache, DiskCacheConfig
from databao.agent.configs.llm import LLMConfig
from databao.agent.core.agent import Agent
from streamlit.navigation.page import StreamlitPage

from databao_cli.project.layout import ProjectLayout, find_project
from databao_cli.ui.components.status import AppStatus, set_status, status_context
from databao_cli.ui.models.chat_session import ChatSession
from databao_cli.ui.models.settings import LLMSettings
from databao_cli.ui.project_utils import DatabaoProjectStatus, databao_project_status, has_build_output
from databao_cli.ui.services.storage import get_cache_dir

logger = logging.getLogger(__name__)


def _load_persisted_state() -> None:
    """Load settings and chats from disk on startup."""
    from databao_cli.ui.services.chat_persistence import load_all_chats
    from databao_cli.ui.services.settings_persistence import get_or_create_settings

    if "app_settings" not in st.session_state:
        settings = get_or_create_settings()
        st.session_state.app_settings = settings

        st.session_state.executor_type = settings.agent.executor_type
        st.session_state.llm_settings = settings.agent.llm

    if "_chats_loaded" not in st.session_state:
        chats = load_all_chats()
        if chats:
            st.session_state.chats = chats
            logger.info(f"Loaded {len(chats)} chats from disk")
        st.session_state._chats_loaded = True


def _save_settings_if_changed() -> None:
    """Save settings to disk if they've changed."""
    from databao_cli.ui.models.settings import Settings
    from databao_cli.ui.services.settings_persistence import save_settings

    settings: Settings | None = st.session_state.get("app_settings")
    if settings is None:
        return

    changed = False

    current_executor = st.session_state.get("executor_type", "claude_code")
    if settings.agent.executor_type != current_executor:
        settings.agent.executor_type = current_executor
        changed = True

    current_llm: LLMSettings = st.session_state.get("llm_settings", LLMSettings())
    if settings.agent.llm != current_llm:
        settings.agent.llm = current_llm
        changed = True

    if changed:
        save_settings(settings)
        logger.debug("Settings saved")


def _get_or_create_disk_cache() -> DiskCache:
    """Get or create the DiskCache instance for the agent."""
    if "disk_cache" not in st.session_state:
        cache_dir = get_cache_dir()
        config = DiskCacheConfig(db_dir=cache_dir / "diskcache")
        st.session_state.disk_cache = DiskCache(config=config)
    return cast(DiskCache, st.session_state.disk_cache)


def _initialize_agent(project: ProjectLayout) -> Agent | None:
    """Initialize or return existing Databao agent.

    This is called at app level to ensure one agent is shared across all chats.
    """
    if st.session_state.get("agent") is not None:
        return cast(Agent, st.session_state.agent)

    status = databao_project_status(project)
    if status == DatabaoProjectStatus.NOT_INITIALIZED:
        set_status(AppStatus.INITIALIZING, "Project not initialized.")
        return None

    if status == DatabaoProjectStatus.NO_DATASOURCES:
        set_status(
            AppStatus.INITIALIZING,
            "No datasources configured. Add datasources to your project first.",
        )
        return None

    try:
        executor_type = st.session_state.get("executor_type", "claude_code")

        cache = _get_or_create_disk_cache()

        with status_context(AppStatus.INITIALIZING, "Loading domain..."):
            _domain = create_domain(project.root_domain_dir)

        from databao.agent.api import agent as create_agent

        llm_config = _build_llm_config()

        kwargs: dict[str, object] = {
            "domain": _domain,
            "cache": cache,
        }
        if llm_config is not None:
            kwargs["llm_config"] = llm_config

        if executor_type == "claude_code":
            from databao.agent.executors import ClaudeCodeExecutor

            kwargs["data_executor"] = ClaudeCodeExecutor()
        else:
            kwargs["executor_type"] = executor_type

        _agent = create_agent(**kwargs)  # type: ignore[arg-type]

        st.session_state.agent = _agent

        return _agent

    except Exception as e:
        logger.exception("Failed to initialize agent")
        set_status(AppStatus.ERROR, f"Failed to initialize agent: {e}")
        return None


def _build_llm_config() -> LLMConfig | None:
    """Build an LLMConfig from session-state LLM settings, or None for defaults."""
    from databao_cli.ui.models.settings import _ENV_VAR_MAP

    llm: LLMSettings = st.session_state.get("llm_settings", LLMSettings())

    if not llm.is_configured:
        return None

    config = llm.active_config
    assert config is not None
    provider_type = llm.active_provider

    env_var = _ENV_VAR_MAP.get(provider_type)
    if env_var and config.api_key:
        os.environ[env_var] = config.api_key

    if provider_type == "ollama" and config.base_url:
        os.environ["OLLAMA_HOST"] = config.base_url

    from databao_cli.executor_utils import build_llm_config

    return build_llm_config(
        config.model,
        provider=provider_type,
        base_url=config.base_url,
    )


def _clear_all_chat_threads() -> None:
    """Clear thread references from all chats.

    Called when agent is reset. Threads will be recreated from
    persistence (cache_scope) when chats are next accessed.
    """
    chats: dict[str, ChatSession] = st.session_state.get("chats", {})
    for chat in chats.values():
        chat.thread = None


def invalidate_agent(status_message: str = "Reloading project...") -> None:
    """Reset the in-memory agent and project so they are re-created on the next rerun.

    Call this whenever the set of datasources changes (add, remove, save)
    to ensure the agent does not reference stale catalogs/schemas.
    """
    st.session_state.databao_project = None
    st.session_state.agent = None
    _clear_all_chat_threads()
    set_status(AppStatus.INITIALIZING, status_message)


def is_read_only_domain() -> bool:
    """Check whether domain-editing operations are disabled."""
    return cast(bool, st.session_state.get("_read_only_domain", False))


def is_hide_build_context_hint() -> bool:
    """Check whether the build context hint and step are hidden."""
    return cast(bool, st.session_state.get("_hide_build_context_hint", False))


def _is_project_ready(project_dir: Path) -> bool:
    """Check if the Databao project is fully set up and ready for normal use."""
    project = find_project(project_dir)
    if project is None:
        return False
    status = databao_project_status(project)
    return status == DatabaoProjectStatus.VALID


def _load_welcome_completed(project: ProjectLayout | None) -> bool:
    """Read the welcome_completed flag from the on-disk settings file.

    This is called early (before full settings load) to decide whether to
    show the setup wizard. Returns False if the project doesn't exist or
    the settings file can't be read.
    """
    if project is None:
        return False
    settings_path = project.databao_dir / "ui" / "settings.yaml"
    if not settings_path.exists():
        return False
    try:
        from databao_cli.ui.models.settings import Settings

        yaml_content = settings_path.read_text()
        settings = Settings.from_yaml(yaml_content)
        return settings.welcome_completed
    except Exception:
        return False


def mark_welcome_completed() -> None:
    """Persist the welcome_completed flag and current agent settings to disk.

    Called when the user finishes the setup wizard. Ensures that executor
    type and LLM configuration (provider, model, api key, etc.) chosen
    during setup are saved, even if the user didn't change them from defaults
    (which means auto_apply never triggered).
    """
    from databao_cli.ui.models.settings import LLMSettings
    from databao_cli.ui.services.settings_persistence import get_or_create_settings, save_settings

    settings = get_or_create_settings()
    settings.welcome_completed = True
    settings.agent.executor_type = st.session_state.get("executor_type", "claude_code")
    llm: LLMSettings = st.session_state.get("llm_settings", LLMSettings())
    settings.agent.llm = llm
    save_settings(settings)
    st.session_state.welcome_completed = True


def _initialize_app(project_dir: Path) -> None:
    """Initialize app-level resources: project and agent.

    This is called on every rerun but returns early if already initialized.
    """

    project = _get_current_project(project_dir)

    status = databao_project_status(project)
    if status == DatabaoProjectStatus.NOT_INITIALIZED:
        set_status(AppStatus.INITIALIZING, "Project not initialized")
        return

    if status == DatabaoProjectStatus.NO_DATASOURCES:
        set_status(AppStatus.INITIALIZING, "No datasources configured")
        return

    with status_context(AppStatus.INITIALIZING, "Loading app data from disk..."):
        _load_persisted_state()

    with status_context(AppStatus.INITIALIZING, "Initializing agent..."):
        agent = _initialize_agent(project)

    if agent:
        set_status(AppStatus.READY)


def init_session_state() -> None:
    """Initialize session state variables."""
    if "chats" not in st.session_state:
        st.session_state.chats = {}
    if "current_chat_id" not in st.session_state:
        st.session_state.current_chat_id = None

    if "databao_project" not in st.session_state:
        st.session_state.databao_project = None
    if "agent" not in st.session_state:
        st.session_state.agent = None
    if "app_status" not in st.session_state:
        st.session_state.app_status = "initializing"
    if "status_message" not in st.session_state:
        st.session_state.status_message = None
    if "executor_type" not in st.session_state:
        st.session_state.executor_type = "claude_code"
    if "llm_provider" not in st.session_state:
        st.session_state.llm_provider = LLMSettings()

    if "suggested_questions" not in st.session_state:
        st.session_state.suggested_questions = []
    if "suggestions_are_llm_generated" not in st.session_state:
        st.session_state.suggestions_are_llm_generated = False
    if "suggestions_status" not in st.session_state:
        st.session_state.suggestions_status = "not_started"
    if "suggestions_future" not in st.session_state:
        st.session_state.suggestions_future = None
    if "suggestions_cancel_event" not in st.session_state:
        st.session_state.suggestions_cancel_event = None

    if "title_futures" not in st.session_state:
        st.session_state.title_futures = {}

    if "build_status" not in st.session_state:
        st.session_state.build_status = "not_started"
    if "build_future" not in st.session_state:
        st.session_state.build_future = None
    if "build_result" not in st.session_state:
        st.session_state.build_result = None
    if "build_error" not in st.session_state:
        st.session_state.build_error = None


def _create_new_chat() -> None:
    """Create a new chat and navigate to it."""
    from uuid6 import uuid6

    from databao_cli.ui.services.chat_persistence import save_chat

    prev_chat_id = st.session_state.get("current_chat_id")
    chats: dict[str, ChatSession] = st.session_state.get("chats", {})
    if prev_chat_id and prev_chat_id in chats:
        prev_chat = chats[prev_chat_id]
        save_chat(prev_chat)

    chat_id = str(uuid6())
    chat = ChatSession(id=chat_id)

    chats[chat_id] = chat
    st.session_state.chats = chats
    st.session_state.current_chat_id = chat_id

    st.session_state._navigate_to_chat = chat_id

    save_chat(chat)


def build_navigation() -> None:
    """Build the full multipage navigation structure (normal mode)."""
    from databao_cli.ui.pages.agent_settings import render_agent_settings_page
    from databao_cli.ui.pages.chat import render_chat_page
    from databao_cli.ui.pages.context_settings import render_context_settings_page
    from databao_cli.ui.pages.general_settings import render_general_settings_page
    from databao_cli.ui.pages.welcome import render_welcome_page

    navigate_to_chat: str | None = st.session_state.get("_navigate_to_chat")
    if navigate_to_chat:
        st.session_state._navigate_to_chat = None

    general_settings_page = st.Page(
        render_general_settings_page,
        title="General",
        icon="🛠️",
        url_path="general-settings",
    )
    context_settings_page = st.Page(
        render_context_settings_page,
        title="Context Settings",
        icon="📊",
        url_path="context-settings",
    )
    agent_settings_page = st.Page(
        render_agent_settings_page,
        title="Agent Settings",
        icon="⚙️",
        url_path="agent-settings",
    )
    settings_pages = [general_settings_page, context_settings_page, agent_settings_page]

    st.session_state._page_general_settings = general_settings_page
    st.session_state._page_context_settings = context_settings_page
    st.session_state._page_agent_settings = agent_settings_page

    chat_pages: list[StreamlitPage] = []

    def new_chat_action() -> None:
        _create_new_chat()
        st.rerun()

    chat_pages.append(
        st.Page(
            new_chat_action,
            title="New Chat",
            icon=":material/add:",
            url_path="new-chat",
        )
    )

    chats: dict[str, ChatSession] = st.session_state.get("chats", {})
    target_chat_page: StreamlitPage | None = None

    if chats:
        sorted_chats = sorted(chats.values(), key=lambda c: c.created_at, reverse=True)

        for chat in sorted_chats:

            def make_chat_page(chat_id: str) -> Callable[[], None]:
                def page_fn() -> None:
                    st.session_state.current_chat_id = chat_id
                    render_chat_page()

                return page_fn

            title = chat.display_title

            is_target = navigate_to_chat == chat.id

            page = st.Page(
                make_chat_page(chat.id),
                title=title,
                icon="💬",
                url_path=f"chat-{chat.id}",
                default=is_target,
            )
            chat_pages.append(page)

            if is_target:
                target_chat_page = page

    welcome_page = st.Page(
        render_welcome_page,
        title="Home",
        icon="🏠",
        url_path="welcome",
        default=(navigate_to_chat is None),
    )

    st.session_state._page_welcome = welcome_page

    pages = {
        "": [welcome_page],
        "Settings": settings_pages,
        "Chats": chat_pages,
    }

    pg = st.navigation(pages)

    if target_chat_page is not None:
        st.switch_page(target_chat_page)

    pg.run()


def build_setup_navigation() -> None:
    """Build navigation for setup mode -- only the setup wizard page, no sidebar."""
    from databao_cli.ui.pages.welcome import render_setup_wizard_page

    setup_page = st.Page(
        render_setup_wizard_page,
        title="Setup",
        icon="🎋",
        url_path="setup",
        default=True,
    )

    pg = st.navigation({"": [setup_page]})
    pg.run()


def _get_current_project(project_dir: Path) -> ProjectLayout:
    """Get the current Databao project, creating a ProjectLayout from the path.

    This is called at app level to determine project status for all pages.
    """
    if st.session_state.get("databao_project") is not None:
        return cast(ProjectLayout, st.session_state.databao_project)

    project = ProjectLayout(project_dir)
    st.session_state.databao_project = project

    return project


def _render_global_sidebar() -> None:
    """Render sidebar elements that appear on all pages.

    This is purely for UI rendering - initialization is handled by _initialize_app().
    """
    from databao_cli.ui.components.sidebar import render_sidebar_header

    with st.sidebar:
        render_sidebar_header()


def main() -> None:
    """Main application entry point."""

    assets_dir = Path(__file__).parent / "assets"
    favicon = assets_dir / "bao.png"

    st.set_page_config(
        page_title="Databao",
        page_icon=str(favicon) if favicon.exists() else "🎋",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-p",
        "--project-dir",
        type=str,
        required=False,
        default=None,
        help="Location of your Databao project (defaults to current directory)",
    )
    parser.add_argument(
        "--read-only-domain",
        action="store_true",
        default=False,
        help="Disable all domain-editing operations (init, datasources, build)",
    )
    parser.add_argument(
        "--hide-suggested-questions",
        action="store_true",
        default=False,
        help="Hide the suggested questions on the empty chat screen",
    )
    parser.add_argument(
        "--hide-build-context-hint",
        action="store_true",
        default=False,
        help="Hide the 'Context isn't built yet' warning and skip the Build Context step in the setup wizard",
    )
    try:
        args = parser.parse_args()
    except SystemExit:
        st.warning("Failed to parse arguments. Using current directory as project directory.")
        args = argparse.Namespace(
            project_dir=None,
            read_only_domain=False,
            hide_suggested_questions=False,
            hide_build_context_hint=False,
        )

    project_dir = Path(args.project_dir) if args.project_dir else Path.cwd()

    init_session_state()

    if "_read_only_domain" not in st.session_state:
        st.session_state._read_only_domain = args.read_only_domain
    if "_hide_suggested_questions" not in st.session_state:
        st.session_state._hide_suggested_questions = args.hide_suggested_questions
    if "_hide_build_context_hint" not in st.session_state:
        st.session_state._hide_build_context_hint = args.hide_build_context_hint

    if "_setup_mode_active" not in st.session_state:
        project = find_project(project_dir)
        welcome_completed = _load_welcome_completed(project)
        st.session_state._setup_mode_active = not welcome_completed and (
            not _is_project_ready(project_dir) or (project is not None and not has_build_output(project))
        )

    is_setup_mode = st.session_state._setup_mode_active and not st.session_state.get("welcome_completed", False)

    st.session_state._project_dir = project_dir

    if is_setup_mode:
        _get_current_project(project_dir)
        build_setup_navigation()
    else:
        _initialize_app(project_dir)
        _render_global_sidebar()
        build_navigation()
        _save_settings_if_changed()


if __name__ == "__main__":
    main()
