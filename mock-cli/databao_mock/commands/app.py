from pathlib import Path

import click


def app_impl(project_dir: Path) -> None:
    click.echo(f"\nStarting Databao web interface for {project_dir.resolve()} ...")
    click.echo(click.style("  (not yet implemented)", fg="yellow"))
