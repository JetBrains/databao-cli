from pathlib import Path

import yaml
from deepdiff import DeepDiff

from utils.path_utils import TEST_RESOURCES_DIR


def load_yaml(path: Path):
    with open(path) as f:
        return yaml.safe_load(f)


def remove_keys(data, keys):
    if isinstance(data, dict):
        return {k: remove_keys(v, keys) for k, v in data.items() if k not in keys}
    elif isinstance(data, list):
        return [remove_keys(i, keys) for i in data]
    return data


def compare_yaml(current_yaml: str, expected_yaml: str):
    diff = DeepDiff(current_yaml, expected_yaml)
    assert not diff, diff


def compare_yaml_by_path(path1: Path, path2: Path):
    keys_to_remove = ["context_built_at"]
    current_yaml = remove_keys(load_yaml(path1), keys_to_remove)
    expected_yaml = remove_keys(load_yaml(path2), keys_to_remove)
    compare_yaml(current_yaml, expected_yaml)


def assert_introspections_equal(path_to_file: Path, expected_file_name: str):
    compare_yaml_by_path(path_to_file, TEST_RESOURCES_DIR / expected_file_name)
