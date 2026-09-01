#!/usr/bin/env node
import {
  existsSync,
  mkdtempSync,
  mkdirSync,
  readFileSync,
  rmSync,
  statSync,
  writeFileSync,
} from "node:fs";
import { tmpdir } from "node:os";
import { dirname, join, resolve, sep } from "node:path";

class ValidationError extends Error {
  constructor(code, message) { super(message); this.code = code; }
}
const fail = (code, message) => { throw new ValidationError(code, message); };

const PASSING_STAGE_STATUSES = new Set([
  "PASS","PASSED","PASS_WITH_DECLARED_RESIDUAL_RISK","PASS_WITH_NOTES","PASS_WITH_WARNINGS",
  "VERIFIED","ACCEPTED_FACT_SAFE","ACCEPTED_FACT_SAFE_AFTER_CONTROLLED_RESCUE","ADDABLE_MERGE_SAFE",
  "EVIDENCE_COMPLETE","SOURCE_CLAIM_COVERED","EVIDENCE_COMPLETE_AND_SOURCE_CLAIM_COVERED",
  "CONTENT_ENRICHED","LANGUAGE_TERMINOLOGY_POLISHED","CONTENT_ENRICHED_AND_LANGUAGE_TERMINOLOGY_POLISHED",
  "PUBLISH_READY","GITHUB_MERGE_READY",
]);
const STATUS_FIELDS = ["status", "artifact_status", "validation_status", "state", "result"];
const RUN_LEVEL_ARTIFACTS = [
  ["document_universe_manifest_ref", "Stage 0.0D manifest"],
  ["coverage_discovery_ref", "Stage 0.0C artifact"],
  ["independent_completeness_ref", "Stage 0.7C artifact"],
];
const normalizeStatus = (value) => String(value).trim().toUpperCase();

const readJson = (path, label) => {
  let raw;
  try { raw = readFileSync(path, "utf8").replace(/^\uFEFF/, ""); }
  catch (error) { fail("BLOCKED_STAGE_ARTIFACT_INVALID", `${label}: 읽기 실패 — ${path}: ${error.message}`); }
  try { return JSON.parse(raw); }
  catch (error) { fail("BLOCKED_STAGE_ARTIFACT_INVALID", `${label}: JSON 파싱 실패 — ${path}: ${error.message}`); }
};

const resolveRepoJson = (root, reference, label) => {
  if (typeof reference !== "string" || !reference.trim()) fail("BLOCKED_STAGE_ARTIFACT_INVALID", `${label}: 빈 reference`);
  if (!reference.toLowerCase().endsWith(".json")) fail("BLOCKED_STAGE_ARTIFACT_INVALID", `${label}: JSON artifact여야 함 — ${reference}`);
  const absoluteRoot = resolve(root), absolute = resolve(absoluteRoot, reference);
  if (absolute !== absoluteRoot && !absolute.startsWith(`${absoluteRoot}${sep}`)) fail("BLOCKED_STAGE_ARTIFACT_INVALID", `${label}: repository 밖 경로 — ${reference}`);
  if (!existsSync(absolute)) fail("BLOCKED_STAGE_ARTIFACT_INVALID", `${label}: 파일 없음 — ${reference}`);
  const stat = statSync(absolute);
  if (!stat.isFile() || stat.size <= 0) fail("BLOCKED_STAGE_ARTIFACT_INVALID", `${label}: 비어 있거나 파일이 아님 — ${reference}`);
  return absolute;
};

const validateAllPresentStatusMarkers = (payload, label, reference) => {
  if (!payload || typeof payload !== "object" || Array.isArray(payload)) fail("BLOCKED_STAGE_ARTIFACT_INVALID", `${label}: 최상위 JSON 객체 필요 — ${reference}`);
  const markers = [];
  for (const field of STATUS_FIELDS) {
    if (!Object.hasOwn(payload, field) || payload[field] === null || payload[field] === undefined) continue;
    if (typeof payload[field] !== "string" || !payload[field].trim()) fail("BLOCKED_STAGE_ARTIFACT_STATUS_INVALID", `${label}.${field}: 비어 있지 않은 문자열 필요`);
    const normalized = normalizeStatus(payload[field]);
    markers.push({ field, raw: payload[field], normalized });
    if (!PASSING_STAGE_STATUSES.has(normalized)) {
      fail("BLOCKED_STAGE_ARTIFACT_CONFLICTING_STATUS", `${label}.${field}: 비통과 상태 ${payload[field]}가 다른 marker와 함께 존재 — ${reference}`);
    }
  }
  if (!markers.length) fail("BLOCKED_STAGE_ARTIFACT_STATUS_MISSING", `${label}: ${STATUS_FIELDS.join("/")} 중 명시적 상태 필요 — ${reference}`);
  return markers;
};

const validateBaselineBinding = (payload, run, label, reference) => {
  const stage = typeof payload?.stage === "string" ? payload.stage.trim().toLowerCase() : "";
  if (stage !== "0.4") return;
  if (typeof run?.base_main_commit_sha !== "string" || typeof run?.base_full_blob_sha !== "string") {
    fail("BLOCKED_STAGE_ARTIFACT_BASELINE_BINDING", `${label}: card run baseline SHA/blob are required`);
  }
  if (payload.base_main_commit_sha !== run.base_main_commit_sha) {
    fail("BLOCKED_STAGE_ARTIFACT_BASELINE_BINDING", `${label}: 0.4 base_main_commit_sha is stale or unbound — ${reference}`);
  }
  if (payload.base_full_blob_sha !== run.base_full_blob_sha) {
    fail("BLOCKED_STAGE_ARTIFACT_BASELINE_BINDING", `${label}: 0.4 base_full_blob_sha is stale or unbound — ${reference}`);
  }
};

