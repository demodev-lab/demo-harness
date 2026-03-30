# Rule Promotion Criteria

Rule promotion is the act of moving a rule from a less enforced layer to a more enforced layer. It is the primary mechanism for strengthening the harness when text rules have demonstrably failed to prevent a violation.

This document defines: when to promote, how to choose the target layer, how to choose the hook type, and examples of rules that should and should not be promoted.

Source: Sections 5.3 and 9 of the Harness Engineering Manual, plus Appendix C.2.

---

## When to Promote

Promotion is warranted when ANY of the following criteria are met:

### Criterion 1: Same Omission Occurs 2+ Times

A rule exists in AGENTS.md or a skill. The same violation of that rule has been observed at least twice — in the same session or across sessions. The text rule is not sufficient; it requires mechanical enforcement.

**Evidence required**: Two failure log entries with the same root behavior, even if the specific task differed.

**Example**: The rule "run typecheck before completion" is in AGENTS.md. It was violated on 2024-11-14 (agent skipped typecheck, committed type errors) and again on 2024-11-22 (agent skipped typecheck on a different file). Two occurrences → promote to pre-commit hook.

---

### Criterion 2: Verification That Humans or Agents Frequently Forget

A verification step is required but is consistently skipped — not because of a deliberate decision, but because it is not memorable enough to execute reliably. Even when reminded, the step is skipped in the next session.

**Evidence required**: The step was skipped in at least 2 of the last 5 task completions. Or: a human has had to manually remind an agent to run this verification more than once.

**Example**: "Check if docs need updating" is in the completion checklist. It is skipped in 3 of the last 5 sessions. → Promote to a prompt hook that injects the question at completion time.

---

### Criterion 3: High Failure Cost

When this rule is violated, the cost of recovery is significant. This criterion can trigger promotion after a single occurrence if the cost is severe enough.

**Cost indicators** (any one is sufficient):
- Data loss risk (destructive command, migration without backup)
- Cascading failures (breaking a shared contract without notifying dependents)
- Significant recovery time (hours of debugging, rollback required)
- External impact (broken API affecting downstream consumers, security exposure)

**Example**: "Always take a database backup before running a migration" — violating this once could cause irreversible data loss. → Promote to command hook immediately after first occurrence, do not wait for second.

---

### Criterion 4: Directly Affects Completion Report Quality

The item being forgotten causes the agent to report "complete" when the task is actually incomplete or incorrect. This is the single most damaging failure mode because subsequent work builds on a false foundation.

**Evidence required**: A completion report was given that omitted verification results, omitted known gaps, or made a false claim about the state of the work.

**Example**: Agent reports "complete" without stating which tests were run. → Promote to completion gate prompt hook (minimum) or command hook (preferred).

---

## Promotion Decision: Which Layer

Use the layer decision guide (`layer-decision-guide.md`) for the full flowchart. For rule promotion specifically:

| Current layer | Promotion target | When |
|---|---|---|
| None (verbal correction only) | Layer A (AGENTS.md) | First occurrence of a universal violation |
| Layer A (AGENTS.md text rule) | Layer B (skill step) | Rule is task-specific, not universal |
| Layer A (AGENTS.md text rule) | Layer C (hook) | 2+ violations OR high cost OR affects completion quality |
| Layer B (skill step) | Layer C (hook) | 2+ violations of this specific step |
| Layer C (prompt hook) | Layer C (command hook) | Prompt hook is being ignored or bypassed |

**Do not skip layers unnecessarily.** A text rule that has only been violated once and has low failure cost does not need a hook. Hooks add friction and maintenance cost — they are warranted only when text rules have demonstrably failed.

---

## Hook Type Selection Guide

When Layer C promotion is warranted, choose between a prompt hook and a command hook.

### Prompt Hook

**What it does**: Injects a question, reminder, or requirement into the agent's context at a trigger point. The agent must respond to or address the prompt before proceeding.

**Use when**:
- The check requires judgment that a script cannot make (e.g., "did you check whether docs need updating?")
- The violation involves reading or updating documents rather than running commands
- The rule is being violated due to forgetting, not resistance — a reminder is sufficient
- First promotion of a frequently-forgotten check (escalate to command hook if prompt is also ignored)

**Format**:
```
[At completion] Before reporting done, answer:
1. Which tests did you run? What were the results?
2. Did any docs or contracts need updating? Were they updated?
```

