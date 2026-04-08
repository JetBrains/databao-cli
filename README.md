[![official project](https://jb.gg/badges/official.svg)](https://github.com/JetBrains#jetbrains-on-github)
[![PyPI version](https://img.shields.io/pypi/v/databao.svg)](https://pypi.org/project/databao)
[![License](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](https://github.com/JetBrains/databao-cli?tab=License-1-ov-file)

<h1 align="center">Databao CLI</h1>

<p align="center">A command-line interface tool for working with <a href="https://github.com/JetBrains/databao-agent">Databao Agent</a> and <a href="https://github.com/JetBrains/databao-context-engine">Databao Context Engine</a></p>

<p align="center">
 <a href="https://jetbrains.com/databao">Website</a> •
 <a href="#quickstart">Quickstart</a> •
 <a href="https://docs.databao.app">Docs</a> •
 <a href="https://discord.gg/hEUqCcWdVh">Discord</a>
</p>

---

## Installation

Databao CLI is [available on PyPI](https://pypi.org/project/databao/)
and can be installed with uv, pip, or another package manager.

### Using uv

```bash
uv add databao
```

### Using pip

```bash
pip install databao
```

## Quickstart

1. Create a project directory and navigate to it:

   ```bash
   mkdir databao-project && cd databao-project
   ```

   > [!TIP]
   > Databao is not terminal-only.
   > If you prefer the web interface, run `databao app` in your project directory.

1. Initialize the project:

   ```bash
   databao init
   ```

1. When prompted, agree to configure a domain –
   a dedicated space where data context, context, and agent chats live.

   Then follow the prompts to add one or several data sources.

1. Build context:

   ```bash
   databao build
   ```

1. Pass your API key as an environment variable:

   ```bash
   # OpenAI or OpenAI-compatible APIs
   export OPENAI_API_KEY=<your-key>

   # Anthropic Claude
   export ANTHROPIC_API_KEY=<your-key>
   ```

1. Run the Databao Agent:

   ```bash
   databao ask
   ```

1. Ask questions about your data:

   ```text
   # Example questions:
   What is our refund rate by month?
   What is our 90-day repeat purchase rate
   ```

For more details about commands, supported data sources, and configuration options,
visit the [docs](https://docs.databao.app).

## Releasing

```bash
# Tag and push a specific version (CI publishes to PyPI)
make release VERSION=0.3.0

# Bump the patch version automatically (e.g. 0.3.0 -> 0.3.1)
make minor-release

# Bump the minor version automatically (e.g. 0.3.1 -> 0.4.0)
make major-release

# Trigger a dev release via GitHub Actions
make dev-release
```

## Contributing

We love contributions! Here’s how you can help:

- ⭐ **Star this repo** — it helps others find us!
- 🐛 **Found a bug?** [Open an issue](https://github.com/JetBrains/databao-cli/issues)
- 💡 **Have an idea?** We’re all ears — create a feature request
- 👍 **Upvote issues** you care about — helps us prioritize
- 🔧 **Submit a PR**
- 📝 **Improve docs** — typos, examples, tutorials — everything helps!

New to open source? No worries! We’re friendly and happy to help you get started.

## License

Apache 2.0 — use it however you want.

See the [LICENSE](LICENSE) file for details.

---

<p align="center">
 <b>Like Databao? </b> Give us a ⭐! It will help to distribute the technology.
</p>

<p align="center">
 <a href="https://jetbrains.com/databao">Website</a> •
 <a href="https://docs.databao.app">Docs</a> •
 <a href="https://discord.gg/hEUqCcWdVh">Discord</a>
</p>