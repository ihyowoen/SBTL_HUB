# App.jsx Patch Spec — 배터리 상담소 Phase 1

**대상 파일:** `src/App.jsx`
**최소 침투 원칙:** Home/NewsDesk/Tracker/WebtoonLibrary/Header/Nav는 건드리지 않음.
**변경 범위:** import 2개 추가, ReceiptBubble 신규, ChatBot 전체 교체, AppContent 4개 지점 수정, StoryNewsItem 호출 지점 3곳 prop 치환.

---

## Section 1 — import 추가

### 위치
파일 최상단 기존 import 바로 아래.

### Before
```jsx
import { useEffect, useMemo, useRef, useState, Component } from "react";
import StoryNewsItem from "./story/StoryNewsItem";
```

### After
```jsx
import { useEffect, useMemo, useRef, useState, Component } from "react";
import StoryNewsItem from "./story/StoryNewsItem";
import { buildCardConsultContext } from "./story/buildCardConsultContext";
import { getCardId } from "./story/normalizeCard";
import {
  createConsultation,
  appendMessage,
  getAllCardConsultationSummaries,
  getRecentOpenerIds,
} from "./consultation/consultationStorage";
```

---

## Section 2 — ReceiptBubble 컴포넌트 신규

### 위치
`ChatBot` function 바로 **위**에 삽입. 기존 `NewsItem` function 끝 이후.

### Insert (신규)
```jsx
// 배터리 상담소 — 접수증 A안 (미니카드 + 받음 stamp)
function ReceiptBubble({ meta, openedAt, dark }) {
  const t = T(dark);
  const d = openedAt ? new Date(openedAt) : null;
  const dateLabel = d && !isNaN(d.getTime()) ? `${d.getMonth() + 1}/${d.getDate()}` : "";
  const metaParts = [];
  if (meta?.region) metaParts.push(meta.region);
  const sigShort = (meta?.signal || "i").toString().slice(0, 1).toLowerCase();
  metaParts.push((SIG_L[sigShort] || "INFO"));
  if (meta?.date) metaParts.push(fmtDate(meta.date));
  const metaLine = metaParts.join(" · ");

  return (
    <div
      role="note"
      aria-label="상담 접수증"
      style={{
        margin: "10px auto",
        maxWidth: "92%",
        padding: "10px 14px",
        background: dark ? "rgba(88,166,255,0.07)" : "rgba(88,166,255,0.05)",
        border: `1px dashed ${t.cyan}`,
        borderRadius: 10,
      }}
    >
      <div style={{
        fontSize: 10, color: t.cyan, fontWeight: 800, marginBottom: 6,
        fontFamily: "'JetBrains Mono',monospace",
        display: "flex", alignItems: "center", gap: 6,
      }}>
        <span aria-hidden="true">📥</span>
        <span>받음{dateLabel ? ` · ${dateLabel}` : ""}</span>
      </div>
      <div style={{
        fontSize: 13, color: t.tx, fontWeight: 700, lineHeight: 1.4, marginBottom: 4,
        fontFamily: "'Pretendard',sans-serif",
      }}>
        {meta?.title || "(제목 없음)"}
      </div>
      {metaLine && (
        <div style={{
          fontSize: 9, color: t.sub, fontWeight: 700,
          fontFamily: "'JetBrains Mono',monospace",
        }}>
          {metaLine}
        </div>
      )}
    </div>
  );
}
```

---

## Section 3 — ChatBot 전체 교체

### 위치
기존 `function ChatBot({ dark, initialPrompt = "", initialPromptNonce = 0 }) { ... }` 전체.

