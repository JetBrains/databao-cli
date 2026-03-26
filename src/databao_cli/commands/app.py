"""databao app command - Launch the Databao Streamlit web interface."""

import click

from databao_cli.shared.cli_utils import handle_feature_errors


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
@handle_feature_errors
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
    from databao_cli.features.ui.cli import app_impl

    click.echo("Starting Databao UI...")
    try:
        app_impl(
            ctx.obj["project_dir"],
            ctx.args,
            read_only_domain=read_only_domain,
            hide_suggested_questions=hide_suggested_questions,
            hide_build_context_hint=hide_build_context_hint,
        )
    except KeyboardInterrupt:
        click.echo("\nShutting down Databao...")
