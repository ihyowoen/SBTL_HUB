import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const here = path.dirname(fileURLToPath(import.meta.url));
const root = path.resolve(here, "..");

function read(rel) { return fs.readFileSync(path.join(root, rel), "utf8"); }
function write(rel, text) { fs.writeFileSync(path.join(root, rel), text); }

function replaceOnce(text, from, to, label) {
  const first = text.indexOf(from);
  if (first < 0) throw new Error(`[phase2] missing anchor: ${label}`);
  if (text.indexOf(from, first + from.length) >= 0) throw new Error(`[phase2] non-unique anchor: ${label}`);
  return text.slice(0, first) + to + text.slice(first + from.length);
}

function replaceLine(text, needle, to, label = needle) {
  const lines = text.split("\n");
  const hits = lines.map((line, i) => line.includes(needle) ? i : -1).filter((i) => i >= 0);
  if (hits.length !== 1) throw new Error(`[phase2] ${label}: expected 1 line, got ${hits.length}`);
  lines[hits[0]] = to;
  return lines.join("\n");
}

function replaceTextCount(text, from, to, expected, label) {
  const count = text.split(from).length - 1;
  if (count !== expected) throw new Error(`[phase2] ${label}: expected ${expected}, got ${count}`);
  return text.split(from).join(to);
}

// ---------------------------------------------------------------------------
// App.jsx — product/UI boundary only. Internal period/localStorage contracts stay.
// ---------------------------------------------------------------------------
let app = read("src/App.jsx");

app = replaceOnce(
  app,
  'import MdText from "./MdText";\n',
  'import MdText from "./MdText";\nimport StrategicBriefPanel from "./StrategicBriefPanel";\n',
  "StrategicBriefPanel import",
);

app = replaceLine(
  app,
  '{ icon: "📮", title: "브리프", desc:',
  '    { icon: "📮", title: "브리핑", desc: "공식 월간 전략 브리핑은 편집 승인본만 · 자동 생성은 주간/30일 빠른 분석으로 분리", chips: ["주간 브리프 보여줘", "지금 브리프 만들어줘", "30일 빠른 분석 만들어줘", "월간 전략 브리핑 보여줘"] },',
  "ChatGuide briefing row",
);

app = replaceOnce(
  app,
  '        <span style={{ fontSize: 9, color: t.sub, fontFamily: "\'JetBrains Mono\',monospace" }}>{entry.generated_at} 발행 · 근거 {refs.length}장</span>',
  '        <span style={{ fontSize: 9, color: t.sub, fontFamily: "\'JetBrains Mono\',monospace" }}>{entry.generated_at} 생성 · 근거 {refs.length}장</span>',
  "quick-analysis reader generated label",
);

app = replaceOnce(
  app,
  '`[SBTL ${entry.period === "monthly" ? "월간" : "주간"} 브리프] ${entry.scope_label || "내워치"} — ${entry.generated_at || ""}`',
  '`[SBTL ${entry.month ? "월별 빠른 분석" : entry.period === "monthly" ? "30일 빠른 분석" : "주간 브리프"}] ${entry.scope_label || "내워치"} — ${entry.generated_at || ""}`',
  "copy header product label",
);

app = replaceOnce(
  app,
  '    } else if (roomSeed.view === "builder") {\n      setBuilderOpen(true);\n      setTimeout(() => { try { builderPanelRef.current?.scrollIntoView({ behavior: "smooth", block: "start" }); } catch { /* noop */ } }, 60);\n    }',
  '    } else if (roomSeed.view === "builder") {\n      setBuilderOpen(true);\n      setTimeout(() => { try { builderPanelRef.current?.scrollIntoView({ behavior: "smooth", block: "start" }); } catch { /* noop */ } }, 60);\n    } else if (roomSeed.view === "strategic") {\n      setTimeout(() => { try { document.getElementById("strategic-brief-panel")?.scrollIntoView({ behavior: "smooth", block: "start" }); } catch { /* noop */ } }, 60);\n    }',
  "strategic room deep-link",
);

