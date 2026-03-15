from pathlib import Path


def get_root() -> Path:
    return Path(__file__).parent.parent.parent


ARTIFACT_DIR = get_root() / "artifacts"
TEST_RESOURCES_DIR = get_root() / "tests" / "resources"


def get_datasource_result(project_path: Path, datasource_name: str):
    return project_path.joinpath("databao", "domains", "root", "output", f"{datasource_name}.yaml")


def get_src_folder(project_path: Path):
    return Path(project_path.joinpath("databao", "domains", "root", "src"))
