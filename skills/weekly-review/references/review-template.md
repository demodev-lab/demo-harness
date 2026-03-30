# Weekly Harness Review Template

This is the full weekly review template combining Appendix D's structure with section 10.1's cleanup criteria. Run this review at the end of every week or sprint. The review has two equal goals: absorb new failures into the harness, and prune stale rules that are adding noise.

A review that only adds rules without removing stale ones will eventually degrade harness performance. Both halves are mandatory.

---

## Review: [YYYY-MM-DD]

Reviewer: [Name or "agent-assisted"]
Period covered: [start date] to [end date]
Failure log entries reviewed: [count]
Active skills reviewed: [count]
AGENTS.md line count at start of review: [N]

---

## Section 1: Repeated Failures

Review all failure log entries from the period. List every failure pattern that appeared more than once. Single-occurrence failures are recorded in the log but may not require immediate harness action — document them and watch for recurrence.

For each repeated failure, complete this block:

```
### Failure: [Short title]

- **Failure**: [Describe the exact behavior that went wrong]
- **Category**: [One of the 6 categories:
    1. Global rule absence
    2. Specific task procedure absence
    3. Tool/verification automation absence
    4. Terminology/documentation mismatch
    5. Excessive context pollution
    6. Unclear authority/responsibility boundaries]
- **Frequency**: [How many times this period]
- **Pattern**: [New this period / Recurrence from [date] / Partially addressed on [date]]
- **Root cause**: [1-2 sentences on why the harness did not prevent this]
```

Example:
```
### Failure: Agent modified shared utility without checking all callers

- **Failure**: Agent refactored a shared date formatting function and updated the direct callers it found, but missed 4 indirect callers that broke silently. Tests did not cover those paths.
- **Category**: 2 — Specific task procedure absence (no refactoring skill defines "find all callers" as a required step)
- **Frequency**: 2 times this period
- **Pattern**: New this period
- **Root cause**: The refactoring skill does not exist. Agents improvise the procedure and skip impact-scope analysis.
```

---

## Section 2: Harness Changes

For each repeated failure in Section 1, decide which structural change to make. Leave the "Source failure" field to trace each change back to its origin.

If a failure has no harness response yet (investigating, deferring), state that explicitly with a reason and a target date.

### Promote to AGENTS.md rule

Rules added here must apply universally to every task. If a rule contains "when doing X", it does not belong here — put it in a skill instead.

```
- Rule: "[exact rule text to add]"
  Replaces/supplements: [existing rule text, if any]
  Source failure: [Section 1 failure title]
  Keeps AGENTS.md within 60 lines: [yes / no — if no, which rule is being removed to make room?]
```

### Create skill

New skills (Layer B) for work types that lack procedure coverage.

```
- Skill name: [skill-name]
  Trigger condition: [When should this skill be loaded? Be specific.]
  Work type covered: [What task does this skill define procedure for?]
  Key steps to include: [The specific steps missing that caused the failure]
  Source failure: [Section 1 failure title]
```

### Add hook

New hooks (Layer C) for violations that have occurred 2+ times or have high failure cost.

```
- Hook name: [hook-name]
  Type: [prompt / command]
  Trigger: [pre-commit / pre-push / at-completion / on-file-change]
  Enforces: [Specific behavior mechanically blocked or required]
  Script or prompt text: [Brief description or draft]
  Source failure: [Section 1 failure title]
  Promotion criteria met: [Criterion 1 (2+ violations) / Criterion 2 (frequently forgotten) / Criterion 3 (high cost) / Criterion 4 (completion quality)]
```

### Update glossary or docs (Layer D)

Terminology fixes, outdated document updates, new glossary entries.

```
- Item: [term name or document path]
  Change: [add / update / correct / archive]
  New content or correction: [Brief description]
  Prohibited synonyms to add: [If terminology issue]
  Source failure: [Section 1 failure title]
```

### Deferred items

Failures that require more investigation before a harness change can be made.

```
- Failure: [Section 1 failure title]
  Reason for deferral: [What is not yet understood]
  Target resolution: [Date or milestone]
  Owner: [Who will investigate]
```

---

## Section 3: Cleanup

Review all existing harness components against section 10.1's four cleanup criteria. Cleanup is not optional — a harness that only grows eventually collapses. Run this section even when no failures occurred.

### Cleanup Criterion 1: Rules unused for 8+ weeks

For each candidate, ask: "Was this rule relevant to any task in the last 8 weeks?" If no, it is a removal candidate.

```
- Rule: "[exact rule text]"
  Location: [AGENTS.md line N / skill name / hook name]
  Last relevant: [date or "unknown"]
  Action: [remove / abbreviate / move to Layer D archive]
  Risk if removed: [none / low — describe if any]
```

### Cleanup Criterion 2: Duplicate rules with same content

Rules that appear in two or more documents with substantially the same content.

