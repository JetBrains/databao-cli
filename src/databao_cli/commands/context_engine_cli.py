from typing import Any

import click
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

        is_optional = "(Optional)" in text
        if default_value:
            final_default = default_value
        elif is_optional and final_type is str:
            final_default = ""
        elif final_type is str:
            final_default = None
        else:
            final_default = None

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
