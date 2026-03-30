# Failure Categories

Every failure absorbed into the harness must be classified into exactly one of these 6 categories. Accurate classification determines which layer receives the prevention rule. Misclassification leads to fixes applied at the wrong layer, which means the failure recurs.

If a failure appears to fit multiple categories, choose the root cause — the earliest point in the chain where a structural change would have prevented it.

---

## Category 1: Global Rule Absence

**Definition**: A universal rule that should apply to all tasks did not exist in Layer A (AGENTS.md). The agent had no guidance on this behavior and therefore either invented its own approach or defaulted to a harmful behavior.

**Identification criteria**:
- The failure would have been prevented if AGENTS.md contained a specific rule
- The rule, if added, would apply to every task type — not just the one that failed
- There is no existing rule in AGENTS.md that covers this behavior even loosely

**Examples**:
- Agent force-pushed to main because no rule prohibited destructive commands
- Agent reported "complete" without running any verification because no completion standard was defined
- Agent introduced a third-party dependency without checking existing modules, because no "prefer existing modules" rule existed

**Absorption target**: Layer A — add the rule to AGENTS.md

**Common false positives**: If the rule already exists in AGENTS.md but was ignored, this is not Category 1. If the rule only applies to a specific task type, this is not Category 1 — it belongs in Category 2.

---

## Category 2: Specific Task Procedure Absence

**Definition**: A universal rule exists (or would not help), but no skill or runbook defined the correct procedure for this specific work type. The agent had no step-by-step guidance and improvised, missing critical steps.

**Identification criteria**:
- The failure occurred during a specific, recognizable task type (migration, API change, deployment, etc.)
- A skill with correct steps would have prevented the failure
- The behavior was not universally wrong — it was wrong specifically for this work type

**Examples**:
- Agent added an API endpoint without updating the OpenAPI spec, because no API skill existed to list spec update as a required step
- Agent ran a database migration without taking a backup first, because no migration runbook defined pre-migration safety steps
- Agent changed a shared utility function without checking all callers, because no refactoring skill defined impact-scope checking

**Absorption target**: Layer B — create or update the relevant skill or runbook

**Common false positives**: If the task type has a skill but the skill is incomplete, update the existing skill rather than creating a new one. If the failure occurs across all task types equally, it may be Category 1 instead.

---

## Category 3: Tool/Verification Automation Absence

**Definition**: A verification step that should have been automated was left to human or agent memory. The step existed as a text rule but was not mechanically enforced, and it was skipped.

**Identification criteria**:
- A verification command (lint, typecheck, test, build) was not run before completion
- Or: a check that could be expressed as a pass/fail command was not implemented as a hook
- The failure would have been caught immediately if the command had been run
- The text rule requiring this verification already existed — the gap is in enforcement

**Examples**:
- Agent introduced a type error and reported complete because typecheck was not run; the rule "run typecheck" existed in AGENTS.md but was not a hook
- Agent committed code that failed lint because no pre-commit lint hook was configured
- Agent skipped the completion gate because it was a checklist but not an enforced command

**Absorption target**: Layer C — create or strengthen a hook, pre-commit check, or completion gate script

**When to promote vs. add**: If this is the first occurrence, add a text rule. If the same verification has been skipped twice or more, promote immediately to a command hook (see rule-promotion criteria).

---

## Category 4: Terminology/Documentation Mismatch

**Definition**: The agent used a different term for a concept than the codebase uses, or documentation was outdated relative to the code, causing confusion or incorrect behavior.

**Identification criteria**:
- A new type, variable name, or concept was created that duplicates an existing one under a different name
- An agent referenced a document that described an outdated architecture or API
- Two documents defined the same concept differently, and the agent chose the wrong one
- A term was used in code that has a different meaning in the glossary (or no glossary entry exists)

**Examples**:
- Agent created `UserRecord` type because the glossary did not define the canonical `User` type, resulting in a duplicate model used across 3 new files
- Agent followed an outdated migration guide that referenced a deprecated tool, because the guide had not been updated when the tool was replaced
- Agent used "endpoint" and "route" interchangeably in new code and docs, creating inconsistency, because the glossary did not specify the canonical term

**Absorption target**: Layer D — add or correct glossary entries, update outdated documents, add prohibited synonyms to relevant terms

**Secondary action**: If a document is so outdated it is actively harmful, archive it (Layer D cleanup) and create a replacement.

---

## Category 5: Excessive Context Pollution

**Definition**: Too much irrelevant content was loaded into the agent's context, causing it to lose focus, misinterpret instructions, or apply rules from a different task type to the current one.

**Identification criteria**:
- The agent followed instructions from a document that was loaded but not relevant to the current task
- The agent was confused by conflicting rules because too many documents were active simultaneously
- A large search result or directory listing was injected into context, displacing relevant information
- The agent's response showed clear mixing of concerns from different contexts

**Examples**:
- A migration skill and a deployment skill were both loaded for a task that only required deployment; the agent followed migration steps mid-deployment
- A sub-agent was asked to "explore the codebase" and returned a full directory tree that consumed the main thread's context budget
- AGENTS.md had grown to 200 lines and contained conditional rules that contradicted each other; the agent chose the wrong branch

**Absorption target**:
- If caused by AGENTS.md bloat: Layer A cleanup — prune AGENTS.md to universal rules only
- If caused by improper skill loading: Layer B — tighten "When to Use" criteria in skills
- If caused by sub-agent misuse: Layer A or B — add sub-agent scope rules

**Key signal**: If agents are frequently "confused" or producing mixed-concern responses, suspect context pollution before assuming model failure.

---

## Category 6: Unclear Authority/Responsibility Boundaries

**Definition**: It was unclear whether the agent, a sub-agent, or a human was responsible for a specific decision or action. Work was duplicated, skipped entirely, or handed off incorrectly with incomplete context.

**Identification criteria**:
- The same work was done twice (by agent and human, or by two sub-agents)
- A critical step was skipped because each party assumed the other was handling it
- A sub-agent made a decision that should have been escalated to the main thread or human
- A human override was ignored or not acted upon because the authority boundary was unclear

**Examples**:
- Main agent and sub-agent both wrote migration scripts independently because the task division was not specified, resulting in two conflicting scripts
- Sub-agent verified tests and reported "passed" to main thread, but main thread also ran tests — the duplication wasted time and obscured which run was authoritative
- Agent applied a destructive operation assuming human approval had been given implicitly, because approval boundaries were not defined

**Absorption target**:
- If boundary between agent and human: Layer A — add explicit authority rules to AGENTS.md
- If boundary between main thread and sub-agent: Layer A or B — add sub-agent scope rules
- If task-specific boundary confusion: Layer B — add responsibility section to the relevant skill

---

## Classification Quick Reference

| Symptom | Likely Category |
|---|---|
| Rule simply did not exist | 1: Global rule absence |
| Rule existed but steps were incomplete for this task | 2: Specific task procedure absence |
| Verification was skipped because it wasn't automated | 3: Tool/verification automation absence |
| Wrong term used, or outdated doc followed | 4: Terminology/documentation mismatch |
| Agent confused by irrelevant instructions | 5: Excessive context pollution |
| Work duplicated or skipped due to unclear ownership | 6: Unclear authority/responsibility boundaries |
