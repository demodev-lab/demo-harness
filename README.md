# Harness Engineering

Harness Engineering Manual을 구현한 Claude Code 플러그인. AI 기반 개발에서 실패를 규칙으로 흡수하는 운영 시스템을 자동으로 구축한다.

## 설치

마켓플레이스에서 설치:

```
claude plugin install harness-engineering
```

로컬 설치:

```
claude plugin install --path /path/to/harness
```

## 빠른 시작

1. 플러그인 설치
2. 아무 프로젝트에서 `/harness-init` 실행
3. 작업 시작 — hook이 자동으로 활성화됨

## 구성 요소

### Skills (6개)

| Skill | 명령어 | 용도 |
|-------|--------|------|
| **harness-init** | `/harness-init` | 새 프로젝트에 harness 운영 체계 생성 (AGENTS.md, glossary, hooks, templates) |
| **harness-team** | `/harness-team` | 도메인에 맞는 에이전트 팀 아키텍처 설계 및 생성 (6가지 패턴, 오케스트레이터, QA) |
| **failure-absorb** | `/failure-absorb` | 실패를 분류하고 원인을 파악해 적절한 harness 레이어로 흡수 |
| **weekly-review** | `/weekly-review` | 주간 harness 회고 — 반복 실패 추출, 규칙 승격, 오래된 항목 정리 |
| **harness-audit** | `/harness-audit` | harness 비대화 점검 — 중복, 충돌, 미사용 규칙, 안티패턴 탐지 |
| **rule-promote** | `/rule-promote` | 반복 위반되는 문장 규칙을 자동화된 hook으로 승격 |

### Hooks (3개)

| Hook | 이벤트 | 타입 | 용도 |
|------|--------|------|------|
| completion-gate | Stop | Command + Prompt | 완료 전 테스트·타입체크·문서 갱신·검증 로그를 점검 (command hook가 1차 차단) |
| docs-change-check | PostToolUse (Edit/Write) | Command | API/계약 파일 변경 시 문서 갱신 알림 |
| destructive-cmd-block | PreToolUse (Bash) | Command | 파괴적 명령 차단 (rm -rf, DROP TABLE, force-push 등) |

검증 보조 스크립트:
- `python3 hooks/scripts/validate-harness-integrity.py` : 필수 파일/참조/후크 경로/실행권한 점검
- `python3 hooks/scripts/harness-hook-selftest.py` : hook 스크립트 동작 회귀 테스트 (rm 강제차단, completion-gate 증빙필요 조건, docs-change 감지)

### Agents (2개)

| Agent | 용도 |
|-------|------|
| **failure-analyzer** | 실패 심층 분석 — 6개 카테고리로 분류하고 흡수 레이어 추천 |
| **harness-auditor** | harness 건강 점검 — 비대화, 중복, 충돌, 안티패턴 탐지 |

## 동작 원리

### 4개 레이어

harness는 규칙을 4개 레이어로 분리한다:

- **Layer A (헌법)**: `AGENTS.md` — 모든 작업에 적용되는 불변 규칙
- **Layer B (상황별)**: Skills, runbooks — 특정 작업 유형에만 적용되는 규칙
- **Layer C (자동 강제)**: Hooks, scripts — 기계적으로 검증하는 자동화 장치
- **Layer D (기억)**: Glossary, postmortem, decision notes — 미래 세션을 위한 지식

### 실패 흡수 루프

실패가 발생하면:

1. 실패를 **식별**한다
2. 6개 카테고리 중 하나로 **분류**한다
3. 어느 레이어에서 막아야 하는지 **결정**한다
4. 규칙, skill, hook, 문서 중 하나로 **흡수**한다
5. 다음 동일 작업에서 실제로 방지되는지 **검증**한다

### 에이전트 팀 아키텍처 (revfactory/harness 방법론)

`/harness-team`으로 도메인에 맞는 에이전트 팀을 설계한다. 6가지 아키텍처 패턴 지원:

| 패턴 | 구조 | 적합한 경우 |
|------|------|------------|
| **파이프라인** | 순차 단계 | 단계 간 강한 의존성 |
| **팬아웃/팬인** | 병렬 후 통합 | 동일 입력에 대한 독립적 관점 |
| **전문가 풀** | 상황별 라우팅 | 입력에 따라 다른 처리 |
| **생성-검증** | 생성 후 품질 검수 | 객관적 기준의 QA |
| **감독자** | 중앙 동적 분배 | 가변 워크로드, 런타임 할당 |
| **계층적 위임** | 다단계 재귀 분해 | 자연적 계층 구조 |

### 자동 강제

3개 hook이 자동으로 실행된다:

- **Bash 명령 전**: 파괴적 패턴 즉시 차단
- **파일 수정 후**: API/계약 변경 시 문서 갱신 알림
- **작업 완료 시**: 테스트, 타입, 문서, 검증 로그 체크리스트 확인

## 매뉴얼 매핑

이 플러그인은 Harness Engineering Manual의 각 섹션을 구현한다:

| 섹션 | 플러그인 컴포넌트 |
|------|-------------------|
| 섹션 4: 기본 운영 원칙 | AGENTS.md 템플릿에 내장, 모든 skill에서 참조 |
| 섹션 5: 실패 흡수 절차 | `failure-absorb` skill + `failure-analyzer` agent |
| 섹션 6: 새 프로젝트 도입 | `harness-init` skill |
| 섹션 7: 문서화 원칙 | `docs-change-check` hook |
| 섹션 8: Sub-agent 원칙 | AGENTS.md 템플릿에 내장 |
| 섹션 9: Hooks와 검증 게이트 | `completion-gate` hook + `rule-promote` skill |
| 섹션 10: 유지보수 규칙 | `weekly-review` + `harness-audit` skill + `harness-auditor` agent |
| 섹션 11: 금지 패턴 | audit 점검 항목 및 AGENTS.md 템플릿에 내장 |
| 부록 A-E | `harness-init`에서 사용하는 템플릿 |
| revfactory/harness 방법론 | `harness-team` skill (6가지 아키텍처 패턴, 오케스트레이터, QA) |

## License

MIT
