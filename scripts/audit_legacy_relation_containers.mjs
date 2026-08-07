#!/usr/bin/env node
import { readFileSync, writeFileSync } from "node:fs";

const canonicalPath = process.argv[2] || "data/cards.full.json";
const legacyManifestPath = process.argv[3] || "docs/remediation/RELATED_LEGACY_DANGLING_MANIFEST_20260723.json";

const canonical = JSON.parse(readFileSync(canonicalPath, "utf8").replace(/^\uFEFF/, ""));
const legacyManifest = JSON.parse(readFileSync(legacyManifestPath, "utf8").replace(/^\uFEFF/, ""));

if (!canonical || !Array.isArray(canonical.cards)) throw new Error("canonical.cards array required");

const cards = canonical.cards;
const ids = cards.map((card) => card?.id).filter((id) => typeof id === "string" && id.trim());
const idSet = new Set(ids);
const duplicateCardIds = [...new Set(ids.filter((id, i) => ids.indexOf(id) !== i))].sort();
const legacyAffectedIds = new Set((legacyManifest.items || []).map((item) => item.card_id));

const missingRelated = [];
const missingLineageObject = [];
const missingLineageRelatedIds = [];
const nonemptyRelatedMissingLineage = [];
const emptyRelatedMissingLineage = [];
const danglingPublished = [];
const danglingLineage = [];
const selfPublished = [];
const selfLineage = [];
const duplicatePublished = [];
const duplicateLineage = [];
const relatedLineageMismatches = [];
const cardsWithNonemptyRelated = [];
const cardsWithValidContainers = [];

const duplicates = (arr) => [...new Set(arr.filter((value, i) => arr.indexOf(value) !== i))];
const symmetricDiff = (a, b) => {
  const as = new Set(a);
  const bs = new Set(b);
  return [...new Set([...a.filter((x) => !bs.has(x)), ...b.filter((x) => !as.has(x))])].sort();
};

for (const card of cards) {
  const id = card?.id ?? null;
  const relatedOk = Array.isArray(card?.related);
  const related = relatedOk ? card.related : [];
  const lineageOk = card?.related_lineage && typeof card.related_lineage === "object" && !Array.isArray(card.related_lineage);
  const lineageIdsOk = lineageOk && Array.isArray(card.related_lineage.related_ids);
  const lineageIds = lineageIdsOk ? card.related_lineage.related_ids : [];

  if (!relatedOk) missingRelated.push(id);
  if (!lineageOk) missingLineageObject.push(id);
  if (!lineageIdsOk) missingLineageRelatedIds.push(id);
  if (related.length > 0) cardsWithNonemptyRelated.push(id);
  if (relatedOk && lineageIdsOk) cardsWithValidContainers.push(id);

  if (!lineageIdsOk) {
    if (related.length > 0) nonemptyRelatedMissingLineage.push(id);
    else emptyRelatedMissingLineage.push(id);
  }

  for (const target of related) {
    if (target === id) selfPublished.push({ card_id: id, target_id: target });
    if (!idSet.has(target)) danglingPublished.push({ card_id: id, target_id: target, legacy_snapshot_card: legacyAffectedIds.has(id) });
  }
  for (const target of lineageIds) {
    if (target === id) selfLineage.push({ card_id: id, target_id: target });
    if (!idSet.has(target)) danglingLineage.push({ card_id: id, target_id: target, legacy_snapshot_card: legacyAffectedIds.has(id) });
  }

  const dupRel = duplicates(related);
  if (dupRel.length) duplicatePublished.push({ card_id: id, duplicate_ids: dupRel });
  const dupLin = duplicates(lineageIds);
  if (dupLin.length) duplicateLineage.push({ card_id: id, duplicate_ids: dupLin });

  if (relatedOk && lineageIdsOk) {
    const diff = symmetricDiff(related, lineageIds);
    if (diff.length) {
      relatedLineageMismatches.push({
        card_id: id,
        related,
        lineage_related_ids: lineageIds,
        symmetric_diff: diff,
      });
    }
  }
}

