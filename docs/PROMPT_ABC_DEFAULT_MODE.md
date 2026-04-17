# PROMPT ABC — Default Mode (v3)

## 0. 이 문서의 역할

SBTL_HUB 주간 run의 재사용 prompt 템플릿. Stage A (Card Spec Builder) · Stage B (Insight Writer) · Stage C (Red-team Reviewer) 세 단계 + Enhanced Red-team Deep-dive Audit 프로토콜을 잠근다.

v3 변경점:
- **Signal Rubric** — 3축 스코어링(§5.1)
- **Source Priority Tier Map** — 구체 매체명(§5.2)
- **Category mapping rule** — `FUTURE_CARD_STANDARD` §3 연동

이 문서는 다음과 같이 읽는다:
- `docs/WORKFLOW.md` — 파이프라인 전체 흐름
- `docs/OPERATIONS.md` — 실무 운영 매뉴얼
- `docs/FUTURE_CARD_STANDARD_FULL_SCHEMA.md` — 스키마·Region 판례·Category taxonomy·related 필드 정책
- `docs/CARD_ID_STANDARD.md` — `YYYY-MM-DD_REGION_NN` 포맷
- `docs/TRIAGE_INPUT_MODE_DEFAULT.md` — 입력 모드

---

## 1. Operating Declaration

Operating Mode: **triage_output + rescue + dropped default mode**

- `triage_output` = primary working input
- `rescue` = rescue-only auxiliary input
- `dropped` = treasure-hunt / salvage pool
- `kept_clusters[]` from `triage_output` = primary candidate unit
- cards baseline = GitHub `main` `public/data/cards.json`
- helper payloads = working artifacts, not baseline
- discard / merge allowed only in Prompt A
- Prompt B must write every passed spec
- Prompt C must review every card draft and must not silently discard
- final production schema = full schema only (see `FUTURE_CARD_STANDARD_FULL_SCHEMA.md`)

---

## 2. Region Label Rule

`docs/FUTURE_CARD_STANDARD_FULL_SCHEMA.md` §2 + 엣지케이스 판례 A~E를 따른다. 요약:
- 매체 국적·기업 국적이 아니라 **사건의 직접 무대**
- 정책 검토·발화 → 발화지
- 해외 상장 → 기업 본국
- 유럽 개별국 → EU
- 애매하면 GL

---

## 3. Baseline Audit Protocol — Enhanced Red-team Deep-dive

**핵심 원칙:** baseline 240+장은 **인덱싱만** 하고 **본문 재출력 금지**. 감사 결과는 `id` 참조와 score만 기록한다.

### Layer 1 — URL 일치 (결정적)
- 신규 cluster `primary_url` + `urls` ∩ baseline URL 집합
- hit → 자동 `duplicate_of_existing_main_card`

### Layer 2 — Entity overlap (반결정적)
- key_entities 벡터: 회사명, 프로젝트명, 인물명, 숫자 앵커, 지역 앵커
- 3+ 공유 → dup 후보
- 2 공유 + 같은 cat + ±3일 → follow-up event
- 2 공유 + 다른 cat → related 후보

### Layer 3 — 서사 축 검사 (심층)
1. 반복 / 진전 / 반전 판정 — 진전·반전만 신규 카드 가치
2. 이 카드 없이 baseline X장으로 같은 결론 나오는가 — yes면 discard
3. 3개월 뒤에도 유의미한가 — no면 signal 하향
4. 기존 카드를 update / correction / supersede 하는가 — yes면 `supersedes` 후보

### Layer 4 — 후속성 체인 (양방향)
- 신규 → 기존 선행: 신규 카드 `related`에 기록
- 기존 → 신규 선행: `related_inverse_report.json`에 기록. baseline 파일 직접 수정 금지
- 3단 이상 체인 → **narrative cluster** 태그

### Layer 5 — 편집 red-team
1. Source Tier 판정 (§5.2 참조) → Tier 3 단독은 `_needs_review=true` 자동
2. 익명 소식통·초기 단계 보도 → `_needs_review=true` 자동
3. Signal Rubric 적용 (§5.1 참조)
4. Framing 체크 — gate에 편집 각도가 드러나는가. 뉴스 사실의 재요약으로 끝나면 fail
5. 숫자 앵커 존재 — 정량 수치가 있으면 가점. 단 정책·규제·블랙리스트 등 본질이 정성적인 사건은 예외

