#!/usr/bin/env node
import { existsSync, mkdtempSync, mkdirSync, readFileSync, rmSync, writeFileSync } from "node:fs";
import { dirname, join, resolve, sep } from "node:path";
import { spawnSync } from "node:child_process";
import { tmpdir } from "node:os";

class ValidationError extends Error {
  constructor(code, message) { super(message); this.code = code; }
}
const fail = (code, message) => { throw new ValidationError(code, message); };
const readJson = (path, label) => {
  try { return JSON.parse(readFileSync(path, "utf8").replace(/^\uFEFF/, "")); }
  catch (error) { fail("BLOCKED_V4_HARDENING_INVALID", `${label}: ${error.message}`); }
};
const resolveRepoJson = (root, reference, label) => {
  if (typeof reference !== "string" || !reference.trim() || !reference.endsWith(".json")) {
    fail("BLOCKED_V4_HARDENING_INVALID", `${label}: repository JSON reference required`);
  }
  const absoluteRoot = resolve(root);
  const absolute = resolve(absoluteRoot, reference);
  if (absolute !== absoluteRoot && !absolute.startsWith(`${absoluteRoot}${sep}`)) {
    fail("BLOCKED_V4_HARDENING_INVALID", `${label}: repository 밖 경로 — ${reference}`);
  }
  if (!existsSync(absolute)) fail("BLOCKED_V4_HARDENING_INVALID", `${label}: 파일 없음 — ${reference}`);
  return absolute;
};

const COMPLETENESS_BOOLEANS = [
  "source_universe_accounted",
  "regional_search_complete",
  "topic_search_complete",
  "baseline_follow_up_review_complete",
  "review_pool_rescue_complete",
  "must_report_candidates_accounted",
];

function validateCoverage(run, root) {
  const path = resolveRepoJson(root, run.coverage_discovery_ref, "coverage_discovery_ref");
  const artifact = readJson(path, "Stage 0.0C");
  if (artifact.stage !== "0.0C" || artifact.status !== "PASS") {
    fail("BLOCKED_COVERAGE_ENVELOPE", "coverage artifact must declare stage=0.0C and status=PASS");
  }
  if (artifact.original_input_accounted !== true) {
    fail("BLOCKED_COVERAGE_ENVELOPE", "0.0C original_input_accounted must be true");
  }
  if (artifact.stage_a_authorized !== true) {
    fail("BLOCKED_COVERAGE_ENVELOPE", "0.0C stage_a_authorized must be true");
  }
  if (artifact.document_universe_manifest_ref !== run.document_universe_manifest_ref) {
    fail("BLOCKED_COVERAGE_BINDING", "0.0C document_universe_manifest_ref must match the card run");
  }
  if (artifact.base_full_blob_sha !== run.base_full_blob_sha) {
    fail("BLOCKED_COVERAGE_BINDING", "0.0C base_full_blob_sha must match the card run");
  }
}

function validateCompleteness(run, root) {
  const path = resolveRepoJson(root, run.independent_completeness_ref, "independent_completeness_ref");
  const artifact = readJson(path, "Stage 0.7C");
  if (artifact.stage !== "0.7C") fail("BLOCKED_COMPLETENESS_ENVELOPE", "independent completeness stage must be 0.7C");
  if (artifact.status !== "PASS_WITH_DECLARED_RESIDUAL_RISK") {
    fail("BLOCKED_COMPLETENESS_ENVELOPE", "0.7C status must be PASS_WITH_DECLARED_RESIDUAL_RISK");
  }
  if (artifact.completeness_status !== artifact.status) {
    fail("BLOCKED_COMPLETENESS_ENVELOPE", "0.7C completeness_status must exactly equal status");
  }
  for (const field of COMPLETENESS_BOOLEANS) {
    if (artifact[field] !== true) fail("BLOCKED_COMPLETENESS_ENVELOPE", `0.7C ${field} must be true`);
  }
  if (artifact.reviewer_independence !== "SEPARATE_PASS") {
    fail("BLOCKED_COMPLETENESS_ENVELOPE", "0.7C reviewer_independence must be SEPARATE_PASS");
  }
  if (artifact.prompt_0_8_authorized !== true) {
    fail("BLOCKED_COMPLETENESS_ENVELOPE", "0.7C prompt_0_8_authorized must be true");
  }
  for (const field of ["material_exclusions", "known_unknowns", "residual_risks"]) {
    if (!Array.isArray(artifact[field])) fail("BLOCKED_COMPLETENESS_ENVELOPE", `0.7C ${field} must be an array`);
  }
}

