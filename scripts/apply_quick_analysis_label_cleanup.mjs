import fs from "node:fs";

function replaceOnce(text, from, to, label) {
  const first = text.indexOf(from);
  if (first < 0) throw new Error(`${label}: anchor not found`);
  if (text.indexOf(from, first + from.length) >= 0) throw new Error(`${label}: anchor not unique`);
  return text.slice(0, first) + to + text.slice(first + from.length);
}

// App: keep storage key `monthly`, but never display it as the official Monthly Brief identity.
{
  const path = "src/App.jsx";
  let text = fs.readFileSync(path, "utf8");
  text = replaceOnce(
    text,
    'import MonthlyBriefPanel from "./MonthlyBriefPanel";',
    'import MonthlyBriefPanel from "./MonthlyBriefPanel";\nimport { quickAnalysisChipLabel } from "./quickAnalysisLabels.js";',
    "App quick-analysis label import",
  );

  const functionPattern = /function briefChipLabel\(e, nowYear, dupMonth = false\) \{[\s\S]*?\n\}/g;
  const matches = [...text.matchAll(functionPattern)];
  if (matches.length !== 1) throw new Error(`briefChipLabel function match count=${matches.length}`);
  text = text.replace(functionPattern, `function briefChipLabel(e, nowYear, dupMonth = false) {\n  return quickAnalysisChipLabel(e, nowYear, dupMonth);\n}`);

  // Clean misleading comments/examples that called automated window outputs “월간 브리프”.
  text = text.replaceAll("'월간 브리프 보여줘'", "'30일 빠른 분석 보여줘'");
  text = text.replaceAll('("월간 브리프 보여줘")', '("30일 빠른 분석 보여줘")');
  text = text.replaceAll('("5월 브리프 보여줘")', '("5월 빠른 분석 보여줘")');
  text = text.replaceAll('("월간/5월/5월 지역별 브리프 보여줘")', '("30일/5월 월별/5월 지역별 빠른 분석 보여줘")');

  fs.writeFileSync(path, text);
}

// Kang: stale calendar-month automation is a quick-analysis snapshot, not an official Monthly Brief.
{
  const path = "src/kang.js";
  let text = fs.readFileSync(path, "utf8");
  text = 'import { calendarQuickAnalysisLabel } from "./quickAnalysisLabels.js";\n\n' + text;
  text = replaceOnce(
    text,
    '      text: `${i.staleBrief.monthNum}월호에 발행 뒤 기사 ${i.staleBrief.drift}건이 더 붙었어 — 새 재료로 다시 뽑을 수 있어.`,\n      chip: `${i.staleBrief.monthNum}월호`, cmd: { type: "weekly_show", period: "monthly", month: i.staleBrief.month || null, group: i.staleBrief.group || null },',
    '      text: `${calendarQuickAnalysisLabel(i.staleBrief.month)}에 생성 뒤 기사 ${i.staleBrief.drift}건이 더 붙었어 — 새 재료로 다시 분석할 수 있어.`,\n      chip: calendarQuickAnalysisLabel(i.staleBrief.month), cmd: { type: "weekly_show", period: "monthly", month: i.staleBrief.month || null, group: i.staleBrief.group || null },',
    "Kang stale quick-analysis label",
  );
  fs.writeFileSync(path, text);
}

console.log("Quick Analysis display labels cleaned up");
