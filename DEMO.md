# Demo Playbook

### 1. Install Databao CLI
Checkout repo
```bash
git clone git@github.com:JetBrains/databao-cli.git
cd databao-cli
```
Install Databao CLI as a global tool
```bash
uv sync --all-extras --all-groups
uv tool install .
```

### 2. Create new Databao project
Go to demo directory
```bash
cd demo
```
Initialize Databao project
```bash
databao init
# Add duckdb source @ shopify002/shopify.duckdb
# Add dbt project @ shopify002/target

databao build
```

### 3. Run UI
Make sure ```OPENAI_API_KEY``` environment variable is set and run
```bash
databao app
```

### 4. In the UI
Select Agent Settings > Executor type: Dbt Executor.

Click Chats > + New Chat and start prompting questions.

Example queries:
```
What is our refund rate by month?

What is our 90-day repeat purchase rate

What share of orders use a discount code (Discount attach rate)

What is our abandoned checkout recovery rate within 7 days

How long does it take to fulfill an order?
```
