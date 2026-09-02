#!/usr/bin/env node
import { existsSync, mkdtempSync, readFileSync, rmSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { dirname, resolve, sep, join } from "node:path";
import { mkdirSync } from "node:fs";

class ValidationError extends Error {
  constructor(code, message) {
    super(message);
    this.code = code;
  }
}

const fail = (code, message) => {
  throw new ValidationError(code, message);
};

const normalizeId = (value) => typeof value === "string" && value.trim() ? value.trim() : null;

const readJson = (path, label) => {
  let raw;
  try {
    raw = readFileSync(path, "utf8").replace(/^\uFEFF/, "");
  } catch (error) {
    fail("BLOCKED_PROMPT_0_8_IO", `${label}: read failed — ${path}: ${error.message}`);
  }
  try {
    return JSON.parse(raw);
  } catch (error) {
    fail("BLOCKED_PROMPT_0_8_JSON", `${label}: invalid JSON — ${path}: ${error.message}`);
  }
};

const repoJson = (root, reference, label) => {
  if (typeof reference !== "string" || !reference.trim() || !reference.endsWith(".json")) {
    fail("BLOCKED_PROMPT_0_8_ARTIFACT", `${label}: repository-relative JSON reference required`);
  }
  const absoluteRoot = resolve(root);
  const absolute = resolve(absoluteRoot, reference);
  if (absolute !== absoluteRoot && !absolute.startsWith(`${absoluteRoot}${sep}`)) {
    fail("BLOCKED_PROMPT_0_8_ARTIFACT", `${label}: repository-outside reference ${reference}`);
  }
  if (!existsSync(absolute)) {
    fail("BLOCKED_PROMPT_0_8_ARTIFACT", `${label}: missing ${reference}`);
  }
  return absolute;
};

const unique = (values, label) => {
  const ids = values.map(normalizeId).filter(Boolean);
  const seen = new Set();
  for (const id of ids) {
    if (seen.has(id)) fail("BLOCKED_PROMPT_0_8_ITEM_SET", `${label}: duplicate ID ${id}`);
    seen.add(id);
  }
  return ids;
};

const cardMap = (full) => {
  if (!full || typeof full !== "object" || !Array.isArray(full.cards)) {
    fail("BLOCKED_PROMPT_0_8_ID_LEDGER", "candidate canonical full must contain cards[]");
  }
  const byId = new Map();
  for (const card of full.cards) {
    if (!card || typeof card !== "object") continue;
    const id = normalizeId(card.id);
    if (!id) continue;
    if (byId.has(id)) fail("BLOCKED_PROMPT_0_8_ID_LEDGER", `duplicate canonical ID ${id}`);
    byId.set(id, card);
  }
  return byId;
};

const resolveRelatedIdentity = (operation, byId, insertedIds, updatedIds, index) => {
  const label = `related_add[${index}]`;
  const sourceId = normalizeId(operation?.source_id);
  const targetId = normalizeId(operation?.target_id);
  if (!sourceId || !targetId) fail("BLOCKED_PROMPT_0_8_RELATED_IDENTITY", `${label}: source_id/target_id required`);
  const endpoints = new Set([sourceId, targetId]);

  const explicit = normalizeId(operation?.identity_card_id);
  if (explicit) {
    if (!endpoints.has(explicit)) {
      fail("BLOCKED_PROMPT_0_8_RELATED_IDENTITY", `${label}.identity_card_id must match source_id or target_id`);
    }
    return explicit;
  }

  const sourceSpecId = normalizeId(operation?.source_spec_id);
  if (sourceSpecId) {
    const matches = [sourceId, targetId].filter((id) => normalizeId(byId.get(id)?.source_spec_id) === sourceSpecId);
    if (matches.length === 1) return matches[0];
  }

  const currentRunMatches = [sourceId, targetId].filter((id) => insertedIds.has(id) || updatedIds.has(id));
  if (currentRunMatches.length === 1) return currentRunMatches[0];

  fail(
    "BLOCKED_PROMPT_0_8_RELATED_IDENTITY",
    `${label}: cannot unambiguously determine the governed Related endpoint; identity_card_id is required`,
  );
};

const deriveIdSets = (run, full) => {
  const operations = run?.operations;
  if (!operations || typeof operations !== "object") {
    fail("BLOCKED_PROMPT_0_8_ITEM_SET", "card run operations object required");
  }
  for (const kind of ["insert", "update", "related_add"]) {
    if (!Array.isArray(operations[kind])) fail("BLOCKED_PROMPT_0_8_ITEM_SET", `operations.${kind} must be an array`);
  }

  const inserted = unique(operations.insert.map((op) => op?.card?.id), "insert IDs");
  const updated = unique(operations.update.map((op) => op?.id), "update IDs");
  const insertedIds = new Set(inserted);
  const updatedIds = new Set(updated);
  const byId = cardMap(full);

  const strictIds = [...new Set([...inserted, ...updated])];
  const operationIds = [...strictIds];
  const operationSet = new Set(operationIds);

  operations.related_add.forEach((operation, index) => {
    const governedId = resolveRelatedIdentity(operation, byId, insertedIds, updatedIds, index);
    if (!operationSet.has(governedId)) {
      operationSet.add(governedId);
      operationIds.push(governedId);
    }
  });

  if (!operationIds.length) {
    fail("BLOCKED_PROMPT_0_8_EMPTY_ID_LEDGER", "formal run has no operation identity to prepare for merge");
  }

  for (const id of operationIds) {
    if (!byId.has(id)) fail("BLOCKED_PROMPT_0_8_ID_LEDGER", `${id} does not resolve in candidate canonical full`);
  }

  return { strictIds, operationIds };
};

const loadMergePrep = (root, run) => {
  if (!Array.isArray(run.audit_refs) || !run.audit_refs.length) {
    fail("BLOCKED_PROMPT_0_8_ARTIFACT", "audit_refs[] required");
  }
  const matches = [];
  run.audit_refs.forEach((reference, index) => {
    const absolute = repoJson(root, reference, `audit_refs[${index}]`);
    const payload = readJson(absolute, `audit_refs[${index}]`);
    if (payload?.stage === "0.8") matches.push({ reference, payload });
  });
  if (matches.length !== 1) {
    fail("BLOCKED_PROMPT_0_8_ARTIFACT", `expected exactly one stage=0.8 artifact, found ${matches.length}`);
  }
  return matches[0];
};

const validateMergePrep = (run, selected, operationIds) => {
  const artifact = selected.payload;
  if (!["PASS", "GITHUB_MERGE_READY"].includes(artifact?.status)) {
    fail("BLOCKED_PROMPT_0_8_ARTIFACT", `non-passing 0.8 status ${String(artifact?.status)}`);
  }
  for (const field of ["run_id", "base_main_commit_sha", "base_full_blob_sha"]) {
    if (artifact[field] !== run[field]) {
      fail("BLOCKED_PROMPT_0_8_ARTIFACT", `${field} is not bound to the card run`);
    }
  }

  if (!Array.isArray(artifact.github_merge_ready) || !artifact.github_merge_ready.length) {
    fail("BLOCKED_PROMPT_0_8_ITEM_SET", "github_merge_ready[] must be non-empty");
  }
  const reviewedIds = unique(
    artifact.github_merge_ready.map((item) => item?.id),
    "github_merge_ready IDs",
  ).sort();
  const expectedIds = [...operationIds].sort();
  if (JSON.stringify(reviewedIds) !== JSON.stringify(expectedIds)) {
    fail(
      "BLOCKED_PROMPT_0_8_ITEM_SET",
      `reviewed=${JSON.stringify(reviewedIds)} expected=${JSON.stringify(expectedIds)}`,
    );
  }
};

const writeLedger = (ledgerPath, strictIds, operationIds) => {
  const payload = {
    schema: "prompt_0_8_current_run_id_ledger_v1",
    ids: strictIds,
    operation_ids: operationIds,
  };
  writeFileSync(ledgerPath, `${JSON.stringify(payload, null, 2)}\n`);
};

const parseArgs = (argv) => {
  const options = { run: null, full: "data/cards.full.json", ledger: null, selfTest: false };
  for (let index = 0; index < argv.length; index += 1) {
    const arg = argv[index];
    if (arg === "--self-test") options.selfTest = true;
    else if (["--run", "--full", "--ledger"].includes(arg)) {
      const value = argv[index + 1];
      if (!value || value.startsWith("--")) fail("INVALID_ARGUMENT", `${arg} PATH required`);
      options[arg.slice(2)] = value;
      index += 1;
    } else fail("INVALID_ARGUMENT", `unsupported argument ${arg}`);
  }
  return options;
};

const runSelfTest = () => {
  const root = mkdtempSync(join(tmpdir(), "prompt-0-8-runtime-"));
  try {
    mkdirSync(join(root, "runs"), { recursive: true });
    const full = {
      cards: [
        { id: "NEW", source_spec_id: "SPEC_NEW" },
        { id: "OLD" },
        { id: "UPDATED", source_spec_id: "SPEC_UPDATED" },
      ],
    };
    const run = {
      run_id: "runtime-self-test",
      base_main_commit_sha: "a".repeat(40),
      base_full_blob_sha: "b".repeat(40),
      operations: {
        insert: [{ card: { id: "NEW", source_spec_id: "SPEC_NEW" } }],
        update: [{ id: "UPDATED", source_spec_id: "SPEC_UPDATED" }],
        related_add: [{
          source_id: "NEW",
          target_id: "OLD",
          source_spec_id: "SPEC_NEW",
          identity_card_id: "NEW",
          direction: "reciprocal",
          patches: [
            { card_id: "NEW" },
            { card_id: "OLD" },
          ],
        }],
      },
      audit_refs: ["runs/merge-prep.json"],
    };
    const sets = deriveIdSets(run, full);
    if (JSON.stringify(sets.strictIds.sort()) !== JSON.stringify(["NEW", "UPDATED"])) {
      throw new Error(`strict ledger unexpectedly includes reciprocal legacy endpoint: ${JSON.stringify(sets.strictIds)}`);
    }
    if (sets.operationIds.includes("OLD")) {
      throw new Error("reciprocal patch target must not become a merge-prep operation identity");
    }

    const mergePrep = {
      stage: "0.8",
      status: "GITHUB_MERGE_READY",
      run_id: run.run_id,
      base_main_commit_sha: run.base_main_commit_sha,
      base_full_blob_sha: run.base_full_blob_sha,
      github_merge_ready: sets.operationIds.map((id) => ({ id })),
    };
    writeFileSync(join(root, "runs/merge-prep.json"), `${JSON.stringify(mergePrep)}\n`);
    validateMergePrep(run, loadMergePrep(root, run), sets.operationIds);

    const ledger = join(root, "ledger.json");
    writeLedger(ledger, sets.strictIds, sets.operationIds);
    const parsed = JSON.parse(readFileSync(ledger, "utf8"));
    if (!Array.isArray(parsed.ids) || parsed.ids.length !== 2) throw new Error("ledger is not JSON ids[] contract");

    const bad = structuredClone(mergePrep);
    bad.github_merge_ready = [{ id: "OLD" }];
    let caught = null;
    try {
      validateMergePrep(run, { reference: "runs/merge-prep.json", payload: bad }, sets.operationIds);
    } catch (error) {
      caught = error;
    }
    if (!(caught instanceof ValidationError) || caught.code !== "BLOCKED_PROMPT_0_8_ITEM_SET") {
      throw new Error("mismatched merge-prep item set was not blocked");
    }

    console.log("PASS: Prompt 0.8 runtime gate writes a JSON current-run ledger, excludes reciprocal legacy patch-only endpoints from strict scope, and binds github_merge_ready to operation identities");
  } finally {
    rmSync(root, { recursive: true, force: true });
  }
};

try {
  const options = parseArgs(process.argv.slice(2));
  if (options.selfTest) {
    runSelfTest();
    process.exit(0);
  }
  if (!options.run || !options.ledger) fail("INVALID_ARGUMENT", "--run PATH and --ledger PATH are required");

  const root = resolve(".");
  const runPath = repoJson(root, options.run, "card run");
  const fullPath = repoJson(root, options.full, "canonical full");
  const run = readJson(runPath, "card run");
  const full = readJson(fullPath, "canonical full");
  const { strictIds, operationIds } = deriveIdSets(run, full);
  const selected = loadMergePrep(root, run);
  validateMergePrep(run, selected, operationIds);
  writeLedger(options.ledger, strictIds, operationIds);
  process.stdout.write(selected.reference);
} catch (error) {
  if (error instanceof ValidationError) {
    console.error(`FAIL [${error.code}]: ${error.message}`);
    process.exit(1);
  }
  console.error(`FAIL [BLOCKED_PROMPT_0_8_INTERNAL]: ${error.message}`);
  process.exit(1);
}
