# PROMPT ABC — Default Mode (v5)

## 0. 이 문서의 역할

SBTL_HUB 일일 run의 재사용 prompt 템플릿. Stage A · Stage B · Stage C.

**v4 → v5 핵심 전환:** 2026-04-17 W7R3 run에서 "draft 후 fact_sources 보강" 순서가 hallucinate → rewrite 2중 작업을 유발하는 것이 확인됐다. v5는 **"fetch 후 draft"** 단일 패스로 역전한다.

v5 변경점:
- **Layer 0 URL Pre-fetch** 추가 — Prompt A 직후, Prompt B 전에 fetch
- **카드 등급 자동 결정** — 추출된 fact 수량에 따라 full / brief / discard
- **Framing 검증** Layer 추가 — 원문과 반대 프레이밍(예: 반고체 → "전고체 상용화") 자동 차단
- **기억 블랙리스트** 연계 — 자주 틀리는 주제는 별도 파일에서 차단
- **run 주기 명시** — 최소 1일 1회 (주간 묶음 금지)

이 문서는 다음과 같이 읽는다:
- **최상위 철칙:** `docs/FACT_DISCIPLINE.md` — 정확성 절대 기준 (충돌 시 이 문서보다 우선)
- `docs/FUTURE_CARD_STANDARD_FULL_SCHEMA.md` — 스키마·Region 판례·Category taxonomy·fact_sources·related 필드
- `docs/CARD_ID_STANDARD.md` — `YYYY-MM-DD_REGION_NN` 포맷
- `docs/TRIAGE_INPUT_MODE_DEFAULT.md` — 입력 모드
- `docs/archive/PROMPT_ABC_DEFAULT_MODE_v4.md` — 이전 버전 (참조 금지, 백업 전용)

---

## 1. Operating Declaration

Operating Mode: **triage_output + rescue + dropped default mode**

- `triage_output` = primary working input
- `rescue` = rescue-only auxiliary input
- `dropped` = treasure-hunt / salvage pool
- `kept_clusters[]` from `triage_output` = primary candidate unit
- cards baseline = GitHub `main` `public/data/cards.json`
- **run 주기 = 최소 1일 1회** (주간 묶음은 배터리 인텔리전스 속보성에 부적합)
- helper payloads = working artifacts, not baseline
- **Layer 0 URL pre-fetch는 카드 생성 전제 조건** — fetch 실패 시 카드화 불가
- **fact 필드는 fetch 결과에서 추출된 정보만 사용** — 기억·추론·상식 0건
- Prompt B는 **추출 가능한 fact 수량**에 따라 카드 등급을 자동 결정
- final production schema = full schema only (see `FUTURE_CARD_STANDARD_FULL_SCHEMA.md`)
- **`fact_sources` 없는 카드는 payload 포함 불가**

---

## 2. Region Label Rule

`docs/FUTURE_CARD_STANDARD_FULL_SCHEMA.md` §2 + 엣지케이스 판례 A~E를 따른다.

---

## 3. Baseline Audit Protocol — Enhanced Red-team Deep-dive

**핵심 원칙:** baseline은 **인덱싱만** 하고 **본문 재출력 금지**.

### Layer 1 — URL 일치
- 신규 cluster URL ∩ baseline URL 집합 → 자동 `duplicate_of_existing_main_card`

### Layer 2 — Entity overlap
- 3+ 공유 → dup 후보
- 2 공유 + 같은 cat + ±3일 → follow-up
- 2 공유 + 다른 cat → related 후보

### Layer 3 — 서사 축 검사 (일일 run 전제 하에 강화)
1. 반복 / 진전 / 반전 판정
2. baseline X장으로 같은 결론 가능한가 → 가능하면 reinforcement
3. 3개월 뒤에도 유의미한가
4. supersedes 후보인가
5. **일일 run 특성상 같은 서사 축이 여러 날 연속 등장하는 경우, 신규 카드 생성 기준을 엄격히 적용** (단순 업데이트는 reinforcement, 구조적 진전만 신규)

