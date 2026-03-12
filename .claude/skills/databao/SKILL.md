---
name: databao
description: >
  Answer data questions using the connected dbt project. Generates SQL and
  semantic layer views as needed. Also supports /databao test and /databao sync.
  Use for any question about business metrics, reports, or data exploration.
argument-hint: "[data question | test [file] | sync]"
allowed-tools: Bash, Read, Write, Glob, Grep
---

You are a data analyst assistant with access to a dbt project.

Read `databao.yml` in the project root to find the dbt project path and connection.
Read `models/staging/_sources.yml` for available tables, columns, and introspection stats.

---

## Commands

### /databao test [file]

Run regression tests against known good questions and SQL.

1. Determine the questions file:
   - If `$ARGUMENTS` contains a file path, use that file
   - Otherwise look for `test_questions.csv` in the dbt project root
   - If neither exists, tell the user no test file was found

2. Parse the CSV — expected columns: `question`, `gold_sql`, `last_result`

3. For each row:
   - Generate SQL for the `question` using the connected dbt project
   - Compare against `gold_sql` — flag differences
   - Run both queries and compare row counts / results
   - Record pass/fail and any diff in `last_result`

4. Write results back to `test_questions.csv` (update `last_result` column)

5. Print a summary table: question | status | diff

If a file path was passed and it's not `test_questions.csv`, also append passing
rows into `test_questions.csv` in the dbt root for future regression runs.

---

### /databao sync

Update schemas and introspections for all sources in the dbt project.

1. Read `databao.yml` for connection details
2. For each source table in `models/staging/_sources.yml`:
   - Re-introspect columns: unique values, null %, data type
   - Update the `meta` block for each column
3. Detect any new tables in the database not yet in sources — list them
4. Save updated `_sources.yml`
5. Report: X tables synced, Y columns updated, Z new tables detected

---

## Data questions (default)

When `$ARGUMENTS` is a plain data question (not `test` or `sync`):

1. **Understand the question** — identify entities, metrics, and time ranges

2. **Check existing models** — search `models/` for relevant dbt models or marts
   that already answer or partially answer the question

3. **Generate SQL** — write a SQL query against available sources/models.
   Use `{{ ref(...) }}` and `{{ source(...) }}` syntax where appropriate.

4. **If semantic layer is missing** — if no suitable mart or intermediate model
   exists, create one:
   - Write the model file to `models/marts/` or `models/intermediate/`
   - Add it to `models/staging/_sources.yml` if it exposes new entities
   - Run `dbt run --select <model_name>` to materialize it

5. **Execute and return results** — run the final SQL via the dbt connection
   and present results as a markdown table with a plain-language explanation

6. **Cite your sources** — mention which dbt models or source tables were used
