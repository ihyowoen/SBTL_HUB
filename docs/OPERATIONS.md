# SBTL_HUB 운영 매뉴얼

## 0. 이 문서의 역할

이 문서는 **실무자가 실제로 무엇을 백업하고, 무엇을 실행하고, 무엇을 확인해야 하는지**를 적는 운영 매뉴얼이다.

신규 카드 기준은 **full schema only** 다.

---

## 1. 운영 기본 규칙

### Rule 1. production 기준은 main이다
### Rule 2. cards.json은 민감 파일이다
### Rule 3. merge 전에 반드시 백업
### Rule 4. merge는 production 확인이 끝나야 종료
### Rule 5. 신규 카드 payload는 full schema 기준이다
### Rule 6. Prompt C accepted payload는 병합 전 post-acceptance enrichment / final QC를 거친다
### Rule 7. Prompt C accepted는 publish-ready가 아니다
### Rule 8. expected final count는 강제 숫자가 아니다

필수 필드:
- `id`
- `region`
- `date`
- `cat`
- `signal`
- `title`
- `sub`
- `gate`
- `fact`
- `implication`
- `urls`
- `fact_sources`

---

## 2. One-page run checklist

이 체크리스트는 실무자가 매 run마다 가장 먼저 보는 실행용 요약이다.
상세 판단은 `docs/PROMPT_ABC_DEFAULT_MODE.md`, `docs/FACT_DISCIPLINE.md`, `docs/POST_ACCEPTANCE_CONTENT_ENRICHMENT_QC.md`를 따른다.

### A. 시작 전

- [ ] 현재 작업 branch와 목적 확인
- [ ] 규칙 문서 최신본 확인
- [ ] latest `final_news_llm_input`의 `run_tag`, `generated_kst`, story count 확인
- [ ] baseline source 선언: `github_main` / `local_final_candidate` / `user_uploaded_baseline`
- [ ] baseline card count 확인
- [ ] source metadata에 `dropped_review_treasure_hunt` 권장 여부 확인

### B. Stage A — 후보 선별

- [ ] `KEEP / REVIEW / STEP2_PENDING` 전체 outcome ledger 작성
- [ ] passed / discarded / merged / existing_reinforcement 분리
- [ ] discarded 항목은 reason code 기록
- [ ] baseline URL·canonical URL·event fingerprint 중복 확인
- [ ] dropped treasure hunt가 필요한 run이면 Stage A에서 샘플 점검 기록

### C. Stage B — draft + evidence

- [ ] passed spec만 draft 작성
- [ ] source verification 수행
- [ ] `fact_sources`에 핵심 claim 근거 연결
- [ ] source coverage 기록
- [ ] single-source card는 reason 기록
- [ ] snippet/paywall/title-only/repost는 core claim 근거로 사용하지 않음

### D. Stage C — fact-safe acceptance

- [ ] accepted / revise_required / rejected 분리
- [ ] `accepted`는 `accepted_fact_safe`일 뿐 publish-ready가 아님을 명시
- [ ] revise_required는 B revise → C revise loop로 처리
- [ ] rejected / revise_required / non-accepted 혼입 금지

### E. Merge safety

- [ ] accepted와 addable 분리
- [ ] 신규 내부 중복 ID/URL/canonical URL/event fingerprint 확인
- [ ] baseline과 중복 사건이면 addable 제외 후 withheld/existing reinforcement로 기록
- [ ] expected final count는 강제하지 않음

### F. Source / content / language finalization

- [ ] source enrichment가 필요하면 별도 pass로 수행하고 변경 근거 기록
- [ ] content depth enrichment는 visible fields만 재작성
- [ ] `fact_sources`, `source_quote`, source URLs, metadata 보존
- [ ] implication 2개 이상, fact 2문장 이상, gate 2문장 이상, sub 1문장 유지
- [ ] 외국어 원문 visible 잔존 0개
- [ ] 금지 문구 0개
- [ ] 단위·회사명·용어 일관성 확인

### G. Publish-ready final QC

