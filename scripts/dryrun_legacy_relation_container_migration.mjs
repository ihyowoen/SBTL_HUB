#!/usr/bin/env node
import { readFileSync, writeFileSync } from "node:fs";

const input = process.argv[2] || "data/cards.full.json";
const output = process.argv[3] || "legacy-related-migration-candidate.full.json";
const doc = JSON.parse(readFileSync(input, "utf8").replace(/^\uFEFF/, ""));
if (!doc || !Array.isArray(doc.cards)) throw new Error("cards array required");

const ids = new Set(doc.cards.map((card) => card?.id));
let initialized = 0;
let skippedDanglingCards = 0;
let alreadyReady = 0;
const initializedIds = [];
const skippedIds = [];

for (const card of doc.cards) {
  const related = Array.isArray(card.related) ? card.related : [];
  const lineageReady = card.related_lineage && typeof card.related_lineage === "object" && !Array.isArray(card.related_lineage) && Array.isArray(card.related_lineage.related_ids);
  if (lineageReady) {
    alreadyReady += 1;
    continue;
  }
  const hasDanglingPublishedEdge = related.some((target) => !ids.has(target));
  if (hasDanglingPublishedEdge) {
    skippedDanglingCards += 1;
    skippedIds.push(card.id);
    continue;
  }
  // Neutral legacy container initialization only: preserve the already-published related[] decision
  // byte-for-byte in meaning, without inventing relation_type/reason/stage/direction.
  card.related_lineage = { related_ids: [...related] };
  initialized += 1;
  initializedIds.push(card.id);
}

writeFileSync(output, `${JSON.stringify(doc, null, 2)}\n`);
console.log(`MIGRATION_DRYRUN_SUMMARY=${JSON.stringify({
  total_cards: doc.cards.length,
  already_ready: alreadyReady,
  initialized,
  skipped_dangling_cards: skippedDanglingCards,
  final_ready_count: alreadyReady + initialized,
  initialized_nonempty_related: initializedIds.filter((id) => {
    const card = doc.cards.find((item) => item.id === id);
    return Array.isArray(card.related) && card.related.length > 0;
  }).length,
})}`);
console.log(`MIGRATION_DRYRUN_SKIPPED_IDS=${JSON.stringify(skippedIds)}`);
console.log("PASS: generated neutral legacy relation-container migration candidate");
