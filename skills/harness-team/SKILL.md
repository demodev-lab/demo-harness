---
name: harness-team
description: "Design and scaffold an agent team architecture for a domain or project. Use when building multi-agent systems, designing agent teams, creating orchestration workflows, or when the user says 'harness team', 'design agent team', 'build agent team', 'scaffold agents', 'create agent architecture', 'set up agent team', or 'orchestrate agents'. Also triggers on requests like 'build me a research team', 'create a code review team', or 'design a content pipeline'."
---

## Purpose

Design domain-specific agent team architectures by analyzing the project, selecting an architecture pattern, defining specialized agents, generating skills for each agent, and creating an orchestrator to coordinate the team. This skill bridges the gap between harness governance (rules, hooks, gates) and harness execution (who does what, how they collaborate).

Based on the Agent Team & Skill Architect methodology by revfactory/harness.

## Core Principle

Agents define WHO does the work. Skills define HOW the work is done. The orchestrator defines WHEN and in what ORDER the team collaborates. Separating these concerns makes the system composable, testable, and reusable.

## Workflow

### Phase 1: Domain Analysis

1. Identify the domain and project scope from the user request
2. Enumerate core work types (generation, verification, editing, analysis, research)
3. Scan existing agents and skills to prevent duplication or conflicts
4. Explore the codebase for technology stack, data models, and key modules
5. Detect user expertise level from conversation context — adjust communication accordingly

### Phase 2: Team Architecture Design

#### Execution Mode Selection

Default to **Agent Team** mode (TeamCreate + SendMessage + TaskCreate) when 2+ agents need collaboration. Use **Sub-agent** mode (Agent tool direct invocation) only for single agents or result-passing-only workflows.

| Mode | Mechanism | Best For |
|------|-----------|----------|
| Agent Team | TeamCreate + SendMessage + TaskCreate | 2+ agents, collaboration needed |
| Sub-agent | Agent tool with run_in_background | Single agent, no inter-agent communication |

#### Architecture Pattern Selection

Select from 6 patterns based on work structure. Detailed patterns and decision criteria: `references/agent-design-patterns.md`.

| Pattern | Structure | Best For |
|---------|-----------|----------|
| **Pipeline** | Sequential stages | Strong dependencies between stages |
| **Fan-out/Fan-in** | Parallel then aggregate | Independent perspectives on same input |
| **Expert Pool** | Contextual routing | Input-dependent handler selection |
| **Producer-Reviewer** | Generate then validate | Quality assurance with objective criteria |
| **Supervisor** | Central dynamic distribution | Variable workloads, runtime allocation |
| **Hierarchical Delegation** | Multi-level recursive breakdown | Naturally hierarchical problems |

#### Agent Separation Criteria

Evaluate each potential agent on 4 axes:

| Axis | Separate if... | Integrate if... |
|------|----------------|-----------------|
| Expertise | Different domains | Overlapping domains |
| Parallelism | Independent execution possible | Sequential dependency |
| Context | Heavy context burden | Light and fast |
| Reusability | Used across multiple teams | Single-team only |

### Phase 3: Agent Definition Generation

Generate agent definition files at `project/.claude/agents/{name}.md`. Every agent MUST have a definition file — never embed agent instructions solely in the Agent tool's prompt parameter.

Required sections per agent file:
1. **Core Role** — one-sentence purpose
2. **Work Principles** — behavioral guidelines with WHY explanations
3. **Input/Output Protocol** — what the agent receives and produces
4. **Error Handling** — how to handle failures (retry once, then escalate or skip)
5. **Collaboration** — who this agent communicates with and how

For Agent Team mode, add a **Team Communication Protocol** section specifying:
- Message recipients (SendMessage targets)
- Task request scope (what tasks this agent can create/claim)
- Discovery sharing rules (when to notify teammates of relevant findings)

Model setting: Use `model: "opus"` for all agents by default. Harness quality depends on agent reasoning capability.

### Phase 4: Skill Generation

Generate skills at `project/.claude/skills/{name}/skill.md` for each agent. Follow the skill writing guide in `references/skill-writing-guide.md`.