**Weakness**: Depends on the agent reading and following the prompt. If the agent is bypassing the prompt, escalate to a command hook.

---

### Command Hook

**What it does**: Runs a script at a trigger point and blocks the action (commit, push, completion) if the script fails. Mechanical enforcement — does not depend on agent or human memory.

**Use when**:
- The check can be expressed as a pass/fail command (lint passes, tests pass, typecheck passes)
- The violation is frequent (2+ times) or high-cost
- A prompt hook has already been tried and was bypassed or ignored
- The rule is in the "must never be skipped" category

**Format**:
```bash
#!/bin/bash
# Runs lint, typecheck, tests. Blocks on failure.
npm run lint && tsc --noEmit && npm test
```

**Trigger point selection**:

| Trigger | Appropriate for |
|---|---|
| pre-commit | Code quality checks: lint, typecheck, unit tests |
| pre-push | Integration checks: full test suite, build verification |
| at-completion | Completion report quality: gate checklist questions |
| on-file-change | Documentation sync: checks whether changed files require doc updates |

---

## Examples: Rules That Should Be Promoted

These rules meet one or more promotion criteria and warrant Layer C enforcement:

**"Run typecheck before completion"** (in AGENTS.md)
- Violated twice → Criterion 1
- Promote to: pre-commit command hook running `tsc --noEmit`

**"Update OpenAPI spec when API response shape changes"** (in API skill)
- Violated twice AND affects downstream consumers → Criteria 1 + 3
- Promote to: on-file-change prompt hook checking "did you update the spec?"

**"Take a database backup before running a migration"** (in migration skill)
- High failure cost (irreversible data loss) → Criterion 3
- Promote to: command hook that confirms backup exists before migration script runs

**"Answer completion gate questions before reporting done"** (in AGENTS.md)
- Affects completion report quality → Criterion 4
- Promote to: completion prompt hook (minimum) or command hook (preferred)

**"Run lint before committing"** (in AGENTS.md)
- Violated twice → Criterion 1
- Promote to: pre-commit command hook running lint

---

## Examples: Rules That Should NOT Be Promoted

These rules do not meet promotion criteria. Promoting them would add unnecessary friction:

**"Prefer existing modules before adding new dependencies"**
- Requires judgment — cannot be expressed as a pass/fail command
- Violated once with low recovery cost
- Keep as Layer A text rule; monitor for recurrence

**"Use the project's error response format for new endpoints"**
- Task-specific (only applies to API work) — belongs in the API skill, not a hook
- Violations are caught by code review
- Move to Layer B if not already there; do not promote to hook

**"Read relevant docs before editing a file"**
- Requires judgment — no command can verify whether the agent read the right docs
- Not verifiable mechanically
- Keep as Layer A text rule

**"Prefer small reversible diffs"**
- Style guidance that requires judgment
- No clear pass/fail criteria
- Keep as Layer A text rule; do not attempt to automate

**"Archive old failure log entries once absorbed"**
- Administrative task with no quality impact if forgotten occasionally
- Low cost, infrequent
- Keep as Layer D convention; not a hook candidate

---

## Promotion Process

When a rule meets promotion criteria:

1. **Identify the trigger point** — when should the enforcement run? (pre-commit, pre-push, at completion, on file change)

2. **Choose the hook type** — prompt hook (judgment required) or command hook (pass/fail)

3. **Write the hook** — as specific as possible to the behavior being enforced, not a generic "be careful" message

4. **Test the hook against a known violation** — deliberately trigger the violation and verify the hook catches it

5. **Record in the failure log** — update the entry that prompted the promotion with "Absorbed-to: Layer C — [hook name]"

6. **Decide whether to keep the text rule** — for command hooks, the text rule in AGENTS.md can often be removed (the hook is now the enforcement). For prompt hooks, keep the text rule as context.

7. **Verify in the next identical task** — confirm the hook fires correctly and the violation does not recur

---

## Promotion Rollback

If a promoted hook is creating excessive friction (blocking legitimate work, firing on false positives), it can be rolled back:

1. Disable or remove the hook
2. Record the rollback in the failure log with reason
3. Keep the text rule as Layer A/B guidance
4. Reconsider whether the hook was too broad — a more targeted hook may work better than removal

Rollback does not mean the rule was wrong. It means the enforcement mechanism needed refinement.