function isStageAArtifact(payload) {
  return payload?.stage === "A" || Array.isArray(payload?.strict_passed_spec);
}

function runPythonChecker(checker, args, label) {
  const result = spawnSync("python3", [resolve(checker), ...args], { encoding: "utf8" });
  if (result.error) fail("BLOCKED_STAGE_A_V4_CONTRACT", `${label}: checker 실행 실패 — ${result.error.message}`);
  if (result.status !== 0) {
    const detail = (result.stdout || result.stderr || "Stage A contract failed").trim();
    fail("BLOCKED_STAGE_A_V4_CONTRACT", `${label}: ${detail}`);
  }
}

function validateStageAArtifact(path, label) {
  runPythonChecker("validation_scripts/stage_artifact_contract_check.py", ["A", path], label);
  runPythonChecker("validation_scripts/stage_lineage_contract_check.py", ["stage_a", path], label);
}

function validateRun(run, root = ".") {
  if (!run || typeof run !== "object" || Array.isArray(run)) fail("BLOCKED_V4_HARDENING_INVALID", "card-run object required");
  validateCoverage(run, root);
  validateCompleteness(run, root);
  let stageACount = 0;
  let operationCount = 0;
  for (const kind of ["insert", "update", "related_add"]) {
    const operations = run.operations?.[kind];
    if (!Array.isArray(operations)) fail("BLOCKED_V4_HARDENING_INVALID", `operations.${kind} array required`);
    for (const [operationIndex, operation] of operations.entries()) {
      operationCount += 1;
      if (!Array.isArray(operation?.stage_artifacts) || operation.stage_artifacts.length === 0) {
        fail("BLOCKED_V4_HARDENING_INVALID", `${kind}[${operationIndex}].stage_artifacts required`);
      }
      let operationStageACount = 0;
      for (const [referenceIndex, reference] of operation.stage_artifacts.entries()) {
        const label = `${kind}[${operationIndex}].stage_artifacts[${referenceIndex}]`;
        const path = resolveRepoJson(root, reference, label);
        const payload = readJson(path, label);
        if (isStageAArtifact(payload)) {
          validateStageAArtifact(path, label);
          stageACount += 1;
          operationStageACount += 1;
        }
      }
      if (operationStageACount === 0) {
        fail(
          "BLOCKED_OPERATION_STAGE_A_MISSING",
          `${kind}[${operationIndex}] must bind at least one passing Stage A artifact in its own stage_artifacts`,
        );
      }
    }
  }
  return { stage_a_artifacts_validated: stageACount, operations_with_stage_a: operationCount };
}

