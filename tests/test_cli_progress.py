"""Tests for the cli_progress module."""

from __future__ import annotations

from typing import Any
from unittest.mock import patch

from databao_cli.shared.log.cli_progress import cli_progress


def test_cli_progress_noop_when_not_terminal() -> None:
    """Progress context manager yields without error when console is not a terminal."""
    with patch("rich.console.Console") as mock_console_cls:
        mock_console_cls.return_value.is_terminal = False
        with cli_progress():
            pass  # Should not raise


def test_cli_progress_noop_when_rich_not_available() -> None:
    """Progress context manager yields without error when Rich is not installed."""
    import builtins

    original_import = builtins.__import__

    def mock_import(name: str, *args: Any, **kwargs: Any) -> object:
        if name == "rich.console":
            raise ImportError("No module named 'rich'")
        return original_import(name, *args, **kwargs)

    with patch("builtins.__import__", side_effect=mock_import), cli_progress():
        pass  # Should not raise
