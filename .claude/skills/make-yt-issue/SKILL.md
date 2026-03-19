---
name: make-yt-issue
description: Ensure a YouTrack issue exists before starting work. Use at the start of any task when the user has not provided a ticket ID, when you need to verify a ticket exists, when the user asks to create a ticket, or before starting untracked work.
---

# Ensure YouTrack Issue

Ensure a YouTrack issue exists for the current work. Depending on context, this
skill resolves an existing ticket, or drafts and creates a new one after user
approval.

## Steps

### 1. Determine intent

Read the conversation to decide which path to take:

| Signal | Path |
|--------|------|
| User provides a ticket ID (`DBA-123`, `123`, or a YouTrack URL) | Go to **step 2** (validate) |
| User explicitly asks to create a ticket (e.g., "create a ticket for …") | Go to **step 3** (draft) |
| No ticket mentioned | Ask: *"Do you have a YouTrack ticket for this work?"* — then route based on answer |

Accept `DBA-XXX`, a bare number (expand to `DBA-XXX`), or a full YouTrack URL.

### 2. Validate the ticket

Use the `get_issue` MCP tool to fetch the issue.

- **Found** — display the issue summary and confirm with the user that it
  matches the intended work. If confirmed, proceed to step 5.
- **Not found / error** — inform the user the ticket could not be loaded and
  offer to create a new one (continue to step 3).

### 3. Draft the issue from context

Generate a proposed issue using details from the conversation:

- **Summary**: concise one-line title in imperative mood.
- **Description**: what the work involves and why it matters (2-4 sentences).
- **Type**: Bug, Task, or Feature — infer from context, default to Task.

Present the draft clearly:

```
Summary:  <proposed summary>
Type:     <proposed type>

Description:
<proposed description>
```

Ask the user to **approve, edit, or reject** the draft.
If the user rejects and does not want a ticket, respect that and stop.

### 4. Create the issue

After the user approves (or edits and then approves):

- Use the `create_issue` MCP tool targeting the **DBA** project.
- Report the created issue ID (e.g., `DBA-456`).

### 5. Transition to Develop

Move the issue to **Develop** state using `update_issue` (set the `State`
custom field) so the board reflects active work.

Report the final state: issue ID and current status.

## Guardrails

- Never create an issue without explicit user approval of the summary,
  description, and type.
- Never skip the validation step when the user provides an existing ticket ID —
  always confirm the ticket matches the intended work.
- If the YouTrack MCP server is unavailable, inform the user and refer them to
  `DEVELOPMENT.md` for setup instructions.
- Default to the **DBA** project unless the user specifies otherwise.
- Accept flexible input: `DBA-123`, `123`, or a YouTrack URL should all resolve
  correctly.
- If the user declines to create a ticket, respect that and do not push back.

## What this skill does NOT do

- It does not manage state transitions beyond the initial move to Develop —
  ongoing state management (Develop → Review) is handled by the workflow in
  CLAUDE.md.
- It does not assign the issue or set priority — use `update_issue` or
  `change_issue_assignee` MCP tools directly for that.
