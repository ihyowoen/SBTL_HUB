# PROMPT ABC — Default Mode (v5)

## 0. 문서의 목적 및 대상 독자

이 문서는 SBTL_HUB 인텔리전스 파이프라인의 **재사용 프롬프트 운용 매뉴얼**이다. 하루에 최소 한 번 실행되는 triage → 카드 생성 → red-team 검증 파이프라인을 구성하는 세 개 Stage(A/B/C)와 그 사이에 삽입된 Pre-fetch Stage를 정의한다.

이 문서 하나만으로 다음이 가능하다:
- 파이프라인에 처음 투입되는 신규 에이전트 또는 실무자가 각 Stage의 입력·절차·출력을 이해하고 바로 실행
- 산출물 파일의 명명 규칙과 역할 파악
- 카드 품질 기준과 자동 판정 규칙 적용
- 실수가 잦은 지점(hallucination·framing 오류·기억 기반 claim)의 사전 차단

이 문서와 충돌하는 상위 문서는 하나뿐이다: `docs/FACT_DISCIPLINE.md`. 팩트 정확성에 관한 규칙은 해당 문서가 최종 판단 기준이며, 이 문서의 어떤 조항보다도 우선한다.

---

## 1. 용어 정의

| 용어 | 정의 |
|---|---|
| **triage** | 외부 뉴스·보도자료 수천 건을 수집·분류해 카드화 대상 cluster로 압축하는 사전 공정. 본 파이프라인은 triage 산출물을 입력으로 받는다. |
| **cluster** | 같은 이벤트를 보도한 여러 매체의 URL·제목·스니펫을 하나로 묶은 단위. triage의 최소 출력 단위. |
| **kept cluster** | triage가 카드화 후보로 선정한 cluster. 본 파이프라인의 1차 입력. |
| **rescue cluster** | triage 초기 단계에서 드롭됐다가 수작업으로 복원된 cluster. 2차 입력. |
| **dropped cluster** | triage가 최종 탈락시킨 cluster. 필요 시 salvage(보물찾기) 대상. |
| **baseline** | GitHub 메인 브랜치 `public/data/cards.json`에 누적된 기존 카드 집합. 이번 run의 신규 카드와 중복·연관 여부를 판정하는 기준. |
| **spec** | Stage A 출력 단위. cluster를 카드화 할 수 있는 형태로 정리한 구조. |
| **passed spec** | Stage A가 카드 생성 대상으로 판정한 spec. |
| **run_id** | 이번 실행의 고유 식별자. 예시 형식: `W7R3` (주차 7, 3번째 run), `20260417_01` (날짜 + 번호). 팀 관례에 따라 정한다. |
| **카드** | 본 파이프라인의 최종 산출물 단위. 스키마는 본 문서 §6 참조. |
| **fact_sources** | 카드 본문의 각 숫자·고유명사·인용에 대해 원문 URL과 30자 내외 직접 인용을 매핑한 배열. 모든 카드에 필수. |
| **related** | 해당 카드와 서사 축을 공유하는 다른 카드의 ID 배열. |

---

## 2. 파이프라인 전체 개요

```
[triage 산출물: kept / rescue / dropped]
              ↓
┌────────────────────────────────────┐
│  Stage A — Card Spec Builder       │
│  cluster를 spec으로 변환            │
│  baseline 중복·유사 판정            │
│  kept cluster 전수를 판정 기록      │
└────────────────────────────────────┘
              ↓
┌────────────────────────────────────┐
│  Pre-fetch Stage                    │
│  passed spec의 대표 URL을 web_fetch │
│  숫자·고유명사·인용·비교 추출        │
│  fetch 실패 spec은 카드화 제외       │
└────────────────────────────────────┘
              ↓
┌────────────────────────────────────┐
│  Stage B — Insight Writer          │
│  추출된 fact만으로 카드 draft 생성  │
│  fact 개수에 따라 등급 자동 결정    │
│  fact_sources 1:1 매핑 구축         │
└────────────────────────────────────┘
              ↓
┌────────────────────────────────────┐
│  Stage C — Red-team Reviewer       │
│  스키마·팩트·프레임 전수 검증       │
│  실패 카드는 명시 제거(silent 금지) │
│  최종 payload 확정                 │
└────────────────────────────────────┘
              ↓
[카드 payload + 감사 로그 + 거절 목록]
```

각 Stage는 독립적으로 실행 가능하며, 모든 Stage는 입력을 전수 처리하고 결정(pass/discard/defer)을 기록한다. 어느 Stage에서도 silent loss는 금지된다.

---

## 3. 파일 명명 규칙

모든 산출물은 `{run_id}` 접두어를 붙여 구분한다. 구체 파일명은 다음 표와 같다. 예시 `run_id`는 `W7R3`이다.

