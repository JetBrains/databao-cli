from unittest.mock import MagicMock, patch

from click.testing import CliRunner

from databao_cli.__main__ import cli


def test_ask_help() -> None:
    """Test that the ask command shows help."""
    runner = CliRunner()
    result = runner.invoke(cli, ["ask", "--help"])

    assert result.exit_code == 0
    assert "Chat with the Databao agent" in result.output


def _make_mock_agent(num_dbs: int = 0, num_dfs: int = 0, num_dbts: int = 0) -> MagicMock:
    """Create a mock agent with the given number of sources."""
    agent = MagicMock()
    agent.sources.dbs = {f"db{i}": MagicMock() for i in range(num_dbs)}
    agent.sources.dfs = {f"df{i}": MagicMock() for i in range(num_dfs)}
    agent.sources.dbts = {f"dbt{i}": MagicMock() for i in range(num_dbts)}
    return agent


class TestSourceCounting:
    """Tests that dbt sources are included in the source count (DBA-126)."""

    @patch("databao_cli.commands.ask.create_agent")
    @patch("databao_cli.commands.ask.create_domain")
    @patch("databao_cli.commands.ask.databao_project_status")
    def test_dbt_only_sources_counted(
        self,
        mock_status: MagicMock,
        mock_domain: MagicMock,
        mock_create_agent: MagicMock,
    ) -> None:
        """When only dbt sources exist, count should be > 0."""
        from databao_cli.commands.ask import initialize_agent_from_dce
        from databao_cli.ui.project_utils import DatabaoProjectStatus

        mock_status.return_value = DatabaoProjectStatus.VALID
        mock_create_agent.return_value = _make_mock_agent(num_dbts=1)

        agent = initialize_agent_from_dce(project_path=MagicMock(), model=None, temperature=0.0)
        assert len(agent.sources.dbs) + len(agent.sources.dfs) + len(agent.sources.dbts) == 1

    @patch("databao_cli.commands.ask.create_agent")
    @patch("databao_cli.commands.ask.create_domain")
    @patch("databao_cli.commands.ask.databao_project_status")
    def test_mixed_sources_counted(
        self,
        mock_status: MagicMock,
        mock_domain: MagicMock,
        mock_create_agent: MagicMock,
    ) -> None:
        """All source types should be summed in the count."""
        from databao_cli.commands.ask import initialize_agent_from_dce
        from databao_cli.ui.project_utils import DatabaoProjectStatus

        mock_status.return_value = DatabaoProjectStatus.VALID
        mock_create_agent.return_value = _make_mock_agent(num_dbs=2, num_dfs=1, num_dbts=1)

        agent = initialize_agent_from_dce(project_path=MagicMock(), model=None, temperature=0.0)
        assert len(agent.sources.dbs) + len(agent.sources.dfs) + len(agent.sources.dbts) == 4
