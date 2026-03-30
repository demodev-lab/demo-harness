# Harness Glossary Template

Use this template as the starting point for `docs/glossary/README.md` in any project. Fill in project-specific terms following the same format. The first section contains harness-universal terms that apply to every project using the Harness Engineering Plugin.

---

## How to Use This Glossary

Every new term introduced to the codebase or operating documents must be defined here before use. When a term is ambiguous or has been used inconsistently, add a "Prohibited synonyms" entry to enforce consistent usage.

Term format:
- **Name**: The canonical term as used in this project.
- **Definition**: What it is and what it does.
- **Differs from**: Terms that are similar but distinct, and how they differ.
- **Example**: A concrete instance of the term in use.
- **Prohibited synonyms**: Alternative phrasings that must not be used to avoid confusion.

---

## Harness Engineering Terms

### Harness

- **Name**: Harness
- **Definition**: The operating layer that controls model behavior from outside the model itself. Comprises constitutional documents, contextual skills, automated enforcement hooks, and memory documents. The harness is what prevents the same mistake from recurring — it absorbs failures into rules rather than relying on human memory or model willpower.
- **Differs from**: A prompt (a harness is structural and persistent; a prompt is ephemeral). A coding standard (a harness includes automation and enforcement; a coding standard is text only).
- **Example**: The combination of AGENTS.md + completion gate hook + failure log that together prevent a class of agent errors from repeating.
- **Prohibited synonyms**: "the system prompt", "the rules file", "agent config"

---

### Layer A: Constitutional Documents

- **Name**: Layer A (Constitutional Documents)
- **Definition**: Immutable rules that apply to all work in a project without exception. Stored in AGENTS.md and CLAUDE.md. Contains only universal rules — nothing conditional, nothing feature-specific. Kept within 40-60 lines to prevent performance degradation.
- **Differs from**: Layer B (Layer A is universal; Layer B applies only to specific work types). The harness as a whole (Layer A is one component of the harness).
- **Example**: "Verify before claiming completion" — this rule applies to every task, so it lives in Layer A.
- **Prohibited synonyms**: "global rules file", "the main prompt", "system instructions"

---

### Layer B: Contextual Execution Documents

- **Name**: Layer B (Contextual Execution Documents)
- **Definition**: Rules and procedures needed only for specific work types. Implemented as skills, playbooks, and runbooks. Loaded only when the relevant task type is active, keeping the main context clean. Format includes: when to use, execution steps, failure response, and verification method.
- **Differs from**: Layer A (Layer B is conditional; Layer A is universal). A hook (Layer B is human-readable procedure; a hook is automated enforcement).
- **Example**: A migration skill that defines the exact steps for database schema changes — only loaded when a migration is being performed.
- **Prohibited synonyms**: "conditional rules", "task docs", "playbooks folder"

---

### Layer C: Automated Enforcement

- **Name**: Layer C (Automated Enforcement)
- **Definition**: Mechanically blocks items that humans forget or models skip. Implemented as hooks, pre-commit checks, completion gates, and scripts. Automation is stronger than human willpower — when a violation repeats, promote the text rule to a hook.
- **Differs from**: Layer B (Layer C is automated and blocks action; Layer B is readable procedure). A completion checklist (a checklist is self-reported; a hook enforces mechanically).
- **Example**: A pre-commit hook that runs lint and typecheck, blocking the commit if either fails.
- **Prohibited synonyms**: "CI checks", "linting rules", "pre-commit config"

---

### Layer D: Memory and Learning Documents

- **Name**: Layer D (Memory and Learning Documents)
- **Definition**: Reusable records of failures, decisions, and operational facts for future sessions. Implemented as glossaries, architecture decision notes, postmortems, and recurring failure ledgers. Rules are abstracted; cases are recorded. This layer prevents the same investigation from being repeated.
- **Differs from**: Layer A (Layer D is reference and memory; Layer A is active operating rules). A skill (a skill is procedural; Layer D is factual and historical).
- **Example**: A postmortem documenting why a particular API design decision was made, preventing future agents from reversing it without understanding the tradeoffs.
- **Prohibited synonyms**: "project notes", "decision log", "ADR folder"

---

### Skill

- **Name**: Skill
- **Definition**: A Layer B document defining the procedure for a specific, repeatable work type. Contains: when to use, ordered steps, verification method, and common mistakes. Loaded into context only when the relevant task is active. One skill covers one work type only.
- **Differs from**: A runbook (a runbook is for incident recovery; a skill is for planned recurring tasks). A hook (a skill is procedural guidance; a hook is automated enforcement).
- **Example**: An "api-endpoint-workflow" skill that specifies the exact steps for adding or changing API endpoints.
- **Prohibited synonyms**: "command", "macro", "workflow doc", "procedure file"

---

### Hook

- **Name**: Hook
- **Definition**: A Layer C automation that runs at a defined trigger point (pre-commit, pre-push, completion) to mechanically enforce a rule. Hooks either block action when the rule is violated or warn the agent/human to take corrective action. Promoted from text rules when a violation repeats 2+ times.
- **Differs from**: A checklist (a checklist is self-reported; a hook runs automatically). A skill (a skill is read and followed; a hook executes and enforces).
- **Example**: A completion gate hook that checks whether tests were run before allowing a "complete" report.
- **Prohibited synonyms**: "script", "automation", "CI step", "pre-commit rule"

---

### Completion Gate

- **Name**: Completion Gate
- **Definition**: A specific hook or checklist that must pass before a task can be reported as complete. Prevents false completion claims. Minimum items: tests run, lint/typecheck run, docs updated for contract changes, user-visible behavior verified, remaining risks reported.
- **Differs from**: A hook (a completion gate is a specific type of hook focused on the completion moment; a hook is the general mechanism). Done criteria (done criteria are defined per task; the completion gate is universal).
- **Example**: A pre-completion check that verifies at least one test was run and that no documentation was changed without updating the related contract.
- **Prohibited synonyms**: "definition of done", "done checklist", "finish gate"

---

### Failure Absorption

- **Name**: Failure Absorption
- **Definition**: The practice of converting a failure into a permanent harness improvement rather than just fixing the immediate instance. The core operating loop: name the failure type, classify its cause, determine which layer should prevent it, absorb into rule/skill/hook/document, verify prevention in the next identical task.
- **Differs from**: Bug fixing (a bug fix addresses one instance; failure absorption prevents recurrence structurally). Root cause analysis (RCA identifies the cause; failure absorption encodes prevention).
- **Example**: After an agent skips typecheck three times, instead of reminding it again, add a pre-commit hook that blocks commits when typecheck fails.
- **Prohibited synonyms**: "adding a rule", "writing it down", "updating the prompt"

---

### Rule Promotion

- **Name**: Rule Promotion
- **Definition**: The act of moving a rule from a less enforced layer to a more enforced layer. Typically: from human memory → text rule (Layer A/B) → automated hook (Layer C). Triggered when the same violation occurs 2+ times, when a verification is frequently forgotten, or when the failure cost is high.
- **Differs from**: Adding a new rule (rule promotion moves an existing rule up the enforcement stack; adding a new rule creates new policy). Failure absorption (failure absorption is the full process; rule promotion is the specific action within that process).
- **Example**: Promoting "always run typecheck" from a line in AGENTS.md to a pre-commit hook.
- **Prohibited synonyms**: "escalating the rule", "hardening the rule", "making it a hook"

---

## Project-Specific Terms

Add project-specific terms below this line using the same format.

### [Term Name]

- **Name**:
- **Definition**:
- **Differs from**:
- **Example**:
- **Prohibited synonyms**:
