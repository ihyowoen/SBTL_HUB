#!/usr/bin/env node
import {
  copyFileSync,
  existsSync,
  mkdirSync,
  readFileSync,
  renameSync,
  rmSync,
  writeFileSync,
} from "node:fs";
import { createHash } from "node:crypto";
import { dirname, resolve } from "node:path";
import { spawnSync } from "node:child_process";

const FAIL = (code, message) => {
  console.error(`FAIL [${code}]: ${message}`);
  process.exit(1);
};

const parseArgs = (argv) => {
  const options = {
    baseline: "data/cards.full.json",
    output: null,
    report: null,
    apply: false,
    skipLean: false,
    baseMainSha: process.env.CARD_RUN_BASE_MAIN_SHA || "",
    leanPath: process.env.CARDS_PUBLIC_PATH || "public/data/cards.json",
  };
  for (let index = 0; index < argv.length; index += 1) {
    const arg = argv[index];
    if (arg === "--apply") options.apply = true;
    else if (arg === "--check") options.apply = false;
    else if (arg === "--skip-lean") options.skipLean = true;
    else if (["--run", "--baseline", "--output", "--report", "--base-main-sha", "--lean-path"].includes(arg)) {
      const value = argv[index + 1];
      if (!value || value.startsWith("--")) FAIL("INVALID_ARGUMENT", `${arg} 값이 없음`);
      index += 1;
      if (arg === "--run") options.run = value;
      if (arg === "--baseline") options.baseline = value;
      if (arg === "--output") options.output = value;
      if (arg === "--report") options.report = value;
      if (arg === "--base-main-sha") options.baseMainSha = value;
      if (arg === "--lean-path") options.leanPath = value;
    } else {
      FAIL("INVALID_ARGUMENT", `지원하지 않는 인자 ${arg}`);
    }
  }
  if (!options.run) FAIL("INVALID_ARGUMENT", "--run PATH가 필요함");
  options.output ||= options.baseline;
  options.report ||= resolve(dirname(options.run), "apply-report.json");
  return options;
};

const readJson = (path, label) => {
  let raw;
  try {
    raw = readFileSync(path);
  } catch (error) {
    FAIL("READ_ERROR", `${label} 읽기 실패 (${path}): ${error.message}`);
  }
  try {
    return { raw, value: JSON.parse(raw.toString("utf8")) };
  } catch (error) {
    FAIL("JSON_PARSE_ERROR", `${label} JSON 파싱 실패 (${path}): ${error.message}`);
  }
};

const assertObject = (value, label) => {
  if (!value || typeof value !== "object" || Array.isArray(value)) {
    FAIL("INVALID_RUN", `${label}은 객체여야 함`);
  }
};

const sha256 = (bytes) => createHash("sha256").update(bytes).digest("hex");
const gitBlobSha = (bytes) => createHash("sha1")
  .update(Buffer.from(`blob ${bytes.length}\0`))
  .update(bytes)
  .digest("hex");

const canonical = (value) => JSON.stringify(value);
const deepClone = (value) => structuredClone(value);
const deepEqual = (left, right) => canonical(left) === canonical(right);

const decodePointerToken = (token) => token.replace(/~1/g, "/").replace(/~0/g, "~");
const parsePointer = (pointer) => {
  if (pointer === "") return [];
  if (typeof pointer !== "string" || !pointer.startsWith("/")) {
    FAIL("INVALID_POINTER", `JSON Pointer는 /로 시작해야 함: ${pointer}`);
  }
  return pointer.slice(1).split("/").map(decodePointerToken);
};

const isArrayIndex = (token) => /^(0|[1-9]\d*)$/.test(token);

const pointerParent = (root, pointer, { create = false } = {}) => {
  const tokens = parsePointer(pointer);
  if (!tokens.length) FAIL("INVALID_POINTER", "문서 루트 변경은 허용되지 않음");
  let current = root;
  for (const token of tokens.slice(0, -1)) {
    if (Array.isArray(current)) {
      if (!isArrayIndex(token)) FAIL("INVALID_POINTER", `배열 인덱스가 아님: ${token}`);
      const idx = Number(token);
      if (idx >= current.length) FAIL("INVALID_POINTER", `배열 범위 초과: ${pointer}`);
      current = current[idx];
      continue;
    }
    if (!current || typeof current !== "object") {
      FAIL("INVALID_POINTER", `중간 경로가 객체/배열이 아님: ${pointer}`);
    }
    if (!(token in current)) {
      if (!create) FAIL("INVALID_POINTER", `존재하지 않는 중간 경로: ${pointer}`);
      current[token] = {};
    }
    current = current[token];
  }
  return { parent: current, key: tokens.at(-1), tokens };
};

const applyUpdateChange = (card, change) => {
  assertObject(change, "update.change");
  const allowed = new Set(["add", "replace", "remove"]);
  if (!allowed.has(change.op)) FAIL("INVALID_UPDATE", `지원하지 않는 update op: ${change.op}`);
  const tokens = parsePointer(change.path);
  const root = tokens[0];
  if (root === "id") FAIL("IMMUTABLE_ID", "기존 카드 id 변경은 허용되지 않음");
  if (["related", "related_ids", "related_lineage"].includes(root)) {
    FAIL("RELATION_UPDATE_FORBIDDEN", `${change.path}는 related_add에서만 변경 가능`);
  }
  if ((change.op === "add" || change.op === "replace") && !("value" in change)) {
    FAIL("INVALID_UPDATE", `${change.op}에는 value가 필요함: ${change.path}`);
  }
  const { parent, key } = pointerParent(card, change.path, { create: change.op === "add" });
  if (Array.isArray(parent)) {
    if (change.op === "add") {
      if (key === "-") parent.push(deepClone(change.value));
      else if (isArrayIndex(key) && Number(key) <= parent.length) parent.splice(Number(key), 0, deepClone(change.value));
      else FAIL("INVALID_POINTER", `배열 add 위치 오류: ${change.path}`);
    } else {
      if (!isArrayIndex(key) || Number(key) >= parent.length) FAIL("INVALID_POINTER", `배열 범위 초과: ${change.path}`);
      if (change.op === "replace") parent[Number(key)] = deepClone(change.value);
      else parent.splice(Number(key), 1);
    }
    return;
  }
  if (!parent || typeof parent !== "object") FAIL("INVALID_POINTER", `부모가 객체가 아님: ${change.path}`);
  const exists = Object.hasOwn(parent, key);
  if (change.op === "add") {
    if (exists) FAIL("UPDATE_ADD_EXISTS", `이미 존재하는 경로에는 add 불가: ${change.path}`);
    parent[key] = deepClone(change.value);
  } else if (change.op === "replace") {
    if (!exists) FAIL("UPDATE_REPLACE_MISSING", `없는 경로에는 replace 불가: ${change.path}`);
    parent[key] = deepClone(change.value);
  } else {
    if (!exists) FAIL("UPDATE_REMOVE_MISSING", `없는 경로에는 remove 불가: ${change.path}`);
    delete parent[key];
  }
};

const relationRoots = new Set(["related", "related_ids", "related_lineage"]);

const applyRelationPatch = (cardsById, operation, patch) => {
  assertObject(patch, "related_add.patch");
  if (!cardsById.has(patch.card_id)) FAIL("MISSING_RELATED_PATCH_CARD", `patch card 없음: ${patch.card_id}`);
  if (![operation.source_id, operation.target_id].includes(patch.card_id)) {
    FAIL("INVALID_RELATED_PATCH_CARD", `patch card는 source/target 중 하나여야 함: ${patch.card_id}`);
  }
  if (patch.op !== "add") FAIL("RELATION_APPEND_ONLY", "related_add patch는 add만 허용됨");
  const tokens = parsePointer(patch.path);
  if (!relationRoots.has(tokens[0])) {
    FAIL("INVALID_RELATED_PATH", `관계 경로가 아님: ${patch.path}`);
  }
  if (!("value" in patch)) FAIL("INVALID_RELATED_PATCH", `value 누락: ${patch.path}`);
  const card = cardsById.get(patch.card_id);
  const { parent, key } = pointerParent(card, patch.path, { create: true });
  if (Array.isArray(parent)) {
    if (key !== "-") FAIL("RELATION_APPEND_ONLY", `관계 배열은 /- append만 허용됨: ${patch.path}`);
    if (parent.some((entry) => deepEqual(entry, patch.value))) {
      FAIL("DUPLICATE_RELATED_EDGE", `이미 존재하는 관계 값: ${patch.card_id} ${patch.path}`);
    }
    parent.push(deepClone(patch.value));
    return;
  }
  if (!parent || typeof parent !== "object") FAIL("INVALID_RELATED_PATH", `부모가 객체가 아님: ${patch.path}`);
  if (key === "-") FAIL("INVALID_RELATED_PATH", `객체에는 /-를 사용할 수 없음: ${patch.path}`);
  if (Object.hasOwn(parent, key)) FAIL("DUPLICATE_RELATED_EDGE", `이미 존재하는 관계 경로: ${patch.path}`);
  parent[key] = deepClone(patch.value);
};

