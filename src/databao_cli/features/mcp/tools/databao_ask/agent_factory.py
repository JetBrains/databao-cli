"""Agent creation logic for the databao_ask tool."""

from databao.agent import Agent
from databao.agent import domain as create_domain
from databao.agent.api import agent as create_agent
from databao.agent.configs.llm import LLMConfig, LLMConfigDirectory
from databao.agent.core import Cache

from databao_cli.features.ui.project_utils import DatabaoProjectStatus, databao_project_status, has_build_output
from databao_cli.shared.executor_utils import DEFAULT_EXECUTOR
from databao_cli.shared.project.layout import ProjectLayout


def create_agent_for_tool(
    project: ProjectLayout,
    model: str | None = None,
    temperature: float = 0.0,
    executor: str = DEFAULT_EXECUTOR,
    cache: Cache | None = None,
) -> Agent:
    """Create a Databao agent from a DCE project, configured for MCP tool use.

    Raises ValueError if the project is not ready (no datasources, no build).
    """
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
        from databao_cli.shared.executor_utils import build_llm_config

        llm_config = build_llm_config(model, temperature=temperature)
    elif temperature != 0.0:
        llm_config = LLMConfig(name=LLMConfigDirectory.DEFAULT.name, temperature=temperature)
    else:
        llm_config = LLMConfigDirectory.DEFAULT

    kwargs: dict[str, object] = {
        "domain": domain,
        "llm_config": llm_config,
        "cache": cache,
    }

    if executor == "claude_code":
        from databao.agent.executors import ClaudeCodeExecutor

        kwargs["data_executor"] = ClaudeCodeExecutor()
    else:
        kwargs["executor_type"] = executor

    return create_agent(**kwargs)  # type: ignore[arg-type]
