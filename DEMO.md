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
```bash
cd /tmp/
mkdir databao-project && cd databao-project
```

### 3. Inint project
```bash
databao init
```