app = replaceLine(
  app,
  '{sectionTitle("📮 브리프",',
  '      <><StrategicBriefPanel dark={dark} cards={kb.cards} seed={roomSeed} />{sectionTitle("⚡ 빠른 분석", `주간은 자동 생성${watchTerms.length ? "" : " (워치가 비어 있어 전체 카드 기준)"} — 필요할 때 30일·월별·지역별·주제별 분석도 바로 만들 수 있어요. 공식 VOL.xx 월간 전략 브리핑과는 별도입니다.`)}</>',
  "official vs exploratory briefing split",
);

app = replaceTextCount(app, '>📮 브리프</span>', '>⚡ 빠른 분석 보관함</span>', 1, "quick shelf heading");
app = replaceTextCount(app, '🔄 새 브리프 만드는 중…', '🔄 새 빠른 분석 만드는 중…', 1, "quick generation status");
app = replaceTextCount(app, '📈 발행 후 {Number(shown.month.slice(5))}월 기사', '📈 생성 후 {Number(shown.month.slice(5))}월 기사', 1, "quick drift label");
app = replaceTextCount(app, '>새 재료로 재발행</button>', '>새 재료로 다시 분석</button>', 1, "quick drift action");
app = replaceOnce(app, '${copiedWeekly ? "복사됨 ✓" : "브리프 복사 (출처 각주 포함)"}', '${copiedWeekly ? "복사됨 ✓" : "빠른 분석 복사 (출처 각주 포함)"}', "quick copy button");
app = replaceOnce(
  app,
  '`[SBTL ${shown.period === "monthly" ? "월간" : "주간"} 브리프] ${shown.scope_label || "내워치"} · ${shown.generated_at}\n\n${String(shown.narrative || "")}`',
  '`[SBTL ${shown.month ? "월별 빠른 분석" : shown.period === "monthly" ? "30일 빠른 분석" : "주간 브리프"}] ${shown.scope_label || "내워치"} · ${shown.generated_at}\n\n${String(shown.narrative || "")}`',
  "quick share header",
);
app = replaceTextCount(app, '>지난 브리프</div>', '>지난 빠른 분석</div>', 1, "quick history label");
app = replaceTextCount(app, '아직 발행본이 없어요 — 아래 버튼으로 바로 만들 수 있어요.', '아직 생성한 빠른 분석이 없어요 — 아래 버튼으로 바로 만들 수 있어요.', 1, "quick empty state");
app = replaceTextCount(app, '>⚡ 주간 발행</button>', '>⚡ 주간 브리프</button>', 1, "weekly button");
app = replaceTextCount(app, '>📅 월간 발행</button>', '>📅 30일 분석</button>', 1, "rolling monthly button");
app = replaceTextCount(app, '월호 바로 열기', '월 빠른 분석 바로 열기', 1, "calendar month instant title");
app = replaceTextCount(app, '월 한 달치 브리프 발행', '월 월별 빠른 분석 만들기', 1, "calendar month create title");
app = replaceTextCount(app, '>월간: {monthlyBlock}</div>', '>30일: {monthlyBlock}</div>', 1, "monthly gate label");
app = replaceTextCount(app, '내 워치(🏢)·지역·주제 축을 고른 순서대로 엮어 나만의 브리프를 만들어요', '내 워치(🏢)·지역·주제 축을 고른 순서대로 엮어 나만의 빠른 분석을 만들어요', 1, "builder description");
app = replaceOnce(app, '[["weekly", "주간"], ["monthly", "월간"], ...briefMonths.map((m) => [m, m.replace("-", ".")])]', '[["weekly", "주간"], ["monthly", "30일"], ...briefMonths.map((m) => [m, m.replace("-", ".")])]', "builder monthly label");
app = replaceOnce(app, '`🧩 발행 — ${builderAxes.map((ax) => ax.key).join("·")} · ${builderAxes.length}축 ${builderCardTotal}장`', '`🧩 분석 만들기 — ${builderAxes.map((ax) => ax.key).join("·")} · ${builderAxes.length}축 ${builderCardTotal}장`', "builder action label");

app = replaceOnce(
  app,
  '      const periodLabel = month\n        ? `${Number(month.slice(0, 4))}년 ${Number(month.slice(5))}월`\n        : period === "monthly" ? "월간" : "주간";',
  '      const periodLabel = month\n        ? `${Number(month.slice(0, 4))}년 ${Number(month.slice(5))}월 빠른 분석`\n        : period === "monthly" ? "30일 빠른 분석" : "주간";',
  "runtime scope product label",
);

