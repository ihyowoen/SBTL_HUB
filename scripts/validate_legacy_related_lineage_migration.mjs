#!/usr/bin/env node
import { readFileSync } from "node:fs";

class ValidationError extends Error {
  constructor(code, message) { super(message); this.code = code; }
}
const fail = (code, message) => { throw new ValidationError(code, message); };
const readJson = (path, label) => {
  try { return JSON.parse(readFileSync(path, "utf8").replace(/^\uFEFF/, "")); }
  catch (error) { fail("BLOCKED_LEGACY_LINEAGE_MIGRATION_INVALID", `${label}: ${error.message}`); }
};
const same = (a, b) => JSON.stringify(a) === JSON.stringify(b);
const validLineageContainer = (card) => card?.related_lineage && typeof card.related_lineage === "object" && !Array.isArray(card.related_lineage) && Array.isArray(card.related_lineage.related_ids);
const withoutKey = (object, key) => Object.fromEntries(Object.entries(object).filter(([k]) => k !== key));
const RFC3339_DATE_TIME = /^(\d{4})-(\d{2})-(\d{2})T(\d{2}):(\d{2}):(\d{2})(?:\.(\d+))?(Z|[+-]\d{2}:\d{2})$/;

function validateRfc3339DateTime(value) {
  if (typeof value !== "string") fail("BLOCKED_LEGACY_LINEAGE_MIGRATION_INVALID", "output_updated must be RFC3339 date-time");
  const match = RFC3339_DATE_TIME.exec(value);
  if (!match) fail("BLOCKED_LEGACY_LINEAGE_MIGRATION_INVALID", `output_updated must be RFC3339 date-time — ${value}`);
  const [, yearText, monthText, dayText, hourText, minuteText, secondText, , zone] = match;
  const year = Number(yearText), month = Number(monthText), day = Number(dayText);
  const hour = Number(hourText), minute = Number(minuteText), second = Number(secondText);
  const maxDay = month >= 1 && month <= 12 ? new Date(Date.UTC(year, month, 0)).getUTCDate() : 0;
  if (month < 1 || month > 12 || day < 1 || day > maxDay || hour > 23 || minute > 59 || second > 59) {
    fail("BLOCKED_LEGACY_LINEAGE_MIGRATION_INVALID", `output_updated date/time out of range — ${value}`);
  }
  if (zone !== "Z") {
    const offsetHour = Number(zone.slice(1, 3));
    const offsetMinute = Number(zone.slice(4, 6));
    if (offsetHour > 23 || offsetMinute > 59) fail("BLOCKED_LEGACY_LINEAGE_MIGRATION_INVALID", `output_updated timezone offset invalid — ${value}`);
  }
  if (Number.isNaN(Date.parse(value))) fail("BLOCKED_LEGACY_LINEAGE_MIGRATION_INVALID", `output_updated parse failed — ${value}`);
}