const currentDanglingCards = new Set(danglingPublished.map((x) => x.card_id));
const oldManifestRecheck = (legacyManifest.items || []).map((item) => {
  const card = cards.find((candidate) => candidate?.id === item.card_id);
  const related = Array.isArray(card?.related) ? card.related : [];
  const currentlyMissing = related.filter((target) => !idSet.has(target));
  return {
    card_id: item.card_id,
    card_still_exists: Boolean(card),
    old_missing_related_ids: item.missing_related_ids || [],
    current_related: related,
    current_missing_related_ids: currentlyMissing,
    still_dangling: currentlyMissing.length > 0,
  };
});

const report = {
  audit_version: "LEGACY_RELATION_CONTAINER_AUDIT_V1_20260808",
  baseline: {
    canonical_path: canonicalPath,
    canonical_updated: canonical.updated ?? null,
    declared_total: canonical.total ?? null,
    actual_card_count: cards.length,
    unique_id_count: idSet.size,
  },
  summary: {
    total_cards: cards.length,
    duplicate_card_id_count: duplicateCardIds.length,
    cards_with_nonempty_related: cardsWithNonemptyRelated.length,
    cards_with_valid_related_and_lineage_containers: cardsWithValidContainers.length,
    missing_or_nonarray_related_count: missingRelated.length,
    missing_or_invalid_related_lineage_object_count: missingLineageObject.length,
    missing_or_nonarray_related_lineage_related_ids_count: missingLineageRelatedIds.length,
    nonempty_related_but_missing_lineage_container_count: nonemptyRelatedMissingLineage.length,
    empty_related_and_missing_lineage_container_count: emptyRelatedMissingLineage.length,
    published_dangling_edge_count: danglingPublished.length,
    published_dangling_card_count: currentDanglingCards.size,
    lineage_dangling_edge_count: danglingLineage.length,
    published_self_link_count: selfPublished.length,
    lineage_self_link_count: selfLineage.length,
    published_duplicate_link_card_count: duplicatePublished.length,
    lineage_duplicate_link_card_count: duplicateLineage.length,
    related_vs_lineage_related_ids_mismatch_count: relatedLineageMismatches.length,
    old_manifest_affected_card_count: (legacyManifest.items || []).length,
    old_manifest_cards_still_dangling: oldManifestRecheck.filter((x) => x.still_dangling).length,
    current_dangling_cards_not_in_old_manifest: [...currentDanglingCards].filter((id) => !legacyAffectedIds.has(id)).length,
  },
  findings: {
    duplicate_card_ids: duplicateCardIds,
    missing_or_nonarray_related_ids: missingRelated,
    missing_or_invalid_related_lineage_object_ids: missingLineageObject,
    missing_or_nonarray_related_lineage_related_ids: missingLineageRelatedIds,
    nonempty_related_but_missing_lineage_container_ids: nonemptyRelatedMissingLineage,
    empty_related_and_missing_lineage_container_ids: emptyRelatedMissingLineage,
    published_dangling_edges: danglingPublished,
    lineage_dangling_edges: danglingLineage,
    published_self_links: selfPublished,
    lineage_self_links: selfLineage,
    published_duplicate_links: duplicatePublished,
    lineage_duplicate_links: duplicateLineage,
    related_vs_lineage_related_ids_mismatches: relatedLineageMismatches,
    old_manifest_recheck: oldManifestRecheck,
  },
};

writeFileSync("legacy-related-audit.json", `${JSON.stringify(report, null, 2)}\n`);
console.log(`AUDIT_SUMMARY_JSON=${JSON.stringify(report.summary)}`);
console.log(`AUDIT_DANGLING_JSON=${JSON.stringify(danglingPublished)}`);
console.log(`AUDIT_OLD_MANIFEST_RECHECK=${JSON.stringify(oldManifestRecheck)}`);
console.log(`AUDIT_NONEMPTY_MISSING_LINEAGE_IDS=${JSON.stringify(nonemptyRelatedMissingLineage)}`);
console.log(`AUDIT_RELATED_LINEAGE_MISMATCH_IDS=${JSON.stringify(relatedLineageMismatches.map((x) => x.card_id))}`);
console.log("PASS: legacy relation-container audit completed");
