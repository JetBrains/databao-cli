import click


@click.group()
def agents():
    """Agents-related commands"""
    pass


@agents.command()
def hello():
    click.echo("Hello from Agents!")
