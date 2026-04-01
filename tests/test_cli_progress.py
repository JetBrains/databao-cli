"""Tests for the cli_progress module."""

from __future__ import annotations

from unittest.mock import patch

import pytest
from databao_context_engine.progress.progress import ProgressEvent, ProgressKind, ProgressStep

from databao_cli.shared.log.cli_progress import (
    _apply_event,
    _compute_percent,
    _DatasourceProgress,
    _OperationProgress,
    _StepProgress,
    cli_progress,
)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _event(kind: ProgressKind, **kwargs: object) -> ProgressEvent:
    return ProgressEvent(kind=kind, **kwargs)  # type: ignore[arg-type]


STEPS = (ProgressStep.PLUGIN_EXECUTION, ProgressStep.CONTEXT_ENRICHMENT, ProgressStep.EMBEDDING)


# ---------------------------------------------------------------------------
# _compute_percent
# ---------------------------------------------------------------------------


class TestComputePercent:
    def test_returns_none_when_no_step_plan(self) -> None:
        ds = _DatasourceProgress(datasource_id="ds")
        assert _compute_percent(ds) is None

    def test_returns_100_when_finished(self) -> None:
        ds = _DatasourceProgress(datasource_id="ds", finished=True)
        assert _compute_percent(ds) == 100.0

    def test_returns_100_when_finished_regardless_of_step_plan(self) -> None:
        ds = _DatasourceProgress(datasource_id="ds", step_plan=STEPS, finished=True)
        assert _compute_percent(ds) == 100.0

    def test_zero_percent_when_no_steps_completed(self) -> None:
        ds = _DatasourceProgress(datasource_id="ds", step_plan=STEPS)
        assert _compute_percent(ds) == 0.0

    def test_partial_steps_completed(self) -> None:
        ds = _DatasourceProgress(
            datasource_id="ds",
            step_plan=STEPS,
            completed_steps={ProgressStep.PLUGIN_EXECUTION},
        )
        assert _compute_percent(ds) == pytest.approx(100.0 / 3)

    def test_all_steps_completed(self) -> None:
        ds = _DatasourceProgress(
            datasource_id="ds",
            step_plan=STEPS,
            completed_steps=set(STEPS),
        )
        assert _compute_percent(ds) == pytest.approx(100.0)

    def test_intra_step_progress(self) -> None:
        ds = _DatasourceProgress(
            datasource_id="ds",
            step_plan=STEPS,
            completed_steps={ProgressStep.PLUGIN_EXECUTION},
            current_step_progress=_StepProgress(
                step=ProgressStep.CONTEXT_ENRICHMENT,
                units_completed=1,
                units_total=4,
            ),
        )
        # 1 completed + 0.25 fraction = 1.25 / 3
        assert _compute_percent(ds) == pytest.approx(1.25 / 3 * 100)

    def test_intra_step_progress_ignored_when_units_total_is_zero(self) -> None:
        ds = _DatasourceProgress(
            datasource_id="ds",
            step_plan=STEPS,
            current_step_progress=_StepProgress(
                step=ProgressStep.PLUGIN_EXECUTION,
                units_completed=0,
                units_total=0,
            ),
        )
        assert _compute_percent(ds) == 0.0


# ---------------------------------------------------------------------------
# _apply_event
# ---------------------------------------------------------------------------


class TestApplyEventOperationStarted:
    def test_sets_total_datasources(self) -> None:
        state = _OperationProgress()
        _apply_event(state, _event(ProgressKind.OPERATION_STARTED, operation_total=5))
        assert state.total_datasources == 5


class TestApplyEventDatasourceStarted:
    def test_creates_current_datasource(self) -> None:
        state = _OperationProgress()
        _apply_event(state, _event(ProgressKind.DATASOURCE_STARTED, datasource_id="my_ds"))
        assert state.current_datasource is not None
        assert state.current_datasource.datasource_id == "my_ds"

    def test_uses_fallback_id_when_none(self) -> None:
        state = _OperationProgress()
        _apply_event(state, _event(ProgressKind.DATASOURCE_STARTED, datasource_id=None))
        assert state.current_datasource is not None
        assert state.current_datasource.datasource_id == "datasource"

    def test_resets_datasource_state_between_datasources(self) -> None:
        state = _OperationProgress()
        _apply_event(state, _event(ProgressKind.DATASOURCE_STARTED, datasource_id="ds1"))
        _apply_event(state, _event(ProgressKind.DATASOURCE_STEP_PLAN_SET, datasource_id="ds1", step_plan=STEPS))
        assert state.current_datasource is not None
        assert state.current_datasource.datasource_id == "ds1"
        assert state.current_datasource.step_plan == STEPS

        # Start new datasource without finishing the previous one
        _apply_event(state, _event(ProgressKind.DATASOURCE_STARTED, datasource_id="ds2"))
        assert state.current_datasource is not None
        assert state.current_datasource.datasource_id == "ds2"
        assert state.current_datasource.step_plan == ()


class TestApplyEventDatasourceStepPlanSet:
    def test_sets_step_plan(self) -> None:
        state = _OperationProgress(current_datasource=_DatasourceProgress(datasource_id="ds"))
        _apply_event(state, _event(ProgressKind.DATASOURCE_STEP_PLAN_SET, step_plan=STEPS))
        assert state.current_datasource is not None
        assert state.current_datasource.step_plan == STEPS

    def test_implicitly_creates_datasource_when_none(self) -> None:
        state = _OperationProgress()
        _apply_event(state, _event(ProgressKind.DATASOURCE_STEP_PLAN_SET, datasource_id="ds", step_plan=STEPS))
        assert state.current_datasource is not None
        assert state.current_datasource.datasource_id == "ds"
        assert state.current_datasource.step_plan == STEPS


