# SBTL_HUB 운영 워크플로

## 0. 목적

이 문서는 **앞으로 생성될 카드**에 대한 운영 기준을 잠그기 위한 문서다.

1. 생산 파이프라인과 편집 판단을 분리한다.
2. raw/final input을 그대로 merge 하지 않는다.
3. cards.json은 최신 main 기준에서만 수정한다.
4. 배포 확인은 브랜치가 아니라 main + production 기준으로 본다.
5. 신규 카드 표준은 **full schema only** 로 본다.
6. `Prompt C accepted`를 `publish-ready`로 오해하지 않도록 후처리 게이트를 강제한다.

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
- accepted / revise_required / rejected 판정
- accepted vs addable 분리
- source enrichment / content depth enrichment / final QC

### C. 병합층
- `merge_cards.py`
- 외부 JSON payload를 `public/data/cards.json`에 병합
- 병합 전 accepted payload는 `docs/POST_ACCEPTANCE_CONTENT_ENRICHMENT_QC.md` 기준의 publish-ready 게이트를 통과해야 한다.

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
### 금지 7) Prompt C accepted를 곧바로 GitHub 반영 후보 또는 publish-ready로 부르기
### 금지 8) expected final count를 맞추기 위해 중복 사건을 강제로 추가하기

---

## 3. 표준 워크플로

### STEP 1. 신규 run 수집 / latest source 확인

현재 기본 입력 universe는 `docs/PROMPT_ABC_DEFAULT_MODE.md`를 따른다.

기본값:
- `final_news_llm_input.stories[]`

확인 항목:
- `run_tag`
- `run_label`
- `generated_kst`
- `story_count`
- `KEEP / REVIEW / STEP2_PENDING / DROPPED / INPUT_ONLY`
- integrity flag 여부
- 직전 baseline source

단, 과거/예외 run의 `triage_output + rescue + dropped` 모드는 `docs/TRIAGE_INPUT_MODE_DEFAULT.md` 또는 사용자의 명시 지시가 있을 때만 적용한다.

### STEP 2. Prompt A/B/C 편집 판단 / red-team review

Prompt A/B/C는 `docs/PROMPT_ABC_DEFAULT_MODE.md` 및 상위 fact discipline 문서 기준으로 실행한다.

- Prompt A = Editorial Selector / spec builder
- Prompt B = Card Writer with source verification
- Prompt C = Enhanced Red Team + Cross-Functional Validator + Formatter

Prompt A/B/C의 상태 의미:

| 상태 | 의미 |
|---|---|
| `passed_specs` | Prompt A에서 B로 넘길 후보 |
| `drafted` | Prompt B에서 작성된 초안 |
| `accepted` | Prompt C 기준 fact-safe 통과 |
| `revise_required` | 근거/문장/구조 보강 필요 |
| `rejected` | 현재 run에서 폐기 |

중요:

```text
Prompt C accepted = fact-safe
Prompt C accepted != publish-ready
```

### STEP 3. 카드 편집 기준

신규 카드는 아래 **full schema 기준**으로 통과해야 한다.

- title
- sub
- gate
- fact
- implication
- signal
- region
- fact_sources

region은 기사 출처가 아니라 **사건의 직접 무대**로 붙인다.

### STEP 4. 중복 통제

중복 통제는 URL만 보지 않는다.

필수 확인:
- exact URL
- canonical URL
- normalized title
- actor + asset/policy + event_type + event_date 기반 event fingerprint
- breaking-news / follow-up / full-report 중복
- baseline에 이미 있는 사건인지 여부

동일 사건이면 신규 카드로 넣지 말고 다음 중 하나로 처리한다.

- `existing_reinforcement`
- `withheld_reinforcement`
- `already_covered_by_broader_card`

### STEP 5. accepted / merge-ready payload 작성

권장 포맷:
- `id / region / date / cat / signal / title / sub / gate / fact / implication / urls / fact_sources`

하지만 이 단계의 산출물은 아직 최종 publish-ready가 아니다.

상태를 분리한다.

```text
accepted_fact_safe
  ↓
addable_merge_safe
  ↓
source_enriched or source_coverage_reviewed
  ↓
content_enriched
  ↓
language_terminology_polished
  ↓
publish_ready
```

### STEP 5.5. Post-Acceptance Content Depth Enrichment / Final QC

