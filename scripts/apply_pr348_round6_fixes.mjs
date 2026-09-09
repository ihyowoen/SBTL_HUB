import fs from "node:fs";

function replaceOnce(text, from, to, label) {
  const first = text.indexOf(from);
  if (first < 0) throw new Error(`${label}: anchor not found`);
  if (text.indexOf(from, first + from.length) >= 0) throw new Error(`${label}: anchor not unique`);
  return text.slice(0, first) + to + text.slice(first + from.length);
}

// 1) Preserve optional 월호 qualifiers in official Monthly Brief show/create commands.
{
  const path = "lib/chat/appCommand.js";
  let text = fs.readFileSync(path, "utf8");
  text = replaceOnce(
    text,
    'const CMD_MONTHLY_BRIEF_SHOW = new RegExp(`(?:((?:\\\\d{4}년\\\\s*)?\\\\d{1,2}월)\\\\s*)?(?:SBTL\\\\s*)?월간\\\\s*브리프(?:을|를)?\\\\s*(?:보여|열어|볼|줘|확인)${VIEW_TAIL}`, "i");',
    'const CMD_MONTHLY_BRIEF_SHOW = new RegExp(`(?:((?:\\\\d{4}년\\\\s*)?\\\\d{1,2}월(?:호)?)\\\\s*)?(?:SBTL\\\\s*)?월간\\\\s*브리프(?:을|를)?\\\\s*(?:보여|열어|볼|줘|확인)${VIEW_TAIL}`, "i");',
    "Monthly Brief show 월호 qualifier",
  );
  text = replaceOnce(
    text,
    'const CMD_MONTHLY_BRIEF_CREATE = new RegExp(`(?:((?:\\\\d{4}년\\\\s*)?\\\\d{1,2}월)\\\\s*)?(?:SBTL\\\\s*)?월간\\\\s*브리프(?:을|를)?\\\\s*(?:지금\\\\s*|새로\\\\s*|다시\\\\s*|하나\\\\s*|한\\\\s*개\\\\s*|한\\\\s*번\\\\s*|한번\\\\s*)*(?:만들어|만들|생성|발행|뽑아)${IMPERATIVE_TAIL}`, "i");',
    'const CMD_MONTHLY_BRIEF_CREATE = new RegExp(`(?:((?:\\\\d{4}년\\\\s*)?\\\\d{1,2}월(?:호)?)\\\\s*)?(?:SBTL\\\\s*)?월간\\\\s*브리프(?:을|를)?\\\\s*(?:지금\\\\s*|새로\\\\s*|다시\\\\s*|하나\\\\s*|한\\\\s*개\\\\s*|한\\\\s*번\\\\s*|한번\\\\s*)*(?:만들어|만들|생성|발행|뽑아)${IMPERATIVE_TAIL}`, "i");',
    "Monthly Brief create 월호 qualifier",
  );
  fs.writeFileSync(path, text);
}

// 2) Provide a prose-safe label for automated Quick Analysis outputs.
{
  const path = "src/quickAnalysisLabels.js";
  let text = fs.readFileSync(path, "utf8");
  const anchor = `export function quickAnalysisChipLabel(entry, nowYear, dupMonth = false) {\n  const e = entry || {};\n  const dd = String(e.generated_at || "").slice(5);\n  if (e.month) {\n    const base = calendarQuickAnalysisLabel(e.month, nowYear);\n    return \`${'${base}${e.group === "custom" ? "🧩" : ""}${dupMonth ? ` ${dd}` : ""}'}\`;\n  }\n  if (e.group === "custom") return \`🧩 ${'${e.period === "monthly" ? "30일" : "주간"}'} ${'${dd}'}\`;\n  return \`${'${e.period === "monthly" ? "30일" : "주간"}'} ${'${dd}'}\`;\n}\n`;
  const replacement = `${anchor}\nexport function quickAnalysisProseLabel(entry, nowYear = null) {\n  const e = entry || {};\n  const label = String(e.label || "").trim();\n  if (e.month) {\n    if (label.includes("분석")) return label;\n    return calendarQuickAnalysisLabel(e.month, nowYear);\n  }\n  if (e.period === "monthly") return \`${'${e.group === "custom" ? "🧩 " : ""}'}30일 빠른 분석\`;\n  if (!label) return "주간 브리프";\n  if (label.includes("분석") || label.includes("브리프")) return label;\n  return \`${'${label}'} 브리프\`;\n}\n`;
  text = replaceOnce(text, anchor, replacement, "Quick Analysis prose label helper");
  fs.writeFileSync(path, text);
}