### After (전체 교체)
```jsx
function ChatBot({ dark, initialConsultation = null, initialConsultationNonce = 0 }) {
  const t = T(dark);
  const [msgs, setMsgs] = useState([{ role: "assistant", content: "안녕, 강차장이야. 🔋\n\n궁금한 주제를 편하게 보내줘.\n핵심부터 짧게 정리해주고,\n관련 카드나 최근 이슈도 같이 찾아줄게." }]);
  const [input, setInput] = useState("");
  // loadingMode: 'none' | 'typing_normal' | 'typing_consult'
  const [loadingMode, setLoadingMode] = useState("none");
  const [searchMode, setSearchMode] = useState("internal");
  const [extQuery, setExtQuery] = useState("");
  const endRef = useRef(null);
  // ChatContext Protocol (Phase 2)
  const chatCtxRef = useRef({ last_turn: null, root_turn: null, selected_item_id: null, region: null, date: null });
  // 현재 active consultation — 후속 유저 메시지는 이 consultation followup으로 처리
  const currentConsultRef = useRef(null);

  const isLoading = loadingMode !== "none";

  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [msgs, loadingMode]);

  const toUiMessage = (data) => ({
    role: "assistant",
    content: data?.answer || "응답을 생성하지 못했어.",
    sourceBadge: ({ external: "external", hybrid: "hybrid", internal: "internal" }[data?.source_mode] || "internal"),
    cards: Array.isArray(data?.cards) ? data.cards : [],
    braveLinks: Array.isArray(data?.external_links) ? data.external_links : [],
    suggestions: Array.isArray(data?.suggestions) ? data.suggestions : [],
  });

  const updateContextFromResponse = (data) => {
    const nc = data?.next_context || {};
    chatCtxRef.current = {
      last_turn: nc.last_turn || null,
      root_turn: nc.root_turn || chatCtxRef.current.root_turn || null,
      selected_item_id: null,
      region: nc.last_turn?.scope?.region || chatCtxRef.current.region,
      date: nc.last_turn?.scope?.date || chatCtxRef.current.date,
    };
  };

  // typing ceremony — min 500ms 보장, max 2s cap
  const ceremonyWait = async (t0, minMs = 500, maxMs = 2000) => {
    const elapsed = Date.now() - t0;
    if (elapsed >= maxMs) return;
    const wait = Math.max(0, minMs - elapsed);
    if (wait > 0) await new Promise((r) => setTimeout(r, wait));
  };

  // ─── 일반 chat POST ──────────────────────────────────────────────────
  const postChat = async (body) => {
    const res = await fetch("/api/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      return {
        answer: err?.answer || "요청 처리 중 오류가 발생했어.",
        answer_type: "general",
        source_mode: "internal",
        confidence: 0,
        cards: [],
        external_links: [],
        suggestions: [
          { label: "오늘 핵심 카드", hint_action: "new_query", hint_topic: "news" },
        ],
        next_context: { last_turn: null, root_turn: chatCtxRef.current.root_turn || null },
      };
    }
    return res.json();
  };

  const sendToChatApi = async (txt, mode = "internal", hint = null) => {
    const body = {
      message: mode === "external" ? `${txt} 외부 기사 링크 중심으로 찾아줘` : txt,
      context: chatCtxRef.current,
    };
    if (hint && (hint.hint_action || hint.hint_topic)) {
      body.hint = {
        action: hint.hint_action || undefined,
        topic: hint.hint_topic || undefined,
      };
    }
    return postChat(body);
  };

  // ─── Consultation opener (initialConsultation seed 진입 시) ──────────
  const startConsultation = async (init) => {
    if (!init?.cardContext?.card) return;
    currentConsultRef.current = {
      id: init.consultationId,
      cardContext: init.cardContext,
    };

    // 1) 접수증 push (유저 풍선 아님)
    const receiptMsg = {
      role: "receipt",
      card_meta: init.card_meta,
      opened_at: init.opened_at,
    };
    setMsgs((prev) => [...prev, receiptMsg]);

    // 2) opener LLM 호출 + typing ceremony
    setLoadingMode("typing_consult");
    const t0 = Date.now();
    try {
      const data = await postChat({
        consultation: init.cardContext,
        is_opener: true,
        ticket_id: init.consultationId,
        context: chatCtxRef.current,
      });
      await ceremonyWait(t0);
      updateContextFromResponse(data);
      const uiMsg = toUiMessage(data);
      setMsgs((prev) => [...prev, uiMsg]);

      if (init.consultationId) {
        appendMessage(init.consultationId, {
          role: "assistant",
          content: data?.answer || "",
          opener: true,
        });
      }
    } catch {
      setMsgs((prev) => [...prev, {
        role: "assistant",
        content: "강차장 잠시 자리 비웠어. 잠깐 뒤에 다시 제출해줘.",
        suggestions: [{ label: "오늘 핵심 카드", hint_action: "new_query", hint_topic: "news" }],
      }]);
    } finally {
      setLoadingMode("none");
    }
  };

  // ─── Consultation followup (유저 메시지 after opener) ────────────────
  const sendConsultFollowup = async (txt, consult) => {
    setMsgs((prev) => [...prev, { role: "user", content: txt }]);
    if (consult.id) appendMessage(consult.id, { role: "user", content: txt });

    setLoadingMode("typing_consult");
    const t0 = Date.now();
    try {
      const data = await postChat({
        message: txt,
        consultation: consult.cardContext,
        is_opener: false,
        ticket_id: consult.id,
        context: chatCtxRef.current,
      });
      await ceremonyWait(t0);
      updateContextFromResponse(data);
      setMsgs((prev) => [...prev, toUiMessage(data)]);
      if (consult.id) appendMessage(consult.id, { role: "assistant", content: data?.answer || "" });
    } catch {
      setMsgs((prev) => [...prev, {
        role: "assistant",
        content: "강차장 잠시 자리 비웠어. 잠깐 뒤에 다시.",
      }]);
    } finally {
      setLoadingMode("none");
    }
  };

  // ─── 일반 chat (기존 로직 유지, loadingMode만 전환) ──────────────────
  const sendWithText = async (rawText, hint = null) => {
    const txt = String(rawText || "").trim();
    if (!txt || isLoading) return;

    setInput("");

    // 현재 active consultation이 있으면 followup 경로로
    const consult = currentConsultRef.current;
    if (consult) {
      await sendConsultFollowup(txt, consult);
      return;
    }

    // 일반 chat
    setMsgs((prev) => [...prev, { role: "user", content: txt }]);
    setLoadingMode("typing_normal");
    try {
      const data = await sendToChatApi(txt, "internal", hint);
      updateContextFromResponse(data);
      setMsgs((prev) => [...prev, toUiMessage(data)]);
    } catch {
      setMsgs((prev) => [...prev, {
        role: "assistant",
        content: "채팅 응답 중 네트워크 오류가 발생했어.",
        suggestions: [
          { label: "오늘 핵심 카드", hint_action: "new_query", hint_topic: "news" },
          { label: "관련 카드 더 보여줘", hint_action: "follow_up" },
        ],
      }]);
    } finally {
      setLoadingMode("none");
    }
  };

  // consultation seed 변경 감지 → opener 시작
  useEffect(() => {
    if (!initialConsultation || !initialConsultationNonce) return;
    void startConsultation(initialConsultation);
     
  }, [initialConsultation, initialConsultationNonce]);

  const sendExternal = async (rawText, hint = null) => {
    const txt = String(rawText || "").trim();
    if (!txt || isLoading) return;

    setLoadingMode("typing_normal");
    setExtQuery("");
    setMsgs((prev) => [...prev, { role: "user", content: `🔗 외부 검색: ${txt}` }]);

    try {
      const data = await sendToChatApi(txt, "external", hint);
      updateContextFromResponse(data);
      setMsgs((prev) => [...prev, toUiMessage(data)]);
    } catch {
      setMsgs((prev) => [...prev, {
        role: "assistant",
        content: "외부 검색 응답 중 네트워크 오류가 발생했어.",
        suggestions: [{ label: "내부 카드로 검색", hint_action: "new_query" }],
      }]);
    } finally {
      setLoadingMode("none");
    }
  };

  const markCardSelected = (card) => {
    const id = card?.url || card?.title || null;
    if (!id) return;
    chatCtxRef.current = { ...chatCtxRef.current, selected_item_id: id };
  };

  const runSuggestion = (suggestion) => {
    const label = typeof suggestion === "string" ? suggestion : (suggestion?.label || "");
    const hint = typeof suggestion === "object" ? suggestion : null;
    const map = {
      "오늘 핵심 카드": "오늘 뉴스 3개",
      "오늘의 시그널 TOP": "오늘 TOP 시그널 카드 보여줘",
      "외부 기사 링크 검색": "실시간 배터리 ESS 기사 검색해줘",
      "오늘 핵심 뉴스 3개": "오늘 뉴스 3개",
      "오늘 뉴스 3개": "오늘 뉴스 3개",
      "요약해서 다시 정리": "방금 답변을 3줄로 다시 요약해줘",
      "카드에서도 찾아봐": "방금 주제와 관련된 카드도 같이 찾아줘",
      "조금 더 쉽게 설명해줘": "방금 답변을 더 쉽게 설명해줘",
      "관련 카드 더 보여줘": "방금 주제와 관련된 카드 더 보여줘",
      "정책 일정만 따로 정리해줘": "방금 주제와 관련된 정책 일정만 따로 정리해줘",
      "한국 뉴스만": "오늘 한국 뉴스 3개",
      "미국 뉴스만": "오늘 미국 뉴스 3개",
      "다가오는 일정만": "다가오는 정책 일정만 정리해줘",
      "한국/EU 비교": "한국과 EU 정책을 비교해줘",
      "실무 영향만 요약": "실무 영향만 요약해줘",
      "한 줄 결론만": "한 줄 결론만 말해줘",
      "오늘 기준으로 다시": "오늘 기준 뉴스 3개",
      "미국만 따로": "미국 뉴스 3개",
      "중국만 따로": "중국 뉴스 3개",
      "쉽게 비유해서 설명": "방금 주제를 쉽게 비유해서 설명해줘",
      "LFP랑 비교": "방금 주제를 LFP와 비교해줘",
      "왜 중요한지 한 줄로": "방금 주제가 왜 중요한지 한 줄로 설명해줘",
    };
    const next = map[label] || label;
    const isExternalLabel = label === "외부 기사 링크 검색" || label.includes("외부 검색");
    if (searchMode === "external" || isExternalLabel) {
      void sendExternal(next, hint);
      return;
    }
    void sendWithText(next, hint);
  };

  return (
    <div style={{ display: "flex", flexDirection: "column", height: "calc(100vh - 190px)" }}>
      <div role="log" aria-live="polite" aria-atomic="false" aria-label="대화 내역" style={{ flex: 1, overflowY: "auto", padding: "12px 14px 8px" }}>
        {msgs.length <= 1 && (
          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 8, marginTop: 6, marginBottom: 12 }}>
            {quickPrimary.map((q) => (
              <button key={q} onClick={() => runSuggestion(q)} style={{ background: dark ? "#1A2333" : "#FFFFFF", border: `1px solid ${t.brd}`, borderRadius: 999, padding: "12px 16px", minHeight: "44px", fontSize: 12, color: t.tx, cursor: "pointer", fontFamily: "'Pretendard',sans-serif", fontWeight: 600, textAlign: "left" }}>{q}</button>
            ))}
          </div>
        )}

        {msgs.map((m, i) => {
          // 접수증 (receipt) 렌더 — user/assistant 풍선 아님
          if (m.role === "receipt") {
            return <ReceiptBubble key={`receipt-${i}`} meta={m.card_meta} openedAt={m.opened_at} dark={dark} />;
          }
          return (
            <div key={i} role="article" aria-label={m.role === "user" ? "내 질문" : "AI 답변"} style={{ display: "flex", flexDirection: "column", alignItems: m.role === "user" ? "flex-end" : "flex-start", marginBottom: 10 }}>
              <div style={{ display: "flex", justifyContent: m.role === "user" ? "flex-end" : "flex-start", width: "100%" }}>
                {m.role === "assistant" && <img src="/data/kang.png" alt="강차장" style={{ width: 28, height: 28, borderRadius: 14, marginRight: 7, flexShrink: 0, marginTop: 2, border: "2px solid #2a1a40" }} />}
                <div style={{ maxWidth: "88%" }}>
                  <div style={{ padding: "11px 14px", fontSize: 13, lineHeight: 1.6, whiteSpace: "pre-wrap", wordBreak: "keep-all", borderRadius: m.role === "user" ? "18px 18px 6px 18px" : "18px 18px 18px 6px", background: m.role === "user" ? "#4C8DFF" : (dark ? "#1A2333" : "#FFFFFF"), color: m.role === "user" ? "#fff" : t.tx, border: m.role === "user" ? "none" : `1px solid ${t.brd}`, fontFamily: "'Pretendard', sans-serif" }}>
                    {m.sourceBadge === "internal" && (
                      <span style={{ display: "inline-block", fontSize: 10, fontWeight: 800, color: "#58A6FF", background: dark ? "rgba(88,166,255,0.14)" : "rgba(45,90,142,0.10)", padding: "3px 8px", borderRadius: 999, marginBottom: 6, fontFamily: "'JetBrains Mono',monospace" }}>
                        📋 내부 카드 기반
                      </span>
                    )}
                    {m.sourceBadge === "external" && (
                      <span style={{ display: "inline-block", fontSize: 10, fontWeight: 800, color: "#D29922", background: dark ? "rgba(210,153,34,0.14)" : "rgba(210,153,34,0.10)", padding: "3px 8px", borderRadius: 999, marginBottom: 6, fontFamily: "'JetBrains Mono',monospace" }}>
                        🔗 외부 기사 링크
                      </span>
                    )}
                    {m.sourceBadge === "hybrid" && (
                      <span style={{ display: "inline-block", fontSize: 10, fontWeight: 800, color: "#A855F7", background: dark ? "rgba(168,85,247,0.14)" : "rgba(168,85,247,0.10)", padding: "3px 8px", borderRadius: 999, marginBottom: 6, fontFamily: "'JetBrains Mono',monospace" }}>
                        🔀 내부+외부 근거
                      </span>
                    )}
                    {m.sourceBadge ? <div>{m.content}</div> : m.content}
                  </div>
                  {m.braveLinks?.map((link, j) => (
                    <a key={`brave-${j}`} href={link.url} target="_blank" rel="noopener noreferrer" aria-label={`Open external article: ${link.title}`} style={{ display: "block", background: dark ? "#1A1E2A" : "#FFFBF0", borderRadius: 10, padding: "10px 12px", marginTop: 6, cursor: "pointer", border: `1px solid ${dark ? "rgba(210,153,34,0.25)" : "rgba(210,153,34,0.2)"}`, textDecoration: "none" }}>
                      <div style={{ fontSize: 12, fontWeight: 700, color: t.tx, lineHeight: 1.4 }}>{link.title}</div>
                      {link.description && <div style={{ fontSize: 11, color: t.sub, marginTop: 3, lineHeight: 1.45 }}>{link.description.slice(0, 120)}{link.description.length > 120 ? "..." : ""}</div>}
                      <div style={{ fontSize: 10, color: "#D29922", marginTop: 4, fontWeight: 700, fontFamily: "'JetBrains Mono',monospace" }}>🔗 외부 기사 ↗</div>
                    </a>
                  ))}
                  {m.cards?.map((card, j) => {
                    const cardStyle = { display: "block", background: dark ? "#151B26" : "#f8f9fc", borderRadius: 10, padding: "10px 12px", marginTop: 6, cursor: card.url ? "pointer" : "default", border: `1px solid ${t.brd}`, textDecoration: "none" };
                    const cardContent = (<>
                      <div style={{ fontSize: 12, fontWeight: 700, color: t.tx }}>{SIG_L[card.signal] || "INFO"} {card.title}</div>
                      {card.subtitle && <div style={{ fontSize: 11, color: t.sub, marginTop: 3 }}>{card.subtitle}</div>}
                      {card.gist && <div style={{ fontSize: 10, color: t.cyan, marginTop: 4, lineHeight: 1.5, opacity: 0.85 }}>💡 {card.gist}</div>}
                      <div style={{ fontSize: 10, color: t.sub, marginTop: 4, fontFamily: "'JetBrains Mono',monospace" }}>{fmtDate(card.date)} · {card.region} · {card.source || "source"}</div>
                      {card.url && <div style={{ fontSize: 10, color: t.cyan, marginTop: 4, fontWeight: 700 }}>→ 원문 보기 ↗</div>}
                    </>);
                    return card.url
                      ? <a key={j} href={card.url} target="_blank" rel="noopener noreferrer" aria-label={`Open article: ${card.title}`} onClick={() => markCardSelected(card)} style={cardStyle}>{cardContent}</a>
                      : <div key={j} style={cardStyle} onClick={() => markCardSelected(card)}>{cardContent}</div>;
                  })}
                </div>
              </div>
              {m.role === "assistant" && m.suggestions?.length > 0 && (
                <div style={{ display: "flex", gap: 6, flexWrap: "wrap", marginTop: 8, marginBottom: 4, paddingLeft: 35 }}>
                  {m.suggestions.map((s) => (
                    <button key={s.label} onClick={() => runSuggestion(s)} style={{ background: dark ? "#1A2333" : "#fff", border: `1px solid ${t.brd}`, borderRadius: 999, padding: "10px 16px", minHeight: "44px", fontSize: 11, color: t.cyan, cursor: "pointer", fontFamily: "'Pretendard',sans-serif", fontWeight: 600 }}>{s.label}</button>
                  ))}
                </div>
              )}
            </div>
          );
        })}

        {isLoading && (
          <div role="status" aria-live="polite" aria-atomic="true" style={{ display: "flex", gap: 7, marginBottom: 10 }}>
            <img src="/data/kang.png" alt="강차장" style={{ width: 28, height: 28, borderRadius: 14, flexShrink: 0, border: "2px solid #2a1a40" }} />
            <div style={{ padding: "10px 14px", borderRadius: "18px 18px 18px 6px", background: dark ? "#1A2333" : "#FFFFFF", border: `1px solid ${t.brd}`, fontSize: 12, color: t.sub }}>
              {loadingMode === "typing_consult" ? "검토 중..." : "찾아보는 중..."}
            </div>
          </div>
        )}
        <div ref={endRef} />
      </div>
      <div style={{ padding: "8px 12px 14px", background: "#0A0E14", borderTop: `1px solid ${t.brd}` }}>
        <div style={{ display: "flex", gap: 0, marginBottom: 8, background: dark ? "#151B26" : "#f0f0f5", borderRadius: 8, padding: 2 }}>
          <button onClick={() => setSearchMode("internal")} style={{ flex: 1, padding: "6px 0", borderRadius: 6, border: "none", background: searchMode === "internal" ? (dark ? "#1A2333" : "#fff") : "transparent", color: searchMode === "internal" ? "#58A6FF" : t.sub, fontSize: 11, fontWeight: 700, cursor: "pointer", fontFamily: "'JetBrains Mono',monospace", boxShadow: searchMode === "internal" ? "0 1px 3px rgba(0,0,0,0.15)" : "none", transition: "all 0.15s" }}>📋 내부 카드</button>
          <button onClick={() => setSearchMode("external")} style={{ flex: 1, padding: "6px 0", borderRadius: 6, border: "none", background: searchMode === "external" ? (dark ? "#1A2333" : "#fff") : "transparent", color: searchMode === "external" ? "#D29922" : t.sub, fontSize: 11, fontWeight: 700, cursor: "pointer", fontFamily: "'JetBrains Mono',monospace", boxShadow: searchMode === "external" ? "0 1px 3px rgba(0,0,0,0.15)" : "none", transition: "all 0.15s" }}>🔗 외부 기사</button>
        </div>
        <div style={{ display: "flex", gap: 6 }}>
          <input
            type="text"
            value={searchMode === "external" ? extQuery : input}
            onChange={(e) => searchMode === "external" ? setExtQuery(e.target.value) : setInput(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === "Enter") {
                searchMode === "external" ? void sendExternal(extQuery) : void sendWithText(input);
              }
            }}
            placeholder={searchMode === "internal" ? "궁금한 주제를 입력해줘" : "외부 기사 검색어 입력 (예: LFP 화재 리스크)"}
            aria-label={searchMode === "internal" ? "Ask AI assistant" : "Search external articles"}
            style={{ flex: 1, padding: "12px 14px", minHeight: "44px", borderRadius: 10, border: `1px solid ${searchMode === "external" ? (dark ? "rgba(210,153,34,0.3)" : "rgba(210,153,34,0.2)") : t.brd}`, background: searchMode === "external" ? (dark ? "#1A1E2A" : "#FFFBF0") : t.card2, color: t.tx, fontSize: 13, outline: "none", fontFamily: "'Pretendard',sans-serif" }}
          />
          <button
            onClick={() => searchMode === "external" ? void sendExternal(extQuery) : void sendWithText(input)}
            disabled={isLoading || (searchMode === "external" ? !extQuery.trim() : !input.trim())}
            aria-label={searchMode === "external" ? "Search external articles" : "Send message"}
            style={{ padding: "12px 18px", minHeight: "44px", minWidth: "44px", borderRadius: 10, border: "none", background: searchMode === "external" ? "#D29922" : t.cyan, color: "#000", fontWeight: 800, cursor: "pointer", fontSize: 13, fontFamily: "'Pretendard',sans-serif" }}
          >
            {searchMode === "external" ? "🔍" : "→"}
          </button>
        </div>
      </div>
    </div>
  );
}
```

