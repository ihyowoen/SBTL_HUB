<!-- REPLACE_ALL_CLEAN_VERSION: LLM_PROMPT_GITHUB_CANONICAL_V1_SOURCE_DIVERSITY_IB_CODEX -->
<!-- Generated KST: 2026-07-08T21:33:49.790191+09:00 -->
<!-- This file is a full clean replacement file. It is not a patch stub. -->

# FACT DISCIPLINE — Locked

## 0. 이 문서의 역할

SBTL_HUB는 산업 인텔리전스 뉴스레터다. 뉴스는 **정확성**이 생명이고, 잘못된 정보를 전달하면 프로덕트 신뢰가 끝난다.

이 문서는 **카드에 들어가는 모든 fact·숫자·인용**에 대한 절대 기준을 잠근다. 다른 모든 문서의 규칙보다 상위에 있으며, 충돌 시 본 문서가 우선한다.

**User 명시 입장 (2026-04-17):** *"뉴스라서 정확성이랑 데이터가 생명이야. 잘못된 정보를 전달하면 끝나. 절대금지절대."*

---

## 1. 절대 금지 — PROHIBITED

다음은 **예외 없이 금지**된다.

### 1.1 기억·훈련 데이터에서 가져온 숫자·팩트 인용
- 기억이 맞다 하더라도 **원문 fetch 없이는 fact 필드에 쓰지 않는다**.
- 기업 로드맵, 점유율, 에너지밀도, 양산 일정, 시장 규모 등은 반드시 원문 근거가 필요하다.

### 1.2 출처 없는 숫자 생성
- 근거 없는 정량 추정, 환산, 비교, 비용, 수익, 시장규모를 만들지 않는다.
- 그럴듯한 수치를 채우라는 요청이 있어도, 근거 없으면 작성하지 않는다.

### 1.3 비교 기준 없는 "과거 대비" 서술
- 두 시점 모두 출처가 있을 때만 비교한다.
- 과거 가이던스, 이전 계획, 이전 실적을 기억으로 채우지 않는다.

### 1.4 환산 근거 없는 통화 환산
- 원문에 환산이 있으면 그대로 인용한다.
- 원문에 환산이 없으면 추가하지 않거나, 추가 시 환율 출처와 기준 날짜를 명시한다.

### 1.5 기억 기반 기업 로드맵·타임라인 인용
- 기업 계획은 최신 IR·공시·보도자료·공식자료 원문에만 근거한다.
- implication에도 출처 없는 구체 연도·생산량·CAPA를 쓰지 않는다.

### 1.6 추론을 fact와 같은 어조로 서술
- 추론은 implication에서 관찰형 어휘로만 쓴다.
- “~한다”, “~로 이어진다”, “~에 반영된다”처럼 사실처럼 보이는 단정형 추론을 금지한다.

---

## 2. 절대 의무 — REQUIRED

### 2.1 fact 작성 전 web_fetch 의무
- 모든 passed_spec의 `primary_url`은 Prompt B 실행 시 provided source-candidate 로만 취급한다. 실제 web_fetch 후 body-level evidence 여부를 검증하고, 부족하면 공식/대체 source discovery 로 검증 또는 대체한다.
- fetch 실패 시 동일 이벤트의 다른 매체 URL로 재시도한다.
- 모두 실패 시 카드 생성 중단 또는 `_fact_unverified=true` + `_needs_review=true`로 둔다.

### 2.1A fact/evidence/source-discovery package 분리
- `fact_package`, `evidence_package`, `source_discovery_ledger[]`, `source_claim_coverage_map[]`은 서로 다른 증거물이다.
- `fact_package` / `evidence_package`는 fetch/quote를 증명하지만, source diversity를 증명하지 않는다. source diversity는 `source_discovery_ledger[]`와 함께 판단한다.
- `source_discovery_ledger[]`에는 official/primary/cited/same-event alternate search 시도, 미사용 source, 미사용 이유를 기록한다.
- 모든 visible claim은 `source_claim_coverage_map[]`에서 body-level 또는 official-material quote에 매핑되어야 한다.
- single-source fact package는 official/primary single-source exception이 명시될 때만 통과 가능하다. 그 외에는 source augmentation hold 또는 visible claim 축소가 필요하다.
- web search는 동일 Stage A event anchor 검증/보강에만 사용한다. 새 candidate 생성, event 확장, silent background claim 추가는 금지한다.

