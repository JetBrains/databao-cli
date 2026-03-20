---
name: check-pr-comments
description: Check GitHub pull request review comments using the GitHub CLI. Use when the user wants to fetch unresolved PR review threads, implement requested changes on the PR branch, validate the fix locally, reply in-thread, and resolve addressed threads.
compatibility: gh must be installed and authenticated.
---

# Address PR Comments

Address GitHub pull request review comments with `gh`, make the requested
changes on the PR branch, validate them locally, and close the loop on GitHub.

## Steps

### 1. Identify the PR and verify GitHub access

Start with:

```bash
gh auth status
```

If the user supplied a PR number or URL, use it. Otherwise try the PR for the
current branch:

```bash
gh pr view --json number,title,url,headRefName,baseRefName
```

If no PR can be identified, ask the user for the PR number or URL before doing
anything else.

### 2. Fetch unresolved review threads

Prefer GraphQL over `gh pr view --comments`. Timeline comments do not preserve
thread resolution state, file paths, or line mappings well enough for this
task.

First, obtain the repository owner and name:

```bash
gh repo view --json owner,name -q '.owner.login + " " + .name'
```

Then fetch the review threads using those values:

```bash
gh api graphql -f query='
  query($owner:String!, $repo:String!, $number:Int!) {
    repository(owner:$owner, name:$repo) {
      pullRequest(number:$number) {
        reviewThreads(first:100) {
          pageInfo { hasNextPage endCursor }
          nodes {
            id
            isResolved
            isOutdated
            comments(first:20) {
              pageInfo { hasNextPage endCursor }
              nodes {
                id
                databaseId
                author { login }
                body
                path
                line
                originalLine
                createdAt
                url
              }
            }
          }
        }
      }
    }
  }' -F owner=<OWNER> -F repo=<REPO> -F number=<PR_NUMBER>
```

Replace `<OWNER>` and `<REPO>` with the values from `gh repo view` above, and
`<PR_NUMBER>` with the pull request number.

If `hasNextPage` is `true` for either `reviewThreads` or `comments`, paginate
by re-running the query with an `after: "<endCursor>"` argument on the
corresponding connection until all pages are fetched.

Focus first on threads where `isResolved` is `false`. Treat `isOutdated: true`
as lower priority unless the underlying issue still exists in the current code.

### 3. Build a Markdown triage table and stop for approval

Before making changes, summarize the unresolved threads in a Markdown table so
the user can see the plan at a glance.

Use one row per unresolved thread with these columns:

- `Comment`: a short paraphrase of the reviewer request
- `File`: the referenced path, or `PR-level` if the thread is not tied to a file
- `Triage`: one of `Implement`, `Reply only`, or `Blocked`

Template:

```md
| Comment | File | Triage |
| --- | --- | --- |
| Validate empty input before calling the parser | `src/foo.py` | Implement |
| Why not keep the old flag name for compatibility? | `src/cli.py` | Reply only |
| This conflicts with another approved requirement | `src/config.py` | Blocked |
```

Then decide which bucket each thread belongs to:

- **Code change needed**: implement the requested fix.
- **Explanation needed**: no code change is appropriate; prepare a concise,
  respectful reply with evidence.
- **Blocked or conflicting**: the reviewer request conflicts with the PR scope,
  another comment, or product intent. Surface that to the user before making a
  broad or risky change.

Read the referenced files and nearby code before editing. Do not treat a single
comment in isolation if it touches behavior shared across the module.

The triage table should come before any file edits or GitHub replies.

After showing the table, stop and wait for explicit user approval. Do not:

- edit files
- run validation for a proposed fix
- reply on GitHub
- resolve any review thread

Approval must be explicit. A vague acknowledgment is not enough.

### 4. Apply the fixes on the PR branch

Only proceed to this step after the user approves the triage table.

Address one thread at a time and keep the change set minimal. When multiple
threads point to the same root cause, fix the root cause once and reply to each
affected thread explicitly.

Guardrails:

- Do not push unrelated cleanups while addressing review comments.
- Do not discard reviewer requests without explaining why.
- Do not mark a thread resolved until the underlying issue is actually handled.

### 5. Validate before replying

Only run this after the user has approved implementation.

Run the smallest meaningful validation for the changed area, based on the repo's
actual tooling.

Do not reply with "fixed" unless you have either run the relevant validation or
state clearly that the change is unverified.

### 6. Reply in-thread and resolve when appropriate

Only run this after the user has approved proceeding beyond the triage table.

If the user asked you to actually address the PR comments on GitHub, post a
thread reply after the code change and validation.

Reply to a thread:

```bash
gh api graphql -f query='
  mutation($threadId:ID!, $body:String!) {
    addPullRequestReviewThreadReply(
      input:{pullRequestReviewThreadId:$threadId, body:$body}
    ) {
      comment { url }
    }
  }' -F threadId=<THREAD_ID> -f body='Addressed in <summary>. Validation: <command/result>.'
```

Resolve the thread only after the response is posted and the issue is actually
addressed:

```bash
gh api graphql -f query='
  mutation($threadId:ID!) {
    resolveReviewThread(input:{threadId:$threadId}) {
      thread { id isResolved }
    }
  }' -F threadId=<THREAD_ID>
```

If the right action is explanation rather than code, reply with the reasoning
and leave the thread open unless the user explicitly wants you to resolve it.

## What this skill does NOT do

- It does not replace local code review before implementation.
- It does not assume every comment should lead to a code change.
- It does not resolve threads silently without a reply and a real fix.
