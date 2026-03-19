from pathlib import Path
from unittest.mock import MagicMock, patch

import click
from click.testing import CliRunner
from databao.agent.core.data_source import Sources

from databao_cli.__main__ import cli
from databao_cli.commands.ask import initialize_agent_from_dce
from databao_cli.ui.project_utils import DatabaoProjectStatus


def test_ask_help() -> None:
    """Test that the ask command shows help."""
    runner = CliRunner()
    result = runner.invoke(cli, ["ask", "--help"])

    assert result.exit_code == 0
    assert "Chat with the Databao agent" in result.output


@patch("databao_cli.commands.ask.create_agent")
@patch("databao_cli.commands.ask.create_domain")
@patch("databao_cli.commands.ask.databao_project_status")
@patch("databao_cli.commands.ask.ProjectLayout")
def test_source_count_includes_dbt(
    mock_layout: MagicMock,
    mock_status: MagicMock,
    mock_create_domain: MagicMock,
    mock_create_agent: MagicMock,
) -> None:
    """Test that dbt sources are included in the connected source count."""
    mock_status.return_value = DatabaoProjectStatus.VALID
    mock_layout.return_value.project_dir = Path("/fake")
    mock_layout.return_value.root_domain_dir = Path("/fake/domain")

    mock_agent = MagicMock()
    mock_agent.sources = Sources(
        dbs={},
        dfs={},
        dbts={"my_dbt": MagicMock()},
        additional_description=[],
    )
    mock_create_agent.return_value = mock_agent

    runner = CliRunner()
    with runner.isolated_filesystem():
        result = runner.invoke(
            click.command()(lambda: initialize_agent_from_dce(Path("."), None, 0.0)),
            [],
            catch_exceptions=False,
        )

    assert "Connected to 1 data source(s)" in result.output


@patch("databao_cli.commands.ask.create_agent")
@patch("databao_cli.commands.ask.create_domain")
@patch("databao_cli.commands.ask.databao_project_status")
@patch("databao_cli.commands.ask.ProjectLayout")
def test_source_count_includes_all_types(
    mock_layout: MagicMock,
    mock_status: MagicMock,
    mock_create_domain: MagicMock,
    mock_create_agent: MagicMock,
) -> None:
    """Test that all source types (dbs, dfs, dbts) are counted."""
    mock_status.return_value = DatabaoProjectStatus.VALID
    mock_layout.return_value.project_dir = Path("/fake")
    mock_layout.return_value.root_domain_dir = Path("/fake/domain")

    mock_agent = MagicMock()
    mock_agent.sources = Sources(
        dbs={"db1": MagicMock()},
        dfs={"df1": MagicMock()},
        dbts={"dbt1": MagicMock()},
        additional_description=[],
    )
    mock_create_agent.return_value = mock_agent

    runner = CliRunner()
    with runner.isolated_filesystem():
        result = runner.invoke(
            click.command()(lambda: initialize_agent_from_dce(Path("."), None, 0.0)),
            [],
            catch_exceptions=False,
        )

    assert "Connected to 3 data source(s)" in result.output
