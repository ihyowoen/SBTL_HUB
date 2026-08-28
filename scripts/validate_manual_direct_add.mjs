#!/usr/bin/env node
import { readFileSync } from "node:fs";

class ValidationError extends Error {
  constructor(code, message) { super(message); this.code = code; }
}

const fail = (code, message) => { throw new ValidationError(code, message); };
const readJson = (path, label) => {
  try { return JSON.parse(readFileSync(path, "utf8").replace(/^\uFEFF/, "")); }
  catch (error) { fail("BLOCKED_MANUAL_DIRECT_ADD_INVALID", `${label}: ${error.message}`); }
};
const same = (a, b) => JSON.stringify(a) === JSON.stringify(b);
const uniq = (items) => new Set(items).size === items.length;
const RFC3339 = /^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:\d{2})$/;

function requireString(value, label) {
  if (typeof value !== "string" || !value.trim()) fail("BLOCKED_MANUAL_DIRECT_ADD_INVALID", `${label} must be a non-empty string`);
  return value.trim();
}

function requireStringArray(value, label) {
  if (!Array.isArray(value) || value.some((item) => typeof item !== "string" || !item.trim())) {
    fail("BLOCKED_MANUAL_DIRECT_ADD_INVALID", `${label} must be an array of non-empty strings`);
  }
  if (!uniq(value)) fail("BLOCKED_MANUAL_DIRECT_ADD_INVALID", `${label} contains duplicates`);
  return value;
}

function validateTimestamp(value) {
  requireString(value, "output_updated");
  if (!RFC3339.test(value) || Number.isNaN(Date.parse(value))) {
    fail("BLOCKED_MANUAL_DIRECT_ADD_INVALID", `output_updated must be RFC3339 date-time — ${value}`);
  }
}

function cardMap(cards, label) {
  if (!Array.isArray(cards)) fail("BLOCKED_MANUAL_DIRECT_ADD_INVALID", `${label}.cards must be an array`);
  const map = new Map();
  for (const card of cards) {
    const id = requireString(card?.id, `${label} card id`);
    if (map.has(id)) fail("BLOCKED_MANUAL_DIRECT_ADD_DUPLICATE_ID", `${label} duplicate id ${id}`);
    map.set(id, card);
  }
  return map;
}

function topWithoutMutableFields(doc) {
  const copy = { ...doc };
  delete copy.cards;
  delete copy.updated;
  delete copy.total;
  return copy;
}

function sourceIdentityTokens(card) {
  const tokens = new Set();
  for (const key of ["source_spec_id", "origin_source_spec_id", "original_source_spec_id"]) {
    if (typeof card?.[key] === "string" && card[key].trim()) tokens.add(`spec:${card[key].trim()}`);
  }
  const provenance = card?.provenance;
  if (provenance && typeof provenance === "object") {
    for (const key of ["source_spec_id", "origin_source_spec_id", "original_source_spec_id"]) {
      if (typeof provenance[key] === "string" && provenance[key].trim()) tokens.add(`spec:${provenance[key].trim()}`);
    }
  }
  for (const url of Array.isArray(card?.urls) ? card.urls : []) {
    if (typeof url === "string" && url.trim()) tokens.add(`url:${url.trim()}`);
  }
  for (const source of Array.isArray(card?.fact_sources) ? card.fact_sources : []) {
    if (typeof source?.source_url === "string" && source.source_url.trim()) tokens.add(`url:${source.source_url.trim()}`);
  }
  if (typeof card?.title === "string" && card.title.trim()) tokens.add(`title:${card.title.trim()}`);
  return tokens;
}

function hasStableIdentity(before, after) {
  const left = sourceIdentityTokens(before);
  const right = sourceIdentityTokens(after);
  for (const token of left) if (right.has(token)) return true;
  return false;
}

function brokenPairs(doc, migrate = new Map()) {
  const ids = new Set(doc.cards.map((card) => card.id));
  const pairs = new Set();
  for (const card of doc.cards) {
    for (const target of Array.isArray(card.related) ? card.related : []) {
      if (!ids.has(target)) {
        const owner = migrate.get(card.id) || card.id;
        const mappedTarget = migrate.get(target) || target;
        pairs.add(`${owner}→${mappedTarget}`);
      }
    }
  }
  return pairs;
}

