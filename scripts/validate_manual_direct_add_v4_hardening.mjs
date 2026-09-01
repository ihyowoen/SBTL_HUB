#!/usr/bin/env node
import { readFileSync } from "node:fs";
import { isDeepStrictEqual } from "node:util";

class ValidationError extends Error {
  constructor(code, message) { super(message); this.code = code; }
}
const fail = (code, message) => { throw new ValidationError(code, message); };
const readJson = (path, label) => {
  try { return JSON.parse(readFileSync(path, "utf8").replace(/^\uFEFF/, "")); }
  catch (error) { fail("BLOCKED_MANUAL_DIRECT_ADD_V4_HARDENING", `${label}: ${error.message}`); }
};
const same = (a, b) => isDeepStrictEqual(a, b);
const cardMap = (doc, label) => {
  if (!Array.isArray(doc?.cards)) fail("BLOCKED_MANUAL_DIRECT_ADD_V4_HARDENING", `${label}.cards must be an array`);
  return new Map(doc.cards.map((card) => [card.id, card]));
};
const MIGRATION_MUTABLE_FIELDS = new Set(["id", "date", "region"]);
const RELATED_CONTAINERS = ["related", "related_ids", "related_lineage"];
const FORMAL_RUN_FIELDS = new Set([
  "stage_a_validity_status",
  "stage_b_validity_status",
  "stage_c_validity_status",
  "final_qc_status",
  "merge_status",
  "pipeline_lineage",
  "publish_ready",
  "github_merge_ready",
  "production_verified",
]);
const GOVERNED_PUBLISH_STATES = new Set(["publish_ready", "github_merge_ready", "production_verified"]);
const RFC3339 = /^(\d{4})-(\d{2})-(\d{2})T(\d{2}):(\d{2}):(\d{2})(?:\.\d+)?(?:Z|[+-](\d{2}):(\d{2}))$/;

function changedTopLevelFields(before, after) {
  const keys = new Set([...Object.keys(before || {}), ...Object.keys(after || {})]);
  return [...keys].filter((key) => !same(before?.[key], after?.[key])).sort();
}

function validateStrictRfc3339(value) {
  if (typeof value !== "string") fail("BLOCKED_MANUAL_DIRECT_ADD_TIMESTAMP", "output_updated must be an RFC3339 string");
  const match = value.match(RFC3339);
  if (!match) fail("BLOCKED_MANUAL_DIRECT_ADD_TIMESTAMP", `output_updated must be RFC3339 — ${value}`);
  const [, ys, ms, ds, hs, mins, ss, offsetHs, offsetMins] = match;
  const year = Number(ys), month = Number(ms), day = Number(ds);
  const hour = Number(hs), minute = Number(mins), second = Number(ss);
  if (hour > 23 || minute > 59 || second > 59 || Number(offsetHs || 0) > 23 || Number(offsetMins || 0) > 59) {
    fail("BLOCKED_MANUAL_DIRECT_ADD_TIMESTAMP", `output_updated has an invalid time/offset — ${value}`);
  }
  const probe = new Date(Date.UTC(year, month - 1, day));
  if (probe.getUTCFullYear() !== year || probe.getUTCMonth() !== month - 1 || probe.getUTCDate() !== day) {
    fail("BLOCKED_MANUAL_DIRECT_ADD_TIMESTAMP", `output_updated contains a nonexistent calendar date — ${value}`);
  }
  if (Number.isNaN(Date.parse(value))) fail("BLOCKED_MANUAL_DIRECT_ADD_TIMESTAMP", `output_updated is not parseable — ${value}`);
}

function validateMigrationContent(manifest, baseMap, fullMap) {
  for (const migration of manifest.operations?.id_migration || []) {
    const before = baseMap.get(migration.old_id);
    const after = fullMap.get(migration.new_id);
    if (!before || !after) fail("BLOCKED_MANUAL_DIRECT_ADD_MIGRATION_SCOPE", `migration card missing ${migration.old_id} → ${migration.new_id}`);
    const changed = changedTopLevelFields(before, after);
    const forbidden = changed.filter((field) => !MIGRATION_MUTABLE_FIELDS.has(field));
    if (forbidden.length) {
      fail(
        "BLOCKED_MANUAL_DIRECT_ADD_MIGRATION_SCOPE",
        `${migration.old_id} → ${migration.new_id}: migration may change only id/date/region; forbidden=[${forbidden.join(",")}]`,
      );
    }
  }
}

function fabricatedFormalFields(card) {
  const fields = [...FORMAL_RUN_FIELDS].filter((field) => Object.prototype.hasOwnProperty.call(card, field));
  if (GOVERNED_PUBLISH_STATES.has(card?.state)) fields.push(`state=${card.state}`);
  return fields;
}

