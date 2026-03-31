---
name: weekly-review
description: Conduct a weekly harness retrospective to identify repeated failures, promote rules, and clean up stale entries. Use when performing periodic harness maintenance. Triggers on "weekly review", "harness review", "harness retrospective", "weekly harness", or "review harness".
---

## Purpose

Perform a structured retrospective of the harness to keep it lean, current, and effective. A harness that grows without pruning degrades agent performance: rules conflict, context bloats, and enforcement gaps accumulate silently. The weekly review corrects this drift before it becomes dysfunction.

A harness that is never reviewed evolves toward one of two failure states: a bloated global context that buries important rules under noise, or a stale collection of rules that no longer match actual project conditions. Both states cause agents to misinterpret instructions, miss enforcement steps, and waste time on procedure selection. The weekly review is the scheduled maintenance that prevents both.

Each review produces three concrete, actionable outputs: a list of promotion candidates (text rules that have been violated enough times to warrant mechanical enforcement), a cleanup list (stale, duplicate, or misplaced entries), and a pattern analysis of the failure log that identifies which rule gaps remain unaddressed. The review proposes; the human confirms and executes.

The review is not a planning session. It does not introduce new rules or skills. It evaluates what the harness currently contains against what actually happened during the week, and surfaces the gap between the two.

---

## When To Use

- At the end of each week of active development, as scheduled recurring maintenance
- When the harness feels slow, contradictory, or consistently ignored by agents
- After a burst of failure absorption that may have introduced redundancy or conflict
- When `AGENTS.md` has grown significantly since the last review
- When the user says "weekly review", "harness review", "harness retrospective", "weekly harness", or "review harness"

---

## Workflow

### Step 1 — Read Current State

Load the following files before doing any analysis. Do not proceed without reading all of them. Analyzing from memory rather than current file contents produces inaccurate proposals.

- `docs/failure-log.md` — the recurring failure ledger; primary data source for the review
- `AGENTS.md` — current constitutional rules; check line count and rule distribution
- `.claude/hooks.json` — current automated enforcement configuration; check for gaps
- All files under `skills/` — current contextual execution documents; check for staleness and overlap
- `docs/glossary/README.md` — terminology registry; check for undefined terms that appeared in recent failures

각 하네스 파일의 마지막 수정일을 git으로 확인한다:
`git log --format=%ai -1 -- <file>`

`.harness.json`의 `staleness_weeks` 값(기본값: 8주)보다 오래된 파일은 staleness 후보로 표시한다.

Record the current line count of `AGENTS.md`. If it exceeds 60 lines, that is a finding in itself — flag it as a high-priority cleanup item before any other analysis.

### Step 2 — Extract Repeated Failure Patterns

Scan `docs/failure-log.md` for entries where the same failure description or same cause category number appears more than once. The failure log is the ground truth of what the harness failed to prevent.

For each repeated pattern, record:
- The failure description and how many times it appears
- Whether an absorption action was previously taken (check the Absorption Action column)
- Whether the failure recurred after a prior absorption — these are "incomplete absorptions" and require escalated response

Group patterns by cause category to reveal systemic gaps:

| Category | If repeated, indicates |
|----------|----------------------|
| 1 — Global rule absence | AGENTS.md is missing a universally needed rule |
| 2 — Task procedure absence | A skill is missing or its steps are incomplete |
| 3 — Automation absence | A hook needs to be created or an existing hook is insufficient |
| 4 — Terminology mismatch | A glossary term is missing or being used inconsistently across documents |
| 5 — Context pollution | AGENTS.md or a skill document is too long and burying its own rules |
| 6 — Authority boundaries | Roles or decision ownership between agents and humans is ambiguous |

Any cause category appearing 3+ times in the failure log signals a structural gap in that layer, not just individual failures.

### Step 3 — Identify Promotion Candidates

A promotion candidate is any text-based rule that should become an automated hook or a dedicated skill. The promotion criteria come from Appendix C.2 of the Harness Engineering Manual:

- Same omission occurs 2+ times in the failure log → promote to hook candidate
- Verification step that humans or agents frequently forget → promote to hook candidate
- Rule whose violation has high downstream cost (build breakage, false completion, data loss) → promote to hook candidate
- Rule that directly affects completion report quality → promote to hook candidate

For each candidate, record all three of the following:

1. **Current rule text and location** — exact quote and file path
2. **Recommended promotion target** — hook (for deterministic violations) or new skill (for procedural gaps)
3. **Estimated effort** — low (hook configuration only), medium (hook plus test plan), high (new skill required)

Do not recommend promotion unless at least one criterion is met with evidence from the failure log. Promotion without evidence is speculation.

### Step 4 — Propose Cleanup Actions

Apply the cleanup criteria from Manual section 10.1. Flag entries for deletion, abbreviation, movement, or archival if any of the following conditions are met:

**8-week staleness**: The rule or document has not been referenced, updated, or triggered in 8+ weeks. Staleness indicates the problem the rule was solving may no longer be active, or the rule is not being read. Check whether the problem is still relevant before flagging for deletion.

**Duplicate rule**: The same requirement appears with equivalent meaning in two or more files. Duplicates waste context space and create maintenance burden — when one copy is updated, the other becomes a contradiction. Recommend keeping the copy at the most layer-appropriate location (specific rules in skills, universal rules in AGENTS.md).

