import fs from "node:fs";

function replaceOnce(text, from, to, label) {
  const first = text.indexOf(from);
  if (first < 0) throw new Error(`${label}: anchor not found`);
  if (text.indexOf(from, first + from.length) >= 0) throw new Error(`${label}: anchor not unique`);
  return text.slice(0, first) + to + text.slice(first + from.length);
}

// ---- App command semantics: Monthly Brief is official; quick analysis stays separate.
{
  const path = "lib/chat/appCommand.js";
  let text = fs.readFileSync(path, "utf8");

  text = replaceOnce(
    text,
    'const CMD_STRATEGIC_SHOW = new RegExp(`(?:(VOL\\\\.\\\\s*\\\\d{2,})\\\\s*|((?:\\\\d{4}년\\\\s*)?\\\\d{1,2}월)\\\\s*)?(?:월간\\\\s*)?전략\\\\s*브리핑(?:을|를)?\\\\s*(?:보여|열어|볼|줘|확인)${VIEW_TAIL}`, "i");',
    'const CMD_MONTHLY_BRIEF_SHOW = new RegExp(`(?:((?:\\\\d{4}년\\\\s*)?\\\\d{1,2}월)\\\\s*)?(?:SBTL\\\\s*)?월간\\\\s*브리프(?:을|를)?\\\\s*(?:보여|열어|볼|줘|확인)${VIEW_TAIL}`, "i");\nconst CMD_MONTHLY_BRIEF_CREATE = new RegExp(`(?:((?:\\\\d{4}년\\\\s*)?\\\\d{1,2}월)\\\\s*)?(?:SBTL\\\\s*)?월간\\\\s*브리프(?:을|를)?\\\\s*(?:지금\\\\s*|새로\\\\s*|다시\\\\s*)*(?:만들어|만들|생성|발행|뽑아)${IMPERATIVE_TAIL}`, "i");',
    "monthly command regexes",
  );

  text = replaceOnce(
    text,
    '  const strategicShowMatch = msg.match(CMD_STRATEGIC_SHOW);\n  if (strategicShowMatch) {\n    const edition = strategicShowMatch[1] ? String(strategicShowMatch[1]).replace(/\\s+/g, "").toUpperCase() : null;\n    const parsedMonth = strategicShowMatch[2] ? parsePeriodToken(strategicShowMatch[2]) : null;\n    if (parsedMonth?.invalid) return null;\n    return { type: "strategic_show", ...(edition ? { edition } : {}), ...(parsedMonth?.month ? { month: parsedMonth.month } : {}) };\n  }',
    '  const monthlyShowMatch = msg.match(CMD_MONTHLY_BRIEF_SHOW);\n  if (monthlyShowMatch) {\n    const parsedMonth = monthlyShowMatch[1] ? parsePeriodToken(monthlyShowMatch[1]) : null;\n    if (parsedMonth?.invalid) return null;\n    return { type: "monthly_show", ...(parsedMonth?.month ? { month: parsedMonth.month } : {}) };\n  }\n  const monthlyCreateMatch = msg.match(CMD_MONTHLY_BRIEF_CREATE);\n  if (monthlyCreateMatch) {\n    const parsedMonth = monthlyCreateMatch[1] ? parsePeriodToken(monthlyCreateMatch[1]) : null;\n    if (parsedMonth?.invalid) return null;\n    return { type: "monthly_show", requested_action: "create", ...(parsedMonth?.month ? { month: parsedMonth.month } : {}) };\n  }',
    "monthly command detection",
  );

  text = replaceOnce(
    text,
    '  if (cmd.type === "strategic_show") {\n    const target = cmd.edition || (cmd.month ? `${monthKo(cmd.month)} ` : "");\n    return {\n      answer: `${target}공식 월간 전략 브리핑 열어줄게 — 브리핑룸의 승인본으로 이동할게. 아직 승인본이 없으면 편집 중으로 표시되고, 자동 생성하지 않아.`,\n      suggestions: [\n        { label: "30일 빠른 분석 만들어줘" },\n        { label: "주간 브리프 보여줘" },\n      ],\n    };\n  }',
    '  if (cmd.type === "monthly_show") {\n    const target = cmd.month ? `${monthKo(cmd.month)} ` : "";\n    if (cmd.requested_action === "create") {\n      return {\n        answer: `${target}SBTL Monthly Brief는 자동 생성하지 않아. 월간 전체 Deep Dive와 Red Team을 거쳐 편집 승인된 정본만 발행해. 현재 공식 월간 브리프 영역을 열어둘게.`,\n        suggestions: [\n          { label: "30일 빠른 분석 만들어줘" },\n          { label: "주간 브리프 보여줘" },\n        ],\n      };\n    }\n    return {\n      answer: `${target}공식 SBTL Monthly Brief 열어줄게 — 브리핑룸의 승인본으로 이동할게. 아직 승인본이 없으면 편집 중으로 표시되고, 자동 생성하지 않아.`,\n      suggestions: [\n        { label: "30일 빠른 분석 만들어줘" },\n        { label: "주간 브리프 보여줘" },\n      ],\n    };\n  }',
    "monthly command response",
  );

  fs.writeFileSync(path, text);
}

