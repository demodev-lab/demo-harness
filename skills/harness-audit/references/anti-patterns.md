# Anti-Patterns

These 7 anti-patterns are the most common ways the harness engineering approach fails in practice. Each represents a recurring failure mode that looks like a reasonable response in the moment but makes the system worse over time.

Every harness audit should check for these patterns. When detected, the recommended fix is always a structural change — not a reminder or a verbal correction.

---

## Anti-Pattern 1: Only Lengthening the Global Prompt with Each Failure

**Description**: Every time an agent makes a mistake, a new line is added to AGENTS.md. The file grows from 40 lines to 80, to 120, to 200. Each addition feels justified because it addresses a real failure. The cumulative effect is a bloated global document that degrades performance for all tasks.

**Why it happens**: Adding a line to AGENTS.md is the path of least resistance when a failure occurs. It is faster than creating a skill, writing a hook, or updating a glossary. It feels like "fixing the problem."

**Why it is harmful**:
- Long global documents cause context pollution (Failure Category 5)
- Conditional rules mixed with universal rules cause rule conflicts (Warning Sign 1)
- Agents cannot reliably track 150+ rules simultaneously
- The 10 operating principles get buried in noise and stop being followed

**Detection heuristics**:
- AGENTS.md is over 60 lines
- AGENTS.md contains rules with "when doing X" or "unless Y" — these are conditional rules
- The failure log shows failures of Category 2 (task procedure absence) being absorbed as AGENTS.md additions
- AGENTS.md was modified in the last 3 weekly reviews without any corresponding skill creation

**Recommended fix**:
1. Audit AGENTS.md — identify every rule that is conditional or task-specific
2. Move conditional rules to the appropriate skill (create if it does not exist)
3. Remove rules that restate the 10 operating principles in different words
4. Target 40-60 lines of universal rules only
5. Establish the discipline: Category 2 failures → Layer B (skills), not Layer A (AGENTS.md)

---

## Anti-Pattern 2: Assuming Humans Will Always Remember

**Description**: A failure occurs, a human corrects the agent verbally or in the current session, and the correction is not encoded anywhere. The assumption is that the human will remember to apply this correction in every future session, or that it will "stick" with the agent.

**Why it happens**: Verbal corrections feel sufficient because they resolve the immediate problem. Encoding the correction into the harness takes more effort and feels like overhead for a one-off issue.

**Why it is harmful**:
- Human memory is session-scoped for practical purposes — corrections made today are forgotten in a month
- Agent context resets every session — corrections not in the harness are invisible to the next session
- Unencoded corrections accumulate, and the team gradually loses track of what the "real" operating rules are
- The same failure recurs, requiring repeated correction, with increasing frustration

**Detection heuristics**:
- The failure log contains the same failure type appearing in multiple entries without a harness change
- Team members have verbal agreements about how the agent should behave that are not in AGENTS.md or any skill
- The weekly review reveals failures that were "already corrected" but occurred again
- An agent makes a mistake, the human says "I've told it this before" — that statement is the signal

**Recommended fix**:
1. Any correction that is given more than once must be encoded into the harness immediately
2. Adopt the rule: corrections to agent behavior go into a harness document the same day they are identified
3. At the weekly review, ask: "What corrections did we make this week that are not yet encoded?" Encode them all
4. Use the failure log to track whether a correction has been encoded — entries should have an "Absorbed-to" layer, not remain as "pending" indefinitely

---

## Anti-Pattern 3: Pasting Entire Directory Trees into Documents

**Description**: An AGENTS.md or skill includes a full directory listing, a complete file tree, or a large dump of project structure, assuming this helps agents navigate the codebase.

**Why it happens**: It feels helpful to give agents a map of the project. When an agent seems confused about where things are, adding a directory listing feels like the fix.

**Why it is harmful**:
- Directory trees go stale immediately — the next file addition or rename makes the listing wrong
- A stale directory listing is worse than no listing — it actively misdirects the agent
- Large pasted content consumes context budget, displacing rules and instructions that actually matter
- Agents have tools (Glob, Grep, file search) to discover structure — a listing teaches them nothing about using those tools

