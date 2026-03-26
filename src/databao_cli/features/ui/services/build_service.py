"""Background build service for the Databao UI.

Runs DCE build_context in a background thread so the user can switch pages.
Follows the same pattern as suggestions.py (ThreadPoolExecutor + session state).
Build log output from DCE is captured via a custom logging handler and displayed live.
"""

import io
import logging
import threading
from concurrent.futures import Future, ThreadPoolExecutor
from concurrent.futures import TimeoutError as FuturesTimeoutError
from pathlib import Path
from typing import cast

import streamlit as st
from databao_context_engine import BuildDatasourceResult

from databao_cli.features.ui.services.dce_operations import build_context

logger = logging.getLogger(__name__)

BuildResult = list[BuildDatasourceResult]

DCE_LOGGER_NAME = "databao_context_engine"


class BuildLogCapture(logging.Handler):
    """Captures log records from DCE into a thread-safe StringIO buffer for UI display."""

    def __init__(self) -> None:
        super().__init__(level=logging.DEBUG)
        self._buffer = io.StringIO()
        self._lock = threading.Lock()
        self.setFormatter(logging.Formatter("%(asctime)s %(levelname)s: %(message)s", datefmt="%H:%M:%S"))

    def emit(self, record: logging.LogRecord) -> None:
        msg = self.format(record)
        with self._lock:
            self._buffer.write(msg + "\n")

    def getvalue(self) -> str:
        with self._lock:
            return self._buffer.getvalue()

    def close(self) -> None:
        super().close()
        self._buffer.close()


@st.cache_resource
def _get_build_executor() -> ThreadPoolExecutor:
    """Get a shared thread pool executor for build operations."""
    return ThreadPoolExecutor(max_workers=1, thread_name_prefix="build")


def _build_task(project_dir: Path, log_capture: BuildLogCapture) -> BuildResult:
    """Background task that runs the build with log capture."""
    dce_logger = logging.getLogger(DCE_LOGGER_NAME)
    dce_logger.addHandler(log_capture)
    original_level = dce_logger.level
    dce_logger.setLevel(logging.DEBUG)
    try:
        return build_context(project_dir)
    except Exception:
        logger.exception("Background build failed")
        raise
    finally:
        dce_logger.removeHandler(log_capture)
        dce_logger.setLevel(original_level)


def start_build(project_dir: Path) -> bool:
    """Start background build.

    Returns True if build was started, False if already running or completed.
    """
    status = st.session_state.get("build_status", "not_started")
    if status == "running":
        return False

    log_capture = BuildLogCapture()
    st.session_state.build_log_capture = log_capture

    executor = _get_build_executor()
    future: Future[BuildResult] = executor.submit(_build_task, project_dir, log_capture)

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
    return cast(str, st.session_state.get("build_status", "not_started"))


def get_build_result() -> BuildResult | None:
    """Return the build result if completed, else None."""
    return st.session_state.get("build_result")


def get_build_error() -> str | None:
    """Return the build error message if failed, else None."""
    return st.session_state.get("build_error")


def get_build_log() -> str:
    """Return the current build log text."""
    capture: BuildLogCapture | None = st.session_state.get("build_log_capture")
    if capture is None:
        return ""
    return capture.getvalue()


def reset_build_state() -> None:
    """Reset build state to allow re-building."""
    st.session_state.build_future = None
    st.session_state.build_status = "not_started"
    st.session_state.build_result = None
    st.session_state.build_error = None
    st.session_state.build_log_capture = None
    logger.info("Reset build state")


def render_build_section(project_dir: Path, *, read_only: bool = False) -> None:
    """Render the build UI section with button, progress, and results.

    Reusable component used by both the welcome wizard and context settings.
    The entire section is a fragment so that build actions only rerun this
    section, not the full page (which would exit setup mode prematurely).

    When *read_only* is True, only the current build status is shown
    (built / not built) without any action buttons.
    """
    if read_only:
        _render_build_status_readonly(project_dir)
        return

    from datetime import timedelta

    @st.fragment(run_every=timedelta(seconds=2))
    def _build_fragment() -> None:
        just_finished = check_build_completion()
        if just_finished:
            st.rerun()

        build_status = get_build_status()

        col_build, col_rebuild = st.columns([3, 1])

        with col_build:
            if build_status == "not_started":
                if st.button("Build context", key="build_btn", type="primary"):
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

        log_text = get_build_log()
        if log_text:
            expanded = build_status == "running"
            with st.expander("Build log", expanded=expanded):
                st.code(log_text, language="log")

    _build_fragment()


def _render_build_status_readonly(project_dir: Path) -> None:
    """Show whether the project has been built, without any action buttons."""
    from databao.agent.integrations.dce import DatabaoContextApi

    try:
        dce_project = DatabaoContextApi.get_dce_project(project_dir)
        has_build = len(dce_project.get_introspected_datasource_list()) > 0
    except Exception:
        has_build = False

    if has_build:
        st.success("Context has been built.", icon="✅")
    else:
        st.caption("Context has not been built yet.")
