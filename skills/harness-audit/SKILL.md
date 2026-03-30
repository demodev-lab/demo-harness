---
name: harness-audit
description: Audit the harness for bloat, duplication, and decay. Use when checking harness health or when the harness feels slow or contradictory. Triggers on "harness audit", "audit harness", "check harness bloat", "harness health", or "harness bloat".
---

## Purpose

Diagnose the health of a harness by detecting bloat, duplication, staleness, conflicts, and anti-patterns. A harness that has grown without pruning exhibits measurable symptoms: agents interpret rules with conflicts, global documents become excessively long, the same rule appears in multiple files, pre-completion verification is repeatedly missed despite being documented, and time is wasted on procedure and tool selection that should be automatic.

These symptoms appear gradually. No single rule addition is catastrophic. The harness degrades over months of incremental additions without corresponding deletions. The audit makes the degradation visible so it can be corrected before it becomes dysfunction.

The audit produces a health report with severity ratings and recommended actions. It does not execute changes. Its role is diagnostic: produce evidence, assign severity, and recommend remediation. The human decides what to act on. Executing changes during an audit conflates two separate operations and risks removing rules based on incomplete analysis.

The primary benchmark for this audit is Manual section 10.2's list of harness performance warning signs. Each check below maps directly to one or more of those warning signs.

---

## When To Use

- When the harness feels slow or agents frequently misinterpret or conflict on rules
- When there is suspicion of rule duplication or contradiction across documents
- Before a quarterly cleanup to establish a current-state baseline
- After a large batch of failure absorptions to check whether new rules created redundancy
- When `AGENTS.md` has grown noticeably since the last review
- When the user says "harness audit", "audit harness", "check harness bloat", "harness health", or "harness bloat"

---

## Pre-Audit File Load

Load all harness files before beginning any check. Do not perform checks from memory.

Required reads:
- `AGENTS.md` and `CLAUDE.md` (Layer A)
- All files under `skills/` (Layer B)
- `.claude/hooks.json` (Layer C)
- All files under `docs/` (Layer D)
- `docs/failure-log.md` (Layer D — failure history)
- `docs/glossary/README.md` (Layer D — terminology)

Record the line count of `AGENTS.md` before beginning Check 1. This number determines whether the first finding is Critical.

---

## Audit Checks

Run all six checks in order. Each check produces findings with severity ratings. A finding with no recommended action is incomplete — every finding must include a specific remediation step.

### Check 1 — Rule Count and Distribution

Count rules and documents across all four layers to assess whether the harness is correctly distributed or collapsed into a single layer.

Layer A (AGENTS.md and CLAUDE.md):
- Count total lines in AGENTS.md
- Count distinct rules (each imperative statement is one rule)
- Record whether rules are universal or task-specific

Layer B (skills/):
- Count skill files
- Note which task types have dedicated skills and which do not

Layer C (.claude/hooks.json):
- Count hook entries
- Note whether any hook entries are missing a `description` field

Layer D (docs/):
- Count document files
- Note whether a failure log, glossary, and architecture record exist

Severity thresholds:
- **Critical**: `AGENTS.md` exceeds 60 lines
- **High**: distinct rule count in `AGENTS.md` exceeds 15
- **Medium**: Layer C has zero hook entries — all enforcement is text-only
- **Medium**: Layer B has fewer than 2 skills for a project with known repetitive task types
- **Low**: Layer C hook entries missing `description` fields

### Check 2 — Duplication Detection

Scan all harness files for rules, requirements, or prohibitions that express the same meaning in two or more locations.

Equivalence criteria for duplication:
- Same behavioral requirement written in different words
- Same forbidden action listed in both `AGENTS.md` and a skill's "Common Mistakes" section
- Same verification step described in both a skill procedure and a hook's description
- Same term defined in both the glossary and inline in a skill document

For each duplicate found, record:
- Both file paths containing the duplicate
- The duplicate content (exact quotes from both locations)
- The recommended resolution: which copy to keep, which to remove

Recommendation rule: keep the copy at the most layer-appropriate location. Universal requirements belong in `AGENTS.md`. Task-specific requirements belong in skills. Mechanical enforcement belongs in hooks. Reference definitions belong in the glossary.

Severity thresholds:
- **High**: a rule appears in 3 or more files
- **Medium**: a rule appears in exactly 2 files

### Check 3 — Staleness Check

Evaluate every harness file for evidence of active use. A rule that has not been relevant for 8+ weeks is either solving a resolved problem or being ignored — both are findings.

Check the last-modified date of each file. For rules without modification history, check the failure log for references to the rule or the task type it covers.

Flag as **High**: any rule or document not updated in 8+ weeks where the problem it addresses is confirmed resolved.
Flag as **Medium**: any skill file not referenced in the failure log or session notes in the past 8 weeks — may indicate the skill exists but agents are not using it.
Flag as **Low**: any glossary entry for a term that does not appear in current code, documentation, or agent sessions.

Exception: do not flag `docs/failure-log.md` for staleness under any conditions. The failure log is append-only evidence and its age is irrelevant to its validity.

### Check 4 — Conflict Detection

Identify rules that directly contradict each other across harness files. Conflicting rules force agents to make arbitrary choices, which produces inconsistent behavior. This is the failure mode described in Manual section 10.2 as "agent frequently interprets rules with conflicts."

Common conflict patterns to check explicitly:
- `AGENTS.md` says "always run tests before completion" but a skill's steps do not include a test-run step
- `AGENTS.md` prohibits a command (e.g., `git push --force`) that a skill explicitly instructs to run
- Two skills cover overlapping task types and give different instructions for the same decision point
- A skill defines a term differently from the glossary definition of the same term

