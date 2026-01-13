import click

from databao.agents.hello import agents
from databao.dce.hello import dce


@click.group()
def cli():
    """Databao Common CLI"""
    pass


cli.add_command(agents)
cli.add_command(dce)


if __name__ == "__main__":
    cli()
