# SBTL_HUB 운영 매뉴얼 (Enhanced Detail)

## 0. 이 문서의 역할

이 문서는 **실무자가 실제로 무엇을 클릭하고, 무엇을 백업하고, 무엇을 확인해야 하는지**를 적는 운영 매뉴얼이다.

WORKFLOW가 “어떻게 생각할지”라면,
OPERATIONS는 “어떻게 실행할지”다.

---

## 1. 운영 기본 규칙

## Rule 1. production 기준은 main이다
브랜치 preview가 아무리 정상이어도,
production이 main을 보고 있으면 앱은 main 기준으로 보인다.

## Rule 2. cards.json은 민감 파일이다
이 파일 하나가 앱의 뉴스 피드를 사실상 결정한다.
잘못 건드리면 앱 전체 품질이 망가진다.

## Rule 3. merge 전에 반드시 백업
최소한 직전 cards.json은 백업한다.

## Rule 4. merge는 로컬 결과보다 production 확인이 끝나야 종료
`git push`에서 끝이 아니다.
앱에서 실제 숫자와 카드가 보여야 끝이다.

---

## 2. 표준 작업 전 준비

## 2-1. 확인할 것
- 최신 repo를 기준으로 작업 중인가
- 현재 브랜치가 무엇인가
- production이 main을 보는 구조인가
- 넣을 카드가 safe payload로 정리되었는가

## 2-2. 백업 대상
- `public/data/cards.json`
- 사용한 payload JSON
- 필요 시 직전 main commit SHA

---

## 3. 표준 병합 절차

## A. 최신 repo 준비
1. 최신 repo clone 또는 pull
2. main 기준인지 확인
3. 작업 브랜치 생성 또는 기존 작업 브랜치 사용

## B. 백업
1. `public/data/cards.json` 백업
2. payload JSON 저장
3. 병합 전 total 기록

## C. merge 실행
1. safe payload 준비
2. `python merge_cards.py <payload.json>` 실행
3. 콘솔 출력 기록

## D. 검증
1. JSON 파싱 확인
2. total 확인
3. 특정 신규 카드 match 확인
4. 중복 육안 점검
5. `git diff` 확인

## E. Git 반영
1. add
2. commit
3. push
4. PR
5. main 반영

## F. 배포 확인
1. GitHub main 숫자 확인
2. Vercel deployment success 확인
3. production 화면 확인
4. 캐시 제거 후 재확인

---

## 4. 병합 전 체크 기준

## 4-1. 이 payload를 넣어도 되는가
다음에 하나라도 걸리면 멈춘다.

- 이미 main cards에 같은 의미 카드가 있음
- 허브/landing/pr 성격 기사임
- relevance가 약함
- 제목은 새롭지만 사실상 같은 사건 재표현임
- 카드 문안이 아직 약함

## 4-2. safe batch 기준
권장:
- 민감한 run: 1~2장
- 일반 run: 3~5장
- 대량 삽입: 금지

---

## 5. merge_cards.py 운영상 주의점

현재 스크립트는 다음 성격으로 이해해야 한다.

### 강점
- 빠름
- 단순함
- payload → cards.json 반영이 쉬움

### 약점
- validator 아님
- 의미 중복 못 잡음
- 제목 prefix dedupe가 취약
- formatting 차이 때문에 diff가 크게 보일 수 있음
- compact input에서 updated가 꼬일 수 있음

### 운영 결론
**merge_cards.py는 최종 편집 결과를 반영하는 도구일 뿐, 품질을 보장하는 도구가 아니다.**

---

## 6. 실수 방지 규칙

## 6-1. 절대 하지 말 것
- 오래된 cards.json 덮어쓰기
- triage raw 대량 merge
- 브랜치 preview만 보고 “배포 완료” 판단
- merge script 출력의 “중복 0건”을 편집적 진실로 오해

## 6-2. 항상 할 것
- 최신 main 기준 작업
- merge 전 백업
- merge 후 Python 검증
- production 화면 확인

---

## 7. 실제 검증 예시

## 7-1. 숫자 검증
확인 항목:
- updated
- total
- 특정 제목 match_count

## 7-2. 카드 검증
확인 항목:
- title
- url
- signal
- region
- date

## 7-3. 의미 검증
질문:
- 이 카드가 기존 카드와 truly different 인가
- 독자에게 새 관점이 추가되나
- 아니면 같은 뜻을 새 제목으로 또 넣은 건가

---

## 8. README 반드시 고쳐야 하는 이유

현재 README가 실제 운영 구조를 충분히 설명하지 못하면,
다음 문제가 반복된다.

1. cards DB가 App.jsx에 들어있다고 오해
2. data 파일 구조를 놓침
3. merge → PR → main → deploy 관계를 혼동
4. Vercel preview와 production을 헷갈림

즉 README는 단순 소개문서가 아니라,
**운영 사고를 고정하는 문서**여야 한다.

---

## 9. 지금 가장 필요한 문서 구조

권장 구조:

```text
README.md
docs/
  WORKFLOW.md
  OPERATIONS.md
  DATA_CONTRACT.md
  DEPLOYMENT.md
```

### README.md
- 프로젝트 소개
- 실제 디렉토리 구조
- 로컬 실행
- 데이터 파일 구조
- 운영 문서 링크

### WORKFLOW.md
- triage → 편집 판단 → safe payload → merge → deploy

### OPERATIONS.md
- 실제 명령어 / 실제 확인 포인트 / 사고 방지 규칙

### DATA_CONTRACT.md
- cards.json 필드 정의
- payload 입력 포맷
- tracker_data / faq 구조

### DEPLOYMENT.md
- main vs branch preview
- production 확인법
- Vercel 체크포인트

---

## 10. 강화 로드맵 (추천 순서)

## Phase 1. 문서 고정
- README 수정
- WORKFLOW 작성
- OPERATIONS 작성

## Phase 2. merge 안전화
- dry-run
- validate-only
- URL dedupe
- duplicate suspicion warning
- backup output 자동화

## Phase 3. data contract
- cards schema
- payload schema
- tracker schema
- faq schema

## Phase 4. editorial tooling
- 카드 QA 체크리스트
- 중복 위험 카드 자동 경고
- payload preview 화면 또는 스크립트

## Phase 5. deployment discipline
- production 확인 루틴 고정
- 운영 로그 남기기
- hotfix 기준 정하기

---

## 11. 운영자가 마지막에 반드시 자문할 질문

배포 직전 아래 5문항에 “예”가 아니면 멈춘다.

1. 이 payload는 최신 main 기준에서 다시 merge 했는가?
2. 이 카드들은 편집적으로 truly new 인가?
3. JSON이 정상 파싱되는가?
4. GitHub main 숫자가 기대치와 일치하는가?
5. production 화면에서 실제로 반영됐는가?

---

## 12. 지금 당장 보완해야 할 우선순위

### 가장 시급
1. README 현실화
2. WORKFLOW/OPERATIONS 문서 추가
3. merge_cards.py 안전장치 보강

### 그다음
4. DATA_CONTRACT 문서화
5. editorial QA checklist
6. deploy/hotfix 기준 명문화

---

## 13. 운영상 최종 한 줄 원칙

**SBTL_HUB는 “자동 수집 앱”이 아니라 “편집된 intelligence 앱”이다.**
그러므로 가장 중요한 것은
수집량이 아니라
**운영 질서 + 편집 품질 + 배포 통제**다.
