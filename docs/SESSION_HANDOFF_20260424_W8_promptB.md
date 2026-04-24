# SESSION HANDOFF — W8 Prompt B 재개 (2026-04-24)

> 이 문서는 **뉴스 파이프라인** 핸드오프. SBTL_HUB PWA 코드 핸드오프 아님.
> W8 run (`run_tag=20260423_134635`) Prompt B가 도구 제약으로 중단됨. 새 세션에서 이어받기 위한 context.

---

## 0. 현재 상태

| Stage | 상태 | 산출물 |
|---|---|---|
| **Prompt A (Selector)** | ✅ 완료 | `/mnt/user-data/outputs/PromptA_output_20260423_134635.json` (2.84MB) |
| **Prompt B (Writer)** | ❌ 미완 | — (이 문서가 재개 가이드) |
| **Prompt C (QC)** | ❌ 미시작 | — |

A output 요약:
- 40 passed_specs (`new` 32 + `follow_up` 4 + `reinforcement_of_main` 4)
- 20건 `needs_review: true`
- 3건 `source_origin: DROPPED` override
- `decision_ledger` 6,906 stories 전체 커버 (silent drop 없음)
- Cat: Battery 6 / Materials 10 / ESS 14 / PowerGrid 2 / Charging 1 / Policy 2 / Manufacturing 2 / Robotics 1 / SupplyChain 1 / EV 1
- Region: CN 15 / US 8 / KR 7 / EU 4 / GL 4 / JP 2
- Signal: top 2 / high 19 / mid 19

---

## 1. 새 세션 시작 순서 (필수)

### 1-A. 규칙 문서 로드 — GitHub MCP, `ihyowoen/SBTL_HUB` main 브랜치

우선순위 순서:

1. `docs/FACT_DISCIPLINE.md` — **최상위 철칙**, 다른 모든 문서보다 우선
2. `docs/PROMPT_ABC_DEFAULT_MODE.md` — B.1~B.7 규칙 (§Prompt B 전체)
3. `docs/FUTURE_CARD_STANDARD_FULL_SCHEMA.md` — card schema
4. `docs/CARD_ID_STANDARD.md` — id 규칙
5. `docs/PROMPT_ABC_SUPPORTING_RULES.md` — 보조 규칙

### 1-B. A 산출물 + baseline 로드

- A output: `/mnt/user-data/outputs/PromptA_output_20260423_134635.json`
  - `$.passed_specs` (40건) — B 입력
  - `$.decision_ledger` (6906건) — C가 쓰므로 B는 참고만
- Baseline: GitHub MCP → `ihyowoen/SBTL_HUB:public/data/cards.json` (317 cards, updated 2026-04-20)
  - B는 baseline_relation 재판정 안 함 (A 권한). 단 card id 넘버링 시 기존 카드 id 충돌 확인용

### 1-C. 이 문서 (§2~§5) 정독

---

## 2. B 실행 방식

### 2-A. 각 passed_spec에 대한 표준 루프

```
for spec in a_output.passed_specs:
    # 1. primary_url web_fetch (B.4 의무)
    try:
        content = web_fetch(spec.primary_url)
        web_fetch_status = "ok"
    except fetch_rejected:
        # 폴백 1: web_search로 headline/entity 검색하여 URL을 results pool에 등록 후 재fetch
        # 폴백 2: search 결과 excerpt 자체를 원문으로 간주 (단 이 경우도 verbatim 기준 유지)
        content = try_search_then_fetch(spec)
        web_fetch_status = "partial_fallback"

    if content is None:
        # 폴백 3: spec.urls[] 다른 URL 시도
        for url in spec.urls[1:]:
            content = web_fetch(url)
            if content: break

    if content is None:
        # 원문 확보 실패 → draft_blocked (권장) OR needs_review=True + _fact_unverified=True
        record_blocked(spec, reason="fact_fetch_failed_all_urls")
        continue

    # 2. fact/숫자/인용에 필요한 verbatim substring 추출
    #    - source_quote는 반드시 web_fetch로 확보한 content의 verbatim substring
    #    - upstream spec.context_text / spec.summary_hint는 참고용, substring 금지
    fact_sources = extract_verbatim_citations(content, spec)

    # 3. B.5 full schema card 작성
    card = {
        "id": build_card_id(spec),  # §2-C 참조
        "region": spec.region,
        "date": spec.representative_date,
        "cat": spec.cat,
        "sub_cat": spec.sub_cat,
        "signal": spec.signal,
        "title": ...,           # event anchor 일치, over-claim 금지
        "sub": ...,             # actor/숫자/범위로 sharpen
        "gate": ...,            # ≥40자, 편집적 중요성, fact 반복 금지
        "fact": ...,            # ≥50자, "X에 따르면" 출처 attribution
        "implication": [...],   # ≥2개, 각 ≥20자, observation/watchpoint
        "urls": spec.urls,
        "related": [],
        "fact_sources": fact_sources,
    }

    record_drafted(spec, card, web_fetch_status)
```

