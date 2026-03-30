# Completion Checklist Template

Use this template for `docs/completion-checklist.md`.

A team should answer these 5 questions before declaring a task complete:

1. 무엇을 변경했는지 핵심 변경사항 3줄 이내로 요약했는가?
2. 변경한 코드에 대해 관련 테스트/타입체크/린트를 실행했고 결과를 저장했는가?
3. API/문서/스키마/설계 규약 변경이 있었으면 문서가 함께 업데이트되었는가?
4. 남은 위험 또는 TODO가 있다면 파일명/이슈 번호와 함께 명시했는가?
5. 이 변경이 다른 문서(AGENTS.md, glossary, 운영 원칙)와 충돌하지 않음을 확인했는가?

완료 판단 규칙:
- 1~4번이 모두 "완료"이고, 5번이 "없음" 또는 "확인됨"이면 완료로 승인.
- 하나라도 "미실행"이면 완료 블록.

권장 형식:

- Tests: `<command> -> pass/fail`
- Typecheck: `<command> -> pass/fail`
- Docs updated: `<files>`
- Risks: `<항목>`
- Remaining actions: `<actions>`
