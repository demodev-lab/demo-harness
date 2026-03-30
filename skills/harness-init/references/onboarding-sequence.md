# Onboarding Sequence

This document defines the recommended introduction sequence for the Harness Engineering Plugin in a new project. Follow the steps in order — each step builds on the previous one. Skipping steps is possible but reduces the effectiveness of the harness.

The sequence is drawn from Appendix E and sections 6 and 12 of the Harness Engineering Manual.

---

## Overview

| Phase | Timeline | Goal |
|---|---|---|
| Day 0 | First session | Basic harness functional |
| Day 1 | Second session or first repetitive task | Skill + hook coverage begins |
| Week 1+ | Ongoing | Feedback loop established |

---

## The 7-Step Introduction Sequence

### Step 1: Read the Operating Manual

**What**: Read this manual (the Harness Engineering Manual) alongside the project's existing root operating document (AGENTS.md, CLAUDE.md, or equivalent).

**Why**: The manual defines the vocabulary and mental model for the entire harness. Steps 2-7 reference concepts defined here. Skipping this step means building without shared language.

**Output**: Familiarity with the 4 layers, 6 failure categories, 10 operating principles, and the failure absorption loop.

**Verify**: Can you describe the difference between Layer A and Layer B? Can you name the 6 failure categories without looking?

---

### Step 2: Fill the Minimal AGENTS.md

**What**: Create or update the project's root AGENTS.md using the minimal template (Appendix A / `agents-md-template.md`).

**Why**: This is the project's operating contract. It is the first document any agent reads. Without it, every session starts from zero context.

**Requirements**:
- Incorporate all 10 operating principles (adapted to project-specific language where needed)
- Keep within 40-60 lines
- Include only universal rules — nothing conditional or task-specific
- Add the sub-agent operating principles from Section 8

**Output**: A committed AGENTS.md that covers core rules, workflow, sub-agent use, and completion standards.

**Verify**: Is every line in AGENTS.md a rule that applies to every task? Is the file under 60 lines?

---

### Step 3: Finalize 3 Verification Commands

**What**: Define and test exactly three verification commands for the project: lint, typecheck, and test.

**Why**: Verification is meaningless if the commands are unknown or inconsistent. These three commands are the foundation of the completion gate and all Layer C hooks.

**Requirements**:
- Each command must be runnable from the project root
- Each command must have a clear pass/fail output
- Commands must be recorded in AGENTS.md and/or a project config

**Examples**:
- Lint: `npm run lint` / `ruff check .` / `golangci-lint run`
- Typecheck: `tsc --noEmit` / `mypy .` / `cargo check`
- Test: `npm test` / `pytest` / `go test ./...`

**Output**: Three working commands documented in the project.

**Verify**: Run all three commands. Do they pass on the current codebase? Are they recorded where agents will find them?

---

### Step 4: Create the Glossary

**What**: Create `docs/glossary/README.md` using the glossary template (`glossary-template.md`). Add at minimum the core harness terms, plus any project-specific terms already in use.

**Why**: Terminology mismatches are one of the 6 failure categories. Without a glossary, agents invent synonyms, create duplicate types, and create inconsistent naming across the codebase.

**Requirements**:
- Include harness-universal terms (harness, layer A/B/C/D, skill, hook, completion gate, failure absorption, rule promotion)
- Add at least 3 project-specific terms that are already in use
- For each term: name, definition, differs from, example, prohibited synonyms

**Output**: A committed `docs/glossary/README.md` with 10+ defined terms.

**Verify**: Does the glossary define every term used in AGENTS.md? Does it define terms that have caused confusion in past sessions?

---

### Step 5: Separate the First Repetitive Task into a Skill

**What**: Identify the most common recurring task type in this project and create a skill for it using the skill template (`skill-template.md`).

**Why**: Repetitive tasks without skills are a source of Layer B failures — the agent has no procedure and improvises. The first skill converts the most common ad hoc process into a reliable one.

**How to identify the first skill**:
- What task type comes up most often in this project? (deploys, API changes, migrations, PR reviews, etc.)
- What task has caused the most inconsistency or required the most correction?
- What task has a clear sequence of steps that are sometimes skipped?

**Requirements**:
- YAML frontmatter with name and description
- When to use section (specific trigger conditions)
- Ordered steps
- Verification checklist
- At least one common mistake drawn from real experience

**Output**: A committed skill file in `skills/[skill-name]/SKILL.md`.

**Verify**: If you ran this task right now using only the skill, would it produce the correct result? Are the steps ordered correctly?

---

### Step 6: Enforce the Completion Checklist as a Hook

**What**: Implement the completion gate checklist (from `hook-checklist-template.md` C.1) as either a prompt hook or a command hook.

**Why**: Text rules for completion verification are insufficient. The single most common failure pattern across all projects is agents (and humans) reporting "complete" when verification was skipped. Mechanical enforcement is required.

**Minimum implementation** (prompt hook):
- Add the 5-question completion checklist to AGENTS.md under "Completion"
- Configure it to be injected at the completion moment in the project's hook configuration

**Preferred implementation** (command hook):
- Create a `hooks/scripts/completion-gate.py` (or equivalent) that runs lint, typecheck, and tests
- Configure as a pre-commit or completion hook
- Hook blocks on failure with a clear message

**Output**: A working completion gate that actually blocks or challenges incomplete completion claims.

**Verify**: Deliberately skip running tests and attempt to report "complete." Does the gate fire? Does it block or challenge the claim?

---

### Step 7: Start Weekly Review from the First Week's Failure Cases

**What**: At the end of the first week (or first sprint), conduct the first weekly harness review using the weekly review template (`weekly-review-template.md`). Record all failure cases from the week and make at least one harness change.

**Why**: The harness only improves through the feedback loop. Without the first review, failures accumulate without absorption. The review habit is harder to start than to maintain — establishing it in week 1 is critical.

**Requirements**:
- Complete all four sections: Repeated Failures, Harness Changes, Cleanup, Next Week Targets
- Make at least one structural change (new rule, new skill, updated glossary, or new hook)
- Record the review in `docs/weekly-reviews/[date].md`

**Output**: A completed first weekly review with at least one harness change committed.

**Verify**: Is there at least one new harness artifact (rule, skill, hook, or glossary entry) that was created as a result of this review?

---

## Day 0 Milestone

After Step 1 and Step 2, the project has:
- A shared operating vocabulary
- An operating contract that agents can follow

The harness is not functional yet — verification and skills are missing — but agents can begin work without starting from zero context.

## Day 1 Milestone

After Steps 3-5, the project has:
- Working verification commands
- A glossary preventing terminology failures
- At least one skill preventing procedural improvisation

Agents can now complete the most common task type reliably.

## Week 1+ Milestone

After Steps 6-7 and the first weekly review, the project has:
- Mechanical enforcement of the completion gate
- An active feedback loop absorbing failures into the harness
- A review cadence that prevents the harness from growing stale

The basic harness is functional. From this point, each week's review either absorbs new failures or prunes stale rules — the harness improves rather than decays.

---

## Quick Introduction Checklist (Section 12)

The minimum order for a working harness:

1. Write root AGENTS.md
2. Define 3 verification commands: lint, typecheck, test
3. Create glossary document
4. Separate 1 repetitive task into a skill
5. Add 1 completion hook
6. Start failure retrospective document

These 6 alone make the basic harness functional.
