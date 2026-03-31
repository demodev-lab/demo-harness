---
name: failure-absorb
description: Absorb a failure into the harness operating system. Use when a mistake, bug, or process failure occurs and needs systematic prevention. Triggers on "failure absorb", "absorb failure", "learn from failure", "failure happened", "absorb this mistake", or "prevent this from happening again".
---

## Purpose

Convert a one-time failure into a permanent prevention mechanism. The goal is not to fix the immediate problem — that is already done — but to encode prevention into the harness so the same failure cannot recur in any future session.

The core operating principle of the harness: before changing the model, change the harness so the failure does not repeat. Fixing the immediate problem without absorption is the wrong response. It leaves the next session unprotected.

A correctly absorbed failure produces exactly one artifact: a rule update, a new or updated skill, a new hook, or a documentation change. It does not produce only a mental note, a comment in a PR, or a verbal reminder. Those are not absorption — they are hopes. Absorption is structural.

The three wrong responses to failure are: fixing it and moving on, dismissing it as a model limitation, and appending more text to an already long prompt. All three leave the harness unchanged. Absorption requires identifying which layer of the harness failed and encoding the prevention at that layer.

---

## When To Use

- After any mistake, incorrect output, missed verification step, or process breakdown
- When the same error has occurred more than once and needs mechanical prevention
- When a human says "failure absorb", "absorb failure", "learn from failure", "failure happened", "absorb this mistake", or "prevent this from happening again"
- After a postmortem when action items need encoding into the harness
- At the end of any task where something went differently than expected — even minor deviations are absorption candidates

---

## 4-Phase Workflow

### Phase 1 — Identify

Name the failure precisely. Vague names produce vague prevention rules.

Gather all four of the following before moving to Phase 2:

- **What happened**: the exact observable failure, stated in concrete behavioral terms (e.g., "agent claimed completion without running tests", not "agent was sloppy")
- **When it happened**: task context, session type, or trigger condition that was present
- **Who was affected**: human, agent, downstream system, or dependent process
- **What the correct behavior should have been**: the specific action that should have occurred instead

Output a one-sentence failure statement in this exact format:

> "During [task type], [agent/human] [did X / failed to do Y], resulting in [consequence]."

Examples of well-formed failure statements:
- "During API endpoint implementation, the agent claimed completion without running the test suite, resulting in a broken endpoint being reported as done."
- "During a code review task, the agent used the term 'service' to mean both a domain service and an infrastructure service, resulting in contradictory recommendations."
- "During a migration task, the agent executed a DROP TABLE command without explicit approval, resulting in data loss."

Do not proceed to Phase 2 until the failure statement is written and confirmed accurate.

### Phase 2 — Classify

Match the failure to one of the 6 cause categories from `${CLAUDE_PLUGIN_ROOT}/skills/failure-absorb/references/failure-categories.md`:

| # | Category | Description |
|---|----------|-------------|
| 1 | Global rule absence | No universal rule existed to prohibit or require the behavior |
| 2 | Specific task procedure absence | The task type had no skill or runbook defining the correct procedure |
| 3 | Tool/verification automation absence | A hook or script that should have caught this did not exist |
| 4 | Terminology/documentation mismatch | The failure occurred because a term was undefined or used inconsistently |
| 5 | Excessive context pollution | Important rules were buried in overly long documents and not followed |
| 6 | Unclear authority/responsibility boundaries | It was unclear which agent, role, or document owned the decision |

Select the single best-fit category. If multiple categories apply, select the one that, if fixed, would have the highest prevention impact. A failure often has multiple contributing causes; the classification identifies the primary structural gap.

Classification examples:
- "Agent completed without running tests" → Category 3 (no hook enforcing test execution) or Category 1 (no global rule requiring test verification before completion)
- "Agent used contradictory terminology" → Category 4 (terminology not defined in glossary)
- "Agent rewrote a module that already existed" → Category 2 (no skill instructing agent to check for existing implementations first)

For complex or ambiguous failures involving multiple interacting causes, delegate classification to the `failure-analyzer` agent before continuing.

### Phase 3 — Decide Layer

Route the failure to the correct absorption layer using `${CLAUDE_PLUGIN_ROOT}/skills/failure-absorb/references/layer-decision-guide.md`.

Apply the following decision logic in strict order. Stop at the first matching condition.

**Decision 1:** Does this failure apply to every task in every context — regardless of task type, project, or session?
- Yes → Layer A: add or update a rule in `AGENTS.md`
- No → continue to Decision 2

**Decision 2:** Does this failure apply only when performing a specific, nameable task type?
- Yes → Layer B: create or update a skill or runbook scoped to that task type
- No → continue to Decision 3

**Decision 3:** Did a human or agent repeatedly forget or violate a rule that already exists in text form?
- Yes → Layer C: the text rule has proven insufficient; promote to a hook or automated gate
- No → continue to Decision 4

**Decision 4:** Is future reference more valuable than active enforcement?
- Yes → Layer D: add to glossary, postmortem archive, architecture notes, or failure log

Do not absorb into Layer A (AGENTS.md) unless the rule genuinely applies to all tasks across all contexts. Each unnecessary global rule degrades every future session by increasing context size and creating more rules for agents to reconcile. When in doubt between Layer A and Layer B, choose Layer B.

### Phase 4 — Absorb

Execute the absorption action determined in Phase 3. Each layer has a specific execution procedure.

**Layer A — Update AGENTS.md**

