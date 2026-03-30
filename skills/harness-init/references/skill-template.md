# Skill Template

Use this template when creating a new Layer B skill. A skill defines the procedure for one specific, repeatable work type. It is loaded into context only when that work type is active, keeping the main context clean.

One skill covers one work type only. If a skill is being used for two unrelated task types, split it.

---

## Template

Copy the block below into a new file named after the work type (e.g., `skills/db-migration/SKILL.md`).

```md
---
name: [skill-name]
description: Use when [specific trigger condition].
---

## When To Use

List the specific conditions under which this skill should be loaded. Be concrete — a skill loaded unnecessarily pollutes context.

- [Condition 1]
- [Condition 2]
- [Condition 3]

Do NOT use this skill when:
- [Counter-condition 1]
- [Counter-condition 2]

## Steps

Execute in order. Do not skip steps. If a step cannot be completed, stop and report the blocker rather than proceeding.

1. [First action — specific and verifiable]
2. [Second action]
3. [Third action]
4. [Fourth action]
5. [Fifth action — typically verification]
6. [Sixth action — typically docs update]

## Verification

Run these checks before reporting this task complete. Do not report complete until all checks pass.

- [ ] [Specific verification command or check]
- [ ] [Second verification]
- [ ] [Third verification — typically docs/contract check]

## Common Mistakes

Failures that have been observed when this work type is performed without this skill. Each entry here represents a real absorbed failure.

- **[Mistake name]**: [What goes wrong and why. What to do instead.]
- **[Mistake name]**: [What goes wrong and why. What to do instead.]
- **[Mistake name]**: [What goes wrong and why. What to do instead.]

## Related Documents

- [Link to relevant doc]
- [Link to related skill]
- [Link to relevant glossary entries]
```

---

## Filled Example: API Endpoint Workflow

```md
---
name: api-endpoint-workflow
description: Use when adding or changing API endpoints.
---

## When To Use

- New endpoint is being added
- Request or response schema is changing
- Authentication or validation logic is changing
- Endpoint is being deprecated or removed

Do NOT use this skill when:
- Only internal business logic is changing with no API surface impact
- Only tests for an existing stable endpoint are being updated

## Steps

1. Read the API contract docs and OpenAPI spec before writing any code.
2. Check existing endpoint patterns — auth middleware, error response shape, pagination format.
3. Update the schema first (OpenAPI spec or equivalent). Get schema reviewed before implementation.
4. Implement the handler following existing patterns.
5. Add or update tests: happy path, auth failure, validation failure, error paths.
6. Update docs and examples. Confirm OpenAPI spec matches implementation.

## Verification

- [ ] Run endpoint tests: `npm test -- --grep "api"`
- [ ] Run typecheck: `tsc --noEmit`
- [ ] Confirm OpenAPI spec was updated if contract changed
- [ ] Confirm auth and error paths are tested

## Common Mistakes

- **Forgetting schema updates**: Implementing the handler before updating the schema leads to drift between spec and code. Schema first, always.
- **Changing response shape without docs**: Downstream consumers break silently. Always update OpenAPI spec in the same commit.
- **Skipping auth and error-path tests**: Happy path tests pass but production incidents occur on edge cases. Tests must cover at least one auth failure and one validation failure.
- **Copying an old endpoint pattern**: Old endpoints may not follow current conventions. Check the most recent endpoint added, not the most familiar one.

## Related Documents

- `docs/api-contracts/README.md`
- `docs/glossary/README.md` — see "endpoint", "schema", "contract"
```

---

## Separation Criteria

Extract a new skill when:
- A task type recurs at least twice
- The task has a defined sequence of steps that an agent consistently gets wrong or skips
- The steps are conditional (only apply to this task type, not all tasks)

Do not create a skill for:
- One-time tasks with no expected recurrence
- Tasks with fewer than 3 steps
- Tasks already fully covered by a checklist in an existing skill

## Size Guidance

A well-formed skill is typically 30-80 lines. If a skill exceeds 100 lines, consider whether it covers multiple distinct work types that should be split.

## Description Writing (Trigger Optimization)

The description field is the ONLY trigger mechanism. Write it aggressively:

**Weak:** `"Process PDF documents."`
**Strong:** `"PDF manipulation: read, extract text/tables, merge, split, rotate, watermark, encrypt, OCR. Use whenever a .pdf file is mentioned or PDF output is requested."`

Rules:
- Name specific actions the skill handles
- Name specific trigger scenarios
- Distinguish from similar skills that should NOT trigger

## Skill Writing Principles

From the Agent Team & Skill Architect methodology:

1. **Why over rules** — explain WHY something works, not "ALWAYS do X". Agents generalize better from principles than commands.
2. **Progressive Disclosure** — keep skill.md under 500 lines. Move detailed content to `references/`. Load conditionally.
3. **Generalize** — extract principles from test feedback, not narrow rules. Bad: "if column is Q4_Sales, convert". Good: "if column name suggests numeric (Sales/Amount), convert".
4. **Bundle repeated scripts** — if 3+ test runs generate the same helper script, bundle it in `scripts/`.
5. **Imperative voice** — use command form ("Read the file", "Run the tests"), not advisory ("You should read the file").