### Layer 4 — 후속성 체인 (양방향)
- 신규 → 기존: `related`
- 기존 → 신규: `related_inverse_report.json` 기록. baseline 직접 수정 금지

### Layer 5 — 편집 red-team
1. Source Tier 판정 → Tier 3 단독 `_needs_review=true` 또는 discard
2. 익명·초기 단계 → `_needs_review=true`
3. Signal Rubric 적용
4. Framing 체크 (§7.2 §2 참조 — 원문과 반대 프레이밍 차단)
5. 숫자 앵커 존재 (정성적 예외)

### Layer 6 — Zero-omission 증적
- 모든 `kept_cluster`: `passed | existing_reinforcement | discard` + reason
- 모든 `dropped`: STRONG+DROP 전수 검사

---

## 4. Prompt A — Card Spec Builder

v4 동일. 각 passed_spec의 `primary_url` 필드는 Layer 0 fetch 대상이 되므로 **fetchable URL**만 허용 (paywall·login·404는 대체 URL로 교체하거나 spec 단계에서 discard).

Output: `W7Rx_prompt_a_output.json`, `W7Rx_prompt_a_audit.json`

---

## 5. Shared Rubrics — Signal & Source

§5.1 Signal Rubric (3축 A·B·C), §5.2 Source Priority Tier Map. v4 동일.

---

## 6. Layer 0 — URL Pre-fetch (v5 신규)

**Prompt A 완료 후, Prompt B 시작 전에 모든 passed_spec에 대해 일괄 fetch 수행.**

### 6.1 목적
fact 작성 전에 원문 확보. fetch 실패 spec은 카드 생성 대상에서 제외하고 Prompt B는 fetch 성공 spec만 처리.

### 6.2 절차
1. 각 passed_spec의 `primary_url` web_fetch 시도
2. 실패 시(404·paywall·JS-only·timeout): 같은 이벤트의 대체 URL 검색 (web_search로 해당 이벤트 fetchable 매체 찾기)
3. 복수 매체 merged spec: 대표 URL + 검증용 보조 1개 최소 fetch
4. **모두 실패**: 해당 spec은 `unverified_specs.json`에 기록, **카드 생성 시도 안 함**
5. 성공 spec: fetch 본문을 `W7Rx_fetched_corpus.json`에 보존 (Prompt B 입력)

### 6.3 추출 규칙
각 성공 fetch에서 다음 4종만 추출 — 그 외 정보는 카드화 근거 금지:
- **숫자·수량** (금액·용량·일자·비율 등)
- **고유명사** (기업·인물·제품·법안·프로젝트)
- **직접 인용** (회장·장관·CEO 발언을 원문 그대로)
- **명시적 비교·맥락** (원문이 직접 서술한 비교만, 추론 금지)

### 6.4 Output
- `W7Rx_fetched_corpus.json` — spec별 fetch 결과 및 추출된 4종 목록
- `W7Rx_unverified_specs.json` — fetch 실패 spec 목록 + 사유 + 대체 URL 제안

---

## 7. Prompt B — Insight Writer (v5 재구성)

### Mission
Layer 0에서 성공 fetch된 spec만 대상으로 full-schema 카드 생성. **fact 필드는 추출된 정보만 사용**. 등급은 자동 결정.

### 7.1 카드 등급 자동 결정 (v5 신규)

Layer 0에서 추출된 fact 건수에 따라:

| 추출된 fact 건수 | 카드 등급 | 처리 |
|---|---|---|
| ≥ 5건 (숫자·고유명사·인용 합산) | **full** | §7.3 full 템플릿 |
| 2~4건 | **brief** | §7.4 brief 템플릿 |
| ≤ 1건 | **discard** | `insufficient_facts.json` 기록 |

이 규칙은 기계적으로 적용. "맥락상 중요하니까 full로" 같은 예외 금지.

### 7.2 필드 작성 규칙

#### fact 필드
- "X에 따르면" attribution 필수
- 추출된 숫자·고유명사·인용만 사용
- **원문에 없는 비교·해석·업계 진단·전망 금지**
- 환산 수치는 원문 환산 또는 환율 기준 명시