function validate(manifest, base, full) {
  if (manifest?.schema !== "manual_direct_add_v1") fail("BLOCKED_MANUAL_DIRECT_ADD_INVALID", "unsupported manifest schema");
  if (manifest?.status !== "PASS") fail("BLOCKED_MANUAL_DIRECT_ADD_INVALID", "manifest status must be PASS");
  requireString(manifest.direct_add_id, "direct_add_id");
  requireString(manifest.base_main_commit_sha, "base_main_commit_sha");
  requireString(manifest.base_full_blob_sha, "base_full_blob_sha");
  validateTimestamp(manifest.output_updated);
  if (!Number.isInteger(manifest.expected_before) || !Number.isInteger(manifest.expected_after)) {
    fail("BLOCKED_MANUAL_DIRECT_ADD_INVALID", "expected_before/expected_after must be integers");
  }

  const operations = manifest.operations;
  if (!operations || typeof operations !== "object" || Array.isArray(operations)) {
    fail("BLOCKED_MANUAL_DIRECT_ADD_INVALID", "operations object required");
  }
  const adds = requireStringArray(operations.add ?? [], "operations.add");
  const updates = requireStringArray(operations.update ?? [], "operations.update");
  const migrations = operations.id_migration ?? [];
  if (!Array.isArray(migrations)) fail("BLOCKED_MANUAL_DIRECT_ADD_INVALID", "operations.id_migration must be an array");

  const oldIds = [], newIds = [];
  const migrationMap = new Map();
  for (const [index, migration] of migrations.entries()) {
    if (!migration || typeof migration !== "object" || Array.isArray(migration)) {
      fail("BLOCKED_MANUAL_DIRECT_ADD_INVALID", `operations.id_migration[${index}] must be an object`);
    }
    const oldId = requireString(migration.old_id, `operations.id_migration[${index}].old_id`);
    const newId = requireString(migration.new_id, `operations.id_migration[${index}].new_id`);
    requireString(migration.reason, `operations.id_migration[${index}].reason`);
    if (oldId === newId) fail("BLOCKED_MANUAL_DIRECT_ADD_INVALID", `id migration must change id — ${oldId}`);
    if (migrationMap.has(oldId)) fail("BLOCKED_MANUAL_DIRECT_ADD_INVALID", `duplicate migration old_id ${oldId}`);
    migrationMap.set(oldId, newId);
    oldIds.push(oldId); newIds.push(newId);
  }
  if (!uniq(newIds)) fail("BLOCKED_MANUAL_DIRECT_ADD_INVALID", "duplicate migration new_id");

  const overlap = (a, b) => a.filter((id) => new Set(b).has(id));
  if (overlap(adds, updates).length || overlap(adds, oldIds).length || overlap(adds, newIds).length || overlap(updates, oldIds).length || overlap(updates, newIds).length) {
    fail("BLOCKED_MANUAL_DIRECT_ADD_INVALID", "add/update/id_migration identities must be disjoint");
  }

  if (!base || !full) fail("BLOCKED_MANUAL_DIRECT_ADD_INVALID", "base/full documents required");
  const baseMap = cardMap(base.cards, "base");
  const fullMap = cardMap(full.cards, "full");
  if (base.cards.length !== manifest.expected_before || full.cards.length !== manifest.expected_after) {
    fail("BLOCKED_MANUAL_DIRECT_ADD_COUNT", `card count mismatch base=${base.cards.length}/${manifest.expected_before} full=${full.cards.length}/${manifest.expected_after}`);
  }
  if (manifest.expected_after !== manifest.expected_before + adds.length) {
    fail("BLOCKED_MANUAL_DIRECT_ADD_COUNT", "expected_after must equal expected_before + declared adds; id migrations are count-neutral");
  }
  if (full.total !== full.cards.length || base.total !== base.cards.length) fail("BLOCKED_MANUAL_DIRECT_ADD_COUNT", "total field must equal cards.length");
  if (full.updated !== manifest.output_updated) fail("BLOCKED_MANUAL_DIRECT_ADD_INVALID", "full.updated must equal manifest.output_updated");
  if (!same(topWithoutMutableFields(base), topWithoutMutableFields(full))) {
    fail("BLOCKED_MANUAL_DIRECT_ADD_UNDECLARED_CHANGE", "top-level fields other than total/updated/cards changed");
  }

  const lost = [...baseMap.keys()].filter((id) => !fullMap.has(id)).sort();
  const introduced = [...fullMap.keys()].filter((id) => !baseMap.has(id)).sort();
  const expectedLost = [...oldIds].sort();
  const expectedIntroduced = [...adds, ...newIds].sort();
  if (!same(lost, expectedLost)) {
    fail("BLOCKED_MANUAL_DIRECT_ADD_SCOPE", `lost id set does not match id_migration old_ids — actual ${JSON.stringify(lost)} expected ${JSON.stringify(expectedLost)}`);
  }
  if (!same(introduced, expectedIntroduced)) {
    fail("BLOCKED_MANUAL_DIRECT_ADD_SCOPE", `introduced id set does not match add + migration new_ids — actual ${JSON.stringify(introduced)} expected ${JSON.stringify(expectedIntroduced)}`);
  }

  for (const id of adds) {
    if (baseMap.has(id) || !fullMap.has(id)) fail("BLOCKED_MANUAL_DIRECT_ADD_SCOPE", `declared add invalid ${id}`);
  }
  for (const id of updates) {
    if (!baseMap.has(id) || !fullMap.has(id)) fail("BLOCKED_MANUAL_DIRECT_ADD_SCOPE", `declared update must exist before and after — ${id}`);
    if (same(baseMap.get(id), fullMap.get(id))) fail("BLOCKED_MANUAL_DIRECT_ADD_SCOPE", `declared update did not change — ${id}`);
  }
  for (const { old_id: oldId, new_id: newId } of migrations) {
    const before = baseMap.get(oldId), after = fullMap.get(newId);
    if (!before || !after || fullMap.has(oldId) || baseMap.has(newId)) {
      fail("BLOCKED_MANUAL_DIRECT_ADD_SCOPE", `invalid one-to-one id migration ${oldId} → ${newId}`);
    }
    if (!hasStableIdentity(before, after)) {
      fail("BLOCKED_MANUAL_DIRECT_ADD_IDENTITY", `id migration lacks stable identity evidence ${oldId} → ${newId}`);
    }
  }

  const declaredMutable = new Set(updates);
  for (const [id, before] of baseMap.entries()) {
    if (migrationMap.has(id)) continue;
    const after = fullMap.get(id);
    if (!after) continue;
    if (!declaredMutable.has(id) && !same(before, after)) {
      fail("BLOCKED_MANUAL_DIRECT_ADD_UNDECLARED_CHANGE", `${id}: card changed but is not declared in operations.update`);
    }
  }

  const baseBroken = brokenPairs(base, migrationMap);
  const fullBroken = brokenPairs(full);
  const newBroken = [...fullBroken].filter((pair) => !baseBroken.has(pair));
  if (newBroken.length) fail("BLOCKED_MANUAL_DIRECT_ADD_RELATED", `new dangling related edges: ${newBroken.slice(0, 5).join(", ")}`);

  return {
    before: base.cards.length,
    after: full.cards.length,
    added_ids: [...adds],
    updated_ids: [...updates],
    id_migrations: migrations.map(({ old_id, new_id, reason }) => ({ old_id, new_id, reason })),
    new_dangling_related: 0,
  };
}

