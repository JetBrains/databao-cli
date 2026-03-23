---
name: local-code-review
description: Review local code changes in Databao repositories before a commit or PR. Use when the user wants a review of staged or unstaged diffs, local branches, or pre-merge changes. Focus on correctness, regressions, missing tests, API/CLI behavior changes, executor or tooling changes, dependency or plugin-loading risks, and user-visible behavior changes.
compatibility: git must be installed and rg (ripgrep) is recommended.
---

# Local Code Review

This skill is for review, not implementation. Do not edit files unless the
user explicitly switches from review to fixing issues.

If the user didn't request an explicit review, ask the user if a review is
wanted before doing it.

## Parameter

This skill accepts an optional **scope** argument:

- `staged` — review only staged changes (`git diff --cached`)
- `branch` — review the branch diff against main (default)
- `files:<path>` — review specific files or directories (e.g. `files:src/databao_cli/mcp/`)

If no scope is provided, default to `branch`.

## Steps

### 1. Resolve scope

Determine the review scope from the parameter (or default to `branch`).
Prepare a short description of what will be reviewed.

### 2. Spawn review sub-agent

Launch a sub-agent using the **Agent tool** with `subagent_type: "general-purpose"`.

Build the sub-agent prompt as follows:

1. Read the file `.claude/skills/local-code-review/review-guidelines.md` and
   include its full content in the prompt.
2. Tell the sub-agent the resolved scope (e.g. "Review the branch diff against
   main", "Review staged changes", "Review files under src/databao_cli/mcp/").
3. Include this preamble in the prompt:

   > You are reviewing code changes for the Databao CLI project.
   > You have NO prior context about why these changes were made — review
   > purely on merit. Use your tools (Read, Grep, Glob, Bash) to inspect
   > the code, diffs, and surrounding implementation. Do NOT edit any files.

### 3. Report findings

Return the sub-agent's output to the user as-is. Do not summarize or filter
the findings. If the sub-agent reports no findings, relay that clearly.

### 4. Wait for user approval before fixing

Do NOT start resolving any findings automatically. Present the findings and
**ask the user** which ones (if any) they want you to fix. Only proceed with
code changes after explicit user approval.