### 2.2 fact_sources 필드 기록
각 카드에는 fact에 등장하는 모든 숫자·고유명사·인용·날짜에 대응하는 `fact_sources`를 기록한다.

```json
"fact_sources": [
  {
    "claim": "source-backed factual claim",
    "source_url": "https://...",
    "source_quote": "verbatim source substring",
    "fetched_at": "ISO8601"
  }
]
```

- 대응 없는 수치·고유명사·날짜·인용은 fact에서 제거한다.
- `source_quote`는 원문에서 직접 복사 가능한 구절이어야 하며 자의적 번역·요약문은 금지한다.

### 2.3 불확실 시 비워두기
- 일부 필드가 짧아지는 것은 정당하다.
- 빈 칸을 기억·추론으로 채우는 것이 잘못된 정보의 주 원인이다.

### 2.4 Prompt C red-team fact 검증
- 각 카드 fact의 모든 숫자·고유명사·인용·날짜가 `fact_sources`의 `source_quote`와 대응하는지 검증한다.
- 대응 없는 수치·인용 검출 시 payload에서 제외하고 사유를 기록한다.

---

## 3. fact 필드 — 허용 / 금지

### 3.1 허용
- 원문에 명시적으로 적힌 수치·날짜·주체·인용
- 원문 문장의 의미를 바꾸지 않는 한국어 번역·요약
- “X에 따르면” 형태의 attribution
- 복수 출처의 교집합 정보

### 3.2 금지
- 원문에 없는 숫자·비교·해석·맥락 추가
- 출처 불명확한 “업계”, “시장”, “분석가들” 표현
- reporter speculation을 fact처럼 쓰는 행위

---

## 4. implication 필드 — 관찰형만 허용

### 4.1 금지
- “X가 나온다” / “X한다” / “X 가능성이 증가” / “X에 반영된다”

### 4.2 허용
- “X할 여지가 있다”
- “X하는 방향으로 열린다”
- “X 신호가 보인다”
- “X가 관찰 포인트다”
- “X인지 확인이 필요하다”

### 4.3 implication에도 적용되는 정확성 원칙
- implication에 등장하는 수치·연도·회사 계획도 fact_sources 대응이 필요하다.
- 사실 기반이 없는 implication은 제거한다.

---

## 5. 숫자 인용 규칙

- 원문 수치의 단위·정밀도를 임의로 바꾸지 않는다.
- `about`/`approximately` 여부를 원문보다 과하게 바꾸지 않는다.
- 환산 수치는 원문 환산 또는 기준일 환율 출처가 있을 때만 허용한다.

---

## 6. fact_sources 필드 스키마

필수 최소 필드:

```json
{
  "claim": "string",
  "source_url": "string",
  "source_quote": "string",
  "fetched_at": "ISO8601"
}
```

Post-acceptance publish-forward 단계에서는 `source_name`, `source_quote_status`, `evidence_role`, `supports`, `fetch_method` 등 확장 필드를 요구할 수 있다.

---

## 7. Pre-publish Self-check

- fact에 등장하는 모든 숫자·날짜·고유명사·인용이 source_quote로 확인되는가?
- 환산 수치의 기준이 명시됐는가?
- implication이 관찰형인가?
- source_url이 urls 배열에도 존재하는가?
- fact_sources가 비어 있지 않은가?

한 항목이라도 fail이면 publish payload에서 제외한다.

---

## 8. 실제 위반 사례

- 기억 기반 K-배터리 양산 타임라인 인용
- 원문에 없는 V2G 수익 수치 생성
- 근거 없는 과거 대비 비교

---

## 9. Assistant assertion discipline — QC 결론의 검증 의무

> R3C_P04 integrated rule (run 20260516_012728 retrospective). 이 절은 카드 fact 가 아니라
> **assistant 가 run 에 대해 내놓는 진술**에 적용된다.

