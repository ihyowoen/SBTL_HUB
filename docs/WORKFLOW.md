# SBTL_HUB 운영 워크플로 (Enhanced Detail)

## 0. 목적

이 문서는 **SBTL_HUB의 카드 데이터 운영, 편집 판단, 병합, Git 반영, 배포 확인**까지의 전체 흐름을
사람이 헷갈리지 않도록 한 번에 정리한 운영용 기준서다.

핵심 원칙은 단순하다.

1. **생산 파이프라인과 편집 판단을 분리한다**
2. **raw/triage를 그대로 merge 하지 않는다**
3. **cards.json은 최신 main 기준에서만 수정한다**
4. **배포 확인은 “브랜치”가 아니라 “main + production” 기준으로 본다**
5. **merge는 기술 작업이 아니라 편집 작업의 마지막 단계다**

---

## 1. 현재 시스템을 이렇게 이해하면 된다

SBTL_HUB는 크게 4층으로 나뉜다.

### A. 데이터 표시층
- 앱 프론트는 `public/data/cards.json`
- FAQ는 `public/data/faq.json`
- 정책/트래커는 `public/data/tracker_data.json`

즉, 앱에 보이는 뉴스카드는 **cards.json이 사실상 단일 소스 오브 트루스(SSOT)** 다.

### B. 편집/판단층
- triage 결과
- 사용자의 추가 파일
- 사람이 검토한 카드 문안
- 중복/관련 기사 통합 판단
- safe merge payload 작성

이 층은 자동화보다 **편집 품질 통제**가 중요하다.

### C. 병합층
- `merge_cards.py`
- 외부 JSON payload를 `public/data/cards.json`에 병합
- dedupe / 정렬 / 저장

주의:
현재 merge 스크립트는 **validator가 아니라 단순 merger**에 가깝다.
즉, 병합 전 payload 품질이 좋지 않으면 앱도 바로 오염된다.

### D. Git / 배포층
- GitHub repo
- main branch
- Vercel production

중요:
**브랜치에 올라간 것과 production에 반영된 것은 다르다.**
항상 마지막 기준은 **main + production 화면**이다.

---

## 2. 권장 운영 원칙

## 2-1. 절대 하지 말아야 할 것

### 금지 1) triage kept를 대량으로 바로 merge
이건 가장 위험하다.

이유:
- nav/landing/PR/허브성 문서가 섞일 수 있음
- 같은 의미 기사 제목만 달리 중복될 수 있음
- 앱 품질이 한 번에 무너짐

### 금지 2) 오래된 로컬 cards.json을 최신 repo에 덮어쓰기
항상 최신 main의 `public/data/cards.json`을 base로 잡아야 한다.

### 금지 3) “브랜치에 있으니 앱에도 있을 것”이라고 생각하기
production은 보통 main 기준이다.
브랜치 preview와 production을 혼동하면 안 된다.

### 금지 4) merge 결과만 보고 중복 없다고 믿기
현재 merge dedupe는 제목 prefix 기반이라,
**의미 중복을 못 잡을 수 있다.**
즉 “중복 0건”은 편집적으로 0건이라는 뜻이 아니다.

---

## 3. 앞으로의 표준 워크플로

## STEP 1. 신규 run 수집
입력물:
- triage 결과
- kept / dropped / review candidate
- 사용자가 따로 올린 카드 후보
- 수동 검토 대상 기사

산출물:
- “검토 대기 후보 리스트”

### 이 단계 목표
“많이 모으는 것”이지, “바로 넣는 것”이 아니다.

---

## STEP 2. 편집 판단 / red-team review
각 후보를 아래 5가지로 분류한다.

### A. KEEP
그대로 카드화 가능

### B. MERGE
동일 주제의 여러 기사를 1장 강화 카드로 통합

### C. DROP
배터리/ESS/EV/핵심광물/정책 relevance 부족
또는 nav/landing/PR/허브성

### D. HOLD
지금 넣기엔 약하지만 추적 가치 있음

### E. REWRITE
핵심은 맞지만 제목/문안/게이트가 약해서 재작성 필요

---

## STEP 3. 카드 편집 기준
카드는 아래 기준으로 통과해야 한다.

### 3-1. 제목
- 한 줄만 읽어도 “왜 중요한지” 감이 와야 함
- 단순 기사 제목 복붙 금지
- 해석은 가능하지만 과장 금지

### 3-2. sub
- 사건 요약
- 누가 / 무엇을 / 어느 정도 규모로 했는지

### 3-3. g (gist / why it matters)
- 앱에서 가장 중요한 문장
- “그래서 공급망/정책/수익성/경쟁구도에 무슨 의미인가”를 써야 함

### 3-4. signal
- t: 정말 상단에 올릴 톱 시그널
- h: 높은 중요도
- m: 의미는 있으나 톱은 아님
- i: 정보성

### 3-5. region
- KR / US / CN / EU / JP / GL
- 애매하면 GL
- 여러 지역 직접 연결이면 GL 또는 US/KR 같은 예외적 표기 검토

---

## STEP 4. 중복 통제
중복은 2가지로 본다.

### 4-1. 기술적 중복
- 제목 거의 동일
- URL 동일
- 같은 payload 내 동일 카드

### 4-2. 편집적 중복
- 제목은 다르지만 사실상 같은 사건
- 다른 기사지만 같은 메시지
- 이미 cards.json에 같은 뜻의 카드가 있음

운영상 중요한 건 **편집적 중복 제거**다.

