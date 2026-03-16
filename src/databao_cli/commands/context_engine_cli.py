import sys
from typing import Any

import click
import questionary
from databao_context_engine import Choice, UserInputCallback


class ClickUserInputCallback(UserInputCallback):
    def prompt(
        self,
        text: str,
        type: Choice | Any | None = None,
        default_value: Any | None = None,
        is_secret: bool = False,
    ) -> Any:
        show_default: bool = default_value is not None and default_value != ""
        final_type = click.Choice(type.choices) if isinstance(type, Choice) else str

        # Determine if this field is optional
        is_optional = "(Optional)" in text

        if isinstance(type, Choice):
            is_interactive = sys.stdin.isatty() and sys.stdout.isatty()
            if is_interactive:
                from databao_cli.labels import LABELS

                choices = [
                    questionary.Choice(title=LABELS.get(choice, choice), value=choice) for choice in type.choices
                ]
                result = questionary.select(
                    text, choices=choices, default=default_value if default_value in type.choices else None
                ).ask()
                if result is None:
                    raise click.Abort()
                return result
            else:
                return click.prompt(
                    text=text,
                    default=default_value,
                    hide_input=is_secret,
                    type=click.Choice(type.choices),
                    show_default=show_default,
                )

        if default_value:
            final_default = default_value
        elif is_optional:
            final_default = ""
        else:
            final_default = None

        is_interactive = sys.stdin.isatty() and sys.stdout.isatty()
        if is_interactive and final_type is str:
            if is_secret:
                prompt_func = questionary.password
            else:
                prompt_func = questionary.text

            if not is_optional and final_default is None:
                while True:
                    result = prompt_func(text, default=final_default or "").ask()
                    if result is None:
                        raise click.Abort()
                    value = str(result).strip()
                    if value:
                        return value
                    click.echo("This field is required and cannot be empty. Please try again.")
            else:
                result = prompt_func(text, default=final_default or "").ask()
                if result is None:
                    raise click.Abort()
                return str(result)
        else:
            if final_type is str and not is_optional and final_default is None:
                while True:
                    value = click.prompt(
                        text=text, default=final_default, hide_input=is_secret, type=final_type, show_default=show_default
                    )
                    if value and value.strip():
                        return value
                    click.echo("This field is required and cannot be empty. Please try again.")
            else:
                return click.prompt(
                    text=text, default=final_default, hide_input=is_secret, type=final_type, show_default=show_default
                )

    def confirm(self, text: str) -> bool:
        return click.confirm(text=text)
