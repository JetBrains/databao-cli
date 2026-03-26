"""Tests for the cli_progress module."""

from __future__ import annotations

import logging
from typing import Any
from unittest.mock import MagicMock, patch

from databao_cli.shared.log.cli_progress import cli_progress


def test_cli_progress_noop_when_not_tty() -> None:
    """Progress context manager yields without error when stderr is not a TTY."""
    with patch("sys.stderr") as mock_stderr:
        mock_stderr.isatty.return_value = False
        with cli_progress(total=5, label="Test"):
            pass  # Should not raise


def test_cli_progress_noop_when_rich_not_available() -> None:
    """Progress context manager yields without error when Rich is not installed."""
    import builtins

    original_import = builtins.__import__

    def mock_import(name: str, *args: Any, **kwargs: Any) -> object:
        if name == "rich.console":
            raise ImportError("No module named 'rich'")
        return original_import(name, *args, **kwargs)

    with patch("builtins.__import__", side_effect=mock_import), cli_progress(total=3, label="Test"):
        pass  # Should not raise


def test_progress_tracking_handler_advances_on_datasource_start() -> None:
    """The tracking handler advances the progress bar when a new datasource starts."""
    from databao_cli.shared.log.cli_progress import _ProgressTrackingHandler

    mock_progress = MagicMock()
    overall_task = MagicMock()
    ds_task = MagicMock()

    handler = _ProgressTrackingHandler(mock_progress, overall_task, ds_task)

    # First datasource — no advance (nothing to finish)
    record = logging.LogRecord(
        name="test",
        level=logging.INFO,
        pathname="",
        lineno=0,
        msg='Found datasource of type "duckdb" with name my_db',
        args=(),
        exc_info=None,
    )
    handler.emit(record)
    mock_progress.advance.assert_not_called()
    mock_progress.update.assert_called_once_with(ds_task, description="  [dim]my_db[/dim]")

    mock_progress.reset_mock()

    # Second datasource — advance for first
    record2 = logging.LogRecord(
        name="test",
        level=logging.INFO,
        pathname="",
        lineno=0,
        msg='Found datasource of type "csv" with name my_csv',
        args=(),
        exc_info=None,
    )
    handler.emit(record2)
    mock_progress.advance.assert_called_once_with(overall_task)


def test_progress_tracking_handler_advances_on_skip() -> None:
    """The tracking handler advances when a datasource is skipped."""
    from databao_cli.shared.log.cli_progress import _ProgressTrackingHandler

    mock_progress = MagicMock()
    handler = _ProgressTrackingHandler(mock_progress, "overall", "ds")

    record = logging.LogRecord(
        name="test",
        level=logging.INFO,
        pathname="",
        lineno=0,
        msg="Skipping disabled datasource my_ds",
        args=(),
        exc_info=None,
    )
    handler.emit(record)
    mock_progress.advance.assert_called_once_with("overall")


def test_progress_tracking_handler_advances_on_failure() -> None:
    """The tracking handler advances when a datasource fails."""
    from databao_cli.shared.log.cli_progress import _ProgressTrackingHandler

    mock_progress = MagicMock()
    handler = _ProgressTrackingHandler(mock_progress, "overall", "ds")

    # Start a datasource first
    record1 = logging.LogRecord(
        name="test",
        level=logging.INFO,
        pathname="",
        lineno=0,
        msg='Found datasource of type "duckdb" with name my_db',
        args=(),
        exc_info=None,
    )
    handler.emit(record1)

    # Fail it
    record2 = logging.LogRecord(
        name="test",
        level=logging.INFO,
        pathname="",
        lineno=0,
        msg="Failed to build source at (my_db): connection error",
        args=(),
        exc_info=None,
    )
    handler.emit(record2)
    mock_progress.advance.assert_called_once_with("overall")


def test_progress_tracking_handler_finish_advances_last() -> None:
    """finish() advances the bar for the last datasource that was being processed."""
    from databao_cli.shared.log.cli_progress import _ProgressTrackingHandler

    mock_progress = MagicMock()
    handler = _ProgressTrackingHandler(mock_progress, "overall", "ds")

    record = logging.LogRecord(
        name="test",
        level=logging.INFO,
        pathname="",
        lineno=0,
        msg='Found datasource of type "duckdb" with name my_db',
        args=(),
        exc_info=None,
    )
    handler.emit(record)
    mock_progress.advance.assert_not_called()

    handler.finish()
    mock_progress.advance.assert_called_once_with("overall")


def test_progress_tracking_handler_finish_noop_when_no_active() -> None:
    """finish() does nothing if no datasource was active."""
    from databao_cli.shared.log.cli_progress import _ProgressTrackingHandler

    mock_progress = MagicMock()
    handler = _ProgressTrackingHandler(mock_progress, "overall", "ds")

    handler.finish()
    mock_progress.advance.assert_not_called()


def test_progress_tracking_handler_index_pattern() -> None:
    """The handler recognizes indexing log messages."""
    from databao_cli.shared.log.cli_progress import _ProgressTrackingHandler

    mock_progress = MagicMock()
    handler = _ProgressTrackingHandler(mock_progress, "overall", "ds")

    record = logging.LogRecord(
        name="test",
        level=logging.INFO,
        pathname="",
        lineno=0,
        msg="Indexing datasource my_ds",
        args=(),
        exc_info=None,
    )
    handler.emit(record)
    mock_progress.update.assert_called_once_with("ds", description="  [dim]my_ds[/dim]")
