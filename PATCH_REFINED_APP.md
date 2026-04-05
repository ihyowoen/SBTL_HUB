# App.jsx refinement patch

Apply the following changes to `src/App.jsx`.

## 1) Replace `fmtDate`

```js
const fmtDate = (date) => {
  if (!date) return "-";
  const s = String(date).trim();
  const m = s.match(/^(\d{4})[.-](\d{2})[.-](\d{2})/);
  if (m) return `${m[1]}.${m[2]}.${m[3]}`;
  return s;
};
```

## 2) NewsDesk copy

Replace the title and body copy:

```jsx
<h2 style={{fontSize:22,fontWeight:900,color:t.tx,margin:"0 0 6px",lineHeight:1.25}}>
  날짜별 시그널 피드
</h2>
<p style={{fontSize:12,color:t.sub,margin:0,lineHeight:1.6}}>
  최신 카드부터 날짜 기준으로 정렬했습니다. 같은 날짜 안에서는 중요도가 높은 이슈를 먼저 보여줍니다.
</p>
```

Replace highlights label copy:

```jsx
<div style={{fontSize:10,color:t.sub,fontFamily:"'JetBrains Mono',monospace",marginBottom:4}}>
  EDITOR'S PICKS
</div>
<h3 style={{fontSize:18,fontWeight:900,color:t.tx,margin:0}}>
  오늘의 핵심 카드
</h3>
```

## 3) Tracker labels and schedule width

Replace `SCHEDULE` with `KEY DATES`.

Replace `UPCOMING EVENTS` with `WATCHLIST`.

Replace `UPDATED {updatedLabel}` with `LAST CHECKED {updatedLabel}`.

Replace the date cell style:

```jsx
<span
  style={{
    width:72,
    fontSize:10,
    fontWeight:700,
    color:t.sub,
    fontFamily:"'JetBrains Mono',monospace",
    flexShrink:0,
    lineHeight:1.35,
    whiteSpace:"normal",
    wordBreak:"keep-all"
  }}
>
  {ev.date}
</span>
```

Replace the event title style:

```jsx
<span style={{flex:1,fontSize:12,fontWeight:700,color:t.tx,lineHeight:1.45}}>{ev.title}</span>
```

## 4) Chat header subtitle

Replace the chatbot subtitle mapping with:

```js
chatbot:`배터리·ESS 이슈를 빠르게 찾고 정리해주는 AI 데스크`
```

## 5) Chat initial message

Replace the initial message with:

```js
const [msgs, setMsgs] = useState([
  {
    role: "assistant",
    content:
      `안녕, 강차장이야. 🔋\n\n` +
      `궁금한 주제를 편하게 보내줘.\n` +
      `핵심부터 짧게 정리해주고,\n` +
      `관련 카드나 최근 이슈도 같이 찾아줄게.`,
    tier: null,
  },
]);
```

## 6) Quick buttons

Replace the quick menu array with:

```js
const qQ = [
  "오늘 핵심 뉴스 3개",
  "LFP 리스크 한 번에",
  "한국 정책 일정 뭐 있어?",
  "미국 FEOC 쉽게 설명해줘",
  "이번주 ESS 시그널 요약",
  "전고체 어디까지 왔어?",
  "중국 가격 흐름 체크",
  "먼저 봐야 할 카드 추천"
];
```

Replace the quick button container with a 2-column grid.

Replace the button style with:

```jsx
style={{
  background: dark ? "#1A2333" : "#FFFFFF",
  border: `1px solid ${t.brd}`,
  borderRadius: 999,
  padding: "8px 12px",
  fontSize: 12,
  color: t.tx,
  cursor: "pointer",
  fontFamily: "'Pretendard', sans-serif",
  fontWeight: 600
}}
```

## 7) Chat bubble style

Replace the message wrapper width with:

```jsx
<div style={{maxWidth:"88%"}}>
```

Replace the bubble style with:

```jsx
<div
  style={{
    padding: "11px 14px",
    fontSize: 13,
    lineHeight: 1.6,
    whiteSpace: "pre-wrap",
    wordBreak: "keep-all",
    borderRadius: m.role === "user" ? "18px 18px 6px 18px" : "18px 18px 18px 6px",
    background: m.role === "user" ? "#4C8DFF" : (dark ? "#1A2333" : "#FFFFFF"),
    color: m.role === "user" ? "#fff" : t.tx,
    border: m.role === "user" ? "none" : `1px solid ${t.brd}`,
    fontFamily: "'Pretendard', sans-serif"
  }}
>
```

## 8) Hide internal tier labels

Remove the small tier label under each assistant message.

## 9) Loading text

Replace `{mode}...` with `찾아보는 중...`.

## 10) Input placeholder

Replace the placeholder with:

```jsx
placeholder="궁금한 주제를 입력해줘"
```