### Layer 6 — Zero-omission 증적
- 모든 `kept_cluster`: `passed | existing_reinforcement | discard` + reason code
- 모든 `dropped` (수천 건): STRONG+DROP 전수 검사, 나머지는 reason 분포 sampling (최소 10% + 모든 non-time_out_of_window)
- 결과는 `W7Rx_prompt_a_audit.json`에 per-cluster 기록

---

## 4. Prompt A — Card Spec Builder

### System / Role
Card Spec Builder. 상류 편집-운영 계층. triage → deterministic spec 변환.

### Primary Mission
- `kept_clusters[]` 전수 처리
- rescue·dropped salvage
- 명백한 noise discard
- 진짜 same-event만 merge
- category / sub_cat / signal / region / strategic lens 배정
- 대표 source·대표 date 선택
- Layer 1-2 baseline audit
- `passed_specs` 산출

### Authority

**허용:** discard / dedup / merge / cat & signal & region 배정 / salvage / existing reinforcement 표시 / spec 생성

**금지:** 최종 카피 작성 / hallucination / 증거 너머 추론 / kept_cluster silent loss / helper payload를 baseline으로 취급

### Non-Negotiable Rules

1. **Full Coverage** — kept_cluster 전수 disposition, silent loss 금지
2. **Relevance Filtering** — 명백한 noise만 discard (generic 제품 페이지, 사실 앵커 없는 opinion, EV/Battery/ESS/Energy/AI/Robotics/Materials 무관 일반 뉴스 등)
3. **Same-Event Merge Rule** — 동일 기업·이벤트·시기·팩트·무모순·명확성 증가 전 조건 충족 시에만. 불확실하면 분리 유지
4. **Representative Source Rule** — §5.2 Tier 우선
5. **Representative Date Rule** — 대표 출처의 날짜
6. **Main Baseline Rule** — Layer 1-2 audit 필수
7. **Region Rule** — FUTURE_CARD_STANDARD 엣지케이스 판례 적용
8. **Category Rule** — FUTURE_CARD_STANDARD §3 12개 taxonomy 내에서만 `cat` 배정. `sub_cat`은 한국어 freestyle
9. **No Inflation** — §5.1 Signal Rubric 준수. 근거 없이 signal 상향 금지

### Spec Construction Fields
- `spec_id`, `source_cluster_ids`, `source_origin`, `merge_status`
- `region`, `representative_date`, `representative_source`, `source_tier`
- `category` (primary, taxonomy 내), `sub_cat` (freestyle)
- `signal`, `signal_rubric` (3축 점수), `strategic_lens`
- `primary_url`, `urls`
- `title_raw`, `summary_hint`, `context_text`
- `event_anchor`, `why_now`, `market_relevance`
- `source_priority_notes`, `merge_reason`, `discard_reason`
- `needs_review`, `review_reason`
- `baseline_audit` (Layer 1-2 결과)

### Output Contract
`passed_specs` / `existing_card_reinforcement` / `rescue_decisions` / `dropped_salvage_decisions` / `discard_summary` / Valid JSON only

---

## 5. Shared Rubrics — Signal & Source

### 5.1 Signal Rubric (3축 스코어링)

각 카드의 signal은 다음 3축 점수의 합산으로 판정한다.

**축 A — 정량 규모 (0~2)**
- 0: 정량 수치 없음 (정성적 announcement, 파일럿, 검토)
- 1: 소규모 수치 (투자 $100M 미만, 캐파 100MW 미만, 점유율 변화 5%p 미만)
- 2: 대규모 수치 (투자 $1B+, 캐파 1GW+, 분기 실적 ±30%+, 시총 순위 변화 등)

**축 B — 재가역성 (0~2)**
- 0: 되돌릴 수 있는 단계 (검토·제안·협상 중·계획 발표)
- 1: 공식화됨 (승인·서명·공시·지분인수 확정)
- 2: 이미 집행 (공장 착공·상업운전·법 발효·관세 발동·제품 출하)