| 파일 패턴 | 예시 파일명 | 생성 Stage |
|---|---|---|
| `{run_id}_prompt_a_output.json` | `W7R3_prompt_a_output.json` | Stage A |
| `{run_id}_prompt_a_audit.json` | `W7R3_prompt_a_audit.json` | Stage A |
| `{run_id}_baseline_match_audit.json` | `W7R3_baseline_match_audit.json` | Stage A |
| `{run_id}_related_inverse_report.json` | `W7R3_related_inverse_report.json` | Stage A |
| `{run_id}_fetched_corpus.json` | `W7R3_fetched_corpus.json` | Pre-fetch |
| `{run_id}_unverified_specs.json` | `W7R3_unverified_specs.json` | Pre-fetch |
| `{run_id}_prompt_b_output.json` | `W7R3_prompt_b_output.json` | Stage B |
| `{run_id}_insufficient_facts.json` | `W7R3_insufficient_facts.json` | Stage B |
| `{run_id}_payload.json` | `W7R3_payload.json` | Stage C |
| `{run_id}_redteam_report.md` | `W7R3_redteam_report.md` | Stage C |
| `{run_id}_rejected_cards.json` | `W7R3_rejected_cards.json` | Stage C |

어떤 산출물에도 baseline 카드의 본문을 재출력하지 않는다. baseline은 인덱스·메타데이터(ID·제목·URL 셋·entity 셋)만 참조 목적으로 사용한다.

---

## 4. 입력 명세

### 4.1 Primary 입력 — triage_output

triage가 생성한 `triage_output_{YYYYMMDD}_{HHMMSS}.json` 파일을 파이프라인의 1차 입력으로 받는다. 최소 포함 필드:
- `kept_clusters[]`: 카드화 후보 cluster 배열
  - 각 cluster는 `cluster_id`, `title`, `snippet`, `urls[]`, `region_hint`, `cat_hint`, `signal_hint`, `date_hint`, `entity_tags[]` 등을 포함
- `dropped_clusters[]`: 탈락 cluster 배열 (STRONG+DROP 플래그 포함)
- `rescue_clusters[]`: 수동 복원 cluster 배열

### 4.2 보조 입력

- `baseline` — GitHub `main` 브랜치의 `public/data/cards.json`. 전수 로드가 아니라 인덱싱 목적으로만 사용 (§11 참조).
- `tier2_entities.json`, `tier2_events.json` — 엔티티·이벤트 사전. triage 설정 파일이지만 Stage A에서 중복 판정 보조에 사용 가능.
- `scope_policy.json` — Tier 1 매체 정의 목록. Source Tier 판정에 사용.

### 4.3 Run 주기

파이프라인은 **최소 1일 1회** 실행한다. 배터리·ESS·EV 산업의 이벤트 발생 빈도와 속보성 요구가 일일 단위이기 때문이다. 주간 묶음 실행은 금지한다. 단, 주말·공휴일에 triage 산출물이 없으면 해당 일자는 실행 생략 가능하며, 다음 실행 시 누적 데이터를 정상 처리한다.

---

## 5. Region 라벨 규칙

카드의 `region` 필드는 다음 값 중 하나를 사용한다: `KR`(한국), `US`(미국), `EU`(유럽 전체), `CN`(중국), `JP`(일본), `GL`(Global·다국가 걸친 이벤트).

판정 기준은 **이벤트의 지리적 주체**이며, 매체 국적이 아니다. 다음 원칙을 순서대로 적용한다.

1. **정책·규제 이벤트**는 해당 정부·입법기관의 관할 region.
   - 예: 미국 Virginia 주지사 서명 → `US`
   - 예: EU 집행위원회 지침 발표 → `EU`
   - 예: 중국 공업정보화부 발표 → `CN`

2. **기업 이벤트**(양산 개시·공장 착공·제품 출시 등)는 해당 시설·활동의 소재 지역.
   - 예: 독일 VW 공장 관련 발표 → `EU`
   - 예: 중국 안후이성 공장 투산 → `CN`
   - 예: 미국 Virginia 공장 신설 → `US`

3. **본사 소재와 활동 소재가 다르면** 활동 소재 우선.
   - 예: 홍콩 본사 Alinta가 호주에서 BESS 공사 → `GL` (호주 이벤트로 분류, 아래 4번 참조)

4. **Global(`GL`) 적용 조건**: 이벤트가 본문 region 5개(`KR·US·EU·CN·JP`) 중 어느 하나에도 단독 귀속되지 않거나, 명시적으로 다국가를 걸치는 경우.
   - 예: 호주·캐나다·남미·인도·동남아 관련 이벤트 → `GL`
   - 예: IEA 글로벌 전망 발표 → `GL`
   - 예: Amazon이 호주 PPA 9건 체결 → `GL`
   - 예: 캐나다 정부가 자국 기업 지원 → `GL`

5. **복수 region이 동시 관련된 이벤트**는 이벤트의 1차 발생지 기준.
   - 예: 미국 Virginia mandate가 PJM 전력망 전체에 영향 → `US` (서명 주체가 Virginia 주)
   - 예: 한국 기업이 EU 공장 수주 → `EU` (활동 소재)

6. **의심 케이스 처리**: 어느 region에도 명확히 귀속되지 않으면 `GL`로 분류하되 `_needs_review=true` 플래그를 추가해 수작업 재검토 대상에 포함시킨다.

