---
name: harness-import
description: 기존 프로젝트에 하네스 거버넌스를 도입한다. 기존 CLAUDE.md, AGENTS.md, hooks.json, docs/ 파일을 스캔하고 하네스 템플릿과 diff/merge 계획을 생성한다.
---

## Purpose

기존 프로젝트(brownfield)에 하네스 운영 체계를 이식한다. harness-init은 빈 프로젝트를 대상으로 전체 파일 세트를 생성하지만, harness-import는 이미 거버넌스 파일이 존재하는 프로젝트를 대상으로 충돌 없이 하네스를 병합한다.

핵심 원칙: 기존 내용을 덮어쓰지 않는다. 스캔 → 비교 → 리포트 → 사용자 승인 → 실행의 순서를 엄격히 따른다. 승인 없이 파일을 수정하거나 생성하지 않는다.

---

## When To Use

- 이미 CLAUDE.md, AGENTS.md, hooks.json 등이 존재하는 프로젝트에 하네스를 도입할 때
- 기존 프로젝트의 거버넌스를 하네스 표준으로 마이그레이션할 때
- 사용자가 "harness import", "import harness", "기존 프로젝트 하네스 도입", "brownfield harness" 라고 말할 때
- harness-init을 실행했으나 기존 파일과 충돌이 발생했을 때

---

## Workflow

### Step 1 — Scan: 기존 파일 탐색

프로젝트 루트에서 다음 파일들을 탐색한다. 파일 존재 여부와 줄 수(line count)를 기록한다.

탐색 대상 파일 목록은 `${CLAUDE_PLUGIN_ROOT}/skills/harness-import/references/import-checklist.md`를 참조한다.

핵심 탐색 대상:

| 파일 경로 | 역할 | 하네스 레이어 |
|-----------|------|--------------|
| `AGENTS.md` | Constitutional document | Layer A |
| `CLAUDE.md` | Claude operating contract | Layer A |
| `.claude/hooks.json` | Automated enforcement | Layer C |
| `docs/failure-log.md` | Failure ledger | Layer D |
| `docs/glossary/README.md` | Terminology registry | Layer D |
| `docs/completion-checklist.md` | Pre-completion gate | Layer C |
| `docs/weekly-review-template.md` | Retrospective template | Layer D |
| `docs/operating-principles.md` | Operating principles | Layer D |
| `docs/architecture-notes.md` | Architecture decisions | Layer D |
| `skills/*/SKILL.md` | Contextual execution skills | Layer B |

존재하지 않는 파일은 "누락(missing)" 으로 분류한다. 파일 내용은 Step 2에서 읽는다.

### Step 2 — Compare: 템플릿과 diff 생성

존재하는 각 파일을 harness-init 템플릿과 비교한다. 템플릿 경로: `${CLAUDE_PLUGIN_ROOT}/skills/harness-init/references/`

각 파일에 대해 다음을 확인한다:

**AGENTS.md 비교 기준:**
- 줄 수가 40–60 lines 범위인가
- 5개 core directive가 모두 포함되어 있는가 (solve directly, update docs, reuse modules, verify before completion, no destructive commands)
- Completion 섹션이 있는가
- Anti-Patterns 섹션이 있는가

**.claude/hooks.json 비교 기준:**
- JSON이 유효한가 (파싱 가능한가)
- `matchers` 배열 구조를 따르는가
- completion gate 역할의 hook이 하나 이상 있는가
- 각 hook entry에 `description` 필드가 있는가

**docs/failure-log.md 비교 기준:**
- 헤더 행(Date, Failure Description, Cause Category, Absorption Action, Verification Method)이 있는가
- 예제 행이 없는가 (실제 항목만 있어야 함)

