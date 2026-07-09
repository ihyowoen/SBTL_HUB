<!-- REPLACE_ALL_CLEAN_VERSION: LLM_PROMPT_GITHUB_CANONICAL_V1_SOURCE_DIVERSITY_IB_CODEX -->
<!-- Generated KST: 2026-07-08T21:33:49.790191+09:00 -->
<!-- This file is a full clean replacement file. It is not a patch stub. -->

# Future Card Standard — Full Schema Locked

이 문서는 **앞으로 생성될 카드**에 대한 고정 기준이다.

> **최상위 철칙:** `docs/FACT_DISCIPLINE.md` — fact·숫자·인용의 정확성 절대 기준. 본 문서의 어떤 항목보다 우선한다.

## 1. 신규 카드 표준

앞으로의 신규 카드는 **full schema only** 로 본다.

```json
{
  "id": "YYYY-MM-DD_REGION_NN",
  "region": "KR|US|CN|JP|EU|GL",
  "date": "YYYY-MM-DD",
  "cat": "Battery|ESS|Materials|EV|Charging|Policy|Manufacturing|AI|Robotics|PowerGrid|SupplyChain|Other",
  "sub_cat": "자유형 한국어 서브카테고리",
  "signal": "top|high|mid",
  "title": "...",
  "sub": "...",
  "gate": "...",
  "fact": "...",
  "implication": ["...", "..."],
  "urls": ["..."],
  "related": ["..."],
  "fact_sources": [
    {"claim": "...", "source_url": "...", "source_quote": "...", "fetched_at": "ISO8601"}
  ]
}
```

- `id`: `docs/CARD_ID_STANDARD.md` 참조
- `cat`: Primary Category Taxonomy 내 12개 중 하나
- `sub_cat`: 편집자 freestyle 한국어
- `related`: 본문 안에 ID 하드코딩 금지, 배열로만 관리
- `fact_sources`: 필수

---

## 2. Region Label Rule — Locked

region은 기사 출처 국가가 아니라 **사건의 직접 무대**로 붙인다.

- KR / US / CN / JP는 해당 국가가 직접 무대일 때만 사용
- 유럽 개별 국가 사건과 EU 제도 뉴스는 EU
- 두 개 이상 국가가 동등하게 핵심이면 GL
- 현재 배지 체계 밖 국가는 GL
- 애매하면 GL

### 2.1 엣지케이스 판례

**해외 상장·해외 자본 조달**: 본토 기업의 해외 상장/증자는 기업 본국 기준.

**정책 검토·정책 보도 단계**: 정책 발화지 기준.

**합작/JV**: 두 국가 지분·경영 동등이면 GL, 한 쪽 지배면 지배 쪽 국가.

**다국적 제품·플랫폼 런칭**: 최초 런칭 시장 기준.

**매체 국적**: region 판정에 무관.

---

## 3. Category Taxonomy — Locked

| cat | 정의 |
|---|---|
| Battery | 셀·팩·차세대 배터리, 배터리 제조사 동향 |
| ESS | 계통·산업용·주거용 에너지 저장 프로젝트·정책·시장 |
| Materials | 양극재·음극재·전해질·분리막·핵심광물·재활용 |
| EV | 전기차 OEM·모델·판매 |
| Charging | EV 충전 인프라·CPO·충전기·V2G |
| Policy | 정부 정책·규제·법안·보조금·세제·무역조치 |
| Manufacturing | 공장·장비·소부장·생산시설 |
| AI | AI 데이터센터·GPU·전력 수요 |
| Robotics | 휴머노이드·embodied AI 하드웨어 연결 |
| PowerGrid | 전력망·재생에너지 발전 사업·PPA |
| SupplyChain | 수출통제·관세·물류·공급망 리스크 |
| Other | 위 12개에 맞지 않는 경우, 신중 사용 |

### 3.1 Category 할당 규칙

1. 한 카드는 정확히 하나의 primary `cat`을 가진다.
2. 두 축에 걸치면 더 지배적인 축으로 배정하고 나머지는 `sub_cat`에 반영한다.
3. `Other`는 신중히 사용한다.

### 3.2 sub_cat 권장 형식

- 한국어 복합어
- 쉼표·세미콜론·`|` 금지
- 10자 내외 권장

---

## 4. 최종 원칙

**앞으로 생성되는 카드는 full schema 기준으로만 작성·검수·병합한다.**
**그리고 `fact_sources` 없는 카드는 payload에 포함되지 않는다.**


## 부록 A — Category Migration Policy (Locked, 20260513)

§3 Category Taxonomy 의 locked 12 cat 외 production 에 보존된 legacy 값들에 대한 마이그레이션 정책:

### A.1 Legacy 보존 정책

다음 non-locked cat 값들은 production 의 `cards.json` 에 historical state 로 **보존**된다 (재명명 금지, `docs/CARD_ID_STANDARD.md` §4 와 동일 원칙):

- `Solar`, `Hydrogen`, `Equity`, `Energy`, `Strategy`
- 한국어 compound 형식 (`ESS·중국`, `정책·관세`, `재활용·순환경제` 등)

### A.2 신규 카드 적용 정책

