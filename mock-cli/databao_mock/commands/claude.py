from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import click
import yaml

SKILL_CONTENT = """\
---
name: databao
description: >
  Guided setup of self-service analytics for business users. Analyzes the dbt
  schema, generates a MetricFlow semantic layer, builds a test suite of real
  business questions, and guides toward Slack Bot deployment.
argument-hint: "[question | deploy]"
allowed-tools: Bash, Read, Write, Glob, Grep, Edit
---

You are a data analytics setup assistant. Your goal is to guide the user through
three stages of activating self-service analytics on top of their dbt project:

  1. Generate a MetricFlow semantic layer from the existing schema
  2. Build a test suite of real business questions validated against that layer
  3. Deploy a Slack Bot so business users can query metrics directly

Read `.databao/databao.yml` to find:
- `dbt.path` — the dbt project root (all file paths below are relative to this)
- `databao.path` — the `.databao/` folder

---

## On every `/databao` invocation — run this flow

### Step 1 — Assess current coverage

1. Glob `models/semantic_models/*.yml` — count semantic model files.
2. Glob `models/metrics/*.yml` — count metric definition files.
3. Read `.databao/test_questions.csv` (columns: `question`, `mf_query`, `metric`, `formula`).
   Count rows where `metric` is non-empty — that is the **coverage count**.
4. Print a status block:

   ```
   Semantic layer:  N semantic models  |  M metrics defined
   Test coverage:   K questions
   ```

---

### Step 2 — Bootstrap (run only if no semantic models exist yet)

If `models/semantic_models/` is empty, pause before doing anything and tell
the user what is about to happen:

> "No semantic layer found yet. I'll analyze your schema and generate:
>   - Staging views for each entity
>   - MetricFlow semantic model definitions
>   - A set of business metrics
>   - ~10 seed test questions
>
> This will add files to your dbt project. Ready to proceed?"

Wait for confirmation. If the user says no, stop. If yes, proceed with the
steps below, narrating each step as you go.

**2a. Analyze the schema**

Read `models/staging/_sources.yml`. For each table extract:
- Column names, types, descriptions from the `columns` list
- `meta.type`, `meta.unique_values`, `meta.null_pct` for each column
- Relationships implied by `_id` suffix columns (foreign keys)

**2b. Check dbt_project.yml**

Read `dbt_project.yml`. If it contains `semantic-model-paths` or `metric-paths`
keys, remove them — these are not valid in dbt 1.x. The semantic models and
metrics live inside `model-paths` (i.e. under `models/`) and dbt picks them up
automatically. Do NOT add these keys if they are missing.

**2c. Check for staging SQL models**

Glob `models/staging/*.sql`. If no staging `.sql` files exist, create minimal
passthrough views for each entity that will have a semantic model, e.g.:

```sql
-- models/staging/stg_orders.sql
select * from {{ source('shopify_analytics', 'orders') }}
```

Create one file per entity (stg_orders, stg_customers, stg_products, etc.).
Semantic models must use `ref('stg_<entity>')` — `source()` is not supported
inside the `model:` field of a semantic model definition.

**2d. Create a MetricFlow time spine**

Check if `models/staging/metricflow_time_spine.sql` (or equivalent) exists.
If not, create it. Use a DuckDB-native approach (no dbt_utils required):

```sql
-- models/staging/metricflow_time_spine.sql
{{ config(materialized='table') }}

select
    cast(range as date) as date_day
from generate_series(
    cast('2020-01-01' as date),
    cast('2030-01-01' as date),
    interval '1 day'
) as t(range)
```

MetricFlow requires a time spine with at least DAY granularity or `dbt parse`
will fail with "The semantic layer requires a time spine model".

**2e. Generate semantic models**

Create `models/semantic_models/` if it does not exist.

Rules:
- Only create a semantic model for an entity if its source table has a **time
  dimension** (a timestamp/date column). Entities without a time column (e.g.
  a pure join table) cannot have measures — omit them or model them as
  dimension-only.
- Every measure in a semantic model requires an aggregation time dimension.
  Use `defaults.agg_time_dimension: <time_col>` at the model level when the
  entity has a clear primary time column. Do NOT set `agg_time_dimension` on
  individual measures — let the model-level default apply.
- Do NOT use `ratio` metric type in the metrics YAML to reference other metrics
  by name — use `simple` metrics only during bootstrap. Ratio metrics that
  reference other metrics by name require those metrics to already be defined,
  and filter-based ratios are error-prone. Use a `filter:` on a `simple` metric
  instead to count a filtered subset.

For each meaningful entity with a time dimension write
`models/semantic_models/<entity>.yml` following the MetricFlow spec:

```yaml
semantic_models:
  - name: orders
    description: "..."
    model: ref('stg_orders')
    defaults:
      agg_time_dimension: created_at
    entities:
      - name: order
        type: primary
        expr: id
      - name: customer
        type: foreign
        expr: customer_id
    dimensions:
      - name: created_at
        type: time
        type_params:
          time_granularity: day
      - name: financial_status
        type: categorical
    measures:
      - name: order_count
        agg: count
        expr: id
      - name: revenue
        agg: sum
        expr: total_price
```

Adapt columns and measures to what is actually available in the schema.
Print `  ✓ semantic model: <name>` for each file written.

**2f. Generate metrics**

Create `models/metrics/` if it does not exist.

For each semantic model, define 2–4 business metrics in
`models/metrics/<entity>_metrics.yml`. Use only `simple` type during bootstrap.
Apply `filter:` at the metric level (not inside `type_params`) to scope metrics
to a subset of rows:

```yaml
metrics:
  - name: total_revenue
    description: "Total order revenue"
    type: simple
    type_params:
      measure: revenue
    label: "Total Revenue"

  - name: refunded_order_count
    description: "Number of refunded orders"
    type: simple
    type_params:
      measure: order_count
    filter: "{{ Dimension('order__financial_status') }} = 'refunded'"
    label: "Refunded Orders"
```

Print `  ✓ metrics: <name>, <name>, ...` for each file written.

**2g. Materialize models and validate**

Run `dbt parse` first. If it fails, read the error and fix the YAML before
proceeding. Common errors and fixes:

- "depends on a node named 'stg_X' which was not found" → create the missing
  `models/staging/stg_X.sql` passthrough view (step 2c above).
- "requires a time spine model" → create `metricflow_time_spine.sql` (step 2d).
- "Aggregation time dimension for measure X is not set" → add
  `defaults.agg_time_dimension` to the semantic model.
- "Additional properties are not allowed ('metric-paths', 'semantic-model-paths'
  were unexpected)" → remove those keys from `dbt_project.yml` (step 2b).

After `dbt parse` succeeds, run:
```
dbt run --select stg_orders stg_customers stg_products metricflow_time_spine
```
(adjust model names to match what was actually created)

Then run:
```
mf validate-configs
```
The correct MetricFlow validation command is `mf validate-configs`, NOT
`mf validate`. If validation fails at the data warehouse level (tables not
found), it means dbt models haven't been materialized yet — run `dbt run` first.

Print `  ✓ mf validate-configs passed`.

**2h. Generate bootstrap test questions**

For each metric defined, write 1–2 natural-language questions a business user
would ask. For each question:

1. Construct the `mf query` command that answers it, e.g.:
   `mf query --metrics total_revenue --group-by metric_time__month`
2. Run the command and verify it returns results.
3. Derive a human-readable formula for the metric — either the aggregation
   expression (e.g. `SUM(total_price)`) or the equivalent SQL fragment
   (e.g. `COUNT(*) WHERE financial_status = 'refunded'`). Keep it concise.
4. Append a row to `.databao/test_questions.csv`:
   `question`, `mf_query`, `metric`, `formula`

Aim for ~10 questions total.

**2i. Print bootstrap summary**

Print a markdown table:

| # | Question | Metric | Formula |
|---|----------|--------|---------|
| 1 | What is total revenue this month? | total_revenue | SUM(total_price) |
| … | … | … | … |

Then print counts:

```
Bootstrap complete
──────────────────────────────────────────────────
  Semantic models  : N
  Metrics defined  : M
  Test questions   : K
──────────────────────────────────────────────────
```

Then continue to Step 3.

---

### Step 3 — Grow the test suite with real questions

**If coverage count < 10:**

Tell the user you need at least 10 covered questions before deploying.
Ask them to share questions their team actually asks — revenue, retention, top
products, cohorts, funnel metrics, etc. Be conversational; one or two at a time.

For each question:
  a. Identify which metric(s) answer it. If one exists, construct and run the
     `mf query` command and show results as a markdown table.
  b. If no metric covers it:
     - Add the necessary measure to the relevant semantic model YAML.
     - Define a new metric in the metrics YAML.
     - Run `mf validate-configs` to confirm.
     - Tell the user: _"I've added a `<metric_name>` metric to the semantic layer."_
  c. Derive the metric formula (e.g. `SUM(total_price)` or `COUNT(*) WHERE ...`).
  d. Append the question + `mf_query` + `metric` + `formula` to `.databao/test_questions.csv`.
  d. Print updated coverage count after each question.

**If coverage count is 10–14:**

Coverage is good. Offer two options:
  - "Ask another question"
  - "I'm ready — deploy the Slack Bot"

If they choose to deploy, tell them:
_"To deploy, exit Claude Code and select **Deploy Slack Bot** from the Databao menu."_

**If coverage count ≥ 15:**

Proactively suggest deploying:
_"You have N questions covered across M metrics. Your team is ready for
self-service analytics. To deploy the Slack Bot, exit Claude Code — the
Databao menu will reappear and you can select **Deploy Slack Bot** from there."_

---

### Deploy

There is no deploy command to run from here. When the user asks about deploying,
always direct them to exit Claude Code first:

_"Exit Claude Code to return to the Databao menu, then select **Deploy Slack Bot**."_

---

## Tone and style

- Be encouraging and concrete — this is an onboarding wizard, not a chat interface.
- Always show `mf query` results as markdown tables.
- After every interaction, show the current coverage count and the next suggested action.
- Never ask the user to do something manually that you can do with a tool.
"""