const isDeepSubset = (before, after) => {
  if (Array.isArray(before)) {
    return Array.isArray(after) && before.every((entry) => after.some((candidate) => deepEqual(entry, candidate)));
  }
  if (before && typeof before === "object") {
    return Boolean(after && typeof after === "object" && !Array.isArray(after))
      && Object.entries(before).every(([key, value]) => Object.hasOwn(after, key) && isDeepSubset(value, after[key]));
  }
  return deepEqual(before, after);
};

const snapshotRelations = (cards) => new Map(cards.map((card) => [
  card.id,
  Object.fromEntries([...relationRoots]
    .filter((key) => Object.hasOwn(card, key))
    .map((key) => [key, deepClone(card[key])])),
]));

const validateRunShape = (run) => {
  assertObject(run, "run");
  const allowedTop = new Set([
    "schema", "run_id", "base_main_commit_sha", "base_full_blob_sha", "expected_before",
    "operations", "expected_after", "audit_refs", "document_universe_manifest_ref",
    "coverage_discovery_ref", "independent_completeness_ref",
  ]);
  const unknownTop = Object.keys(run).filter((key) => !allowedTop.has(key));
  if (unknownTop.length) FAIL("INVALID_RUN", `지원하지 않는 top-level 필드: ${unknownTop.join(", ")}`);
  if (run.schema !== "card_run_v1") FAIL("INVALID_RUN", "schema는 card_run_v1이어야 함");
  if (typeof run.run_id !== "string" || !run.run_id.trim()) FAIL("INVALID_RUN", "run_id 누락");
  for (const key of ["base_main_commit_sha", "base_full_blob_sha"]) {
    if (typeof run[key] !== "string" || !/^[0-9a-f]{40}$/.test(run[key])) FAIL("INVALID_RUN", `${key}는 40자리 소문자 SHA여야 함`);
  }
  if (!Number.isInteger(run.expected_before) || run.expected_before < 0) FAIL("INVALID_RUN", "expected_before 오류");
  if (!Number.isInteger(run.expected_after) || run.expected_after < 0) FAIL("INVALID_RUN", "expected_after 오류");
  assertObject(run.operations, "operations");
  const allowedOps = new Set(["insert", "update", "related_add"]);
  const unknownOps = Object.keys(run.operations).filter((key) => !allowedOps.has(key));
  if (unknownOps.length) FAIL("FORBIDDEN_OPERATION", `허용되지 않는 operation: ${unknownOps.join(", ")}`);
  for (const key of allowedOps) {
    if (!Array.isArray(run.operations[key])) FAIL("INVALID_RUN", `operations.${key}는 배열이어야 함`);
  }
  if (!Array.isArray(run.audit_refs) || !run.audit_refs.length) FAIL("INVALID_RUN", "audit_refs가 비어 있음");
  for (const key of ["document_universe_manifest_ref", "coverage_discovery_ref", "independent_completeness_ref"]) {
    if (typeof run[key] !== "string" || !run[key].trim()) FAIL("INVALID_RUN", `${key} 누락`);
  }
};

