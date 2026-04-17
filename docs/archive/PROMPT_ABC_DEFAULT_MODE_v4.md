# PROMPT ABC — Default Mode (v4)

> **⚠️ ARCHIVED 2026-04-17**
> 이 문서는 v5로 대체되었다. 현재 운용 버전: `docs/PROMPT_ABC_DEFAULT_MODE.md`
> 백업 목적으로만 보존. 참조 금지.

## 0. 이 문서의 역할

SBTL_HUB 주간 run의 재사용 prompt 템플릿. Stage A · Stage B · Stage C + Enhanced Red-team Deep-dive Audit + Fact Discipline Verification.

v4 변경점 (정확성 사고 대응):
- **Prompt B에 web_fetch 의무화** — fact 작성 전 원문 fetch
- **fact_sources 필드 의무화** — 모든 숫자·인용의 원문 트레이스 필수
- **Prompt C에 fact verification 레이어 추가** — 출처 미검증 카드 배제

이 문서는 다음과 같이 읽는다:
- **최상위 철칙:** `docs/FACT_DISCIPLINE.md` — 정확성 절대 기준 (충돌 시 이 문서보다 우선)
- `docs/WORKFLOW.md` — 파이프라인 전체 흐름
- `docs/OPERATIONS.md` — 실무 운영 매뉴얼
- `docs/FUTURE_CARD_STANDARD_FULL_SCHEMA.md` — 스키마·Region 판례·Category taxonomy·fact_sources·related 필드
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
- Prompt B must write every passed spec **with web_fetch-verified fact**
- Prompt C must review every card draft, must not silently discard, **and must verify fact_sources**
- final production schema = full schema only (see `FUTURE_CARD_STANDARD_FULL_SCHEMA.md`)
- **`fact_sources` 없는 카드는 payload 포함 불가**

---

## 2. Region Label Rule

`docs/FUTURE_CARD_STANDARD_FULL_SCHEMA.md` §2 + 엣지케이스 판례 A~E를 따른다.

---

## 3. Baseline Audit Protocol — Enhanced Red-team Deep-dive

**핵심 원칙:** baseline 240+장은 **인덱싱만** 하고 **본문 재출력 금지**.

### Layer 1 — URL 일치
- 신규 cluster URL ∩ baseline URL 집합 → 자동 `duplicate_of_existing_main_card`

### Layer 2 — Entity overlap
- 3+ 공유 → dup 후보
- 2 공유 + 같은 cat + ±3일 → follow-up
- 2 공유 + 다른 cat → related 후보

### Layer 3 — 서사 축 검사
1. 반복 / 진전 / 반전 판정
2. baseline X장으로 같은 결론 가능한가
3. 3개월 뒤에도 유의미한가
4. supersedes 후보인가

### Layer 4 — 후속성 체인 (양방향)
- 신규 → 기존: `related`
- 기존 → 신규: `related_inverse_report.json` 기록. baseline 직접 수정 금지

### Layer 5 — 편집 red-team
1. Source Tier 판정 → Tier 3 단독 `_needs_review=true`
2. 익명·초기 단계 → `_needs_review=true`
3. Signal Rubric 적용
4. Framing 체크
5. 숫자 앵커 존재 (정성적 예외)

### Layer 6 — Zero-omission 증적
- 모든 `kept_cluster`: `passed | existing_reinforcement | discard` + reason
- 모든 `dropped`: STRONG+DROP 전수 검사

---

## 4. Prompt A — Card Spec Builder

동일 (v3). 단, 각 passed_spec의 `primary_url` 필드는 Stage B에서 fetch 대상이 되므로 **fetchable URL**만 허용 (paywall, login-required, 404 발견 시 대체 URL 검색).

---

## 5. Shared Rubrics — Signal & Source (동일 v3)

§5.1 Signal Rubric (3축), §5.2 Source Priority Tier Map.

---

