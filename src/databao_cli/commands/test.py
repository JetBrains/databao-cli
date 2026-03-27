import click

from databao_cli.shared.cli_utils import handle_feature_errors


@click.command()
@click.pass_context
@handle_feature_errors
def test(ctx: click.Context) -> None:
    """Test command."""
    click.echo("Test command executed successfully!")
