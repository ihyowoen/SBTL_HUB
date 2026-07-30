import fs from "node:fs";

function replaceOnce(file, before, after) {
  const current = fs.readFileSync(file, "utf8");
  if (current.includes(after)) return;
  const first = current.indexOf(before);
  if (first < 0) throw new Error(`Expected snippet not found in ${file}`);
  if (current.indexOf(before, first + before.length) >= 0) throw new Error(`Snippet is not unique in ${file}`);
  fs.writeFileSync(file, current.slice(0, first) + after + current.slice(first + before.length));
}

function replaceBetween(file, startMarker, endMarker, replacement) {
  const current = fs.readFileSync(file, "utf8");
  if (current.includes(replacement)) return;
  const start = current.indexOf(startMarker);
  if (start < 0) throw new Error(`Start marker not found in ${file}`);
  const endStart = current.indexOf(endMarker, start);
  if (endStart < 0) throw new Error(`End marker not found in ${file}`);
  const end = endStart + endMarker.length;
  fs.writeFileSync(file, current.slice(0, start) + replacement + current.slice(end));
}

function literal(strings) {
  return strings.raw[0].split("\\`").join("`").split("\\${").join("${");
}

replaceOnce(
  "api/chat.js",
  'import { synthesizeScout, synthesizeAnalyst, synthesizeRedTeam } from "../lib/chat/consultation.js";\n',
  'import { synthesizeScout, synthesizeAnalyst, synthesizeRedTeam } from "../lib/chat/consultation.js";\nimport { enrichNewsWithOgImages } from "../lib/chat/retrieve/ogExtractor.js";\n',
);

const synthStart = "    const synthesis = await synthesize({";
const synthEnd = '    console.log(`[chat-synth] path=${synthesis?.meta?.path} used_llm=${synthesis?.used_llm} delegate=${synthesis?.delegate?.to || "-"}`);';
const synthReplacement = [
  '    // OG fetch는 LLM 합성과 병렬 실행해 체감 지연을 최소화한다. trustedCards는',
  '    // 서버가 방금 로드한 정본이므로 context로 주입된 임의 URL은 네트워크 요청 대상이 아니다.',
  '    const ogImageTask = parsed.topic === "news" && (retrieval.cards || []).length',
  '      ? enrichNewsWithOgImages(retrieval.cards, { trustedCards: data.cards || [] })',
  '      : Promise.resolve({ cards: retrieval.cards || [], meta: { attempted: 0, found: 0, deduped: 0, skipped_untrusted: 0, latency_ms: 0 } });',
  '',
  '    const synthesis = await synthesize({',
  '      parsed,',
  '      resolved: resolvedCtx.resolved,',
  '      retrieval,',
  '      personal: { watch_terms: watchTerms },',
  '    });',
  '    const ogImageResult = await ogImageTask;',
  '    retrieval = {',
  '      ...retrieval,',
  '      cards: ogImageResult.cards,',
  '      _reasons: [...(retrieval._reasons || []), `og_images:${ogImageResult.meta.found}/${ogImageResult.meta.attempted}`],',
  '    };',
  '    console.log(`[chat-synth] path=${synthesis?.meta?.path} used_llm=${synthesis?.used_llm} delegate=${synthesis?.delegate?.to || "-"} og=${ogImageResult.meta.found}/${ogImageResult.meta.attempted}`);',
].join("\n");
replaceBetween("api/chat.js", synthStart, synthEnd, synthReplacement);

replaceOnce(
  "api/chat.js",
  '      debug: expandMeta ? { ...debugBase, query_expand: expandMeta } : debugBase,\n',
  '      debug: { ...debugBase, ...(expandMeta ? { query_expand: expandMeta } : {}), og_image: ogImageResult.meta },\n',
);

replaceOnce(
  "lib/chat/common.js",
  '    gist: card?.g || "",\n',
  '    gist: card?.g || "",\n    image: card?.image || card?.ogImage || card?.og_image || "",\n',
);

replaceOnce(
  "src/App.jsx",
  'import StoryNewsItem from "./story/StoryNewsItem";\n',
  'import StoryNewsItem, { assignCardCoverImages } from "./story/StoryNewsItem";\n',
);

const newCards = literal`                  {(() => {
                    const chatCards = Array.isArray(m.cards) ? m.cards : [];
                    const fallbackImages = assignCardCoverImages(chatCards, { alreadyUsed: chatCards.map((card) => card.image).filter(Boolean) });
                    return chatCards.map((card, j) => {
                      const fallbackImage = fallbackImages[j] || "";
                      const image = card.image || fallbackImage;
                      const cardStyle = { display: "block", background: dark ? "#151B26" : "#f8f9fc", borderRadius: 10, padding: 0, overflow: "hidden", marginTop: 6, cursor: card.url ? "pointer" : "default", border: \`1px solid \${t.brd}\`, textDecoration: "none" };
                      const imageBlock = image ? <img src={image} data-fallback={card.image && fallbackImage && card.image !== fallbackImage ? fallbackImage : ""} alt={\`\${card.title || "뉴스 카드"} 관련 이미지\`} loading="lazy" decoding="async" referrerPolicy="no-referrer" onError={(e) => { const fallback = e.currentTarget.dataset.fallback; if (fallback) { e.currentTarget.dataset.fallback = ""; e.currentTarget.src = fallback; } else { e.currentTarget.style.display = "none"; } }} style={{ display: "block", width: "100%", height: 112, objectFit: "cover", background: dark ? "#10151F" : "#E9EDF4" }} /> : null;
                      const cardContent = <>{imageBlock}<div style={{ padding: "10px 12px" }}><div style={{ fontSize: 12, fontWeight: 700, color: t.tx }}>{SIG_L[card.signal] || SIG_L[card.s] || "INFO"} {card.title}</div>{card.subtitle && <div style={{ fontSize: 11, color: t.sub, marginTop: 3 }}>{card.subtitle}</div>}{card.gist && <div style={{ fontSize: 10, color: t.cyan, marginTop: 4, lineHeight: 1.5, opacity: 0.85 }}>💡 {card.gist}</div>}<div style={{ fontSize: 10, color: t.sub, marginTop: 4, fontFamily: "'JetBrains Mono',monospace" }}>{fmtDate(card.date)} · {card.region} · {card.source || "source"}</div>{card.url && <div style={{ fontSize: 10, color: t.cyan, marginTop: 4, fontWeight: 700 }}>→ 원문 보기 ↗</div>}</div></>;
                      return card.url ? <a key={j} id={\`chat-card-\${i}-\${j + 1}\`} href={card.url} target="_blank" rel="noopener noreferrer" aria-label={\`Open article: \${card.title}\`} onClick={() => markCardSelected(card)} style={cardStyle}>{cardContent}</a> : <div key={j} id={\`chat-card-\${i}-\${j + 1}\`} style={cardStyle} onClick={() => markCardSelected(card)}>{cardContent}</div>;
                    });
                  })()}`;
replaceBetween(
  "src/App.jsx",
  "                  {m.cards?.map((card, j) => {",
  "                  })}",
  newCards,
);

for (const temp of ["scripts/apply-og-image-patch.mjs", ".github/workflows/apply-og-image-patch.yml"]) {
  try { fs.unlinkSync(temp); } catch { /* noop */ }
}

console.log("OG image patch applied");