**주요 변경:**
- props: `initialPrompt, initialPromptNonce` → `initialConsultation, initialConsultationNonce`
- `loading` state → `loadingMode` ("none"|"typing_normal"|"typing_consult")
- `currentConsultRef` ref 신규 (active consultation 추적)
- `ceremonyWait`: min 500ms 보장, max 2s cap (typing 동적)
- `startConsultation`: receipt push → opener POST (유저 풍선 스킵)
- `sendConsultFollowup`: consultation 중이면 유저 메시지 → followup 경로
- `sendWithText`: current consultation 있으면 followup, 없으면 일반 chat
- loading indicator 문구: consultation 중엔 "검토 중...", 일반은 "찾아보는 중..."
- `msgs.map`에 receipt role 분기 추가 → ReceiptBubble 렌더

---

## Section 4 — AppContent 내부 변경

### 4-A. state 변경

#### Before
```jsx
const [chatSeed, setChatSeed] = useState({ text: "", nonce: 0 });
```

#### After
```jsx
const [consultationSeed, setConsultationSeed] = useState({ data: null, nonce: 0 });
const [consultSummaries, setConsultSummaries] = useState(() =>
  typeof window !== "undefined" ? getAllCardConsultationSummaries() : {}
);
```

### 4-B. handler 변경

