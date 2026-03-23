import duckdb
from _pytest.tmpdir import TempPathFactory
from databao_context_engine import DatabaoContextDomainManager, DatasourceType

from databao_cli.shared.project.layout import ProjectLayout
from tests.utils.project import describe_result, run_build


def test_databao_build_duckdb_datasource(project_layout: ProjectLayout, tmp_path_factory: TempPathFactory) -> None:
    test_db = tmp_path_factory.mktemp("duckdb") / "test_db.duckdb"
    duckdb.connect(str(test_db))
    duckdb.execute("CREATE TABLE t1 AS SELECT 1 AS i, 2 AS j;")

    dce_domain_manager = DatabaoContextDomainManager(domain_dir=project_layout.root_domain_dir)
    dce_domain_manager.create_datasource_config(
        datasource_type=DatasourceType(full_type="duckdb"),
        datasource_name="my_test",
        config_content={"connection": {"database_path": str(test_db)}},
    )
    with run_build(project_layout.project_dir) as result:
        assert result.exit_code == 0, describe_result(result)
        assert "Build complete. Processed 1 datasources." in result.output, result.output
