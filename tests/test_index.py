import duckdb
from _pytest.tmpdir import TempPathFactory
from databao_context_engine import DatabaoContextDomainManager, DatasourceType

from databao_cli.shared.project.layout import ProjectLayout
from tests.utils.project import describe_result, run_build, run_index


def test_databao_index_duckdb_datasource(project_layout: ProjectLayout, tmp_path_factory: TempPathFactory) -> None:
    test_db = tmp_path_factory.mktemp("duckdb") / "test_db.duckdb"
    conn = duckdb.connect(str(test_db))
    conn.execute("CREATE TABLE t1 AS SELECT 1 AS i, 2 AS j;")
    conn.close()

    dce_domain_manager = DatabaoContextDomainManager(domain_dir=project_layout.root_domain_dir)
    dce_domain_manager.create_datasource_config(
        datasource_type=DatasourceType(full_type="duckdb"),
        datasource_name="my_test",
        config_content={"connection": {"database_path": str(test_db)}},
    )
    with run_build(project_layout.project_dir, args=["build", "--should-not-index"]) as build_result:
        assert build_result.exit_code == 0, describe_result(build_result)
        assert "Build complete. Processed 1 datasources." in build_result.output, build_result.output

    with run_index(project_layout.project_dir) as result:
        assert result.exit_code == 0, describe_result(result)
        assert "Index complete. Processed 1 contexts." in result.output, result.output
