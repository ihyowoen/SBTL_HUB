# QC Backlog and Next Steps

## 목적
이 문서는 최근 대화에서 나온 기능 버그, UX 문제, 구조적 오해, 그리고 다음 개발 우선순위를 **한 번에 정리한 실행 문서**다.

기존 `ENHANCED_RED_TEAM_FUNCTIONAL_BRIEF.md`가 **방향/금지사항/완료 기준** 중심이라면,
이 문서는 그 이후 발견된 **실제 버그 원인, QC 결과, 백로그 우선순위, 구현 힌트**까지 포함한다.

---

## 1. 현재 상태 요약

### 이미 남겨진 문서/코멘트
현재 repo / PR에는 이미 다음이 기록되어 있다.

- `ENHANCED_RED_TEAM_FUNCTIONAL_BRIEF.md`
  - 별도 Translator 탭 금지
  - 기존 News + AI 흐름 안에서 번역/요약/설명 통합
  - 웹툰 URL/내비게이션 복구 필요
  - 챗봇 링크 클릭 가능 구조 필요
  - 1차/2차/3차 퀵가이드 필요
  - 완료 기준은 build success가 아니라 실제 동작

- PR conversation comments
  - 별도 번역기 탭은 잘못된 IA라는 점
  - 웹툰 EP.2 / BONUS / next-link 확인 필요
  - 챗봇 링크는 plain text가 아니라 anchor로 렌더해야 한다는 점
  - 현재 translate action이 거꾸로 동작한다는 점

### 이 문서가 추가로 다루는 것
이 문서는 아래를 추가로 정리한다.

- 챗봇 QC 결과
- 왜 챗봇이 “바보처럼” 느껴지는지
- 미국 뉴스가 자꾸 2026.03.16으로 뜨는 원인
- 번역 버튼이 한국어 → 외국어로 뒤집히는 원인
- 분석에 우리 prompt를 어디에 넣어야 하는지
- P0 / P1 / P2 개발 백로그

---

## 2. 핵심 버그 / 구조 문제

### A. 외국 뉴스 카드의 `번역` 버튼이 거꾸로 동작함
#### 현재 문제
현재 foreign news card에서 `번역` 버튼을 누르면,
사용자가 기대하는 것은 **외국 기사 → 한국어 번역/설명**이다.

하지만 실제 구현은 다음처럼 동작한다.
- 입력값: `card.T`, `card.sub`
- 이 값들은 이미 `cards.json` 안의 **한국어 카드 문구**임
- API 호출은 `sourceLang: "ko"` + `targetLang: regionLangMap[card.r]`

즉 지금 번역 버튼은
- 원문 외국 기사 → 한국어 번역 ❌
- 한국어 카드 텍스트 → 외국어 재번역 ✅

#### 왜 문제인가
이건 단순 wording 문제가 아니라 **product behavior bug**다.

사용자 입장에서는
- “외국 기사를 이해하고 싶다”
가 목적이지,
- “이미 한국어로 정리된 카드를 영어/중국어/일본어로 다시 바꾸고 싶다”
가 목적이 아니다.

#### 즉시 수정 권고
현재 데이터 구조상 **진짜 번역 입력값(원문 본문/원문 요약)**이 앱에 없는 경우가 많다.
따라서 즉시 수정으로는 다음이 맞다.

- 카드의 `🌐 번역` 버튼 제거
- 아래 중 하나로 교체
  - `한국어 요약`
  - `핵심 설명`
  - `왜 중요한지`
- 내용은 기존 `card.sub` / `card.g` 사용

#### 진짜 번역 기능을 하려면
진짜 `번역`을 유지하려면 번역 대상이 바뀌어야 한다.
즉,
- 원문 기사 텍스트
또는
- 외부 검색에서 받아온 원문 title/summary
를 기준으로 foreign → Korean translation을 해야 한다.

---

### B. 미국 뉴스가 자꾸 2026.03.16으로 뜨는 문제
#### 관찰
사용자가 미국 뉴스 요청 시,
최신 카드가 아니라 예전 날짜(특히 `2026.03.16`)가 반복적으로 보이는 문제가 있음.

#### 데이터 자체 문제인지?
현재 `public/data/cards.json`에는 이미 2026-04-03 / 2026-04-02 / 2026-04-01 수준의 US 카드가 존재한다.
즉 문제는 **데이터가 없음**이 아니라 **retrieval logic**일 가능성이 높다.

#### 가장 유력한 원인
현재 `latestCards(cards, limit, region, targetDate)` 구조는
1. 전체 카드 풀에서 `latestDate(cards)` 계산
2. 그 날짜로 먼저 filter
3. 마지막에 region filter
를 하고 있다.

이 구조의 문제:
- 전체 최신일이 2026.04.05일 수 있음
- 그런데 그 날짜에 US 카드가 없으면
- region filter 후 빈 배열이 됨
- 이후 fallback이 일반 검색(searchCards / Brave)으로 넘어감
- 일반 검색은 recency 보장이 약해서 2026.03.16 카드가 튈 수 있음

