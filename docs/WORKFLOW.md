# SBTL_HUB 운영 워크플로

## 0. 목적

이 문서는 **앞으로 생성될 카드**에 대한 운영 기준을 잠그기 위한 문서다.

1. 생산 파이프라인과 편집 판단을 분리한다.
2. raw/final input을 그대로 merge 하지 않는다.
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
- `final_news_llm_input.stories[]`
- Prompt A/B/C 결과물
- 사용자의 추가 파일
- 사람이 검토한 카드 문안
- 중복/관련 기사 통합 판단
- accepted / merge-ready payload 작성

### C. 병합층
- `merge_cards.py`
- 외부 JSON payload를 `public/data/cards.json`에 병합

### D. Git / 배포층
- GitHub repo
- main branch
- Vercel production

---

## 2. 절대 하지 말아야 할 것

### 금지 1) raw final input / upstream story를 대량으로 바로 merge
### 금지 2) 오래된 로컬 cards.json을 최신 repo에 덮어쓰기
### 금지 3) “브랜치에 있으니 앱에도 있을 것”이라고 생각하기
### 금지 4) merge 결과만 보고 중복 없다고 믿기
### 금지 5) accepted 이후 enrichment 단계에서 rejected / revise_required / non-accepted 항목을 임의로 되살리기
### 금지 6) web search를 독자-facing 문구 보강 근거로 조용히 사용하기

---

## 3. 표준 워크플로

### STEP 1. 신규 run 수집

현재 기본 입력 universe는 `docs/PROMPT_ABC_DEFAULT_MODE.md`를 따른다.

기본값:
- `final_news_llm_input.stories[]`

단, 과거/예외 run의 `triage_output + rescue + dropped` 모드는 `docs/TRIAGE_INPUT_MODE_DEFAULT.md` 또는 사용자의 명시 지시가 있을 때만 적용한다.

### STEP 2. Prompt A/B/C 편집 판단 / red-team review

Prompt A/B/C는 `docs/PROMPT_ABC_DEFAULT_MODE.md` 및 상위 fact discipline 문서 기준으로 실행한다.

- Prompt A = Editorial Selector / spec builder
- Prompt B = Card Writer with source verification
- Prompt C = Enhanced Red Team + Cross-Functional Validator + Formatter

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
### STEP 5. accepted / merge-ready payload 작성

권장 포맷:
- `id / region / date / cat / signal / title / sub / gate / fact / implication / urls / fact_sources`

### STEP 5.5. Accepted Content Depth Enrichment / Final QC

Prompt C 또는 동등한 final validator를 통해 accepted로 확정된 신규 카드 payload는 병합 전에 `docs/POST_ACCEPTANCE_CONTENT_ENRICHMENT_QC.md` 기준으로 content depth enrichment pass를 수행한다.

이 단계의 목적은 accepted 카드의 visible fields만 고도화하고, `fact_sources` / `source_quote`를 보존하며, baseline `cards.json`과의 중복·정렬·source-lock을 최종 검증하는 것이다.

이 단계에서는 신규 후보를 추가 선별하거나 rejected / revise_required / non-accepted 항목을 임의로 되살리지 않는다. Web search는 enrichment 근거 추가용이 아니라 final QC 검증·충돌탐지·중복탐지용으로만 사용한다.

필수 산출물:
- content-enriched accepted payload
- baseline에 병합한 final cards.json
- QC report

### STEP 6. 최신 repo 기준 병합
### STEP 7. 검증
### STEP 8. Git 반영
### STEP 9. 배포 확인

---

## 4. 최종 원칙

**앞으로 생성되는 카드는 full schema 기준으로만 작성·검수·병합한다.**

**Prompt A/B/C는 무엇을 accepted로 볼지 판단하고, `POST_ACCEPTANCE_CONTENT_ENRICHMENT_QC.md`는 Prompt C accepted 카드를 production-safe 데이터로 잠그는 후처리 단계다.**
