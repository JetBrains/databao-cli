import importlib
import importlib.util
import subprocess
import sys
from pathlib import Path


def _get_streamlit_app_path() -> str:
    """Get the path to the Streamlit app without importing it.

    This avoids triggering module-level Streamlit code during import.
    """
    spec = importlib.util.find_spec("databao_cli.ui.app")
    if spec is None or spec.origin is None:
        raise ValueError("Could not find databao_cli.ui.app module. ")
    return spec.origin


def bootstrap_streamlit_app(
    project_path: Path,
    streamlit_args: list[str] | None = None,
    *,
    read_only_domain: bool = False,
    hide_suggested_questions: bool = False,
    hide_build_context_hint: bool = False,
) -> None:
    """Bootstrap the UI."""

    if streamlit_args is None:
        streamlit_args = []

    app_path = _get_streamlit_app_path()

    app_args = ["--project-dir", str(project_path)]
    if read_only_domain:
        app_args.append("--read-only-domain")
    if hide_suggested_questions:
        app_args.append("--hide-suggested-questions")
    if hide_build_context_hint:
        app_args.append("--hide-build-context-hint")

    subprocess.run(
        [sys.executable, "-m", "streamlit", "run", app_path, *streamlit_args, "--", *app_args],
        check=True,
    )
