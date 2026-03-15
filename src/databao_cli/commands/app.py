"""databao app command - Launch the Databao Streamlit web interface."""

import subprocess
import sys

import click

from databao_cli.ui.cli import bootstrap_streamlit_app


def app_impl(ctx: click.Context) -> None:
    click.echo("Starting Databao web interface...")

    try:
        bootstrap_streamlit_app(
            ctx.obj["project_dir"],
            ctx.args,
            read_only_domain=ctx.obj.get("read_only_domain", False),
        )
    except subprocess.CalledProcessError as e:
        click.echo(f"Error starting web interface: {e}", err=True)
        sys.exit(1)
    except KeyboardInterrupt:
        click.echo("\nShutting down...")