#### Before
```jsx
const handleAskChatbot = (prompt) => {
  if (!prompt) return;
  setChatSeed({ text: prompt, nonce: Date.now() });
  setTab("chatbot");
};
```

#### After
```jsx
const handleSubmitConsultation = (card) => {
  if (!card) return;

  // 1) build context on client (cards.json + recent openers for few-shot 배제)
  const recentOpenerIds = getRecentOpenerIds(5);
  const cardContext = buildCardConsultContext({
    card,
    allCards: kb.cards,
    recentOpenerIds,
  });
  if (!cardContext) return;

  // 2) create consultation record in localStorage
  const created = createConsultation({
    card,
    openerCategory: cardContext.opener_category,
    openerIdUsed: null, // LLM 성공 시에는 pool opener는 few-shot anchor로만 쓰임
  });
  if (!created) return;

  // 3) seed ChatBot (nonce로 재트리거)
  setConsultationSeed({
    data: {
      consultationId: created.id,
      cardContext,
      card_meta: created.card_meta,
      opened_at: created.opened_at,
    },
    nonce: Date.now(),
  });

  // 4) B안 footer 즉시 반영
  setConsultSummaries(getAllCardConsultationSummaries());

  // 5) chatbot tab 전환
  setTab("chatbot");
};
```