```
- Duplicate: "[rule text]" appears in [document A] and [document B]
  Canonical location: [Keep in A / Keep in B / Merge into C]
  Action: Remove from [non-canonical location]
  Notes: [Any difference between the two versions that needs resolving]
```

### Cleanup Criterion 3: Temporary rules whose original problem no longer occurs

Rules that were added as responses to specific incidents, bugs, or environmental problems that have since been resolved.

```
- Rule: "[exact rule text]"
  Location: [document name]
  Original problem: [What incident or bug prompted this rule]
  Status of original problem: [Resolved on [date] / Replaced by [hook/layer C] / No longer applicable because...]
  Action: [remove / archive in failure log / convert to historical note]
```

### Cleanup Criterion 4: Detailed rules in global scope that belong in a skill

Rules in AGENTS.md that are conditional, multi-step, or task-specific.

```
- Rule: "[exact rule text]"
  Why it does not belong in global scope: [Contains condition / Is multi-step / Only applies to task type X]
  Move to: [skill name — create if does not exist]
  Action: Remove from AGENTS.md after confirming skill covers it
```

---

## Section 4: Post-Cleanup AGENTS.md Audit

After making Section 3 changes, audit the current state of AGENTS.md.

- Current line count after cleanup: [N]
- Target: 40-60 lines
- Lines over target (if any): [N — list specific rules still flagged for extraction]
- All remaining rules apply universally to every task: [yes / no — list exceptions]
- The 10 operating principles are represented: [yes / partially — list which are missing]

The 10 operating principles that must be reflected in AGENTS.md:
1. All development proceeds alongside documentation.
2. When structure, contracts, policies, or APIs change, update related docs immediately.
3. Prioritize existing patterns, common modules, and common terminology.
4. Do not leave temporary code, duplicate code, or ad hoc rules as new standards.
5. Before changes, check impact scope; after changes, verify actual impact is reflected.
6. Completion claims are backed by verification logs or test results.
7. Failures are absorbed into prevention rules, not just manually fixed.
8. When new concepts emerge, first define their name and meaning.
9. Prefer short global directives + detailed documents at the point of need over long global directives.
10. Agents prioritize evidence over assumptions; humans prioritize system improvement over exceptions.

---

## Section 5: Anti-Pattern Check

Quickly scan for the 7 anti-patterns. Mark each as "clear" or "detected — [brief note]".

1. Only lengthening global prompt: [clear / detected]
2. Assuming humans will remember: [clear / detected]
3. Directory trees pasted in documents: [clear / detected]
4. New abstractions for small problems: [clear / detected]
5. Docs separated from operating contracts: [clear / detected]
6. Sub-agents used as role decoration: [clear / detected]
7. Completing without verification: [clear / detected]

For any "detected" item, add to Section 2 (Harness Changes) or Section 3 (Cleanup) as appropriate.

---

## Section 6: Performance Warning Signs Check

Check each warning sign from section 10.2. Mark as "clear" or "detected — [brief note]".

1. Agent frequently interprets rules with conflicts: [clear / detected]
2. Global documents excessively long (AGENTS.md > 60 lines): [clear / detected — current: N lines]
3. Same rule duplicated across documents: [clear / detected]
4. Time wasted on tool or procedure selection: [clear / detected]
5. Essential verification still frequently missed: [clear / detected]

For any "detected" item, add a response in Section 2 or 3.

---

## Section 7: Next Week Targets

List 1-3 specific, actionable harness improvements to complete before the next review. Incomplete targets carry over and create debt — keep the list short enough to complete.

```
1. [Specific action] by [date]
   Owner: [name]
   Blocking: [what cannot happen until this is done, if anything]

2. [Specific action] by [date]
   Owner: [name]

3. [Specific action] by [date]
   Owner: [name]
```

---

## Review Completion Checklist

Before closing this review:

- [ ] All Section 1 repeated failures have a Section 2 response or explicit deferral with date
- [ ] All four cleanup criteria in Section 3 were checked (not just one or two)
- [ ] AGENTS.md line count is within 40-60 lines after cleanup
- [ ] Failure log entries from this period have "Absorbed-to" filled in or marked "pending with target date"
- [ ] Section 4 AGENTS.md audit is complete
- [ ] Section 5 anti-pattern check is complete
- [ ] Section 6 warning signs check is complete
- [ ] Next week targets are specific, actionable, and owned
- [ ] This review document is committed to `docs/weekly-reviews/[YYYY-MM-DD].md`

---

## Archive: Previous Review Summary

Link to the previous review and note whether its targets were completed:

- Previous review: `docs/weekly-reviews/[previous date].md`
- Target 1: [completed / deferred — reason]
- Target 2: [completed / deferred — reason]
- Target 3: [completed / deferred — reason]

Persistent deferrals (same target deferred 2+ reviews) must be either escalated to a blocking priority or explicitly abandoned with documented reason.