app = replaceOnce(
  app,
  '      } else if (cmd.type === "weekly_show") {',
  '      } else if (cmd.type === "strategic_show") {\n        setRoomSeed((s) => ({ view: "strategic", edition: cmd.edition || null, month: cmd.month || null, nonce: (s ? s.nonce : 0) + 1 }));\n        setTab("watchroom");\n      } else if (cmd.type === "weekly_show") {',
  "strategic_show dispatcher",
);

app = replaceLine(
  app,
  'const [roomSeed, setRoomSeed] = useState(null);',
  '  const [roomSeed, setRoomSeed] = useState(null); // 딥링크 — {view:"map"|"builder"|"strategic", edition?, month?, nonce}',
  "room seed contract",
);

app = replaceLine(
  app,
  'const headerSub = { news:',
  '  const headerSub = { news: `Cards ${kb.cardCount} · updated ${fmtDate(lastCardDate)} · live feed`, chatbot: "배터리·ESS 이슈를 빠르게 찾고 정리해주는 AI 데스크", watchroom: "월간 전략 브리핑 · 빠른 분석 · 내 워치 · 저장 카드", archive: `정책 ${tracker.meta.totalItems}건 · 용어 ${kb.faqCount}항목 · ${WEBTOON_COLLECTIONS.length}시리즈` }[tab] || `Cards ${kb.cardCount} · ESS · EV · Policy`;',
  "watchroom header semantics",
);

write("src/App.jsx", app);

// ---------------------------------------------------------------------------
// appCommand.js — new terminology + separate official reader command.
// ---------------------------------------------------------------------------
let cmd = read("lib/chat/appCommand.js");

cmd = replaceOnce(
  cmd,
  'const PERIOD_TOKEN = "((?:\\\\d{4}년\\\\s*)?\\\\d{1,2}월(?:호)?|주간|월간)";',
  'const PERIOD_TOKEN = "((?:\\\\d{4}년\\\\s*)?\\\\d{1,2}월(?:호)?|30일|주간|월간)";\nconst ANALYSIS_NOUN = "(?:브리프|빠른\\\\s*분석)";',
  "quick analysis period token",
);
cmd = replaceOnce(
  cmd,
  'const CMD_WEEKLY = new RegExp(`${GROUP_TOKEN}\\\\s*${PERIOD_TOKEN}?\\\\s*${GROUP_TOKEN}\\\\s*브리프(?:을|를)?\\\\s*(?:보여|열어|볼|줘|확인)${VIEW_TAIL}`);',
  'const CMD_WEEKLY = new RegExp(`${GROUP_TOKEN}\\\\s*${PERIOD_TOKEN}?\\\\s*${GROUP_TOKEN}\\\\s*${ANALYSIS_NOUN}(?:을|를)?\\\\s*(?:보여|열어|볼|줘|확인)${VIEW_TAIL}`);',
  "quick analysis show regex",
);
cmd = replaceOnce(
  cmd,
  'const CMD_BRIEF_NOW = new RegExp(`${GROUP_TOKEN}\\\\s*${PERIOD_TOKEN}?\\\\s*${GROUP_TOKEN}\\\\s*브리프(?:을|를)?\\\\s*(?:지금\\\\s*|새로\\\\s*|다시\\\\s*|하나\\\\s*)*(?:만들어|만들|생성|발행|뽑아)${IMPERATIVE_TAIL}`);',
  'const CMD_BRIEF_NOW = new RegExp(`${GROUP_TOKEN}\\\\s*${PERIOD_TOKEN}?\\\\s*${GROUP_TOKEN}\\\\s*${ANALYSIS_NOUN}(?:을|를)?\\\\s*(?:지금\\\\s*|새로\\\\s*|다시\\\\s*|하나\\\\s*)*(?:만들어|만들|생성|발행|뽑아)${IMPERATIVE_TAIL}`);\nconst CMD_STRATEGIC_SHOW = new RegExp(`(?:(VOL\\\\.\\\\s*\\\\d{2,})|((?:\\\\d{4}년\\\\s*)?\\\\d{1,2}월)\\\\s*)?(?:월간\\\\s*)?전략\\\\s*브리핑(?:을|를)?\\\\s*(?:보여|열어|볼|줘|확인)${VIEW_TAIL}`, "i");',
  "official Strategic Brief show regex",
);
cmd = replaceOnce(cmd, '  if (tok === "월간") return { period: "monthly", month: null };', '  if (tok === "월간" || tok === "30일") return { period: "monthly", month: null };', "30-day period parse");
cmd = replaceOnce(
  cmd,
  '  const briefNowMatch = msg.match(CMD_BRIEF_NOW);',
  '  const strategicShowMatch = msg.match(CMD_STRATEGIC_SHOW);\n  if (strategicShowMatch) {\n    const edition = strategicShowMatch[1] ? String(strategicShowMatch[1]).replace(/\\s+/g, "").toUpperCase() : null;\n    const parsedMonth = strategicShowMatch[2] ? parsePeriodToken(strategicShowMatch[2]) : null;\n    if (parsedMonth?.invalid) return null;\n    return { type: "strategic_show", ...(edition ? { edition } : {}), ...(parsedMonth?.month ? { month: parsedMonth.month } : {}) };\n  }\n  const briefNowMatch = msg.match(CMD_BRIEF_NOW);',
  "official command precedence",
);