### 4-C. main render — ChatBot 호출 변경

#### Before
```jsx
{tab === "chatbot" && <ChatBot dark={dark} initialPrompt={chatSeed.text} initialPromptNonce={chatSeed.nonce} />}
```

#### After
```jsx
{tab === "chatbot" && <ChatBot dark={dark} initialConsultation={consultationSeed.data} initialConsultationNonce={consultationSeed.nonce} />}
```

### 4-D. Home/NewsDesk prop 전달 변경

#### Before
```jsx
{tab === "all" && <div style={{ paddingTop: 10 }}><Home kb={kb} tracker={tracker} onNav={setTab} onAskChatbot={handleAskChatbot} dark={dark} /></div>}
{tab === "news" && <NewsDesk kb={kb} onAskChatbot={handleAskChatbot} dark={dark} />}
```

#### After
```jsx
{tab === "all" && <div style={{ paddingTop: 10 }}><Home kb={kb} tracker={tracker} onNav={setTab} onSubmitConsultation={handleSubmitConsultation} consultSummaries={consultSummaries} dark={dark} /></div>}
{tab === "news" && <NewsDesk kb={kb} onSubmitConsultation={handleSubmitConsultation} consultSummaries={consultSummaries} dark={dark} />}
```

---

## Section 5 — Home / NewsDesk 내부 StoryNewsItem 호출 변경