region 판정이 이 규칙으로 해결되지 않는 엣지케이스는 `docs/FUTURE_CARD_STANDARD_FULL_SCHEMA.md`의 판례 섹션에서 관리하며, 신규 판례 발생 시 해당 문서를 업데이트한다.

---

## 6. 카드 스키마

모든 카드는 다음 필드를 포함한다.

### 6.1 필수 필드

| 필드 | 타입 | 설명 |
|---|---|---|
| `id` | string | 형식: `YYYY-MM-DD_REGION_NN`. 날짜는 **이벤트 발생일**(뉴스 보도일 아님). NN은 같은 날짜·region 내 2자리 일련번호. |
| `region` | string | §5 참조. 대문자. |
| `date` | string | `YYYY-MM-DD`. 이벤트 발생일. |
| `cat` | string | Category taxonomy 값. 현 taxonomy: `Battery`, `ESS`, `EV`, `Charging`, `Materials`, `Policy`, `PowerGrid`, `Recycling`, `Safety`, `Industry`, `Research`, `Macro` 12종. 소문자·오탈자·변형 금지. |
| `sub_cat` | string | 자유 서술(10자 내외). cat 하위의 세부 주제. 예: "주 ESS 의무화", "반고체 양산". |
| `signal` | string | `top`·`high`·`mid` 중 하나. 소문자 고정. |
| `source_tier` | integer | `1`·`2`·`3` 중 하나. §8 참조. |
| `title` | string | 카드의 메인 헤드라인. |
| `sub` | string | title 아래 보조 헤드라인. 1줄. |
| `gate` | string | 해당 이벤트의 편집적 의미·해석 프레임. editor 영역. |
| `fact` | string | 원문 기반 사실 서술. attribution 포함. ≤ 400자 (full 카드), 50~120자 (brief 카드). |
| `implication` | array of string | 카드의 후속 관찰 포인트. 각 원소 ≥ 20자. full 카드는 ≥ 2개, brief 카드는 ≥ 1개. |
| `urls` | array of string | 이벤트 근거 URL 배열. 첫 번째는 대표 URL. |
| `fact_sources` | array of object | §6.3 참조. 모든 카드에 필수. |
| `related` | array of string | 서사 축을 공유하는 다른 카드의 `id` 배열. 없으면 빈 배열. |

### 6.2 선택 필드

| 필드 | 타입 | 설명 |
|---|---|---|
| `signal_rubric` | object | Signal 판정 근거(§7). 형식: `{A: 0-2, B: 0-2, C: 0-2, total: sum, exception: string\|null}`. |
| `_needs_review` | boolean | 자동 플래그. Source Tier 3 단독·익명·framing 의심·수치 불명확 등의 경우 `true`. |
| `supersedes` | string | 이 카드가 대체하는 이전 카드의 `id`. 서사 반전·정정 시 사용. |

### 6.3 fact_sources 구조

`fact_sources`는 객체 배열이며 각 객체는 다음 필드를 포함한다.

| 필드 | 타입 | 설명 |
|---|---|---|
| `claim` | string | 카드 본문(fact 또는 implication)에 등장한 숫자·고유명사·인용을 15자 내외로 식별 |
| `source_url` | string | 해당 claim의 근거 URL. 반드시 카드의 `urls` 배열에 존재해야 함 |
| `source_quote` | string | 원문에서 복사한 직접 인용. 30자 내외. 원문 언어 그대로 |
| `fetched_at` | string | ISO 8601 형식의 fetch 시각 |

모든 숫자·수량·날짜·고유명사·직접 인용은 최소 하나의 `fact_sources` 항목에 연결되어야 한다. 연결되지 않은 숫자·고유명사가 있으면 해당 카드는 Stage C에서 탈락한다.

---

## 7. Signal Rubric

Signal은 이벤트의 중요도·긴급도를 세 값(`top`·`high`·`mid`)으로 분류한다. 판정은 세 개 축 A·B·C에 대해 각각 0·1·2점을 부여한 뒤 합산한다.

### 7.1 축 정의

**A축 — 시장 규모·영향**
- 2점: 연 매출 영향 US$1B 이상 또는 GWh급 capacity 관련 또는 주가에 당일 유의미한 영향
- 1점: 연 매출 영향 US$100M~1B 또는 MWh급 단일 프로젝트
- 0점: 그 이하

**B축 — 정책·규제**
- 2점: 정부·연방·EU 지시/법안 서명·발효 또는 관세·보조금 주요 변경
- 1점: 정책 초안·consultation·가이드라인 발표 또는 지방정부 결정
- 0점: 정책 관련 없음

**C축 — 기술·공급망**
- 2점: 신규 양산 개시·공장 착공·인수합병·핵심 기술 규격 최초 공표
- 1점: 파일럿·시제품·MOU·공동 R&D 협력
- 0점: 기술·공급망 관련 없음

### 7.2 판정 규칙

