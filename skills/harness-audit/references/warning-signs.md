# Warning Signs and Cleanup Criteria

A harness that keeps growing without pruning eventually degrades agent performance. This document defines the signals that indicate the harness has become bloated (section 10.2) and the criteria for when rules, documents, and hooks should be removed or consolidated (section 10.1).

Use this document during weekly harness reviews and when running the harness-audit skill.

---

## Part 1: Performance Warning Signs (Section 10.2)

These five signals indicate the harness has become a liability rather than an asset. When any of these appear, treat it as a harness health incident requiring immediate action — not a model quality issue.

---

### Warning Sign 1: Agent Frequently Interprets Rules with Conflicts

**Description**: The agent produces behavior that appears to follow one rule while violating another. Or the agent asks for clarification about conflicting instructions more than once per session.

**Severity**: High

**Root cause**: Rules in different documents (typically AGENTS.md and a skill, or two skills) make contradictory demands for the same situation. Or conditional rules have been placed in AGENTS.md where they conflict with unconditional rules.

**Detection heuristics**:
- Agent says "I followed rule X but it conflicts with rule Y" — or produces output that demonstrates this confusion
- Review AGENTS.md for any rule that contains "unless", "except when", or "if X then" — these are conditional rules that belong in Layer B, not Layer A
- Search for the same concept across AGENTS.md and all skills — check whether any two documents make different demands for it
- Count how many times per session the agent has asked a clarifying question about which rule to follow

**Recommended action**:
1. Identify the conflicting rules specifically
2. Move conditional rules from AGENTS.md to the relevant skill
3. If two skills conflict: determine which takes precedence and document it in both
4. Reduce AGENTS.md to universal rules only — if a rule has conditions, it does not belong there

---

### Warning Sign 2: Global Documents Are Excessively Long

**Description**: AGENTS.md exceeds 60 lines, or CLAUDE.md exceeds the project's established limit.

**Severity**: Medium-High

**Root cause**: Over time, every failure response adds a line to AGENTS.md. Without weekly pruning, the file accumulates rules that are conditional, task-specific, or no longer relevant. A 200-line AGENTS.md is not twice as effective as a 100-line one — it is less effective because agents cannot reliably track 200 rules simultaneously.

**Detection heuristics**:
- Run `wc -l AGENTS.md` — alert if over 60 lines
- Review each rule: would it apply to a completely unrelated task type? If not, it is conditional and belongs in Layer B
- Look for rules added in the last 4 weeks — were they added as first responses to single failures, or do they represent established patterns?
- Check for rules that contain more than 2 clauses — long rules are often multiple rules combined

**Recommended action**:
1. Audit AGENTS.md line by line
2. Move any conditional rule ("when doing X", "if Y applies") to the relevant skill
3. Remove rules that duplicate the 10 operating principles — the principles should be in AGENTS.md, not re-stated in different words
4. Target: 40-60 lines, all universal rules

---

### Warning Sign 3: Same Rule Duplicated Across Multiple Documents

**Description**: The same rule, or a substantially similar rule, appears in AGENTS.md and one or more skills, or in two different skills.

**Severity**: Medium

**Root cause**: Rules are added reactively without checking whether they already exist elsewhere. Or a rule was added to AGENTS.md and then again to a skill "just to be sure." Duplication creates drift — when the rule needs to change, it is updated in one place but not all places, creating contradictions.

**Detection heuristics**:
- Search for key phrases from AGENTS.md rules across all skill files: `grep -r "destructive" skills/` — any hits that substantially repeat what AGENTS.md already says
- Look for completion-related rules in skills — the completion gate belongs in one place (AGENTS.md and Layer C hook), not re-stated in each skill
- Check whether the glossary defines terms that are also defined inline in AGENTS.md or skills
- During weekly review, read AGENTS.md and each active skill side by side for 10 minutes — duplication is usually visible immediately

**Recommended action**:
1. Identify the canonical location for the duplicated rule (AGENTS.md for universal rules, skill for task-specific rules)
2. Remove the duplicate from the non-canonical location
3. If both locations have slightly different versions, choose the clearer one and update both locations to remove the duplicate
4. Add a note to the weekly review checklist to scan for new duplication

---

### Warning Sign 4: Time Wasted on Tool or Procedure Selection

**Description**: The agent (or human) spends time at the start of a task deciding which verification command to run, which skill to follow, or which procedure applies — rather than immediately knowing.

**Severity**: Medium

**Root cause**: The harness has not defined clear decision boundaries. Either skills are not named clearly enough to make selection obvious, or multiple skills overlap in scope, or the verification commands are not documented in a single canonical location.

**Detection heuristics**:
- Agent produces a question or uncertainty statement about which skill applies at the start of a recognized task type
- Agent runs a different verification command each time (e.g., `npm test` sometimes, `jest` other times, `npm run test:unit` other times)
- Agent asks "should I use skill X or skill Y?" for a task that has occurred before
- More than one skill has the same or similar "When to Use" conditions

