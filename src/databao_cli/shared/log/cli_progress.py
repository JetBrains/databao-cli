from __future__ import annotations

import sys
from collections.abc import Iterator
from contextlib import contextmanager
from dataclasses import dataclass, field

from databao_context_engine.progress.progress import (
    ProgressCallback,
    ProgressEvent,
    ProgressKind,
    ProgressStep,
)
from rich.progress import (
    BarColumn,
    Progress,
    SpinnerColumn,
    TaskID,
    TaskProgressColumn,
    TextColumn,
)
from rich.table import Column

from databao_cli.shared.log.console import rich_console


def _noop_progress_cb(_: ProgressEvent) -> None:
    return


@dataclass
class _StepProgress:
    step: ProgressStep
    units_completed: int
    units_total: int


@dataclass
class _DatasourceProgress:
    datasource_id: str
    step_plan: tuple[ProgressStep, ...] = ()
    completed_steps: set[ProgressStep] = field(default_factory=set)
    current_step_progress: _StepProgress | None = None
    finished: bool = False


@dataclass
class _OperationProgress:
    total_datasources: int | None = None
    completed_datasource_ids: list[str] = field(default_factory=list)
    current_datasource: _DatasourceProgress | None = None


def _compute_percent(ds: _DatasourceProgress) -> float | None:
    if ds.finished:
        return 100.0
    if not ds.step_plan:
        return None
    fraction = 0.0
    p = ds.current_step_progress
    if p is not None and p.units_total > 0:
        fraction = p.units_completed / p.units_total
    return ((len(ds.completed_steps) + fraction) / len(ds.step_plan)) * 100.0


def _apply_event(state: _OperationProgress, ev: ProgressEvent) -> _OperationProgress:
    match ev.kind:
        case ProgressKind.OPERATION_STARTED:
            state.total_datasources = ev.operation_total

        case ProgressKind.OPERATION_FINISHED:
            pass

        case ProgressKind.DATASOURCE_STARTED:
            if state.total_datasources is None:
                state.total_datasources = ev.datasource_total
            state.current_datasource = _DatasourceProgress(datasource_id=ev.datasource_id or "datasource")

        case ProgressKind.DATASOURCE_STEP_PLAN_SET:
            if state.current_datasource is None:
                state.current_datasource = _DatasourceProgress(datasource_id=ev.datasource_id or "datasource")
            state.current_datasource.step_plan = ev.step_plan or ()

        case ProgressKind.DATASOURCE_STEP_COMPLETED:
            ds = state.current_datasource
            if ds is not None and ev.step is not None and ev.step not in ds.completed_steps:
                ds.completed_steps.add(ev.step)
                if ds.current_step_progress is not None and ds.current_step_progress.step == ev.step:
                    ds.current_step_progress = None

        case ProgressKind.DATASOURCE_STEP_PROGRESS:
            ds = state.current_datasource
            if ds is not None and ev.step is not None and ev.step not in ds.completed_steps:
                current = ds.current_step_progress
                new_completed = ev.current_units_completed or 0
                if current is not None and current.step == ev.step:
                    new_completed = max(current.units_completed, new_completed)
                ds.current_step_progress = _StepProgress(
                    step=ev.step,
                    units_completed=new_completed,
                    units_total=ev.current_units_total or 0,
                )

        case ProgressKind.DATASOURCE_FINISHED:
            ds = state.current_datasource
            if ds is not None:
                ds.finished = True
                state.completed_datasource_ids.append(ds.datasource_id)

    return state


class _ProgressRenderer:
    def __init__(self, progress: Progress) -> None:
        self._progress = progress
        self._overall_task_id: TaskID | None = None
        self._datasource_task_id: TaskID | None = None

    def render(self, state: _OperationProgress) -> None:
        self._render_overall(state)
        self._render_datasource(state.current_datasource)

    def _render_overall(self, state: _OperationProgress) -> None:
        completed = len(state.completed_datasource_ids)
        description = f"Datasources {completed}/{state.total_datasources}" if state.total_datasources else "Datasources"
        if self._overall_task_id is None:
            self._overall_task_id = self._progress.add_task(description, total=state.total_datasources, completed=completed)
        else:
            self._progress.update(
                self._overall_task_id,
                description=description,
                total=state.total_datasources,
                completed=float(completed),
            )

    def _render_datasource(self, ds: _DatasourceProgress | None) -> None:
        if ds is None:
            return

        description = f"    {ds.datasource_id}"
        percent = _compute_percent(ds)

        if self._datasource_task_id is None:
            self._datasource_task_id = self._progress.add_task(
                description,
                total=100.0 if percent is not None else None,
                completed=int(percent or 0),
            )
        else:
            self._progress.update(
                self._datasource_task_id,
                description=description,
                total=100.0 if percent is not None else None,
                completed=percent or 0.0,
            )


@contextmanager
def cli_progress() -> Iterator[ProgressCallback]:
    if not sys.stderr.isatty():
        yield _noop_progress_cb
        return

    progress = Progress(
        SpinnerColumn(),
        TextColumn(
            "[progress.description]{task.description}",
            table_column=Column(width=50, overflow="ellipsis", no_wrap=True),
        ),
        BarColumn(),
        TaskProgressColumn(),
        transient=True,
        console=rich_console,
    )

    state = _OperationProgress()
    renderer = _ProgressRenderer(progress)

    def on_event(ev: ProgressEvent) -> None:
        renderer.render(_apply_event(state, ev))

    with progress:
        yield on_event
