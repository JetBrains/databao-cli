from pathlib import Path


def get_root() -> Path:
    return Path(__file__).parent.parent.parent


ARTIFACT_DIR = get_root() / "artifacts"
TEST_RESOURCES_DIR = get_root() / "tests" / "resources"


def get_all_results(project_path: Path):
    return project_path.joinpath("databao", "domains", "root", "output", "all_results.yaml")


def get_src_folder(project_path: Path):
    return Path(project_path.joinpath("databao", "domains", "root", "src"))
