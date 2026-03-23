"""databao app command - Launch the Databao Streamlit web interface."""

import subprocess
import sys

import click

from databao_cli.ui.cli import bootstrap_streamlit_app


@click.command(
    context_settings={"ignore_unknown_options": True, "allow_extra_args": True},
)
@click.option(
    "--read-only-domain",
    is_flag=True,
    default=False,
    help="Disable all domain-editing operations (init, datasources, build) in the UI",
)
@click.option(
    "--hide-suggested-questions",
    is_flag=True,
    default=False,
    help="Hide the suggested questions on the empty chat screen",
)
@click.option(
    "--hide-build-context-hint",
    is_flag=True,
    default=False,
    help=(
        "Hide the 'Context isn't built yet' warning on the empty chat screen and "
        "remove the Build Context step from the setup wizard"
    ),
)
@click.pass_context
def app(
    ctx: click.Context,
    read_only_domain: bool,
    hide_suggested_questions: bool,
    hide_build_context_hint: bool,
) -> None:
    """Launch the Databao Streamlit web interface.

    All additional arguments are passed directly to streamlit run.

    \b
    Examples:
        databao app
        databao app --server.port 8502
        databao app --server.headless true
        databao app --read-only-domain
    """
    ctx.obj["read_only_domain"] = read_only_domain
    ctx.obj["hide_suggested_questions"] = hide_suggested_questions
    ctx.obj["hide_build_context_hint"] = hide_build_context_hint
    app_impl(ctx)


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
