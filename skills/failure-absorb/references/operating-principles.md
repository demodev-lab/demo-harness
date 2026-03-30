# Operating Principles

These 10 principles are the foundation of the Harness Engineering approach. They apply universally to every project, every session, every developer, and every agent. They are not guidelines — they are the operating contract.

Every AGENTS.md created with this plugin reflects these principles. Every skill, hook, and review process enforces them.

---

## Principle 1: All development proceeds alongside documentation.

**Verbatim**: All development proceeds alongside documentation.

**Explanation**: Documentation is not a post-development task. When code changes, docs change in the same commit or session. When a new feature is built, its contracts and interfaces are documented before or during implementation — not after. "We'll document it later" is not a valid state. Documentation that lags behind code is actively harmful because it creates false confidence in readers.

**In practice**:
- Never close a task with undocumented changed contracts or APIs
- The completion gate must check whether docs were updated when contracts changed
- If a doc cannot be updated in the same session, the task is not complete — it is deferred

---

## Principle 2: When structure, contracts, policies, or APIs change, update related docs immediately.

**Verbatim**: When structure, contracts, policies, or APIs change, update related docs immediately.

**Explanation**: This is the application of Principle 1 to specific change types. "Immediately" means in the same commit, not the next session. Structural changes (file organization, module boundaries), contract changes (API shapes, database schemas), policy changes (auth rules, rate limits), and API changes all have downstream readers who depend on documentation accuracy. Delayed updates create a window of incorrect guidance.

**In practice**:
- API endpoint changes require OpenAPI spec or equivalent update in the same diff
- Database schema changes require migration docs or schema docs update
- Architecture changes require ADR or architecture doc update
- A completion hook should check for this automatically when relevant files change

---

## Principle 3: Prioritize existing patterns, common modules, and common terminology.

**Verbatim**: Prioritize existing patterns, common modules, and common terminology.

**Explanation**: Before writing new code, check whether the pattern already exists in the codebase. Before introducing a new abstraction, check whether an existing module covers the need. Before naming a new concept, check the glossary. Duplication is not just inefficient — it creates diverging implementations that must be maintained separately and creates confusion about which version is canonical.

**In practice**:
- Read relevant existing code before writing new code
- Check the glossary before naming new types, functions, or concepts
- Reuse existing error handling patterns, response shapes, and utility functions
- If an existing pattern is wrong, refactor it — don't create a parallel one

---

## Principle 4: Do not leave temporary code, duplicate code, or ad hoc rules as new standards.

**Verbatim**: Don't leave temporary code, duplicate code, or ad hoc rules as new standards.

**Explanation**: Temporary workarounds become permanent when they are committed without a removal plan. Duplicate code becomes the de facto standard when the original is forgotten. Ad hoc rules added to AGENTS.md in response to one incident become permanent noise when the incident context is forgotten. Every piece of code and every rule should be either a permanent intentional addition or explicitly marked for removal.

**In practice**:
- Do not commit TODO-workaround code without a tracking issue or explicit removal criteria
- Do not add rules to AGENTS.md that only apply to one specific past incident
- Do not duplicate a function because modifying the original feels risky — refactor the original
- Weekly review should identify and remove temporary rules that have outlived their purpose

---

## Principle 5: Before changes, check impact scope; after changes, verify actual impact is reflected.

**Verbatim**: Before changes, check impact scope; after changes, verify actual impact is reflected.

**Explanation**: Changes to shared code have ripple effects. Before modifying a shared module, utility, or interface, identify every caller and dependent. After making the change, verify that the actual behavior change is reflected everywhere it needs to be — not just in the files directly edited. "I only changed one file" is not a scope analysis.

**In practice**:
- Before modifying a shared function: find all callers
- Before changing a type: find all usages
- After changes: run the full test suite, not just tests for the changed file
- After changing a doc: check whether downstream docs reference it and need updates

---

## Principle 6: Completion claims are backed by verification logs or test results.

**Verbatim**: Completion claims are backed by verification logs or test results.

**Explanation**: "Complete" is not a feeling — it is a verifiable state. A task is complete when verification evidence exists: tests passed, lint passed, typecheck passed, behavior confirmed. Claiming completion without evidence is a false completion report. False completion reports are the most common and most costly failure mode in agent-assisted development because they compound — subsequent tasks build on an incorrect foundation.

