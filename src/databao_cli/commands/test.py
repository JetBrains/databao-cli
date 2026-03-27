import click

from databao_cli.shared.cli_utils import handle_feature_errors


@click.command()
@handle_feature_errors
def test() -> None:
    """Test command."""
    click.echo("Test command executed successfully!")