## 6. Prompt B — Insight Writer (v4 강화)

### Mission
Prompt A passed_specs **전수**를 full-schema 카드 draft로 작성. **모든 fact는 web_fetch 결과에만 근거.**

### 6.1 작성 절차 (strict sequence)

1. **각 spec에 대해 `primary_url` web_fetch 수행**
   - 실패 시: 동일 이벤트의 다른 URL (다른 매체) fetch 시도
   - 복수 매체 merged spec이면 **대표 URL + 검증용 보조 URL 최소 1개** fetch
   - 모두 실패 → 카드 생성 중단, `unverified_specs` 리스트에 기록

2. **fetch 결과에서 정보 추출**
   - 숫자 (금액·용량·일자·비율)
   - 고유명사 (기업·인물·프로젝트·상세명)
   - 직접 인용
   - 원문이 명시한 비교·맥락

3. **`fact_sources` 구축**
   - 각 `claim` (숫자 단위, 인용 단위)에 대해:
     - `source_url` (fetch한 URL)
     - `source_quote` (원문에서 복사한 30자 내외 직접 인용)
     - `fetched_at` (ISO 8601)
   - 원칙: **fact에 들어갈 모든 숫자·고유명사·인용은 반드시 `fact_sources` 항목 1개 이상에 연결**

4. **fact 필드 작성**
   - §6.2 규칙 준수. 원문에 없는 정보 추가 금지

5. **implication 필드 작성**
   - §6.3 규칙 준수. 단정형 금지, 관찰형만
   - implication에 수치가 등장하면 그 수치도 `fact_sources` 연결

### 6.2 fact 필드 제약

- ≥0자 (고정·인위적 최소 삭제), ≤400자 (가독성)
- "X에 따르면" attribution 필수
- 숫자·날짜·주체 명시 (단, 원문에 있는 것만)
- **원문에 없는 비교·해석·업계 진단·전망 금지**
- 환산 수치는 원문 환산 또는 환율 기준 명시 (`FACT_DISCIPLINE` §5 참조)

### 6.3 implication 필드 제약

- ≥2개 항목, 각 ≥20자
- **단정형 문장 금지** (`FACT_DISCIPLINE` §4.1)
  - 금지: "X가 나온다", "X한다", "X 가능성이 증가"
- **관찰형 어휘 사용** (`FACT_DISCIPLINE` §4.2)
  - 허용: "X할 여지", "X인지 확인 필요", "X가 관찰 포인트"
- implication에 등장하는 세부 수치와 주체가 fact에 있어야 함 (implication은 fact의 문맥 확장, 새 fact 생성 불가)

### 6.4 본문 텍스트 위생 (hard rule)

1. 다른 카드 ID 하드코딩 금지. `related` 배열로만
2. signal 소문자, date `YYYY-MM-DD`, `cat`은 taxonomy 내

### 6.5 금지
- passed spec silent 누락
- fetch 없이 fact 작성 — **이것이 이번 v4 핵심 금지**
- Prompt A가 정한 cat/signal/date 임의 변경
- baseline 본문 재출력

### 6.6 Output
- `W7Rx_prompt_b_output.json` — draft 카드 N장 (fact_sources 포함)
- `W7Rx_unverified_specs.json` — fetch 실패로 카드화 불가했던 spec 목록 (사유 + 대체 URL 제안)

---

## 7. Prompt C — Red-team Reviewer (v4 강화)

### Mission
Prompt B draft **전수** red-team + **fact 검증** 후 production-ready payload 확정.

### 7.1 금지
- silent discard
- signal·region·date·category 임의 변경
- 본문 대량 rewrite

### 7.2 적용 절차

