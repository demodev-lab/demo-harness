# Hook and Checklist Template

This document provides the two foundational Layer C enforcement templates: the Completion Gate Checklist (C.1) and the Repeated Violation Promotion Rule (C.2). Use these when setting up or auditing automated enforcement in a project.

---

## C.1 Completion Gate Checklist

The completion gate is the universal check that must pass before any task is reported as complete. It is the last line of defense against false completion claims.

This checklist may be implemented as:
- A prompt hook injected at the completion moment
- A script that an agent runs before reporting done
- A manual checklist embedded in AGENTS.md

### Checklist Template

```md
Before declaring completion on any task:

1. Did I run the relevant tests, and did they pass?
   - If no tests exist for this change, did I write at least one?
   - If tests were skipped, state the reason explicitly.

2. Did I run lint and/or typecheck if the change affects typed or shared code?
   - For TypeScript/typed projects: `tsc --noEmit` must pass.
   - For linted projects: lint must pass with no new errors.

3. Did I update related docs and contracts?
   - If an API contract changed: OpenAPI spec or equivalent updated?
   - If architecture changed: relevant decision doc updated?
   - If a new term was introduced: glossary entry added?

4. Did I verify the user-visible or caller-visible behavior?
   - Not just "the code looks right" — actually confirmed the behavior works as expected.

5. Did I record remaining risks or gaps honestly?
   - If anything was deferred, skipped, or uncertain, it is listed in the completion report.
   - "Complete" does not mean "perfect" — it means "nothing hidden."
```

### Implementation as a Prompt Hook

When implementing as an injected prompt hook (runs at session completion or agent "done" signal):

```
Before you report this task as complete, answer each question:
1. Which tests did you run? What were the results?
2. Did you run lint/typecheck? Any failures?
3. Did any contracts, APIs, or docs need updating? Were they updated?
4. Did you verify the actual behavior (not just the code)?
5. What risks or open items remain?

Do not write "complete" until you have answered all five.
```

### Implementation as a Command Hook

When implementing as a script (runs before commit or completion signal):

```bash
#!/bin/bash
# completion-gate.py
# Blocks completion if basic verification has not been run.

echo "Completion Gate Check"
echo "====================="

# Check 1: Tests
if ! npm test --silent 2>/dev/null; then
  echo "BLOCKED: Tests failed or did not run."
  exit 1
fi

# Check 2: Typecheck (adjust command for your stack)
if ! npx tsc --noEmit --silent 2>/dev/null; then
  echo "BLOCKED: Typecheck failed."
  exit 1
fi

echo "Completion gate passed."
exit 0
```

---

## C.2 Repeated Violation Promotion Rule

Not every rule needs to be a hook. Hooks add friction and maintenance cost. Use this rule to decide when a text rule has earned promotion to automated enforcement.

### Promotion Criteria

Promote a text rule to a hook candidate if ANY of the following are true:

1. **Same omission occurs 2+ times**
   The rule exists in AGENTS.md or a skill, but the same violation has been observed at least twice. The text rule is not sufficient.

2. **Verification humans or agents frequently forget**
   Even when reminded, this verification step is skipped. It requires mechanical enforcement to be reliable.

3. **High failure cost**
   When this rule is violated, the cost of recovery is significant — broken builds, data loss risk, cascading failures, or hours of manual work. High cost justifies pre-emptive blocking.

4. **Directly affects completion report quality**
   If missing this step causes a "complete" report that is actually incomplete or incorrect, it must be mechanically blocked. False completion reports erode trust in the entire operating system.

### How to Promote

When a rule meets one or more promotion criteria:

1. Identify the trigger point — when should the hook fire? (pre-commit, pre-push, at completion, on specific file change)
2. Choose the hook type:
   - **Prompt hook**: Injects a reminder or question into context. Lower friction, weaker enforcement.
   - **Command hook**: Runs a script and blocks on failure. Higher friction, stronger enforcement.
3. Write the hook targeting the specific behavior (not a general "be careful" message).
4. Test the hook against a known violation case — verify it actually blocks the behavior.
5. Record the promotion in the failure log and weekly review.

### Promotion Decision Table

| Condition | Recommended Action |
|---|---|
| Rule violated once, low cost | Keep as text rule, monitor |
| Rule violated once, high cost | Promote immediately to command hook |
| Rule violated twice, any cost | Promote to prompt hook minimum |
| Rule violated 3+ times | Promote to command hook |
| Verification always forgotten | Promote to command hook |
| Affects completion quality | Prompt hook minimum, command hook preferred |

### Hook Type Selection

**Use a prompt hook when:**
- The check requires judgment that a script cannot make
- The violation is infrequent enough that a reminder suffices
- The rule involves reading or updating docs (hard to automate fully)

**Use a command hook when:**
- The check can be expressed as a pass/fail command
- The violation is frequent or high-cost
- Human willpower and agent memory have both already failed

---

## Existing Hooks Inventory

Track hooks in this project below. Review during weekly harness review — remove hooks for problems that no longer occur.

| Hook name | Type | Trigger | Enforces | Added date | Last relevant |
|---|---|---|---|---|---|
| completion-gate | command | pre-completion | Tests + typecheck run | | |
| | | | | | |
