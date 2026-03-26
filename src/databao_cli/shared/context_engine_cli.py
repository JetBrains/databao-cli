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
        show_default = default_value is not None and default_value != ""
        final_type = click.Choice(type.choices) if isinstance(type, Choice) else str

        # click.prompt does not let optional string fields be skipped cleanly when
        # default is None, so use "" and let config_wizard normalize it back to None.
        click_default = default_value
        if final_type is str and default_value is None:
            click_default = ""

        return click.prompt(
            text=text,
            default=click_default,
            hide_input=is_secret,
            type=final_type,
            show_default=show_default,
        )

    def confirm(self, text: str) -> bool:
        return click.confirm(text=text)

    def on_validation_error(self, property_key: str, input_value: Any, error_message: str) -> None:
        click.echo(f"Invalid value for '{property_key}': {error_message}", err=True)