#### title / gate 필드 (editor 영역)
추론·관점·맥락은 여기에 허용된다. **단** 다음 제약:
1. **Framing은 원문이 제시한 프레임과 일치해야 한다** — 원문이 "반고체 양산"이라 하면 카드 title도 반고체. "전고체 상용화 1기" 같은 역방향 프레임 금지. (W7R3 CN_05 사례 참조)
2. **"X가 아니라 Y다" 템플릿 금지** — AI 문체로 판정됨, user memory #3
3. **"~의 진짜 의미는", "이 카드의 핵심은" 같은 연역적 오프닝도 최대한 지양** — 자연 문체 선호

#### implication 필드
- ≥ 2개 항목 (full) / ≥ 1개 (brief), 각 ≥ 20자
- **단정형 금지**, 관찰형만 ("X할 여지", "X가 관찰 포인트")
- implication에 수치·고유명사 등장 시 fact_sources 연결 필수 (implication은 fact 확장, 새 fact 생성 불가)
- **기억 블랙리스트 참조** — `docs/FORBIDDEN_MEMORY_CLAIMS.md` (예정) 에 등재된 주제(예: 삼성SDI 전고체 2027, K-3사 로드맵 구체 연도)는 fetch 근거 없이 사용 금지

### 7.3 Full 카드 템플릿
```
title / sub / gate
fact (≤400자, attribution 포함)
implication (≥2 항목)
urls[], related[]
fact_sources[] — fact·implication 모든 숫자·고유명사·인용 1:1 매핑
```

### 7.4 Brief 카드 템플릿
```
title / sub (sub는 1줄)
gate (선택, ≤2문장)
fact (50~120자)
implication (1 항목)
urls[], related[]
fact_sources[] — 필수
```

### 7.5 Framing 자가 검증 (작성 직후)
작성 후 Prompt B가 스스로 확인:
- fact 서술이 원문과 같은 방향인가?
- title이 fact를 압축한 것인가, 아니면 추론을 덧붙인 것인가?
- implication이 fact에서 파생된 것인가, 새 fact를 만든 것인가?

어느 하나라도 불확실 → `_needs_review=true` 플래그.

### 7.6 본문 텍스트 위생
1. 다른 카드 ID 하드코딩 금지 — `related` 배열로만
2. signal 소문자, date `YYYY-MM-DD`, `cat` ∈ taxonomy
3. 이벤트일 vs news 발행일 구분 — **카드의 `date`는 이벤트일 기준** (예: 서명일 ≠ 보도일)

### 7.7 Output
- `W7Rx_prompt_b_output.json` — draft 카드 N장 (fact_sources 포함, 등급 표시)
- `W7Rx_insufficient_facts.json` — fact ≤1건으로 discard된 spec 목록

---

## 8. Prompt C — Red-team Reviewer

### Mission
Prompt B draft 전수에 대해 fact·framing·서사축 red-team. 통과한 것만 payload에 확정.

### 8.1 금지
- silent discard (제거 시 사유 명시 필수)
- signal·region·date·category 임의 변경
- 본문 대량 rewrite (명백한 사실 오류만 수정, 스타일 변경 금지)

### 8.2 적용 절차

1. **스키마 컴플라이언스 자동 검사**

2. **Fact Discipline 검증** (`docs/FACT_DISCIPLINE.md` 전수 적용)
   - 모든 `fact_sources` 항목의 `source_url`이 `urls`에 존재
   - 모든 `source_quote`가 30자 내외 직접 인용
   - fact·implication의 모든 숫자·고유명사·인용·날짜가 `source_quote`에서 검색됨
   - fact에 "업계·시장·분석가·전문가" 모호 주체 없음
   - 환산 수치에 환율 기준 명시
   - **한 줄이라도 fail → 명시 제거** (rejected_cards 기록)

