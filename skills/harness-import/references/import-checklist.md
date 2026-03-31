# Harness Import Checklist

harness-import skill의 Step 1에서 탐색할 파일 목록과 각 파일의 기대 구조를 정의한다.

---

## Layer A — Constitutional Documents

### AGENTS.md

**탐색 경로**: `<project-root>/AGENTS.md`

**기대 구조:**
- 총 40–60 lines
- `## Core Rules` 섹션 포함
- 5개 core directive 포함:
  1. 직접 해결 (solve directly)
  2. 계약 변경 시 문서 업데이트 (update docs on contract changes)
  3. 기존 모듈 재사용 (reuse modules)
  4. 완료 전 검증 (verify before claiming completion)
  5. 파괴적 명령 금지 (no destructive commands without approval)
- `## Workflow` 섹션 포함
- `## Completion` 섹션 포함
- `## Anti-Patterns` 섹션 포함
- 조건부 규칙(if/else) 없음
- 디렉토리 트리 없음

**호환 판정 기준**: 5개 core directive 중 3개 이상 포함 + 60 lines 이하

---

### CLAUDE.md

**탐색 경로**: `<project-root>/CLAUDE.md`

**기대 구조:**
- Claude 특화 동작 계약
- 응답 형식 지침
- 도구 사용 지침
- AGENTS.md와 동일한 핵심 규칙 반영

**호환 판정 기준**: 파일 존재 + 비어있지 않음

---

## Layer B — Contextual Execution Skills

### skills/*/SKILL.md

**탐색 경로**: `<project-root>/skills/`의 모든 하위 디렉토리

**기대 구조 (각 SKILL.md):**
```
---
name: <skill-name>
description: <description>
---

## When To Use
...

## Workflow / Steps
...

## Verification
...

## Common Mistakes
...
```

**호환 판정 기준**: frontmatter(`name`, `description`) 존재 + When To Use 섹션 존재

---

## Layer C — Automated Enforcement

### .claude/hooks.json

**탐색 경로**: `<project-root>/.claude/hooks.json`

**기대 구조 (현재 harness 형식):**
```json
[
  {
    "matcher": "<pattern>",
    "hooks": [
      {
        "type": "command",
        "command": "<command>",
        "description": "<description>"
      }
    ]
  }
]
```

**비호환 신호:**
- 최상위가 배열이 아닌 객체인 경우 (구버전 형식)
- `hooks` 배열 없이 직접 `command` 필드를 가진 경우
- `description` 필드가 없는 hook entry
- JSON 파싱 불가

**호환 판정 기준**: 유효한 JSON + matchers 배열 구조 + 각 entry에 `description` 필드

---

### docs/completion-checklist.md

**탐색 경로**: `<project-root>/docs/completion-checklist.md`

**기대 구조:**
- 정확히 5개의 체크리스트 항목
- 각 항목: `- [ ] <질문>` 형식
- 다음 5가지 질문 포함:
  1. 테스트 실행 여부
  2. lint/typecheck 실행 여부
  3. 계약 변경 시 문서 업데이트 여부
  4. 사용자 가시 동작 검증 여부
  5. 잔여 리스크 기록 여부

**호환 판정 기준**: 파일 존재 + 체크박스 항목 3개 이상

---

## Layer D — Memory and Learning Artifacts

### docs/failure-log.md

**탐색 경로**: `<project-root>/docs/failure-log.md`

**기대 구조:**
```markdown
| Date | Failure Description | Cause Category | Absorption Action | Verification Method |
|------|---------------------|----------------|-------------------|---------------------|
```

- 헤더 행 존재
- 구분선(---|---) 행 존재
- 예제 행 없음 (실제 항목만)
- Append-only (삭제 금지)

**호환 판정 기준**: 헤더 행에 5개 컬럼명 중 3개 이상 포함

---

### docs/glossary/README.md

**탐색 경로**: `<project-root>/docs/glossary/README.md`

**기대 구조 (5-field 형식, Manual section 7.3):**
```markdown
## <Term Name>

**Definition**: ...
**Differences from related terms**: ...
**Examples**: ...
**Prohibited mixed expressions**: ...
```

- 최소 3개 용어 정의
- 각 용어에 5개 필드 모두 포함

**호환 판정 기준**: 파일 존재 + 용어 정의 1개 이상 (필드 수 무관)

---

### docs/operating-principles.md

**탐색 경로**: `<project-root>/docs/operating-principles.md`

**기대 구조:**
- 프로젝트에 맞게 적용된 10개 운영 원칙
- 각 원칙: 번호 + 제목 + 설명

**호환 판정 기준**: 파일 존재 + 비어있지 않음

---

### docs/architecture-notes.md

**탐색 경로**: `<project-root>/docs/architecture-notes.md`

**기대 구조 (ADR 형식):**
```markdown
## <Decision Title>

**Context**: ...
**Options considered**: ...
**Decision**: ...
**Consequences**: ...
**Date**: YYYY-MM-DD
```

**호환 판정 기준**: 파일 존재

---

### docs/weekly-review-template.md

**탐색 경로**: `<project-root>/docs/weekly-review-template.md`

**기대 구조 (Appendix D 형식):**
- `## Repeated Failures` 섹션
- `## Incomplete Absorptions` 섹션
- `## Promotion Candidates` 섹션
- `## Cleanup List` 섹션
- `## Harness Changes Executed` 섹션

**호환 판정 기준**: 파일 존재 + 섹션 2개 이상 포함

---

### docs/postmortem-template.md

**탐색 경로**: `<project-root>/docs/postmortem-template.md`

**기대 구조:**
- Timeline 섹션
- Root Cause 섹션
- Impact 섹션
- Action Items 섹션

**호환 판정 기준**: 파일 존재

---

## 탐색 우선순위

harness-import는 다음 순서로 파일을 처리한다:

1. **필수 파일** (없으면 하네스 기능 불완전): `AGENTS.md`, `.claude/hooks.json`, `docs/failure-log.md`
2. **권장 파일** (없으면 학습/회고 불가): `docs/glossary/README.md`, `docs/completion-checklist.md`, `docs/weekly-review-template.md`
3. **선택 파일** (없어도 즉시 영향 없음): `CLAUDE.md`, `docs/operating-principles.md`, `docs/architecture-notes.md`, `docs/postmortem-template.md`

필수 파일이 누락된 경우 사용자에게 생성 우선순위를 명확히 안내한다.
