# SBTL_HUB 운영 워크플로

## 0. 목적

이 문서는 **앞으로 생성될 카드**에 대한 운영 기준을 잠그기 위한 문서다.

1. 생산 파이프라인과 편집 판단을 분리한다.
2. raw/triage를 그대로 merge 하지 않는다.
3. cards.json은 최신 main 기준에서만 수정한다.
4. 배포 확인은 브랜치가 아니라 main + production 기준으로 본다.
5. 신규 카드 표준은 **full schema only** 로 본다.

---

## 1. 시스템 이해

### A. 데이터 표시층
- 앱 프론트는 `public/data/cards.json`
- FAQ는 `public/data/faq.json`
- 정책/트래커는 `public/data/tracker_data.json`

### B. 편집/판단층
- triage 결과
- 사용자의 추가 파일
- 사람이 검토한 카드 문안
- 중복/관련 기사 통합 판단
- safe merge payload 작성

### C. 병합층
- `merge_cards.py`
- 외부 JSON payload를 `public/data/cards.json`에 병합

### D. Git / 배포층
- GitHub repo
- main branch
- Vercel production

---

## 2. 절대 하지 말아야 할 것

### 금지 1) triage kept를 대량으로 바로 merge
### 금지 2) 오래된 로컬 cards.json을 최신 repo에 덮어쓰기
### 금지 3) “브랜치에 있으니 앱에도 있을 것”이라고 생각하기
### 금지 4) merge 결과만 보고 중복 없다고 믿기

---

## 3. 표준 워크플로

### STEP 1. 신규 run 수집
### STEP 2. 편집 판단 / red-team review
### STEP 3. 카드 편집 기준

신규 카드는 아래 **full schema 기준**으로 통과해야 한다.

- title
- sub
- gate
- fact
- implication
- signal
- region

region은 기사 출처가 아니라 **사건의 직접 무대**로 붙인다.

### STEP 4. 중복 통제
### STEP 5. safe payload 작성

권장 포맷:
- `id / region / date / cat / signal / title / sub / gate / fact / implication / urls`

### STEP 6. 최신 repo 기준 병합
### STEP 7. 검증
### STEP 8. Git 반영
### STEP 9. 배포 확인

---

## 4. 최종 원칙

**앞으로 생성되는 카드는 full schema 기준으로만 작성·검수·병합한다.**