### 실무 체크 질문
- 이 카드가 기존 카드와 “독자 입장에서 다른 정보”를 주는가?
- 새 숫자 / 새 정책 / 새 일정 / 새 관전포인트가 있나?
- 아니면 제목만 바꾼 재삽입인가?

---

## STEP 5. safe payload 작성
병합용 payload는 **편집이 끝난 카드만** 담는다.

권장 포맷:
- raw schema 사용
- `date` 필드 포함
- `title / sub / gate / urls / keys / signal / region` 포함

권장 이유:
- `merge_cards.py`가 raw schema를 compact로 변환
- top-level `updated` 관리가 더 덜 꼬임

### payload 작성 원칙
- 한 번에 너무 많이 넣지 않는다
- 논쟁성 카드 / 중복 의심 카드는 소량으로 나눠 넣는다
- safe batch 기준은 보통 1~5장

---

## STEP 6. 최신 repo 기준 병합
항상 이 순서를 지킨다.

1. 최신 GitHub repo clone 또는 pull
2. 최신 `main` 기준 확인
3. 현재 `public/data/cards.json` 백업
4. safe payload를 최신 repo에서 실행
5. 병합 후 JSON 검증
6. total / match / 샘플 카드 확인
7. git diff 확인

### 핵심
**옛날 cards.json 파일을 복사해서 덮어쓰지 않는다.**
항상 최신 base에서 다시 merge 한다.

---

## STEP 7. 검증
병합 직후 검증은 최소 아래 4개는 해야 한다.

### 7-1. JSON 파싱 성공 여부
파일이 깨지면 앱 전체가 무너진다.

### 7-2. total 숫자 확인
예상 total과 실제 total이 맞는지

### 7-3. 신규 카드 존재 여부
특정 제목/URL/match count 확인

### 7-4. 중복 육안 점검
merge script 결과만 믿지 말고
의미 중복을 다시 본다.

---

## STEP 8. Git 반영
권장:
- 작업 브랜치에서 commit/push
- PR 생성
- main 반영
- production 확인

다만 운영상 긴급 수정은 예외가 있을 수 있다.
그 경우에도 최소한:
- 현재 main 상태 기록
- 왜 긴급 반영했는지 남김
- 반영 후 production 숫자 확인
이 필요하다.

---

## STEP 9. 배포 확인
확인은 3단계로 본다.

### 9-1. GitHub main 파일
`public/data/cards.json` total 확인

### 9-2. 배포 상태
Vercel build / deployment success 확인

### 9-3. 실제 앱 화면
브라우저/앱에서 숫자와 카드 노출 확인

주의:
- 브랜치 preview
- merged PR
- production main
이 셋은 서로 다를 수 있다.

---

## 4. 역할 분담 권장안

## A. 생산 파이프라인
- Linux/WSL
- triage 생성
- raw source 정리

## B. 편집 판단자
- GPT/Claude + 사람
- 중복 제거
- 관련 기사 통합
- 최종 카드 문안 작성

## C. Git 반영자
- merge payload 적용
- git commit/push/PR
- deployment 체크

현재 가장 맞는 구조는:

**파이프라인은 Linux에서 돌리고, 편집 판단은 LLM+사람이 하고, GitHub에는 “문안이 끝난 payload 결과”만 올리는 구조**

---

## 5. 지금 앱을 더 강화하려면 우선순위는 이것이다

## Priority 1. merge_cards.py 안전화
현재 가장 위험한 부분

필수 보완:
- 제목 prefix 35자 dedupe 보강
- URL 기준 보조 dedupe
- empty title 방지
- compact input에서도 `updated` 안전 처리
- dry-run 모드
- validate-only 모드
- before/after diff summary 출력
- duplicate suspicion warning 출력

## Priority 2. 운영 문서 고정
사람이 헷갈려서 실수가 반복되는 구조다.
README / WORKFLOW / OPERATIONS를 현실 구조에 맞게 고쳐야 한다.

## Priority 3. 데이터 계약 문서
`cards.json` / payload / tracker / faq 각각 필드 명세와 필수값을 문서화해야 한다.

## Priority 4. deploy discipline
- production은 main only
- 브랜치 preview는 참고용
- 숫자 확인 기준은 항상 production

## Priority 5. editorial QA checklist
매 run마다 같은 질문을 반복하지 않도록 체크리스트화

---

## 6. 추천 체크리스트 (실전용)

### merge 전
- [ ] 최신 main 기준 repo인가
- [ ] payload가 safe batch인가
- [ ] 기존 cards와 의미 중복 없는가
- [ ] nav/landing/PR 제거됐는가
- [ ] date 필드가 있는가

### merge 후
- [ ] JSON 파싱 성공
- [ ] total 예상치 일치
- [ ] 신규 카드 실제 존재
- [ ] 기존 핵심 카드 손실 없음
- [ ] 앱에서 숫자 반영 확인

### deploy 후
- [ ] GitHub main 숫자 확인
- [ ] Vercel success 확인
- [ ] production 화면 확인
- [ ] 캐시 이슈 여부 확인

---

## 7. 앞으로 문서 세트 추천

최소 문서는 아래 4개가 좋다.

1. `README.md`
2. `docs/WORKFLOW.md`
3. `docs/OPERATIONS.md`
4. `docs/DATA_CONTRACT.md`

이번 정리에서는 우선
- WORKFLOW
- OPERATIONS
를 먼저 잠그는 것이 맞다.