- [ ] Gate 1 Fact Safety PASS
- [ ] Gate 2 Merge Safety PASS
- [ ] Gate 3 Source Layer PASS
- [ ] Gate 4 Content Depth PASS
- [ ] Gate 5 Language & Tone PASS
- [ ] Gate 6 Publish Readiness PASS
- [ ] QC report 생성
- [ ] `publish_ready=true`는 위 6개 gate가 모두 PASS일 때만 사용

### H. GitHub 반영 전

- [ ] main sync
- [ ] current `public/data/cards.json` count 확인
- [ ] final candidate baseline count와 비교
- [ ] main에 추가 변경이 있으면 재병합 판단
- [ ] PR diff가 의도한 파일만 포함하는지 확인
- [ ] Vercel production 확인 전까지 완료로 보지 않음

---

## 3. 작업 전 준비

현재 기본 A/B/C 입력 모드는 `docs/PROMPT_ABC_DEFAULT_MODE.md`를 따른다.

기본 입력 universe:
- `final_news_llm_input.stories[]`

과거/예외 run의 `triage_output + rescue + dropped` 입력 모드는 `docs/TRIAGE_INPUT_MODE_DEFAULT.md` 또는 사용자의 명시 지시가 있을 때만 적용한다.

Baseline은 원칙적으로:
- GitHub `main` `public/data/cards.json`

단, 사용자가 명시적으로 직전 최종 후보 파일을 baseline으로 지시한 경우 다음 중 하나로 표기한다.

- `github_main`
- `local_final_candidate`
- `user_uploaded_baseline`

`local_final_candidate` 또는 `user_uploaded_baseline` 기준 산출물은 PR/merge 전 반드시 GitHub main sync gate를 다시 통과해야 한다.

---

## 4. 표준 병합 절차

### Accepted Payload 후처리 운영

Prompt C 또는 동등한 final validator 결과 accepted payload가 확정되면, baseline `cards.json`에 병합하기 전에 반드시 다음 문서를 적용한다.

- `docs/POST_ACCEPTANCE_CONTENT_ENRICHMENT_QC.md`

이 단계는 신규 카드를 추가 선별하는 단계가 아니라, 이미 accepted 된 카드를 production-safe 데이터로 잠그는 후처리 단계다.

상태는 반드시 분리한다.

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

필수 산출물:

1. content-enriched accepted payload
2. baseline에 병합한 final cards.json
3. QC report

완료 기준:

- visible fields(`title`, `sub`, `gate`, `fact`, `implication`)만 재작성
- `fact_sources` / `source_quote` 보존
- source URL 및 metadata 보존
- accepted와 addable 분리
- withheld reinforcement / existing reinforcement 사유 기록
- 신규 accepted 내부 ID/URL/사건 중복 없음
- baseline과 사건 중복 없음 또는 QC report에 명시
- event fingerprint 확인
- source coverage 검토
- single-source card 사유 기록
- claim coverage map 작성 또는 중요/취약 카드에 대해 요약 기록
- 금지 문구 0개
- 중국어·일본어 원문 visible field 잔존 0개
- 용어/단위 일관성 확인
- implication 2개 미만 카드 0개
- fact 2문장 미만 카드 0개
- gate 2문장 미만 카드 0개
- sub 1문장 초과 카드 0개
- unsupported number / causal claim / benefit claim / company intention 0개
- schema/type drift 0개
- rejected / revise_required / non-accepted 혼입 0개
- latest-first 정렬 유지
- web QC는 검증·충돌탐지·중복탐지용으로만 수행
- baseline source declaration 기록
- GitHub main sync gate 상태 기록

---

## 5. 병합 전 체크 기준

병합 전 반드시 확인한다.

1. 현재 baseline count
2. accepted input count
3. addable count
4. withheld reinforcement count
5. expected final count와 actual final count의 차이
6. 차이가 있으면 중복/제외 사유
7. 중복 ID / URL / canonical URL
8. event fingerprint 중복
9. latest-first 정렬
10. JSON 유효성

Expected final count가 다르다고 강제로 카드를 추가하지 않는다.
중복 사건이면 final count가 줄어드는 것이 맞다.

---

## 6. 병합 도구 운영상 주의점

