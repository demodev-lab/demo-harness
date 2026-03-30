# Failure Log Template

Use this document as `docs/failure-log.md` in any project. Record every significant agent or human failure here. This log feeds the weekly harness review process — without recorded failures, pattern extraction is impossible.

A failure log entry is not a blame record. It is raw material for harness improvement. The goal is to answer: "What structural change prevents this from recurring?"

---

## Log Format

Each entry follows this structure:

```
### [YYYY-MM-DD] [Short failure title]

- **Date**: YYYY-MM-DD
- **Category**: [One of the 6 categories below]
- **Cause**: [1-3 sentences describing what went wrong and why]
- **Resolution**: [What was done to fix this specific instance]
- **Absorbed-to**: [Which layer received the prevention rule, or "pending" if not yet absorbed]
```

---

## The 6 Failure Categories

Every failure must be classified into exactly one of these categories. If a failure fits multiple categories, choose the root cause.

1. **Global rule absence** — A universal rule that should have been in AGENTS.md did not exist. The agent had no guidance on this behavior.

2. **Specific task procedure absence** — A rule exists but no skill or runbook defined the steps for this specific work type. The agent improvised a procedure.

3. **Tool/verification automation absence** — A verification step that should have been automated (hook, lint, test) was not automated. It was left to human or agent memory.

4. **Terminology/documentation mismatch** — The agent used a different term for a concept than the codebase uses, or documentation was outdated relative to the code.

5. **Excessive context pollution** — Too much irrelevant content was loaded into context, causing the agent to lose focus on the actual task or misinterpret instructions.

6. **Unclear authority/responsibility boundaries** — It was unclear whether the agent, a sub-agent, or a human was responsible for a decision or action. Work was duplicated, skipped, or handed off incorrectly.

---

## Example Entry

```
### 2024-11-14 Agent reported complete without running typecheck

- **Date**: 2024-11-14
- **Category**: Tool/verification automation absence
- **Cause**: The agent added a new function with a TypeScript generic parameter, introduced a type error in the process, and reported the task complete. No hook blocked the completion. The AGENTS.md rule "run typecheck before completion" was present as text but not enforced mechanically.
- **Resolution**: Manually ran `tsc --noEmit`, found 2 type errors, fixed them, re-tested.
- **Absorbed-to**: Layer C — added pre-commit hook that runs `tsc --noEmit` and blocks commit on failure. AGENTS.md rule retained as context but no longer the sole enforcement mechanism.
```

---

## Second Example Entry

```
### 2024-11-21 Agent created a new "UserRecord" type conflicting with existing "User" model

- **Date**: 2024-11-21
- **Category**: Terminology/documentation mismatch
- **Cause**: The glossary did not define the canonical name for the user domain model. The agent invented "UserRecord" because it could not find guidance. This created a duplicate type that was used in 3 new files before the conflict was caught.
- **Resolution**: Deleted UserRecord, refactored 3 files to use the existing User model, added User to glossary.
- **Absorbed-to**: Layer D — added "User" entry to glossary with prohibited synonyms including UserRecord, UserModel, UserEntity. Layer A updated to add: "When new concepts emerge, check glossary first; define before using."
```

---

## Active Failure Log

Add new entries below, most recent at the top.

<!-- Most recent entries first -->

---

## Absorbed Entries Archive

Move entries here once the harness change has been made and verified to prevent recurrence.

<!-- Entries where prevention is confirmed working -->
