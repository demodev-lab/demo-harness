# AGENTS.md Template

Use this template when initializing a new project with the Harness Engineering Plugin. Replace `{{project_name}}` with the actual project name. Keep the final document within 40-60 lines — remove any sections that don't apply universally to your project.

---

```md
# {{project_name}} Operating Contract

## Core Rules

- Solve the task directly when safe. When uncertainty exists, surface it rather than guessing.
- Update related docs when contracts, APIs, architecture, or schemas change. Documentation and code change together, never separately.
- Reuse existing modules, patterns, and terminology before adding new abstractions or dependencies.
- Verify before claiming completion. Completion claims require verification logs or test results, not assumptions.
- Do not use destructive commands (force push, hard reset, drop table, rm -rf) unless explicitly approved by a human in the current session.
- When using agent teams, define every agent in `.claude/agents/` with a definition file — never embed agent instructions solely in prompt parameters.

## Workflow

- Read relevant docs and existing patterns before editing any file.
- Keep diffs small and reversible. Large sweeping changes require explicit approval.
- Use project-standard commands for lint, typecheck, and tests. Do not invent alternative verification methods.
- When structure, contracts, policies, or APIs change, update related docs in the same commit or session.
- If a mistake repeats, encode the prevention into the harness — rule, skill, hook, or document — rather than relying on future memory.
- When new concepts or terms emerge, define them in the glossary before using them in code or docs.

## Sub-Agent Use

- Sub-agents are context firewalls, not role-play. Use them to isolate large searches or parallel verification tasks.
- Main thread handles direction and integration. Sub-agents handle narrow, verifiable work only.
- Do not delegate core blocked tasks to sub-agents. Do not delegate exploration without reading first.
- Pass sub-agent results up as summaries only — do not flood the main thread with raw output.

## Completion

- Report which files changed.
- Report which verification commands were actually run and their results.
- Report remaining risks, gaps, or deferred items honestly.
- Do not report "complete" when tests were skipped, lint was not run, or docs were not updated for changed contracts.

## Anti-Patterns (Never Do)

- Do not lengthen this document with every new failure. Absorb repeated failures into skills or hooks instead.
- Do not assume humans will remember context between sessions. Make rules explicit.
- Do not paste entire directory trees into documents. Link to specific files.
- Do not cover small problems with new abstractions or dependencies.
- Do not separate documentation from operating contracts — docs that aren't enforced are decoration.
```

---

## Template Usage Notes

### What belongs here

Layer A (Constitutional Documents) contains only rules that apply to every task, every session, every developer. If a rule is conditional — "only when doing migrations" or "only for API endpoints" — it does not belong here. Move it to a skill (Layer B).

The 10 operating principles that must be reflected in every AGENTS.md:

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

### What does not belong here

- Long step-by-step procedures → extract as a skill (Appendix B format)
- Conditional branching rules ("if X then Y") → extract as a skill
- Feature-specific instructions → extract as a skill or runbook
- Detailed directory maps → link to a doc instead
- Rules that apply only to one task type → extract as a skill

### Size discipline

Keep AGENTS.md within 40-60 lines. When it grows beyond 60 lines, that is a signal that conditional rules have been added to global scope. Audit the document and extract anything that is not universal.

### Sub-agent principles reminder

Sub-agents are context firewalls (section 8 of the Harness Engineering Manual):
- Main thread handles direction and integration
- Sub-agents handle narrow, verifiable work only
- Sub-agent results are passed up as summaries, not raw output
- When the same mistake pattern repeats, improve the harness before adding sub-agents

### When to update this document

Update AGENTS.md only when:
- A rule needs to apply to every task without exception
- A failure that occurred has no existing layer to absorb it
- A principle has been validated across at least two sessions

Do not update AGENTS.md:
- As a first response to a single failure
- To add task-specific instructions
- To record one-time decisions
