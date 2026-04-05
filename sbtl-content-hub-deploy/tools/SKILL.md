# Battery Policy Tracker — Daily Update Skill

## Trigger
User says any of: `트래커 업데이트`, `daily tracker run`, `tracker update`, `정책 트래커 돌려줘`

## Overview
5개 권역(NA·EU·CN·KR·JP) 배터리·ESS·EV 정책 트래커를 업데이트하는 프로토콜.
데이터 파일(JSON)을 업데이트한 뒤, 렌더러(JS)로 인터랙티브 HTML을 재생성한다.

## File Locations
- **Data**: `/home/claude/tracker-skill/tracker_data.json`
- **Renderer**: `/home/claude/tracker-skill/render_tracker.js`
- **Output**: `/mnt/user-data/outputs/battery_policy_tracker_2026_internal.html`

## Update Protocol

### Step 1: Load Current Data
```bash
cat /home/claude/tracker-skill/tracker_data.json
```
현재 아이템 목록과 상태를 확인한다.

### Step 2A: 기존 항목 상태 체크 — 5개 권역
각 권역별로 기존 UPCOMING/ACTIVE/WATCH 아이템의 상태 변화를 확인한다.

**검색 쿼리 템플릿 (기존 항목 기반):**
- 기존 아이템 중 상태 전이가 예상되는 건(시행일 임박 등)에 대해 개별 검색
- 예: `"FEOC MACR guidance 2026"`, `"GB38031 battery standard July 2026"`

### Step 2B: 신규 정책 탐색 — 5개 권역
트래커에 아직 없는 새로운 정책·규제·법안을 탐색한다.

**검색 쿼리 템플릿 (신규 발견용):**
- NA: `US battery energy storage new regulation {current month} {year}`
- NA: `Congress battery bill introduced {year}`
- EU: `EU battery regulation new delegated act {year}`
- EU: `European Commission battery industry proposal {current month} {year}`
- CN: `中国 电池 新规 {current month} {year}` 또는 `China battery new policy {current month} {year}`
- CN: `MIIT 公告 电池 {year}`
- KR: `배터리 이차전지 신규 고시 공포 {current month} {year}`
- KR: `산업부 환경부 배터리 발표 {current month} {year}`
- JP: `Japan METI battery new rule {current month} {year}`
- JP: `経産省 蓄電池 新制度 {year}`

**신규 발견 시 처리:**
1. 기존 46건과 중복 여부 확인
2. 중복 아니면 신규 아이템 객체 생성 (ID 규칙: {권역}-{3자리 번호})
3. 적절한 상태(UPCOMING/ACTIVE/WATCH) 부여
4. 1차 출처(Tier 1) 소스를 src[0]에 배치
5. tip과 detail은 가능한 범위에서 채우고, 불확실하면 비워둔다
6. lastChecked + checkNote 포함
7. 변경 리포트에 ➕ 신규 추가로 별도 표시

### Step 3: 상태 전이 판단
검색 결과를 기반으로 각 아이템의 상태를 업데이트한다:

| 현재 상태 | 전이 조건 | 새 상태 |
|----------|----------|--------|
| UPCOMING | 시행일 도래 또는 시행 확인 | ACTIVE |
| UPCOMING | 시행 완료 또는 일회성 이벤트 종료 | DONE |
| ACTIVE | 이슈 종결·법안 통과·시행 완료 | DONE |
| WATCH | 구체적 일정 확정 | UPCOMING |
| WATCH | 즉시 시행 | ACTIVE |
| (신규) | 새로운 정책·규제·시장 신호 발견 | 적절한 상태로 신규 추가 |

### Step 4: JSON 업데이트
`tracker_data.json`을 수정한다:
- 상태 변경: `s` 필드 업데이트
- 날짜 업데이트: `dt` 필드 업데이트
- 설명 보강: `d` 필드에 최신 정보 반영
- 신규 아이템 추가: 배열에 새 객체 append
- 출처 추가: `src` 배열에 새 소스 append

### Step 5: HTML 재생성
```bash
cd /home/claude/tracker-skill && node render_tracker.js
```
JSON 데이터를 읽어 인터랙티브 HTML을 생성하고 `/mnt/user-data/outputs/`에 출력한다.

### Step 6: 변경 리포트
유저에게 변경사항을 간결하게 보고한다:
```
[Daily Tracker Update — 2026.MM.DD]

── 2A: 기존 항목 ──
✅ 상태 변경: N건 (예: CN-005 UPCOMING→ACTIVE)
📝 설명 업데이트: N건
🔍 확인 완료: N건 (변화 없음)

── 2B: 신규 탐색 ──
➕ 신규 추가: N건 (예: EU-012 새로운 위임입법 발표)
🔎 탐색 완료: 변화 없음 / 후보 N건 발견

⚠️ 다음 주 주목 이벤트: (있으면 간단히)
```

## Source Directory (모니터링 사이트)
업데이트 시 아래 사이트를 우선 체크한다:

### NA
- IRS.gov (credits-deductions)
- Federal Register
- DOE EERE
- SEIA Research
- Congress.gov
- Energy Storage News
- pv magazine USA

### EU
- EUR-Lex
- EU Council Press
- EC News & Media
- Innovation Fund
- EBA250
- electrive

### CN
- gov.cn (영문)
- MIIT
- CarNewsChina
- ChinaEVHome
- GlobalChinaEV

### KR
- Korea.kr 정책브리핑
- MOTIR (영문)
- 국가법령정보센터
- 머니투데이
- The Elec

### JP
- METI (영문)
- Borderless Law
- ESS News
- Toyota Global Newsroom
- Nikkei Asia

## Rules
- **Zero-hallucination**: 검색에서 확인되지 않은 상태 변경은 하지 않는다.
- **Source-matched**: 모든 신규/변경 아이템에는 반드시 출처 링크를 포함한다.
- **날짜 기준**: 오늘 날짜(KST)를 기준으로 상태를 판단한다.
- **LAST UPDATED 갱신**: HTML 내 타임스탬프를 오늘 날짜로 업데이트한다.
- **lastChecked 갱신**: 검색으로 확인한 모든 아이템의 `lastChecked`를 오늘 날짜로, `checkNote`를 검색 결과 요약으로 업데이트한다.