function validateAddedCards(manifest, baseMap, fullMap) {
  for (const id of manifest.operations?.add || []) {
    if (baseMap.has(id) || !fullMap.has(id)) fail("BLOCKED_MANUAL_DIRECT_ADD_V4_HARDENING", `invalid added card ${id}`);
    const card = fullMap.get(id);
    if (Object.prototype.hasOwnProperty.call(card, "related")) {
      if (!Array.isArray(card.related) || card.related.length !== 0) {
        fail("BLOCKED_MANUAL_DIRECT_ADD_RELATED", `${id}: direct-added card must leave related empty; establish lineage through formal Related review`);
      }
    }
    if (Object.prototype.hasOwnProperty.call(card, "related_ids")) {
      if (!Array.isArray(card.related_ids) || card.related_ids.length !== 0) {
        fail("BLOCKED_MANUAL_DIRECT_ADD_RELATED", `${id}: direct-added card must leave related_ids empty`);
      }
    }
    if (Object.prototype.hasOwnProperty.call(card, "related_lineage")) {
      const lineage = card.related_lineage;
      if (lineage !== null && (!lineage || typeof lineage !== "object" || Array.isArray(lineage)
        || (Array.isArray(lineage.related_ids) && lineage.related_ids.length !== 0))) {
        fail("BLOCKED_MANUAL_DIRECT_ADD_RELATED", `${id}: direct-added related_lineage may not establish targets`);
      }
    }
    const fabricated = fabricatedFormalFields(card);
    if (fabricated.length) {
      fail(
        "BLOCKED_MANUAL_DIRECT_ADD_FORMAL_PROVENANCE",
        `${id}: direct-add cannot claim formal-run state/provenance fields [${fabricated.join(",")}]`,
      );
    }
  }
}

function validateUpdatedCards(manifest, baseMap, fullMap) {
  for (const id of manifest.operations?.update || []) {
    const before = baseMap.get(id);
    const after = fullMap.get(id);
    if (!before || !after) fail("BLOCKED_MANUAL_DIRECT_ADD_V4_HARDENING", `update card missing ${id}`);
    for (const field of RELATED_CONTAINERS) {
      if (!same(before?.[field], after?.[field])) {
        fail("BLOCKED_MANUAL_DIRECT_ADD_RELATED", `${id}: direct update cannot change ${field}; use formal Related review`);
      }
    }
    const changedFormal = [...FORMAL_RUN_FIELDS].filter((field) => !same(before?.[field], after?.[field]));
    if (!same(before?.state, after?.state) && (GOVERNED_PUBLISH_STATES.has(before?.state) || GOVERNED_PUBLISH_STATES.has(after?.state))) {
      changedFormal.push("state");
    }
    if (changedFormal.length) {
      fail(
        "BLOCKED_MANUAL_DIRECT_ADD_FORMAL_PROVENANCE",
        `${id}: direct update cannot add/change formal publication state [${changedFormal.join(",")}]`,
      );
    }
  }
}

function validate(manifest, base, full) {
  if (manifest?.schema !== "manual_direct_add_v2") {
    fail("BLOCKED_MANUAL_DIRECT_ADD_V4_HARDENING", "active hardening accepts manual_direct_add_v2 only");
  }
  if (manifest.formal_full_run_claimed !== false) {
    fail("BLOCKED_MANUAL_DIRECT_ADD_FORMAL_PROVENANCE", "manual direct-add must declare formal_full_run_claimed=false");
  }
  validateStrictRfc3339(manifest.output_updated);
  const baseMap = cardMap(base, "base");
  const fullMap = cardMap(full, "full");
  validateMigrationContent(manifest, baseMap, fullMap);
  validateAddedCards(manifest, baseMap, fullMap);
  validateUpdatedCards(manifest, baseMap, fullMap);
  return {
    migrations_checked: (manifest.operations?.id_migration || []).length,
    additions_checked: (manifest.operations?.add || []).length,
    updates_checked: (manifest.operations?.update || []).length,
  };
}