**Detection heuristics**:
- AGENTS.md contains more than a few lines describing file locations
- Any document contains a block that starts with `├──` or similar tree characters
- A skill or runbook has a "Project structure" section with specific file paths
- Any document has not been updated when new files were added to the areas it describes

**Recommended fix**:
1. Remove directory listings from all documents
2. Replace with a pointer to the conventions: "Use Glob to find files matching `src/**/*.ts`" or "Controllers live in `src/controllers/` by convention"
3. Document naming conventions and organization principles instead of specific paths
4. If a specific file is genuinely important to reference, link to it by path with a one-line description — not a tree

---

## Anti-Pattern 4: Covering Small Problems with New Abstractions or Dependencies

**Description**: A small, specific problem is solved by introducing a new abstraction layer, a new utility class, or a new third-party dependency — when a direct fix would have been simpler and sufficient.

**Why it happens**: Abstractions feel like "doing it right." Adding a utility feels cleaner than repeating logic. The scope of the solution expands beyond the scope of the problem without the expansion being noticed.

**Why it is harmful**:
- New abstractions add maintenance surface without proportional value for single-use logic
- New dependencies add security risk, upgrade burden, and compatibility constraints
- Future agents and developers encounter the abstraction without understanding the small problem it was created for
- Complexity accumulates — each small abstraction compounds with others until the codebase is hard to understand

**Detection heuristics**:
- A new utility file or helper class exists that is used in only one place
- A new dependency was added to solve a problem that 5 lines of direct code would have solved
- The fix for a bug introduced a new interface or type that only the fix uses
- A code review comment says "why does this abstraction exist?" and there is no good answer

**Recommended fix**:
1. When tempted to create a utility: ask "is this used in 2+ distinct places?" If no, write it inline
2. When tempted to add a dependency: ask "can I implement the needed behavior in under 20 lines?" If yes, do it directly
3. Apply the same principle to harness documents: do not create a new skill for a one-time task
4. Review new files and dependencies in the weekly review — identify any that were added for single-use and consolidate or remove

---

## Anti-Pattern 5: Separating Documentation from Operating Contracts

**Description**: Documentation exists as a separate artifact that describes what the system should do, while the operating contracts (AGENTS.md, skills, hooks) describe what agents and developers actually do. The two diverge over time.

**Why it happens**: Documentation is written once and forgotten. Operating contracts evolve with each failure absorption. Neither set of authors tracks the other. Eventually, a developer reads the docs and follows guidance that the operating contracts have superseded.

**Why it is harmful**:
- Agents (and humans) cannot trust either source — they have to reconcile two conflicting authorities
- New team members follow the documentation and make mistakes that the operating contracts were designed to prevent
- Absorbed failure learnings exist in skills and AGENTS.md but not in the user-facing docs, creating a hidden knowledge gap
- The documentation loses credibility because it does not reflect reality

**Detection heuristics**:
- Docs describe a workflow that a skill also describes, but they differ in steps
- The glossary defines a term that a README defines differently
- An agent follows a document that contradicts a skill, and there is no clear authority ordering
- Project onboarding documentation has not been updated when a new skill was added

**Recommended fix**:
1. Establish a single authority for each type of information — docs describe what the system is; skills describe how to operate it
2. When a skill is created for a recurring task, update any overlapping documentation to reference the skill
3. Treat documentation updates as part of skill creation — every new skill should prompt a docs review
4. During weekly review, check whether any new skills or rules created this week require a docs update

---

## Anti-Pattern 6: Abusing Sub-Agents as Role Decoration

**Description**: Sub-agents are spawned for every task to perform "roles" (reviewer, architect, specialist) without clear scope boundaries or verifiable outputs. The main thread fills with sub-agent summaries that add noise rather than value.