### 9.1 적용 대상

assistant 가 run·stage·카드 집합에 대해 내놓는 모든 결론적 진술. 예:
- "single-source 카드 N건은 정상이다"
- "이상 없음 / clean / 문제 없음 / 다 통과"
- "관련 이슈 없음", "검증 완료"

### 9.2 절대 규칙

위와 같은 진술은 **실제 item-by-item 검사를 실행한 결과**로만 뒷받침할 수 있다.
일반화·추정·"보통 그렇다"·기억으로 단정하지 않는다.

- item 단위로 직접 확인하지 **않았으면**, "정상 / clean / 문제 없음"이라고 말하지 않는다.
- 대신 **"미검증(unverified)"**이라고 명시한다. 미검증은 정직한 상태이고, 거짓 결론은 위반이다.
- "N건 검사 → M건 통과, K건 flag"처럼 검사 범위와 결과 수를 함께 적는다. 검사를 안 했으면 그 사실을 적는다.

### 9.3 위반 사례 (run 20260516_012728)

0.5 단계에서 single-source 21건을 검사 없이 "정상"으로 단정 → 3건 spot-check 즉시 반증.
일반화를 결론으로 제시한 것이 핵심 실패였다 (PV_006). 이 절은 그 실패 모드를 직접 차단한다.

### 9.4 Self-check

- 내가 방금 "정상/clean/이상없음"이라고 했는가? → 그 판단을 뒷받침하는 실행된 검사가 있는가?
- 없으면 진술을 "미검증"으로 교체한다.

---

## 10. 최종 원칙

1. 모르면 비워둔다.
2. 원문에서 보지 않았으면 쓰지 않는다.
3. 추론과 사실을 어휘로 분리한다.
4. 한 카드의 실수는 전체 플랫폼의 신뢰를 깎는다.

**정보가 없으면 카드는 생성하지 않는다.**
**정확성은 스타일이 아니라 생명선이다.**

## FIX-001 — PROVIDED_SOURCE_IS_NOT_EVIDENCE_RULE

A provided URL, `primary_url`, triage URL, uploaded link, source hint, Stage A `usable_text`, or Stage A `context_text` is **not evidence by itself**.

It is only an evidence candidate. It becomes evidence only after Stage B has fetched or directly inspected the source, recorded the resolved `source_url`, extracted body-level / official-material / document-level support, captured `source_quote`, mapped that quote to a specific claim, recorded fetch metadata, and included it in `evidence_package` and `fetch_ledger`.

A `fact_sources` entry built only from a provided URL without fetched/directly inspected evidence is invalid.

# FACT_DISCIPLINE.md — Source Diversity source-diversity integrated rule

    This integrated rule is authoritative for source-diversity, source-preservation, synthesis,
    visible-source-date and same-source grouping rules. Earlier language that conflicts with this
    integrated rule is superseded only to the extent of that conflict.

    ## Source Diversity source-diversity — common definitions

### 1. Diversity unit

Source diversity is measured by **canonical source identity and editorial independence**, not by
`fact_sources[]` row count.

The following count as one source:

- multiple claims or quotes from the same canonical article URL;
- print/mobile/AMP/RSS mirrors of the same article;
- the same press release copied by multiple syndication sites without independent reporting;
- multiple pages controlled by the same editorial owner that merely repeat the same source text;
- one article split into several `fact_sources[]` entries.

Required calculations:

```text
source_evidence_entry_count = count(fact_sources[])
source_unique_url_count = count(unique canonical article URLs)
source_unique_domain_count = count(unique canonical domains after ownership/syndication review)
source_independent_owner_count = count(editorially independent source owners)
```

`PASS_MULTI_SOURCE` or any equivalent status is prohibited when
`source_independent_owner_count < 2`.

### 2. Preferred evidence-role structure

For each independently cardable event, target three complementary roles:

1. `primary_event_evidence`
   - official notice, regulator, filing, contracting party, project owner, research institution,
     original dataset or source owner;
2. `independent_event_confirmation`
   - independent news agency, financial press, trade press or local reporting that confirms the
     event and identifies omissions, conditions or execution status;