Key writing principles:
- **Description is the trigger** — write it aggressively ("pushy") with specific actions AND trigger scenarios
- **Why over rules** — explain WHY something works, not just "always do X". Agents generalize better from principles.
- **Progressive Disclosure** — keep skill.md under 500 lines. Move details to `references/`. Load conditionally.
- **Generalize** — extract principles from examples, not narrow rules. Prevent overfitting.
- **Bundle repeated scripts** — if 3+ tests generate the same helper, bundle it in `scripts/`

Skill-Agent relationship:
- 1 agent : 1-N skills (each agent has 1 or more skills)
- Shared skills across agents are allowed
- Skills define HOW, agents define WHO

### Phase 5: Orchestration

Create an orchestrator skill that coordinates the entire team workflow. Templates: `references/orchestrator-template.md`.

Data flow protocol (Agent Team mode):

| Strategy | Mechanism | Best For |
|----------|-----------|----------|
| Message-based | SendMessage | Real-time coordination, feedback exchange |
| Task-based | TaskCreate/TaskUpdate | Progress tracking, dependency management |
| File-based | Write to `_workspace/` paths | Large artifacts, structured outputs, audit trail |

Recommended combination: Task-based (coordination) + File-based (artifacts) + Message-based (real-time).

Error handling rules:
- 1 agent failure → confirm and retry once
- Same error twice → skip with explicit gap notation
- >50% team failure → escalate to user
- Data conflicts → never delete; version by source

Team size guidelines:

| Scale | Team Size | Tasks per Member |
|-------|-----------|-----------------|
| Small (5-10 tasks) | 2-3 | 3-5 |
| Medium (10-20 tasks) | 3-5 | 4-6 |
| Large (20+ tasks) | 5-7 | 4-5 |

### Phase 6: Verification and Testing

Validate the generated harness. Detailed methodology: `references/skill-testing-guide.md`.

1. **Structure verification** — all agent files exist, skill frontmatter is valid, no cross-reference conflicts
2. **Execution mode verification** — communication paths, task dependencies, team size appropriateness
3. **Skill execution testing** — 2-3 realistic test prompts per skill with With-skill vs Without-skill comparison
4. **Trigger verification** — 8-10 should-trigger + 8-10 should-NOT-trigger queries per skill
5. **Dry-run testing** — orchestrator phase order, data flow dead links, input-output matching
6. **QA boundary verification** — cross-boundary coherence checks (reference `references/qa-agent-guide.md`)

QA priorities:
- Boundary-crossing verification over existence checks
- "Read both sides simultaneously" for cross-agent handoffs
- Incremental QA after each module, not post-build only

## Output Checklist

After generation, verify:
- [ ] `project/.claude/agents/` — agent definition files exist (even for built-in types)
- [ ] `project/.claude/skills/` — skill files with skill.md + references/
- [ ] 1 orchestrator skill (data flow + error handling + test scenarios)
- [ ] Execution mode explicitly stated (Agent Team or Sub-agent)
- [ ] All Agent calls include `model: "opus"` parameter
- [ ] No `.claude/commands/` generated
- [ ] No conflicts with existing agents/skills
- [ ] Skill descriptions are aggressive ("pushy") trigger-inducing
- [ ] skill.md bodies under 500 lines; overflow moved to references/
- [ ] 2-3 test prompts verified per skill
- [ ] Trigger validation (should-trigger + should-NOT-trigger) completed

## Integration with Harness Engineering

This skill connects to the broader harness governance system:
- **Layer A**: Agent separation criteria and team principles go into AGENTS.md
- **Layer B**: Generated skills are Layer B contextual execution documents
- **Layer C**: QA boundary checks can be promoted to hooks via `/rule-promote`
- **Layer D**: Team design decisions and architecture rationale are recorded for future reference

When failures occur in agent team workflows, use `/failure-absorb` to classify and route them. Repeated team coordination failures may indicate architecture pattern mismatch — use `/harness-audit` to diagnose.

## References

- `references/agent-design-patterns.md` — 6 architecture patterns, agent separation criteria, execution mode comparison
- `references/orchestrator-template.md` — orchestrator templates for both modes, data flow, error handling
- `references/team-examples.md` — 5 real team configuration examples with full file contents
- `references/skill-writing-guide.md` — skill writing patterns, progressive disclosure, description optimization
- `references/skill-testing-guide.md` — testing methodology, assertion-based grading, iteration loops
- `references/qa-agent-guide.md` — QA patterns, boundary-crossing verification, 7 real bug cases
