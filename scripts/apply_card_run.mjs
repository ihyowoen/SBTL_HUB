#!/usr/bin/env node
/**
 * Governed incremental card-run engine.
 *
 * Canonical authority:
 *   data/cards.full.json      sole full inventory
 *   public/data/cards.json    generated lean projection
 *
 * Ordinary operations:
 *   insert, update, related_add
 *
 * The expected result is always rebuilt from the declared main commit. The
 * working full must be either that exact baseline or the exact expected result,
 * which makes retries idempotent and blocks undeclared edits.
 */
import {
  copyFileSync,
  existsSync,
  mkdirSync,
  readFileSync,
  renameSync,
  rmSync,
  statSync,
  writeFileSync,
} from "node:fs";
import { createHash } from "node:crypto";
import { dirname, resolve, sep } from "node:path";
import { spawnSync } from "node:child_process";

const FAIL = (code, message) => {
  console.error(`FAIL [${code}]: ${message}`);
  process.exit(1);
};

const parseArgs = (argv) => {
  const options = {
    baseline: "data/cards.full.json",
    canonicalPath: "data/cards.full.json",
    output: null,
    report: null,
    mode: "check",
    skipLean: false,
    baseMainSha: process.env.CARD_RUN_BASE_MAIN_SHA || "",
    leanPath: process.env.CARDS_PUBLIC_PATH || "public/data/cards.json",
  };
  for (let index = 0; index < argv.length; index += 1) {
    const arg = argv[index];
    if (arg === "--apply") options.mode = "apply";
    else if (arg === "--verify") options.mode = "verify";
    else if (arg === "--check") options.mode = "check";
    else if (arg === "--skip-lean") options.skipLean = true;
    else if ([
      "--run", "--baseline", "--canonical-path", "--output", "--report",
      "--base-main-sha", "--lean-path",
    ].includes(arg)) {
      const value = argv[index + 1];
      if (!value || value.startsWith("--")) FAIL("INVALID_ARGUMENT", `${arg} 값이 없음`);
      index += 1;
      if (arg === "--run") options.run = value;
      if (arg === "--baseline") options.baseline = value;
      if (arg === "--canonical-path") options.canonicalPath = value;
      if (arg === "--output") options.output = value;
      if (arg === "--report") options.report = value;
      if (arg === "--base-main-sha") options.baseMainSha = value;
      if (arg === "--lean-path") options.leanPath = value;
    } else {
      FAIL("INVALID_ARGUMENT", `지원하지 않는 인자 ${arg}`);
    }
  }
  if (!options.run) FAIL("INVALID_ARGUMENT", "--run PATH가 필요함");
  if (options.mode === "verify" && options.skipLean) {
    FAIL("INVALID_ARGUMENT", "--verify와 --skip-lean은 함께 사용할 수 없음");
  }
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
    return { raw, value: JSON.parse(raw.toString("utf8").replace(/^\uFEFF/, "")) };
  } catch (error) {
    FAIL("JSON_PARSE_ERROR", `${label} JSON 파싱 실패 (${path}): ${error.message}`);
  }
};

const git = (args, { bytes = false } = {}) => {
  const result = spawnSync("git", args, {
    encoding: bytes ? null : "utf8",
    maxBuffer: 64 * 1024 * 1024,
  });
  if (result.status !== 0) {
    const detail = String(result.stderr || "").trim();
    FAIL("GIT_ERROR", `git ${args.join(" ")} 실패${detail ? ` — ${detail}` : ""}`);
  }
  return bytes ? result.stdout : String(result.stdout).trim();
};

const assertObject = (value, label, code = "INVALID_RUN") => {
  if (!value || typeof value !== "object" || Array.isArray(value)) {
    FAIL(code, `${label}은 객체여야 함`);
  }
};
const assertStringArray = (value, label) => {
  if (!Array.isArray(value) || !value.length
    || value.some((entry) => typeof entry !== "string" || !entry.trim())) {
    FAIL("INVALID_RUN", `${label}은 비어 있지 않은 문자열 배열이어야 함`);
  }
};
const canonical = (value) => JSON.stringify(value);
const deepClone = (value) => structuredClone(value);
const deepEqual = (left, right) => canonical(left) === canonical(right);
const sha256 = (bytes) => createHash("sha256").update(bytes).digest("hex");
const unique = (values) => new Set(values).size === values.length;


const REPO_ROOT = resolve(".");
const BLOCKED_STATUS = /(?:BLOCKED|FAIL|ERROR|REJECTED|INVALID|PENDING)/i;
const HTTP_URL = /^https?:\/\//i;