function validate(manifest, base, full) {
  if (manifest?.schema !== "legacy_related_lineage_container_migration_v1") fail("BLOCKED_LEGACY_LINEAGE_MIGRATION_INVALID", "unsupported manifest schema");
  if (manifest?.status !== "PASS") fail("BLOCKED_LEGACY_LINEAGE_MIGRATION_INVALID", "manifest status must be PASS");
  if (!manifest?.migration_id || !manifest?.base_main_commit_sha || !manifest?.base_full_blob_sha) fail("BLOCKED_LEGACY_LINEAGE_MIGRATION_INVALID", "baseline binding fields missing");
  if (!Number.isInteger(manifest.expected_before) || !Number.isInteger(manifest.expected_after) || !Number.isInteger(manifest.expected_initialized_count)) fail("BLOCKED_LEGACY_LINEAGE_MIGRATION_INVALID", "expected counts must be integers");
  if (!Array.isArray(manifest.expected_skipped_dangling_card_ids)) fail("BLOCKED_LEGACY_LINEAGE_MIGRATION_INVALID", "expected_skipped_dangling_card_ids array required");
  validateRfc3339DateTime(manifest.output_updated);
  if (!base || !Array.isArray(base.cards) || !full || !Array.isArray(full.cards)) fail("BLOCKED_LEGACY_LINEAGE_MIGRATION_INVALID", "base/full cards arrays required");
  if (base.cards.length !== manifest.expected_before || full.cards.length !== manifest.expected_after || base.cards.length !== full.cards.length) fail("BLOCKED_LEGACY_LINEAGE_MIGRATION_COUNT", "card count mismatch");
  if (manifest.expected_before !== manifest.expected_after) fail("BLOCKED_LEGACY_LINEAGE_MIGRATION_COUNT", "migration may not change card count");

  const baseTop = { ...base };
  const fullTop = { ...full };
  delete baseTop.cards; delete fullTop.cards;
  delete baseTop.updated; delete fullTop.updated;
  if (!same(baseTop, fullTop)) fail("BLOCKED_LEGACY_LINEAGE_MIGRATION_UNDECLARED_CHANGE", "top-level fields other than updated changed");
  if (full.updated !== manifest.output_updated) fail("BLOCKED_LEGACY_LINEAGE_MIGRATION_INVALID", "full.updated must equal manifest.output_updated");

  const ids = new Set(base.cards.map((card) => card?.id));
  let initialized = 0;
  const skipped = [];
  const initializedIds = [];

  for (let i = 0; i < base.cards.length; i += 1) {
    const before = base.cards[i];
    const after = full.cards[i];
    if (before?.id !== after?.id) fail("BLOCKED_LEGACY_LINEAGE_MIGRATION_ID_ORDER", `card id/order changed at index ${i}`);
    if (!Array.isArray(before.related) || !Array.isArray(after.related) || !same(before.related, after.related)) fail("BLOCKED_LEGACY_LINEAGE_MIGRATION_RELATED_CHANGE", `${before?.id}: related[] changed or invalid`);
    if (!same(withoutKey(before, "related_lineage"), withoutKey(after, "related_lineage"))) fail("BLOCKED_LEGACY_LINEAGE_MIGRATION_UNDECLARED_CHANGE", `${before?.id}: field other than related_lineage changed`);

    if (validLineageContainer(before)) {
      if (!same(before.related_lineage, after.related_lineage)) fail("BLOCKED_LEGACY_LINEAGE_MIGRATION_EXISTING_LINEAGE_CHANGED", `${before.id}: existing lineage changed`);
      continue;
    }

    const dangling = before.related.some((target) => !ids.has(target));
    if (dangling) {
      if (!same(before.related_lineage, after.related_lineage)) fail("BLOCKED_LEGACY_LINEAGE_MIGRATION_DANGLING_TOUCHED", `${before.id}: dangling legacy card must remain unchanged`);
      skipped.push(before.id);
      continue;
    }

    const expected = { related_ids: [...before.related] };
    if (!same(after.related_lineage, expected)) fail("BLOCKED_LEGACY_LINEAGE_MIGRATION_BAD_MATERIALIZATION", `${before.id}: related_lineage must be exact neutral mirror`);
    initialized += 1;
    initializedIds.push(before.id);
  }

  const sortedSkipped = [...skipped].sort();
  const expectedSkipped = [...manifest.expected_skipped_dangling_card_ids].sort();
  if (!same(sortedSkipped, expectedSkipped)) fail("BLOCKED_LEGACY_LINEAGE_MIGRATION_SKIP_SET", "skipped dangling set mismatch");
  if (initialized !== manifest.expected_initialized_count) fail("BLOCKED_LEGACY_LINEAGE_MIGRATION_COUNT", `initialized ${initialized} != expected ${manifest.expected_initialized_count}`);

  return { initialized_count: initialized, skipped_dangling_card_ids: sortedSkipped, initialized_ids: initializedIds };
}

function selfTest() {
  const base = { updated: "2026-01-01T00:00:00Z", total: 3, cards: [
    { id: "A", related: [], title: "A" },
    { id: "B", related: ["A"], title: "B" },
    { id: "C", related: ["MISSING"], title: "C" },
  ] };
  const full = structuredClone(base);
  full.updated = "2026-08-08T00:00:00+09:00";
  full.cards[0].related_lineage = { related_ids: [] };
  full.cards[1].related_lineage = { related_ids: ["A"] };
  const manifest = { schema: "legacy_related_lineage_container_migration_v1", status: "PASS", migration_id: "TEST", base_main_commit_sha: "x", base_full_blob_sha: "y", expected_before: 3, expected_after: 3, expected_initialized_count: 2, expected_skipped_dangling_card_ids: ["C"], output_updated: full.updated };
  validate(manifest, base, full);

  const badRelated = structuredClone(full); badRelated.cards[1].related.push("C");
  let caught = false; try { validate(manifest, base, badRelated); } catch (error) { caught = error instanceof ValidationError; }
  if (!caught) throw new Error("self-test failed to block related change");

  for (const invalidTimestamp of ["2026-08-08", "08/08/2026 12:00", "2026-13-08T00:00:00Z", "2026-08-08T25:00:00Z", "2026-08-08T00:00:00+24:00"]) {
    const badManifest = { ...manifest, output_updated: invalidTimestamp };
    const badFull = structuredClone(full); badFull.updated = invalidTimestamp;
    let timestampBlocked = false;
    try { validate(badManifest, base, badFull); } catch (error) { timestampBlocked = error instanceof ValidationError; }
    if (!timestampBlocked) throw new Error(`self-test failed to block invalid output_updated ${invalidTimestamp}`);
  }
  console.log("PASS: validate_legacy_related_lineage_migration self-test");
}

const args = process.argv.slice(2);
if (args.includes("--self-test")) { selfTest(); process.exit(0); }
const get = (flag) => { const i = args.indexOf(flag); return i >= 0 ? args[i + 1] : null; };
try {
  const manifestPath = get("--manifest"), basePath = get("--base"), fullPath = get("--full");
  if (!manifestPath || !basePath || !fullPath) fail("INVALID_ARGUMENT", "--manifest --base --full required");
  const result = validate(readJson(manifestPath, "manifest"), readJson(basePath, "base"), readJson(fullPath, "full"));
  console.log(JSON.stringify({ status: "PASS", ...result }, null, 2));
  console.log(`PASS: initialized ${result.initialized_count} legacy relation containers; preserved ${result.skipped_dangling_card_ids.length} dangling-remediation cards`);
} catch (error) {
  if (error instanceof ValidationError) { console.error(`FAIL [${error.code}]: ${error.message}`); process.exit(1); }
  throw error;
}
