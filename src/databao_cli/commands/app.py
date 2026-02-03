"""databao app command - Launch the Databao Streamlit web interface."""

import importlib.util
import subprocess
import sys

import click


def _get_streamlit_app_path() -> str:
    """Get the path to the Streamlit app without importing it.

    This avoids triggering module-level Streamlit code during import.
    """
    spec = importlib.util.find_spec("databao.ui.app")
    if spec is None or spec.origin is None:
        raise click.ClickException(
            "Could not find databao.ui.app module. "
            "Make sure databao[ui] is installed."
        )
    return spec.origin


def app_impl(ctx: click.Context) -> None:
    app_path = _get_streamlit_app_path()

    click.echo("Starting Databao...")

    try:
        subprocess.run(
            [sys.executable, "-m", "streamlit", "run", app_path] + ctx.args,
            check=True,
        )
    except subprocess.CalledProcessError as e:
        click.echo(f"Error running Streamlit: {e}", err=True)
        sys.exit(1)
    except KeyboardInterrupt:
        click.echo("\nShutting down Databao...")
