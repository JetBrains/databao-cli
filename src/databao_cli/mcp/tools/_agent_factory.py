"""Shared agent creation logic for MCP tools."""

from pathlib import Path

from databao import Agent
from databao import domain as create_domain
from databao.api import agent as create_agent
from databao.configs.llm import LLMConfig, LLMConfigDirectory
from databao.core import Cache

from databao_cli.executor_utils import create_executor
from databao_cli.project.layout import ProjectLayout
from databao_cli.ui.project_utils import DCEProjectStatus, dce_status


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

    status = dce_status(project)
    if status == DCEProjectStatus.NO_DATASOURCES:
        raise ValueError(f"No datasources configured in project at {project.project_dir}. Run 'databao datasource add' first.")
    if status == DCEProjectStatus.NO_BUILD:
        raise ValueError(f"Project at {project.project_dir} has no build output. Run 'databao build' first.")

    domain = create_domain(project.root_domain_dir)

    llm_config: LLMConfig
    if model:
        llm_config = LLMConfig(name=model, temperature=temperature)
    elif temperature != 0.0:
        llm_config = LLMConfig(name=LLMConfigDirectory.DEFAULT.name, temperature=temperature)
    else:
        llm_config = LLMConfigDirectory.DEFAULT

    data_executor = create_executor(executor) if executor != "lighthouse" else None

    return create_agent(
        domain=domain,
        llm_config=llm_config,
        data_executor=data_executor,
        cache=cache,
    )
