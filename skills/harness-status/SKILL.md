---
name: harness-status
description: 하네스 운영 상태 대시보드를 출력한다. 흡수율, 실패 분포, 프로모션 후보, 건강도 트렌드를 한눈에 확인한다.
---

## Purpose

`docs/.harness-state.json`을 읽어 하네스의 현재 운영 상태를 CLI 텍스트 대시보드로 출력한다. 수치 기반으로 건강도를 판정하고, 즉각 실행 가능한 권고 사항을 제시한다.

이 skill은 읽기 전용이다. 파일을 수정하거나 상태를 변경하지 않는다. 대시보드는 진단 도구이며, 변경은 weekly-review, failure-absorb, rule-promote skill이 담당한다.

---

## When To Use

- 하네스의 현재 운영 상태를 빠르게 확인하고 싶을 때
- weekly-review 전에 현황을 파악할 때
- 흡수율이나 건강도가 악화되고 있는지 확인할 때
- 사용자가 "harness status", "하네스 상태", "status dashboard", "harness health check" 라고 말할 때

---

## Workflow

### Step 1 — State 파일 로드

`docs/.harness-state.json`을 읽는다.

파일이 없으면 다음 안내를 출력하고 즉시 종료한다:

```
[harness-status] docs/.harness-state.json 파일이 없습니다.

harness-init을 먼저 실행하세요:
  /harness-init    (새 프로젝트)
  /harness-import  (기존 프로젝트)

State 파일은 hook이 실행될 때 자동으로 생성됩니다.
```

파일이 있으나 JSON 파싱에 실패하면:

```
[harness-status] 경고: state 파일 파싱 실패
  경로: docs/.harness-state.json
  원인: <오류 메시지>

hooks/scripts/validate-harness-integrity.py 를 실행해 state 파일을 복구하세요.
```

파싱 성공 시 Step 2로 진행한다.

### Step 2 — 5개 지표 계산

state JSON에서 다음 5개 지표를 계산한다.

**지표 1 — 흡수율 (Absorption Rate)**

```
흡수율 = absorptions.verified / failures.total × 100
```

- `failures.total`이 0이면 "데이터 없음"으로 표시
- `absorptions.verified`는 `absorptions.history` 중 `verified: true`인 항목 수로 재계산

**지표 2 — 카테고리별 실패 분포 (Failure Distribution)**

`failures.by_category`의 각 카테고리(0–6)별 count를 바 차트로 표시.

카테고리 이름:
- 0: 분류 미정
- 1: Global rule 부재
- 2: Task procedure 부재
- 3: Automation 부재
- 4: Terminology mismatch
- 5: Context pollution
- 6: Authority boundary 불명확

**지표 3 — 프로모션 후보 백로그 (Promotion Backlog)**

`promotions.candidates` 배열의 항목 수와 각 항목의 `pattern`, `count`, `date`를 목록으로 표시.

**지표 4 — 마지막 리뷰 이후 경과일 (Days Since Last Review)**

`reviews.last_review_date`를 오늘 날짜와 비교.

- `last_review_date`가 null이면 "리뷰 기록 없음"으로 표시
- 경과일 = 오늘 - last_review_date (일 단위)

**지표 5 — 건강도 트렌드 (Health Score Trend)**

`reviews.health_scores`의 최근 5개 항목을 순서대로 표시.

각 항목 형식: `{"date": "YYYY-MM-DD", "score": 0–100}`

점수가 없으면 "트렌드 데이터 없음"으로 표시.

### Step 3 — 건강도 판정 (Health Status)

harness-audit 기준으로 전체 건강도를 판정한다.

| 조건 | 상태 |
|------|------|
| 흡수율 ≥ 80% AND 경과일 ≤ 14 AND 미검증 흡수 ≤ 3 | **Healthy** |
| 흡수율 50–79% OR 경과일 15–28 OR 미검증 흡수 4–7 | **Degraded** |
| 흡수율 < 50% OR 경과일 > 28 OR 미검증 흡수 > 7 | **Critical** |

복수 조건 충족 시 가장 심각한 상태를 적용한다.

미검증 흡수 수 = `absorptions.pending_verification` 배열 길이.

### Step 4 — 대시보드 출력

