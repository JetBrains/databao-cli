# Eval Skills

Run structured evaluations on agent skills to measure quality and track
improvements across iterations.

## When to use

- After modifying a skill's SKILL.md to verify it still produces good results.
- After changing `docs/agent-shared.md` or guidance docs that skills depend on.
- Periodically to benchmark skill quality and identify regressions.

## Steps

### 1. Pick the skill to evaluate

Identify which skill to eval. Each skill has test cases in
`.claude/skills/<skill-name>/evals/evals.json`.

### 2. Create an iteration directory

```bash
mkdir -p .claude/evals-workspace/iteration-<N>
```

Use the next sequential number. Check existing directories to determine N.

### 3. Run eval cases

For each test case in `evals.json`, run it twice:

**With skill** — spawn a subagent with the skill loaded:
- Provide the skill path: `.claude/skills/<skill-name>`
- Provide the test prompt from `evals.json`
- Save outputs to `.claude/evals-workspace/iteration-<N>/<skill>-<eval-id>/with_skill/outputs/`

**Without skill** — spawn a subagent without the skill:
- Use the same prompt
- Save outputs to `.claude/evals-workspace/iteration-<N>/<skill>-<eval-id>/without_skill/outputs/`

Each run should start with clean context (no prior state).

### 4. Grade outputs

For each run, evaluate every assertion from `evals.json` against the actual
output. Record results in `grading.json`:

```json
{
  "assertion_results": [
    {
      "text": "Agent runs make setup",
      "passed": true,
      "evidence": "Agent executed `make setup` as first command"
    }
  ],
  "summary": { "passed": 3, "failed": 1, "total": 4, "pass_rate": 0.75 }
}
```

Require concrete evidence for every PASS — don't give benefit of the doubt.

### 5. Aggregate results

Compute summary statistics and save to
`.claude/evals-workspace/iteration-<N>/benchmark.json`:

```json
{
  "run_summary": {
    "with_skill": { "pass_rate": { "mean": 0.83 } },
    "without_skill": { "pass_rate": { "mean": 0.33 } },
    "delta": { "pass_rate": 0.50 }
  }
}
```

### 6. Present results for human review

Show a summary table:
- Per-eval pass rates (with vs without skill)
- Overall delta
- Any assertions that always pass (candidates for removal)
- Any assertions that always fail (candidates for revision)

Record human feedback in
`.claude/evals-workspace/iteration-<N>/feedback.json`.

## Iteration loop

After review:
1. Update the SKILL.md based on failed assertions and feedback.
2. Run a new iteration (increment N).
3. Compare benchmark.json across iterations to track improvement.
4. Stop when feedback is consistently empty or pass rates plateau.

## What this skill does NOT do

- Automatically fix skills — it produces evaluation data for human decision-making.
- Run Tier 1/2 validation — use `make lint-skills` or `make smoke-skills` for that.
- Modify evals.json — test cases should be updated deliberately, not during eval runs.
