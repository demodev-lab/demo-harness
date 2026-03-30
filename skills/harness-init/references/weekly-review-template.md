# Weekly Harness Review Template

Use this template every week (or at the end of a development sprint) to review failure patterns and make structural improvements to the harness. Copy this template into a new dated file or fill it in-place and archive.

This review exists because a harness that is never pruned becomes a liability. Long, conflicting, duplicated rules decrease agent performance. The review has two equal goals: absorb new failures, and remove stale weight.

---

## Review: [YYYY-MM-DD]

Reviewer: [Name or "agent-assisted"]
Period covered: [start date] to [end date]
Failure log entries reviewed: [count]

---

## Section 1: Repeated Failures

List every failure pattern that appeared more than once in the period. Failures that appear once may be one-offs; failures that appear twice or more are structural gaps.

For each repeated failure:

```
### Failure: [Short title]
- **Failure**: [Describe the behavior that went wrong]
- **Cause**: [Which of the 6 categories applies: global rule absence / specific task procedure absence / tool/verification automation absence / terminology/documentation mismatch / excessive context pollution / unclear authority/responsibility boundaries]
- **Frequency**: [How many times in this period]
- **Pattern**: [Is this a new pattern or a recurrence of a previously logged failure?]
```

Example:
```
### Failure: Agent skips docs update when changing API response shape
- **Failure**: Agent modifies the response body of an endpoint but does not update the OpenAPI spec or the related docs page.
- **Cause**: Specific task procedure absence — the API endpoint skill does not explicitly list "update OpenAPI spec" as a step.
- **Frequency**: 3 times this week
- **Pattern**: Recurrence — first appeared 2024-11-07, partial fix added then, still recurring.
```

---

## Section 2: Harness Changes

Based on the repeated failures above, decide what structural changes to make. Each decision should map to exactly one failure pattern from Section 1.

### Promote to AGENTS.md rule

List rules that should be added to or strengthened in AGENTS.md (Layer A). Only include rules that apply universally to every task — not conditional rules.

```
- Rule to add: "[exact rule text]"
  Reason: [Which failure this prevents]
  Replaces/supplements: [existing rule, if any]
```

### Create skill

List new skills (Layer B) that should be created. Each skill covers one specific, repeatable work type.

```
- Skill name: [skill-name]
  Trigger: [When should this skill be loaded?]
  Covers: [What work type does this skill define procedure for?]
  Source failure: [Which failure from Section 1 prompted this?]
```

### Add hook

List new hooks (Layer C) that should be created. Hooks are warranted when a text rule has been violated 2+ times.

```
- Hook name: [hook-name]
  Type: [prompt (injected into context) or command (runs a script)]
  Trigger: [pre-commit / pre-push / completion / other]
  Enforces: [What behavior does this mechanically block or require?]
  Source failure: [Which failure from Section 1 prompted this?]
```

### Update glossary or docs

List terminology or documentation that needs to be created or corrected.

```
- Term/doc: [name]
  Change: [add / update / clarify]
  Reason: [Which failure this prevents]
```

---

## Section 3: Cleanup

Review all existing harness components for staleness and redundancy. A harness that only grows eventually collapses under its own weight.

Apply these cleanup criteria:
- Rules unused for 8+ weeks → candidate for removal
- Duplicate rules with identical content across documents → merge to one location
- Temporary rules whose original problem no longer occurs → remove
- Detailed rules in global scope that belong in a skill → relocate

### Remove stale rule

```
- Rule: "[exact rule text]"
  Location: [AGENTS.md / skill name / hook name]
  Reason for removal: [unused 8+ weeks / problem no longer occurs / moved to skill]
  Last confirmed relevant: [date or "unknown"]
```

### Merge duplicate docs

```
- Duplicate: [document A] and [document B] contain the same rule
  Action: [Keep A, remove B / merge into C]
  Rule to preserve: "[exact text]"
```

### Archive obsolete notes

```
- Document: [filename]
  Reason: [one-time note / resolved incident / superseded by newer doc]
  Archive location: [docs/archive/ or delete]
```

---

## Section 4: Next Week Targets

List 1-3 specific harness improvements to complete before the next review. Keep this short — incomplete lists carry over and create debt.

```
1. [Action] by [date]
2. [Action] by [date]
3. [Action] by [date]
```

---

## Review Completion Checklist

Before closing this review:
- [ ] All Section 1 failures have a Section 2 response (or explicitly deferred with reason)
- [ ] All Section 3 cleanup items have been acted on (not just listed)
- [ ] AGENTS.md is still within 40-60 lines after changes
- [ ] Failure log entries from this period are marked as absorbed or pending
- [ ] Next week targets are specific and actionable