다음 형식으로 대시보드를 출력한다:

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  Harness Status Dashboard — <YYYY-MM-DD HH:MM>
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Overall: <Healthy / Degraded / Critical>

── 1. 흡수율 ────────────────────────────────────
  검증된 흡수: <verified>건 / 전체 실패: <total>건
  흡수율: <pct>%  [████████░░] 80%

── 2. 카테고리별 실패 분포 ──────────────────────
  1 Global rule 부재   [████░░░░░░]  4건
  2 Task procedure 부재 [██░░░░░░░░]  2건
  3 Automation 부재    [░░░░░░░░░░]  0건
  4 Terminology        [█░░░░░░░░░]  1건
  5 Context pollution  [░░░░░░░░░░]  0건
  6 Authority boundary [░░░░░░░░░░]  0건
  0 분류 미정          [░░░░░░░░░░]  0건

── 3. 프로모션 후보 백로그 ──────────────────────
  대기 중: <n>건
  - "<pattern>" (발생 <count>회, <date>)
  - "<pattern>" (발생 <count>회, <date>)

── 4. 마지막 리뷰 이후 ──────────────────────────
  마지막 리뷰: <last_review_date>
  경과: <n>일
  총 리뷰 횟수: <review_count>회

── 5. 건강도 트렌드 (최근 5회) ──────────────────
  <date>  <score>/100  [██████████]
  <date>  <score>/100  [████████░░]
  <date>  <score>/100  [██████░░░░]
  <date>  <score>/100  [████░░░░░░]
  <date>  <score>/100  [██░░░░░░░░]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

바 차트 계산:
- 전체 10칸, 카테고리별 실패: 최대값 기준 비율로 채움
- 흡수율: 100% 기준 10칸
- 건강도 점수: 100점 기준 10칸

### Step 5 — 권고 사항 출력

건강도 상태와 지표를 기반으로 즉각 실행 가능한 권고 사항을 출력한다.

**Critical 상태 권고 사항:**

```
[!] 권고 사항
  1. 흡수율 <pct>% — 미검증 흡수 <n>건을 검증하세요 (/failure-absorb)
  2. 리뷰 <n>일 경과 — 즉시 weekly-review를 실행하세요 (/weekly-review)
  3. 프로모션 후보 <n>건 — hook 자동화를 검토하세요 (/rule-promote)
```

**Degraded 상태 권고 사항:**

```
[~] 권고 사항
  1. 카테고리 <n>번 반복 발생 — 해당 레이어 점검 권고
  2. <n>일 이내 weekly-review 실행 권고
```

**Healthy 상태 권고 사항:**

```
[+] 상태 양호
  - 다음 예정 리뷰: <last_review_date + 7일>
```

프로모션 후보가 3건 이상이면 상태와 관계없이 항상 출력:

```
[!] 프로모션 후보 <n>건 누적 — /rule-promote 실행을 권장합니다
```

---

## 출력 형식 원칙

- 색상 코드(ANSI escape) 사용 금지 — 순수 텍스트만 사용
- 바 차트: `█` (채움), `░` (빔) 문자 사용
- 날짜 형식: `YYYY-MM-DD`
- 백분율: 소수점 없이 정수로 표시 (예: 83%)
- 값이 없는 필드: "—" 로 표시 (빈 문자열 금지)

---

## 데이터 없는 경우 처리

state 파일이 존재하지만 데이터가 비어있는 경우:

```
Harness Status Dashboard — <date>
Overall: —

아직 수집된 데이터가 없습니다.
hook이 실행되면 자동으로 지표가 누적됩니다.

첫 실패 발생 시 /failure-absorb 를 실행하세요.
```

---

## Common Mistakes

- state 파일이 없을 때 harness-init을 직접 실행하는 것 — 이 skill은 안내만 제공한다
- `absorptions.verified` 필드를 그대로 읽는 것 — `absorptions.history` 중 `verified: true` 수로 재계산해야 한다
- 바 차트 최대값을 전체 실패 수로 정하는 것 — 카테고리 중 최대값 기준으로 정규화한다
- Critical 판정 후 파일을 수정하려는 것 — 이 skill은 읽기 전용이다
- 경과일 계산에 `last_updated` 필드를 사용하는 것 — `reviews.last_review_date` 기준으로 계산한다