- Add a single, concise rule (one to two sentences maximum)
- Verify AGENTS.md remains within 40–60 lines after the addition
- If adding the rule would exceed 60 lines, identify an existing rule to remove or abbreviate first — the total must stay within the limit
- Cross-check the new rule against the 10 operating principles in `${CLAUDE_PLUGIN_ROOT}/skills/failure-absorb/references/operating-principles.md` to confirm alignment
- Confirm the rule does not duplicate any existing rule under a different phrasing

**Layer B — Create or Update Skill**

- If no skill exists for this task type: create `skills/<skill-name>/SKILL.md` using the Appendix B template structure
- If a skill already exists: add a new entry to its "Common Mistakes" section with the specific failure observed
- The skill must contain all four required sections: When To Use, Steps, Verification, Common Mistakes
- The new or updated skill must describe the failure scenario explicitly so future agents recognize the same situation

**Layer C — Add or Update Hook**

- Determine hook type before writing configuration:
  - Semantic check (requires judgment to evaluate) → `prompt` hook type
  - Deterministic check (can be evaluated by pattern match or command exit code) → `command` hook type
- Add the entry to `.claude/hooks.json` using the standard hook configuration format
- Write a `description` field on the hook that explains what failure it prevents, not what it does mechanically
- Flag the hook for validation: the next identical task must be observed to confirm the hook fires as expected

**Layer D — Update Documentation**

- Glossary entry: add the undefined or misused term using the five-field format (name, definition, differences from related terms, examples, prohibited mixed expressions)
- Failure log: append to `docs/failure-log.md` with a full row (date, failure statement, cause category number, absorption action taken, verification method)
- Architecture notes: add a decision record if the failure revealed an unstated architectural assumption or constraint
- Postmortem: if the failure had significant impact, complete a full postmortem using `docs/postmortem-template.md`

### Phase 5 — Verify (검증)

흡수 완료 후 자동 검증을 실행한다:

1. **Hook 흡수**: synthetic event를 생성하여 hook이 올바르게 트리거되는지 확인
   - 테스트 입력을 stdin으로 파이프하여 hook 스크립트 직접 실행
   - exit code와 stderr 출력 확인
2. **Rule 흡수 (AGENTS.md)**: `.harness.json`의 `agents_md_max_lines` 이내인지 줄 수 확인
3. **Skill 흡수**: SKILL.md frontmatter에 `name`, `description` 필드가 유효한지 확인
4. **Doc 흡수**: failure-log.md 해당 행의 Verification Status를 `verified`로 업데이트

검증 결과를 `docs/.harness-state.json`에 기록:
- `absorptions.verified` 카운트 증가
- `absorptions.history` 해당 항목의 `verified` 필드를 `true`로 변경

---

## Output Format

After completing all 4 phases, output a failure absorption report in this exact format:

```
Failure Absorption Report
=========================
Failure:    <one-sentence failure statement from Phase 1>
Category:   <category number and name from Phase 2>
Layer:      <A / B / C / D>
Action:     <exactly what was changed — specific file, section, and content added>
Artifact:   <full file path of the created or updated artifact>
Verified:   <how the next identical task will confirm the failure is prevented>
```

Every field is required. A report missing any field is incomplete. The Artifact field must contain a real file path, not a description.

---

## Reference Files

| File | Used In |
|------|---------|
| `${CLAUDE_PLUGIN_ROOT}/skills/failure-absorb/references/failure-categories.md` | Phase 2 classification |
| `${CLAUDE_PLUGIN_ROOT}/skills/failure-absorb/references/layer-decision-guide.md` | Phase 3 layer routing |
| `${CLAUDE_PLUGIN_ROOT}/skills/failure-absorb/references/operating-principles.md` | Phase 4 Layer A cross-check |

---

## Delegation

For failures that are ambiguous in classification or that involve multiple interacting causes, delegate Phase 2 and Phase 3 to the `failure-analyzer` agent. Provide the agent with:

- The one-sentence failure statement from Phase 1
- The full task context (what was being done, what went wrong, what was expected)
- The current `AGENTS.md` content
- The list of existing skill names and hook descriptions

Receive the agent's classification and layer decision, then execute Phase 4 directly without re-delegating.

---

## Cross-Check Against Operating Principles

Before finalizing any Layer A absorption, verify the proposed rule does not contradict any of the 10 operating principles:

1. All development proceeds alongside documentation.
2. When structure, contracts, policies, or APIs change, update related docs immediately.
3. Prioritize existing patterns, common modules, and common terminology.
4. Do not leave temporary code, duplicate code, or ad hoc rules as new standards.
5. Before changes, check impact scope; after changes, verify actual impact is reflected.
6. Completion claims are backed by verification logs or test results.
7. Failures are absorbed into prevention rules, not just manually fixed.
8. When new concepts emerge, first define their name and meaning.
9. Prefer short global directives plus detailed documents at the point of need over long global directives.
10. Agents prioritize evidence over assumptions; humans prioritize system improvement over exceptions.

If the proposed rule conflicts with any principle, revise the rule to align or route to a lower layer instead.

---

## Common Mistakes

- Absorbing a task-specific rule into `AGENTS.md` — if the rule only applies during a specific task type, it belongs in a skill; global rules must apply to all tasks
- Writing a rule that is too vague to be actionable (e.g., "be more careful with completions") — every rule must describe a specific, verifiable behavior
- Skipping the failure statement in Phase 1 and jumping straight to writing a rule — the statement anchors every downstream decision
- Adding a duplicate rule that already exists under a different name — check all existing rules before adding
- Reporting absorption complete without specifying the artifact file path — the path is evidence that the absorption actually happened
- Absorbing into Layer D when Layer C (automated enforcement) would prevent recurrence — documentation is weaker than hooks; use the strongest available layer
