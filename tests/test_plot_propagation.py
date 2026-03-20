"""Tests for DBA-94: plot propagation to previous messages.

Verifies that:
1. render_visualization_section refuses the shared thread fallback unless
   explicitly allowed via allow_thread_fallback=True.
2. The persistence round-trip correctly handles missing parquet files when
   _has_spec_df is True.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any
from unittest.mock import MagicMock, patch

import pandas as pd
import pytest


@pytest.fixture(autouse=True, scope="module")
def _preload_results_module() -> None:
    """Pre-import the results module to resolve the circular import chain.

    results → chat_persistence → __init__ → query_executor → results.
    Importing query_executor first breaks the cycle.
    """
    import databao_cli.ui.services.query_executor  # noqa: F401


def _get_render_fn() -> Any:
    """Import render_visualization_section lazily to avoid circular import at collection time."""
    from databao_cli.ui.components.results import render_visualization_section

    return render_visualization_section


# ---------------------------------------------------------------------------
# render_visualization_section tests
# ---------------------------------------------------------------------------


class TestRenderVisualizationSection:
    """Ensure the allow_thread_fallback guard works correctly."""

    def test_thread_fallback_blocked_by_default(self) -> None:
        """Without allow_thread_fallback the shared thread result is ignored."""
        render_visualization_section = _get_render_fn()
        with patch("databao_cli.ui.components.results.st") as mock_st:
            thread = MagicMock()
            thread._visualization_result = MagicMock()

            render_visualization_section(thread, visualization_data=None)

            mock_st.expander.assert_not_called()

    @patch("databao_cli.ui.components.results.st")
    def test_thread_fallback_allowed_renders(self, mock_st: MagicMock) -> None:
        """With allow_thread_fallback=True the shared thread result is used."""
        render_visualization_section = _get_render_fn()
        thread = MagicMock()
        vis = MagicMock()
        vis.plot = None
        thread._visualization_result = vis

        mock_expander = MagicMock()
        mock_st.expander.return_value.__enter__ = MagicMock(return_value=mock_expander)
        mock_st.expander.return_value.__exit__ = MagicMock(return_value=False)

        render_visualization_section(thread, visualization_data=None, allow_thread_fallback=True)

        mock_st.expander.assert_called_once()

    @patch("databao_cli.ui.components.results.st")
    def test_visualization_data_takes_priority(self, mock_st: MagicMock) -> None:
        """Per-message visualization_data is used even when thread has a result."""
        render_visualization_section = _get_render_fn()
        thread = MagicMock()
        thread._visualization_result = MagicMock()

        spec = {"mark": "bar"}
        spec_df = pd.DataFrame({"x": [1], "y": [2]})
        vis_data: dict[str, Any] = {"spec": spec, "spec_df": spec_df}

        mock_expander = MagicMock()
        mock_st.expander.return_value.__enter__ = MagicMock(return_value=mock_expander)
        mock_st.expander.return_value.__exit__ = MagicMock(return_value=False)

        render_visualization_section(thread, visualization_data=vis_data)

        mock_st.vega_lite_chart.assert_called_once()

    @patch("databao_cli.ui.components.results.st")
    def test_visualization_data_missing_spec_df_returns_early(self, mock_st: MagicMock) -> None:
        """If visualization_data has spec but no spec_df, returns without rendering."""
        render_visualization_section = _get_render_fn()
        thread = MagicMock()
        thread._visualization_result = MagicMock()

        vis_data: dict[str, Any] = {"spec": {"mark": "bar"}, "spec_df": None}

        render_visualization_section(thread, visualization_data=vis_data)

        mock_st.expander.assert_not_called()

    @patch("databao_cli.ui.components.results.st")
    def test_no_vis_result_no_data_returns_early(self, mock_st: MagicMock) -> None:
        """No visualization_data and no thread result -> nothing rendered."""
        render_visualization_section = _get_render_fn()
        thread = MagicMock()
        thread._visualization_result = None

        render_visualization_section(thread, visualization_data=None, allow_thread_fallback=True)

        mock_st.expander.assert_not_called()


# ---------------------------------------------------------------------------
# Persistence round-trip tests for _has_spec_df handling
# ---------------------------------------------------------------------------


class TestVisualizationPersistenceRoundTrip:
    """Test the _has_spec_df loading logic by calling the real load_chat function.

    We mock get_chats_dir to point at a tmp directory and build a minimal
    on-disk chat structure so load_chat exercises the actual persistence code.
    """

    @staticmethod
    def _write_chat(
        tmp_path: Path,
        chat_id: str,
        vis_data: dict[str, Any] | None,
        write_parquet: bool = False,
    ) -> None:
        """Write a minimal chat directory that load_chat can read."""
        import json

        chat_dir = tmp_path / chat_id
        chat_dir.mkdir(parents=True, exist_ok=True)

        session = {
            "id": chat_id,
            "created_at": "2026-01-01T00:00:00",
            "messages": [
                {
                    "role": "assistant",
                    "content": "test answer",
                    "has_visualization": True,
                    "visualization_data": vis_data,
                },
            ],
        }
        (chat_dir / "session.json").write_text(json.dumps(session))

        if write_parquet:
            vis_dir = chat_dir / "visualizations"
            vis_dir.mkdir(exist_ok=True)
            df = pd.DataFrame({"x": [1, 2], "y": [3, 4]})
            df.to_parquet(vis_dir / "0_spec_df.parquet")

    @patch("databao_cli.ui.services.chat_persistence.get_chats_dir")
    def test_has_spec_df_true_with_parquet(self, mock_chats_dir: MagicMock, tmp_path: Path) -> None:
        """When _has_spec_df=True and parquet exists, spec_df is loaded."""
        from databao_cli.ui.services.chat_persistence import load_chat

        mock_chats_dir.return_value = tmp_path
        chat_id = "00000000-0000-0000-0000-000000000001"
        self._write_chat(
            tmp_path,
            chat_id,
            vis_data={"spec": {"mark": "bar"}, "_has_spec_df": True},
            write_parquet=True,
        )

        chat = load_chat(chat_id)

        assert chat is not None
        msg = chat.messages[0]
        assert msg.visualization_data is not None
        assert msg.visualization_data["spec_df"] is not None
        assert len(msg.visualization_data["spec_df"]) == 2
        assert "_has_spec_df" not in msg.visualization_data

    @patch("databao_cli.ui.services.chat_persistence.get_chats_dir")
    def test_has_spec_df_true_without_parquet(self, mock_chats_dir: MagicMock, tmp_path: Path) -> None:
        """When _has_spec_df=True but parquet is missing, spec_df is explicitly None."""
        from databao_cli.ui.services.chat_persistence import load_chat

        mock_chats_dir.return_value = tmp_path
        chat_id = "00000000-0000-0000-0000-000000000002"
        self._write_chat(
            tmp_path,
            chat_id,
            vis_data={"spec": {"mark": "bar"}, "_has_spec_df": True},
            write_parquet=False,
        )

        chat = load_chat(chat_id)

        assert chat is not None
        msg = chat.messages[0]
        assert msg.visualization_data is not None
        # Key assertion: spec_df must be explicitly None, not absent
        assert "spec_df" in msg.visualization_data
        assert msg.visualization_data["spec_df"] is None
        assert "_has_spec_df" not in msg.visualization_data

    @patch("databao_cli.ui.services.chat_persistence.get_chats_dir")
    def test_legacy_chat_without_marker_still_loads_parquet(self, mock_chats_dir: MagicMock, tmp_path: Path) -> None:
        """Older chats without _has_spec_df still reload spec_df from parquet."""
        from databao_cli.ui.services.chat_persistence import load_chat

        mock_chats_dir.return_value = tmp_path
        chat_id = "00000000-0000-0000-0000-000000000003"
        self._write_chat(
            tmp_path,
            chat_id,
            vis_data={"spec": {"mark": "bar"}},
            write_parquet=True,
        )

        chat = load_chat(chat_id)

        assert chat is not None
        msg = chat.messages[0]
        assert msg.visualization_data is not None
        assert msg.visualization_data["spec_df"] is not None
        assert len(msg.visualization_data["spec_df"]) == 2

    @patch("databao_cli.ui.services.chat_persistence.get_chats_dir")
    def test_has_spec_df_marker_always_removed(self, mock_chats_dir: MagicMock, tmp_path: Path) -> None:
        """The _has_spec_df marker is always stripped from the loaded data."""
        from databao_cli.ui.services.chat_persistence import load_chat

        mock_chats_dir.return_value = tmp_path
        chat_id = "00000000-0000-0000-0000-000000000004"
        self._write_chat(
            tmp_path,
            chat_id,
            vis_data={"spec": {"mark": "bar"}, "_has_spec_df": False},
            write_parquet=False,
        )

        chat = load_chat(chat_id)

        assert chat is not None
        msg = chat.messages[0]
        assert msg.visualization_data is not None
        assert "_has_spec_df" not in msg.visualization_data