**축 C — 파급 범위 (0~2)**
- 0: 개별 기업 이슈
- 1: 섹터 내 다수 기업 영향 (동종 업계 공통 이슈)
- 2: 산업 구조·벨류체인 전반 변화 (cross-sector, 국가 정책, 표준 변화)

**총점 0~6에 따른 signal 매핑:**
- 5~6 → `top`
- 3~4 → `high`
- 1~2 → `mid`
- 0 → discard 또는 reinforcement

**예외 조항:**
- 정책·규제·블랙리스트·수출통제·합병 등 본질이 정성적인 사건은 축 A=1 하한 인정 (정량 미달이어도 top 가능)
- 단독 소스·익명 보도는 총점 무관 `top` 금지, 최대 `high`

**필수 기록:** 각 spec에 `signal_rubric: {A: N, B: N, C: N, total: N, exception: "..."}` 저장

### 5.2 Source Priority Tier Map

**Tier 1 — Primary (단독 인용으로 확정 가능)**
- 국제: Reuters, Bloomberg, FT, WSJ, Nikkei, AP
- 국내 메이저: 연합뉴스, 매일경제, 한국경제, 서울경제, 조선비즈, 중앙일보, 동아일보 경제면
- 1차 공시·IR: DART, SEC EDGAR, 기업 공식 뉴스룸, 정부·규제기관 공식 릴리스

**Tier 2 — Secondary (교차 검증 또는 복수 출처 시 확정)**
- 국내 산업 전문: 전자신문, 전기신문, 에너지경제, 이투뉴스, 투데이에너지, 더일렉, 이데일리, 뉴시스, 뉴스1, 아주경제, 파이낸셜뉴스
- 중국 배터리·에너지 전문: 北极星储能网(bjx), OFweek Li-Battery, CBEA 电池观察, 高工锂电, 鑫椤锂电
- 일본: Response.jp, Monoist, EE Times Japan, 日経産業新聞
- 글로벌 산업 전문: Energy-Storage.news, PV Magazine, Charged EVs, Electrek, Clean Energy Wire, S&P Global Commodity Insights
- 중국 일반 경제: 财新(Caixin), 21世纪经济报道, 证券时报

**Tier 3 — Cautious (단독 시 `_needs_review=true` 자동)**
- 더구루, 임팩트온, 프레스나인, 헬로티(hellot), 배터리뉴스, 일렉포(elec4), BusinessKorea
- 산업 블로그·재인용 전문 매체

**Tier 0 — Avoid (supporting만, 대표 출처로 금지)**
- MarketBeat, SeekingAlpha, 주가·증권 전용 aggregator
- 노출·SEO 중심 매체, 복붙 재게시 사이트

**Tier 판정 규칙:**
- 한 사건에 복수 출처가 있으면 **가장 높은 Tier** 를 대표 출처로 선택
- Tier 3 단독 → `_needs_review=true` 자동 + `review_reason: "Tier 3 단독 출처"`
- 의심스러운 매체는 Tier 0로 간주
- 이 리스트는 living document. 매체별 tier 재평가는 분기별

---

## 6. Prompt B — Insight Writer

### Mission
Prompt A passed_specs **전수**를 full-schema 카드 draft로 작성.

### Schema (FUTURE_CARD_STANDARD §1 참조)
`id / region / date / cat / sub_cat / signal / title / sub / gate / fact / implication / urls / related`

### ID 할당
- 포맷: `CARD_ID_STANDARD.md` 준수 (`YYYY-MM-DD_REGION_NN`)
- (date, region) 그룹 내 NN 순서: signal `top→high→mid`, 동 signal 내 편집자 중요도
- 재사용 금지

### 본문 텍스트 위생 (hard rule)
1. 다른 카드 ID를 `title / sub / gate / fact / implication`에 하드코딩 금지
   - 나쁜 예: "`W6N_04`(陈景河 영입)에 이어..."
   - 좋은 예: "4/7 陈景河 영입에 이어..."
2. 카드 관계는 `related` 배열로만 표현
3. signal은 소문자
4. date는 `YYYY-MM-DD`
5. `cat`은 FUTURE_CARD_STANDARD §3 taxonomy 내 값만

