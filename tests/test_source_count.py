"""Tests for dbt source counting in CLI and UI components (DBA-126)."""

from dataclasses import dataclass, field
from typing import Any
from unittest.mock import MagicMock, patch


@dataclass
class FakeSources:
    """Minimal Sources stand-in for testing."""

    dbs: dict[str, Any] = field(default_factory=dict)
    dfs: dict[str, Any] = field(default_factory=dict)
    dbts: dict[str, Any] = field(default_factory=dict)
    additional_description: list[str] = field(default_factory=list)


def _make_agent(
    dbs: dict[str, Any] | None = None,
    dfs: dict[str, Any] | None = None,
    dbts: dict[str, Any] | None = None,
) -> MagicMock:
    """Create a mock Agent with the given sources."""
    sources = FakeSources(
        dbs=dbs or {},
        dfs=dfs or {},
        dbts=dbts or {},
    )
    agent = MagicMock()
    agent.sources = sources
    agent.dbs = sources.dbs
    agent.dfs = sources.dfs
    return agent


# ---------------------------------------------------------------------------
# sidebar.py - render_sources_info
# ---------------------------------------------------------------------------


class TestSidebarSourceCount:
    """Verify that sidebar includes dbt sources."""

    @staticmethod
    def _mock_session_state(agent: MagicMock | None) -> MagicMock:
        state = MagicMock()
        state.get = lambda key, default=None: {"agent": agent}.get(key, default)
        return state

    def test_dbt_only_shows_sources(self) -> None:
        agent = _make_agent(dbts={"my_dbt": object()})
        with patch("databao_cli.features.ui.components.sidebar.st") as mock_st:
            mock_st.session_state = self._mock_session_state(agent)

            from databao_cli.features.ui.components.sidebar import render_sources_info

            render_sources_info()

            # Should NOT show "No sources configured"
            caption_calls = [str(c) for c in mock_st.caption.call_args_list]
            assert all("No sources" not in s for s in caption_calls)
            # Should render the dbt source
            markdown_calls = [str(c) for c in mock_st.markdown.call_args_list]
            assert any("my_dbt" in s for s in markdown_calls)

    def test_empty_sources_shows_no_configured(self) -> None:
        agent = _make_agent()
        with patch("databao_cli.features.ui.components.sidebar.st") as mock_st:
            mock_st.session_state = self._mock_session_state(agent)

            from databao_cli.features.ui.components.sidebar import render_sources_info

            render_sources_info()

            mock_st.caption.assert_called_with("No sources configured")


# ---------------------------------------------------------------------------
# context_settings.py - _render_sources
# ---------------------------------------------------------------------------


class TestContextSettingsSourceCount:
    """Verify that context_settings includes dbt sources."""

    def test_dbt_only_shows_sources(self) -> None:
        agent = _make_agent(dbts={"my_dbt": object()})
        with patch("databao_cli.features.ui.pages.context_settings.st") as mock_st:
            from databao_cli.features.ui.pages.context_settings import _render_sources

            _render_sources(agent)

            caption_calls = [str(c) for c in mock_st.caption.call_args_list]
            assert all("No data sources" not in s for s in caption_calls)
            markdown_calls = [str(c) for c in mock_st.markdown.call_args_list]
            assert any("my_dbt" in s for s in markdown_calls)

    def test_empty_sources_shows_no_configured(self) -> None:
        agent = _make_agent()
        with patch("databao_cli.features.ui.pages.context_settings.st") as mock_st:
            from databao_cli.features.ui.pages.context_settings import _render_sources

            _render_sources(agent)

            mock_st.caption.assert_called_with("No data sources configured in this project.")


# ---------------------------------------------------------------------------
# welcome.py - source count metric
# ---------------------------------------------------------------------------


class TestWelcomeSourceCount:
    """Verify that welcome page counts dbt sources via the real render function."""

    @staticmethod
    def _run_welcome(agent: MagicMock | None) -> MagicMock:
        """Patch streamlit and run the real welcome page renderer."""
        with patch("databao_cli.features.ui.pages.welcome.st") as mock_st:
            mock_st.session_state = {
                "chats": {},
                "agent": agent,
                "databao_project": None,
            }
            mock_st.columns.side_effect = lambda n: [MagicMock() for _ in range(n if isinstance(n, int) else len(n))]
            mock_st.button.return_value = False

            from databao_cli.features.ui.pages.welcome import render_welcome_page

            render_welcome_page()
            return mock_st

    def test_only_dbt_sources(self) -> None:
        agent = _make_agent(dbts={"my_dbt": object()})
        mock_st = self._run_welcome(agent)
        mock_st.metric.assert_any_call("Data Sources", 1)

    def test_mixed_sources(self) -> None:
        agent = _make_agent(
            dbs={"pg": object()},
            dfs={"df1": object()},
            dbts={"dbt1": object()},
        )
        mock_st = self._run_welcome(agent)
        mock_st.metric.assert_any_call("Data Sources", 3)

    def test_none_agent(self) -> None:
        mock_st = self._run_welcome(None)
        mock_st.metric.assert_any_call("Data Sources", 0)
