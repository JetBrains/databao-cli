from __future__ import annotations

import logging
import re
import sys
from collections.abc import Iterator
from contextlib import contextmanager
from typing import Any

# Log patterns emitted by databao_context_engine.build_sources.build_runner
_BUILD_START_RE = re.compile(r'^Found datasource of type ".*" with name (.+)$')
_INDEX_START_RE = re.compile(r"^Indexing datasource (.+)$")
_ENRICH_START_RE = re.compile(r"^Enriching context for datasource (.+)$")
_SKIP_RE = re.compile(r"^Skipping disabled datasource (.+)$")
_FAIL_RE = re.compile(r"^Failed to build source at \((.+?)\)")
_FAIL_ENRICH_RE = re.compile(r"^Failed to enrich context for datasource \((.+?)\)")


class _ProgressTrackingHandler(logging.Handler):
    """Intercepts databao_context_engine log messages to drive a Rich progress bar.

    The library processes datasources sequentially. It logs "Found datasource..."
    at the START of each one. We advance the progress bar when we detect that
    a new datasource has started (meaning the previous one finished), and once
    more when the context manager exits (for the last datasource).
    """

    def __init__(
        self,
        progress: Any,
        overall_task: Any,
        datasource_task: Any,
    ) -> None:
        super().__init__()
        self._progress = progress
        self._overall_task = overall_task
        self._datasource_task = datasource_task
        self._has_active = False  # whether a datasource is currently being processed

    def emit(self, record: logging.LogRecord) -> None:
        msg = record.getMessage()

        # Datasource processing started
        m = _BUILD_START_RE.match(msg) or _INDEX_START_RE.match(msg) or _ENRICH_START_RE.match(msg)
        if m:
            if self._has_active:
                # Previous datasource finished — advance
                self._progress.advance(self._overall_task)
            self._has_active = True
            name = m.group(1)
            self._progress.update(self._datasource_task, description=f"  [dim]{name}[/dim]")
            return

        # Datasource skipped (immediately done)
        if _SKIP_RE.match(msg):
            self._progress.advance(self._overall_task)
            return

        # Datasource failed (after "Found datasource", so active is already True)
        if _FAIL_RE.match(msg) or _FAIL_ENRICH_RE.match(msg):
            if self._has_active:
                self._progress.advance(self._overall_task)
                self._has_active = False
            return

    def finish(self) -> None:
        """Advance for the last datasource that was being processed."""
        if self._has_active:
            self._progress.advance(self._overall_task)
            self._has_active = False


@contextmanager
def cli_progress(total: int | None = None, label: str = "Datasources") -> Iterator[None]:
    """Show a Rich progress bar during build/index operations.

    Intercepts ``databao_context_engine`` log messages to track per-datasource progress.
    Redirects library logging through Rich for clean TTY output.

    Args:
        total: Number of datasources to process.
        label: Label for the overall progress bar.
    """
    try:
        from rich.console import Console
        from rich.logging import RichHandler
        from rich.progress import (
            BarColumn,
            MofNCompleteColumn,
            Progress,
            SpinnerColumn,
            TextColumn,
        )
        from rich.table import Column
    except ImportError:
        yield
        return

    console = Console(stderr=True)

    # Rich's is_terminal already checks isatty(), NO_COLOR, TERM=dumb, etc.
    # This prevents progress bar ANSI output from breaking pexpect-based e2e tests.
    if not console.is_terminal:
        yield
        return

    progress = Progress(
        SpinnerColumn(),
        TextColumn(
            "[progress.description]{task.description}",
            table_column=Column(width=50, overflow="ellipsis", no_wrap=True),
        ),
        BarColumn(),
        MofNCompleteColumn(),
        transient=True,
        console=console,
    )

    overall_task = progress.add_task(label, total=total)
    datasource_task = progress.add_task("  [dim]starting…[/dim]", total=None)

    # --- logging setup ---
    engine_logger = logging.getLogger("databao_context_engine")
    cli_logger = logging.getLogger("databao_cli")

    prev_engine = (list(engine_logger.handlers), engine_logger.propagate)
    prev_cli = (list(cli_logger.handlers), cli_logger.propagate)

    def _is_console_handler(h: logging.Handler) -> bool:
        return isinstance(h, logging.StreamHandler) and getattr(h, "stream", None) in (sys.stderr, sys.stdout)

    rich_handler = RichHandler(
        console=console,
        show_time=False,
        show_level=True,
        show_path=False,
        rich_tracebacks=False,
    )

    tracker = _ProgressTrackingHandler(progress, overall_task, datasource_task)
    tracker.setLevel(logging.DEBUG)

    try:
        for lgr in (engine_logger, cli_logger):
            kept = [h for h in lgr.handlers if not _is_console_handler(h)]
            lgr.handlers = [*kept, rich_handler]
            lgr.propagate = False

        engine_logger.addHandler(tracker)

        with progress:
            yield

        tracker.finish()
    finally:
        engine_logger.handlers = prev_engine[0]
        engine_logger.propagate = prev_engine[1]
        cli_logger.handlers = prev_cli[0]
        cli_logger.propagate = prev_cli[1]