**In practice**:
- Always state which verification commands were run and their results in the completion report
- Never write "done" or "complete" without having run at least one verification command
- The completion gate (Layer C) mechanically enforces this
- If verification cannot be run for legitimate reasons, state why explicitly — do not silently skip

---

## Principle 7: Failures are absorbed into prevention rules, not just manually fixed.

**Verbatim**: Failures are absorbed into prevention rules, not just manually fixed.

**Explanation**: When a failure occurs, fixing the immediate instance is necessary but insufficient. The failure must also be absorbed into the harness so the same failure cannot recur. This is the core operating loop of the entire system. A harness that does not absorb failures grows stale while the same mistakes repeat. Absorption means: classify the failure, identify the root cause, determine the correct layer, add the prevention rule, and verify it works.

**In practice**:
- Every significant failure gets a failure log entry
- Every repeated failure triggers a harness change (rule, skill, hook, or doc)
- "We fixed it" is not the same as "we prevented it"
- Weekly review is the scheduled time for absorption — failures should not accumulate without action

---

## Principle 8: When new concepts emerge, first define their name and meaning.

**Verbatim**: When new concepts emerge, first define their name and meaning.

**Explanation**: Naming is architecture. When a new concept appears in code or discussion, the first action is to name it precisely and add it to the glossary before using it in code, documents, or communication. Unnamed concepts become named differently by different contributors, creating terminology fragmentation. Once a concept has multiple names in the codebase, consolidation is expensive.

**In practice**:
- Before creating a new type, class, or module: check the glossary for an existing concept
- If the concept is genuinely new: add it to the glossary first (name, definition, differs from, example, prohibited synonyms)
- Do not use placeholder names like `tempHandler` or `newUtil` in committed code
- When two names are found for the same concept: immediately consolidate and add prohibited synonyms

---

## Principle 9: Prefer short global directives + detailed documents at the point of need over long global directives.

**Verbatim**: Prefer short global directives + detailed documents at the point of need over long global directives.

**Explanation**: A short, focused AGENTS.md that points to detailed skills and runbooks is more effective than a long AGENTS.md that tries to cover everything. Long global directives create context pollution (Category 5 failure), rule conflicts, and agent confusion. Detailed guidance belongs at the point of need — in the skill loaded for the specific task, not in the global document loaded for every task.

**In practice**:
- AGENTS.md stays within 40-60 lines
- When adding a rule to AGENTS.md that is longer than 2 lines, extract it to a skill instead
- When AGENTS.md exceeds 60 lines, audit and extract conditional rules to Layer B
- Each skill is self-contained — it should not require reading AGENTS.md to understand

---

## Principle 10: Agents prioritize evidence over assumptions; humans prioritize system improvement over exceptions.

**Verbatim**: Agents prioritize evidence over assumptions; humans prioritize system improvement over exceptions.

**Explanation**: Two complementary rules for two types of actors. Agents must not assume — they must verify, check, read, and report evidence. "I assumed the tests passed" is never acceptable. Humans must not treat every harness failure as a one-off exception that needs a human fix — they must treat it as a signal that the system needs improvement. "I'll just remind it this time" is the path to an unmaintained harness.

**In practice for agents**:
- Do not assume a file exists — check
- Do not assume tests pass — run them
- Do not assume a concept is defined — look it up in the glossary
- Report what you actually found, not what you expected to find

**In practice for humans**:
- When an agent makes a mistake, ask "what harness change prevents this?" before asking "how do I fix this?"
- Avoid one-off verbal corrections that are not encoded into the harness
- Schedule and protect weekly review time — it is the system improvement mechanism
- Treat repeated agent mistakes as system failures, not agent failures

---

## Summary Reference

| # | Principle |
|---|---|
| 1 | All development proceeds alongside documentation. |
| 2 | When structure, contracts, policies, or APIs change, update related docs immediately. |
| 3 | Prioritize existing patterns, common modules, and common terminology. |
| 4 | Do not leave temporary code, duplicate code, or ad hoc rules as new standards. |
| 5 | Before changes, check impact scope; after changes, verify actual impact is reflected. |
| 6 | Completion claims are backed by verification logs or test results. |
| 7 | Failures are absorbed into prevention rules, not just manually fixed. |
| 8 | When new concepts emerge, first define their name and meaning. |
| 9 | Prefer short global directives + detailed documents at the point of need over long global directives. |
| 10 | Agents prioritize evidence over assumptions; humans prioritize system improvement over exceptions. |
