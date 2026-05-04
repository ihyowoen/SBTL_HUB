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
### Rule 6. accepted payload는 병합 전 post-acceptance enrichment / final QC를 거친다

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

---

## 2. 작업 전 준비
## 3. 표준 병합 절차

### Accepted Payload 후처리 운영

A/B/C 또는 동등한 triage-review 결과 accepted payload가 확정되면, baseline `cards.json`에 병합하기 전에 반드시 다음 문서를 적용한다.

- `docs/POST_ACCEPTANCE_CONTENT_ENRICHMENT_QC.md`

이 단계는 신규 카드를 추가 선별하는 단계가 아니라, 이미 accepted 된 카드를 production-safe 데이터로 잠그는 후처리 단계다.

필수 산출물:

1. content-enriched accepted payload
2. baseline에 병합한 final cards.json
3. QC report

완료 기준:

- visible fields(`title`, `sub`, `gate`, `fact`, `implication`)만 재작성
- `fact_sources` / `source_quote` 보존
- source URL 및 metadata 보존
- 신규 accepted 내부 ID/URL/사건 중복 없음
- baseline과 사건 중복 없음 또는 QC report에 명시
- 금지 문구 0개
- 중국어·일본어 원문 visible field 잔존 0개
- implication 2개 미만 카드 0개
- fact 2문장 미만 카드 0개
- gate 2문장 미만 카드 0개
- sub 1문장 초과 카드 0개
- unsupported number / causal claim / benefit claim 0개
- schema/type drift 0개
- latest-first 정렬 유지
- web QC는 검증·충돌탐지·중복탐지용으로만 수행

## 4. 병합 전 체크 기준
## 5. 병합 도구 운영상 주의점
## 6. 실수 방지 규칙

추가 실수 방지 규칙:

- accepted enrichment 단계에서 dropped/pending/rescue 항목을 임의로 되살리지 않는다.
- web search로 새 사실을 찾더라도 사용자 승인 없이 visible fields나 `fact_sources`에 조용히 추가하지 않는다.
- expected final count는 강제 숫자가 아니다. 중복/제외 사유가 있으면 QC report에 사유와 실제 count를 남긴다.
- 기존 baseline 카드는 사용자가 명시하지 않는 한 수정하지 않는다.

## 7. 실제 검증 항목

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

Post-acceptance enrichment 이후 추가 확인 항목:
- `fact_sources` 보존 여부
- `source_quote` 보존 여부
- visible field 외 변경 여부
- schema/type drift 여부
- banned workflow phrase 잔존 여부
- 외국어 원문 잔존 여부
- baseline과 신규 accepted 간 중복 사건 여부
- latest-first 정렬 여부
- final web QC 수행 여부 및 예외 사유

---

## 8. 최종 한 줄 원칙

**SBTL_HUB는 자동 수집 앱이 아니라 편집된 intelligence 앱이다.**

**Accepted payload는 바로 merge하지 않고, post-acceptance enrichment / final QC를 거쳐 production-safe 데이터로 잠근 뒤 병합한다.**