const validateInsert = (operation) => {
  assertObject(operation, "insert operation");
  assertObject(operation.card, "insert.card");
  if (typeof operation.card.id !== "string" || !operation.card.id.trim()) FAIL("INVALID_INSERT", "insert.card.id 누락");
  if (operation.before_id && operation.after_id) FAIL("INVALID_INSERT", "before_id와 after_id는 함께 사용 불가");
  for (const key of ["stage_artifacts", "evidence_refs"]) {
    if (!Array.isArray(operation[key]) || !operation[key].length) FAIL("INVALID_INSERT", `${operation.card.id}: ${key}가 비어 있음`);
  }
};

const validateUpdate = (operation) => {
  assertObject(operation, "update operation");
  if (typeof operation.id !== "string" || !operation.id.trim()) FAIL("INVALID_UPDATE", "update.id 누락");
  if (!Array.isArray(operation.changes) || !operation.changes.length) FAIL("INVALID_UPDATE", `${operation.id}: changes가 비어 있음`);
  if (typeof operation.reason !== "string" || !operation.reason.trim()) FAIL("INVALID_UPDATE", `${operation.id}: reason 누락`);
  for (const key of ["stage_artifacts", "evidence_refs"]) {
    if (!Array.isArray(operation[key]) || !operation[key].length) FAIL("INVALID_UPDATE", `${operation.id}: ${key}가 비어 있음`);
  }
  const paths = operation.changes.map((change) => change.path);
  if (new Set(paths).size !== paths.length) FAIL("INVALID_UPDATE", `${operation.id}: 중복 변경 경로`);
};

const validateRelatedAdd = (operation) => {
  assertObject(operation, "related_add operation");
  for (const key of ["source_id", "target_id", "relation_type", "lineage_reason", "event_stage_relationship"]) {
    if (typeof operation[key] !== "string" || !operation[key].trim()) FAIL("INVALID_RELATED_ADD", `${key} 누락`);
  }
  if (operation.source_id === operation.target_id) FAIL("SELF_RELATED_EDGE", `${operation.source_id}: self relation`);
  if (!new Set(["directional", "reciprocal"]).has(operation.direction)) FAIL("INVALID_RELATED_ADD", "direction 오류");
  if (!Array.isArray(operation.evidence_refs) || !operation.evidence_refs.length) FAIL("INVALID_RELATED_ADD", "evidence_refs가 비어 있음");
  if (!Array.isArray(operation.patches) || !operation.patches.length) FAIL("INVALID_RELATED_ADD", "patches가 비어 있음");
};

const insertCard = (cards, operation) => {
  const card = deepClone(operation.card);
  if (operation.before_id) {
    const index = cards.findIndex((candidate) => candidate.id === operation.before_id);
    if (index < 0) FAIL("INVALID_INSERT_POSITION", `before_id 없음: ${operation.before_id}`);
    cards.splice(index, 0, card);
  } else if (operation.after_id) {
    const index = cards.findIndex((candidate) => candidate.id === operation.after_id);
    if (index < 0) FAIL("INVALID_INSERT_POSITION", `after_id 없음: ${operation.after_id}`);
    cards.splice(index + 1, 0, card);
  } else {
    cards.push(card);
  }
};

const validateNewRelationResolution = (operation, cardsById) => {
  const sourceValues = operation.patches.filter((patch) => patch.card_id === operation.source_id);
  const targetValues = operation.patches.filter((patch) => patch.card_id === operation.target_id);
  const connects = (patches, expectedId) => patches.some((patch) =>
    ["/related/-", "/related_ids/-"].includes(patch.path)
    && typeof patch.value === "string"
    && patch.value === expectedId);
  if (!connects(sourceValues, operation.target_id)) {
    FAIL("RELATED_TARGET_NOT_DECLARED", `${operation.source_id} → ${operation.target_id} 연결 patch 없음`);
  }
  if (operation.direction === "reciprocal" && !connects(targetValues, operation.source_id)) {
    FAIL("RELATED_RECIPROCAL_MISSING", `${operation.target_id} → ${operation.source_id} reciprocal patch 없음`);
  }
  for (const patch of operation.patches) {
    if (typeof patch.value === "string" && ["/related/-", "/related_ids/-"].includes(patch.path)) {
      if (!cardsById.has(patch.value)) FAIL("BLOCKED_NEW_MISSING_RELATED_TARGETS", `새 관계 target 없음: ${patch.value}`);
    }
  }
};