### 2-B. fact_sources 스키마 (필수)

각 숫자/고유명사/날짜/인용마다 1개 entry:

```json
{
  "claim": "fact/implication 내 특정 주장",
  "source_url": "실제 fetch한 URL",
  "source_quote": "web_fetch content 원문의 VERBATIM substring (paraphrase 금지)",
  "fetched_at": "2026-04-24T14:30:00+09:00"
}
```

**`fetched_at`은 실제 web_fetch 시점.** upstream `collected_at` 재사용 금지.

### 2-C. Card ID 넘버링

포맷: `YYYY-MM-DD_REGION_NN` (2자리 zero-pad)

Baseline 기준 (2026-04-20에서 끝남):
- `2026-04-20_KR_58` 가 최종 KR 카드
- `2026-04-20_CN_NN`, `2026-04-20_US_NN` 등도 각각 별도 카운터

W8 신규 카드는 **다른 날짜**이므로 각 날짜×region 조합에서 `_01`부터 새로 시작:
- `2026-04-21_KR_01`, `2026-04-21_KR_02` (L&F, 배터리솔루션즈 override 2건)
- `2026-04-22_CN_01`, `_02`, ..., `_12`
- `2026-04-22_KR_01`, `_02`, `_03`, `_04`
- `2026-04-22_US_01`, ..., `_08`
- `2026-04-22_EU_01`, ..., `_04`
- `2026-04-22_GL_01`, ..., `_04`
- `2026-04-22_JP_01`
- `2026-04-23_KR_01` (삼성SDI 1.6조)
- `2026-04-23_CN_01`, `_02`, `_03`
- `2026-04-23_JP_01`

A output의 `spec_id`는 `W8_YYYY-MM-DD_REGION_NN` 형태인데 그중 `YYYY-MM-DD_REGION_NN` 부분이 그대로 최종 card id로 사용 가능하도록 이미 할당돼 있음 → **spec_id에서 `W8_` prefix만 떼면 card id**.

---

## 3. needs_review=True 20건 (B가 특별 검증)