class TestApplyEventDatasourceStepCompleted:
    def test_adds_to_completed_steps(self) -> None:
        state = _OperationProgress(current_datasource=_DatasourceProgress(datasource_id="ds"))
        _apply_event(state, _event(ProgressKind.DATASOURCE_STEP_COMPLETED, step=ProgressStep.PLUGIN_EXECUTION))
        assert ProgressStep.PLUGIN_EXECUTION in state.current_datasource.completed_steps  # type: ignore[union-attr]

    def test_ignores_already_completed_step(self) -> None:
        state = _OperationProgress(
            current_datasource=_DatasourceProgress(
                datasource_id="ds",
                completed_steps={ProgressStep.PLUGIN_EXECUTION},
            )
        )
        _apply_event(state, _event(ProgressKind.DATASOURCE_STEP_COMPLETED, step=ProgressStep.PLUGIN_EXECUTION))
        assert len(state.current_datasource.completed_steps) == 1  # type: ignore[union-attr]

    def test_clears_current_step_progress_when_step_matches(self) -> None:
        state = _OperationProgress(
            current_datasource=_DatasourceProgress(
                datasource_id="ds",
                current_step_progress=_StepProgress(step=ProgressStep.PLUGIN_EXECUTION, units_completed=3, units_total=5),
            )
        )
        _apply_event(state, _event(ProgressKind.DATASOURCE_STEP_COMPLETED, step=ProgressStep.PLUGIN_EXECUTION))
        assert state.current_datasource.current_step_progress is None  # type: ignore[union-attr]
        assert ProgressStep.PLUGIN_EXECUTION in state.current_datasource.completed_steps  # type: ignore[union-attr]

    def test_preserves_current_step_progress_when_step_differs(self) -> None:
        step_progress = _StepProgress(step=ProgressStep.CONTEXT_ENRICHMENT, units_completed=3, units_total=5)
        state = _OperationProgress(
            current_datasource=_DatasourceProgress(
                datasource_id="ds",
                current_step_progress=step_progress,
            )
        )
        _apply_event(state, _event(ProgressKind.DATASOURCE_STEP_COMPLETED, step=ProgressStep.PLUGIN_EXECUTION))
        assert state.current_datasource.current_step_progress is step_progress  # type: ignore[union-attr]
        assert ProgressStep.PLUGIN_EXECUTION in state.current_datasource.completed_steps  # type: ignore[union-attr]


class TestApplyEventDatasourceStepProgress:
    def test_sets_current_step_progress(self) -> None:
        state = _OperationProgress(current_datasource=_DatasourceProgress(datasource_id="ds"))
        _apply_event(
            state,
            _event(
                ProgressKind.DATASOURCE_STEP_PROGRESS,
                step=ProgressStep.PLUGIN_EXECUTION,
                current_units_completed=3,
                current_units_total=10,
            ),
        )
        assert state.current_datasource is not None
        p = state.current_datasource.current_step_progress
        assert p is not None
        assert p.step == ProgressStep.PLUGIN_EXECUTION
        assert p.units_completed == 3
        assert p.units_total == 10

    def test_ignores_step_already_completed(self) -> None:
        state = _OperationProgress(
            current_datasource=_DatasourceProgress(
                datasource_id="ds",
                completed_steps={ProgressStep.PLUGIN_EXECUTION},
            )
        )
        _apply_event(
            state,
            _event(
                ProgressKind.DATASOURCE_STEP_PROGRESS,
                step=ProgressStep.PLUGIN_EXECUTION,
                current_units_completed=5,
                current_units_total=10,
            ),
        )
        assert state.current_datasource.current_step_progress is None  # type: ignore[union-attr]

    def test_does_not_decrease_units_completed(self) -> None:
        state = _OperationProgress(
            current_datasource=_DatasourceProgress(
                datasource_id="ds",
                current_step_progress=_StepProgress(step=ProgressStep.PLUGIN_EXECUTION, units_completed=7, units_total=10),
            )
        )
        _apply_event(
            state,
            _event(
                ProgressKind.DATASOURCE_STEP_PROGRESS,
                step=ProgressStep.PLUGIN_EXECUTION,
                current_units_completed=3,
                current_units_total=10,
            ),
        )
        assert state.current_datasource is not None
        assert state.current_datasource.current_step_progress is not None
        assert state.current_datasource.current_step_progress.units_completed == 7


class TestApplyEventDatasourceFinished:
    def test_marks_datasource_as_finished(self) -> None:
        state = _OperationProgress(current_datasource=_DatasourceProgress(datasource_id="ds"))
        _apply_event(state, _event(ProgressKind.DATASOURCE_FINISHED))
        assert state.current_datasource is not None
        assert state.current_datasource.finished is True

    def test_appends_datasource_id_to_completed(self) -> None:
        state = _OperationProgress(current_datasource=_DatasourceProgress(datasource_id="ds"))
        _apply_event(state, _event(ProgressKind.DATASOURCE_FINISHED))
        assert "ds" in state.completed_datasource_ids

    def test_accumulates_multiple_completed_datasources(self) -> None:
        state = _OperationProgress()
        for ds_id in ("ds1", "ds2", "ds3"):
            _apply_event(state, _event(ProgressKind.DATASOURCE_STARTED, datasource_id=ds_id))
            _apply_event(state, _event(ProgressKind.DATASOURCE_FINISHED))
        assert state.completed_datasource_ids == ["ds1", "ds2", "ds3"]


# ---------------------------------------------------------------------------
# cli_progress context manager
# ---------------------------------------------------------------------------


def test_cli_progress_noop_when_not_terminal() -> None:
    with patch("sys.stderr.isatty", return_value=False), cli_progress() as cb:
        cb(_event(ProgressKind.OPERATION_STARTED, operation_total=1))