| 합산 점수 | signal |
|---|---|
| ≥ 5점 | `top` |
| 3~4점 | `high` |
| 1~2점 | `mid` |
| 0점 | 카드 대상 아님 — Stage A에서 discard |

**예외**: 단일 축에서 2점이고 다른 두 축이 0점이어도 이벤트 성격이 명백히 중요하면 (예: 글로벌 공급사 대규모 양산 개시) `high` 부여 가능. 이 경우 `signal_rubric.exception` 필드에 사유 기재.

**하향 제약**: Source Tier가 3이고 단독 보도면 `top` 부여 불가. 최대 `high`. 추가 검증이 필요한 경우 `_needs_review=true`.

---

## 8. Source Tier Map

소스의 신뢰도를 세 Tier로 분류한다. 같은 이벤트가 여러 소스에서 보도되면 가장 높은 Tier를 적용한다.

### 8.1 Tier 1 — 1차 공식·검증 매체

- 정부·규제기관 공식 발표 (예: 미국 주지사실, EU 집행위원회, 중국 공업정보화부, 한국 산업통상자원부, 캐나다 NRCan)
- 상장 기업 IR·공시·보도자료 (예: 기업 공식 newsroom)
- 글로벌 1차 통신사·경제지 (Reuters, Bloomberg, Financial Times, Wall Street Journal, Nikkei)
- 산업 전문지 중 검증 엄격성이 확인된 매체: Energy-Storage.news, PV Magazine, Reuters Events, BloombergNEF

### 8.2 Tier 2 — 국가 레거시·산업 전문 매체

- 각국 주요 경제·산업지 (예: 한국경제, 조선비즈, 서울경제, 매일경제, 中国电池联盟(CBEA), OFweek, Gasgoo, CnEVPost, 日刊工業新聞)
- 산업 전문지 중 중견 매체: electrive, pv-tech, Renew Economy, Utility Magazine
- 주요 컨설팅·리서치 기관의 공개 리포트: IEA, IRENA, Aurora Energy Research, Wood Mackenzie, Rystad Energy, BloombergNEF(월간·분기 요약 제외)

### 8.3 Tier 3 — 블로그·집계·소규모 매체

- 뉴스 집계 사이트, 블로그, 소셜미디어 인용
- 독립·소규모 매체의 단독 보도로 교차 확인이 안 된 경우
- press release 배포 플랫폼(PR Newswire·CNW 등)은 원 발행처를 확인해 상위 Tier로 재분류

### 8.4 판정 규칙

- 같은 이벤트가 Tier 1·2에 모두 보도되면 Tier 1 적용
- Tier 3 단독 보도는 해당 카드의 `source_tier=3`이고 `_needs_review=true`
- `scope_policy.json`에 Tier 1 매체 목록이 관리되며, 매체 추가·강등은 해당 파일 수정으로 반영

---

## 9. Stage A — Card Spec Builder

### 9.1 목적
triage 산출물의 kept cluster 전수를 검토해 카드화 대상 spec으로 변환하거나 reinforcement·discard 판정을 기록한다.

### 9.2 입력
- `triage_output_{YYYYMMDD}_{HHMMSS}.json`의 `kept_clusters[]` 및 `rescue_clusters[]`
- `baseline` 인덱스 (최근 3개월 누적 카드의 `id`·`title`·`urls[]`·`entity_tags[]` 등)
- `tier2_entities.json`, `tier2_events.json`
- `scope_policy.json`

### 9.3 절차

1. **baseline 매칭 검사** (모든 kept cluster에 대해)
   - URL 일치: 신규 cluster의 URL이 baseline 카드의 `urls[]`와 하나라도 겹치면 `duplicate_of_existing_main_card` 후보
   - Entity overlap: `entity_tags[]`가 3개 이상 공유되는 baseline 카드가 있으면 duplicate 후보
   - Entity 2개 + 같은 cat + 날짜 ±3일 이내 → follow-up 후보
   - Entity 2개 + 다른 cat → related 후보

2. **서사 축 검사** (중복 후보에 대해)
   - **반복**: 같은 이벤트·같은 프레임의 단순 재보도 → reinforcement로 분류 (신규 카드 생성 안 함)
   - **진전**: 같은 서사 축에서 새로운 사실(양산 개시, 추가 투자, 후속 발표)이 포함된 경우 → 신규 카드 생성, baseline 카드를 `related`에 추가
   - **반전**: 기존 카드와 반대 방향 사실 또는 정정 → 신규 카드 생성 + `supersedes` 필드에 baseline 카드 ID 기재
   - 일일 run 특성상 동일 서사 축이 여러 날 연속 등장 가능. 신규 카드 생성 기준은 엄격히 적용해 단순 업데이트는 reinforcement로 처리.

3. **Source Tier·Signal 초기 판정** (신규 카드 후보에 대해)
   - Source Tier는 §8 기준으로 판정
   - Signal은 §7 기준으로 초기 점수 부여. 이 점수는 Stage C에서 재검증됨
   - Tier 3 단독 이벤트는 `_needs_review=true` 플래그 예약

