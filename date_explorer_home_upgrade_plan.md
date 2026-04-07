# SBTL HUB — 1차 구현안
## Date Explorer + Home Upgrade

목표:
- `NEWS` 탭에서 날짜 기준으로 빠르게 찾기
- `HOME`을 소개 화면이 아니라 탐색 허브로 바꾸기
- 너무 무거운 월간 캘린더는 넣지 않고, 모바일 친화적인 날짜 탐색 UX부터 구현하기

---

## 이번 라운드에 넣는 것

### 1) App 상태 추가
`App()`에 아래 상태를 추가한다.

```jsx
const [selectedNewsDate, setSelectedNewsDate] = useState("");
```

의미:
- Home에서 날짜 선택 → News로 이동할 때 공통으로 쓰는 상태
- News 내부에서도 날짜 선택/해제 시 이 상태를 공유

---

### 2) 날짜 유틸 추가
`latestDate(cards)` 아래에 추가.

```jsx
function normalizeDateInput(value) {
  if (!value) return "";
  return String(value).trim().replace(/-/g, ".");
}

function toInputDate(value) {
  const f = fmtDate(value);
  if (!f || f === "-") return "";
  return f.replace(/\./g, "-");
}

function getRecentDates(cards, limit = 10) {
  return [...new Set(cards.map((c) => fmtDate(c?.d)).filter(Boolean).filter((d) => d !== "-"))]
    .sort((a, b) => String(b).localeCompare(String(a)))
    .slice(0, limit);
}

function countCardsByDate(cards, date) {
  const target = fmtDate(date);
  return cards.filter((c) => fmtDate(c?.d) === target).length;
}

function countSignalsByDate(cards, date, signal) {
  const target = fmtDate(date);
  return cards.filter((c) => fmtDate(c?.d) === target && c?.s === signal).length;
}

function countRegionsByDate(cards, date) {
  const target = fmtDate(date);
  return new Set(cards.filter((c) => fmtDate(c?.d) === target).map((c) => c?.r).filter(Boolean)).size;
}
```

---

### 3) Home 컴포넌트 고도화
현재 시그니처:

```jsx
function Home({ kb, tracker, onNav, dark })
```

아래로 변경:

```jsx
function Home({ kb, tracker, onNav, onPickDate, selectedNewsDate, dark })
```

`Home` 내부에 추가:

```jsx
const recentDates = getRecentDates(kb.cards, 7);
const focusDate = selectedNewsDate || kstToday();
const todayCardCount = countCardsByDate(kb.cards, focusDate);
const todayTopCount = countSignalsByDate(kb.cards, focusDate, "t");
const todayHighCount = countSignalsByDate(kb.cards, focusDate, "h");
const todayRegionCount = countRegionsByDate(kb.cards, focusDate);
```

### 3-1) Today Snapshot 카드 추가
Hero 아래, 기존 2개 타일 전에 넣는 걸 추천.

```jsx
<div style={{ background: t.card2, borderRadius: 14, padding: "14px 16px", border: `1px solid ${t.brd}` }}>
  <div style={{ fontSize: 10, color: t.sub, fontFamily: "'JetBrains Mono',monospace", marginBottom: 4 }}>TODAY SNAPSHOT</div>
  <div style={{ fontSize: 18, fontWeight: 900, color: t.tx }}>기준 날짜 · {fmtDate(focusDate)}</div>
  <div style={{ display: "grid", gridTemplateColumns: "repeat(4,1fr)", gap: 8, marginTop: 12 }}>
    {[
      { label: "CARDS", value: todayCardCount },
      { label: "TOP", value: todayTopCount },
      { label: "HIGH", value: todayHighCount },
      { label: "REGIONS", value: todayRegionCount },
    ].map((item) => (
      <div key={item.label} style={{ background: dark ? "rgba(10,14,20,0.55)" : "rgba(255,255,255,0.88)", border: `1px solid ${t.brd}`, borderRadius: 12, padding: "10px 8px", textAlign: "center" }}>
        <div style={{ fontSize: 16, fontWeight: 900, color: t.tx, fontFamily: "'JetBrains Mono',monospace" }}>{item.value}</div>
        <div style={{ fontSize: 9, color: t.sub, fontFamily: "'JetBrains Mono',monospace", marginTop: 4 }}>{item.label}</div>
      </div>
    ))}
  </div>
  <div style={{ display: "flex", gap: 8, marginTop: 12 }}>
    <button
      onClick={() => {
        onPickDate(focusDate);
        onNav("news");
      }}
      style={{ flex: 1, border: "none", borderRadius: 10, padding: "10px 12px", background: t.cyan, color: "#000", fontSize: 11, fontWeight: 900, cursor: "pointer", fontFamily: "'JetBrains Mono',monospace" }}
    >
      이 날짜 뉴스 보기 →
    </button>
    <button
      onClick={() => {
        onPickDate(kstToday());
        onNav("news");
      }}
      style={{ flex: 1, border: `1px solid ${t.brd}`, borderRadius: 10, padding: "10px 12px", background: "transparent", color: t.tx, fontSize: 11, fontWeight: 900, cursor: "pointer", fontFamily: "'JetBrains Mono',monospace" }}
    >
      오늘 기준 →
    </button>
  </div>
</div>
```

