from typing import TYPE_CHECKING

from databao_context_engine import DatabaoContextEngine, DatabaseSchemaLite, DatabaseTableDetails, DatasourceId
from mcp.types import ToolAnnotations
from pydantic import BaseModel, TypeAdapter

if TYPE_CHECKING:
    from fastmcp import FastMCP

    from databao_cli.features.mcp.server import McpContext


class DatasourceResult(BaseModel):
    id: str
    name: str
    type: str


class ListDatasourceResult(BaseModel):
    datasources: list[DatasourceResult]


class ListDatabaseSchemaResult(BaseModel):
    schemas: list[DatabaseSchemaLite]


def register(mcp: "FastMCP", context: "McpContext") -> None:
    """Register the database context tools with the MCP server."""

    @mcp.tool(
        annotations=ToolAnnotations(readOnlyHint=True, idempotentHint=True, openWorldHint=False),
    )
    def list_database_datasources() -> ListDatasourceResult:
        """List all configured datasources that support database metadata tools.

        Use this to narrow datasource selection before browsing schemas or inspecting table metadata.
        """
        context_engine = DatabaoContextEngine(domain_dir=context.project_layout.root_domain_dir)

        datasources = context_engine.list_database_datasources()

        return ListDatasourceResult(
            datasources=[
                DatasourceResult(
                    id=str(ds.id),
                    name=ds.id.name,
                    type=ds.type.full_type,
                )
                for ds in datasources
            ]
        )

    @mcp.tool(
        annotations=ToolAnnotations(readOnlyHint=True, idempotentHint=True, openWorldHint=False),
    )
    def list_database_schemas(datasource_id: str) -> ListDatabaseSchemaResult:
        """List all catalogs, schemas and tables for a database-capable datasource.

        The returned list will only contain the name and description of the schemas and tables.
        This allows to find tables related to your query and then query the full details
        using the "get_database_table_details" tool
        """
        context_engine = DatabaoContextEngine(domain_dir=context.project_layout.root_domain_dir)

        ds = DatasourceId.from_string_repr(datasource_id)
        return ListDatabaseSchemaResult(
            schemas=context_engine.list_database_schemas_and_tables(ds),
        )

    @mcp.tool(
        annotations=ToolAnnotations(readOnlyHint=True, idempotentHint=True, openWorldHint=False),
    )
    def get_database_table_details(datasource_id: str, catalog: str, schema: str, table: str) -> DatabaseTableDetails:
        """Get the full built metadata for one specific table in a database-capable datasource.

        Requires an exact datasource_id, catalog, schema, and table name.

        Use this when you already know which table you want and need detailed schema information
        such as columns, types, keys, indexes, samples, or profiling data to help write or validate SQL.
        """
        context_engine = DatabaoContextEngine(domain_dir=context.project_layout.root_domain_dir)

        ds = DatasourceId.from_string_repr(datasource_id)
        # We return a dumped python object so that we can exclude None values in the resulting JSON
        # Without this manual dump, FastMCP includes them by default and we can't configure it
        # The type hint of the function still declares DatabaseTableDetails because a JSON Schema is automatically
        # created from it by FastMCP
        # See https://github.com/PrefectHQ/fastmcp/issues/1090
        return TypeAdapter(DatabaseTableDetails).dump_python(  # type: ignore[no-any-return]
            context_engine.get_database_table_details(
                datasource_id=ds,
                catalog_name=catalog,
                schema_name=schema,
                table_name=table,
            ),
            exclude_none=True,
        )
