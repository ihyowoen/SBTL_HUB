# Future Card Standard — Full Schema Locked

이 문서는 **앞으로 생성될 카드**에 대한 고정 기준이다.

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
  "related": ["...", "..."]
}
```

- `id`: `docs/CARD_ID_STANDARD.md` 참조
- `cat`: **Primary Category Taxonomy 내 12개 중 하나** (§3 참조). 필터·라우팅용
- `sub_cat`: 편집자 freestyle 한국어. 디스플레이·검색용 (선택 필드지만 신규 카드 원칙적으로 포함)
- `related`: 다른 카드와의 관계는 본문 안에 ID 하드코딩 금지. `related` 배열로만 관리

---

## 2. Region Label Rule — Locked

region은 기사 출처 국가가 아니라 **사건의 직접 무대**로 붙인다.

- KR / US / CN / JP는 해당 국가가 직접 무대일 때만 사용
- 유럽 개별 국가 사건과 EU 제도 뉴스는 EU
- 두 개 이상 국가가 동등하게 핵심이면 GL
- 현재 배지 체계 밖 국가는 GL
- 애매하면 GL

### 2.1 엣지케이스 판례 — 반복 발생 패턴

**A. 해외 상장 · 해외 자본 조달**
- 본토 기업의 HK · SG · US 등 해외 상장/증자는 **기업 본국 기준**
- 예) 중국 본토 기업의 HK IPO → `CN`
- 예) 한국 기업의 NASDAQ / NYSE 상장 → `KR`
- 근거: 자본 조달 주체의 사업 활동지가 실질 무대이며, 거래소는 도관

**B. 정책 검토 · 정책 보도 단계**
- 국가 X의 정책 검토 · 초기 보도는 실행 전이라도 **발화지 기준**
- 예) 중국의 대미 태양광 설비 수출제한 "검토" → `CN`

**C. 합작 · JV**
- 두 국가 지분 · 경영 동등 → `GL`
- 한 쪽이 지배적(>50% 지분 또는 운영 주도) → 지배 쪽 국가

**D. 다국적 제품 · 플랫폼 런칭**
- 최초 런칭 시장 기준

**E. 출처 매체와 사건 무대가 다른 경우**
- 매체 국적은 region 판정에 무관
- 한국 매체가 중국 뉴스 보도 → `CN`

---

## 3. Category Taxonomy — Locked

`cat` 필드는 **다음 12개 중 하나** 로만 설정한다.

| cat | 정의 | sub_cat 예시 |
|---|---|---|
| `Battery` | 셀·팩·차세대 배터리(전고체·Na-ion), 배터리 제조사 자체 동향 | 전고체, LFP, 삼원계, 수직통합 |
| `ESS` | 계통·산업용 에너지 저장 프로젝트·정책·시장 | 배치, 장주기, AIDC, BESS |
| `Materials` | 양극재·음극재·전해질·분리막·핵심광물·재활용 | 광물, 재활용, 분리막, ESG 공시 |
| `EV` | 전기차 OEM·모델·판매 | 신모델, 수주, 판매 |
| `Charging` | EV 충전 인프라·CPO·충전기·V2G | IPO, 고속충전, V2G, 공동주택 |
| `Policy` | 정부 정책·규제·법안·보조금·세제·무역조치 | CBAM, 전기요금, 블랙리스트, 태양광장비 |
| `Manufacturing` | 공장·장비·소부장·생산 시설 | 북미 localization, 장비 실적 |
| `AI` | AI 데이터센터·GPU·전력 수요 | DC, GPU 인프라 |
| `Robotics` | 휴머노이드·embodied AI 하드웨어 연결 | 휴머노이드 전고체 |
| `PowerGrid` | 전력망·재생에너지 발전 사업·PPA | 태양광, 풍력, 유틸리티 |
| `SupplyChain` | 수출통제·관세·물류·공급망 리스크 | 핵심광물 협정, 수출중단 |
| `Other` | 위 12개에 맞지 않는 경우 (신중 사용) | - |

### 3.1 Category 할당 규칙

1. 한 카드는 **정확히 하나**의 primary `cat`을 가진다
2. 카드가 두 축에 걸치면 더 지배적인 축으로 배정하고 나머지는 `sub_cat`에 반영
   - 예: "CATL 광물 자회사 설립" → `cat: Battery`, `sub_cat: 소재 수직통합` (주체가 배터리사이므로)
   - 예: "Bloom ESG 재활용 광물 계산도구" → `cat: Materials`, `sub_cat: 재활용 ESG 공시`
3. 애매하면 편집자 판단이되, `sub_cat`이 자동 카테고리 경계를 넘는 경우 `Other` 금지 — 반드시 primary 12개 안에서 하나 선택

### 3.2 sub_cat 권장 형식

- 한국어 복합어 (예: `공동주택 충전`, `장주기 BESS`, `전고체 상용화`)
- 쉼표·세미콜론·`|` 금지 (쿼리 충돌 방지)
- 10자 내외 권장

---

## 4. 최종 원칙

**앞으로 생성되는 카드는 full schema 기준으로만 작성·검수·병합한다.**
