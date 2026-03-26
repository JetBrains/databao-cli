"""Shared CLI utilities for command implementations."""

import functools
import sys
from collections.abc import Callable
from pathlib import Path
from typing import Any

import click

from databao_cli.shared.errors import FeatureError
from databao_cli.shared.project.layout import ProjectLayout, find_project


def get_project_or_raise(project_dir: Path) -> ProjectLayout:
    """Return the project layout or raise FeatureError if no project is found."""
    project_layout = find_project(project_dir)
    if not project_layout:
        raise FeatureError("No project found.")
    return project_layout


def handle_feature_errors(f: Callable[..., Any]) -> Callable[..., Any]:
    """Decorator that catches FeatureError and converts it to a CLI error exit."""

    @functools.wraps(f)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        try:
            return f(*args, **kwargs)
        except FeatureError as e:
            click.echo(e.message, err=True)
            sys.exit(e.exit_code)

    return wrapper
