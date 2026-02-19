"""Background build service for the Databao UI.

Runs DCE build_context in a background thread so the user can switch pages.
Follows the same pattern as suggestions.py (ThreadPoolExecutor + session state).
"""

import logging
from concurrent.futures import Future, ThreadPoolExecutor
from concurrent.futures import TimeoutError as FuturesTimeoutError
from pathlib import Path

import streamlit as st
from databao_context_engine import BuildDatasourceResult

from databao_cli.ui.services.dce_operations import build_context

logger = logging.getLogger(__name__)

BuildResult = list[BuildDatasourceResult]


@st.cache_resource
def _get_build_executor() -> ThreadPoolExecutor:
    """Get a shared thread pool executor for build operations."""
    return ThreadPoolExecutor(max_workers=1, thread_name_prefix="build")


def _build_task(project_dir: Path) -> BuildResult:
    """Background task that runs the build."""
    try:
        return build_context(project_dir)
    except Exception:
        logger.exception("Background build failed")
        raise


def start_build(project_dir: Path) -> bool:
    """Start background build.

    Returns True if build was started, False if already running or completed.
    """
    status = st.session_state.get("build_status", "not_started")
    if status == "running":
        return False

    executor = _get_build_executor()
    future: Future[BuildResult] = executor.submit(_build_task, project_dir)

    st.session_state.build_future = future
    st.session_state.build_status = "running"
    st.session_state.build_result = None
    st.session_state.build_error = None

    logger.info("Started background build")
    return True


def check_build_completion() -> bool:
    """Check if background build has completed.

    If completed, updates session state with results.

    Returns True if build just finished (caller should rerun to update UI).
    """
    status = st.session_state.get("build_status")
    if status != "running":
        return False

    future: Future[BuildResult] | None = st.session_state.get("build_future")
    if future is None:
        return False

    if not future.done():
        return False

    try:
        result = future.result(timeout=1.0)
        st.session_state.build_result = result
        st.session_state.build_error = None
        st.session_state.build_status = "completed"
        logger.info(f"Build completed: {len(result)} datasources processed")
    except FuturesTimeoutError:
        logger.warning("Timeout getting completed build result")
        return False
    except Exception as e:
        st.session_state.build_result = None
        st.session_state.build_error = str(e)
        st.session_state.build_status = "error"
        logger.exception("Build failed")

    st.session_state.build_future = None
    return True


def is_build_running() -> bool:
    """Check if a build is currently running."""
    return st.session_state.get("build_status") == "running"


def get_build_status() -> str:
    """Return current build status string."""
    return st.session_state.get("build_status", "not_started")


def get_build_result() -> BuildResult | None:
    """Return the build result if completed, else None."""
    return st.session_state.get("build_result")


def get_build_error() -> str | None:
    """Return the build error message if failed, else None."""
    return st.session_state.get("build_error")


def reset_build_state() -> None:
    """Reset build state to allow re-building."""
    st.session_state.build_future = None
    st.session_state.build_status = "not_started"
    st.session_state.build_result = None
    st.session_state.build_error = None
    logger.info("Reset build state")


def render_build_section(project_dir: Path) -> None:
    """Render the build UI section with button, progress, and results.

    Reusable component used by both the welcome wizard and context settings.
    The entire section is a fragment so that build actions only rerun this
    section, not the full page (which would exit setup mode prematurely).
    """
    from datetime import timedelta

    @st.fragment(run_every=timedelta(seconds=2))
    def _build_fragment():
        just_finished = check_build_completion()
        if just_finished:
            st.rerun()

        build_status = get_build_status()

        col_build, col_rebuild = st.columns([3, 1])

        with col_build:
            if build_status == "not_started":
                if st.button("Build Context", key="build_btn", type="primary"):
                    start_build(project_dir)
                    st.rerun(scope="fragment")
            elif build_status == "running":
                st.info("Build is running in the background...", icon="⏳")
            elif build_status == "completed":
                result = get_build_result()
                count = len(result) if result else 0
                st.success(f"Build completed. Processed {count} datasource(s).", icon="✅")
            elif build_status == "error":
                error = get_build_error()
                st.error(f"Build failed: {error}", icon="❌")

        with col_rebuild:
            if build_status in ("completed", "error") and st.button("Rebuild", key="rebuild_btn"):
                reset_build_state()
                start_build(project_dir)
                st.rerun(scope="fragment")

    _build_fragment()
