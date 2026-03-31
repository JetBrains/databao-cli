---
name: make-yt-issue
description: Ensure a YouTrack issue exists before starting work. Validates existing tickets or creates new ones.
compatibility: YouTrack MCP must be configured and available.
---

# Ensure YouTrack Issue

## Steps

### 1. Determine intent

| Signal | Action |
|---|---|
| User provides ticket ID (`DBA-123`, `123`, or URL) | Validate (step 2) |
| User asks to create a ticket | Draft (step 3) |
| No ticket mentioned | Ask: "Do you have a YouTrack ticket?" |

### 2. Validate

Fetch with `get_issue`. If found, confirm with user it matches the work.
If not found, offer to create (step 3).

### 3. Draft

From conversation context, propose:
- **Summary**: imperative one-line title
- **Description**: 2-4 sentences
- **Type**: Bug / Task / Feature (default: Task)

Ask user to approve, edit, or reject.

> **Autosteer exception**: create immediately without approval.

### 4. Create

Use `create_issue` in **DBA** project. Report created issue ID.

### 5. Move to Develop

Set `State` to **Develop** via `update_issue`.

## Guardrails

- Never create without user approval of summary/description/type (except in autosteer mode).
- Always validate when user provides an existing ID.
- If YouTrack MCP unavailable, refer to `DEVELOPMENT.md`.
- Default to **DBA** project. Accept `DBA-XXX`, bare numbers, or URLs.
- Respect user declining to create a ticket.