function selfTest() {
  const base = {
    total: 2,
    updated: "2026-01-01T00:00:00Z",
    cards: [
      { id: "2026-01-02_KR_01", date: "2026-01-02", title: "A", urls: ["https://a.example"], related: [] },
      { id: "2026-01-01_KR_01", date: "2026-01-01", title: "B", urls: ["https://b.example"], related: [] },
    ],
  };
  const full = structuredClone(base);
  full.updated = "2026-08-28T22:30:00+09:00";
  full.total = 3;
  full.cards[0].title = "A updated";
  full.cards[1].id = "2025-12-31_KR_01";
  full.cards[1].date = "2025-12-31";
  full.cards.push({ id: "2026-01-03_KR_01", date: "2026-01-03", title: "C", urls: ["https://c.example"], related: [] });
  const manifest = {
    schema: "manual_direct_add_v1",
    status: "PASS",
    direct_add_id: "TEST",
    base_main_commit_sha: "a",
    base_full_blob_sha: "b",
    expected_before: 2,
    expected_after: 3,
    output_updated: full.updated,
    operations: {
      add: ["2026-01-03_KR_01"],
      update: ["2026-01-02_KR_01"],
      id_migration: [{ old_id: "2026-01-01_KR_01", new_id: "2025-12-31_KR_01", reason: "event date correction" }],
    },
  };
  validate(manifest, base, full);

  const undeclared = structuredClone(full);
  undeclared.cards[1].title = "unrelated replacement";
  undeclared.cards[1].urls = ["https://other.example"];
  let blocked = false;
  try { validate(manifest, base, undeclared); } catch (error) { blocked = error instanceof ValidationError; }
  if (!blocked) throw new Error("self-test failed to block unrelated id replacement");

  const hiddenChange = structuredClone(full);
  hiddenChange.cards[0].title = base.cards[0].title;
  hiddenChange.cards.push();
  const badManifest = structuredClone(manifest);
  badManifest.operations.update = [];
  let hiddenBlocked = false;
  try { validate(badManifest, base, full); } catch (error) { hiddenBlocked = error instanceof ValidationError; }
  if (!hiddenBlocked) throw new Error("self-test failed to block undeclared update");

  console.log("PASS: validate_manual_direct_add self-test");
}

const args = process.argv.slice(2);
if (args.includes("--self-test")) { selfTest(); process.exit(0); }
const get = (flag) => { const index = args.indexOf(flag); return index >= 0 ? args[index + 1] : null; };

try {
  const manifestPath = get("--manifest"), basePath = get("--base"), fullPath = get("--full");
  if (!manifestPath || !basePath || !fullPath) fail("INVALID_ARGUMENT", "--manifest --base --full required");
  const result = validate(readJson(manifestPath, "manifest"), readJson(basePath, "base"), readJson(fullPath, "full"));
  console.log(JSON.stringify({ status: "PASS", ...result }, null, 2));
  console.log(`PASS: manual direct-add ${result.before} → ${result.after}; add ${result.added_ids.length}; update ${result.updated_ids.length}; id migration ${result.id_migrations.length}`);
} catch (error) {
  if (error instanceof ValidationError) { console.error(`FAIL [${error.code}]: ${error.message}`); process.exit(1); }
  throw error;
}