**Why it happens**: Multi-agent architectures feel more powerful and thorough. Spawning a "security reviewer" agent feels safer than doing a security review inline. The pattern is adopted broadly without asking whether each specific sub-agent invocation is actually necessary.

**Why it is harmful**:
- Sub-agents consume context budget in the main thread through their summaries and coordination overhead
- Sub-agents without narrow, verifiable scope produce vague, general outputs that require re-work
- The main thread loses clarity of direction when it is coordinating too many sub-agents simultaneously
- Sub-agents used as role decoration do not improve output quality — they add latency and complexity without measurable benefit

**Detection heuristics**:
- Sub-agents are spawned for tasks that take fewer than 5 steps and have no search or parallelization requirement
- A sub-agent's output is "reviewed" by the main thread by re-doing the work
- Sub-agent summaries frequently say things like "I reviewed X and it looks good" without specific findings
- The same task is being done by both the main thread and a sub-agent simultaneously

**Recommended fix**:
1. Apply the sub-agent use criteria strictly (from AGENTS.md Section 8):
   - Large search results that would pollute the main thread → valid use
   - Independent investigation/verification/review tasks → valid use
   - Implementation and verification in parallel → valid use
2. Do not spawn sub-agents for: single-file tasks, core blocked tasks, exploration without reading first
3. Define narrow, verifiable scope before spawning: "Search for all usages of function X and return a list" — not "review the codebase"
4. Require sub-agents to return summaries with specific findings, not general assessments

---

## Anti-Pattern 7: Reporting "Complete" Without Verification

**Description**: An agent (or human) reports a task as complete before running verification — tests, typecheck, lint, or behavioral confirmation. The completion claim is based on "the code looks right" rather than evidence.

**Why it happens**: Verification takes time. Running tests feels like an additional step after the "real work" is done. Agents have a strong tendency toward positive completion signals. The path of least resistance is to report done and let the human discover issues.

**Why it is harmful**:
- False completion reports are the most costly failure mode — subsequent work builds on an incorrect foundation
- Type errors, lint failures, and test failures compound when not caught immediately
- Trust in the agent's completion reports degrades, requiring humans to re-verify everything
- The downstream cost of finding a bug introduced in "completed" work is 5-10x the cost of catching it at completion

**Detection heuristics**:
- Completion reports do not include which verification commands were run
- Completion reports say "tests should pass" or "I believe this is correct" rather than citing actual results
- A failure log shows repeated Category 3 entries (verification automation absence)
- The completion gate hook (if implemented) is frequently triggered, indicating the agent is trying to complete without running verification

**Recommended fix**:
1. Implement the completion gate as a command hook (Layer C) — not just a checklist
2. The completion gate must require explicit answers to: which tests were run, did they pass, was typecheck run, was lint run
3. Add to AGENTS.md: "Do not write 'complete' until you have cited the verification results"
4. Review the last 5 completion reports — if any lack verification evidence, the completion gate is not working and must be strengthened
5. If the agent cannot run verification (test environment unavailable, etc.), it must state this explicitly rather than silently skipping

---

## Anti-Pattern Quick Reference

| # | Anti-Pattern | Primary Signal | Layer Fix |
|---|---|---|---|
| 1 | Lengthening global prompt only | AGENTS.md > 60 lines | Move conditional rules to Layer B |
| 2 | Assuming human memory | Same failure recurs after verbal correction | Encode corrections into Layer A/B/C same day |
| 3 | Pasting directory trees | Tree characters in documents | Replace with conventions + file search guidance |
| 4 | New abstractions for small problems | Utility used in only 1 place | Write inline; remove single-use abstractions |
| 5 | Docs separated from contracts | Docs and skills describe same thing differently | Establish authority ordering; update docs with skills |
| 6 | Sub-agents as role decoration | Sub-agents spawned without narrow scope | Apply strict sub-agent criteria; require specific outputs |
| 7 | Completing without verification | Completion reports lack verification evidence | Implement completion gate as command hook |