### 3-2) Date Explorer 카드 추가
`Today Snapshot` 바로 아래 추천.

```jsx
<div style={{ background: t.card2, borderRadius: 14, padding: "14px 16px", border: `1px solid ${t.brd}` }}>
  <div style={{ fontSize: 10, color: t.sub, fontFamily: "'JetBrains Mono',monospace", marginBottom: 4 }}>DATE EXPLORER</div>
  <div style={{ fontSize: 18, fontWeight: 900, color: t.tx }}>날짜 기준으로 바로 찾기</div>
  <div style={{ fontSize: 11, color: t.sub, lineHeight: 1.6, marginTop: 6 }}>최근 날짜를 누르거나 원하는 날짜를 선택해서 해당 일자의 카드만 빠르게 볼 수 있습니다.</div>
  <div style={{ display: "flex", gap: 6, overflowX: "auto", paddingBottom: 4, marginTop: 12 }}>
    {recentDates.map((date) => {
      const active = fmtDate(selectedNewsDate || "") === fmtDate(date);
      return (
        <button
          key={date}
          onClick={() => {
            onPickDate(date);
            onNav("news");
          }}
          style={{
            background: active ? t.cyan : t.card,
            color: active ? "#000" : t.tx,
            border: `1px solid ${active ? "transparent" : t.brd}`,
            borderRadius: 999,
            padding: "8px 12px",
            fontSize: 10,
            fontWeight: 800,
            cursor: "pointer",
            whiteSpace: "nowrap",
            fontFamily: "'JetBrains Mono',monospace",
          }}
        >
          {shortDate(date)} · {countCardsByDate(kb.cards, date)}
        </button>
      );
    })}
  </div>
</div>
```

---

### 4) NewsDesk 날짜 탐색 추가
현재 시그니처:

```jsx
function NewsDesk({ kb, dark })
```

변경:

```jsx
function NewsDesk({ kb, selectedDate, onSelectDate, dark })
```

`NewsDesk` 내부 상단 state 추가:

```jsx
const dateInputRef = useRef(null);
const recentDates = getRecentDates(kb.cards, 12);
```

현재 필터 로직 앞쪽을 이렇게 바꾼다.

```jsx
let cards = filter === "all"
  ? kb.cards
  : filter === "top"
    ? kb.cards.filter((c) => c.s === "t")
    : filter === "high"
      ? kb.cards.filter((c) => c.s === "h")
      : kb.cards.filter((c) => c.r === filter);

if (selectedDate) {
  cards = cards.filter((c) => fmtDate(c.d) === fmtDate(selectedDate));
}

if (search) {
  const sw = search.toLowerCase();
  cards = cards.filter((c) =>
    String(c.T || "").toLowerCase().includes(sw) ||
    String(c.sub || "").toLowerCase().includes(sw) ||
    String(c.g || "").toLowerCase().includes(sw)
  );
}
```

### 4-1) 날짜 탐색 바 추가
`Editor’s Picks` 아래, 검색창 위 추천.