const validateReference = (root, reference, label, kind, run) => {
  const absolute = resolveRepoJson(root, reference, label), payload = readJson(absolute, label);
  const markers = validateAllPresentStatusMarkers(payload, label, reference);
  if (kind === "operation_stage") validateBaselineBinding(payload, run, label, reference);
  return { kind, reference, markers };
};

const validateRun = (run, root = ".") => {
  if (!run || typeof run !== "object" || Array.isArray(run)) fail("INVALID_RUN", "card-run 최상위 객체 필요");
  if (!run.operations || typeof run.operations !== "object" || Array.isArray(run.operations)) fail("INVALID_RUN", "operations 객체 필요");
  const validated = [];
  for (const [field, label] of RUN_LEVEL_ARTIFACTS) validated.push(validateReference(root, run[field], label, "run_level_governance", run));
  for (const kind of ["insert", "update", "related_add"]) {
    const operations = run.operations[kind];
    if (!Array.isArray(operations)) fail("INVALID_RUN", `operations.${kind} 배열 필요`);
    operations.forEach((operation, operationIndex) => {
      if (!Array.isArray(operation.stage_artifacts) || !operation.stage_artifacts.length) fail("BLOCKED_STAGE_ARTIFACT_INVALID", `${kind}[${operationIndex}].stage_artifacts가 비어 있음`);
      operation.stage_artifacts.forEach((reference, referenceIndex) => {
        const label = `${kind}[${operationIndex}].stage_artifacts[${referenceIndex}]`;
        validated.push(validateReference(root, reference, label, "operation_stage", run));
      });
    });
  }
  return validated;
};

const runSelfTest = () => {
  const root = mkdtempSync(join(tmpdir(), "card-run-status-consistency-"));
  try {
    mkdirSync(join(root, "artifacts"), { recursive: true });
    const write = (name, payload) => { const path = join(root, "artifacts", name); mkdirSync(dirname(path), { recursive: true }); writeFileSync(path, `${JSON.stringify(payload, null, 2)}\n`); return `artifacts/${name}`; };
    const mainSha = "b".repeat(40), blobSha = "a".repeat(40);
    const pass = write("pass.json", { status: "PASS", validation_status: "VERIFIED" });
    const baselinePass = write("0.4.json", { stage: "0.4", status: "PASS", base_main_commit_sha: mainSha, base_full_blob_sha: blobSha });
    const stale = write("0.4-stale.json", { stage: "0.4", status: "PASS", base_main_commit_sha: "c".repeat(40), base_full_blob_sha: blobSha });
    const conflict = write("conflict.json", { status: "PASS", validation_status: "FAIL", result: "HOLD" });
    const makeRun = (operationReference = baselinePass, governanceReference = pass) => ({
      base_main_commit_sha: mainSha, base_full_blob_sha: blobSha,
      document_universe_manifest_ref: governanceReference, coverage_discovery_ref: pass, independent_completeness_ref: pass,
      operations: { insert: [{ stage_artifacts: [operationReference] }], update: [], related_add: [] },
    });
    validateRun(makeRun(), root);
    const expectCode = (run, code, label) => { let caught = null; try { validateRun(run, root); } catch (error) { caught = error; } if (!(caught instanceof ValidationError) || caught.code !== code) throw new Error(`${label}: expected ${code}, got ${caught?.code || "PASS"}`); };
    expectCode(makeRun(conflict, pass), "BLOCKED_STAGE_ARTIFACT_CONFLICTING_STATUS", "operation status conflict");
    expectCode(makeRun(pass, conflict), "BLOCKED_STAGE_ARTIFACT_CONFLICTING_STATUS", "run-level governance status conflict");
    expectCode(makeRun(stale, pass), "BLOCKED_STAGE_ARTIFACT_BASELINE_BINDING", "stale 0.4 baseline");
    console.log("PASS: stage status markers and 0.4 baseline binding are fail-closed");
  } finally { rmSync(root, { recursive: true, force: true }); }
};

const parseArgs = (argv) => {
  const options = { run: null, selfTest: false };
  for (let index = 0; index < argv.length; index += 1) {
    const arg = argv[index];
    if (arg === "--self-test") options.selfTest = true;
    else if (arg === "--run") { const value = argv[index + 1]; if (!value || value.startsWith("--")) fail("INVALID_ARGUMENT", "--run PATH가 필요함"); options.run = value; index += 1; }
    else fail("INVALID_ARGUMENT", `지원하지 않는 인자 ${arg}`);
  }
  return options;
};

try {
  const options = parseArgs(process.argv.slice(2));
  if (options.selfTest) { runSelfTest(); process.exit(0); }
  if (!options.run) fail("INVALID_ARGUMENT", "--run PATH가 필요함");
  const absolute = resolveRepoJson(".", options.run, "card run"), run = readJson(absolute, "card run"), validated = validateRun(run, ".");
  console.log(JSON.stringify({ status: "PASS", run_path: options.run, validated_artifact_count: validated.length, artifacts: validated }, null, 2));
  console.log(`PASS: ${validated.length} artifacts have passing status markers and current-run baseline bindings where required`);
} catch (error) {
  if (error instanceof ValidationError) { console.error(`FAIL [${error.code}]: ${error.message}`); process.exit(1); }
  throw error;
}
