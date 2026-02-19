[![official project](https://jb.gg/badges/official.svg)](https://github.com/JetBrains#jetbrains-on-github)
[![PyPI version](https://img.shields.io/pypi/v/databao.svg)](https://pypi.org/project/databao)

<h1 align="center">Databao CLI</h1>

<p align="center">A command-line interface tool for working with <a href="https://github.com/JetBrains/databao-agent">Databao Agent</a> and <a href="https://github.com/JetBrains/databao-context-engine">Databao Context Engine</a></p>


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

## Quick start

1. Create a project directory and navigate to it:

   ```bash
   mkdir databao-project && cd databao-project
   ```

1. Initialize the project:

   ```bash
   databao init
   ```

1. When prompted, agree to configure a domain and follow the prompts to add data sources.
   
   A domain is a dedicated space where data context, context, and agent chats live.

1. Build context:

   ```bash
   databao build
   ```

1. Run the Databao app:

   ```bash
   databao app
   ```

1. Click **+ New chat** and ask questions about your data:

   ```text
   # Example questions:
   What is our refund rate by month?
   What is our 90-day repeat purchase rate
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

[//]: # (See the [LICENSE]&#40;LICENSE.md&#41; file for details.)

---

<p align="center">
 <b>Like Databao? </b> Give us a ⭐! It will help to distribute the technology.
</p>

<p align="center">
 <a href="https://databao.app">Website</a> •
 <a href="https://discord.gg/hEUqCcWdVh">Discord</a>
</p>