import os
import sys
from importlib.metadata import version
from pathlib import Path

import click
from databao_context_engine import (
    DceDomainInfo,
    DceInfo,
    get_databao_context_engine_domain_info,
    get_databao_context_engine_info,
)

from databao_cli.project.layout import find_project


@click.command()
@click.pass_context
def status(ctx: click.Context) -> None:
    """Display project status and system-wide information."""
    click.echo(status_impl(ctx.obj["project_dir"]))


def status_impl(project_dir: Path) -> str:
    project_layout = find_project(project_dir)

    dce_info = get_databao_context_engine_info()

    return _generate_info_string(
        dce_info,
        [get_databao_context_engine_domain_info(domain) for domain in project_layout.get_domain_dirs()]
        if project_layout
        else [],
    )


def _generate_info_string(command_info: DceInfo, domain_infos: list[DceDomainInfo]) -> str:
    info_lines = [
        f"Databao context engine version: {command_info.version}",
        f"Databao agent version: {version('databao-agent')}",
        f"Databao context engine storage dir: {command_info.dce_path}",
        f"Databao context engine plugins: {command_info.plugin_ids}",
        "",
        f"OS name: {sys.platform}",
        f"OS architecture: {os.uname().machine if hasattr(os, 'uname') else 'unknown'}",
        "",
    ]

    for domain_info in domain_infos:
        if domain_info.is_initialized:
            info_lines.append(f"Databao Domain dir: {domain_info.project_path.resolve()}")
            info_lines.append(f"Databao Domain ID: {domain_info.project_id!s}")

    return os.linesep.join(info_lines)
