import fs from "node:fs";

function replaceOnce(text, from, to, label) {
  const first = text.indexOf(from);
  if (first < 0) throw new Error(`${label}: anchor not found`);
  if (text.indexOf(from, first + from.length) >= 0) throw new Error(`${label}: anchor not unique`);
  return text.slice(0, first) + to + text.slice(first + from.length);
}

// 1) Accept the advertised "YYYY년 M월 월별 빠른 분석" wording as a calendar-month request.
{
  const path = "lib/chat/appCommand.js";
  let text = fs.readFileSync(path, "utf8");
  text = replaceOnce(
    text,
    'const PERIOD_TOKEN = "((?:\\\\d{4}년\\\\s*)?\\\\d{1,2}월(?:호)?|30일|주간|월간)";',
    'const PERIOD_TOKEN = "((?:\\\\d{4}년\\\\s*)?\\\\d{1,2}월(?:호)?(?:\\\\s*월별)?|30일|주간|월간)";',
    "calendar-month quick-analysis grammar",
  );
  fs.writeFileSync(path, text);
}

// 2) Avoid awkward "빠른 분석 브리프" phrasing in Kang when the shelf label is already an analysis label.
{
  const path = "src/kang.js";
  let text = fs.readFileSync(path, "utf8");
  text = replaceOnce(
    text,
    '      text: `${i.unreadBrief.label} 브리프 만들어뒀어 — 읽고 가.`,',
    '      text: `${i.unreadBrief.label}${String(i.unreadBrief.label).includes("분석") ? "" : " 브리프"} 만들어뒀어 — 읽고 가.`,',
    "Kang unread quick-analysis wording",
  );
  fs.writeFileSync(path, text);
}

// 3) Render the complete required refs[] metadata, including URL-less references.
{
  const path = "src/MonthlyBriefPanel.jsx";
  let text = fs.readFileSync(path, "utf8");
  const from = `            <div style={{ marginTop: 7, fontSize: 9.5, color: t.sub, lineHeight: 1.7, fontFamily: "'JetBrains Mono',monospace" }}>
              <div>source cards {shown.source_card_ids?.length || 0} · refs {shown.refs?.length || 0}</div>
              <div>main {shortSha(shown.source_baseline?.main_commit_sha)} · full {shortSha(shown.source_baseline?.full_blob_sha)}</div>
              <div>QC evidence/red-team/coherence/language = PASS · approval {shown.approval?.approved_at}</div>
            </div>`;
  const to = `            <div style={{ marginTop: 7, fontSize: 9.5, color: t.sub, lineHeight: 1.7, fontFamily: "'JetBrains Mono',monospace" }}>
              <div>source cards {shown.source_card_ids?.length || 0} · refs {shown.refs?.length || 0}</div>
              <div>main {shortSha(shown.source_baseline?.main_commit_sha)} · full {shortSha(shown.source_baseline?.full_blob_sha)}</div>
              <div>QC evidence/red-team/coherence/language = PASS · approval {shown.approval?.approved_at}</div>
              <div style={{ marginTop: 7, paddingTop: 7, borderTop: \`1px dashed \${t.brd}\`, display: "flex", flexDirection: "column", gap: 5 }}>
                {(shown.refs || []).map((r) => (
                  <div key={r.id} style={{ display: "flex", gap: 6, alignItems: "baseline", minWidth: 0 }}>
                    <span style={{ flexShrink: 0, color: t.cyan }}>[{r.n}]</span>
                    {r.url
                      ? <a href={r.url} target="_blank" rel="noreferrer" style={{ color: t.tx, textDecorationColor: t.brd, wordBreak: "keep-all" }}>{r.title}</a>
                      : <span style={{ color: t.tx, wordBreak: "keep-all" }}>{r.title}</span>}
                    <span style={{ flexShrink: 0, color: t.sub }}>{r.date}</span>
                  </div>
                ))}
              </div>
            </div>`;
  text = replaceOnce(text, from, to, "Monthly Brief public refs rendering");
  fs.writeFileSync(path, text);
}

console.log("PR #348 Codex fixes applied");