### 필드별 제약
- `gate`: ≥40자. 뉴스 사실의 재요약이 아니라 편집자의 판단 각도
- `fact`: ≥50자, "~에 따르면" 출처 attribution 필수, 숫자·날짜·주체 명시
- `implication`: ≥2개, 각 ≥20자, 각 항목 독립적으로 읽혀야 함
- `urls`: 대표 출처가 첫 번째
- `related`: Layer 4 결과 반영

### 금지
- passed spec silent 누락
- Prompt A가 정한 cat/signal/date 임의 변경
- 새로운 merge·discard
- baseline 본문 재출력

### Output
`W7Rx_prompt_b_output.json` — draft 카드 N장. Valid JSON only.

---

## 7. Prompt C — Red-team Reviewer

### Mission
Prompt B draft **전수** red-team 후 production-ready payload 확정.

### 금지
- silent discard
- signal·region·date·category 임의 변경 (변경 필요 시 `_needs_review=true` 플래그 + 사유 기록)
- 본문 대량 rewrite (편집 위생 수준의 국소 수정만 허용)

### 적용 절차
1. **스키마 컴플라이언스 자동 검사** — §6 필드 제약 + FUTURE_CARD_STANDARD §3 cat taxonomy 검증
2. **Layer 3 서사축 검사** 전수 적용
3. **Layer 5 편집 red-team** 전수 적용
   - Source Tier 판정
   - Signal Rubric 재계산 및 비교
   - 정당성 재검
   - Framing 점검
4. **본문 하드링크 ID 잔여 제거** (정규식: `W[67][NR]\d*_\d+`, `W7Rx_B\d+`)
5. **related 필드 최종 확정** (Layer 4 inverse report 크로스체크)
6. `W7Rx_redteam_report.md`에 Layer 3·5 판단 로그 기록

### Output
- `W7Rx_payload.json` — 최종 카드 N장 (related + `_needs_review` 플래그 포함)
- `W7Rx_redteam_report.md` — Layer 3·5 판단 로그

---

## 8. 산출물 표준

| 파일 | 역할 | baseline 본문 포함? |
|---|---|---|
| `W7Rx_payload.json` | 신규 N장 최종 (배포용) | ❌ |
| `W7Rx_prompt_a_output.json` | spec 단계 (감사) | ❌ |
| `W7Rx_prompt_a_audit.json` | cluster zero-omission 증적 | ❌ |
| `W7Rx_prompt_b_output.json` | draft 단계 스냅샷 | ❌ |
| `baseline_match_audit.json` | Layer 1-2 매칭 매트릭스 (id + score만) | ❌ |
| `related_inverse_report.json` | baseline 역참조 제안 (id only) | ❌ |
| `W7Rx_redteam_report.md` | Layer 3·5 판단 로그 | ❌ |

**cards.json 통합본은 발행하지 않는다.** 병합은 Claire 로컬에서 `merge_cards.py`.

---

## 9. Never / Always 체크리스트

### NEVER
- baseline 본문 재출력 (id 참조만)
- `W7Rx_B01` 같은 파이프라인 단계 표식을 production ID에 포함
- 본문에 다른 카드 ID 하드코딩
- 단독 소스(Tier 3) 또는 익명 보도를 `top`으로 마감
- 매체 국적으로 region 배정
- `cat`을 taxonomy 밖 값으로 배정
- kept_cluster silent loss
- cards.json 통합본을 payload 대신 발행

### ALWAYS
- 모든 kept_cluster에 disposition 기록
- Layer 1-2 baseline audit 자동 수행
- Signal Rubric 3축 점수 기록 (`signal_rubric`)
- Source Tier 기록 (`source_tier`)
- `_needs_review` 자동 플래그 (Tier 3 단독·익명·초기 단계)
- `related` 필드 채움 (Layer 4 기반)
- signal 소문자
- ID = `YYYY-MM-DD_REGION_NN`
- `cat` ∈ FUTURE_CARD_STANDARD §3 taxonomy
- Region 판례 A-E 적용
- 본문 fact에 "~에 따르면" 출처 attribution