4. **Region·Category·이벤트일 확정**
   - Region은 §5 기준. cluster의 `region_hint`는 참고만 하고 실제 이벤트 기준으로 판정
   - Category는 §6.1 taxonomy 12종 중 택일
   - 이벤트일(`date`): cluster의 `date_hint`가 news 발행일일 수 있으므로 본문 상 명시된 이벤트 실행일이 있으면 그것을 우선. 예: 법안 서명일이 4월 13일이고 보도일이 4월 16일이면 `date`는 2026-04-13.

5. **primary_url 선정**
   - passed spec의 `primary_url` 필드에는 다음 조건을 만족하는 URL만 배정:
     - Pre-fetch Stage에서 web_fetch 가능 (paywall·login-required·JS-only 아님)
     - Tier 1 또는 Tier 2 매체
     - 본문이 이벤트 전체를 충분히 다룸(단순 1-2문장 언급 아님)
   - 조건 만족 URL이 cluster 내 없으면 web_search로 추가 검색. 그래도 없으면 Stage A에서 해당 cluster discard.

6. **판정 기록**
   - 모든 kept cluster 각각에 대해 `passed | existing_reinforcement | discard` 중 하나를 기록
   - 각 판정에 reason 명시. 기록 누락(silent loss) 금지.

7. **dropped cluster 감사 (필요 시)**
   - triage가 STRONG+DROP 플래그를 건 dropped cluster는 전수 재검토
   - 실수 탈락으로 판정되면 rescue cluster로 이동시킨 뒤 위 절차로 처리

### 9.4 출력

- `{run_id}_prompt_a_output.json`: passed spec 배열. 각 spec은 `cluster_id`, `primary_url`, `region`, `date`, `cat`, `sub_cat`, `signal`, `source_tier`, `related_candidates[]`, `title_hint`, `fact_hint` 등을 포함.
- `{run_id}_prompt_a_audit.json`: 모든 kept cluster의 판정 결과 (zero-omission 증적).
- `{run_id}_baseline_match_audit.json`: baseline 매칭 결과 로그.
- `{run_id}_related_inverse_report.json`: baseline 카드가 신규 카드를 `related`에 추가해야 하는 경우의 제안 목록. baseline 직접 수정은 하지 않고 제안만 기록.

---

## 10. Pre-fetch Stage — URL 사전 확보

### 10.1 목적
Stage B가 카드 본문을 작성하기 전에 원문을 확보해 fact 추출의 기반을 만든다. fetch 실패 spec은 카드화 대상에서 제외한다. 이 단계는 Stage A 완료 후, Stage B 시작 전에 일괄 실행한다.

### 10.2 입력
- `{run_id}_prompt_a_output.json`의 passed spec 배열

### 10.3 절차

1. **각 passed spec에 대해 `primary_url` web_fetch 수행**

2. **실패 처리**
   - 실패 사유가 paywall·login-required인 경우: 같은 이벤트의 open-access 매체 URL을 web_search로 검색해 대체
   - 실패 사유가 404·timeout·JS-only인 경우: 동일 이벤트의 다른 매체 URL로 대체 시도
   - 대체 URL을 찾으면 해당 spec의 `primary_url` 교체 후 fetch 재시도
   - 모든 대체 시도 실패 시 해당 spec을 `{run_id}_unverified_specs.json`에 기록하고 Stage B 대상에서 제외

3. **복수 매체 merged spec 처리**
   - Stage A에서 여러 cluster가 merge된 spec은 대표 URL 1개와 검증용 보조 URL 최소 1개를 fetch

4. **추출**
   - 각 성공 fetch에서 다음 4종만 추출:
     - **숫자·수량**: 금액, 용량(MW·MWh·GWh), 일자, 비율, 생산량, 인원 등
     - **고유명사**: 기업명, 인물명, 제품명, 법안명, 프로젝트명, 지명
     - **직접 인용**: CEO·회장·장관·주지사 등 실명이 있는 공식 발언
     - **명시적 비교·맥락**: 원문이 직접 서술한 비교(전년 대비 X% 증가)나 배경(이번이 첫 사례 등)
   - 추출 대상 외 정보(기자 해설·업계 전망·추론)는 카드화 근거로 사용하지 않음

5. **추출 결과 저장**
   - 각 spec별로 추출된 4종 목록을 `{run_id}_fetched_corpus.json`에 저장
   - 각 추출 항목은 `{item, source_url, source_quote, fetched_at}` 형식

### 10.4 출력

- `{run_id}_fetched_corpus.json`: spec별 fetch 원문 링크 및 추출된 4종 목록
- `{run_id}_unverified_specs.json`: fetch 실패 spec 목록과 각 사유, 대체 URL 제안 시도 이력

---

## 11. Stage B — Insight Writer

### 11.1 목적
Pre-fetch가 성공한 spec만 대상으로 카드 본문을 작성한다. fact 필드는 `{run_id}_fetched_corpus.json`에 추출된 정보만 사용한다. 카드 등급(full·brief·discard)은 추출된 fact 건수로 기계적으로 결정한다.

