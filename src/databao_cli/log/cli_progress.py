from __future__ import annotations

import logging
import sys
from collections.abc import Iterator
from contextlib import contextmanager
from typing import TypedDict

from databao_context_engine.progress.progress import (
    ProgressCallback,
    ProgressEvent,
    ProgressKind,
)


def _noop_progress_cb(_: ProgressEvent) -> None:
    return


class _UIState(TypedDict):
    datasource_index: int | None
    datasource_total: int | None
    total_steps: int | None
    completed_steps: int
    current_units_completed: int | None
    current_units_total: int | None
    last_percent: float


@contextmanager
def cli_progress() -> Iterator[ProgressCallback]:
    try:
        from rich.console import Console
        from rich.logging import RichHandler
        from rich.progress import (
            BarColumn,
            Progress,
            SpinnerColumn,
            TaskID,
            TaskProgressColumn,
            TextColumn,
        )
        from rich.table import Column
    except ImportError:
        yield _noop_progress_cb
        return

    if not sys.stderr.isatty():
        yield _noop_progress_cb
        return

    console = Console(stderr=True)

    @contextmanager
    def _use_rich_console_logging() -> Iterator[None]:
        logger_names = ("databao_context_engine", "databao_cli")
        previous_state: dict[str, tuple[list[logging.Handler], bool]] = {}

        def _is_console_handler(h: logging.Handler) -> bool:
            return isinstance(h, logging.StreamHandler) and getattr(h, "stream", None) in (sys.stderr, sys.stdout)

        rich_handler = RichHandler(
            console=console,
            show_time=False,
            show_level=True,
            show_path=False,
            rich_tracebacks=False,
        )

        try:
            for logger_name in logger_names:
                logger = logging.getLogger(logger_name)
                prev_handlers = list(logger.handlers)
                prev_propagate = logger.propagate
                previous_state[logger_name] = (prev_handlers, prev_propagate)

                kept_handlers = [h for h in prev_handlers if not _is_console_handler(h)]
                logger.handlers = [*kept_handlers, rich_handler]
                logger.propagate = False

            yield
        finally:
            for logger_name, (prev_handlers, prev_propagate) in previous_state.items():
                logger = logging.getLogger(logger_name)
                logger.handlers = prev_handlers
                logger.propagate = prev_propagate

    task_ids: dict[str, TaskID] = {}
    progress_state: _UIState = {
        "datasource_index": None,
        "datasource_total": None,
        "total_steps": None,
        "completed_steps": 0,
        "current_units_completed": None,
        "current_units_total": None,
        "last_percent": 0.0,
    }

    progress = Progress(
        SpinnerColumn(),
        TextColumn(
            "[progress.description]{task.description}",
            table_column=Column(width=50, overflow="ellipsis", no_wrap=True),
        ),
        BarColumn(),
        TaskProgressColumn(),
        transient=True,
        console=console,
        redirect_stdout=True,
        redirect_stderr=True,
    )

    def _get_or_create_overall_task(total: int | None) -> TaskID:
        if "overall" not in task_ids:
            task_ids["overall"] = progress.add_task("Datasources", total=total)
        elif total is not None:
            progress.update(task_ids["overall"], total=total)
        return task_ids["overall"]

    def _get_or_create_datasource_task() -> TaskID:
        if "datasource" not in task_ids:
            task_ids["datasource"] = progress.add_task("Datasource", total=None)
        return task_ids["datasource"]

    def _set_datasource_percent(percent: float) -> None:
        task_id = _get_or_create_datasource_task()
        clamped = max(0.0, min(100.0, percent))
        progress.update(task_id, total=100.0, completed=clamped)

    def _update_overall_description() -> None:
        if "overall" not in task_ids:
            return
        idx = progress_state["datasource_index"]
        total = progress_state["datasource_total"]
        if idx is not None and total is not None:
            progress.update(task_ids["overall"], description=f"Datasources {idx}/{total}")

    def _compute_percent() -> float | None:
        total_steps = progress_state["total_steps"]
        if total_steps is None or total_steps <= 0:
            return None

        fraction = 0.0
        if (
            progress_state["current_units_completed"] is not None
            and progress_state["current_units_total"] is not None
            and progress_state["current_units_total"] > 0
        ):
            fraction = progress_state["current_units_completed"] / progress_state["current_units_total"]

        return ((progress_state["completed_steps"] + fraction) / total_steps) * 100.0

    def _update_datasource_percent() -> None:
        percent = _compute_percent()
        if percent is None:
            return
        percent = max(progress_state["last_percent"], percent)
        progress_state["last_percent"] = percent
        _set_datasource_percent(percent)

    def on_event(ev: ProgressEvent) -> None:
        match ev.kind:
            case ProgressKind.OPERATION_STARTED:
                _get_or_create_overall_task(ev.operation_total)
                return

            case ProgressKind.OPERATION_FINISHED:
                return

            case ProgressKind.DATASOURCE_STARTED:
                progress_state["datasource_index"] = ev.datasource_index
                progress_state["datasource_total"] = ev.datasource_total
                progress_state["total_steps"] = None
                progress_state["completed_steps"] = 0
                progress_state["current_units_completed"] = None
                progress_state["current_units_total"] = None
                progress_state["last_percent"] = 0.0

                _get_or_create_overall_task(ev.datasource_total)
                _update_overall_description()

                task_id = _get_or_create_datasource_task()

                progress.reset(task_id, completed=0, total=None, description=f"    {ev.datasource_id or 'datasource'}")
                return

            case ProgressKind.DATASOURCE_TOTAL_STEPS_SET:
                progress_state["total_steps"] = ev.total_steps
                _update_datasource_percent()
                return

            case ProgressKind.DATASOURCE_STEP_COMPLETED:
                progress_state["completed_steps"] += ev.step_increment or 1
                progress_state["current_units_completed"] = None
                progress_state["current_units_total"] = None
                _update_datasource_percent()
                return

            case ProgressKind.DATASOURCE_CURRENT_STEP_PROGRESS:
                progress_state["current_units_completed"] = ev.current_units_completed
                progress_state["current_units_total"] = ev.current_units_total
                _update_datasource_percent()
                return

            case ProgressKind.DATASOURCE_FINISHED:
                idx = ev.datasource_index or 0
                total = ev.datasource_total or 0
                ds = ev.datasource_id or "(unknown datasource)"
                status = ev.status or "done"

                progress.console.print(f"{status.upper()} {idx}/{total}: {ds}")

                _set_datasource_percent(100.0)

                _get_or_create_overall_task(ev.datasource_total)
                progress.advance(task_ids["overall"], 1)
                _update_overall_description()
                return

    with _use_rich_console_logging(), progress:
        yield on_event
