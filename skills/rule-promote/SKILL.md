---
name: rule-promote
description: Promote a text-based rule to an automated hook. Use when a rule is repeatedly violated and needs mechanical enforcement. Triggers on "promote rule", "rule to hook", "promote to hook", "automate rule", or "rule promote".
---

## Purpose

Convert a text-based rule into an automated hook that enforces the rule mechanically, without relying on agent memory or human willpower. Text rules are weak enforcement — they depend on the rule being read, understood, and followed in every session. Hooks are strong enforcement — they block or warn regardless of whether the rule was read.

The most common harness failure mode is not the absence of rules — it is rules that exist but are not followed. Promotion closes that gap. When the same rule is violated a second time, the text rule has proven insufficient. The correct response is a hook, not a better-worded sentence.

Promotion does not delete the text rule. The hook enforces; the text rule documents the reasoning. Both coexist. What cannot coexist is a rule that is repeatedly violated without consequence.

---

## When To Use

- After the same rule violation appears 2 or more times in the failure log
- When a rule describes a verification step that is deterministic and mechanically checkable
- When the cost of violating the rule is high: build breakage, false completion report, data destruction, or irreversible state change
- When the weekly review identifies a promotion candidate meeting at least one promotion criterion
- When the user says "promote rule", "rule to hook", "promote to hook", "automate rule", or "rule promote"

---

## Promotion Criteria

A rule is eligible for promotion only if it satisfies all four criteria from `${CLAUDE_PLUGIN_ROOT}/skills/rule-promote/references/promotion-criteria.md`. Evaluate each criterion explicitly and produce a checklist before proceeding to the promotion workflow. Do not skip the evaluation — a hook that should not have been created wastes execution time and creates noise.

### Criterion 1 — Repeated Violation (2+ times)

Check `docs/failure-log.md` for entries where the same rule was violated or the same omission occurred.

- Confirm the violation count is 2 or more with evidence from the failure log (dates and descriptions)
- If the violation count is exactly 1, flag the rule for re-evaluation after the next occurrence — do not promote yet
- If the rule has never been violated but feels important, it does not meet the promotion bar — keep it as a text rule until it is violated

### Criterion 2 — Deterministic Pattern

The rule must describe a behavior that can be checked mechanically, without requiring judgment.

Deterministic examples — these can be enforced by a command hook:
- "Run the test suite before claiming task completion"
- "Do not execute `git push --force` on the main branch"
- "Update docs when API request or response schemas change"
- "Do not leave `console.log` statements in committed code"

Non-deterministic examples — these require model judgment and can only be enforced by a prompt hook:
- "Ensure the solution is architecturally sound"
- "Consider edge cases before submitting"
- "Write clear, descriptive commit messages"

If the rule requires judgment to evaluate, it is not a candidate for a command hook. Route it to a prompt hook type instead, which injects a reminder into the model's context at the trigger event.

### Criterion 3 — Clear Scope (Specific Event Type)

The rule must map to a specific, triggerable event in the hook system. A rule that applies "always" with no event anchor is not hookable.

Common hookable event types:
- `PreToolUse` — before a specific tool is invoked (e.g., before a file write, before a bash command)
- `PostToolUse` — after a specific tool completes (e.g., after a git commit, after a file is edited)
- `Stop` — when a session completion is declared

If the rule does not map cleanly to one event type, it is a process rule enforced by procedure, not by automation. Keep it as a text rule in a skill document. The rule-promote skill only produces hooks — it does not convert text rules into other text rules.

### Criterion 4 — High Impact

The rule, if violated, causes at least one of the following:
- Build breakage or test failures that reach a shared environment
- False completion report (task reported done when it is not)
- Documentation mismatch with actual system behavior
- Data destruction or irreversible state change

Low-impact rules — style preferences, minor formatting inconsistencies, cosmetic issues — do not meet the promotion bar. The overhead of a hook that fires on every session must be justified by the impact of the violation it prevents. Keep low-impact rules as text rules.

---

## Promotion Workflow

### Step 1 — Identify Candidate Rule

State the rule text, its current location, and the violation record before doing anything else.

Output:
```
Rule:       "<exact rule text as it appears in the source document>"
Location:   <file path — e.g., AGENTS.md line 23, or skills/deploy/SKILL.md>
Violations: <n occurrences>
  - <date>: <brief description of the violation>
  - <date>: <brief description of the violation>
```

If the rule cannot be stated as an exact quote, it may not be written down yet. In that case, write the rule text first, add it to the appropriate layer document, and then return to this step.

### Step 2 — Validate Against Promotion Criteria

Evaluate all four criteria explicitly. Do not proceed if any criterion is not met.

Output:
```
Promotion Criteria Evaluation
------------------------------
[x] Criterion 1 — Repeated violation: <n violations found on dates: ...>
[x] Criterion 2 — Deterministic pattern: <yes — can be checked by command / no — requires prompt hook>
[x] Criterion 3 — Clear scope: <event type: PreToolUse / PostToolUse / Stop>
[x] Criterion 4 — High impact: <build breakage / false completion / docs mismatch / data destruction>

Eligible for promotion: YES
```

If any criterion is not met, output the failure and stop:
```
Criterion <n> not met: <reason>
Condition for future eligibility: <what must happen before this rule is eligible>
```

### Step 3 — Determine Hook Type

Select the hook type based on the Criterion 2 evaluation:

