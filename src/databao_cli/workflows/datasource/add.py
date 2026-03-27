"""Interactive CLI workflow for adding a datasource."""

import os

import click
from databao_context_engine import (
    DatabaoContextDomainManager,
    DatabaoContextPluginLoader,
    DatasourceType,
)

from databao_cli.shared.context_engine_cli import ClickUserInputCallback
from databao_cli.shared.project.layout import ProjectLayout
from databao_cli.workflows.datasource.check import print_connection_check_results


def add_workflow(project_layout: ProjectLayout, domain: str) -> None:
    """Interactive wizard: collect inputs, create config, optionally check connection."""
    from databao_cli.features.datasource.add import create_datasource_config, datasource_config_exists

    domain_dir = project_layout.domains_dir / domain
    plugin_loader = DatabaoContextPluginLoader()

    click.echo(f"We will guide you to add a new datasource into {domain} domain, at {domain_dir.resolve()}")

    datasource_type = _ask_for_datasource_type(plugin_loader.get_all_supported_datasource_types(exclude_file_plugins=True))
    datasource_name = click.prompt("Datasource name?", type=str)

    overwrite_existing = False
    existing_id = datasource_config_exists(project_layout, domain, datasource_name)
    if existing_id is not None:
        click.confirm(
            f"A config file already exists for this datasource {existing_id.relative_path_to_config_file()}. "
            f"Do you want to overwrite it?",
            abort=True,
            default=False,
        )
        overwrite_existing = True

    datasource_id, config_path = create_datasource_config(
        project_layout,
        domain,
        datasource_type,
        datasource_name,
        ClickUserInputCallback(),
        overwrite_existing=overwrite_existing,
    )

    click.echo(f"{os.linesep}We've created a new config file for your datasource at: {config_path}")

    if click.confirm("\nDo you want to check the connection to this new datasource?"):
        domain_manager = DatabaoContextDomainManager(domain_dir=domain_dir)
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
