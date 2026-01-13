import click


@click.group()
def dce():
    """DCE-related commands"""
    pass


@dce.command()
def hello():
    click.echo("Hello from DCE!")
