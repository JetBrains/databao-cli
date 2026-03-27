import click

from databao_cli.commands.datasource.add import add
from databao_cli.commands.datasource.check import check


@click.group()
def datasource() -> None:
    """Manage datasource configurations."""


datasource.add_command(add)
datasource.add_command(check)