**skills/*/SKILL.md 비교 기준:**
- frontmatter(`name`, `description`)가 있는가
- When To Use, Workflow, Verification, Common Mistakes 섹션이 있는가

### Step 3 — Report: 3가지 분류로 리포트 출력

스캔 및 비교 결과를 다음 형식으로 출력한다:

```
Harness Import Scan — <project-name>
=====================================

[유지] 이미 있고 호환 가능
  AGENTS.md             52 lines — core directives 5개 확인, 범위 정상
  docs/failure-log.md   헤더 정상, 실제 항목 3개

[충돌] 이미 있지만 하네스 표준과 불일치 — 사용자 확인 필요
  .claude/hooks.json    hooks 배열 구조 없음 (구버전 형식)
  docs/glossary/README.md  용어 정의 형식이 하네스 5-field 형식과 다름

[누락] 없음 — 자동 생성 제안
  docs/completion-checklist.md
  docs/weekly-review-template.md
  docs/operating-principles.md
```

리포트를 출력한 후 Step 4로 진행하기 전에 반드시 멈추고 사용자의 지시를 기다린다.

### Step 4 — Merge Plan: 충돌 파일 merge 전략 제안

[충돌] 분류의 각 파일에 대해 구체적인 merge 전략을 제안한다.

Merge 전략 원칙:
- **기존 내용 보존**: 프로젝트 고유 규칙, 커스텀 설정은 유지한다
- **하네스 구조 추가**: 누락된 섹션, 필드, hook entry를 추가한다
- **덮어쓰기 금지**: 기존 값을 하네스 기본값으로 교체하지 않는다

각 충돌 파일에 대한 제안 형식:

```
[충돌] .claude/hooks.json
  현재 상태: matchers 배열 없이 직접 hooks 배열 사용
  필요한 변경: matchers[].hooks[] 구조로 감싸기
  보존 내용: 기존 command, 기존 matcher 패턴
  추가 내용: description 필드, completion gate hook entry
  작업 규모: 낮음 (구조 리팩토링, 내용 보존)
```

[누락] 분류의 파일들은 harness-init 템플릿 기반으로 생성을 제안한다. 단, 프로젝트 이름과 스택을 먼저 확인한다.

### Step 5 — Execute: 사용자 승인 후 실행

Step 3 리포트와 Step 4 merge 전략을 제시한 후, **사용자 명시적 승인**을 받은 항목에 대해서만 실행한다.

실행 순서:
1. [누락] 파일 생성 — harness-init 템플릿 기반
2. [충돌] 파일 merge — 승인된 전략에 따라 수정
3. [유지] 파일 — 변경하지 않음

각 파일 수정/생성 후 즉시 결과를 확인하고 다음 파일로 진행한다.

사용자가 특정 파일의 변경을 거부하면 해당 파일은 건너뛰고 나머지를 계속 진행한다.

### Step 6 — Verify: 결과 확인

모든 실행 완료 후 `validate-harness-integrity.py`가 프로젝트에 존재하면 실행한다.

```bash
python hooks/scripts/validate-harness-integrity.py
```

스크립트가 없으면 다음 수동 확인을 수행한다:

- [ ] `AGENTS.md` 존재 및 40–60 lines 범위
- [ ] `.claude/hooks.json` JSON 유효성 — `python -c "import json; json.load(open('.claude/hooks.json'))"`
- [ ] `docs/failure-log.md` 헤더 행 확인
- [ ] 새로 생성된 파일 수 확인

최종 요약을 출력한다:

```
Harness Import 완료 — <project-name>

실행 결과:
  생성: <n>개 파일
  수정: <n>개 파일
  건너뜀: <n>개 파일 (사용자 거부 또는 이미 호환)

다음 단계:
  - 검증 명령 실행: <lint/typecheck/test 명령>
  - weekly-review 스킬로 초기 상태 점검
  - failure-log.md에 기존 실패 이력 추가
```

---

## 실행 시 주의사항

- **승인 없이 파일 수정 금지**: Step 3 리포트 출력 후 반드시 대기
- **덮어쓰기 금지**: 기존 파일을 템플릿으로 교체하지 않음. 항상 merge
- **부분 실행 허용**: 사용자가 일부 항목만 승인해도 그 항목만 실행
- **AGENTS.md 줄 수 준수**: merge 후에도 60 lines 이하 유지. 초과하면 초과 규칙을 skill로 이동 제안
- 기존 `.claude/hooks.json`이 구버전 형식일 경우, 마이그레이션 전 백업 제안

---

## Common Mistakes

- Step 3 리포트 없이 바로 파일을 수정하는 것 — 스캔과 리포트가 먼저다
- [유지] 분류 파일에 "개선"을 추가하는 것 — harness-import는 하네스 구조 도입만 담당한다
- 사용자 승인 없이 [충돌] 파일을 덮어쓰는 것 — 항상 merge 전략을 먼저 제시한다
- AGENTS.md merge 후 줄 수를 확인하지 않는 것 — 60 lines 초과는 즉시 경고
- 기존 hooks.json의 command를 하네스 기본 command로 교체하는 것 — 기존 command는 항상 보존

---

## Reference Files

| 파일 | 사용 단계 |
|------|----------|
| `${CLAUDE_PLUGIN_ROOT}/skills/harness-import/references/import-checklist.md` | Step 1 탐색 대상 목록 |
| `${CLAUDE_PLUGIN_ROOT}/skills/harness-init/references/agents-md-template.md` | Step 2 AGENTS.md 비교 기준 |
| `${CLAUDE_PLUGIN_ROOT}/skills/harness-init/references/hooks-template.json` | Step 2 hooks.json 비교 기준 |
| `${CLAUDE_PLUGIN_ROOT}/skills/harness-init/references/failure-log-template.md` | Step 4 누락 파일 생성 |