**Resolved temporary rule**: The rule was added to address a temporary condition (e.g., "during migration, always backup before running") and that condition no longer applies. Flag for deletion with the date the condition resolved.

**Wrong scope**: A detailed, conditional, or task-specific rule is sitting in `AGENTS.md` when it belongs in a skill or runbook. This is the most common harness anti-pattern: AGENTS.md grows because it is the easiest place to add rules. Any rule in AGENTS.md that does not apply to all tasks in all contexts is wrong-scoped.

For each cleanup candidate, specify all three of:
- File path and the specific rule or section
- Cleanup action: delete, abbreviate, move to skill, or archive
- Reason for the action using one of the four criteria names above

Do not execute cleanup actions during the review session. Produce proposals only. The human reviews and confirms before any changes are made. Unilateral cleanup without confirmation can remove rules that appear stale but are actually load-bearing.

### Step 5 — Generate Review Report

Write the review report using the template at `${CLAUDE_PLUGIN_ROOT}/skills/weekly-review/references/review-template.md`.

The report must contain all five sections. Omitting a section is not acceptable even if the section is empty — use "None found this week" as the entry for empty sections so it is clear the check was performed.

1. **Repeated Failures** — patterns found in the failure log with occurrence counts and cause category
2. **Incomplete Absorptions** — failures that recurred after a previous absorption attempt, with recommended stronger action
3. **Promotion Candidates** — rules meeting at least one promotion criterion, with target and effort estimate
4. **Cleanup List** — stale, duplicate, or misplaced entries with proposed action and reason
5. **Harness Changes Executed** — any changes made during this session (almost always none, pending human confirmation)

---

## Review Report Format

Use the Appendix D template from the Harness Engineering Manual as the base:

```
# Weekly Harness Review — <YYYY-MM-DD>

## Repeated Failures
- Failure: <description>
  Category: <number and name>
  Frequency: <n occurrences, date range>
  Prior absorption: <yes/no — what was done>

## Incomplete Absorptions
- Failure: <description>
  Previous action: <what was absorbed and when>
  Recurrence: <date and context of recurrence>
  Recommended next action: <stronger layer or different approach>

## Promotion Candidates
- Rule: "<current rule text>"
  Location: <file path>
  Target: <hook type / new skill name>
  Criteria met: <which of the 4 criteria apply>
  Effort: <low / medium / high>

## Cleanup List
- Entry: <rule text or section title>
  Location: <file path>
  Action: <delete / abbreviate / move / archive>
  Reason: <staleness / duplicate / resolved / wrong scope>

## Harness Changes Executed
- <none — pending human confirmation>
  OR
- <description of change made, file path, reason>
```

---

## Cleanup Criteria Reference (Section 10.1)

| Criterion | Threshold | Recommended Action |
|-----------|-----------|-------------------|
| Staleness | Not referenced or updated in 8+ weeks | Flag for deletion after confirming problem is resolved |
| Duplicate | Same content in 2+ files | Keep one copy at the correct layer; flag others for deletion |
| Resolved temporary | Original condition no longer applies | Delete with note in failure log of when it was resolved |
| Wrong scope | Conditional rule in global `AGENTS.md` | Move to appropriate skill or runbook |

Never delete entries from `docs/failure-log.md`. The failure log is append-only. Old entries are evidence of real failures and the history of absorption attempts. Deleting them destroys the pattern analysis needed for future reviews.

---

## Reference Files

| File | Used In |
|------|---------|
| `${CLAUDE_PLUGIN_ROOT}/skills/weekly-review/references/review-template.md` | Step 5 report generation |
| `docs/failure-log.md` | Step 2 pattern extraction — primary data source |
| `AGENTS.md` | Step 3 and Step 4 rule analysis |
| `.claude/hooks.json` | Step 3 promotion candidate gap analysis |
| `skills/*/SKILL.md` | Step 3 and Step 4 skill staleness and overlap analysis |

---

## Connection to the Failure Absorption Cycle

The weekly review and the failure-absorb skill are complementary. The failure-absorb skill handles individual failures in real time. The weekly review handles patterns across multiple failures over time. A single failure may not justify promotion to a hook; a pattern of the same failure three weeks in a row always does.

When the weekly review identifies an incomplete absorption — a failure that recurred after a prior absorption attempt — invoke the failure-absorb skill for that specific failure with the additional context that a prior absorption was attempted and failed. This escalates the absorption to a stronger layer: if a text rule was added but the violation recurred, a hook is required.

---

## Common Mistakes

- Executing cleanup actions immediately without presenting proposals to the human first — unconfirmed deletions can remove load-bearing rules
- Marking a rule as stale based on age alone without confirming the underlying problem is resolved — a rule can be old and still necessary
- Proposing promotion without citing which of the 4 promotion criteria the candidate meets — promotion proposals without evidence are not actionable
- Skipping Step 1 (reading current state) and analyzing from memory — current file contents may differ significantly from last week
- Writing a review report that lists patterns without recommending a specific action for each — every finding must have a proposed action
- Deleting entries from `docs/failure-log.md` — the log is append-only and its history is the foundation of pattern analysis
- Reporting "None found" for every section without showing evidence the checks were actually performed
