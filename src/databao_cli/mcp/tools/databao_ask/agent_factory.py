"""Agent creation logic for the databao_ask tool."""

from pathlib import Path

from databao.agent import Agent
from databao.agent import domain as create_domain
from databao.agent.api import agent as create_agent
from databao.agent.configs.llm import LLMConfig, LLMConfigDirectory
from databao.agent.core import Cache

from databao_cli.project.layout import ProjectLayout
from databao_cli.ui.project_utils import DatabaoProjectStatus, databao_project_status, has_build_output


def create_agent_for_tool(
    project_dir: Path,
    model: str | None = None,
    temperature: float = 0.0,
    executor: str = "lighthouse",
    cache: Cache | None = None,
) -> Agent:
    """Create a Databao agent from a DCE project, configured for MCP tool use.

    Raises ValueError if the project is not ready (no datasources, no build).
    """
    project = ProjectLayout(project_dir)

    status = databao_project_status(project)
    if status == DatabaoProjectStatus.NOT_INITIALIZED:
        raise ValueError("Databao project is not initialized. Run 'databao init' first.")
    if status == DatabaoProjectStatus.NO_DATASOURCES:
        raise ValueError("No datasources configured. Run 'databao datasource add' first.")
    if not has_build_output(project):
        raise ValueError("Project has no build output. Run 'databao build' first.")

    domain = create_domain(project.root_domain_dir)

    llm_config: LLMConfig
    if model:
        llm_config = LLMConfig(name=model, temperature=temperature)
    elif temperature != 0.0:
        llm_config = LLMConfig(name=LLMConfigDirectory.DEFAULT.name, temperature=temperature)
    else:
        llm_config = LLMConfigDirectory.DEFAULT

    return create_agent(
        domain=domain,
        llm_config=llm_config,
        executor_type=executor,
        cache=cache,
    )