const detectJsonFormat = (raw) => {
  let text = raw.toString("utf8");
  const bom = text.startsWith("\uFEFF");
  if (bom) text = text.slice(1);
  const eol = text.includes("\r\n") ? "\r\n" : "\n";
  const trailingNewline = text.endsWith("\r\n") || text.endsWith("\n");
  const indentMatch = text.match(/\r?\n([ \t]+)[\"}]/);
  const indent = text.includes("\n") ? (indentMatch?.[1] || "  ") : null;
  return { bom, eol, trailingNewline, indent };
};

const serializeLike = (value, templateRaw) => {
  const format = detectJsonFormat(templateRaw);
  let text = format.indent === null
    ? JSON.stringify(value)
    : JSON.stringify(value, null, format.indent);
  if (format.eol === "\r\n") text = text.replace(/\n/g, "\r\n");
  if (format.trailingNewline && !text.endsWith(format.eol)) text += format.eol;
  if (format.bom) text = `\uFEFF${text}`;
  return Buffer.from(text, "utf8");
};

const resolveRepoFile = (reference, label, code = "BLOCKED_GOVERNANCE_REFERENCE_INVALID") => {
  if (typeof reference !== "string" || !reference.trim()) {
    FAIL(code, `${label}: 빈 reference`);
  }
  if (HTTP_URL.test(reference)) {
    FAIL(code, `${label}: repository artifact는 URL일 수 없음 — ${reference}`);
  }
  const absolute = resolve(REPO_ROOT, reference);
  if (absolute !== REPO_ROOT && !absolute.startsWith(`${REPO_ROOT}${sep}`)) {
    FAIL(code, `${label}: repository 밖 경로 — ${reference}`);
  }
  if (!existsSync(absolute)) {
    FAIL(code, `${label}: 파일 없음 — ${reference}`);
  }
  let stat;
  try { stat = statSync(absolute); } catch (error) {
    FAIL(code, `${label}: stat 실패 — ${reference}: ${error.message}`);
  }
  if (!stat.isFile() || stat.size <= 0) {
    FAIL(code, `${label}: 비어 있거나 파일이 아님 — ${reference}`);
  }
  return { absolute, raw: readFileSync(absolute) };
};

const loadReferencedJson = (reference, label) => {
  const resolved = resolveRepoFile(reference, label);
  try {
    const value = JSON.parse(resolved.raw.toString("utf8").replace(/^\uFEFF/, ""));
    assertObject(value, label, "BLOCKED_GOVERNANCE_REFERENCE_INVALID");
    return value;
  } catch (error) {
    if (error?.code === "BLOCKED_GOVERNANCE_REFERENCE_INVALID") throw error;
    FAIL("BLOCKED_GOVERNANCE_REFERENCE_INVALID", `${label}: JSON 파싱 실패 — ${reference}: ${error.message}`);
  }
};

const validateEvidenceReference = (reference, label) => {
  if (typeof reference !== "string" || !reference.trim()) {
    FAIL("BLOCKED_EVIDENCE_REFERENCE_INVALID", `${label}: 빈 reference`);
  }
  if (HTTP_URL.test(reference)) {
    let parsed;
    try { parsed = new URL(reference); } catch (error) {
      FAIL("BLOCKED_EVIDENCE_REFERENCE_INVALID", `${label}: URL 파싱 실패 — ${reference}: ${error.message}`);
    }
    if (!["http:", "https:"].includes(parsed.protocol) || !parsed.hostname) {
      FAIL("BLOCKED_EVIDENCE_REFERENCE_INVALID", `${label}: http(s) absolute URL 필요 — ${reference}`);
    }
    return;
  }
  resolveRepoFile(reference, label, "BLOCKED_EVIDENCE_REFERENCE_INVALID");
};

const validateStageArtifact = (reference, label) => {
  const { raw } = resolveRepoFile(reference, label);
  if (!reference.toLowerCase().endsWith(".json")) return;
  let payload;
  try { payload = JSON.parse(raw.toString("utf8").replace(/^\uFEFF/, "")); }
  catch (error) {
    FAIL("BLOCKED_STAGE_ARTIFACT_INVALID", `${label}: JSON 파싱 실패 — ${reference}: ${error.message}`);
  }
  assertObject(payload, label, "BLOCKED_STAGE_ARTIFACT_INVALID");
  const marker = payload.status ?? payload.artifact_status ?? payload.state ?? payload.result;
  if (typeof marker === "string" && BLOCKED_STATUS.test(marker)) {
    FAIL("BLOCKED_STAGE_ARTIFACT_NOT_PASSING", `${label}: 비통과 상태 ${marker} — ${reference}`);
  }
  if (!(typeof payload.stage === "string" || typeof marker === "string" || typeof payload.schema === "string")) {
    FAIL("BLOCKED_STAGE_ARTIFACT_INVALID", `${label}: stage/status/schema 식별자 없음 — ${reference}`);
  }
};

const requireBooleanTrue = (payload, key, label) => {
  if (payload[key] !== true) FAIL("BLOCKED_GOVERNANCE_ARTIFACT_NOT_PASSING", `${label}.${key} !== true`);
};
const requireEmptyArray = (payload, key, label) => {
  if (!Array.isArray(payload[key]) || payload[key].length) {
    FAIL("BLOCKED_GOVERNANCE_ARTIFACT_NOT_PASSING", `${label}.${key}는 빈 배열이어야 함`);
  }
};

const validateGovernanceReferences = (run) => {
  const d = loadReferencedJson(run.document_universe_manifest_ref, "Stage 0.0D manifest");
  if (d.stage !== "0.0D" || d.status !== "PASS") {
    FAIL("BLOCKED_GOVERNANCE_ARTIFACT_NOT_PASSING", "Stage 0.0D status=PASS 필요");
  }
  requireBooleanTrue(d, "all_docs_files_read_or_parsed", "Stage 0.0D");
  requireBooleanTrue(d, "stage_0_0c_authorized", "Stage 0.0D");
  requireEmptyArray(d, "unresolved_rule_conflicts", "Stage 0.0D");
  requireEmptyArray(d, "incomplete_universe_defects", "Stage 0.0D");
  if (d.repository_head_sha !== run.base_main_commit_sha) {
    FAIL("BLOCKED_GOVERNANCE_ARTIFACT_STALE", `Stage 0.0D repository_head_sha ${d.repository_head_sha} != ${run.base_main_commit_sha}`);
  }
  if (d.canonical_full_blob_sha !== run.base_full_blob_sha) {
    FAIL("BLOCKED_GOVERNANCE_ARTIFACT_STALE", `Stage 0.0D canonical_full_blob_sha ${d.canonical_full_blob_sha} != ${run.base_full_blob_sha}`);
  }

  const c = loadReferencedJson(run.coverage_discovery_ref, "Stage 0.0C artifact");
  if (c.stage !== "0.0C" || c.status !== "PASS") {
    FAIL("BLOCKED_GOVERNANCE_ARTIFACT_NOT_PASSING", "Stage 0.0C status=PASS 필요");
  }
  requireBooleanTrue(c, "original_input_accounted", "Stage 0.0C");
  requireBooleanTrue(c, "stage_a_authorized", "Stage 0.0C");
  if (c.document_universe_manifest_ref !== run.document_universe_manifest_ref) {
    FAIL("BLOCKED_GOVERNANCE_ARTIFACT_STALE", "Stage 0.0C document_universe_manifest_ref 불일치");
  }
  if (c.base_full_blob_sha !== run.base_full_blob_sha) {
    FAIL("BLOCKED_GOVERNANCE_ARTIFACT_STALE", "Stage 0.0C base_full_blob_sha 불일치");
  }

  const completeness = loadReferencedJson(run.independent_completeness_ref, "Stage 0.7C artifact");
  if (completeness.stage !== "0.7C"
    || completeness.status !== "PASS_WITH_DECLARED_RESIDUAL_RISK") {
    FAIL("BLOCKED_GOVERNANCE_ARTIFACT_NOT_PASSING", "Stage 0.7C PASS_WITH_DECLARED_RESIDUAL_RISK 필요");
  }
  for (const key of [
    "source_universe_accounted", "regional_search_complete", "topic_search_complete",
    "baseline_follow_up_review_complete", "review_pool_rescue_complete",
    "must_report_candidates_accounted", "prompt_0_8_authorized",
  ]) requireBooleanTrue(completeness, key, "Stage 0.7C");
  if (completeness.reviewer_independence !== "SEPARATE_PASS") {
    FAIL("BLOCKED_GOVERNANCE_ARTIFACT_NOT_PASSING", "Stage 0.7C reviewer_independence=SEPARATE_PASS 필요");
  }

  run.audit_refs.forEach((reference, index) => resolveRepoFile(reference, `audit_refs[${index}]`));
  for (const [kind, operations] of Object.entries(run.operations)) {
    operations.forEach((operation, index) => {
      const stageRefs = operation.stage_artifacts || [];
      stageRefs.forEach((reference, refIndex) =>
        validateStageArtifact(reference, `${kind}[${index}].stage_artifacts[${refIndex}]`));
      operation.evidence_refs.forEach((reference, refIndex) =>
        validateEvidenceReference(reference, `${kind}[${index}].evidence_refs[${refIndex}]`));
    });
  }
};

const decodePointerToken = (token) => token.replace(/~1/g, "/").replace(/~0/g, "~");
const parsePointer = (pointer) => {
  if (typeof pointer !== "string" || !pointer.startsWith("/") || pointer === "/") {
    FAIL("INVALID_POINTER", `JSON Pointer는 비어 있지 않은 / 경로여야 함: ${pointer}`);
  }
  return pointer.slice(1).split("/").map(decodePointerToken);
};
const isArrayIndex = (token) => /^(0|[1-9]\d*)$/.test(token);

const pointerParent = (root, pointer, { create = false } = {}) => {
  const tokens = parsePointer(pointer);
  let current = root;
  for (const token of tokens.slice(0, -1)) {
    if (Array.isArray(current)) {
      if (!isArrayIndex(token) || Number(token) >= current.length) {
        FAIL("INVALID_POINTER", `배열 범위 오류: ${pointer}`);
      }
      current = current[Number(token)];
      continue;
    }
    if (!current || typeof current !== "object") {
      FAIL("INVALID_POINTER", `중간 경로가 객체/배열이 아님: ${pointer}`);
    }
    if (!Object.hasOwn(current, token)) {
      if (!create) FAIL("INVALID_POINTER", `존재하지 않는 중간 경로: ${pointer}`);
      current[token] = {};
    }
    current = current[token];
  }
  return { parent: current, key: tokens.at(-1), tokens };
};

const relationRoots = new Set(["related", "related_ids", "related_lineage"]);
const edgeRoots = new Set(["related", "related_ids"]);

const applyUpdateChange = (card, change) => {
  assertObject(change, "update.change");
  const allowed = new Set(["add", "replace", "remove"]);
  if (!allowed.has(change.op)) FAIL("INVALID_UPDATE", `지원하지 않는 update op: ${change.op}`);
  const tokens = parsePointer(change.path);
  const root = tokens[0];
  if (root === "id") FAIL("IMMUTABLE_ID", "기존 카드 id 변경은 허용되지 않음");
  if (root === "source_spec_id") {
    FAIL("IMMUTABLE_SOURCE_SPEC_ID", "source_spec_id는 formal binding metadata이며 card update로 변경할 수 없음");
  }
  if (relationRoots.has(root)) {
    FAIL("RELATION_UPDATE_FORBIDDEN", `${change.path}는 related_add에서만 변경 가능`);
  }
  if ((change.op === "add" || change.op === "replace") && !("value" in change)) {
    FAIL("INVALID_UPDATE", `${change.op}에는 value가 필요함: ${change.path}`);
  }
  if (change.op === "remove" && "value" in change) {
    FAIL("INVALID_UPDATE", `remove에는 value를 둘 수 없음: ${change.path}`);
  }
  const { parent, key } = pointerParent(card, change.path, { create: change.op === "add" });
  if (Array.isArray(parent)) {
    if (change.op === "add") {
      if (key === "-") parent.push(deepClone(change.value));
      else if (isArrayIndex(key) && Number(key) <= parent.length) {
        parent.splice(Number(key), 0, deepClone(change.value));
      } else FAIL("INVALID_POINTER", `배열 add 위치 오류: ${change.path}`);
    } else {
      if (!isArrayIndex(key) || Number(key) >= parent.length) {
        FAIL("INVALID_POINTER", `배열 범위 초과: ${change.path}`);
      }
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

const validateRelationPatch = (operation, patch) => {
  assertObject(patch, "related_add.patch");
  const allowedKeys = new Set(["card_id", "op", "path", "value"]);
  const extras = Object.keys(patch).filter((key) => !allowedKeys.has(key));
  if (extras.length) FAIL("INVALID_RELATED_PATCH", `지원하지 않는 patch 필드: ${extras.join(", ")}`);
  if (![operation.source_id, operation.target_id].includes(patch.card_id)) {
    FAIL("INVALID_RELATED_PATCH_CARD", `patch card는 source/target 중 하나여야 함: ${patch.card_id}`);
  }
  if (!new Set(["add", "replace"]).has(patch.op)) {
    FAIL("RELATION_APPEND_ONLY", `related_add patch는 add/metadata replace만 허용: ${patch.op}`);
  }
  if (!("value" in patch)) FAIL("INVALID_RELATED_PATCH", `value 누락: ${patch.path}`);
  const tokens = parsePointer(patch.path);
  const root = tokens[0];
  if (!relationRoots.has(root)) FAIL("INVALID_RELATED_PATH", `관계 경로가 아님: ${patch.path}`);

  if (edgeRoots.has(root)) {
    if (patch.op !== "add" || tokens.length !== 2 || tokens[1] !== "-") {
      FAIL("RELATION_APPEND_ONLY", `${root}는 /${root}/- add만 허용: ${patch.path}`);
    }
    const expected = patch.card_id === operation.source_id ? operation.target_id : operation.source_id;
    if (patch.value !== expected) {
      FAIL("UNDECLARED_RELATED_EDGE", `${patch.card_id} patch가 선언 상대가 아닌 ${patch.value}를 가리킴`);
    }
    if (operation.direction === "directional" && patch.card_id === operation.target_id) {
      FAIL("UNDECLARED_RELATED_EDGE", "directional 관계에 역방향 edge patch를 둘 수 없음");
    }
  } else {
    const expected = patch.card_id === operation.source_id ? operation.target_id : operation.source_id;
    if (operation.direction === "directional" && patch.card_id === operation.target_id) {
      FAIL("UNDECLARED_RELATED_EDGE", "directional 관계에 target-side lineage patch를 둘 수 없음");
    }
    const path = `/${tokens.join("/")}`;
    if (path === "/related_lineage/related_ids/-") {
      if (patch.op !== "add" || patch.value !== expected) {
        FAIL("UNDECLARED_RELATED_EDGE", `${patch.card_id} lineage target은 선언 상대 ${expected}여야 함`);
      }
    } else {
      const expectedMetadata = new Map([
        ["/related_lineage/relation_type", operation.relation_type],
        ["/related_lineage/reason", operation.lineage_reason],
        ["/related_lineage/event_stage_relationship", operation.event_stage_relationship],
        ["/related_lineage/direction", operation.direction],
      ]);
      if (!expectedMetadata.has(path) || patch.value !== expectedMetadata.get(path)) {
        FAIL("INVALID_RELATED_PATH", `관련 metadata는 선언값과 일치하는 허용 경로만 가능: ${patch.path}`);
      }
    }
  }
};

const applyRelationPatch = (cardsById, operation, patch) => {
  validateRelationPatch(operation, patch);
  const card = cardsById.get(patch.card_id);
  if (!card) FAIL("MISSING_RELATED_PATCH_CARD", `patch card 없음: ${patch.card_id}`);
  const { parent, key } = pointerParent(card, patch.path, { create: patch.op === "add" });
  if (Array.isArray(parent)) {
    if (key !== "-" || patch.op !== "add") {
      FAIL("RELATION_APPEND_ONLY", `관계 배열은 /- add만 허용: ${patch.path}`);
    }
    if (parent.some((entry) => deepEqual(entry, patch.value))) {
      FAIL("DUPLICATE_RELATED_EDGE", `이미 존재하는 관계 값: ${patch.card_id} ${patch.path}`);
    }
    parent.push(deepClone(patch.value));
    return;
  }
  if (!parent || typeof parent !== "object") FAIL("INVALID_RELATED_PATH", `부모가 객체가 아님: ${patch.path}`);
  const exists = Object.hasOwn(parent, key);
  if (patch.op === "add") {
    if (exists) FAIL("DUPLICATE_RELATED_EDGE", `이미 존재하는 관계 경로: ${patch.path}`);
    parent[key] = deepClone(patch.value);
  } else {
    if (!exists) FAIL("INVALID_RELATED_PATH", `replace 대상 없음: ${patch.path}`);
    parent[key] = deepClone(patch.value);
  }
};

const validateRunShape = (run) => {
  assertObject(run, "run");
  const allowedTop = new Set([
    "schema", "run_id", "base_main_commit_sha", "base_full_blob_sha", "expected_before",
    "output_updated", "operations", "expected_after", "audit_refs",
    "document_universe_manifest_ref", "coverage_discovery_ref",
    "independent_completeness_ref", "notes",
  ]);
  const unknownTop = Object.keys(run).filter((key) => !allowedTop.has(key));
  if (unknownTop.length) FAIL("INVALID_RUN", `지원하지 않는 top-level 필드: ${unknownTop.join(", ")}`);
  if (run.schema !== "card_run_v1") FAIL("INVALID_RUN", "schema는 card_run_v1이어야 함");
  if (typeof run.run_id !== "string" || !run.run_id.trim()) FAIL("INVALID_RUN", "run_id 누락");
  for (const key of ["base_main_commit_sha", "base_full_blob_sha"]) {
    if (typeof run[key] !== "string" || !/^[0-9a-f]{40}$/.test(run[key])) {
      FAIL("INVALID_RUN", `${key}는 40자리 소문자 SHA여야 함`);
    }
  }
  if (!Number.isInteger(run.expected_before) || run.expected_before < 0) FAIL("INVALID_RUN", "expected_before 오류");
  if (!Number.isInteger(run.expected_after) || run.expected_after < 0) FAIL("INVALID_RUN", "expected_after 오류");
  if (typeof run.output_updated !== "string" || Number.isNaN(Date.parse(run.output_updated))) {
    FAIL("INVALID_RUN", "output_updated는 파싱 가능한 ISO datetime이어야 함");
  }
  assertObject(run.operations, "operations");
  const allowedOps = new Set(["insert", "update", "related_add"]);
  const unknownOps = Object.keys(run.operations).filter((key) => !allowedOps.has(key));
  if (unknownOps.length) FAIL("FORBIDDEN_OPERATION", `허용되지 않는 operation: ${unknownOps.join(", ")}`);
  for (const key of allowedOps) {
    if (!Array.isArray(run.operations[key])) FAIL("INVALID_RUN", `operations.${key}는 배열이어야 함`);
  }
  assertStringArray(run.audit_refs, "audit_refs");
  for (const key of ["document_universe_manifest_ref", "coverage_discovery_ref", "independent_completeness_ref"]) {
    if (typeof run[key] !== "string" || !run[key].trim()) FAIL("INVALID_RUN", `${key} 누락`);
  }
};

const validateInsert = (operation) => {
  assertObject(operation, "insert operation");
  const allowedKeys = new Set(["card", "stage_artifacts", "evidence_refs"]);
  const extras = Object.keys(operation).filter((key) => !allowedKeys.has(key));
  if (extras.length) FAIL("INVALID_INSERT", `지원하지 않는 insert 필드: ${extras.join(", ")}`);
  assertObject(operation.card, "insert.card", "INVALID_INSERT");
  if (typeof operation.card.id !== "string" || !operation.card.id.trim()) FAIL("INVALID_INSERT", "insert.card.id 누락");
  for (const root of ["related", "related_ids"]) {
    if (operation.card[root] !== undefined
      && (!Array.isArray(operation.card[root]) || operation.card[root].length)) {
      FAIL("INVALID_INSERT", `${operation.card.id}.${root}는 비워 두고 related_add로 선언할 것`);
    }
  }
  if (operation.card.related_lineage !== undefined) {
    const rl = operation.card.related_lineage;
    assertObject(rl, `${operation.card.id}.related_lineage`, "INVALID_INSERT");
    const ids = Array.isArray(rl.related_ids) ? rl.related_ids : [];
    if (ids.length || String(rl.relation_type || "") !== "new_unrelated_event") {
      FAIL("INVALID_INSERT", `${operation.card.id}.related_lineage는 독립 사건 판정만 insert에 포함 가능`);
    }
  }
  assertStringArray(operation.stage_artifacts, `${operation.card.id}.stage_artifacts`);
  assertStringArray(operation.evidence_refs, `${operation.card.id}.evidence_refs`);
};

const validateUpdate = (operation) => {
  assertObject(operation, "update operation");
  const allowedKeys = new Set(["id", "source_spec_id", "changes", "reason", "stage_artifacts", "evidence_refs"]);
  const extras = Object.keys(operation).filter((key) => !allowedKeys.has(key));
  if (extras.length) FAIL("INVALID_UPDATE", `지원하지 않는 update 필드: ${extras.join(", ")}`);
  if (typeof operation.id !== "string" || !operation.id.trim()) FAIL("INVALID_UPDATE", "update.id 누락");
  if (operation.source_spec_id !== undefined
    && (typeof operation.source_spec_id !== "string" || !operation.source_spec_id.trim())) {
    FAIL("INVALID_UPDATE", `${operation.id}: source_spec_id는 비어 있지 않은 binding metadata여야 함`);
  }
  if (!Array.isArray(operation.changes) || !operation.changes.length) FAIL("INVALID_UPDATE", `${operation.id}: changes가 비어 있음`);
  if (typeof operation.reason !== "string" || !operation.reason.trim()) FAIL("INVALID_UPDATE", `${operation.id}: reason 누락`);
  assertStringArray(operation.stage_artifacts, `${operation.id}.stage_artifacts`);
  assertStringArray(operation.evidence_refs, `${operation.id}.evidence_refs`);
  const paths = operation.changes.map((change) => change.path);
  if (!unique(paths)) FAIL("INVALID_UPDATE", `${operation.id}: 중복 변경 경로`);
};

const validateRelatedAdd = (operation) => {
  assertObject(operation, "related_add operation");
  const allowedKeys = new Set([
    "source_id", "target_id", "source_spec_id", "identity_card_id",
    "relation_type", "lineage_reason", "event_stage_relationship", "direction",
    "stage_artifacts", "evidence_refs", "patches",
  ]);
  const extras = Object.keys(operation).filter((key) => !allowedKeys.has(key));
  if (extras.length) FAIL("INVALID_RELATED_ADD", `지원하지 않는 related_add 필드: ${extras.join(", ")}`);
  for (const key of ["source_id", "target_id", "relation_type", "lineage_reason", "event_stage_relationship"]) {
    if (typeof operation[key] !== "string" || !operation[key].trim()) FAIL("INVALID_RELATED_ADD", `${key} 누락`);
  }
  for (const key of ["source_spec_id", "identity_card_id"]) {
    if (operation[key] !== undefined && (typeof operation[key] !== "string" || !operation[key].trim())) {
      FAIL("INVALID_RELATED_ADD", `${key}는 비어 있지 않은 binding metadata여야 함`);
    }
  }
  if (operation.source_id === operation.target_id) FAIL("SELF_RELATED_EDGE", `${operation.source_id}: self relation`);
  if (!new Set(["directional", "reciprocal"]).has(operation.direction)) FAIL("INVALID_RELATED_ADD", "direction 오류");
  assertStringArray(operation.stage_artifacts, "related_add.stage_artifacts");
  assertStringArray(operation.evidence_refs, "related_add.evidence_refs");
  if (!Array.isArray(operation.patches) || !operation.patches.length) FAIL("INVALID_RELATED_ADD", "patches가 비어 있음");
  operation.patches.forEach((patch) => validateRelationPatch(operation, patch));
};

const validateDocument = (doc, label) => {
  if (!doc || typeof doc !== "object" || Array.isArray(doc) || !Array.isArray(doc.cards)) {
    FAIL("BLOCKED_CANONICAL_FULL_UNREADABLE", `${label} 최상위 객체/cards 배열 계약 불일치`);
  }
  const ids = doc.cards.map((card) => card?.id);
  if (ids.some((id) => typeof id !== "string" || !id)) FAIL("INVALID_CANONICAL_FULL", `${label}: id 없는 카드 존재`);
  if (!unique(ids)) FAIL("INVALID_CANONICAL_FULL", `${label}: 중복 id 존재`);
};

const isLatestFirst = (cards) => {
  for (let index = 1; index < cards.length; index += 1) {
    if (String(cards[index - 1].date || "") < String(cards[index].date || "")) return false;
  }
  return true;
};
const stableLatestFirst = (cards) => cards
  .map((card, index) => ({ card, index }))
  .sort((left, right) => String(right.card.date || "").localeCompare(String(left.card.date || "")) || left.index - right.index)
  .map(({ card }) => card);

const snapshotEdges = (cards) => {
  const ids = new Set(cards.map((card) => card.id));
  const edges = new Set();
  const missing = new Set();
  for (const card of cards) {
    for (const root of edgeRoots) {
      if (card[root] === undefined) continue;
      if (!Array.isArray(card[root])) FAIL("INVALID_CANONICAL_FULL", `${card.id}.${root}는 배열이어야 함`);
      const seen = new Set();
      for (const target of card[root]) {
        if (typeof target !== "string" || !target.trim()) FAIL("INVALID_CANONICAL_FULL", `${card.id}.${root} 비문자열 target`);
        if (target === card.id) FAIL("SELF_RELATED_EDGE", `${card.id}.${root} self relation`);
        if (seen.has(target)) FAIL("DUPLICATE_RELATED_EDGE", `${card.id}.${root} 중복 target ${target}`);
        seen.add(target);
        const edge = `${root}:${card.id}→${target}`;
        edges.add(edge);
        if (!ids.has(target)) missing.add(edge);
      }
    }
  }
  return { edges, missing };
};

const validateRelationResult = (cards, baselineEdges, baselineMissing) => {
  const current = snapshotEdges(cards);
  const lost = [...baselineEdges].filter((edge) => !current.edges.has(edge));
  if (lost.length) {
    FAIL("BLOCKED_EXISTING_RELATED_EDGE_LOSS", `기존 관계 ${lost.length}건 소실 — ${lost.slice(0, 5).join(", ")}`);
  }
  const newMissing = [...current.missing].filter((edge) => !baselineMissing.has(edge));
  if (newMissing.length) {
    FAIL("BLOCKED_NEW_MISSING_RELATED_TARGETS", `신규 dangling ${newMissing.length}건 — ${newMissing.slice(0, 5).join(", ")}`);
  }
};

const validateDeclaredConnectivity = (operation) => {
  const edgePatches = operation.patches.filter((patch) => {
    const root = parsePointer(patch.path)[0];
    return edgeRoots.has(root);
  });
  const sourceConnected = edgePatches.some((patch) =>
    patch.card_id === operation.source_id && patch.value === operation.target_id);
  if (!sourceConnected) {
    FAIL("RELATED_TARGET_NOT_DECLARED", `${operation.source_id} → ${operation.target_id} edge patch 없음`);
  }
  if (operation.direction === "reciprocal") {
    const targetConnected = edgePatches.some((patch) =>
      patch.card_id === operation.target_id && patch.value === operation.source_id);
    if (!targetConnected) {
      FAIL("RELATED_RECIPROCAL_MISSING", `${operation.target_id} → ${operation.source_id} reciprocal patch 없음`);
    }
  }
};

const atomicWrite = (path, bytes) => {
  mkdirSync(dirname(path), { recursive: true });
  const temporary = `${path}.tmp-${process.pid}`;
  writeFileSync(temporary, bytes);
  renameSync(temporary, path);
};

const buildExpected = (baseDoc, run) => {
  validateDocument(baseDoc, "canonical baseline");
  if (baseDoc.cards.length !== run.expected_before) {
    FAIL("BLOCKED_BASELINE_MOVED_REBASE_REQUIRED", `카드 수 ${baseDoc.cards.length} != expected_before ${run.expected_before}`);
  }
  if (!isLatestFirst(baseDoc.cards)) FAIL("LATEST_FIRST_BASELINE_FAILED", "canonical baseline이 latest-first가 아님");

  const baselineIds = new Set(baseDoc.cards.map((card) => card.id));
  const { edges: baselineEdges, missing: baselineMissing } = snapshotEdges(baseDoc.cards);
  const result = deepClone(baseDoc);
  const insertOps = run.operations.insert;
  const updateOps = run.operations.update;
  const relatedOps = run.operations.related_add;

  const incomingIds = insertOps.map((operation) => {
    validateInsert(operation);
    return operation.card.id;
  });
  if (!unique(incomingIds)) FAIL("DUPLICATE_INSERT_ID", "insert id 중복");
  for (const id of incomingIds) {
    if (baselineIds.has(id)) FAIL("DUPLICATE_INSERT_ID", `insert id가 baseline에 존재: ${id}`);
  }
  const updateIds = updateOps.map((operation) => {
    validateUpdate(operation);
    return operation.id;
  });
  if (!unique(updateIds)) FAIL("INVALID_UPDATE", "같은 카드의 update는 하나로 합칠 것");
  for (const id of updateIds) {
    if (!baselineIds.has(id)) FAIL("UPDATE_TARGET_MISSING", `update target 없음: ${id}`);
  }
  relatedOps.forEach(validateRelatedAdd);

  const cardsById = new Map(result.cards.map((card) => [card.id, card]));
  for (const operation of updateOps) {
    const card = cardsById.get(operation.id);
    for (const change of operation.changes) applyUpdateChange(card, change);
  }
  for (const operation of insertOps) {
    const card = deepClone(operation.card);
    result.cards.push(card);
    cardsById.set(card.id, card);
  }
  result.cards = stableLatestFirst(result.cards);
  const resultById = new Map(result.cards.map((card) => [card.id, card]));

  const declaredPairs = new Set();
  for (const operation of relatedOps) {
    const pair = `${operation.direction}:${operation.source_id}→${operation.target_id}`;
    if (declaredPairs.has(pair)) FAIL("INVALID_RELATED_ADD", `중복 related_add 선언: ${pair}`);
    declaredPairs.add(pair);
    if (!resultById.has(operation.source_id) || !resultById.has(operation.target_id)) {
      FAIL("BLOCKED_NEW_MISSING_RELATED_TARGETS", `${operation.source_id} ↔ ${operation.target_id} 중 카드 없음`);
    }
    validateDeclaredConnectivity(operation);
    for (const patch of operation.patches) applyRelationPatch(resultById, operation, patch);
  }

  if (result.cards.length !== run.expected_after
    || run.expected_after !== run.expected_before + insertOps.length) {
    FAIL("COUNT_RECONCILIATION_FAILED",
      `expected ${run.expected_before}+${insertOps.length}=${run.expected_before + insertOps.length}, result ${result.cards.length}, declared ${run.expected_after}`);
  }
  if (!isLatestFirst(result.cards)) FAIL("LATEST_FIRST_RESULT_FAILED", "result가 latest-first가 아님");
  for (const id of baselineIds) {
    if (!resultById.has(id)) FAIL("UNDECLARED_CARD_LOSS", `기존 카드 소실: ${id}`);
  }
  validateRelationResult(result.cards, baselineEdges, baselineMissing);

  result.total = result.cards.length;
  result.updated = run.output_updated;
  return result;
};

const options = parseArgs(process.argv.slice(2));
if (!existsSync(options.baseline)) FAIL("BLOCKED_CANONICAL_FULL_UNREADABLE", `working full 없음: ${options.baseline}`);
if (!options.baseMainSha || !/^[0-9a-f]{40}$/.test(options.baseMainSha)) {
  FAIL("BLOCKED_INCREMENTAL_MERGE_PRECONDITION_MISSING", "--base-main-sha 또는 CARD_RUN_BASE_MAIN_SHA가 필요함");
}
const run = readJson(options.run, "card run").value;
validateRunShape(run);
validateGovernanceReferences(run);
if (run.base_main_commit_sha !== options.baseMainSha) {
  FAIL("BLOCKED_BASELINE_MOVED_REBASE_REQUIRED", `main SHA ${options.baseMainSha} != run ${run.base_main_commit_sha}`);
}

const gitBlob = git(["rev-parse", `${run.base_main_commit_sha}:${options.canonicalPath}`]);
if (gitBlob !== run.base_full_blob_sha) {
  FAIL("BLOCKED_BASELINE_MOVED_REBASE_REQUIRED", `main full blob ${gitBlob} != run ${run.base_full_blob_sha}`);
}
const baseBytes = git(["show", `${run.base_main_commit_sha}:${options.canonicalPath}`], { bytes: true });
let baseDoc;
try {
  baseDoc = JSON.parse(baseBytes.toString("utf8").replace(/^\uFEFF/, ""));
} catch (error) {
  FAIL("BLOCKED_CANONICAL_FULL_UNREADABLE", `git canonical full 파싱 실패: ${error.message}`);
}
const expected = buildExpected(baseDoc, run);
const expectedBytes = serializeLike(expected, baseBytes);
const workingLoaded = readJson(options.baseline, "working canonical full");
const working = workingLoaded.value;
validateDocument(working, "working canonical full");
const workingCanonical = canonical(working);
const baseCanonical = canonical(baseDoc);
const expectedCanonical = canonical(expected);
let state;
if (workingCanonical === expectedCanonical) {
  state = workingLoaded.raw.equals(expectedBytes) ? "ALREADY_APPLIED" : "READY_TO_NORMALIZE";
} else if (workingCanonical === baseCanonical) state = "READY_TO_APPLY";
else FAIL("BLOCKED_UNDECLARED_CARD_DIFF", "working full이 declared main baseline도 expected output도 아님");

if (options.mode === "verify" && state !== "ALREADY_APPLIED") {
  FAIL("VERIFY_NOT_APPLIED", `canonical full이 byte-exact expected output이 아님: ${state}`);
}

const writeReport = (status, ready) => {
  const fullBytes = existsSync(options.output) ? readFileSync(options.output) : expectedBytes;
  const leanBytes = existsSync(options.leanPath) ? readFileSync(options.leanPath) : null;
  const report = {
    schema: "card_run_apply_report_v1",
    run_id: run.run_id,
    status,
    base_main_commit_sha: run.base_main_commit_sha,
    base_full_blob_sha: run.base_full_blob_sha,
    expected_before: run.expected_before,
    insert_count: run.operations.insert.length,
    update_count: run.operations.update.length,
    related_add_count: run.operations.related_add.length,
    delete_count: 0,
    related_remove_count: 0,
    existing_related_preserved: true,
    undeclared_existing_card_change_count: 0,
    governance_refs_validated: true,
    expected_after: run.expected_after,
    full_output_sha256: sha256(fullBytes),
    lean_output_sha256: leanBytes ? sha256(leanBytes) : "",
    github_merge_ready: Boolean(ready && leanBytes),
  };
  atomicWrite(options.report, Buffer.from(`${JSON.stringify(report, null, 2)}\n`));
  return report;
};

if (options.mode === "check") {
  console.log(JSON.stringify({
    run_id: run.run_id,
    state,
    expected_before: run.expected_before,
    expected_after: run.expected_after,
    full_output_sha256: sha256(expectedBytes),
  }, null, 2));
  console.log(`PASS: ${run.run_id} check — ${run.expected_before} → ${run.expected_after}`);
  process.exit(0);
}

if (options.mode === "verify") {
  const report = writeReport("VERIFIED", true);
  if (!report.lean_output_sha256) FAIL("LEAN_PROJECTION_MISSING", `lean projection 없음: ${options.leanPath}`);
  console.log(`PASS: ${run.run_id} verified — github_merge_ready=true`);
  process.exit(0);
}

const backup = options.output === options.baseline ? `${options.output}.card-run-backup-${process.pid}` : null;
try {
  if (state !== "ALREADY_APPLIED") {
    if (backup) copyFileSync(options.baseline, backup);
    atomicWrite(options.output, expectedBytes);
  }
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
      if (backup && existsSync(backup)) copyFileSync(backup, options.output);
      FAIL("LEAN_PROJECTION_FAILED", `lean exporter exit ${lean.status}`);
    }
  }
  writeReport(state === "ALREADY_APPLIED" ? "ALREADY_APPLIED" : (state === "READY_TO_NORMALIZE" ? "FORMATTING_NORMALIZED" : "APPLIED"), false);
  if (backup) rmSync(backup, { force: true });
  console.log(`PASS: ${run.run_id} ${state === "ALREADY_APPLIED" ? "already applied" : (state === "READY_TO_NORMALIZE" ? "format normalized" : "applied")} — ${run.expected_before} → ${run.expected_after}`);
  console.log(`REPORT: ${options.report}`);
} catch (error) {
  if (backup && existsSync(backup)) {
    copyFileSync(backup, options.output);
    rmSync(backup, { force: true });
  }
  throw error;
}