3. `policy_market_context`
   - policy, market, operational, comparable-project or system-impact evidence that materially
     improves `gate` or `implication`.

Two independent source owners are the minimum default. Three complementary roles are preferred.
A source does not satisfy diversity merely by existing; it must make a distinct contribution.

### 3. Source contribution requirement

Every retained source must record:

```json
{
  "source_role": "",
  "source_contribution": "",
  "source_origin_type": "",
  "source_published_date": "YYYY-MM-DD",
  "visible_quote_date": "YYYY-MM-DD"
}
```

`source_contribution` must explain the unique information supplied by that source. Generic values
such as `corroboration`, `additional source`, `supports card`, or `same event` are insufficient.

### 4. Visible-field synthesis requirement

When an additional source supplies material information, at least one of the following visible
fields must be revised using source-locked wording:

- `fact`
- `gate`
- `implication`

The output must record:

```json
{
  "source_synthesis_applied": true,
  "source_synthesis_fields": ["fact", "gate", "implication"],
  "source_synthesis_audit": [
    {
      "source_domain": "",
      "source_role": "",
      "unique_contribution": "",
      "affected_visible_fields": []
    }
  ]
}
```

A card that merely integrates URLs while its visible content still reflects only one article has not
passed source-diversity synthesis.

### 5. Publication date and audit timestamps

The date shown beside a quote must be the article or official-material publication date:

```text
visible date = source_published_date
```

`fetched_at` and `checked_at` are audit timestamps only. They must be preserved but must never be
used as the visible news date.

### 6. Rescue-before-delete rule

A weak, blocked or duplicate source must not be silently discarded when it contains unique useful
information.

Use this order:

1. refetch or locate the source owner/original material;
2. find an independent same-event source;
3. narrow unsupported wording;
4. move unique information into an existing card as reinforcement;
5. place unresolved items in `needs_source_augmentation` or a controlled remediation queue;
6. use hard rejection only when the item is false, irrelevant, irreparable, promotional noise or
   lacks any defensible decision value.

Duplicate-event articles are not separate cards, but their unique facts and quotes must follow the
representative event as support-source candidates.

### 7. Single-source exception

A single-source exception is narrow and rare. It may pass only when all conditions are true:

- the source is official, regulatory, a filing, original dataset, court decision, contracting-party
  release, or original research institution;
- bounded discovery was performed and no independent body-level source was available;
- the card contains only claims supported by that source;
- no broad causal, comparative, first/largest, market-impact or strategic implication is asserted
  unless the source explicitly supports it;
- the exception reason, search ledger and scope limitation are recorded;
- downstream Evidence QC and Final QC separately approve the exception.

A media article alone does not qualify merely because it is detailed.

## Fact-discipline implications

Source diversity never permits claim inflation. Multiple sources may broaden a card only to the
extent that their body-level or official evidence supports the added wording.

Each number, date, named entity, legal stage, contract condition, comparative claim and causal
statement must map to a source quote. Source diversity and claim coverage are separate gates; both
must pass.

A quote may be split into multiple contiguous entries for traceability, but those entries remain one
source. Ellipsis-stitched or composite verified quotes are prohibited.

# Source Diversity / IB-grade + Codex Hardening Integrated rule

Version: `GITHUB_CANONICAL_V1_SOURCE_DIVERSITY_IB_CODEX`  
Generated KST: `2026-07-08T21:18:40.089502+09:00`

This integrated section supersedes earlier conflicting language only to the extent of conflict.  
It does **not** weaken Source Diversity source-diversity. It adds downstream hardening learned from PR #148 and the 20260706_130022 run.

## 1. IB-grade editorial upgrade rule

Cards should not be treated as publishable merely because they are fact-safe.

Before `publish_ready=true`, the pipeline must classify each card into one of the following:

| Tier | Meaning | Publish rule |
|---|---|---|
| `A` / `A-` | IB-grade or near-IB anchor | May be used as lead/anchor signal |
| `B+` | publishable supporting signal | May publish, but must not be described as top-tier anchor |
| below `B+` | insufficient | Must remain deferred, remediation, or support-only |