#### 수정 원칙
`latestCards()`는 region이 들어오면 **region 내부에서 latestDate를 계산**해야 한다.

즉,
- 전체 latest 먼저 잡고 region filter ❌
- region별 card pool 만들고 그 안에서 latest 계산 ✅

#### 추가 보완
- `searchCards()` 정렬에 recency tie-break 추가
- “오늘 미국 뉴스 3개” 같은 요청은 일반 검색이 아니라 **전용 news retrieval route**로 처리
- region/date intent가 잡히면 Brave fallback 전에 내부 latest cards 우선

---

### C. 챗봇이 바보처럼 느껴지는 이유
#### 핵심 진단
현재 챗봇은 “대화형 AI”라기보다 **규칙 기반 검색기 + 카드 조합기**에 더 가깝다.

#### 이유 1) 질문 분류가 얕음
질문 분류가 keyword 기반이라
- 문맥 유지
- 대명사형 후속 질문
- 바로 직전 기사 기반 대화
를 버티기 어렵다.

예:
- “첫 번째 기사 번역해줘”
- “방금 미국 기사만 다시 설명해줘”
- “이 카드랑 관련된 중국 뉴스 더 찾아줘”
이런 요청을 제대로 처리하기 어렵다.

#### 이유 2) 마지막으로 보여준 기사/카드 상태를 기억하지 않음
실제 좋은 UX는 기사 객체 중심으로 이어져야 한다.

필요한 상태:
- lastShownCards
- lastShownLinks
- currentSelectedItem
- lastQuestionType
- lastRegion
- lastTargetDate

이 상태가 있어야 후속 대화가 자연스러워진다.

#### 이유 3) 외부 검색 결과도 너무 얕음
현재 Brave 결과는 title / description / url 정도만 보여줘서,
- 관련성 재정렬
- 중복 제거
- 출처 신뢰도 레이어
- 정부/기업/언론 우선순위
가 부족하다.

#### 이유 4) follow-up suggestions가 아직 충분히 문맥형이 아님
2차/3차 퀵가이드가 들어갔다 하더라도,
진짜로 좋아지려면 다음을 따라가야 한다.
- 이전 답변 타입
- 지역
- 날짜
- 직전 카드/기사
- foreign / policy / compare 같은 맥락

즉, “타입별 canned button”만으로는 한계가 있다.

---

## 3. 분석에 우리 prompt를 쓰는 방법

### 결론
**분석 레이어에는 우리 prompt를 쓰는 게 맞다.**
하지만 retrieval 단계까지 같은 prompt가 다 먹으면 안 된다.

### 올바른 구조
#### 1) Retrieval Layer
사실 수집 단계.
여기서는 아래만 정리한다.
- cards.json hits
- tracker_data.json hits
- Brave / external search results
- currently selected article/card object
- date / region / signal metadata

이 단계에서는 **사실과 객체를 정리**하는 것이 목적이다.

#### 2) Analysis Layer
여기서 우리 prompt 사용.
이 단계에서
- 왜 중요한지
- 한 줄 결론
- SBTL 관점 해석
- 한국/미국/중국 관점 영향
- follow-up suggestion
같은 해석을 붙인다.

### 잘못된 구조
- prompt가 검색도 하고
- 최신 날짜도 추정하고
- 링크 우선순위도 정하고
- 요약과 분석까지 동시에 하는 구조

이렇게 되면
- 날짜 오류
- 근거 흐림
- 추적성 약화
가 생긴다.

### 정리
- 검색/선별: deterministic + rules + metadata
- 해석/프레이밍: our prompt

---

## 4. P0 / P1 / P2 백로그

### P0 — 지금 바로 고칠 것
#### 1) foreign card의 `번역` 버튼 제거 또는 rename
- `🌐 번역` 제거
- `한국어 요약` / `핵심 설명` / `왜 중요한지` 중 하나로 교체
- 기존 `card.sub`, `card.g` 활용

#### 2) region-aware latestCards 수정
- region이 있으면 region pool 내부 latestDate 계산
- fallback search 전에도 region recent items를 우선

#### 3) 마지막으로 보여준 카드/링크 상태 추가
필수 상태 예시:
- `lastShownCards`
- `lastShownLinks`
- `lastSelectedItem`
- `lastQuestionType`
- `lastRegion`
- `lastTargetDate`

#### 4) “뉴스형 요청” 전용 처리 강화
예:
- 오늘 미국 뉴스 3개
- 이번 주 중국 뉴스
- 4월 5일 기준 한국 뉴스

이런 요청은 일반 `searchCards()`보다
- `latestCards()`
- region/date aware selection
을 먼저 타야 한다.

#### 5) 별도 Translator 탭 재도입 금지
현재 구조에서 다시 Translator tab이 생기면 안 된다.

---

### P1 — 체감이 크게 좋아지는 것
#### 1) 뉴스 카드 액션 강화
특히 foreign / important card에 다음 액션을 붙일 수 있다.
- `한국어 요약`
- `왜 중요한지`
- `관련 카드`
- `AI 해설`

