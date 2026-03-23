---
name: review-architecture
description: Review architecture quality, maintainability, and developer experience before or after significant changes. Use when introducing a new CLI command or MCP tool, refactoring core module boundaries, diagnosing repeated dev friction, or preparing a PR with broad structural impact.
---

# Review Architecture

This skill reviews architecture quality, maintainability, and developer
experience (Dev UX) before or after significant changes.

## Parameter

This skill accepts an optional **scope** argument:

- `branch` — review architecture of code changed on the current branch (default)
- `module:<path>` — review a specific module (e.g. `module:src/databao_cli/mcp/`)
- `full` — review the full project architecture

If no scope is provided, default to `branch`.

## Steps

### 1. Resolve scope

Determine the review scope from the parameter (or default to `branch`).
Prepare a short description of what will be reviewed.

### 2. Spawn review sub-agent

Launch a sub-agent using the **Agent tool** with `subagent_type: "general-purpose"`.

Build the sub-agent prompt as follows:

1. Read the file `.claude/skills/review-architecture/review-guidelines.md` and
   include its full content in the prompt.
2. Tell the sub-agent the resolved scope (e.g. "Review the architecture of the
   current branch changes", "Review the module src/databao_cli/mcp/",
   "Review the full project architecture").
3. Include this preamble in the prompt:

   > You are reviewing the architecture of the Databao CLI project.
   > You have NO prior context about why these changes were made — review
   > purely on merit. Use your tools (Read, Grep, Glob, Bash) to inspect
   > the code and project structure. Do NOT edit any files.

### 3. Report findings

Return the sub-agent's output to the user as-is. Do not summarize or filter
the findings.

### 4. Wait for user approval before fixing

Do NOT start resolving any findings automatically. Present the findings and
**ask the user** which ones (if any) they want you to fix. Only proceed with
code changes after explicit user approval.
