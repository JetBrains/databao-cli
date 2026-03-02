"""User-friendly error messages for LLM provider API errors.

Each provider has a dedicated formatter that recognises known error shapes
(e.g. model-not-found) and returns a human-readable string.
Unrecognised errors fall through and the original message is preserved.
"""

from collections.abc import Callable

import anthropic
import openai


def format_llm_error(e: Exception) -> str:
    """Return a user-friendly message for known LLM API errors, or ``str(e)`` as fallback."""
    for formatter in _FORMATTERS:
        result = formatter(e)
        if result is not None:
            return result
    return str(e)


# ---------------------------------------------------------------------------
# OpenAI
# ---------------------------------------------------------------------------


def _format_openai_error(e: Exception) -> str | None:
    if not isinstance(e, openai.APIStatusError):
        return None

    body = e.body
    if isinstance(body, dict) and body.get("code") == "model_not_found":
        return body.get("message", "Model was not found. Please check the model name and try again.")

    return None


# ---------------------------------------------------------------------------
# Anthropic
# ---------------------------------------------------------------------------


def _format_anthropic_error(e: Exception) -> str | None:
    if not isinstance(e, anthropic.APIStatusError):
        return None

    body = e.body
    if not isinstance(body, dict):
        return None

    error_detail = body.get("error")
    if not isinstance(error_detail, dict):
        return None

    if error_detail.get("type") == "not_found_error":
        msg = error_detail.get("message", "")
        if isinstance(msg, str) and msg.startswith("model: "):
            model_name = msg[len("model: ") :]
            return f'Model "{model_name}" was not found. Please check the model name and try again.'

    return None


# ---------------------------------------------------------------------------
# Registry — add new provider formatters here
# ---------------------------------------------------------------------------

_FORMATTERS: list[Callable[[Exception], str | None]] = [
    _format_openai_error,
    _format_anthropic_error,
]
