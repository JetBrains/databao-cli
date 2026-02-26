import os

import click
from databao_context_engine import (
    DatabaoContextPluginLoader,
    DatabaoContextProjectManager,
    DatasourceType,
)

from databao_cli.commands.context_engine_cli import ClickUserInputCallback
from databao_cli.commands.datasource.check_datasource_connection import print_connection_check_results
from databao_cli.project.layout import ProjectLayout


def add_datasource_config_interactive_impl(project_layout: ProjectLayout, domain: str) -> None:
    domain_dir = project_layout.domains_dir / domain
    domain_manager = DatabaoContextProjectManager(project_dir=domain_dir)
    plugin_loader = DatabaoContextPluginLoader()

    click.echo(f"We will guide you to add a new datasource into {domain} domain, at {domain_dir.resolve()}")

    datasource_type = _ask_for_datasource_type(plugin_loader.get_all_supported_datasource_types(exclude_file_plugins=True))

    datasource_name = click.prompt("Datasource name?", type=str)

    datasource_id = domain_manager.datasource_config_exists(datasource_name=datasource_name)
    if datasource_id is not None:
        click.confirm(
            f"A config file already exists for this datasource {datasource_id.relative_path_to_config_file()}. "
            f"Do you want to overwrite it?",
            abort=True,
            default=False,
        )
    created_datasource = domain_manager.create_datasource_config_interactively(
        datasource_type, datasource_name, ClickUserInputCallback(), overwrite_existing=True
    )

    datasource_id = created_datasource.datasource.id
    click.echo(
        f"{os.linesep}We've created a new config file for your datasource at: "
        f"{domain_manager.get_config_file_path_for_datasource(datasource_id)}"
    )
    if click.confirm("\nDo you want to check the connection to this new datasource?"):
        results = domain_manager.check_datasource_connection(datasource_ids=[datasource_id])
        print_connection_check_results(domain, results)


def _ask_for_datasource_type(supported_datasource_types: set[DatasourceType]) -> DatasourceType:
    all_datasource_types = sorted([ds_type.full_type for ds_type in supported_datasource_types])
    config_type = click.prompt(
        "What type of datasource do you want to add?",
        type=click.Choice(all_datasource_types),
        default=all_datasource_types[0] if len(all_datasource_types) == 1 else None,
    )
    click.echo(f"Selected type: {config_type}")

    return DatasourceType(full_type=config_type)