### 11.2 입력
- `{run_id}_fetched_corpus.json`

### 11.3 카드 등급 자동 결정

spec별로 추출된 fact 총 건수(숫자·고유명사·직접 인용의 합산)를 집계한다.

| 추출된 fact 건수 | 카드 등급 | 처리 |
|---|---|---|
| ≥ 5건 | **full** | §11.5 full 카드 템플릿으로 작성 |
| 2~4건 | **brief** | §11.6 brief 카드 템플릿으로 작성 |
| ≤ 1건 | **discard** | `{run_id}_insufficient_facts.json`에 기록, 카드화 안 함 |

등급 결정은 기계적으로 적용하며 editor 판단에 의한 예외를 허용하지 않는다. 단, fact 건수가 경계선(예: 정확히 5건)이면서 원문 맥락이 빈약한 경우 Stage C에서 downgrade(full → brief) 가능.

### 11.4 필드 작성 규칙

#### fact 필드
- 반드시 "X에 따르면" 형식의 attribution 포함. 예: "VW 공식 보도자료 및 electrive 보도에 따르면 ..."
- 본문에 등장하는 모든 숫자·고유명사·인용은 `{run_id}_fetched_corpus.json`의 추출 항목에서 가져온다.
- 원문에 없는 비교·해석·업계 진단·전망은 fact에 포함하지 않는다. 그런 내용이 필요하면 implication 필드에 관찰형으로 기술한다.
- 환산 수치(예: 달러 → 원화)는 원문에 환산이 있으면 그대로 인용하고, 없으면 환산하지 않거나 환율 기준일을 명시한다.
- full 카드 fact는 400자 이내, brief 카드 fact는 50~120자 범위.

#### title 필드
- 카드의 메인 헤드라인. editor 영역이지만 다음 제약을 지킨다:
  - 원문이 제시한 프레임과 같은 방향이어야 한다. 원문이 "반고체 양산 개시"를 다루면 title도 반고체. 원문과 반대 방향(반고체 → "전고체 상용화")으로 프레임 뒤집기 금지.
  - "X가 아니라 Y다", "X는 Y를 의미한다" 같은 단정적 템플릿 문장 금지.
  - "이 카드의 핵심은 ~이다", "~의 진짜 의미는"으로 시작하는 연역적 오프닝 지양.

#### sub 필드
- title 아래 보조 1줄. 핵심 수치나 행위자를 간결히 표기.

#### gate 필드
- 해당 이벤트의 편집적 의미·해석·서사 프레임. editor 영역.
- 원문 프레임과 같은 방향 유지. 반전·정정·강한 반박이 필요하면 fact 기반으로 논증하고 `supersedes` 필드 연계.
- 길이는 2~4문장 권장.

#### implication 필드
- 후속 관찰 포인트 배열. full 카드 ≥ 2개, brief 카드 ≥ 1개. 각 원소 ≥ 20자.
- 단정형 문장 금지. 관찰형·조건형 어휘만 사용. 예시:
  - 허용: "~할 여지가 있다", "~인지 Q2 IR에서 확인이 필요한 축", "~가 관찰 포인트", "~로 이어질지 여부"
  - 금지: "~가 된다", "~할 것이다", "~의 시대가 열린다", "~가 확실시된다"
- implication에 수치·고유명사가 등장하면 해당 항목도 `fact_sources`에 매핑한다. implication은 fact의 문맥 확장이며 새 fact를 생성하지 않는다.
- 기억 블랙리스트 주제(자주 틀리는 로드맵·연도·수치)는 fetch 근거 없이 사용하지 않는다. 예: 특정 기업의 전고체 양산 시점을 원문 확인 없이 기재 금지.

#### urls 필드
- 이벤트 근거 URL 배열. 첫 번째 원소는 primary_url.
- Pre-fetch Stage에서 실제로 fetch 성공한 URL만 포함. 실패·paywall·404 URL은 제외.

#### related 필드
- 서사 축을 공유하는 다른 카드(baseline 또는 이번 run 내)의 `id` 배열.
- 같은 run 내 카드 간 관계는 Stage C에서 최종 확정됨. Stage B에서는 baseline 기반 `related_candidates[]`만 우선 채운다.

### 11.5 Full 카드 템플릿

```
id:             YYYY-MM-DD_REGION_NN
region:         ...
date:           ... (이벤트 발생일)
cat:            ... (taxonomy 12종 중 택일)
sub_cat:        ...
signal:         top|high|mid
signal_rubric:  {A: 0-2, B: 0-2, C: 0-2, total: sum, exception: null 또는 사유}
source_tier:    1|2|3
title:          ... (메인 헤드라인)
sub:            ... (1줄)
gate:           ... (2~4문장, 프레임·해석)
fact:           ... (≤ 400자, attribution 포함)
implication:    [항목 ≥ 2개, 각 ≥ 20자]
urls:           [... 대표 URL 포함]
related:        [... baseline 또는 이번 run 카드 ID]
fact_sources:   [모든 숫자·고유명사·인용에 1:1 매핑]
_needs_review:  true|false (조건 해당 시)
```