**신규 카드 (이번 run 및 이후 생성되는 모든 카드)** 의 `cat` 필드는 §3 의 locked 12 만 사용:

`Battery | ESS | Materials | EV | Charging | Policy | Manufacturing | AI | Robotics | PowerGrid | SupplyChain | Other`

- production legacy 값 (`Solar`, `Hydrogen` 등) 을 신규 카드에 매핑 **금지**
- 영어 compound 신조어 (`EV_charging_infrastructure` 등) 매핑 **금지**
- 12 중 어디에도 명확히 속하지 않을 때만 `Other` 사용 (신중히)

### A.3 매핑 가이드 (legacy → locked)

신규 카드를 작성할 때 legacy 가 떠오르면 다음 매핑 권장:

| legacy 발상 | 신규 권장 cat |
|---|---|
| Solar (utility-scale grid) | `PowerGrid` |
| Solar (manufacturing / M&A) | `Manufacturing` |
| Solar (panel materials) | `Materials` |
| Hydrogen (연료전지) | `SupplyChain` 또는 `Manufacturing` |
| Hydrogen (정책) | `Policy` |
| Equity | `Policy` 또는 cat 자체보다 sub_cat 활용 |
| Strategy | event 의 주된 도메인으로 (Battery/ESS/Materials/EV 등) |

### A.4 근거

`src/story/buildCardConsultContext.js` 가 cat 매치에 weighting 을 적용하므로, locked 12 외 값을 가진 신규 카드는 동종 카드 풀 (Battery 113건, ESS 163건, Materials 124건 등) 과 매칭 안 되어 related-card retrieval 이 fragment 된다.

---

## 부록 B — Region Decision Clarifications (Locked, 20260513)

§2 Region Label Rule + §2.1 엣지케이스를 보강한다. run 20260512_134524 에서 발견된 US-specific 케이스가 GL 로 분류되어 `src/App.jsx` 의 strict filter `(c.r || c.region) === filter` 에 의해 US 뉴스데스크에 노출되지 않은 사례.

### B.1 US-specific 판정 강화 케이스

다음 케이스는 region = `US` 로 분류 (외국 자본이 주체여도 무방):

| 케이스 | 예시 | region |
|---|---|---|
| 미국 시설 신설·증설·M&A | 한화 Qcells 미시간 Jabil 공장 가정용 BESS 조립 | `US` |
| 미국 제조법인 인수 | FH Capital (Korea) 의 JinkoSolar 미국 제조법인 75.1% 인수 | `US` |
| NYSE / Nasdaq IPO·상장 | Sunshine Silver (Idaho mine) NYSE Form S-1 제출 | `US` |
| 미국 시 / 주 / 연방 정부 정책 발표 | 필라델피아 시 curbside 충전 inception agreement | `US` |
| 미국 위치 광산 / 인프라 자산 거래 | (위 Sunshine Silver Idaho) | `US` |

### B.2 GL 유지 케이스

다음 케이스는 region = `GL`:

- 다국적 hyperscaler MSA / 글로벌 매출 (예: Fluence FY26 Q2 글로벌 수주 실적)
- 글로벌 시장 통계 / 분석 리포트 (예: BNEF 100GW 글로벌 ESS)
- Allowed-set 외 단일 국가 사건 (호주·인도·이집트·나우루·뉴질랜드 등)

### B.3 결정 우선순위

`region` 결정 시 다음 순서로 판정:

1. **Event 의 무대가 단일 allowed 국가** (KR/US/CN/JP/EU 중 하나) → 그 국가
2. **두 개 이상 allowed 국가가 동등** → `GL`
3. **Event 의 무대가 allowed-set 외 국가** → `GL`
4. **무대가 글로벌 또는 추상적** → `GL`
5. **매체 국적 / 보도 언어** → region 판정과 무관 (예: 한국 매체가 미국 시설 보도해도 US)

### B.4 다운스트림 영향

`src/App.jsx`:
```javascript
const filtered = cards.filter(c => filter === 'all' || (c.r || c.region) === filter);
```

이 strict equality 필터가 region 별 newsdesk 노출을 결정. misclassification 시 해당 region 사용자에게 카드가 안 보이며, 0.9 production verification 에서도 발견하기 어려움 (cards.json 자체에는 존재하나 UI 에 안 노출). Codex bot review 가 이 패턴을 catch 한 바 있음.

# FUTURE_CARD_STANDARD_FULL_SCHEMA.md — Source Diversity source-diversity integrated rule

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

## Full-schema additions

Each card must include:

```json
{
  "source_evidence_entry_count": 0,
  "source_unique_url_count": 0,
  "source_unique_domain_count": 0,
  "source_independent_owner_count": 0,
  "source_unique_domains": [],
  "source_diversity_status": "",
  "source_diversity_measure": "canonical_unique_domain_and_editorial_independence",
  "source_diversity_roles": {},
  "source_synthesis_applied": false,
  "source_synthesis_fields": [],
  "source_synthesis_audit": [],
  "needs_source_diversity_remediation": false
}
```

Each `fact_sources[]` entry must include the fields defined in the common rule.

Multiple claim rows from one article are allowed for evidence mapping, but UI and source counts must
group them under one canonical source.

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
