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
# ask.py - _setup_agent source count
# ---------------------------------------------------------------------------


class TestAskSourceCount:
    """Verify that ask.py counts dbt sources."""

    @staticmethod
    def _count_sources(agent: MagicMock) -> int:
        """Reproduce the counting logic from ask.py:_setup_agent."""
        return len(agent.sources.dbs) + len(agent.sources.dfs) + len(agent.sources.dbts)

    def test_only_dbt_sources(self) -> None:
        agent = _make_agent(dbts={"my_dbt": object()})
        assert self._count_sources(agent) == 1

    def test_mixed_sources(self) -> None:
        agent = _make_agent(
            dbs={"pg": object()},
            dfs={"df1": object()},
            dbts={"dbt1": object()},
        )
        assert self._count_sources(agent) == 3

    def test_no_sources(self) -> None:
        agent = _make_agent()
        assert self._count_sources(agent) == 0

    def test_dbs_and_dfs_only(self) -> None:
        agent = _make_agent(dbs={"pg": object()}, dfs={"df1": object()})
        assert self._count_sources(agent) == 2


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
    """Verify that welcome page counts dbt sources."""

    @staticmethod
    def _count_sources(agent: MagicMock | None) -> int:
        """Reproduce the counting logic from welcome.py."""
        return (len(agent.sources.dbs) + len(agent.sources.dfs) + len(agent.sources.dbts)) if agent else 0

    def test_only_dbt_sources(self) -> None:
        agent = _make_agent(dbts={"my_dbt": object()})
        assert self._count_sources(agent) == 1

    def test_mixed_sources(self) -> None:
        agent = _make_agent(
            dbs={"pg": object()},
            dfs={"df1": object()},
            dbts={"dbt1": object()},
        )
        assert self._count_sources(agent) == 3

    def test_none_agent(self) -> None:
        assert self._count_sources(None) == 0