### 11.6 Brief 카드 템플릿

```
id:             YYYY-MM-DD_REGION_NN
region:         ...
date:           ...
cat:            ...
sub_cat:        ...
signal:         mid (brief는 대부분 mid. 예외적으로 high 가능)
source_tier:    1|2|3
title:          ...
sub:            ... (1줄)
gate:           ... (선택, 1~2문장)
fact:           ... (50~120자)
implication:    [항목 ≥ 1개, ≥ 20자]
urls:           [...]
related:        [...]
fact_sources:   [필수]
_needs_review:  true|false
```

### 11.7 Framing 자가 검증 (Stage B가 각 카드 작성 직후 수행)

작성한 카드 각각에 대해 다음 세 질문을 자가 점검한다.

1. fact 서술 방향이 원문과 같은가? 다르면 카드 폐기 또는 fact 재작성.
2. title이 fact를 압축한 것인가, 아니면 추론·해석을 덧붙여 방향을 바꾼 것인가? 후자면 title 재작성.
3. implication이 fact에서 파생된 것인가, 아니면 새 사실을 만들어낸 것인가? 후자면 implication 재작성.

어느 하나라도 판정이 불확실하면 `_needs_review=true` 플래그를 추가한다.

### 11.8 본문 텍스트 위생

- 본문(title·sub·gate·fact·implication) 어디에도 다른 카드의 `id`를 하드코딩하지 않는다. 연관 관계는 `related` 배열로만 표현한다.
- `signal`은 소문자 고정. `date`는 `YYYY-MM-DD` 고정. `cat`은 taxonomy 12종 이내.
- 카드 `date`는 이벤트 발생일. news 발행일과 다르면 이벤트일 우선. 예: 법안 서명일 4월 13일, 보도일 4월 16일 → `date: 2026-04-13`.

### 11.9 출력

- `{run_id}_prompt_b_output.json`: draft 카드 배열 (등급·fact_sources·`_needs_review` 플래그 포함)
- `{run_id}_insufficient_facts.json`: fact 1건 이하로 discard된 spec 목록과 각 사유

---

## 12. Stage C — Red-team Reviewer

### 12.1 목적
Stage B의 draft 카드 전수를 검증해 최종 payload를 확정한다. 검증 항목은 스키마 컴플라이언스·팩트 추적성·프레임 정합성·서사 축 일관성이다.

### 12.2 입력
- `{run_id}_prompt_b_output.json`
- `{run_id}_fetched_corpus.json`
- `baseline` 인덱스

### 12.3 금지 사항
- 실패 카드의 silent 제거. 제거 시 `{run_id}_rejected_cards.json`에 ID와 사유를 명시한다.
- `signal`, `region`, `date`, `cat` 필드의 임의 변경. Stage A·B에서 확정된 값을 유지한다. 명백한 오류만 수정하되 수정 사유를 Redteam Report에 기록한다.
- 본문의 대량 rewrite. 명백한 사실 오류·오타·프레임 위반만 수정하며 스타일 변경은 하지 않는다.

### 12.4 검증 절차

1. **스키마 컴플라이언스 자동 검사**
   - §6의 필수 필드 누락 여부
   - 필드 타입 및 형식 (ID 포맷, date 포맷, signal 소문자, cat 12종 이내)
   - `fact_sources`의 각 객체가 `{claim, source_url, source_quote, fetched_at}` 네 필드를 모두 갖는지

2. **Fact Discipline 검증** (`docs/FACT_DISCIPLINE.md` 기준)
   - `fact_sources`의 모든 `source_url`이 해당 카드의 `urls[]` 내에 존재하는지
   - 모든 `source_quote`가 30자 내외 직접 인용 형태인지
   - fact와 implication에 등장하는 모든 숫자·고유명사·인용·날짜가 적어도 하나의 `source_quote`에서 검색 가능한지 (문자 매칭)
   - fact에 "업계·시장·분석가·전문가" 같은 모호한 주체어가 쓰이지 않았는지
   - 환산 수치(예: 원화 환산)가 있으면 환율 기준 또는 원문 환산 명시가 있는지
   - 위 항목 중 하나라도 실패한 카드는 payload에서 제외하고 `{run_id}_rejected_cards.json`에 기록

3. **Framing 검증**
   - 원문 프레임과 카드 프레임의 방향 일치 여부 점검 (Pre-fetch corpus의 추출 항목과 비교)
   - 다음 세 가지 위반 유형을 자동 스캔:
     - 원문 대비 반대 방향 프레임 (예: 원문이 "반고체 양산"인데 카드가 "전고체 상용화"로 서술)
     - "X가 아니라 Y다", "X보다 Y가 의미있다" 등 AI 단정 템플릿
     - 원문에 없는 기업 로드맵·연도 예측을 기억에 기반해 기재
   - 위반 발견 시 해당 카드는 payload 제외 또는 본문 수정 후 재검토