// 3) Use the prose-safe Quick Analysis label in Kang unread messaging.
{
  const path = "src/kang.js";
  let text = fs.readFileSync(path, "utf8");
  text = replaceOnce(
    text,
    'import { calendarQuickAnalysisLabel } from "./quickAnalysisLabels.js";',
    'import { calendarQuickAnalysisLabel, quickAnalysisProseLabel } from "./quickAnalysisLabels.js";',
    "Kang Quick Analysis label import",
  );
  text = replaceOnce(
    text,
    '      text: `${i.unreadBrief.label}${String(i.unreadBrief.label).includes("분석") ? "" : " 브리프"} 만들어뒀어 — 읽고 가.`,',
    '      text: `${quickAnalysisProseLabel(i.unreadBrief)} 만들어뒀어 — 읽고 가.`,',
    "Kang unread Quick Analysis prose",
  );
  fs.writeFileSync(path, text);
}

// 4) Enforce QC review chronology before approval/publication.
{
  const path = "lib/brief/monthlyPublication.js";
  let text = fs.readFileSync(path, "utf8");
  const anchor = `  }\n\n  if (Array.isArray(item.source_card_ids)) {`;
  const block = `  }\n\n  const reviewedAt = item.qc?.reviewed_at;\n  if (validIsoDate(reviewedAt)) {\n    if (validIsoDate(approval?.approved_at) && reviewedAt > approval.approved_at) {\n      push(errors, \`${'${path}'}.qc.reviewed_at\`, "cannot be later than approval.approved_at");\n    }\n    if (validIsoDate(item.published_at) && reviewedAt > item.published_at) {\n      push(errors, \`${'${path}'}.qc.reviewed_at\`, "cannot be later than published_at");\n    }\n  }\n\n  if (Array.isArray(item.source_card_ids)) {`;
  text = replaceOnce(text, anchor, block, "Monthly Brief QC chronology");
  fs.writeFileSync(path, text);
}

// 5) Regression coverage for 월호 command semantics.
{
  const path = "__tests__/monthlyBriefProductBoundary.test.js";
  let text = fs.readFileSync(path, "utf8");
  const anchor = `  it("does not let Monthly Brief create wording fall into the automatic generator", () => {`;
  const insert = `  it("preserves optional 월호 qualifiers in official Monthly Brief commands", () => {\n    expect(detectAppCommand("8월호 월간 브리프 보여줘", [], opts())).toEqual({ type: "monthly_show", month: "2026-08" });\n    expect(detectAppCommand("2025년 8월호 월간 브리프 만들어줘", [], opts())).toMatchObject({ type: "monthly_show", month: "2025-08", requested_action: "create" });\n  });\n\n${anchor}`;
  text = replaceOnce(text, anchor, insert, "Monthly Brief 월호 regression");
  fs.writeFileSync(path, text);
}

// 6) Regression coverage for Quick Analysis prose labels.
{
  const path = "__tests__/quickAnalysisLabels.test.js";
  let text = fs.readFileSync(path, "utf8");
  text = replaceOnce(
    text,
    'import { calendarQuickAnalysisLabel, quickAnalysisChipLabel } from "../src/quickAnalysisLabels.js";',
    'import { calendarQuickAnalysisLabel, quickAnalysisChipLabel, quickAnalysisProseLabel } from "../src/quickAnalysisLabels.js";',
    "Quick Analysis prose test import",
  );
  const anchor = `  it("preserves custom and duplicate disambiguation without saying 월간", () => {`;
  const insert = `  it("keeps rolling unread prose classified as Quick Analysis", () => {\n    expect(quickAnalysisProseLabel({ period: "monthly", label: "30일 09-08" })).toBe("30일 빠른 분석");\n    expect(quickAnalysisProseLabel({ period: "monthly", group: "custom", label: "🧩 30일 09-08" })).toBe("🧩 30일 빠른 분석");\n    expect(quickAnalysisProseLabel({ period: "weekly", label: "주간 09-08" })).toBe("주간 09-08 브리프");\n  });\n\n${anchor}`;
  text = replaceOnce(text, anchor, insert, "Quick Analysis prose regression");
  fs.writeFileSync(path, text);
}

// 7) Regression coverage for QC chronology.
{
  const path = "__tests__/monthlyBriefPublication.test.js";
  let text = fs.readFileSync(path, "utf8");
  const anchor = `  it("rejects key-flow evidence outside the governed source set", () => {`;
  const insert = `  it("requires QC review to complete before approval and publication", () => {\n    const afterApproval = sample({\n      qc: { ...sample().qc, reviewed_at: "2026-09-09" },\n      approval: { ...sample().approval, approved_at: "2026-09-08" },\n      published_at: "2026-09-10",\n    });\n    expect(validateMonthlyBriefItem(afterApproval).join("\\n")).toContain("cannot be later than approval.approved_at");\n\n    const afterPublication = sample({\n      qc: { ...sample().qc, reviewed_at: "2026-09-10" },\n      approval: { ...sample().approval, approved_at: "2026-09-10" },\n      published_at: "2026-09-09",\n    });\n    const errors = validateMonthlyBriefItem(afterPublication).join("\\n");\n    expect(errors).toContain("qc.reviewed_at");\n    expect(errors).toContain("cannot be later than published_at");\n  });\n\n${anchor}`;
  text = replaceOnce(text, anchor, insert, "Monthly Brief QC chronology regression");
  fs.writeFileSync(path, text);
}
