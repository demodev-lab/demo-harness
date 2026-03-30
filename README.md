# Harness Engineering

Harness Engineering Manual을 구현한 Claude Code 플러그인.

AI 기반 개발에서 실패를 규칙으로 흡수하는 운영 시스템을 자동으로 구축하고, 도메인에 맞는 에이전트 팀 아키텍처를 설계한다.

## 설치

### 마켓플레이스에서 설치 (권장)

```bash
# 1. 마켓플레이스 등록
claude plugin marketplace add demodev-lab/demo-harness

# 2. 플러그인 설치
claude plugin install harness-engineering@demo-harness
```

### 로컬 설치

```bash
# 저장소 클론 후 직접 설치
git clone https://github.com/demodev-lab/demo-harness.git
claude plugin install --path ./demo-harness
```

### 글로벌 스킬로 설치

```bash
# skills 디렉토리만 복사하여 사용
cp -r demo-harness/skills/* ~/.claude/skills/
```

### 설치 확인

```bash
# 설치된 플러그인 목록 확인
claude plugin list

# 스킬 트리거 테스트 — Claude Code에서 아래 입력
/harness-init
```

## 빠른 시작

```
1. 플러그인 설치
2. 아무 프로젝트에서 `/harness-init` 실행
3. 작업 시작 — hook이 자동으로 활성화됨
```

### 첫 프로젝트에 적용하기

```
# Step 1: harness 운영 체계 생성
> /harness-init

# Step 2: 에이전트 팀 설계 (선택)
> /harness-team

# Step 3: 작업 중 실패가 발생하면
> /failure-absorb

# Step 4: 매주 한 번 회고
> /weekly-review
```

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

플러그인 설치 후 별도 설정 없이 자동으로 활성화된다.

| Hook | 이벤트 | 타입 | 용도 |
|------|--------|------|------|
| **completion-gate** | Stop | Command + Prompt | 완료 전 테스트/타입체크/문서 갱신/검증 로그를 점검 |
| **docs-change-check** | PostToolUse (Edit/Write) | Command | API/계약 파일 변경 시 문서 갱신 알림 |
| **destructive-cmd-block** | PreToolUse (Bash) | Command | 파괴적 명령 차단 (rm -rf, DROP TABLE, force-push 등) |

검증 보조 스크립트:
- `python3 hooks/scripts/validate-harness-integrity.py` — 필수 파일/참조/후크 경로/실행권한 점검
- `python3 hooks/scripts/harness-hook-selftest.py` — hook 스크립트 동작 회귀 테스트

### Agents (2개)

skill에서 복잡한 분석이 필요할 때 자동으로 위임된다.

| Agent | 용도 |
|-------|------|
| **failure-analyzer** | 실패 심층 분석 — 6개 카테고리로 분류하고 흡수 레이어 추천 |
| **harness-auditor** | harness 건강 점검 — 비대화, 중복, 충돌, 안티패턴 탐지 |

## 동작 원리

### 4개 레이어

harness는 규칙을 4개 레이어로 분리한다:

| 레이어 | 위치 | 용도 | 예시 |
|--------|------|------|------|
| **A (헌법)** | `AGENTS.md` | 모든 작업에 적용되는 불변 규칙 | "완료 전 검증 필수" |
| **B (상황별)** | Skills, runbooks | 특정 작업 유형에만 적용 | "API 변경 시 스키마 먼저 수정" |
| **C (자동 강제)** | Hooks, scripts | 기계적 자동 검증 | completion-gate, destructive-cmd-block |
| **D (기억)** | Glossary, postmortem | 미래 세션을 위한 지식 | 실패 기록, 아키텍처 결정 노트 |

### 실패 흡수 루프

harness의 핵심 운영 루프. 실패를 수동 수정으로 끝내지 않고 시스템 규칙으로 흡수한다.

```
실패 발생
  ↓
① 식별 — 실패에 이름을 붙인다
  ↓
② 분류 — 6개 카테고리 중 하나로 분류
  │  1. 전역 규칙 부재
  │  2. 특정 작업 절차 부재
  │  3. 도구/검증 자동화 부재
  │  4. 용어/문서 불일치
  │  5. 과도한 컨텍스트 오염
  │  6. 권한/책임 경계 불명확
  ↓
③ 결정 — 어느 레이어에서 막을지 결정
  │  모든 작업 해당 → Layer A (AGENTS.md)
  │  특정 작업만 → Layer B (skill/runbook)
  │  반복 위반 → Layer C (hook/script)
  │  미래 참고 → Layer D (docs/glossary)
  ↓
④ 흡수 — 규칙, skill, hook, 문서 중 하나로 흡수
  ↓
⑤ 검증 — 다음 동일 작업에서 방지되는지 확인
```