4. **서사 축 검사 (Stage A 판정 재확인)**
   - Stage A가 신규 카드로 분류한 spec이 실제로 baseline 대비 "진전" 또는 "반전" 기준을 충족하는지
   - 단순 반복으로 판정되면 reinforcement로 재분류하고 payload 제외

5. **편집 red-team**
   - Source Tier 3 단독인데 `_needs_review=false`인 카드 → 플래그 재설정
   - 익명 소스·초기 단계 이벤트가 `top` signal로 잡혀있으면 `high` 또는 `mid`로 하향
   - Signal Rubric 점수가 실제 본문과 일치하는지

6. **related 필드 최종 확정**
   - 이번 run 내 카드 간 관계 추가 매핑
   - baseline 역참조 제안은 `{run_id}_related_inverse_report.json`에 별도 기록 (baseline 카드 직접 수정 안 함)

7. **본문 하드링크 정리**
   - 본문에 잘못 포함된 다른 카드 ID를 `related` 배열로 이동

### 12.5 출력

- `{run_id}_payload.json`: 최종 카드 배열. 모든 카드는 fact_sources·related·`_needs_review`(해당 시) 포함.
- `{run_id}_redteam_report.md`: 검증 단계별 로그. 각 카드의 통과/탈락, 수정 내역, 재분류 사유 기록.
- `{run_id}_rejected_cards.json`: 검증 실패로 payload에서 제외된 카드와 각 제외 사유.

---

## 13. Never / Always 체크리스트

### 13.1 NEVER

- baseline 카드 본문을 산출물 파일에 재출력
- 파이프라인 단계 표식(prompt_a, draft 등)을 카드의 production `id`에 포함
- 카드 본문(title·sub·gate·fact·implication)에 다른 카드 ID 하드코딩
- Source Tier 3 단독 보도를 `top` signal로 부여
- 매체 국적만으로 region 배정 (이벤트 기준이 아님)
- `cat` 필드에 taxonomy 12종 밖의 값 사용
- fact·implication 필드를 기억·추론·상식으로 메우기
- Pre-fetch 실패 spec으로 카드 생성
- `fact_sources` 배열 없이 카드를 payload에 포함
- 원문 프레임과 반대 방향으로 title·gate 작성
- "X가 아니라 Y다" 단정 템플릿 사용
- 기억에 기반한 기업 로드맵·연도·수치 claim (예: 특정 기업의 전고체 양산 시점을 fetch 확인 없이 기재)
- kept cluster의 판정 기록 누락 (silent loss)
- 카드 `date`에 news 발행일 사용 (이벤트 발생일이 원칙)
- Stage C에서 실패 카드를 silent 제거 (사유 기록 필수)
- `cards.json` 통합본을 baseline 교체 목적으로 이번 run 산출물에 포함

### 13.2 ALWAYS

- 모든 kept cluster에 `passed | existing_reinforcement | discard` 중 하나를 기록
- Stage A 완료 후 Stage B 시작 전에 Pre-fetch Stage 실행
- Stage B는 Pre-fetch 성공 spec만 대상으로 처리
- 카드 등급(full·brief·discard)은 추출된 fact 건수로 기계적 결정
- fact와 implication에 등장하는 모든 숫자·고유명사·인용·일자를 `fact_sources`에 1:1 매핑
- 환산 수치에 환율 기준 또는 원문 환산 명시
- Signal Rubric 3축 점수를 `signal_rubric` 필드에 기록
- Source Tier를 `source_tier` 필드에 기록
- Tier 3 단독·익명·framing 의심 카드에 `_needs_review=true` 플래그 부여
- `related` 필드를 빈 배열로라도 항상 채움
- `signal` 소문자 고정, `id`는 `YYYY-MM-DD_REGION_NN` 형식
- `cat`은 §6.1 taxonomy 12종 이내
- Region 판정은 §5의 6개 원칙 순서대로 적용
- fact 필드에 "~에 따르면" attribution 포함
- 카드 작성 후 Stage B 자체의 Framing 자가 검증 3문항 수행
- Stage C에서 원문 프레임 방향과 카드 프레임 방향 일치 검증
- 실패 카드의 ID와 사유를 `{run_id}_rejected_cards.json`에 명시 기록

---

## 14. 운영 원칙

- Stage A는 **선별과 분류**이다. cluster를 카드 후보로 변환하고 baseline과의 관계를 판정한다.
- Pre-fetch Stage는 **원문 확보**이다. 카드 작성의 사실 기반을 만든다.
- Stage B는 **추출된 fact로만 작성**이다. 추론·기억·상식은 이 단계에 들어오지 않는다.
- Stage C는 **이중 검증**이다. 팩트 추적성과 프레임 정합성을 동시에 본다.

Baseline은 인덱싱만 하고, 인용은 원문만 사용하며, 프레임은 원문 방향만 따른다.

정확성은 취향이 아니라 방화벽이다. Framing도 fact 검증의 일부이다.

이 문서에 기재되지 않은 엣지케이스가 발생하면 `docs/FACT_DISCIPLINE.md`의 판단을 우선 적용하고, 해당 케이스를 본 문서 또는 스키마 문서에 판례로 추가한다.