### 5-A. Home component 시그니처

#### Before
```jsx
function Home({ kb, tracker, onNav, onAskChatbot, dark }) {
```

#### After
```jsx
function Home({ kb, tracker, onNav, onSubmitConsultation, consultSummaries = {}, dark }) {
```

### 5-B. Home 내부 StoryNewsItem 호출 2곳

#### Before (Lead — `picks[0]`)
```jsx
<StoryNewsItem
  card={lead}
  dark={dark}
  onAskChatbot={onAskChatbot}
  coverImage={pickHomeCover(lead)}
  featured
/>
```

#### After
```jsx
<StoryNewsItem
  card={lead}
  dark={dark}
  onSubmitConsultation={onSubmitConsultation}
  consultationHint={consultSummaries[getCardId(lead)] || null}
  coverImage={pickHomeCover(lead)}
  featured
/>
```

#### Before (rest map)
```jsx
{rest.map((card, i) => (
  <StoryNewsItem
    key={`${card.id || card.T || card.title}-${i}`}
    card={card}
    dark={dark}
    onAskChatbot={onAskChatbot}
    coverImage=""
  />
))}
```

#### After
```jsx
{rest.map((card, i) => (
  <StoryNewsItem
    key={`${card.id || card.T || card.title}-${i}`}
    card={card}
    dark={dark}
    onSubmitConsultation={onSubmitConsultation}
    consultationHint={consultSummaries[getCardId(card)] || null}
    coverImage=""
  />
))}
```

