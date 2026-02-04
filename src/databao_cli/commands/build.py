from pathlib import Path

from databao_context_engine import BuildContextResult, DatabaoContextProjectManager

from databao_cli.project.layout import find_project


def build_impl(project_dir: Path, domain: str) -> list[BuildContextResult]:
    project_layout = find_project(project_dir)
    dce_project_dir = project_layout.domains_dir / domain
    return DatabaoContextProjectManager(project_dir=dce_project_dir).build_context(datasource_ids=None)