Prompt C 또는 동등한 final validator를 통해 accepted로 확정된 신규 카드 payload는 병합 전에 `docs/POST_ACCEPTANCE_CONTENT_ENRICHMENT_QC.md` 기준으로 content depth enrichment pass를 수행한다.

이 단계의 목적은 accepted 카드의 visible fields만 고도화하고, `fact_sources` / `source_quote`를 보존하며, baseline `cards.json`과의 중복·정렬·source-lock·source coverage·event fingerprint를 최종 검증하는 것이다.

이 단계에서는 신규 후보를 추가 선별하거나 rejected / revise_required / non-accepted 항목을 임의로 되살리지 않는다. Web search는 enrichment 근거 추가용이 아니라 final QC 검증·충돌탐지·중복탐지용으로만 사용한다.

필수 산출물:
- content-enriched accepted payload
- baseline에 병합한 final cards.json
- QC report

필수 게이트:

| Gate | 내용 |
|---|---|
| Gate 1 — Fact Safety | 핵심 claim이 `fact_sources` 또는 `source_quote`로 확인되는가 |
| Gate 2 — Merge Safety | accepted와 addable이 분리되고 baseline 중복 사건이 제거/기록됐는가 |
| Gate 3 — Source Layer | source coverage, single-source reason, claim coverage가 검토됐는가 |
| Gate 4 — Content Depth | visible fields가 단순 요약이 아니라 전략 브리핑인가 |
| Gate 5 — Language & Tone | 외국어/단위/용어/금지문구/SBTL 억지 연결이 제거됐는가 |
| Gate 6 — Publish Readiness | 정렬, schema drift, 혼입, QC report, baseline sync 상태가 확인됐는가 |

`publish_ready=true`는 위 게이트가 모두 PASS일 때만 부여한다.

### STEP 6. 최신 repo 기준 병합

병합 직전 baseline source를 명시한다.

허용 baseline source:
- `github_main`
- `local_final_candidate`
- `user_uploaded_baseline`

주의:
- `local_final_candidate` 또는 `user_uploaded_baseline` 기준 output은 GitHub 반영 후보일 수 있으나, PR/merge 전 반드시 GitHub main sync gate를 다시 통과해야 한다.
- GitHub main과 로컬/업로드 baseline이 다를 수 있으므로 최종 반영 전 `public/data/cards.json` count와 변경 범위를 재확인한다.

### STEP 7. 검증

최소 확인:
- JSON 유효성
- 카드 수
- 중복 ID
- 중복 URL
- 중복 사건
- rejected / revise_required / non-accepted 혼입
- visible 외국어 잔존
- 금지문구 잔존
- fact_sources/source_quote 보존
- implication 2개 미만 0개
- latest-first 정렬
- schema/type drift 0개

### STEP 8. Git 반영

Git 반영 전:
- main 동기화
- 현재 `public/data/cards.json` count 확인
- final candidate의 baseline count와 일치 여부 확인
- 불일치 시 무조건 멈추고 재병합 또는 conflict 판단

### STEP 9. 배포 확인

배포 확인은 브랜치 preview만으로 종료하지 않는다.

확인 기준:
- main 반영 여부
- Vercel production 반영 여부
- 앱에서 신규 카드 표시 여부
- 정렬/중복/필드 렌더링 이상 여부

---

## 4. Dropped treasure hunt 원칙

`final_news_llm_input`가 `dropped_review_treasure_hunt`를 권장하거나 사용자가 요청한 경우, Stage A에서 DROPPED 샘플을 별도 점검한다.

점검 대상 예:
- battery
- lithium
- graphite
- cathode
- anode
- separator
- ESS
- storage
- grid
- transformer
- rare earth
- critical minerals
- 배터리
- 이차전지
- 리튬
- 흑연
- 전력망
- 변압기
- 희토류
- 핵심광물

이 점검은 post-acceptance 단계가 아니라 Prompt A 단계에서 수행한다.

---

## 5. 최종 원칙

**앞으로 생성되는 카드는 full schema 기준으로만 작성·검수·병합한다.**

**Prompt A/B/C는 무엇을 accepted로 볼지 판단하고, `POST_ACCEPTANCE_CONTENT_ENRICHMENT_QC.md`는 Prompt C accepted 카드를 production-safe 데이터로 잠그는 후처리 단계다.**

**Prompt C accepted는 publish-ready가 아니다. Publish-ready는 merge safety, source coverage, content depth, language polish, final QC, GitHub sync gate를 모두 통과한 뒤에만 부여한다.**
