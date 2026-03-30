# Incident Postmortem Template

본 템플릿은 큰 실패, 사용자 영향이 있었거나 반복 가능성이 높은 사고의 원인 분석에 사용한다.

---

## Incident Summary

- **Incident ID / 날짜:** [YYYY-MM-DD]
- **영향 범위:** [서비스, 기능, 사용자 수, 기간]
- **중요도:** [높음/중간/낮음]

## Timeline

- **발생 시각:** `YYYY-MM-DD HH:MM`
- **탐지 시각:** `YYYY-MM-DD HH:MM`
- **완화 완료:** `YYYY-MM-DD HH:MM`

## Root Cause

- 바로 가는 핵심 원인
- 2차 원인 및 기여요인

## Impact

- 사용자 영향
- 시스템 영향
- 데이터/보안 영향
- 운영 영향

## Why It Wasn't Caught Earlier

- 프로세스/도구/검증의 빈틈
- 재발 방지 실패 포인트

## Corrective Actions

- [ ] 즉시 조치: <조치명>
- [ ] 재발 방지 규칙: <Layer A/B/C/D 중 적합한 레이어로 흡수>
- [ ] 소유자: @<owner>, 목표일: <YYYY-MM-DD>

## Verification

- 적용 검증 방법: <테스트/체크>
- 재발 모니터링 계획: <어떻게 추적할지>

## Lessons Learned

- 이번 사고에서 배운 점 3개

---

## Absorption Log

- [ ] 규칙 승격 완료
- [ ] skill 또는 hook/문서 업데이트 완료
- [ ] Failure Log 업데이트 완료
