---
name: eval-skills
description: Run structured evaluations on skills to measure quality and track improvements.
argument-hint: "[skill-name ...] (e.g. local-code-review review-architecture)"
---

# Eval Skills

## Steps

### 1. Determine skills to evaluate

If names provided via `$ARGUMENTS`, evaluate those. Otherwise list skills
with `evals/evals.json` files and ask user to pick (accept "all").

### 2. Create iteration directory

```bash
mkdir -p .claude/evals-workspace/iteration-<N>
```

Use next sequential number.

### 3. Run eval cases

For each test case in `evals.json`, run twice:

- **With skill**: subagent with skill loaded, save to `iteration-<N>/<skill>-<id>/with_skill/outputs/`
- **Without skill**: subagent without skill, save to `iteration-<N>/<skill>-<id>/without_skill/outputs/`

Each run starts with clean context.

### 4. Grade

Evaluate assertions against output. Save `grading.json`:
```json
{
  "assertion_results": [{"text": "...", "passed": true, "evidence": "..."}],
  "summary": {"passed": 3, "failed": 1, "total": 4, "pass_rate": 0.75}
}
```

Require concrete evidence for every PASS.

### 5. Aggregate

Save `iteration-<N>/benchmark.json` with mean pass rates (with/without skill) and delta.

### 6. Present results

Show per-eval pass rates, overall delta, always-pass candidates (remove?),
always-fail candidates (revise?). Save feedback to `feedback.json`.

## Iteration loop

Update SKILL.md based on findings, run new iteration, compare benchmarks,
stop when pass rates plateau.