def claude_impl(project_dir: Path, on_exit=None) -> None:
    databao_yml = project_dir / ".databao" / "databao.yml"
    if not databao_yml.exists():
        click.echo(click.style("Error: ", fg="red") + "No Databao project found. Run `databao init` first.")
        raise SystemExit(1)

    config = _load_yaml(databao_yml)
    dbt_project = config.get("dbt", {}).get("project", "databao")

    skill_dir = project_dir / ".claude" / "skills" / "databao"
    skill_dir.mkdir(parents=True, exist_ok=True)
    skill_file = skill_dir / "SKILL.md"
    skill_file.write_text(SKILL_CONTENT)

    click.echo(click.style("  ✓ ", fg="green") + f"Databao skill written to {skill_file}")
    click.echo(f"\nOpening Claude Code with Databao skill for '{dbt_project}'...\n")

    result = subprocess.run(["claude", "/databao"], cwd=project_dir)
    if result.returncode != 0:
        click.echo(click.style("Error: ", fg="red") + "`claude` exited with an error.", err=True)
        sys.exit(result.returncode)

    if on_exit is not None:
        on_exit()


def _load_yaml(path: Path) -> dict:
    try:
        with open(path) as f:
            return yaml.safe_load(f) or {}
    except Exception:
        return {}
