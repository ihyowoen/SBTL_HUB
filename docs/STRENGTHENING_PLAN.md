# SBTL_HUB 강화 우선순위 요약

## 지금 바로 해야 할 것
1. README를 실제 구조에 맞게 수정
2. WORKFLOW / OPERATIONS 문서 추가
3. merge_cards.py 안전장치 보강
4. cards/payload data contract 문서화
5. 배포 기준을 main + production으로 고정

## 왜 이 순서인가
현재 문제의 본질은 기능 부족보다 운영 혼선이다.
문서를 먼저 고정해야:
- merge 실수 감소
- 브랜치/배포 혼동 감소
- 카드 품질 기준 통일
- future automation 설계 기준 확보

## 추천 다음 작업
- README replace-all 초안 작성
- docs/WORKFLOW.md 추가
- docs/OPERATIONS.md 추가
- merge_cards.py red-team 개선안 작성
