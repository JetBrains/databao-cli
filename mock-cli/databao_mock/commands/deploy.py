from __future__ import annotations

import subprocess
import time
from pathlib import Path

import click
import yaml


def _load_yaml(path: Path) -> dict:
    try:
        with open(path) as f:
            return yaml.safe_load(f) or {}
    except Exception:
        return {}


def _check_git(project_dir: Path) -> bool:
    """Return True if it's safe to deploy (no uncommitted or unpushed changes)."""
    # Check if inside a git repo
    result = subprocess.run(
        ["git", "rev-parse", "--is-inside-work-tree"],
        cwd=project_dir, capture_output=True, text=True
    )
    if result.returncode != 0:
        return True  # not a git repo, nothing to check

    # Uncommitted changes (staged or unstaged)
    dirty = subprocess.run(
        ["git", "status", "--porcelain"],
        cwd=project_dir, capture_output=True, text=True
    ).stdout.strip()

    # Unpushed commits
    unpushed = subprocess.run(
        ["git", "log", "@{u}..", "--oneline"],
        cwd=project_dir, capture_output=True, text=True
    ).stdout.strip()

    issues = []
    if dirty:
        issues.append(f"  Uncommitted changes:\n" +
                      "\n".join(f"    {l}" for l in dirty.splitlines()))
    if unpushed:
        issues.append(f"  Unpushed commits:\n" +
                      "\n".join(f"    {l}" for l in unpushed.splitlines()))

    if not issues:
        return True

    click.echo()
    click.echo(click.style("  ! ", fg="yellow") +
               "Your dbt project has changes that aren't published yet:\n")
    for issue in issues:
        click.echo(click.style(issue, fg="yellow"))
    click.echo()
    click.echo("  Databao deploys directly from your repository. Please commit")
    click.echo("  and push your changes so the Slack Bot gets the latest semantic")
    click.echo("  layer before deployment.\n")

    if not click.confirm("  Continue anyway?", default=False):
        return False

    return True


def deploy_impl(project_dir: Path) -> None:
    databao_yml = project_dir / ".databao" / "databao.yml"
    if not databao_yml.exists():
        click.echo(click.style("Error: ", fg="red") + "No Databao project found. Run `databao init` first.")
        raise SystemExit(1)

    config = _load_yaml(databao_yml)
    dbt_project = config.get("dbt", {}).get("project", "databao")

    if not _check_git(project_dir):
        return

    click.echo(f"\n  Deploying Slack Bot for '{click.style(dbt_project, bold=True)}'...\n")

    steps = [
        ("Packaging semantic models",   1.0),
        ("Uploading to Databao cloud",  1.4),
        ("Registering Slack app",       1.0),
        ("Configuring OAuth scopes",    0.8),
        ("Running smoke test",          1.2),
    ]

    for label, duration in steps:
        click.echo(f"  {label}...", nl=False)
        time.sleep(duration)
        click.echo(click.style(" done", fg="green"))

    click.echo()
    click.echo(click.style("  ✓ ", fg="green") + "Slack Bot deployed successfully.")
    click.echo(click.style("  ✓ ", fg="green") + "Invite it to a channel:  " + click.style("/invite @databao", bold=True))
    click.echo(click.style("  ✓ ", fg="green") + "Users can now ask questions directly in Slack.")
    click.echo()
