#!/usr/bin/env node
import { readFileSync } from "node:fs";

class ValidationError extends Error {
  constructor(code, message) { super(message); this.code = code; }
}
const fail = (code, message) => { throw new ValidationError(code, message); };
const readJson = (path, label) => {
  try { return JSON.parse(readFileSync(path, "utf8").replace(/^\uFEFF/, "")); }
  catch (error) { fail("BLOCKED_MANUAL_DIRECT_ADD_V4_HARDENING", `${label}: ${error.message}`); }
};
const same = (a, b) => JSON.stringify(a) === JSON.stringify(b);
const cardMap = (doc, label) => {
  if (!Array.isArray(doc?.cards)) fail("BLOCKED_MANUAL_DIRECT_ADD_V4_HARDENING", `${label}.cards must be an array`);
  return new Map(doc.cards.map((card) => [card.id, card]));
};
const MIGRATION_MUTABLE_FIELDS = new Set(["id", "date", "region"]);
const FORMAL_RUN_FIELDS = new Set([
  "stage_a_validity_status",
  "stage_b_validity_status",
  "stage_c_validity_status",
  "final_qc_status",
  "merge_status",
  "pipeline_lineage",
]);

function changedTopLevelFields(before, after) {
  const keys = new Set([...Object.keys(before || {}), ...Object.keys(after || {})]);
  return [...keys].filter((key) => !same(before?.[key], after?.[key])).sort();
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
    const fabricated = [...FORMAL_RUN_FIELDS].filter((field) => Object.prototype.hasOwnProperty.call(card, field));
    if (fabricated.length) {
      fail(
        "BLOCKED_MANUAL_DIRECT_ADD_FORMAL_PROVENANCE",
        `${id}: direct-add cannot claim formal-run state/provenance fields [${fabricated.join(",")}]`,
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
  const baseMap = cardMap(base, "base");
  const fullMap = cardMap(full, "full");
  validateMigrationContent(manifest, baseMap, fullMap);
  validateAddedCards(manifest, baseMap, fullMap);
  return {
    migrations_checked: (manifest.operations?.id_migration || []).length,
    additions_checked: (manifest.operations?.add || []).length,
  };
}

function selfTest() {
  const base = { cards: [{ id: "2026-01-01_KR_01", date: "2026-01-01", region: "KR", title: "A", urls: ["https://a.example"], related: [] }] };
  const manifest = {
    schema: "manual_direct_add_v2",
    formal_full_run_claimed: false,
    operations: { add: ["2026-01-02_KR_01"], update: [], id_migration: [{ old_id: "2026-01-01_KR_01", new_id: "2025-12-31_KR_01" }] },
  };
  const good = { cards: [
    { id: "2025-12-31_KR_01", date: "2025-12-31", region: "KR", title: "A", urls: ["https://a.example"], related: [] },
    { id: "2026-01-02_KR_01", date: "2026-01-02", region: "KR", title: "B", related: [] },
  ] };
  validate(manifest, base, good);

  const contentSwap = structuredClone(good);
  contentSwap.cards[0].title = "Different event";
  let migrationBlocked = false;
  try { validate(manifest, base, contentSwap); }
  catch (error) { migrationBlocked = error instanceof ValidationError && error.code === "BLOCKED_MANUAL_DIRECT_ADD_MIGRATION_SCOPE"; }
  if (!migrationBlocked) throw new Error("self-test failed to reject migration content mutation");

  const withRelated = structuredClone(good);
  withRelated.cards[1].related = ["2025-12-31_KR_01"];
  let relatedBlocked = false;
  try { validate(manifest, base, withRelated); }
  catch (error) { relatedBlocked = error instanceof ValidationError && error.code === "BLOCKED_MANUAL_DIRECT_ADD_RELATED"; }
  if (!relatedBlocked) throw new Error("self-test failed to reject direct-add Related edge");

  const withFormalState = structuredClone(good);
  withFormalState.cards[1].final_qc_status = "PUBLISH_READY";
  let provenanceBlocked = false;
  try { validate(manifest, base, withFormalState); }
  catch (error) { provenanceBlocked = error instanceof ValidationError && error.code === "BLOCKED_MANUAL_DIRECT_ADD_FORMAL_PROVENANCE"; }
  if (!provenanceBlocked) throw new Error("self-test failed to reject fabricated formal provenance");

  console.log("PASS: manual direct-add V4 hardening closes migration, Related, and formal-provenance bypasses");
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
  console.log(`PASS: manual direct-add V4 hardening; add=${result.additions_checked}; migration=${result.migrations_checked}`);
} catch (error) {
  if (error instanceof ValidationError) { console.error(`FAIL [${error.code}]: ${error.message}`); process.exit(1); }
  throw error;
}