function selfTest() {
  const root = mkdtempSync(join(tmpdir(), "card-run-v4-hardening-"));
  try {
    mkdirSync(join(root, "artifacts"), { recursive: true });
    const write = (name, payload) => {
      const path = join(root, "artifacts", name);
      mkdirSync(dirname(path), { recursive: true });
      writeFileSync(path, `${JSON.stringify(payload, null, 2)}\n`);
      return `artifacts/${name}`;
    };
    const baseFullBlobSha = "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa";
    const documentUniverseRef = "artifacts/0.0d.json";
    const coverageRef = write("0.0c.json", {
      stage: "0.0C",
      status: "PASS",
      original_input_accounted: true,
      stage_a_authorized: true,
      document_universe_manifest_ref: documentUniverseRef,
      base_full_blob_sha: baseFullBlobSha,
    });
    write("0.0d.json", { stage: "0.0D", status: "PASS" });
    const completenessRef = write("0.7c.json", {
      stage: "0.7C",
      status: "PASS_WITH_DECLARED_RESIDUAL_RISK",
      completeness_status: "PASS_WITH_DECLARED_RESIDUAL_RISK",
      source_universe_accounted: true,
      regional_search_complete: true,
      topic_search_complete: true,
      baseline_follow_up_review_complete: true,
      review_pool_rescue_complete: true,
      must_report_candidates_accounted: true,
      material_exclusions: [], known_unknowns: [], residual_risks: [],
      reviewer_independence: "SEPARATE_PASS",
      prompt_0_8_authorized: true,
    });
    const malformedStageA = write("stage-a.json", { stage: "A", status: "PASS", strict_passed_spec: [{}] });
    const nonStageA = write("stage-0.4.json", { stage: "0.4", status: "PASS", addable_merge_safe: [] });
    const common = {
      document_universe_manifest_ref: documentUniverseRef,
      coverage_discovery_ref: coverageRef,
      independent_completeness_ref: completenessRef,
      base_full_blob_sha: baseFullBlobSha,
    };
    const run = {
      ...common,
      operations: { insert: [{ stage_artifacts: [malformedStageA] }], update: [], related_add: [] },
    };
    let stageABlocked = false;
    try { validateRun(run, root); } catch (error) { stageABlocked = error instanceof ValidationError && error.code === "BLOCKED_STAGE_A_V4_CONTRACT"; }
    if (!stageABlocked) throw new Error("self-test failed to reject malformed Stage A artifact");

    let missingStageABlocked = false;
    try {
      validateRun({ ...common, operations: { insert: [{ stage_artifacts: [nonStageA] }], update: [], related_add: [] } }, root);
    } catch (error) {
      missingStageABlocked = error instanceof ValidationError && error.code === "BLOCKED_OPERATION_STAGE_A_MISSING";
    }
    if (!missingStageABlocked) throw new Error("self-test failed to require Stage A per operation");

    const badCoverage = readJson(join(root, coverageRef), "test coverage");
    badCoverage.original_input_accounted = false;
    writeFileSync(join(root, coverageRef), `${JSON.stringify(badCoverage, null, 2)}\n`);
    let coverageBlocked = false;
    try { validateRun({ ...common, operations: { insert: [], update: [], related_add: [] } }, root); }
    catch (error) { coverageBlocked = error instanceof ValidationError && error.code === "BLOCKED_COVERAGE_ENVELOPE"; }
    if (!coverageBlocked) throw new Error("self-test failed to reject incomplete 0.0C envelope");

    const goodCoverage = { ...badCoverage, original_input_accounted: true };
    writeFileSync(join(root, coverageRef), `${JSON.stringify(goodCoverage, null, 2)}\n`);
    const badCompleteness = readJson(join(root, completenessRef), "test completeness");
    badCompleteness.source_universe_accounted = false;
    writeFileSync(join(root, completenessRef), `${JSON.stringify(badCompleteness, null, 2)}\n`);
    let completenessBlocked = false;
    try { validateRun({ ...common, operations: { insert: [], update: [], related_add: [] } }, root); }
    catch (error) { completenessBlocked = error instanceof ValidationError && error.code === "BLOCKED_COMPLETENESS_ENVELOPE"; }
    if (!completenessBlocked) throw new Error("self-test failed to reject incomplete 0.7C envelope");
    console.log("PASS: formal V4 card-run hardening rejects invalid coverage/completeness and requires authoritative Stage A per operation");
  } finally {
    rmSync(root, { recursive: true, force: true });
  }
}

const args = process.argv.slice(2);
try {
  if (args.includes("--self-test")) { selfTest(); process.exit(0); }
  const index = args.indexOf("--run");
  const runPath = index >= 0 ? args[index + 1] : null;
  if (!runPath) fail("INVALID_ARGUMENT", "--run PATH required");
  const result = validateRun(readJson(resolve(runPath), "card run"), ".");
  console.log(JSON.stringify({ status: "PASS", ...result }, null, 2));
  console.log(`PASS: formal V4 hardening; Stage A artifacts validated=${result.stage_a_artifacts_validated}; operations=${result.operations_with_stage_a}`);
} catch (error) {
  if (error instanceof ValidationError) { console.error(`FAIL [${error.code}]: ${error.message}`); process.exit(1); }
  throw error;
}