const atomicWrite = (path, bytes) => {
  mkdirSync(dirname(path), { recursive: true });
  const temporary = `${path}.tmp-${process.pid}`;
  writeFileSync(temporary, bytes);
  renameSync(temporary, path);
};

const options = parseArgs(process.argv.slice(2));
if (!existsSync(options.baseline)) FAIL("BLOCKED_CANONICAL_FULL_UNREADABLE", `baseline 없음: ${options.baseline}`);
if (!options.baseMainSha || !/^[0-9a-f]{40}$/.test(options.baseMainSha)) {
  FAIL("BLOCKED_INCREMENTAL_MERGE_PRECONDITION_MISSING", "--base-main-sha 또는 CARD_RUN_BASE_MAIN_SHA가 필요함");
}

const runLoaded = readJson(options.run, "card run");
const baselineLoaded = readJson(options.baseline, "canonical full");
const run = runLoaded.value;
const baseline = baselineLoaded.value;
validateRunShape(run);

if (run.base_main_commit_sha !== options.baseMainSha) {
  FAIL("BLOCKED_BASELINE_MOVED_REBASE_REQUIRED", `main SHA ${options.baseMainSha} != run ${run.base_main_commit_sha}`);
}
const actualBlobSha = gitBlobSha(baselineLoaded.raw);
if (run.base_full_blob_sha !== actualBlobSha) {
  FAIL("BLOCKED_BASELINE_MOVED_REBASE_REQUIRED", `full blob SHA ${actualBlobSha} != run ${run.base_full_blob_sha}`);
}
if (!baseline || typeof baseline !== "object" || Array.isArray(baseline) || !Array.isArray(baseline.cards)) {
  FAIL("BLOCKED_CANONICAL_FULL_UNREADABLE", "canonical full 최상위 객체/cards 배열 계약 불일치");
}
if (baseline.cards.length !== run.expected_before) {
  FAIL("BLOCKED_BASELINE_MOVED_REBASE_REQUIRED", `카드 수 ${baseline.cards.length} != expected_before ${run.expected_before}`);
}

const baselineIds = baseline.cards.map((card) => card?.id);
if (baselineIds.some((id) => typeof id !== "string" || !id)) FAIL("INVALID_CANONICAL_FULL", "id 없는 카드 존재");
if (new Set(baselineIds).size !== baselineIds.length) FAIL("INVALID_CANONICAL_FULL", "중복 id 존재");

const relationBefore = snapshotRelations(baseline.cards);
const result = deepClone(baseline);
const insertOps = run.operations.insert;
const updateOps = run.operations.update;
const relatedOps = run.operations.related_add;

const incomingIds = new Set();
for (const operation of insertOps) {
  validateInsert(operation);
  const id = operation.card.id;
  if (baselineIds.includes(id) || incomingIds.has(id)) FAIL("DUPLICATE_INSERT_ID", `insert id 충돌: ${id}`);
  incomingIds.add(id);
}
for (const operation of updateOps) validateUpdate(operation);
for (const operation of relatedOps) validateRelatedAdd(operation);

// Unpositioned inserts form one ordered latest-first block at the front. Explicitly positioned
// inserts are then placed relative to the resulting inventory without reordering existing cards.
const defaultInsertOps = insertOps.filter((operation) => !operation.before_id && !operation.after_id);
const positionedInsertOps = insertOps.filter((operation) => operation.before_id || operation.after_id);
result.cards.unshift(...defaultInsertOps.map((operation) => deepClone(operation.card)));
for (const operation of positionedInsertOps) insertCard(result.cards, operation);
let cardsById = new Map(result.cards.map((card) => [card.id, card]));

for (const operation of updateOps) {
  const card = cardsById.get(operation.id);
  if (!card) FAIL("UPDATE_TARGET_MISSING", `update target 없음: ${operation.id}`);
  for (const change of operation.changes) applyUpdateChange(card, change);
}