### 5-C. NewsDesk component 시그니처

#### Before
```jsx
function NewsDesk({ kb, onAskChatbot, dark }) {
```

#### After
```jsx
function NewsDesk({ kb, onSubmitConsultation, consultSummaries = {}, dark }) {
```

### 5-D. NewsDesk 내부 StoryNewsItem 호출 2곳

#### Before (highlights map — EDITOR'S PICKS)
```jsx
{highlights.map((card, i) => (
  <StoryNewsItem
    key={`${card.id || card.T || card.title}-${i}`}
    card={card}
    dark={dark}
    onAskChatbot={onAskChatbot}
  />
))}
```

#### After
```jsx
{highlights.map((card, i) => (
  <StoryNewsItem
    key={`${card.id || card.T || card.title}-${i}`}
    card={card}
    dark={dark}
    onSubmitConsultation={onSubmitConsultation}
    consultationHint={consultSummaries[getCardId(card)] || null}
  />
))}
```

#### Before (date별 map)
```jsx
{visible.filter((c) => c.d === date).map((card, i) => (
  <StoryNewsItem
    key={`${card.id || date}-${i}`}
    card={card}
    dark={dark}
    onAskChatbot={onAskChatbot}
  />
))}
```

#### After
```jsx
{visible.filter((c) => c.d === date).map((card, i) => (
  <StoryNewsItem
    key={`${card.id || date}-${i}`}
    card={card}
    dark={dark}
    onSubmitConsultation={onSubmitConsultation}
    consultationHint={consultSummaries[getCardId(card)] || null}
  />
))}
```

