# Layer Decision Guide

When absorbing a failure into the harness, you must decide which layer receives the prevention rule. Placing a rule in the wrong layer means it either gets ignored (too weak) or creates unnecessary friction (too strong).

This guide provides the decision criteria, a flowchart, and examples for each layer assignment.

---

## The Four Layers

| Layer | Name | What goes here | Implemented as |
|---|---|---|---|
| A | Constitutional Documents | Universal rules for all work | AGENTS.md, CLAUDE.md |
| B | Contextual Execution Documents | Rules for specific work types | Skills, runbooks, playbooks |
| C | Automated Enforcement | Mechanically blocked violations | Hooks, scripts, pre-commit checks |
| D | Memory and Learning Documents | Reference, history, terminology | Glossary, postmortems, failure log, ADRs |

---

## Decision Flowchart

Work through the questions in order. Stop at the first "yes."

```
START: A failure has occurred. Where does the prevention rule go?

Q1: Does this rule apply to EVERY task, regardless of type?
    |
    YES --> Layer A (AGENTS.md)
    |       Add a universal rule.
    |       Keep AGENTS.md under 60 lines.
    |
    NO
    |
    v
Q2: Does this failure occur within a specific, recognizable work type?
    (migration, API change, code review, deployment, etc.)
    |
    YES --> Layer B (Skill or Runbook)
    |       Create or update the skill for that work type.
    |       Add the missing step, verification, or guidance.
    |
    NO
    |
    v
Q3: Has this specific violation occurred 2+ times already?
    OR: Is the failure cost so high that one recurrence is unacceptable?
    OR: Is this a verification step that humans and agents both skip?
    |
    YES --> Layer C (Hook or Script)
    |       Promote to automated enforcement.
    |       Choose: prompt hook (judgment required) or command hook (pass/fail).
    |
    NO (first occurrence, low cost, non-verifiable)
    |
    v
Q4: Is this a terminology issue, an outdated document, or a fact
    that future sessions should remember?
    |
    YES --> Layer D (Docs, Glossary, Postmortem)
    |       Add or update the relevant document.
    |       Add prohibited synonyms if terminology was the issue.
    |
    NO
    |
    v
    UNCLEAR --> Start at Q1 again with the root cause, not the symptom.
                If still unclear, default to Layer B (add a skill step)
                and revisit after the next occurrence.
```

---

## Layer A: Constitutional Documents

**Decision rule**: If the rule applies to all work → AGENTS.md

**Use when**:
- The behavior that failed should be correct in every session, every task, every developer
- There is no condition under which the rule would not apply
- The rule is short enough to fit in one or two lines without explanation

**Do not use when**:
- The rule only applies when doing a specific type of work (use Layer B instead)
- The rule requires a long explanation or step-by-step procedure (use Layer B instead)
- The rule is a response to a single failure with no established pattern (wait for recurrence)

**Examples of correct Layer A rules**:
- "Verify before claiming completion."
- "Do not use destructive commands without explicit approval."
- "When new concepts emerge, define them in the glossary before using them in code."
- "Update related docs when contracts or APIs change."

**Examples of things that do NOT belong in Layer A**:
- "When running a migration, take a backup first." (Layer B — migration skill)
- "Run `tsc --noEmit` before commit." (Layer C — hook)
- "The canonical term for user records is `User`, not `UserRecord`." (Layer D — glossary)

---

## Layer B: Contextual Execution Documents

**Decision rule**: If the rule applies only to a specific work type → skill or runbook

**Use when**:
- The failure occurred during a recognizable, recurring task type
- The fix is a missing step, missing verification, or missing guidance within that task type
- The rule would be noisy or irrelevant if loaded for unrelated tasks

**Skill vs. Runbook**:
- **Skill**: Planned, recurring work (API changes, migrations, code review, deployments)
- **Runbook**: Reactive, incident-triggered work (outage recovery, rollback, data fix)

