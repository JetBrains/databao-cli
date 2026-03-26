from pathlib import Path

from databao.agent import Agent
from databao.agent import domain as create_domain
from databao.agent.api import agent as create_agent
from databao.agent.configs.llm import LLMConfig, LLMConfigDirectory

from databao_cli.features.ui.project_utils import DatabaoProjectStatus, databao_project_status
from databao_cli.shared.errors import FeatureError
from databao_cli.shared.project.layout import ProjectLayout


def initialize_agent_from_dce(project_path: Path, model: str | None, temperature: float) -> Agent:
    """Initialize the Databao agent using DCE project at the given path."""
    project = ProjectLayout(project_path)

    status = databao_project_status(project)
    if status == DatabaoProjectStatus.NOT_INITIALIZED:
        raise FeatureError(f"No Databao project found at {project.project_dir}. Run 'databao init' first.")

    if status == DatabaoProjectStatus.NO_DATASOURCES:
        raise FeatureError(f"No datasources configured in project at {project.project_dir}. Add datasources first.")

    _domain = create_domain(project.root_domain_dir)

    if model:
        from databao_cli.shared.executor_utils import build_llm_config

        llm_config = build_llm_config(model, temperature=temperature)
    else:
        if temperature != 0.0:
            llm_config = LLMConfig(
                name=LLMConfigDirectory.DEFAULT.name,
                temperature=temperature,
            )
        else:
            llm_config = LLMConfigDirectory.DEFAULT

    agent = create_agent(domain=_domain, llm_config=llm_config)

    return agent
