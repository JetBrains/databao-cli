---
name: check-pr-comments
description: Fetch unresolved PR review threads, triage them, implement fixes, validate, reply in-thread, and resolve.
compatibility: gh must be installed and authenticated.
---

# Address PR Comments

## Steps

### 1. Identify the PR

Run `gh auth status`. Use the user-supplied PR number/URL, or detect from
current branch: `gh pr view --json number,title,url,headRefName,baseRefName`.
If no PR found, ask the user.

### 2. Fetch unresolved review threads

Get repo owner/name: `gh repo view --json owner,name -q '.owner.login + " " + .name'`

Fetch threads via GraphQL:

```bash
gh api graphql -f query="
  query(\$owner:String!, \$repo:String!, \$number:Int!) {
    repository(owner:\$owner, name:\$repo) {
      pullRequest(number:\$number) {
        reviewThreads(first:100) {
          nodes {
            id isResolved isOutdated
            comments(first:20) {
              nodes { id author{login} body path line url }
            }
          }
        }
      }
    }
  }" -F owner=<OWNER> -F repo=<REPO> -F number=<PR_NUMBER>
```

Paginate if `hasNextPage` is true. Focus on `isResolved: false` threads.

### 3. Triage table -- stop for approval

Present a Markdown table before any edits:

| Comment | File | Triage |
| --- | --- | --- |
| <paraphrase> | `path` or `PR-level` | Implement / Reply only / Blocked |

Wait for **explicit** user approval before proceeding.

### 4. Apply fixes

Address one thread at a time, minimal changes. Fix root cause once when
multiple threads share it.

### 5. Validate

Run smallest meaningful validation for the changed area. Do not claim
"fixed" without running validation or stating it is unverified.

### 6. Reply and resolve

Reply in-thread:
```bash
gh api graphql -f query="mutation(\$threadId:ID!, \$body:String!) {
  addPullRequestReviewThreadReply(input:{pullRequestReviewThreadId:\$threadId, body:\$body})
  { comment { url } }
}" -F threadId=<ID> -f body='Addressed in <summary>.'
```

Resolve only after reply and real fix:
```bash
gh api graphql -f query="mutation(\$threadId:ID!) {
  resolveReviewThread(input:{threadId:\$threadId}) { thread { id isResolved } }
}" -F threadId=<ID>
```

For explanation-only replies, leave thread open unless user says to resolve.

## Guardrails

- No edits, replies, or resolves before user approves the triage table.
- No unrelated cleanups while addressing comments.
- No silent thread resolution without a reply and real fix.