A `B+` card may be upgraded only through supported visible-field refinement:

- stronger strategic framing;
- clearer `sub`;
- sharper `gate`;
- implication rewritten toward market / policy / supply-chain decision use;
- no unsupported new numbers, contracts, capacity, pricing, or customer claims.

Never upgrade a weak source into a strong source by language alone.

## 2. Visible-field upgrade boundary

When improving title, sub, fact, gate, or implication:

- preserve all source boundaries;
- do not add a new factual claim unless it is directly supported by an existing `fact_sources[]` quote or an added source;
- do not convert `prequalified` into `awarded`;
- do not convert `pilot` into commercial performance;
- do not convert product showcase into customer order, certification, delivery, or revenue;
- do not convert policy award/achievement material into implementing notice unless the notice text is present;
- do not convert “focus / plan / report says” into confirmed CAPEX, customer, chemistry, or production start.

## 3. Single-source publish-ready waiver rule

If a card has:

```text
publish_ready = true
source_independent_owner_count = 1
```

then it must satisfy one of the following:

1. official / regulator / company primary source;
2. reputable market data provider with bounded data claim;
3. reputable trade or mainstream media with body-level evidence and bounded claims;
4. explicit user-provided official body text.

A valid waiver must include:

```json
"single_source_exception": {
  "allowed": true,
  "type": "...",
  "reason": "...",
  "mitigation": "..."
}
```

Invalid patterns:

```json
"single_source_exception": {
  "allowed": false,
  "reason": "two or more source owners..."
}
```

on a publish-ready single-source card is a blocker.

Required blocker:

```text
status = BLOCKED_PUBLISH_READY_SINGLE_SOURCE_WITHOUT_VALID_WAIVER
```

## 4. Stale publish blocker removal rule

No card may be both publish-ready and actively blocked.

Invalid:

```json
{
  "publish_ready": true,
  "state": "publish_ready",
  "do_not_publish_until": "..."
}
```

If the blocker has been satisfied, remove the active field entirely.

Permitted audit trail:

```json
"prior_publish_blocker_removed": {
  "field": "do_not_publish_until",
  "old_value": "...",
  "reason": "...",
  "removed_at_kst": "..."
}
```

Required blocker:

```text
status = BLOCKED_PUBLISH_READY_CARD_HAS_ACTIVE_DO_NOT_PUBLISH_UNTIL
```

## 5. Deferred/watchlist discipline

Do not delete high-value deferred cards simply because official/independent evidence is not yet available.

Use:

- `deferred_watchlist_high_value`
- `conditional_watchlist`
- `support_only_pending`
- `deprioritized_not_deleted`

A deferred card can be promoted only when the missing source-claim coverage is actually satisfied.

## 6. PR / GitHub merge hardening

Before PR or merge:

- verify total count;
- verify latest baseline;
- verify `publish_ready` cards have no active blockers;
- verify single-source publish cards have valid waiver;
- verify no visible internal terms remain:
  - `fetch`
  - `stage`
  - `quote mapping`
  - `baseline` unless user-facing context explicitly requires it;
- verify `source_independent_owner_count` is editorial-owner based, not `fact_sources[]` row count;
- verify UI display groups same canonical URL once;
- verify quote date is article/publication date, not fetch/check date.

## 7. Codex response protocol

If Codex flags metadata inconsistency:

1. Determine whether the issue is a visible claim problem or metadata/QC state problem.
2. Do not expand visible claims unless evidence requires it.
3. Prefer minimal metadata fix if the card is already fact-safe.
4. Add an audit record only if it is non-blocking.
5. Re-run:
   - JSON parse
   - publish-ready blocker scan
   - single-source waiver scan
   - visible internal-term scan
   - total count check

## 8. Required final statuses

A card may be merged only when:

```text
accepted_fact_safe = true
addable_merge_safe = true
evidence_complete = true
source_claim_covered = true
content_enriched = true
language_terminology_polished = true
publish_ready = true
github_ready = true
```

Any waiver or exception must be explicit, bounded, and auditable.