for (const operation of relatedOps) {
  if (!cardsById.has(operation.source_id) || !cardsById.has(operation.target_id)) {
    FAIL("BLOCKED_NEW_MISSING_RELATED_TARGETS", `${operation.source_id} ↔ ${operation.target_id} 중 target 없음`);
  }
  for (const patch of operation.patches) applyRelationPatch(cardsById, operation, patch);
  validateNewRelationResolution(operation, cardsById);
}

cardsById = new Map(result.cards.map((card) => [card.id, card]));
if (cardsById.size !== result.cards.length) FAIL("DUPLICATE_RESULT_ID", "결과 카드 id 중복");
if (result.cards.length !== run.expected_after) {
  FAIL("COUNT_RECONCILIATION_FAILED", `결과 ${result.cards.length} != expected_after ${run.expected_after}`);
}
if (run.expected_after !== run.expected_before + insertOps.length) {
  FAIL("COUNT_RECONCILIATION_FAILED", "expected_after는 expected_before + insert_count와 같아야 함");
}
for (const id of baselineIds) {
  if (!cardsById.has(id)) FAIL("UNDECLARED_CARD_LOSS", `기존 카드 소실: ${id}`);
  const before = relationBefore.get(id);
  const afterCard = cardsById.get(id);
  for (const [key, value] of Object.entries(before)) {
    if (!Object.hasOwn(afterCard, key) || !isDeepSubset(value, afterCard[key])) {
      FAIL("BLOCKED_EXISTING_RELATED_EDGE_LOSS", `${id}.${key} 기존 관계 소실/변경`);
    }
  }
}

const outputBytes = Buffer.from(JSON.stringify(result));
const report = {
  schema: "card_run_apply_report_v1",
  run_id: run.run_id,
  base_main_commit_sha: run.base_main_commit_sha,
  base_full_blob_sha: run.base_full_blob_sha,
  expected_before: run.expected_before,
  insert_count: insertOps.length,
  update_count: updateOps.length,
  related_add_count: relatedOps.length,
  delete_count: 0,
  related_remove_count: 0,
  existing_related_preserved: true,
  undeclared_existing_card_change_count: 0,
  expected_after: run.expected_after,
  full_output_sha256: sha256(outputBytes),
  lean_output_sha256: "",
  mode: options.apply ? "apply" : "check",
  github_merge_ready: false,
};

if (!options.apply) {
  console.log(JSON.stringify(report, null, 2));
  console.log(`PASS: ${run.run_id} check — ${run.expected_before} → ${run.expected_after}`);
  process.exit(0);
}

const backup = options.output === options.baseline ? `${options.output}.card-run-backup-${process.pid}` : null;
try {
  if (backup) copyFileSync(options.baseline, backup);
  atomicWrite(options.output, outputBytes);
  if (!options.skipLean) {
    const lean = spawnSync(process.execPath, ["scripts/lean_cards.mjs"], {
      stdio: "inherit",
      env: {
        ...process.env,
        CARDS_FULL_PATH: options.output,
        CARDS_PUBLIC_PATH: options.leanPath,
      },
    });
    if (lean.status !== 0) {
      if (backup && existsSync(backup)) {
        copyFileSync(backup, options.output);
        rmSync(backup, { force: true });
      }
      FAIL("LEAN_PROJECTION_FAILED", `lean exporter exit ${lean.status}`);
    }
    const leanBytes = readFileSync(options.leanPath);
    report.lean_output_sha256 = sha256(leanBytes);
  }
  // Repository validators run after this engine. The workflow flips github_merge_ready only after
  // schema, tracker, full-card and exact lean-projection checks all pass.
  atomicWrite(options.report, Buffer.from(`${JSON.stringify(report, null, 2)}\n`));
  if (backup) rmSync(backup, { force: true });
  console.log(`PASS: ${run.run_id} applied — ${run.expected_before} → ${run.expected_after}`);
  console.log(`REPORT: ${options.report}`);
} catch (error) {
  if (backup && existsSync(backup)) {
    copyFileSync(backup, options.output);
    rmSync(backup, { force: true });
  }
  throw error;
}
