from pathlib import Path

import pexpect
from pexpect.popen_spawn import PopenSpawn

from database_utils import DatabaseBase


def execute_init(project_dir: Path, db: DatabaseBase | None = None):
    with open(project_dir / "cli.log", "w") as logfile:
        # child = PopenSpawn(
        child = pexpect.spawn("databao init", cwd=project_dir, encoding="utf-8", timeout=5, logfile=logfile)

        child.expect(r"Do you want to configure a domain now\? \[y/N\]:")
        if db:
            child.sendline("Y")
            db.run_interactive_flow(child)
            child.expect(r"Do you want to add more datasources\? \[y/N\]:")
            child.sendline("N")
            child.expect(pexpect.EOF)
        else:
            child.sendline("N")
            child.expect(pexpect.EOF)


def execute_build(project_dir: Path):
    with open(project_dir / "cli.log", "w") as logfile:
        child = PopenSpawn("databao build", cwd=project_dir, encoding="utf-8", timeout=30)
        child.logfile = logfile
        child.expect(pexpect.EOF)
