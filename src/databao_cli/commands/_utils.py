"""Shared CLI utilities for command implementations."""

import sys
from pathlib import Path

import click

from databao_cli.project.layout import ProjectLayout, find_project


def get_project_or_exit(project_dir: Path) -> ProjectLayout:
    """Return the project layout or exit with an error if no project is found."""
    project_layout = find_project(project_dir)
    if not project_layout:
        click.echo("No project found.")
        sys.exit(1)
    return project_layout
