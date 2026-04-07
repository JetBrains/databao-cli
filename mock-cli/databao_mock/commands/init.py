"""
Mock implementation of `databao init`.

Flow:
  1. Scan project_dir (top-level + one level deep) for dbt_project.yml files.
  2. Found one   → auto-import that dbt project + connection from profiles.yml
  3. Found many  → let user pick one, then import
  4. Found none  → run `dbt init` to create and initialize a new dbt project
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import click
import questionary
import yaml
from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn, TimeElapsedColumn


# ---------------------------------------------------------------------------
# dbt project detection
# ---------------------------------------------------------------------------

def find_dbt_projects(root: Path) -> list[Path]:
    """Return paths to dbt_project.yml files found in root or one level deep."""
    hits: list[Path] = []
    # Check root itself
    if (root / "dbt_project.yml").exists():
        hits.append(root / "dbt_project.yml")
    # Check immediate subdirectories
    try:
        for child in sorted(root.iterdir()):
            if child.is_dir() and not child.name.startswith("."):
                candidate = child / "dbt_project.yml"
                if candidate.exists():
                    hits.append(candidate)
    except PermissionError:
        pass
    return hits


def _load_yaml(path: Path) -> dict:
    try:
        with open(path) as f:
            return yaml.safe_load(f) or {}
    except Exception:
        return {}


def _extract_connection_info(profiles_yml: Path, profile_name: str) -> dict | None:
    """Try to extract target connection info from profiles.yml."""
    data = _load_yaml(profiles_yml)
    profile = data.get(profile_name, {})
    outputs = profile.get("outputs", {})
    target_name = profile.get("target", next(iter(outputs), None))
    if target_name and target_name in outputs:
        return outputs[target_name]
    return None


def _describe_connection(conn: dict) -> str:
    parts = [f"type={conn.get('type', '?')}"]
    for key in ("host", "database", "schema", "project", "dataset", "path"):
        if key in conn:
            parts.append(f"{key}={conn[key]}")
    return ", ".join(parts)


# ---------------------------------------------------------------------------
# Import a discovered dbt project
# ---------------------------------------------------------------------------

def _discover_dbt_tables(dbt_dir: Path) -> list[str]:
    """Discover table names from existing dbt source YAMLs and model files."""
    tables: list[str] = []

    # Scan all yml files under models/ for source table definitions
    models_dir = dbt_dir / "models"
    if models_dir.exists():
        for yml_file in models_dir.rglob("*.yml"):
            data = _load_yaml(yml_file)
            for source in data.get("sources", []):
                for table in source.get("tables", []):
                    name = table.get("name") if isinstance(table, dict) else table
                    if name and name not in tables:
                        tables.append(name)

        # Fall back to model file names if no sources found
        if not tables:
            for sql_file in models_dir.rglob("*.sql"):
                tables.append(sql_file.stem)

    return tables

def _import_dbt_project(dbt_project_yml: Path) -> None:
    """Mock: show what would be imported from a dbt project."""
    dbt_dir = dbt_project_yml.parent
    project_data = _load_yaml(dbt_project_yml)
    project_name = project_data.get("name", dbt_dir.name)
    profile_name = project_data.get("profile", project_name)

    click.echo(f"\n  dbt project : {click.style(project_name, bold=True)}")
    click.echo(f"  location    : {dbt_dir.resolve()}")

    profiles_candidates = [
        dbt_dir / "profiles.yml",
        Path.home() / ".dbt" / "profiles.yml",
    ]
    conn_info: dict | None = None
    profiles_path: Path | None = None
    for p in profiles_candidates:
        if p.exists():
            conn_info = _extract_connection_info(p, profile_name)
            profiles_path = p
            if conn_info:
                break

    if conn_info:
        click.echo(f"  profile     : {profile_name} ({profiles_path})")
        click.echo(f"  connection  : {_describe_connection(conn_info)}")
    else:
        click.echo(f"  profile     : {profile_name} (connection details not found)")

    # Create databao/ folder and test_questions.csv
    databao_folder = dbt_dir.parent / "databao"
    databao_folder.mkdir(exist_ok=True)
    test_questions = databao_folder / "test_questions.csv"
    if not test_questions.exists():
        test_questions.write_text("question,gold_sql\n")

    config: dict = {
        "dbt": {"project": project_name, "path": str(dbt_dir.resolve())},
        "databao": {"path": str(databao_folder.resolve())},
    }
    if conn_info:
        config["connection"] = {k: v for k, v in conn_info.items() if not str(v).startswith("{{")}

    databao_yml = dbt_dir.parent / "databao.yml"
    existing = _load_yaml(databao_yml)
    if "user" in existing:
        config["user"] = existing["user"]
    with open(databao_yml, "w") as f:
        yaml.dump(config, f, default_flow_style=False, sort_keys=False)

    click.echo()
    click.echo(click.style("  ✓ ", fg="green") + f"dbt project '{project_name}' imported")
    if conn_info:
        click.echo(click.style("  ✓ ", fg="green") + f"{conn_info.get('type', 'unknown')} connection configured")
    click.echo(click.style("  ✓ ", fg="green") + f"databao/ folder created at {databao_folder}")
    click.echo(click.style("  ✓ ", fg="green") + f"databao.yml created at {databao_yml}")


# ---------------------------------------------------------------------------
# Fresh project setup (no dbt found)
# ---------------------------------------------------------------------------

def _find_dbt() -> str:
    """Return path to dbt executable — prefer the one in the current venv."""
    venv_dbt = Path(sys.executable).parent / "dbt"
    if venv_dbt.exists():
        return str(venv_dbt)
    return "dbt"

def _col(name: str, description: str, dtype: str, unique: int, nulls: float) -> dict:
    return {
        "name": name,
        "description": description,
        "meta": {
            "type": dtype,
            "unique_values": unique,
            "null_pct": nulls,
        },
    }

_MOCK_COLUMNS: dict[str, list[dict]] = {
    "orders": [
        _col("id",                 "Unique order ID",                          "integer",   48_203, 0.0),
        _col("customer_id",        "Reference to customer",                    "integer",   31_847, 1.2),
        _col("created_at",         "Order creation timestamp",                 "timestamp", 48_189, 0.0),
        _col("total_price",        "Total order value including tax",          "float",     12_430, 0.0),
        _col("subtotal_price",     "Order value before tax and shipping",      "float",     11_980, 0.0),
        _col("financial_status",   "Payment status (paid, refunded, pending)", "varchar",       5, 0.0),
        _col("fulfillment_status", "Fulfillment status",                       "varchar",       4, 3.1),
        _col("currency",           "Currency code",                            "varchar",      12, 0.0),
        _col("email",              "Customer email at time of order",          "varchar",   30_112, 2.4),
    ],
    "order_lines": [
        _col("id",         "Unique order line ID",           "integer",  142_804, 0.0),
        _col("order_id",   "Reference to order",             "integer",   48_203, 0.0),
        _col("product_id", "Reference to product",           "integer",    4_821, 0.8),
        _col("variant_id", "Reference to product variant",   "integer",   18_340, 0.8),
        _col("quantity",   "Number of units ordered",        "integer",       24, 0.0),
        _col("price",      "Unit price",                     "float",      3_204, 0.0),
        _col("title",      "Product title at time of order", "varchar",    4_950, 0.0),
        _col("sku",        "Stock keeping unit",             "varchar",   17_200, 5.3),
    ],
    "customers": [
        _col("id",                 "Unique customer ID",                   "integer",  31_847, 0.0),
        _col("email",              "Customer email address",               "varchar",  31_847, 0.0),
        _col("first_name",         "First name",                           "varchar",   8_430, 0.5),
        _col("last_name",          "Last name",                            "varchar",  14_210, 0.5),
        _col("created_at",         "Account creation timestamp",           "timestamp",31_840, 0.0),
        _col("orders_count",       "Total number of orders placed",        "integer",      87, 0.0),
        _col("total_spent",        "Lifetime spend",                       "float",    18_920, 0.0),
        _col("accepts_marketing",  "Whether customer opted into marketing", "boolean",       2, 0.0),
    ],
    "products": [
        _col("id",           "Unique product ID",                        "integer",  4_821, 0.0),
        _col("title",        "Product title",                            "varchar",  4_810, 0.0),
        _col("vendor",       "Product vendor",                           "varchar",    340, 1.0),
        _col("product_type", "Product category",                         "varchar",     82, 2.1),
        _col("created_at",   "Product creation timestamp",               "timestamp",4_821, 0.0),
        _col("status",       "Product status (active, archived, draft)", "varchar",      3, 0.0),
        _col("tags",         "Comma-separated product tags",             "varchar",  3_200, 8.4),
    ],
    "product_variants": [
        _col("id",                 "Unique variant ID",            "integer",  18_340, 0.0),
        _col("product_id",         "Reference to product",         "integer",   4_821, 0.0),
        _col("title",              "Variant title (e.g. S / Red)", "varchar",     420, 0.0),
        _col("price",              "Variant price",                "float",     3_204, 0.0),
        _col("sku",                "Stock keeping unit",           "varchar",  17_200, 5.3),
        _col("inventory_quantity", "Current stock level",          "integer",   2_840, 0.0),
        _col("weight",             "Variant weight",               "float",       312, 12.0),
    ],
    "refunds": [
        _col("id",         "Unique refund ID",               "integer",  3_841, 0.0),
        _col("order_id",   "Reference to order",             "integer",  3_790, 0.0),
        _col("created_at", "Refund creation timestamp",      "timestamp",3_841, 0.0),
        _col("note",       "Refund reason note",             "varchar",    820, 34.2),
        _col("restock",    "Whether inventory was restocked","boolean",      2, 0.0),
    ],
    "transactions": [
        _col("id",         "Unique transaction ID",                      "integer",  52_410, 0.0),
        _col("order_id",   "Reference to order",                         "integer",  48_203, 0.0),
        _col("amount",     "Transaction amount",                         "float",    11_840, 0.0),
        _col("currency",   "Currency code",                              "varchar",      12, 0.0),
        _col("kind",       "Transaction type (sale, refund, capture)",   "varchar",       5, 0.0),
        _col("status",     "Transaction status (success, failure, ...)", "varchar",       4, 0.0),
        _col("gateway",    "Payment gateway used",                       "varchar",      18, 0.5),
        _col("created_at", "Transaction timestamp",                      "timestamp",52_410, 0.0),
    ],
    "inventory_levels": [
        _col("inventory_item_id", "Reference to inventory item", "integer",  18_340, 0.0),
        _col("location_id",       "Reference to location",       "integer",      24, 0.0),
        _col("available",         "Available stock quantity",    "integer",   2_840, 0.0),
        _col("updated_at",        "Last update timestamp",       "timestamp",42_100, 0.0),
    ],
    "collections": [
        _col("id",           "Unique collection ID",                   "integer",    940, 0.0),
        _col("title",        "Collection title",                       "varchar",    938, 0.0),
        _col("handle",       "URL-safe collection handle",             "varchar",    940, 0.0),
        _col("published_at", "Publication timestamp",                  "timestamp",  921, 2.0),
        _col("sort_order",   "Default sort order for products",        "varchar",      6, 0.0),
    ],
    "discounts": [
        _col("id",          "Unique discount ID",                                       "integer",  1_204, 0.0),
        _col("code",        "Discount code string",                                     "varchar",  1_204, 0.0),
        _col("amount",      "Discount amount or percentage",                            "float",      340, 0.0),
        _col("type",        "Discount type (percentage, fixed_amount, free_shipping)",  "varchar",      3, 0.0),
        _col("starts_at",   "Discount start date",                                      "timestamp",1_204, 0.0),
        _col("ends_at",     "Discount end date",                                        "timestamp",  980, 18.5),
        _col("usage_count", "Number of times used",                                     "integer",    420, 0.0),
    ],
}

_MOCK_TABLES = [
    # orders
    "orders", "order_lines", "order_adjustments", "order_tags",
    "order_note_attributes", "order_shipping_lines", "order_shipping_tax_lines",
    "order_url_tags", "order_discount_codes",
    # customers
    "customers", "customer_tags", "customer_emails",
    # products
    "products", "product_variants", "product_images", "product_tags",
    # inventory
    "inventory_levels", "inventory_items", "locations",
    # payments
    "transactions", "refunds", "tender_transactions",
    # fulfillment
    "fulfillments", "fulfillment_events",
    # promotions
    "discounts", "discount_codes", "price_rules",
    # abandoned
    "abandoned_checkouts", "abandoned_checkout_discount_codes",
    "abandoned_checkout_shipping_lines",
    # catalog
    "collections", "collection_products",
    # misc
    "metafields", "shops", "tax_lines",
]

def _mock_connect_and_list(conn_type: str) -> list[str]:
    """Mock: connect and return list of available tables."""
    import time
    click.echo(f"\n  Connecting to {conn_type}...", nl=False)
    time.sleep(0.6)
    click.echo(click.style(" connected", fg="green"))
    click.echo(f"  Found {len(_MOCK_TABLES)} tables.\n")
    return _MOCK_TABLES


def _mock_introspect(selected: list[str]) -> None:
    """Mock: show progress bar while introspecting selected tables."""
    import time
    click.echo()
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TextColumn("[cyan]{task.completed}/{task.total}"),
        TimeElapsedColumn(),
    ) as progress:
        task = progress.add_task("  Introspecting", total=len(selected))
        for table in selected:
            progress.update(task, description=f"  {table:<35}")
            time.sleep(0.12)
            progress.advance(task)
    click.echo()


def _generate_sources(dbt_dir: Path, project_name: str, tables: list[str], new_project: bool = False) -> None:
    """Write models/staging/_sources.yml with column definitions for each selected table."""
    staging_dir = dbt_dir / "models" / "staging"
    staging_dir.mkdir(parents=True, exist_ok=True)

    table_entries = []
    for t in tables:
        entry: dict = {"name": t}
        if t in _MOCK_COLUMNS:
            entry["columns"] = _MOCK_COLUMNS[t]
        table_entries.append(entry)

    sources_yml = {
        "version": 2,
        "sources": [{
            "name": project_name,
            "database": "{{ env_var('DBT_DATABASE', 'shopify') }}",
            "schema": "{{ env_var('DBT_SCHEMA', 'main') }}",
            "tables": table_entries,
        }],
    }

    sources_path = staging_dir / "_sources.yml"
    with open(sources_path, "w") as f:
        yaml.dump(sources_yml, f, default_flow_style=False, sort_keys=False, allow_unicode=True)

    if new_project:
        click.echo(click.style("  ✓ ", fg="green") + f"Added {len(tables)} tables → {sources_path}")
    total_cols = sum(len(_MOCK_COLUMNS.get(t, [])) for t in tables)
    click.echo(click.style("  ✓ ", fg="green") + f"{total_cols} columns introspected across {len(tables)} tables")


def _introspect_existing_project(dbt_project_yml: Path) -> None:
    dbt_dir = dbt_project_yml.parent
    project_data = _load_yaml(dbt_project_yml)
    project_name = project_data.get("name", dbt_dir.name)
    tables = _discover_dbt_tables(dbt_dir) or _MOCK_TABLES
    click.echo(f"\n  Found {len(tables)} tables in the project.")
    _mock_introspect(tables)
    _generate_sources(dbt_dir, project_name, tables)


def _create_fresh_project(project_dir: Path) -> None:
    """No dbt project found — run `dbt init` to create one."""
    click.echo("No dbt project detected.")

    if not click.confirm("\nWould you like to create a new dbt project?", default=True):
        raise click.Abort()

    click.echo()
    dbt = _find_dbt()
    result = subprocess.run([dbt, "init"], cwd=project_dir, stdin=sys.stdin)
    if result.returncode != 0:
        click.echo(click.style("Error: ", fg="red") + "`dbt init` failed.", err=True)
        sys.exit(result.returncode)

    # Pick up the newly created project
    dbt_projects = find_dbt_projects(project_dir)
    if not dbt_projects:
        return
    dbt_project_yml = dbt_projects[0]
    _import_dbt_project(dbt_project_yml)

    # Fetch tables and let user pick
    project_data = _load_yaml(dbt_project_yml)
    project_name = project_data.get("name", dbt_project_yml.parent.name)
    profile_name = project_data.get("profile", project_name)
    conn_info = None
    for p in [dbt_project_yml.parent / "profiles.yml", Path.home() / ".dbt" / "profiles.yml"]:
        if p.exists():
            conn_info = _extract_connection_info(p, profile_name)
            if conn_info:
                break
    conn_type = conn_info.get("type", "database") if conn_info else "database"

    tables = _mock_connect_and_list(conn_type)

    selected = questionary.checkbox(
        "Which tables would you like to ingest? (type to search)",
        choices=tables,
        use_search_filter=True,
        use_jk_keys=False,
        instruction="(space to select, type to filter, enter to confirm)",
    ).ask()

    if not selected:
        click.echo(click.style("  ! ", fg="yellow") + "No tables selected, skipping source generation.")
        return

    _mock_introspect(selected)
    _generate_sources(dbt_project_yml.parent, project_name, selected, new_project=True)


# ---------------------------------------------------------------------------
# Main entry point
# ---------------------------------------------------------------------------

def init_impl(project_dir: Path) -> None:
    databao_yml = project_dir / "databao.yml"
    if databao_yml.exists() and bool((_load_yaml(databao_yml)).get("dbt")):
        click.echo(click.style("Error: ", fg="red") + f"Databao is already initialized in {project_dir.resolve()}")
        raise SystemExit(1)

    click.echo(f"\nInitializing Databao in {click.style(str(project_dir.resolve()), bold=True)}")
    click.echo("Scanning for dbt projects...\n")

    dbt_projects = find_dbt_projects(project_dir)

    if len(dbt_projects) == 0:
        _create_fresh_project(project_dir)

    elif len(dbt_projects) == 1:
        click.echo(click.style("  Found 1 dbt project:", fg="cyan"))
        proj_name = _load_yaml(dbt_projects[0]).get("name", dbt_projects[0].parent.name)
        click.echo(f"    {proj_name}  ({dbt_projects[0].parent})\n")
        if not click.confirm(f"Use '{proj_name}' as a base dbt project?", default=True):
            _create_fresh_project(project_dir)
            return
        _import_dbt_project(dbt_projects[0])
        _introspect_existing_project(dbt_projects[0])

    else:
        click.echo(click.style(f"  Found {len(dbt_projects)} dbt projects:", fg="cyan"))

        choices = {
            _load_yaml(p).get("name", p.parent.name): p
            for p in dbt_projects
        }
        selected_name = questionary.select(
            "Which dbt project do you want to import?",
            choices=list(choices.keys()),
        ).ask()

        if selected_name is None:
            _create_fresh_project(project_dir)
            return

        _import_dbt_project(choices[selected_name])
        _introspect_existing_project(choices[selected_name])

    click.echo("\n" + click.style("Project initialized successfully.", fg="green", bold=True))
