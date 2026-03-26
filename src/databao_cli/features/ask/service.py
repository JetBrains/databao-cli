from pathlib import Path

from databao.agent import Agent

from databao_cli.features.ask.agent_factory import initialize_agent_from_dce
from databao_cli.shared.errors import FeatureError


def ask_impl(
    project_path: Path,
    question: str | None,
    one_shot: bool,
    model: str | None,
    temperature: float,
) -> Agent:
    if one_shot and not question:
        raise FeatureError("Error: QUESTION argument is required in one-shot mode.")
    return initialize_agent_from_dce(project_path, model, temperature)
