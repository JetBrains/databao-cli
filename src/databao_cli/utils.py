import sys
from typing import Any

import click
import questionary

_labels: dict[str, str] = {}


def register_labels(labels: dict[str, str]) -> None:
    _labels.update(labels)


def _resolve(value: str) -> tuple[str, str]:
    label = _labels.get(value, value)
    return value, label


def is_interactive() -> bool:
    """True when running in an interactive terminal."""
    return sys.stdin.isatty() and sys.stdout.isatty()


def ask_select(message: str, choices: list[str], default: str | None = None) -> str:
    """Select from a list. Interactive in TTY, plain text otherwise."""
    if is_interactive():
        resolved = [_resolve(c) if isinstance(c, str) else c for c in choices]
        q_choices = [questionary.Choice(title=label, value=value) for value, label in resolved]
        result: Any = questionary.select(message, choices=q_choices, default=default).ask()
        if result is None:
            raise click.Abort()
        return str(result)
    else:
        click.echo(f"{message}")
        for i, choice in enumerate(choices, 1):
            click.echo(f"  {i}. {choice}")
        value: str = click.prompt(
            "Enter a number of value",
            default=default or choices[0],
        )
        if value.isdigit() and 1 <= int(value) <= len(choices):
            return choices[int(value) - 1]
        if value in choices:
            return value
        raise click.BadParameter(f"Invalid choice: {value}")


def ask_confirm(message: str, default: bool = True, abort: bool = False) -> bool:
    """Yes/no. Fancy in TTY, plain click.confirm otherwise."""
    if is_interactive():
        result: Any = questionary.confirm(message, default=default).ask()
        if result is None:
            raise click.Abort()
        if abort and not result:
            raise click.Abort()
        return bool(result)
    else:
        return click.confirm(message, default=default, abort=abort)


def ask_text(message: str, default: str | None = None, allow_empty: bool = False) -> str:
    """Text input. Interactive in TTY, plain click.prompt otherwise."""
    if is_interactive():
        while True:
            result: Any = questionary.text(message, default=default or "").ask()
            value = str(result) if result is not None else ""
            if value.strip() or allow_empty:
                return value
            click.echo("Value cannot be empty. Please try again.")
    else:
        value: str = click.prompt(message, default=default)
        return value
