from pathlib import Path

import yaml
from utils.path_utils import get_src_folder


def create_and_save_database_creds_file(project_path: Path, name: str, content: dict):
    get_src_folder(project_path).joinpath(name).write_text(yaml.safe_dump(content, sort_keys=False, indent=2))