cmd = replaceOnce(
  cmd,
  '  if (cmd.type === "brief_now") {\n    const periodLabel = cmd.month ? monthKo(cmd.month) : cmd.period === "monthly" ? "월간" : "주간";',
  '  if (cmd.type === "strategic_show") {\n    const target = cmd.edition || (cmd.month ? `${monthKo(cmd.month)} ` : "");\n    return {\n      answer: `${target}공식 월간 전략 브리핑 열어줄게 — 브리핑룸의 승인본으로 이동할게. 아직 승인본이 없으면 편집 중으로 표시되고, 자동 생성하지 않아.`,\n      suggestions: [\n        { label: "30일 빠른 분석 만들어줘" },\n        { label: "주간 브리프 보여줘" },\n      ],\n    };\n  }\n  if (cmd.type === "brief_now") {\n    const periodLabel = cmd.month ? `${monthKo(cmd.month)} 월별 빠른 분석` : cmd.period === "monthly" ? "30일 빠른 분석" : "주간 브리프";',
  "official response + quick label",
);
cmd = replaceOnce(
  cmd,
  '      answer: `응, 지금 ${periodLabel} 브리프 만들게.${groupText} ${scopeText}를 모아 정리하는 데 수십 초 걸려 — 브리핑룸 📮 선반 열어놓을 테니 완성되면 맨 위에 꽂아둘게.`,',
  '      answer: `응, 지금 ${periodLabel} 만들게.${groupText} ${scopeText}를 모아 정리하는 데 수십 초 걸려 — 브리핑룸 ⚡ 빠른 분석 보관함을 열어놓을 테니 완성되면 맨 위에 꽂아둘게.`,',
  "quick analysis response copy",
);
cmd = replaceOnce(cmd, '? { label: `${monthChipLabel(cmd.month)} 지역별 브리프 만들어줘` }', '? { label: `${monthChipLabel(cmd.month)} 지역별 빠른 분석 만들어줘` }', "calendar quick suggestion");
cmd = replaceOnce(cmd, ': { label: cmd.period === "monthly" ? "월간 브리프 보여줘" : "주간 브리프 보여줘" },', ': { label: cmd.period === "monthly" ? "30일 빠른 분석 보여줘" : "주간 브리프 보여줘" },', "rolling quick suggestion");
cmd = replaceOnce(cmd, '이번엔 브리프감이 부족해.', '이번엔 분석 재료가 부족해.', "no-material terminology");
cmd = replaceOnce(
  cmd,
  '  const showLabel = cmd.month ? monthKo(cmd.month) : cmd.period === "monthly" ? "월간" : cmd.period === "weekly" ? "주간" : "";',
  '  const showLabel = cmd.month ? `${monthKo(cmd.month)} 월별 빠른 분석` : cmd.period === "monthly" ? "30일 빠른 분석" : cmd.period === "weekly" ? "주간 브리프" : "";',
  "show label terminology",
);
cmd = replaceOnce(cmd, 'answer: `방금 만든 ${showLabel ? `${showLabel} ` : ""}브리프가 있어 — 새로 만드는 대신 바로 보여줄게.', 'answer: `방금 만든 ${showLabel || "빠른 분석"}이 있어 — 새로 만드는 대신 바로 보여줄게.', "recent quick response");
cmd = replaceOnce(
  cmd,
  '      answer: `${monthKo(cmd.month)} 브리프 열어줄게 — 브리핑룸으로 이동할게. 그 달 호수가 아직 없으면 \'${chipMonth} 브리프 만들어줘\'라고 해주면 바로 만들게.`,',
  '      answer: `${monthKo(cmd.month)} 월별 빠른 분석 열어줄게 — 브리핑룸으로 이동할게. 그 달 분석이 아직 없으면 \'${chipMonth} 빠른 분석 만들어줘\'라고 해주면 바로 만들게.`,',
  "calendar quick show response",
);
cmd = replaceOnce(cmd, '{ label: `${chipMonth} 브리프 만들어줘` },', '{ label: `${chipMonth} 빠른 분석 만들어줘` },', "calendar quick create suggestion");
cmd = replaceOnce(
  cmd,
  '      answer: "월간 브리프 열어줄게 — 브리핑룸으로 이동할게. 월간은 자동 발행이 없어서, 아직 없으면 \'월간 브리프 만들어줘\'라고 해주면 바로 만들게.",',
  '      answer: "30일 빠른 분석 열어줄게 — 브리핑룸으로 이동할게. 아직 없으면 \'30일 빠른 분석 만들어줘\'라고 해주면 바로 만들게.",',
  "rolling quick show response",
);
cmd = replaceOnce(cmd, '{ label: "월간 브리프 만들어줘" },', '{ label: "30일 빠른 분석 만들어줘" },', "rolling quick create suggestion");
cmd = replaceOnce(
  cmd,
  '    answer: `${showLabel || "최신"} 브리프 열어줄게 — 브리핑룸으로 이동할게. 아직 발행된 게 없으면 다음 접속 때 자동으로 만들어져.`,',
  '    answer: `${showLabel || "최신 브리프/빠른 분석"} 열어줄게 — 브리핑룸으로 이동할게. 주간 브리프가 아직 없으면 다음 접속 때 자동으로 만들어져.`,',
  "default show response",
);

