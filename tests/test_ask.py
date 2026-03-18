from dataclasses import dataclass, field
from pathlib import Path
from typing import Any
from unittest.mock import MagicMock, patch

import pytest
from click.testing import CliRunner

from databao_cli.__main__ import cli
from databao_cli.commands.ask import initialize_agent_from_dce


def test_ask_help() -> None:
    """Test that the ask command shows help."""
    runner = CliRunner()
    result = runner.invoke(cli, ["ask", "--help"])

    assert result.exit_code == 0
    assert "Chat with the Databao agent" in result.output


@dataclass
class _FakeSources:
    dbs: dict[str, Any] = field(default_factory=dict)
    dfs: dict[str, Any] = field(default_factory=dict)
    dbts: dict[str, Any] = field(default_factory=dict)
    additional_description: list[str] = field(default_factory=list)


def _make_mock_agent(num_dbs: int = 0, num_dfs: int = 0, num_dbts: int = 0) -> MagicMock:
    """Create a mock agent with the given number of sources."""
    agent = MagicMock()
    agent.sources = _FakeSources(
        dbs={f"db{i}": MagicMock() for i in range(num_dbs)},
        dfs={f"df{i}": MagicMock() for i in range(num_dfs)},
        dbts={f"dbt{i}": MagicMock() for i in range(num_dbts)},
    )
    return agent


@patch("databao_cli.commands.ask.create_agent")
@patch("databao_cli.commands.ask.create_domain")
@patch("databao_cli.commands.ask.databao_project_status")
@patch("databao_cli.commands.ask.ProjectLayout")
def test_initialize_agent_counts_dbt_sources(
    mock_layout: MagicMock,
    mock_status: MagicMock,
    mock_create_domain: MagicMock,
    mock_create_agent: MagicMock,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Test that dbt sources are included in the connected sources count."""
    from databao_cli.ui.project_utils import DatabaoProjectStatus

    mock_status.return_value = DatabaoProjectStatus.VALID
    mock_create_agent.return_value = _make_mock_agent(num_dbs=0, num_dfs=0, num_dbts=1)

    agent = initialize_agent_from_dce(Path("/fake"), model=None, temperature=0.0)

    assert agent.sources.dbts
    captured = capsys.readouterr()
    assert "Connected to 1 data source(s)" in captured.out


@patch("databao_cli.commands.ask.create_agent")
@patch("databao_cli.commands.ask.create_domain")
@patch("databao_cli.commands.ask.databao_project_status")
@patch("databao_cli.commands.ask.ProjectLayout")
def test_initialize_agent_counts_all_source_types(
    mock_layout: MagicMock,
    mock_status: MagicMock,
    mock_create_domain: MagicMock,
    mock_create_agent: MagicMock,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Test that all source types (dbs, dfs, dbts) are summed correctly."""
    from databao_cli.ui.project_utils import DatabaoProjectStatus

    mock_status.return_value = DatabaoProjectStatus.VALID
    mock_create_agent.return_value = _make_mock_agent(num_dbs=2, num_dfs=1, num_dbts=3)

    initialize_agent_from_dce(Path("/fake"), model=None, temperature=0.0)

    captured = capsys.readouterr()
    assert "Connected to 6 data source(s)" in captured.out
