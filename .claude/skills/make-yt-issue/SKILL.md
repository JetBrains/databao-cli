---
name: make-yt-issue
description: Create a YouTrack issue for planned work using MCP tools. Use when no ticket exists for the work, when the user asks to create a ticket, or before starting untracked work.
---

# Make YouTrack Issue

Create a YouTrack issue in the DBA project using the YouTrack MCP tools.

## Steps

### 1. Gather issue details

Ask the user for (or propose from conversation context):

- **Summary**: concise one-line title
- **Description**: what the work involves and why
- **Type**: Bug, Task, Feature, or other applicable type

### 2. Show the proposed issue

Present the summary, description, and type to the user.
**Wait for explicit approval before creating.**

### 3. Create the issue

Use the `create_issue` MCP tool to create the issue in the DBA project.

### 4. Report

Output the issue ID (e.g., `DBA-123`) so the user can reference it.

### 5. Optionally transition to Develop

If the user is starting work immediately, move the issue to **Develop**
state using `update_issue` (set the `State` field).

## Guardrails

- Never create an issue without explicit user approval of the summary,
  description, and type.
- If the YouTrack MCP server is unavailable, inform the user and refer
  them to `DEVELOPMENT.md` for setup instructions.
- Default to the `DBA` project unless the user specifies otherwise.

## What this skill does NOT do

- It does not manage issue state transitions beyond the initial Develop
  move — ongoing state management (Develop → Review) is handled by the
  development workflow in CLAUDE.md.
- It does not search or update existing issues — use `get_issue` and
  `update_issue` MCP tools directly for that.