function selfTest() {
  const base = { cards: [
    { id: "2026-01-01_KR_01", date: "2026-01-01", region: "KR", title: "A", urls: ["https://a.example"], related: [], related_ids: [], related_lineage: { relation_type: "new_unrelated_event", related_ids: [] } },
    { id: "2026-01-03_KR_01", date: "2026-01-03", region: "KR", title: "U", urls: ["https://u.example"], related: [], related_ids: [], related_lineage: { relation_type: "new_unrelated_event", related_ids: [] } },
  ] };
  const manifest = {
    schema: "manual_direct_add_v2",
    formal_full_run_claimed: false,
    output_updated: "2026-08-29T22:30:00+09:00",
    operations: {
      add: ["2026-01-02_KR_01"],
      update: ["2026-01-03_KR_01"],
      id_migration: [{ old_id: "2026-01-01_KR_01", new_id: "2025-12-31_KR_01" }],
    },
  };
  const good = { cards: [
    { id: "2025-12-31_KR_01", date: "2025-12-31", region: "KR", title: "A", urls: ["https://a.example"], related: [], related_ids: [], related_lineage: { relation_type: "new_unrelated_event", related_ids: [] } },
    { id: "2026-01-03_KR_01", date: "2026-01-03", region: "KR", title: "U corrected", urls: ["https://u.example"], related: [], related_ids: [], related_lineage: { relation_type: "new_unrelated_event", related_ids: [] } },
    { id: "2026-01-02_KR_01", date: "2026-01-02", region: "KR", title: "B", related: [], related_ids: [] },
  ] };
  validate(manifest, base, good);

  const reordered = { cards: [
    { title: "A", related_lineage: { related_ids: [], relation_type: "new_unrelated_event" }, related_ids: [], related: [], urls: ["https://a.example"], region: "KR", date: "2025-12-31", id: "2025-12-31_KR_01" },
    good.cards[1], good.cards[2],
  ] };
  validate(manifest, base, reordered);

  const contentSwap = structuredClone(good);
  contentSwap.cards[0].title = "Different event";
  let migrationBlocked = false;
  try { validate(manifest, base, contentSwap); }
  catch (error) { migrationBlocked = error instanceof ValidationError && error.code === "BLOCKED_MANUAL_DIRECT_ADD_MIGRATION_SCOPE"; }
  if (!migrationBlocked) throw new Error("self-test failed to reject migration content mutation");

  const withRelated = structuredClone(good);
  withRelated.cards[2].related = ["2025-12-31_KR_01"];
  let relatedBlocked = false;
  try { validate(manifest, base, withRelated); }
  catch (error) { relatedBlocked = error instanceof ValidationError && error.code === "BLOCKED_MANUAL_DIRECT_ADD_RELATED"; }
  if (!relatedBlocked) throw new Error("self-test failed to reject direct-add Related edge");

  const updateLineage = structuredClone(good);
  updateLineage.cards[1].related_lineage = { relation_type: "direct_follow_up", related_ids: ["2026-01-02_KR_01"] };
  let updateRelatedBlocked = false;
  try { validate(manifest, base, updateLineage); }
  catch (error) { updateRelatedBlocked = error instanceof ValidationError && error.code === "BLOCKED_MANUAL_DIRECT_ADD_RELATED"; }
  if (!updateRelatedBlocked) throw new Error("self-test failed to reject direct update Related mutation");

  const withFormalState = structuredClone(good);
  withFormalState.cards[2].publish_ready = true;
  let provenanceBlocked = false;
  try { validate(manifest, base, withFormalState); }
  catch (error) { provenanceBlocked = error instanceof ValidationError && error.code === "BLOCKED_MANUAL_DIRECT_ADD_FORMAL_PROVENANCE"; }
  if (!provenanceBlocked) throw new Error("self-test failed to reject fabricated publication state");

  const withStateAlias = structuredClone(good);
  withStateAlias.cards[2].state = "github_merge_ready";
  let stateAliasBlocked = false;
  try { validate(manifest, base, withStateAlias); }
  catch (error) { stateAliasBlocked = error instanceof ValidationError && error.code === "BLOCKED_MANUAL_DIRECT_ADD_FORMAL_PROVENANCE"; }
  if (!stateAliasBlocked) throw new Error("self-test failed to reject governed publication state alias");

  const invalidDate = structuredClone(manifest);
  invalidDate.output_updated = "2026-02-30T12:00:00Z";
  let invalidDateBlocked = false;
  try { validate(invalidDate, base, good); }
  catch (error) { invalidDateBlocked = error instanceof ValidationError && error.code === "BLOCKED_MANUAL_DIRECT_ADD_TIMESTAMP"; }
  if (!invalidDateBlocked) throw new Error("self-test failed to reject nonexistent calendar date");

  console.log("PASS: manual direct-add V4 hardening closes migration, Related, publication-state aliases, and timestamp bypasses");
}

const args = process.argv.slice(2);
const arg = (name) => { const index = args.indexOf(name); return index >= 0 ? args[index + 1] : null; };
try {
  if (args.includes("--self-test")) { selfTest(); process.exit(0); }
  const manifestPath = arg("--manifest");
  const basePath = arg("--base");
  const fullPath = arg("--full");
  if (!manifestPath || !basePath || !fullPath) fail("INVALID_ARGUMENT", "--manifest --base --full required");
  const result = validate(readJson(manifestPath, "manifest"), readJson(basePath, "base"), readJson(fullPath, "full"));
  console.log(JSON.stringify({ status: "PASS", ...result }, null, 2));
  console.log(`PASS: manual direct-add V4 hardening; add=${result.additions_checked}; update=${result.updates_checked}; migration=${result.migrations_checked}`);
} catch (error) {
  if (error instanceof ValidationError) { console.error(`FAIL [${error.code}]: ${error.message}`); process.exit(1); }
  throw error;
}
