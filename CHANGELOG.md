# Changelog

모든 주요 변경 사항을 이 파일에 기록한다.

## [2.0.1] - 2026-04-08

### Fixed
- **session-doc-cleanup KeyError**: `e['status']` → `e.get('status', '')` — failure-log에 status 컬럼이 없는 프로젝트에서 Stop hook이 크래시하던 버그 수정

## [2.0.0] - 2026-03-31

Advisory 시스템에서 closed-loop 운영 체제로 전환.

### Added
- **공유 인프라**: `hooks/scripts/lib/config_loader.py` — 프로젝트별 `.harness.json` 설정 로더 (모든 임계값 오버라이드 가능)
- **공유 인프라**: `hooks/scripts/lib/state_manager.py` — `docs/.harness-state.json` 영속 상태 관리 (session buffer/flush 패턴)
- **harness-import 스킬**: 기존 프로젝트에 하네스 거버넌스 도입 (brownfield 지원)
- **harness-status 스킬**: `docs/.harness-state.json` 기반 CLI 대시보드 — 흡수율, 실패 분포, 프로모션 백로그, 건강도 트렌드
- **2-tier 자동 분류**: 실패 감지 시 Cat 2(환경)/Cat 3(테스트)/Cat 5(타임아웃) 자동 분류, 나머지 Cat 0(unclassified)
- **failure-log 자동 기록**: 5컬럼 형식 (`Date | Description | Cause Category | Absorption Action | Verification Status`)으로 자동 기록
- **failure-absorb Phase 5 — Verify**: 흡수 완료 후 자동 검증 단계 추가
- **프로모션 큐**: session-doc-cleanup이 `docs/.harness-state.json`에 프로모션 후보 자동 큐잉
- **selftest 7/7 커버리지**: suggest-failure-absorb, suggest-rule-promote, suggest-harness-audit, session-doc-cleanup 테스트 추가
- **false-positive 테스트 코퍼스**: 10개 정상 + 10개 실패 빌드 출력 (20/20 통과)
- **설정 템플릿**: `.harness.json` 스키마 문서화 (`harness-config-template.json`)

### Changed
- **suggest-failure-absorb**: "Do NOT run /failure-absorb" → 실제로 `/failure-absorb` 실행 제안으로 변경
- **suggest-failure-absorb**: 5분 쿨다운 추가 (동일 에러 시그니처 기준 dedup)
- **suggest-rule-promote**: `/tmp` 트래커 → `docs/.harness-state.json` 영속 상태로 이전
- **suggest-harness-audit**: `/tmp` 트래커 → `docs/.harness-state.json` 영속 상태로 이전
- **session-doc-cleanup**: 듀얼 파서 — 기존 structured entry + 신규 5컬럼 테이블 모두 파싱
- **session-doc-cleanup**: Stop hook에서 session buffer flush 수행
- **completion-gate**: Stop hook payload 파싱 시도 + `.harness-state.json` 변경 감지 제외
- **weekly-review**: `git log --format=%ai -1` 기반 정확한 staleness 감지
- **hooks-template**: 3개 → 7개 훅 전체 등록, `${CLAUDE_PLUGIN_ROOT}` → `.claude/scripts/` (자급자족)
- **모든 훅 스크립트**: `lib/` import에 `try/except ImportError` fallback 패턴 적용

### Fixed
- **marketplace.json 버전 불일치**: plugin.json과 동기화 (1.0.1 → 2.0.0)
- **failure-log 스키마 불일치**: 3개 컴포넌트가 다른 포맷 사용 → 5컬럼 통일

## [1.0.5] - 2026-03-31

### Fixed
- **FAIL 패턴 버그**: `FAIL[ED]?\b` → `\bFAIL(ED)?\b` — "FAILED" 키워드를 매칭하지 못하던 버그 수정
- **IGNORE 순서 버그**: 전체 출력 기반 → 라인 단위 IGNORE 체크로 변경 — "Successfully...failures" 혼합 출력에서 실패를 놓치던 문제 해결
- **TODO/FIXME 과차단**: debug artifact에서 제거 — 정상적인 코드 마커가 세션 종료를 차단하던 문제 해결
- **Stop hook JSON validation**: stderr JSON 출력 → plain text 변경 — "JSON validation failed" 에러 해결
- **Stop prompt hook 제거**: "No assistant message found" 에러 해결
- **suggest-harness-audit**: 30분 비활성 후 `last_suggest` 리셋 추가

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