```jsx
<div style={{ background: t.card2, borderRadius: 14, padding: 14, border: `1px solid ${t.brd}` }}>
  <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", gap: 8, marginBottom: 10 }}>
    <div>
      <div style={{ fontSize: 10, color: t.sub, fontFamily: "'JetBrains Mono',monospace", marginBottom: 4 }}>DATE FINDER</div>
      <div style={{ fontSize: 16, fontWeight: 900, color: t.tx }}>
        {selectedDate ? `${fmtDate(selectedDate)} 카드` : "전체 날짜 보기"}
      </div>
    </div>
    <div style={{ display: "flex", gap: 6 }}>
      <button
        onClick={() => onSelectDate(kstToday())}
        style={{ border: `1px solid ${t.brd}`, background: "transparent", color: t.tx, borderRadius: 8, padding: "7px 10px", fontSize: 10, fontWeight: 800, cursor: "pointer", fontFamily: "'JetBrains Mono',monospace" }}
      >
        오늘
      </button>
      <button
        onClick={() => dateInputRef.current?.showPicker ? dateInputRef.current.showPicker() : dateInputRef.current?.click()}
        style={{ border: `1px solid ${t.brd}`, background: "transparent", color: t.tx, borderRadius: 8, padding: "7px 10px", fontSize: 10, fontWeight: 800, cursor: "pointer", fontFamily: "'JetBrains Mono',monospace" }}
      >
        📅 날짜 선택
      </button>
      {selectedDate && (
        <button
          onClick={() => onSelectDate("")}
          style={{ border: `1px solid ${t.brd}`, background: "transparent", color: t.sub, borderRadius: 8, padding: "7px 10px", fontSize: 10, fontWeight: 800, cursor: "pointer", fontFamily: "'JetBrains Mono',monospace" }}
        >
          전체
        </button>
      )}
    </div>
  </div>

  <input
    ref={dateInputRef}
    type="date"
    value={toInputDate(selectedDate)}
    onChange={(e) => onSelectDate(normalizeDateInput(e.target.value))}
    style={{ position: "absolute", opacity: 0, pointerEvents: "none", width: 0, height: 0 }}
  />

  <div style={{ display: "flex", gap: 6, overflowX: "auto", paddingBottom: 4 }}>
    {recentDates.map((date) => {
      const active = fmtDate(selectedDate || "") === fmtDate(date);
      return (
        <button
          key={date}
          onClick={() => onSelectDate(date)}
          style={{
            background: active ? t.cyan : t.card,
            color: active ? "#000" : t.tx,
            border: `1px solid ${active ? "transparent" : t.brd}`,
            borderRadius: 999,
            padding: "7px 11px",
            fontSize: 10,
            fontWeight: 800,
            cursor: "pointer",
            whiteSpace: "nowrap",
            fontFamily: "'JetBrains Mono',monospace",
          }}
        >
          {shortDate(date)} · {countCardsByDate(kb.cards, date)}
        </button>
      );
    })}
  </div>
</div>
```

---

### 5) App에서 prop 연결
`App()`에서 `selectedNewsDate` 상태 추가 후, 렌더 부분 교체.

```jsx
const [selectedNewsDate, setSelectedNewsDate] = useState("");
```

렌더 교체:

```jsx
{tab === "all" && (
  <div style={{ paddingTop: 10 }}>
    <Home
      kb={kb}
      tracker={tracker}
      onNav={setTab}
      onPickDate={setSelectedNewsDate}
      selectedNewsDate={selectedNewsDate}
      dark={dark}
    />
  </div>
)}

{tab === "news" && (
  <NewsDesk
    kb={kb}
    selectedDate={selectedNewsDate}
    onSelectDate={setSelectedNewsDate}
    dark={dark}
  />
)}
```

---

## 이 라운드에서 기대되는 UX 변화

- 홈에서 `오늘 / 특정 날짜` 기준으로 바로 NEWS 진입 가능
- NEWS에서 날짜 선택/최근 날짜칩으로 원하는 날 바로 찾기 가능
- 긴 리스트를 무한 스크롤로만 뒤지는 불편 감소
- 홈이 소개 화면에서 탐색 허브로 진화

---

## 이번 라운드에서 일부러 안 넣는 것

- 월간 캘린더 그리드
- 과도한 홈 리디자인
- 날짜 + 지역 + 시그널 + 검색의 복합 고급 필터

이유:
- 첫 구현에서 복잡도를 너무 올리면 모바일 UX와 유지보수 난도가 동시에 올라감
- 지금 필요한 것은 “더 많은 기능”이 아니라 “더 빠른 진입”임

---

## 브랜치 / 커밋 추천

```bash
git switch -c add-date-explorer-and-home-upgrade-20260406
```

```bash
git commit -m "feat: add date explorer and upgrade home navigation"
```

