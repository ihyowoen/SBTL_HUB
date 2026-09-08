import fs from "node:fs";

const path = "src/StrategicBriefPanel.jsx";
let text = fs.readFileSync(path, "utf8");

function once(from, to, label) {
  const i = text.indexOf(from);
  if (i < 0) throw new Error(`missing anchor: ${label}`);
  if (text.indexOf(from, i + from.length) >= 0) throw new Error(`non-unique anchor: ${label}`);
  text = text.slice(0, i) + to + text.slice(i + from.length);
}

once(
  'import { isOfficialStrategicBrief, validateStrategicBriefLibrary } from "../lib/brief/strategicPublication.js";\n',
  'import { isOfficialStrategicBrief, validateStrategicBriefLibrary } from "../lib/brief/strategicPublication.js";\nimport { selectStrategicIssue } from "./strategicBriefSelection.js";\n',
  "selection policy import",
);

once(
  '  useEffect(() => {\n    if (!items.length) { setSelectedId(null); return; }\n    if (requested) {\n      const exact = items.find((it) => (!requested.edition || it.edition === requested.edition) && (!requested.month || it.month === requested.month));\n      if (exact) { setSelectedId(exact.id); return; }\n    }\n    setSelectedId((cur) => items.some((it) => it.id === cur) ? cur : items[0].id);\n  }, [items, requested]);\n\n  const shown = items.find((it) => it.id === selectedId) || items[0] || null;\n',
  '  useEffect(() => {\n    if (!items.length) { setSelectedId(null); return; }\n    if (requested) {\n      const { issue } = selectStrategicIssue(items, requested, selectedId);\n      setSelectedId(issue?.id || null);\n      return;\n    }\n    setSelectedId((cur) => items.some((it) => it.id === cur) ? cur : items[0].id);\n  }, [items, requested]);\n\n  const { issue: shown, requestMissing } = selectStrategicIssue(items, requested, selectedId);\n  const requestedLabel = requested?.edition || (requested?.month ? `${requested.month} 월간 전략 브리핑` : "요청한 공식 월간 전략 브리핑");\n',
  "strict requested issue selection",
);

once(
  '      {library && !loadError && items.length === 0 && (\n        <div style={{ borderRadius: 12, padding: "14px", background: t.card2, border: `1px solid ${t.brd}` }}>\n          <div style={{ fontSize: 13, fontWeight: 900, color: t.tx }}>편집 중 · 아직 공식 발행본 없음</div>\n          <div style={{ marginTop: 5, fontSize: 11, color: t.sub, lineHeight: 1.65, wordBreak: "keep-all" }}>공식 VOL.xx가 승인되기 전에는 자동으로 월간 전략 브리핑을 만들지 않습니다. 아래 빠른 분석은 조사·탐색용으로만 사용할 수 있습니다.</div>\n        </div>\n      )}\n',
  '      {library && !loadError && requestMissing && (\n        <div style={{ borderRadius: 12, padding: "14px", background: t.card2, border: `1px solid ${t.brd}` }}>\n          <div style={{ fontSize: 13, fontWeight: 900, color: t.tx }}>편집 중 · {requestedLabel} 공식 발행본 없음</div>\n          <div style={{ marginTop: 5, fontSize: 11, color: t.sub, lineHeight: 1.65, wordBreak: "keep-all" }}>요청한 공식본이 없어서 다른 VOL이나 자동 분석으로 대체하지 않습니다. 승인 후 이 자리에 표시됩니다.</div>\n        </div>\n      )}\n      {library && !loadError && !requested && items.length === 0 && (\n        <div style={{ borderRadius: 12, padding: "14px", background: t.card2, border: `1px solid ${t.brd}` }}>\n          <div style={{ fontSize: 13, fontWeight: 900, color: t.tx }}>편집 중 · 아직 공식 발행본 없음</div>\n          <div style={{ marginTop: 5, fontSize: 11, color: t.sub, lineHeight: 1.65, wordBreak: "keep-all" }}>공식 VOL.xx가 승인되기 전에는 자동으로 월간 전략 브리핑을 만들지 않습니다. 아래 빠른 분석은 조사·탐색용으로만 사용할 수 있습니다.</div>\n        </div>\n      )}\n',
  "requested issue missing state",
);

once(
  '{items.map((it) => <button key={it.id} onClick={() => setSelectedId(it.id)} aria-pressed={shown.id === it.id}',
  '{items.map((it) => <button key={it.id} onClick={() => { setRequested(null); setSelectedId(it.id); }} aria-pressed={shown.id === it.id}',
  "manual issue selection clears request",
);

fs.writeFileSync(path, text);
console.log("Official Strategic Brief reader now has strict no-fallback request semantics");