- 병합 도구가 단순 URL 또는 title-prefix dedupe만 수행하는 경우, 별도의 event fingerprint QC를 반드시 수행한다.
- 기존 baseline 카드는 사용자가 명시하지 않는 한 수정하지 않는다.
- helper payload / prior run / branch payload는 canonical baseline이 아니다.
- source enrichment 또는 content depth enrichment 후에는 다시 final cards.json을 생성한다.
- source enrichment 없이 web search에서 찾은 새 사실을 visible fields에 조용히 넣지 않는다.

---

## 7. 실수 방지 규칙

추가 실수 방지 규칙:

- post-acceptance enrichment 단계에서 rejected / revise_required / non-accepted 항목을 임의로 되살리지 않는다.
- web search로 새 사실을 찾더라도 사용자 승인 없이 visible fields나 `fact_sources`에 조용히 추가하지 않는다.
- expected final count는 강제 숫자가 아니다. 중복/제외 사유가 있으면 QC report에 사유와 실제 count를 남긴다.
- 기존 baseline 카드는 사용자가 명시하지 않는 한 수정하지 않는다.
- Prompt A/B/C의 acceptance 판단을 post-acceptance 단계에서 조용히 뒤집지 않는다.
- background_context source만으로 revise_required 카드를 accepted/publish_ready로 올리지 않는다.
- source count를 KPI로 삼지 않는다. claim coverage를 KPI로 삼는다.
- Prompt C accepted를 “GitHub에 넣을 최종 후보”라고 부르지 않는다.
- `publish_ready=true`는 6개 final gates가 모두 PASS일 때만 쓴다.

---

## 8. 실제 검증 항목

최소 확인 항목:
- `title`
- `region`
- `date`
- `cat`
- `signal`
- `gate`
- `fact`
- `implication`
- `urls`
- `fact_sources`

Post-acceptance enrichment 이후 추가 확인 항목:
- `fact_sources` 보존 여부
- `source_quote` 보존 여부
- visible field 외 변경 여부
- schema/type drift 여부
- banned workflow phrase 잔존 여부
- 외국어 원문 잔존 여부
- 용어/단위 일관성 여부
- baseline과 신규 accepted 간 중복 사건 여부
- event fingerprint 중복 여부
- accepted vs addable 분리 여부
- source coverage / single-source reason 여부
- claim coverage map 또는 요약 여부
- latest-first 정렬 여부
- final web QC 수행 여부 및 예외 사유
- baseline source declaration
- GitHub main sync gate 상태

---

## 9. Dropped treasure hunt 운영

현재 Final-input era 기본 입력은 `final_news_llm_input.stories[]`이다.

단, source metadata가 `dropped_review_treasure_hunt`를 권장하거나 사용자가 요청한 경우 Stage A에서 DROPPED 샘플을 검토한다.

이 검토는 post-acceptance 단계가 아니라 Stage A에서 수행한다.

권장 샘플 키워드:
- battery / lithium / graphite / cathode / anode / separator
- ESS / storage / grid / transformer / rare earth / critical minerals
- 배터리 / 이차전지 / 리튬 / 흑연 / 전력망 / 변압기 / 희토류 / 핵심광물

QC report에는 다음을 남긴다.

```json
{
  "dropped_treasure_hunt": {
    "performed": true,
    "sample_size": 50,
    "rescued": 0,
    "notes": "..."
  }
}
```

---

## 10. GitHub 반영 전 sync gate

GitHub 반영 전 반드시 수행한다.

1. `main` 동기화
2. 현재 `public/data/cards.json` count 확인
3. 최종 후보 파일의 baseline count와 비교
4. main에 추가 변경이 있으면 final candidate를 그대로 덮지 말고 재병합 판단
5. PR diff가 `public/data/cards.json` 또는 의도된 docs/data 파일만 포함하는지 확인
6. Vercel production 확인 전까지 작업 완료로 보지 않음

---

## 11. 최종 한 줄 원칙

**SBTL_HUB는 자동 수집 앱이 아니라 편집된 intelligence 앱이다.**

**Prompt C accepted payload는 바로 merge하지 않고, post-acceptance enrichment / final QC를 거쳐 production-safe 데이터로 잠근 뒤 병합한다.**

**Publish-ready는 accepted가 아니라, merge safety + source coverage + content depth + language polish + final QC + GitHub sync gate를 통과한 상태다.**