**Recommended action**:
1. Ensure each skill has a distinct, non-overlapping "When to Use" section
2. Document the 3 canonical verification commands in AGENTS.md and in a project config file
3. If two skills overlap significantly, merge them or add a decision rule to both
4. Add a "Decision guide" to the harness if multiple skill types serve the same domain

---

### Warning Sign 5: Essential Pre-Completion Verification Is Still Frequently Missed

**Description**: Despite a completion rule in AGENTS.md and possibly a checklist, verification steps (tests, typecheck, lint) are still being skipped before completion reports.

**Severity**: High

**Root cause**: The verification requirement exists as a text rule (Layer A or B) but has not been promoted to automated enforcement (Layer C). Text rules depend on agent and human memory. When the same verification is skipped twice or more, the text rule has demonstrably failed and a hook is required.

**Detection heuristics**:
- Review the last 5 completion reports — how many included explicit verification results?
- Review the failure log — how many entries have Category 3 (tool/verification automation absence)?
- Check whether a completion gate hook exists and is functional (`cat hooks/scripts/completion-gate.py` or equivalent)
- Ask: if an agent deliberately skipped all verification and reported complete, would anything block it?

**Recommended action**:
1. Implement or strengthen the completion gate as a command hook (not just a checklist)
2. Ensure the hook runs and fails visibly when verification is skipped
3. Review the hook triggers — it must fire at the actual completion moment, not just pre-commit
4. Record in the failure log as Category 3 and mark as absorbed once the hook is verified working

---

## Part 2: Cleanup Criteria (Section 10.1)

These criteria determine when a harness component should be removed, abbreviated, merged, or archived. Apply during every weekly harness review.

---

### Cleanup Criterion 1: Rules Unused for 8+ Weeks

**What**: Any rule in AGENTS.md, any skill step, or any hook that has not been relevant to any task in the last 8 weeks.

**Why remove**: Unused rules add noise to context without benefit. They slow agents down by increasing the volume of rules to track. They may also become outdated and start producing incorrect behavior if they are followed in a context that has changed.

**How to identify**: During weekly review, ask for each rule: "Was this rule relevant to any task this week, or in the last 8 weeks?" If the answer is no, it is a cleanup candidate.

**Action**: Remove from AGENTS.md or skill. If the rule addresses a real risk, consider whether the risk has genuinely passed or whether the rule is simply never being read. If the risk is real but the rule is not working, move to Layer C enforcement instead.

---

### Cleanup Criterion 2: Duplicate Rules with Same Content

**What**: Rules in two or more documents that say the same thing in different words.

**Why remove**: Duplicates create maintenance burden and eventual drift. When the rule needs to change, one copy gets updated and the other does not, creating contradictions (Warning Sign 3 above).

**How to identify**: Cross-read AGENTS.md and all active skills. Search for key terms that appear in AGENTS.md rules across skill files.

**Action**: Keep the rule in its canonical location (AGENTS.md for universal rules, skill for task-specific rules). Remove from the non-canonical location. Do not keep "just as a reminder" copies.

---

### Cleanup Criterion 3: Temporary Rules Whose Original Problem No Longer Occurs

**What**: Rules added in response to a specific incident, bug, or environmental problem that has since been permanently resolved.

**Why remove**: Temporary rules that become permanent create confusion. Future agents and developers cannot tell whether a rule is a permanent standard or a workaround for a resolved problem.

**How to identify**: Look for rules containing phrases like "for now", "until X is fixed", "temporary", or rules with a specific version or date reference. Also check the failure log — if the failure that prompted a rule has been absorbed at a stronger layer and has not recurred in 8+ weeks, the text rule may be redundant.

**Action**: Remove the rule. If the underlying risk still exists but is now handled by a hook, the text rule is redundant and can be removed. If in doubt, check whether removing the rule would leave any gap in coverage.

---

### Cleanup Criterion 4: Detailed Rules That Do Not Belong in Global Scope

**What**: Rules in AGENTS.md that are conditional, multi-step, or task-specific.

**Why remove**: These rules cause context pollution (Category 5 failure) and rule conflicts (Warning Sign 1). A rule that begins "when doing X..." belongs in the skill for X, not in AGENTS.md.

**How to identify**: Review each AGENTS.md rule and ask: "Would this rule apply to a completely unrelated task?" If the answer is no, it does not belong in AGENTS.md.

**Action**: Move to the appropriate skill (Layer B). Remove from AGENTS.md. If no skill exists for the task type, create one.

---

## Audit Frequency

| Check | Frequency |
|---|---|
| Warning signs 1-5 | Weekly (during harness review) |
| AGENTS.md line count | Weekly |
| Cleanup criteria 1-4 | Every 4 weeks minimum |
| Full cross-document duplication scan | Every 8 weeks |

The harness audit skill automates detection of these signals. Run it as part of the weekly review process.