#### 2) AI 답변에 추적성 고정
번역/요약/설명 시 항상 유지:
- 원문 제목
- 원문 링크
- 날짜
- 출처
- 번역/요약/해설 라벨

#### 3) 답변 타입별 템플릿 고도화
- **요약형**: 핵심 3줄 + 관련 카드 링크
- **비교형**: 차이점 3개 + 한 줄 결론
- **정책형**: 다가오는 일정 + 지역 + last checked
- **뉴스형**: 기사 3개 + 왜 중요한지 + 후속 버튼

#### 4) follow-up suggestions의 문맥성 강화
예:
- 뉴스형 후: `오늘 기준으로 다시`, `미국만`, `중국만`, `링크 3개만`
- 정책형 후: `다가오는 일정만`, `한국/EU 비교`, `실무 영향만`
- 기술형 후: `쉽게 비유`, `LFP와 비교`, `왜 중요한지`

---

### P2 — 있으면 더 좋아지는 것
#### 1) source trust layer
외부 링크를 보여줄 때 출처 성격을 레이어링:
- 정부/규제기관
- 기업 IR/공시
- 주요 언론
- 2차 기사/블로그

#### 2) 웹툰과 뉴스 연결
웹툰 각 화 끝에
- 관련 뉴스 카드
- 관련 리서치 카드
를 연결하면 허브 전체 흐름이 좋아진다.

#### 3) Tracker 변화 감지
정적 상태판에서 한 단계 더 가려면
- NEW
- UPDATED
- DATE CHANGED
- MOVED TO ACTIVE
를 보여주는 편이 좋다.

#### 4) 저장 기능
- 카드 저장
- AI 답변 저장
- 나중에 보기
정도는 허브가 커질수록 효율적이다.

---

## 5. 구현 힌트

### A. region-aware latestCards 예시 방향
```js
function latestCards(cards, limit = 3, region = null, targetDate = null) {
  const pool = region ? cards.filter((c) => c.r === region) : cards;
  const ld = targetDate || latestDate(pool);

  let list = targetDate
    ? pool.filter((c) => c.d && String(c.d).startsWith(targetDate))
    : pool.filter((c) => c.d === ld);

  const rank = { t: 3, h: 2, m: 1, i: 0 };
  return list
    .sort((a, b) => {
      const r = (rank[b.s] || 0) - (rank[a.s] || 0);
      if (r !== 0) return r;
      return String(b.d).localeCompare(String(a.d));
    })
    .slice(0, limit);
}
```

### B. foreign card helper action 방향
```js
// wrong
// Korean card text -> foreign language translation

// better immediate path
const helperAction = {
  label: "한국어 요약",
  content: card.g || card.sub || card.T,
};
```

### C. last-selected context 예시
```js
const [lastContext, setLastContext] = useState({
  cards: [],
  links: [],
  selected: null,
  type: null,
  region: null,
  targetDate: null,
});
```

---

## 6. Acceptance Criteria

다음이 모두 충족되어야 QC 통과로 본다.

### 외국 뉴스 번역/설명
- foreign news card의 helper action이 더 이상 한국어 → 외국어 번역을 하지 않는다
- helper action은 한국어 설명/요약으로 동작하거나,
  진짜 원문 foreign → Korean translation으로 동작한다
- 사용자는 번역 기능이 거꾸로 동작한다고 느끼지 않는다

### 최신 뉴스
- “오늘 미국 뉴스 3개” 요청 시 2026.03.16 같은 오래된 카드가 우선으로 나오지 않는다
- region별 latest date 기준으로 카드가 선택된다
- 필요 시 internal recent cards → external search 순으로 fallback 한다

### 챗봇
- 마지막으로 보여준 카드/링크 문맥을 활용할 수 있다
- 후속 요청이 이전 기사/카드 기준으로 이어진다
- 2차/3차 퀵가이드가 문맥적으로 이어진다
- AI 답변은 링크/카드/출처 정보를 구조적으로 유지한다

### 정보 구조
- 별도 Translator 탭이 없다
- 번역/설명은 기존 News + AI 흐름 안에 통합되어 있다

---

## 7. 다음 작업 권장 순서
1. `🌐 번역` 버튼 제거/rename
2. `latestCards()` region-aware 수정
3. lastContext 상태 추가
4. news-type retrieval route 강화
5. follow-up suggestions 문맥형 개선
6. source trust layer / tracker diff / bookmark 등은 그 다음

---

## 결론
지금 필요한 것은 “새 기능을 계속 더하는 것”이 아니라,
이미 있는 기능이 **사용자 기대와 맞게 동작하도록 구조를 바로잡는 것**이다.

특히 중요한 포인트는 두 가지다.
- foreign news helper action은 지금 거꾸로 동작하고 있다
- 미국 최신 뉴스는 prompt 문제가 아니라 retrieval logic 문제다

즉,
- 번역 기능은 **뉴스 이해 보조 기능**으로 정리하고
- 챗봇은 **키워드 검색기**가 아니라 **문맥을 기억하는 뉴스 해석 도구**로 끌어올려야 한다.
