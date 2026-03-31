# Changelog

모든 주요 변경 사항을 이 파일에 기록한다.

## [1.0.4] - 2026-03-31

### Added
- **session-doc-cleanup Stop hook**: 세션 종료 시 failure-log.md 반복 패턴 자동 감지 + 승격 후보 마킹
- **completion-gate 멀티 언어 패턴**: Dart/Flutter (`flutter test`, `dart analyze`), Java (`./gradlew test`, `mvn compile`, `javac`), TypeScript (`vitest`, `bun test`, `biome`, `vue-tsc`) 총 20개 패턴 추가
- **suggest-failure-absorb 패턴 확장**: `yarn ERR!`, `pnpm ERR!`, `Cannot find module`, `ClassNotFoundException`, `Unhandled Exception` 등 14개 추가
- **block-destructive 차단 추가**: `rimraf`, `docker system prune`, `git stash drop/clear`
- **check-docs-change 프레임워크 감지**: Spring Boot (`application.yml`), Next.js (`next.config.*`), Flutter (`pubspec.yaml`), Django (`urls.py`, `models.py`)
- **harness-init 언어 지원**: Dart/Flutter, Java/Kotlin (Gradle/Maven) 검증 명령어 추가

### Fixed
- **suggest-rule-promote**: `tool_result`/`tool_response` 폴백 추가 (hook이 죽어있던 문제), threshold 2→3 (TDD 오탐 방지)
- **suggest-harness-audit/rule-promote**: `/tmp` 상태 파일 프로젝트별 분리 (cross-project 오염 방지)
- **check-docs-change**: 경로 추출 로직 강화 (`.`/`/` 단일 문자 체크 → 파일 패턴 매칭)
- **suggest-failure-absorb**: Maven `BUILD SUCCESS` 오탐 수정 (`BUILD SUCCESSFUL`만 매칭하던 문제)

## [1.0.3] - 2026-03-30

### Changed
- **failure-absorb 자동 실행**: 테스트 실패/에러 감지 시 제안 → 자동 실행으로 변경
- **에러 패턴 확장**: Java (`NullPointerException`, `BUILD FAILURE`, `mvn/gradle`), TypeScript (`TS2304`, `jest/vitest`, `ERR_MODULE_NOT_FOUND`), Dart/Flutter (`FormatException`, `flutter test fail`, `pub get failed`) 패턴 추가
- **IGNORE 패턴 보강**: `BUILD SUCCESSFUL`, `no issues found`, `passed, 0 failed` 추가

## [1.0.2] - 2026-03-30

### Fixed
- **completion-gate Stop hook 오탐 수정**: payload 텍스트 파싱 대신 `git diff` 기반 변경 파일 감지로 전환
  - Stop hook payload에 변경 파일 정보가 없어 항상 BLOCK되던 문제 해결
  - test/lint 증거 확인 불가 시 BLOCK(exit 2) → advisory 메시지(exit 0)로 변경
  - debug artifact 스캔에서 `re.compile` 정의 줄, 주석 줄 false positive 방지 추가

## [1.0.1] - 2026-03-30

### Added
- **Proactive hooks**: 사용자가 직접 호출하지 않아도 상황을 감지해 skill 사용을 자동 제안
  - `suggest-failure-absorb.py` — Bash 실행 후 테스트 실패/에러 감지 시 `/failure-absorb` 제안
  - `suggest-rule-promote.py` — 같은 에러 패턴 2회 이상 반복 시 `/rule-promote` 제안
  - `suggest-harness-audit.py` — 세션 내 10+개 파일 수정 시 `/harness-audit` 제안
- **harness-team skill**: revfactory/harness 방법론 흡수 — 6가지 에이전트 팀 아키텍처 패턴 (파이프라인, 팬아웃/팬인, 전문가 풀, 생성-검증, 감독자, 계층적 위임)
  - agent-design-patterns, orchestrator-template, team-examples, skill-writing-guide, skill-testing-guide, qa-agent-guide reference 포함
- **skill-template 보강**: pushy description, Why-first 원칙, Progressive Disclosure, 스크립트 번들링 가이드 추가
- **agents-md-template 보강**: 에이전트 팀 정의 파일 필수 생성 규칙 추가

### Changed
- README를 한글로 전면 재작성 — 설치 방법 3가지, 사용 사례, 실패 흡수 루프 플로우차트, 플러그인 구조 추가

## [1.0.0] - 2026-03-30

### Added
- **6 Skills**: harness-init, failure-absorb, weekly-review, harness-audit, rule-promote, harness-team
- **3 Hooks**: completion-gate (Stop/Prompt), docs-change-check (PostToolUse/Command), destructive-cmd-block (PreToolUse/Command)
- **2 Agents**: failure-analyzer (실패 분류 + 흡수 레이어 추천), harness-auditor (규칙 중복/비대화 진단)
- **20 Reference docs**: 부록 A-E 템플릿, 운영 원칙, 실패 카테고리, 안티패턴, 승격 기준 등
- 마켓플레이스 배포용 plugin.json + marketplace.json
- Harness Engineering Manual 전체 섹션 매핑 (섹션 4-11, 부록 A-E)