**Structure required** (from skill-template.md):
- When to use (and when NOT to use)
- Ordered steps
- Verification checklist
- Common mistakes

**Examples of correct Layer B placements**:
- "Before running a database migration, verify a backup exists." → migration skill, Steps section
- "When changing an API response, update the OpenAPI spec in the same commit." → API endpoint skill, Steps section
- "When rolling back a deployment, verify the previous version is still in the artifact registry." → deployment runbook

---

## Layer C: Automated Enforcement

**Decision rule**: If repeated violations must be forcibly blocked → hook or script

**Use when**:
- The same violation has occurred 2+ times despite a text rule existing
- The failure cost is high enough that one more occurrence is unacceptable
- The check can be expressed as a pass/fail command
- Human or agent memory has demonstrably failed to enforce the rule

**Hook type selection**:

| Type | When to use |
|---|---|
| Prompt hook | Judgment required; check involves reading/updating docs; reminder is sufficient |
| Command hook | Pass/fail check; mechanical; violation is frequent or high-cost |

**Trigger point selection**:

| Trigger | What it guards |
|---|---|
| pre-commit | Code quality (lint, typecheck, test) |
| pre-push | Integration quality (full test suite, build) |
| at completion | Completion report quality (gate checklist) |
| on file change | Documentation sync (changed code requires doc update) |

**Examples of correct Layer C placements**:
- "Run `tsc --noEmit` before commit" (violated twice) → pre-commit command hook
- "Answer completion gate questions before reporting done" → completion prompt hook
- "Lint must pass" (violated three times) → pre-commit command hook

**When NOT to use Layer C**:
- First occurrence of a violation (use Layer A or B first)
- Rule that requires complex judgment (use Layer B skill instead)
- Rule that is rarely violated (Layer C maintenance cost exceeds benefit)

---

## Layer D: Memory and Learning Documents

**Decision rule**: If future reference is important → docs, glossary, postmortem, or failure log

**Use when**:
- A terminology conflict caused the failure → glossary entry
- An architectural or API decision was made that future sessions should know → ADR
- A significant incident occurred that has investigation and resolution value → postmortem
- A failure pattern was observed that may recur — recording it enables pattern detection → failure log

**Document types**:

| Type | When to create |
|---|---|
| Glossary entry | New term introduced, or existing term used inconsistently |
| ADR (Architecture Decision Record) | Significant design choice made with tradeoffs |
| Postmortem | Incident with meaningful investigation and recovery steps |
| Failure log entry | Any failure absorbed into the harness |

**Examples of correct Layer D placements**:
- Agent created `UserRecord` type when `User` already existed → add `User` to glossary with prohibited synonyms
- Team decided to use CQRS for the write path after evaluating alternatives → ADR documenting the decision and rejected alternatives
- Outage caused by misconfigured environment variable → postmortem with timeline and prevention steps

---

## Multi-Layer Absorptions

Some failures require changes at multiple layers simultaneously. This is normal — classify the root cause first, then identify secondary layers.

**Example**:
Agent skipped typecheck (Category 3) and used a non-canonical term (Category 4) in the same session.

- Root cause: typecheck not automated → Layer C (add pre-commit hook)
- Secondary: term not in glossary → Layer D (add glossary entry)
- No Layer A or B change needed

**Example**:
Agent improvised a migration procedure (Category 2) and the migration guide was outdated (Category 4).

- Root cause: no migration skill → Layer B (create migration skill)
- Secondary: outdated guide caused confusion → Layer D (update or archive the old guide)
- Consider Layer C if migrations have a high failure cost: add a hook requiring backup confirmation

---

## Decision Summary

| Question | Answer | Layer |
|---|---|---|
| Applies to all work? | Yes | A |
| Specific to one work type? | Yes | B |
| Repeated violation or high cost? | Yes | C |
| Terminology, history, or reference? | Yes | D |
| None of the above | — | Default to B, revisit |