write("lib/chat/appCommand.js", cmd);

// ---------------------------------------------------------------------------
// /api/brief — exploratory synthesis only, never official publication.
// ---------------------------------------------------------------------------
let api = read("api/brief.js");
api = replaceOnce(
  api,
  'const MAX_CARDS = 40;\n',
  'export function isOfficialPublicationRequest(payload) {\n  return payload?.publication_class === "official_editorial" || payload?.publication_mode === "editorial_curated";\n}\n\nconst MAX_CARDS = 40;\n',
  "brief API official-request helper",
);
api = replaceOnce(
  api,
  '  if (typeof payload === "string") {\n    try { payload = JSON.parse(payload); } catch { payload = null; }\n  }\n  const scopeLabel = clip(payload?.scopeLabel, 120) || "선택 범위";',
  '  if (typeof payload === "string") {\n    try { payload = JSON.parse(payload); } catch { payload = null; }\n  }\n  if (isOfficialPublicationRequest(payload)) {\n    return res.status(409).json({ ok: false, error: "official-publication-not-supported", publication_class: "exploratory_auto" });\n  }\n  const scopeLabel = clip(payload?.scopeLabel, 120) || "선택 범위";',
  "brief API publication rejection",
);
api = replaceOnce(
  api,
  '    return res.status(200).json({ ok: true, narrative: clip(attempt.raw, 2000), watch: [], degraded: true, provider: attempt.provider });',
  '    return res.status(200).json({ ok: true, publication_class: "exploratory_auto", narrative: clip(attempt.raw, 2000), watch: [], degraded: true, provider: attempt.provider });',
  "degraded output classification",
);
api = replaceOnce(
  api,
  '  return res.status(200).json({\n    ok: true,\n    narrative,',
  '  return res.status(200).json({\n    ok: true,\n    publication_class: "exploratory_auto",\n    narrative,',
  "normal output classification",
);
write("api/brief.js", api);

console.log("[phase2] patched App.jsx, appCommand.js and api/brief.js");