| spec_id | 검증 포인트 |
|---|---|
| `W8_2026-04-22_JP_01` Toyota-CATL 인도네시아 | 투자액(Rp1.3조/$76m) · 카라왕 공장 · 수출 시점 2H 2026 |
| `W8_2026-04-22_US_01` Meta × Noon 100GWh | "up to 100GWh" vs 확정 용량(25MW/2.5GWh 2028) 구분 |
| `W8_2026-04-22_US_02` SK Key Capture | 매각 vs 추가투자 수위 — "various strategic options" 표현 원문 확인 |
| `W8_2026-04-23_KR_01` 삼성SDI 1.6조 | 1.6조 추정치 출처: 미래에셋증권 리포트 vs 회사 공식 구분 |
| `W8_2026-04-21_KR_01` L&F 1.6조 LFP | 3월 공시 vs 4/21 카운터파티 공개 뉴스 구분, 삼성SDI 미국 인디애나 스타플러스 투입 |
| `W8_2026-04-22_US_03` Tesla TX 리튬정제소 | 더구루 단일출처 → Texas 환경청 원문 또는 Reuters 확인 |
| `W8_2026-04-22_US_04` Standard Lithium | 1M barrels brine / 15,000 cycles DLE / 6 years no incident 마일스톤 |
| `W8_2026-04-22_CN_02` 5GWh 해외 ESS | 수주자=BYD, 고객=Fortescue Pilbara Green Grid 4-5GWh (추정 — 본문 확인) |
| `W8_2026-04-22_CN_03` 110억 Si-C | 회사명 埃普诺(Epinuo) 四川凉山西昌 (추정 — 본문 확인) |
| `W8_2026-04-22_EU_02` LONGi EU ESS | 13.75MW/50.16MWh 이탈리아 지중해 연안 프로젝트 (추정) |
| `W8_2026-04-22_CN_07` 山西 25座 | 25座/300만kW(315.98만kW) 2026-04-14 기준시점 |
| `W8_2026-04-23_CN_03` BYD ESS 대수주 | Fortescue 4-5GWh BESS 공급 (#W8_2026-04-22_CN_02와 동일 사건 클러스터 가능성 — 재검토) |
| `W8_2026-04-22_US_06` 600kW 충전기 | ChargePoint Express Solo (추정) |
| `W8_2026-04-21_KR_02` 배터리솔루션즈 | "중국 대표 전기차 기업" 실명 (BYD 추정 — 본문 확인) |
| `W8_2026-04-22_KR_02` 엠오티 80억 | 수주처=국내 자동차 정밀 부품 기업 |
| `W8_2026-04-22_KR_03` KAI 항공 ESS | 1단계(항공기 정비용) 완료 + 2단계(AAV E2X용 ESS+HV PDU) 개발 |
| `W8_2026-04-22_CN_09` 액랭 ESS Q1 -82% | 英维克 002837.SZ 순이익 865.76만원 |
| `W8_2026-04-23_JP_01` Honda 2륜 리콜 | Mobile Power Pack e: 2만3893대 (2022-12-02 ~ 2023-04-22 제조분) |
| `W8_2026-04-22_US_07` 페로브스카이트 탠덤 | Solx × Caelux 3GW Aurora, Suniva 실리콘 셀, Puerto Rico Aguadilla |
| `W8_2026-04-22_US_08` House 광물 법안 | H.R. 1501 "Protect Domestic Mining Act" 21-16 표결 |

---

## 4. DROPPED override 3건 (추가 주의)

| spec_id | 상류 drop_reason | override 근거 |
|---|---|---|
| `W8_2026-04-21_KR_01` 엘앤에프 × 삼성SDI 1.6조 LFP | `time_out_of_window` (2026-04-21) | 3월 공시의 **카운터파티 공개** follow-up 가치 — Non-PFE LFP 양극재 최대 규모 계약 실체 드러남 |
| `W8_2026-04-22_KR_01` GS풍력 × 네이버 25년 PPA | `time_in_window / topic_not_strong` | AIDC × K-재생E 직접PPA 역대 최대 (연 180GWh, 25년) — topic strong 재평가 |
| `W8_2026-04-21_KR_02` 배터리솔루션즈 LFP 폐배터리 | `time_out_of_window` (2026-04-21) | 국내 보급 상용차 LFP 폐배터리 **전량** 확보 계약 — K-재활용 체력 보강 독립 뉴스 |

---

## 5. 알려진 제약·함정

### 5-A. Paywalled sources (fetch 실패 가능성 높음)

| 출처 | 해당 spec | 우회 |
|---|---|---|
| **딜사이트** dealsite.co.kr | W8_2026-04-23_KR_01, W8_2026-04-21_KR_01, W8_2026-04-21_KR_02 | "유료콘텐츠서비스" 차단 — web_search로 헤드라인 검색하여 search excerpt 활용 |
| **더구루** theguru.co.kr | W8_2026-04-22_US_03 | "[유료기사코]" 차단 — Reuters/Bloomberg 원 외신 보도 찾아 verbatim 추출 |
| **임팩트온** impacton.net | W8_2026-04-22_GL_03 | Reuters/Bloomberg 원 외신 보도 (NIMMA letter 관련) |
| **딜사이트TV** dealsitetv.com | W8_2026-04-22_KR_04 | 비디오 콘텐츠 — transcript 없으면 `draft_blocked` 고려 |

### 5-B. web_fetch URL 거부 문제

이전 세션 검증: 입력 파일에서 가져온 URL을 직접 `web_fetch`에 전달 시 "URL was not provided by the user nor did it appear in any search/fetch results" 오류. **우회책**:

1. 먼저 `web_search`로 해당 기사의 헤드라인/entity 조합 검색
2. search 결과에 해당 URL이 나타나면 → 그 시점부터 `web_fetch` 가능
3. 또는 search 결과 excerpt 자체가 원문의 verbatim 포함 → excerpt에서 source_quote 추출 (여전히 verbatim 기준 유지)

### 5-C. upstream `context_text` 의존 금지

A output의 각 spec에는 `summary_hint`/`context_text` 필드가 있는데 이건 **upstream excerpt** (body fetch 일부, 최대 6000자 cap). FACT_DISCIPLINE §2.2에 의해 `source_quote` 추출 금지. 반드시 **B의 새 web_fetch로 확보한 원문**에서 substring.

### 5-D. 이전 세션에서 이미 수집된 verbatim (참조만, 재fetch 필수)

W8_2026-04-22_CN_01 (CATL Super Tech Day) + W8_2026-04-22_JP_01 (Toyota Indonesia CATL) 2건에 대해 이전 세션에서 web_search verbatim 일부 확보됨. 하지만:
- `fetched_at`은 **새 세션의 실제 fetch 시점**이어야 함 → 재실행
- FACT_DISCIPLINE §2.1에 예외 없음 → 새 세션에서 web_search/fetch 반복

---

## 6. Output 기대

### 6-A. 파일
- `/mnt/user-data/outputs/PromptB_output_20260423_134635.json` (canonical, valid JSON)
- `/mnt/user-data/outputs/PromptB_output_20260423_134635.response.json` (response-size 버전, 있으면)

### 6-B. 예상 분포
- drafted: 30~38건 (paywall 일부 draft_blocked 예상)
- draft_blocked: 2~10건 (paywall 원문 확보 실패 시)

### 6-C. B.6 Output Contract 구조
```json
{
  "stage": "PromptB",
  "version": "v2_final_input",
  "summary": {"input_passed_specs": 40, "drafted": N, "blocked": M},
  "write_ledger": [{"spec_id", "source_story_ids", "draft_status", "reason"}],
  "drafts": [{
    "spec_id", "source_story_ids", "draft_status": "drafted",
    "web_fetch_status": "ok|partial_fallback|unverified_exception",
    "web_fetch_url_used", "evidence_citations_count",
    "needs_review", "review_reason", "writer_notes",
    "card": { ... full schema ... }
  }],
  "blocked": [{"spec_id", "source_story_ids", "draft_status": "draft_blocked", "reason"}]
}
```

---

## 7. 새 채팅 오프닝 프롬프트 (Claire 복붙용)

```
SBTL_HUB W8 run (run_tag=20260423_134635) Prompt B 수행해줘.

시작 순서:
1. ihyowoen/SBTL_HUB main에서 docs/SESSION_HANDOFF_20260424_W8_promptB.md 를 먼저 읽고
2. 거기 §1에 나온 규칙 문서들(FACT_DISCIPLINE / PROMPT_ABC_DEFAULT_MODE / FUTURE_CARD_STANDARD_FULL_SCHEMA / CARD_ID_STANDARD) 로드
3. /mnt/user-data/outputs/PromptA_output_20260423_134635.json 의 passed_specs 40건을 입력으로
4. public/data/cards.json (baseline) 참조
5. 핸드오프 §2 실행 방식대로 web_fetch 의무 + B.5 schema 카드 작성 + B.6 output
```