For each conflict found, record:
- Both conflicting statements with exact quotes and file paths
- The recommended resolution: which statement takes precedence (Layer A overrides Layer B, Layer B overrides ad hoc procedure) or how to reconcile if both are valid

Severity thresholds:
- **Critical**: conflict exists between `AGENTS.md` and a hook configuration — constitutional rules and automated enforcement are misaligned
- **High**: conflict exists between two skills covering overlapping task types
- **Medium**: a skill's procedural steps contradict a glossary definition

### Check 5 — Context Pollution Check

Measure the specificity and length of global documents. Context pollution is the failure mode where important rules are buried in long documents and missed during execution. It is also how AGENTS.md exceeds its 60-line limit — by accumulating rules that belong in skills.

Check each of the following explicitly:

- Does `AGENTS.md` contain conditional branching logic (if/else rules, rules that apply only under certain conditions)?
- Does `AGENTS.md` contain detailed step-by-step procedures that belong in a skill?
- Does `AGENTS.md` contain a directory tree, file map, or listing of project structure?
- Does any single skill file exceed 400 lines?
- Does any document contain a rule duplicated verbatim from the Harness Engineering Manual?

Severity thresholds:
- **Critical**: `AGENTS.md` contains conditional branching logic or feature-specific instructions
- **High**: `AGENTS.md` contains detailed multi-step procedures
- **High**: any skill file exceeds 400 lines
- **Medium**: `AGENTS.md` contains a directory tree or file map
- **Low**: verbatim duplication of manual content in project harness files

### Check 6 — Anti-Pattern Scan

Check for each of the 7 prohibited patterns from Manual section 11. Reference `${CLAUDE_PLUGIN_ROOT}/skills/harness-audit/references/anti-patterns.md` for detection detail.

| # | Anti-Pattern | Detection Signal |
|---|--------------|-----------------|
| 1 | Only lengthening the global prompt with each failure | `AGENTS.md` line count > 60, or more than 15 distinct rules |
| 2 | Assuming humans will always remember | No entries in `.claude/hooks.json` |
| 3 | Pasting directory trees into documents | Directory listing content found in any harness file |
| 4 | Covering small problems with new abstractions | Skills that cover one-time tasks with no reuse potential |
| 5 | Separating documentation from operating contracts | Skills referencing docs/ files that do not exist |
| 6 | Abusing sub-agents as role decoration | Sub-agent instructions in skills without defined scope boundaries or output contracts |
| 7 | Reporting complete without verification | No completion checklist in docs/, or `.claude/hooks.json` has no completion gate |

Flag each confirmed anti-pattern as **High**. Do not flag suspected anti-patterns — only confirmed ones with evidence.

---

## Deep Analysis Delegation

For projects with more than 20 harness files or more than 100 total rules across all layers, delegate the audit to the `harness-auditor` agent. Provide:

- Full contents of `AGENTS.md`
- Full list of all skill file paths with line counts
- Full contents of `.claude/hooks.json`
- Full contents of `docs/failure-log.md`
- The six checks above as the audit specification

Receive the agent's findings, validate them against the files, and incorporate into the health report before presenting to the human.

---

## Health Report Format

```
Harness Health Report — <YYYY-MM-DD>
======================================
Overall Status: <Healthy / Degraded / Critical>

Summary
-------
Total findings: <n>
  Critical: <n>
  High:     <n>
  Medium:   <n>
  Low:      <n>

Findings
--------
[CRITICAL] <finding title>
  Check:    <which check produced this finding>
  File:     <file path>
  Evidence: <specific rule text, line count, or metric>
  Action:   <specific recommended remediation>

[HIGH] ...
[MEDIUM] ...
[LOW] ...

Recommended Next Steps (top 3)
-------------------------------
1. <highest priority action — address all Critical findings first>
2. <second priority action>
3. <third priority action>
```

Overall Status determination:
- **Critical**: one or more Critical findings exist
- **Degraded**: no Critical findings, but 2 or more High findings exist
- **Healthy**: zero Critical findings and fewer than 2 High findings

---

## Reference Files

| File | Used In |
|------|---------|
| `${CLAUDE_PLUGIN_ROOT}/skills/harness-audit/references/warning-signs.md` | Checks 1–5 severity calibration |
| `${CLAUDE_PLUGIN_ROOT}/skills/harness-audit/references/anti-patterns.md` | Check 6 anti-pattern detection |

The five warning signs from Manual section 10.2 map directly to checks:

- "Agent frequently interprets rules with conflicts" → Check 4 (conflict detection)
- "Global documents are excessively long" → Check 1 (rule count) and Check 5 (context pollution)
- "Same rule is duplicated across multiple documents" → Check 2 (duplication detection)
- "Time wasted on tool or procedure selection" → Check 1 (distribution) and Check 3 (staleness)
- "Essential pre-completion verification frequently missed" → Check 6, anti-pattern 7

---

## Common Mistakes

- Executing recommended changes during the audit instead of reporting — the audit role is diagnostic; changes are a separate operation
- Flagging `docs/failure-log.md` as stale — the failure log is append-only evidence and is exempt from all staleness checks
- Marking a rule as a duplicate without confirming the two instances have genuinely equivalent meaning — superficial similarity is not duplication
- Reporting "Healthy" status when no hooks exist — zero automated enforcement is a structural gap regardless of how well-written the text rules are
- Skipping Check 6 (anti-pattern scan) because no obvious symptoms are present — hidden anti-patterns cause future degradation and are the point of the check
- Producing findings without remediation steps — every finding must include a specific recommended action
