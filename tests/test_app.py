from unittest.mock import MagicMock, patch

from click.testing import CliRunner

from databao_cli.__main__ import cli


def test_app_help() -> None:
    """Test that the app command shows help."""
    runner = CliRunner()
    result = runner.invoke(cli, ["app", "--help"])

    assert result.exit_code == 0
    assert "Launch the Databao Streamlit web interface" in result.output


def test_app_hide_flags_forwarded() -> None:
    """Test that --hide-suggested-questions and --hide-build-context-hint are parsed and forwarded."""
    runner = CliRunner()
    mock_bootstrap = MagicMock()

    with patch("databao_cli.commands.app.bootstrap_streamlit_app", mock_bootstrap):
        result = runner.invoke(
            cli,
            ["app", "--hide-suggested-questions", "--hide-build-context-hint"],
        )

    assert result.exit_code == 0
    _, kwargs = mock_bootstrap.call_args
    assert kwargs["hide_suggested_questions"] is True
    assert kwargs["hide_build_context_hint"] is True


def test_app_hide_flags_default_false() -> None:
    """Test that hide flags default to False when not provided."""
    runner = CliRunner()
    mock_bootstrap = MagicMock()

    with patch("databao_cli.commands.app.bootstrap_streamlit_app", mock_bootstrap):
        result = runner.invoke(cli, ["app"])

    assert result.exit_code == 0
    _, kwargs = mock_bootstrap.call_args
    assert kwargs["hide_suggested_questions"] is False
    assert kwargs["hide_build_context_hint"] is False