---

## 검증 체크리스트

패치 적용 후 확인:

- [ ] `npm run dev` (또는 `pnpm dev`) 에서 에러 없이 빌드
- [ ] 뉴스 탭에서 `📋 상담카드 제출` 버튼 상시 노출 (브리프 안 펴도 보임)
- [ ] 버튼 클릭 → chatbot 탭 전환 + 접수증 bubble + 강차장 opener 등장
- [ ] Groq 응답 도착 시점에 ceremony (min 500ms) 유지되어 typing이 튀지 않음
- [ ] opener 이후 유저 텍스트 입력 → consultation followup으로 전송
- [ ] 두 번째 상담 접수 시: 같은 카드 뉴스 탭 footer에 `↘ 2번 상담 · 최근 X/Y` 표시
- [ ] `localStorage.getItem("sbtl_consult_v1")`로 저장 구조 육안 확인
- [ ] 일반 chat (carousel 버튼 / 직접 타이핑)은 기존과 동일하게 작동
- [ ] 외부 검색 모드도 기존 동작 유지

---

## 주의

- `getCardId` import 안 하면 `consultSummaries[getCardId(card)]` 부분에서 에러. Section 1 import 블록 누락 없이 반영.
- Section 3 ChatBot 교체 시 반드시 기존 함수 **전체**를 덮어써야 함 (부분 edit 시 unused import / ref 충돌 가능).
- 기존 `onAskChatbot` prop 사용처가 이 3곳 외 더 있는지 패치 전 `grep onAskChatbot src/` 로 확인 권장.