3. **Framing 검증** (v5 신규)
   - 원문 프레임 ↔ 카드 프레임 일치 검사
   - W7R3 3대 위반 유형 자동 스캔:
     - 반대 방향 프레임 (예: 반고체 → 전고체)
     - "X가 아니라 Y다" 템플릿
     - 기억 블랙리스트 claim (삼성SDI 2027 등)

4. **Layer 3 서사축 검사** — 일일 run 특성상 엄격 적용

5. **Layer 5 편집 red-team**

6. **본문 하드링크 ID 잔여 제거**

7. **related 필드 최종 확정**

### 8.3 Output
- `W7Rx_payload.json` — 최종 카드 N장 (fact_sources + related + `_needs_review`)
- `W7Rx_redteam_report.md` — Layer 3·5·Fact·Framing 검증 로그
- `W7Rx_rejected_cards.json` — fail 카드 + 제거 사유

---

## 9. 산출물 표준

| 파일 | 역할 | baseline 본문 포함? |
|---|---|---|
| `W7Rx_payload.json` | 최종 카드 (fact_sources 포함) | ❌ |
| `W7Rx_prompt_a_output.json` | spec 단계 | ❌ |
| `W7Rx_prompt_a_audit.json` | cluster zero-omission | ❌ |
| `W7Rx_fetched_corpus.json` | Layer 0 fetch 결과 (v5) | ❌ |
| `W7Rx_unverified_specs.json` | fetch 실패 spec (v5) | ❌ |
| `W7Rx_prompt_b_output.json` | draft 스냅샷 | ❌ |
| `W7Rx_insufficient_facts.json` | fact ≤1 discard (v5) | ❌ |
| `baseline_match_audit.json` | Layer 1-2 매칭 | ❌ |
| `related_inverse_report.json` | 역참조 제안 | ❌ |
| `W7Rx_redteam_report.md` | Layer 3·5·Fact·Framing 로그 | ❌ |
| `W7Rx_rejected_cards.json` | 검증 fail 카드 | ❌ |

---

## 10. Never / Always 체크리스트

### NEVER
- baseline 본문 재출력
- 파이프라인 단계 표식을 production ID에 포함
- 본문에 다른 카드 ID 하드코딩
- 단독 소스(Tier 3) 또는 익명 보도를 `top`으로
- 매체 국적으로 region 배정
- `cat`을 taxonomy 밖 값으로
- **기억·추론·상식으로 fact 필드 메우기**
- **Layer 0 fetch 실패 spec으로 카드 생성**
- **`fact_sources` 없는 카드를 payload에 포함**
- **원문 프레임과 반대 방향으로 title·gate 작성** (v5)
- **"X가 아니라 Y다" 템플릿 사용** (v5)
- **기억 블랙리스트 주제를 fetch 근거 없이 사용** (v5)
- kept_cluster silent loss
- cards.json 통합본 발행
- 이벤트일과 news 발행일 혼동 (카드 `date`는 이벤트일)

### ALWAYS
- 모든 kept_cluster에 disposition 기록
- Layer 0 URL pre-fetch를 Prompt B 전에 수행 (v5)
- Prompt B는 fetch 성공 spec만 처리 (v5)
- 카드 등급은 추출된 fact 수량으로 자동 결정 (v5)
- fact·implication 내 숫자·인용·고유명사·일자는 `fact_sources`에 1:1 대응
- 환산 수치는 환율 원문 또는 기준 날짜 명시
- Signal Rubric 3축 점수 기록
- Source Tier 기록
- `_needs_review` 자동 플래그
- `related` 필드 채움
- signal 소문자, ID = `YYYY-MM-DD_REGION_NN`
- `cat` ∈ taxonomy
- Region 판례 A-E
- fact에 "~에 따르면" attribution
- Framing 검증 (원문 프레임과 같은 방향) (v5)

---

## 11. 최종 원칙

**A 단계는 선별·분류, Layer 0은 원문 확보, B 단계는 추출된 fact로만 작성, C 단계는 인용·프레임 이중 검증.**

**Baseline은 인덱싱만, 인용은 원문만, 프레임은 원문 방향만.**

**정확성은 taste가 아니라 방화벽이다. Framing도 fact 검증의 일부다.**
