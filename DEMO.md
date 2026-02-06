# Demo Playbook

### 1. Install Databao CLI
#### Checkout CLI repository

[Clone](https://docs.github.com/en/repositories/creating-and-managing-repositories/cloning-a-repository) the repository and navigate to the root folder.

```bash
git clone git@github.com:JetBrains/databao-cli.git
cd databao-cli
```
#### Install Databao CLI as a global tool
Install [node](https://nodejs.org/en/download) and [pnpm](https://www.npmjs.com/package/pnpm) to be able to build the frontend.

Next, install [uv](https://docs.astral.sh/uv/getting-started/installation/) to be able to build CLI using  below commands.

```bash
uv sync --all-extras --all-groups
uv tool install .
```

### 2. Create new Databao project
#### Navigate to demo directory
```bash
cd demo
```
#### Initialize Databao project
Execute databao init command.
```bash
databao init
```
After initializing a project, as CLI prompts, confirm configuring a domain

```bash
Do you want to configure a domain now? [y/N]
```
1. During domain creation, start adding datasources. First, add `duckdb` datasource (use name of your choice)

    ```bash
    What type of datasource do you want to add? (dbt, duckdb, parquet, snowflake, sqlite): duckdb
    Datasource name?: new_source
    ```

2. Next, CLI prompts providing database path. Use `shopify002/shopify.duckdb` 
    ```bash
    connection.database_path? : shopify002/shopify.duckdb
    ```

3. Check the connection by confirming the following:
    ```bash
    Do you want to check the connection to this new datasource? [y/N]: y
    ```
Similarly following above steps 1-3, add one more datasource of type `dbt` with `database_path` being `shopify002/target`.

After both `dbt` and `duckdb` datasources are added, `databao` can be built using below command.
```bash
databao build
```

### 3. Run UI
Make sure to set ```OPENAI_API_KEY``` environment variable, if not previously configured.
After that, run `databao` app using below command.
```bash
databao app
```

### 4. In the UI
1. Select `Agent Settings`
2. Locate `Executor type:` and select `Dbt Executor`. Apply changes by pressing the button below.
3. Click `Chats` and add a new chat by pressing `+ New Chat`
4. Start prompting questions.

Example questions:
```
What is our refund rate by month?

What is our 90-day repeat purchase rate

What share of orders use a discount code (Discount attach rate)

What is our abandoned checkout recovery rate within 7 days

How long does it take to fulfill an order?
```