### 에이전트 팀 아키텍처

`/harness-team`으로 도메인에 맞는 에이전트 팀을 설계한다. [revfactory/harness](https://github.com/revfactory/harness) 방법론 기반 6가지 아키텍처 패턴 지원:

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

- **Bash 명령 전**: `rm -rf /`, `DROP TABLE`, `git push --force` 등 파괴적 패턴 즉시 차단
- **파일 수정 후**: API/계약/스키마 파일 변경 감지 시 문서 갱신 알림
- **작업 완료 시**: 테스트 실행 여부, 타입체크, 문서 갱신, 검증 로그 체크리스트 확인

## 사용 사례

### 새 프로젝트 시작

```
/harness-init
```
AGENTS.md, glossary, failure log, weekly review 템플릿, hook 설정 등 10+개 파일을 자동 생성한다.

### 에이전트 팀 구축

```
코드 리뷰 에이전트 팀을 설계해줘
```
또는
```
/harness-team
```
도메인을 분석하고, 아키텍처 패턴을 선택하고, 에이전트 정의와 스킬을 자동 생성한다.

### 실패 발생 시

```
/failure-absorb
```
실패를 6개 카테고리로 분류하고, 적절한 레이어(A-D)에 흡수한다. 복잡한 경우 `failure-analyzer` agent에게 자동 위임한다.

### 규칙을 hook으로 승격

```
/rule-promote
```
같은 실수가 2번 이상 반복되면, 문장 규칙을 자동 hook으로 전환한다.

### 주간 회고

```
/weekly-review
```
실패 로그를 읽고 반복 패턴을 추출한다. 규칙 승격 후보와 정리 대상을 제안한다.

### harness 건강 점검

```
/harness-audit
```
규칙 중복, 8주 이상 미사용, 충돌, 안티패턴을 탐지한다. 심층 분석은 `harness-auditor` agent에게 위임한다.

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
| [revfactory/harness](https://github.com/revfactory/harness) 방법론 | `harness-team` skill (6가지 아키텍처 패턴, 오케스트레이터, QA) |

## 플러그인 구조

```
harness/
├── .claude-plugin/
│   ├── plugin.json                 # 플러그인 매니페스트
│   └── marketplace.json            # 마켓플레이스 등록 정보
├── skills/
│   ├── harness-init/               # 프로젝트 초기화
│   │   ├── SKILL.md
│   │   └── references/ (12 templates)
│   ├── harness-team/               # 에이전트 팀 설계
│   │   ├── SKILL.md
│   │   └── references/ (6 guides)
│   ├── failure-absorb/             # 실패 흡수
│   │   ├── SKILL.md
│   │   └── references/ (3 docs)
│   ├── weekly-review/              # 주간 회고
│   │   ├── SKILL.md
│   │   └── references/ (1 template)
│   ├── harness-audit/              # 건강 점검
│   │   ├── SKILL.md
│   │   └── references/ (2 docs)
│   └── rule-promote/               # 규칙 승격
│       ├── SKILL.md
│       └── references/ (1 doc)
├── agents/
│   ├── failure-analyzer.md         # 실패 분석 에이전트
│   └── harness-auditor.md          # 건강 점검 에이전트
├── hooks/
│   ├── hooks.json                  # hook 설정
│   └── scripts/
│       ├── block-destructive.sh    # 파괴적 명령 차단
│       ├── block-destructive.py
│       ├── check-docs-change.py    # 문서 변경 감지
│       ├── completion-gate.py      # 완료 게이트
│       ├── validate-harness-integrity.py
│       └── harness-hook-selftest.py
└── README.md
```

## 요구사항

- [Claude Code](https://claude.ai/code) CLI 또는 데스크톱 앱
- 에이전트 팀 기능 사용 시: `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1`

## 크레딧

- Harness Engineering Manual 원칙 기반
- 에이전트 팀 아키텍처: [revfactory/harness](https://github.com/revfactory/harness) 방법론 흡수

## License

MIT