// ---- App reader/UI wiring.
{
  const path = "src/App.jsx";
  let text = fs.readFileSync(path, "utf8");

  text = replaceOnce(text, 'import StrategicBriefPanel from "./StrategicBriefPanel";', 'import MonthlyBriefPanel from "./MonthlyBriefPanel";', "App panel import");
  text = replaceOnce(
    text,
    '    } else if (roomSeed.view === "strategic") {\n      setTimeout(() => { try { document.getElementById("strategic-brief-panel")?.scrollIntoView({ behavior: "smooth", block: "start" }); } catch { /* noop */ } }, 60);\n    }',
    '    } else if (roomSeed.view === "monthly") {\n      setTimeout(() => { try { document.getElementById("monthly-brief-panel")?.scrollIntoView({ behavior: "smooth", block: "start" }); } catch { /* noop */ } }, 60);\n    }',
    "App room deep link",
  );
  text = replaceOnce(
    text,
    '      <><StrategicBriefPanel dark={dark} cards={kb.cards} seed={roomSeed} />{sectionTitle("⚡ 빠른 분석", `주간은 자동 생성${watchTerms.length ? "" : " (워치가 비어 있어 전체 카드 기준)"} — 필요할 때 30일·월별·지역별·주제별 분석도 바로 만들 수 있어요. 공식 VOL.xx 월간 전략 브리핑과는 별도입니다.`)}</>',
    '      <><MonthlyBriefPanel dark={dark} cards={kb.cards} seed={roomSeed} />{sectionTitle("⚡ 빠른 분석", `주간은 자동 생성${watchTerms.length ? "" : " (워치가 비어 있어 전체 카드 기준)"} — 필요할 때 30일·월별·지역별·주제별 분석도 바로 만들 수 있어요. 공식 SBTL Monthly Brief와는 별도입니다.`)}</>',
    "App reader render",
  );
  text = replaceOnce(
    text,
    '    { icon: "📮", title: "브리핑", desc: "공식 월간 전략 브리핑은 편집 승인본만 · 자동 생성은 주간/30일 빠른 분석으로 분리", chips: ["주간 브리프 보여줘", "지금 브리프 만들어줘", "30일 빠른 분석 만들어줘", "월간 전략 브리핑 보여줘"] },',
    '    { icon: "📮", title: "브리핑", desc: "SBTL Monthly Brief는 Deep Dive·편집 승인본만 · 자동 생성은 주간/빠른 분석으로 분리", chips: ["월간 브리프 보여줘", "주간 브리프 보여줘", "30일 빠른 분석 만들어줘", "2026년 8월 월별 빠른 분석 만들어줘"] },',
    "App chat guide",
  );
  text = replaceOnce(
    text,
    '  const [roomSeed, setRoomSeed] = useState(null); // 딥링크 — {view:"map"|"builder"|"strategic", edition?, month?, nonce}',
    '  const [roomSeed, setRoomSeed] = useState(null); // 딥링크 — {view:"map"|"builder"|"monthly", month?, nonce}',
    "App room seed comment",
  );
  text = replaceOnce(
    text,
    '      } else if (cmd.type === "strategic_show") {\n        setRoomSeed((s) => ({ view: "strategic", edition: cmd.edition || null, month: cmd.month || null, nonce: (s ? s.nonce : 0) + 1 }));\n        setTab("watchroom");',
    '      } else if (cmd.type === "monthly_show") {\n        setRoomSeed((s) => ({ view: "monthly", month: cmd.month || null, nonce: (s ? s.nonce : 0) + 1 }));\n        setTab("watchroom");',
    "App command dispatch",
  );
  text = replaceOnce(
    text,
    'watchroom: "월간 전략 브리핑 · 빠른 분석 · 내 워치 · 저장 카드"',
    'watchroom: "SBTL Monthly Brief · 빠른 분석 · 내 워치 · 저장 카드"',
    "App watchroom subtitle",
  );

  fs.writeFileSync(path, text);
}

// Remove the obsolete Strategic/VOL domain after the replacement reader and tests exist.
for (const path of [
  "product/STRATEGIC_BRIEF_EDITORIAL_CONTRACT.md",
  "public/data/strategic_briefs.json",
  "schemas/strategic-brief.v1.schema.json",
  "lib/brief/strategicPublication.js",
  "scripts/validate_strategic_briefs.mjs",
  "src/StrategicBriefPanel.jsx",
  "src/strategicBriefSelection.js",
  "__tests__/strategicBriefPublication.test.js",
  "__tests__/strategicBriefProductBoundary.test.js",
  "__tests__/strategicBriefSelection.test.js",
  "__tests__/strategicBriefEditionCommand.test.js",
  ".github/workflows/validate-strategic-briefs.yml",
]) {
  if (!fs.existsSync(path)) throw new Error(`obsolete path missing: ${path}`);
  fs.rmSync(path);
}

console.log("Monthly Brief domain cleanup applied");