**Command hook** — the rule is deterministic and can be checked by a shell command or script:
- Runs a shell command at the trigger event
- Exits non-zero to block the triggering action and surface an error message
- The command must be self-contained, side-effect-free where possible, and produce a clear error message on failure
- Examples: run test suite and check exit code, scan for forbidden string patterns with grep, validate that a required file exists

**Prompt hook** — the rule requires model judgment to evaluate:
- Injects a prompt into the model's context at the trigger event
- Does not block mechanically — raises awareness and requires the model to self-check
- Examples: remind the model to check whether docs need updating, require the model to state remaining risks before completing, prompt for confirmation before destructive operations

If a rule fails Criterion 2 (non-deterministic) but still meets the other three criteria, use a prompt hook. A prompt hook is weaker than a command hook but stronger than a text rule — the model must engage with the check at the trigger event rather than potentially overlooking it.

### Step 4 — Generate Hook Configuration

Write the complete hook entry for `.claude/hooks.json`.

Command hook entry format:
```json
{
  "event": "<PreToolUse | PostToolUse | Stop>",
  "type": "command",
  "command": "<shell command>",
  "description": "<what failure this hook prevents>",
  "matcher": "<tool name or event pattern, if scoped to specific tool>"
}
```

Prompt hook entry format:
```json
{
  "event": "<PreToolUse | PostToolUse | Stop>",
  "type": "prompt",
  "prompt": "<the injected prompt text — imperative, specific, checkable>",
  "description": "<what failure this hook prevents>",
  "matcher": "<tool name or event pattern, if scoped to specific tool>"
}
```

Required fields on every hook:
- `event` — the trigger event type
- `type` — command or prompt
- `description` — explains the failure being prevented, not what the hook does mechanically; this field is required for auditability
- Either `command` or `prompt` depending on type

The `matcher` field is optional but recommended when the rule applies only during specific tool invocations. A hook without a matcher fires on every event of that type — appropriate only for truly universal rules.

### Step 5 — Generate Test Plan

A hook without a test plan cannot be verified as working. Write a three-case test plan for every hook produced by this skill.

Test plan format:
```
Hook Test Plan
--------------
Hook:    <description field from the hook entry>
Event:   <trigger event type>
Type:    <command / prompt>

Test Case 1 — Hook fires on violation
  Setup:    <exact steps to trigger the violation condition>
  Expected: <hook blocks the action with a specific error / prompt appears in context>
  Pass:     <observable evidence — error message text, prompt text, blocked operation>

Test Case 2 — Hook does not fire on compliant behavior
  Setup:    <exact steps that satisfy the rule being enforced>
  Expected: <no interruption — action proceeds normally>
  Pass:     <task completes without hook intervention>

Test Case 3 — Hook failure mode
  Setup:    <simulate the hook command erroring — e.g., command not found, permission denied>
  Expected: <graceful failure — informative error message, does not silently pass>
  Pass:     <error message is clear enough to diagnose the hook failure>
```

---

## Output Format

After completing all steps, produce the full promotion proposal:

```
Rule Promotion Proposal
=======================
Rule:             "<rule text>"
Current location: <file path>
Violation count:  <n>

Promotion criteria: PASS — all 4 criteria met

Hook type:        <command / prompt>
Trigger event:    <PreToolUse / PostToolUse / Stop>
Scope:            <all events of this type / scoped to: tool name>

Hook configuration:
<JSON block>

Text rule disposition after promotion:
  <Keep in skill as rationale documentation | Remove from AGENTS.md | Archive in failure log>

Test plan:
<three-case test plan>

Next step: add the hook entry to .claude/hooks.json and execute the test plan.
```

---

## Reference Files

| File | Used In |
|------|---------|
| `${CLAUDE_PLUGIN_ROOT}/skills/rule-promote/references/promotion-criteria.md` | Step 2 criteria evaluation |
| `docs/failure-log.md` | Step 1 violation record and Step 2 Criterion 1 evidence |
| `.claude/hooks.json` | Step 4 hook configuration target |

---

## Text Rule Disposition After Promotion

After a rule is promoted to a hook, decide what happens to the original text rule. Three options:

**Keep in skill as rationale**: The rule explains the "why" behind the hook. Preferred for important rules.

**Remove from AGENTS.md**: If the hook fully enforces the rule, remove the text rule to reduce context size. Do this only when the hook covers 100% of the violation scenario.

**Archive in failure log**: If the rule was temporary, append a note to `docs/failure-log.md` recording the promotion date.

Never leave a promoted rule in `AGENTS.md` without noting that a hook now enforces it. A rule with no such note implies text-only enforcement, creating confusion during audits.

---

## Common Mistakes

- Promoting a rule with only 1 violation — wait for the second occurrence; one violation may be an anomaly
- Generating a command hook for a non-deterministic rule — command hooks that require judgment cannot be implemented and will either always pass or always fail
- Writing a hook without a `description` field — descriptions are required for auditability; a hook without a description cannot be understood in isolation
- Leaving the promoted rule in `AGENTS.md` without noting that a hook now enforces it — creates confusion during audits
- Skipping the test plan — a hook without a test plan has unknown behavior; untested hooks can silently fail or produce false positives
- Creating a hook without a `matcher` when the rule applies only to specific tools — an unscoped hook fires on every event of that type and creates unnecessary overhead