1. **스키마 컴플라이언스 자동 검사**
2. **Fact Discipline 검증** (NEW v4)
   - 모든 `fact_sources` 항목의 `source_url`이 `urls` 배열에 존재
   - 모든 `source_quote`가 30자 이내 직접 인용 형태
   - fact 내 모든 숫자·고유명사·인용·날짜가 `fact_sources`의 `source_quote`에서 검색됨
   - implication 내 모든 수치·고유명사도 `fact_sources` 연결
   - fact에 "업계·시장·분석가·전문가" 모호 주체 없음
   - fact에 환산 수치 있다면 환율 기준 명시
   - **위 항목 한 줄이라도 fail → payload에서 제거 (silent discard 아니라 명시 제거)**
3. **Layer 3 서사축 검사** 전수 적용
4. **Layer 5 편집 red-team** 전수 적용
5. **본문 하드링크 ID 잔여 제거**
6. **related 필드 최종 확정**
7. `W7Rx_redteam_report.md`에 기록 — 제거된 카드의 ID·사유·제거 항목 명시

### 7.3 Output
- `W7Rx_payload.json` — 최종 카드 N장 (fact_sources + related + `_needs_review` 포함)
- `W7Rx_redteam_report.md` — Layer 3·5 + Fact Discipline 검증 로그
- `W7Rx_rejected_cards.json` — Fact Discipline 검증에 fail해서 제외된 카드 목록 (사유가 기예)

---

## 8. 산출물 표준

| 파일 | 역할 | baseline 본문 포함? |
|---|---|---|
| `W7Rx_payload.json` | 신규 N장 최종 (fact_sources 포함) | ❌ |
| `W7Rx_prompt_a_output.json` | spec 단계 | ❌ |
| `W7Rx_prompt_a_audit.json` | cluster zero-omission | ❌ |
| `W7Rx_prompt_b_output.json` | draft 스냅샷 | ❌ |
| `W7Rx_unverified_specs.json` | fetch 실패 spec (NEW v4) | ❌ |
| `baseline_match_audit.json` | Layer 1-2 매칭 | ❌ |
| `related_inverse_report.json` | 역참조 제안 | ❌ |
| `W7Rx_redteam_report.md` | Layer 3·5 + Fact 검증 로그 | ❌ |
| `W7Rx_rejected_cards.json` | Fact 검증 fail 카드 (NEW v4) | ❌ |

---

## 9. Never / Always 체크리스트

### NEVER
- baseline 본문 재출력
- 파이프라인 단계 표식을 production ID에 포함
- 본문에 다른 카드 ID 하드코딩
- 단독 소스(Tier 3) 또는 익명 보도를 `top`으로
- 매체 국적으로 region 배정
- `cat`을 taxonomy 밖 값으로
- **기억·추론·상식으로 fact 필드 메우기** — v4 핵심
- **출처 fetch 없는 숫자·인용·비교 기재** — v4 핵심
- **`fact_sources` 없는 카드를 payload에 포함** — v4 핵심
- kept_cluster silent loss
- cards.json 통합본 발행

### ALWAYS
- 모든 kept_cluster에 disposition 기록
- Layer 1-2 baseline audit 자동 수행
- **Prompt B 시 passed_spec 전수 primary_url web_fetch** — v4 핵심
- **fact·implication 내 숫자·인용·고유명사·일자는 `fact_sources`에 1:1 대응** — v4 핵심
- **환산 수치는 환율 원문 또는 기준 날짜 명시** — v4 핵심
- Signal Rubric 3축 점수 기록
- Source Tier 기록
- `_needs_review` 자동 플래그
- `related` 필드 채움
- signal 소문자, ID = `YYYY-MM-DD_REGION_NN`
- `cat` ∈ taxonomy
- Region 판례 A-E
- fact에 "~에 따르면" attribution

---

## 10. 최종 원칙

**A 단계는 선별·분류, B 단계는 원문 검증 계적 작성, C 단계는 인용 검증·이중 red-team.**
**Baseline은 인덱싱만, 인용은 원문만.**
**정확성은 taste가 아니라 방화벽이다.**
