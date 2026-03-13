"""databao app command - Launch the Databao Streamlit web interface."""

import subprocess
import sys

import click

from databao_cli.ui.cli import bootstrap_streamlit_app


def app_impl(ctx: click.Context) -> None:
    click.echo("Starting Databao UI...")

    try:
        bootstrap_streamlit_app(
            ctx.obj["project_dir"],
            ctx.args,
            read_only_domain=ctx.obj.get("read_only_domain", False),
            hide_suggested_questions=ctx.obj.get("hide_suggested_questions", False),
            hide_build_context_hint=ctx.obj.get("hide_build_context_hint", False),
        )
    except subprocess.CalledProcessError as e:
        click.echo(f"Error running Streamlit: {e}", err=True)
        sys.exit(1)
    except KeyboardInterrupt:
        click.echo("\nShutting down Databao...")
