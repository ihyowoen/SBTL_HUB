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
import { createHash } from "node:crypto";
import { tmpdir } from "node:os";
import { dirname, join, resolve, sep } from "node:path";

class ValidationError extends Error {
  constructor(code, message) {
    super(message);
    this.code = code;
  }
}

const fail = (code, message) => {
  throw new ValidationError(code, message);
};

const PASSING_STAGE_STATUSES = new Set([
  "PASS",
  "PASSED",
  "PASS_WITH_DECLARED_RESIDUAL_RISK",
  "PASS_WITH_NOTES",
  "PASS_WITH_WARNINGS",
  "VERIFIED",
  "ACCEPTED_FACT_SAFE",
  "ACCEPTED_FACT_SAFE_AFTER_CONTROLLED_RESCUE",
  "ADDABLE_MERGE_SAFE",
  "EVIDENCE_COMPLETE",
  "SOURCE_CLAIM_COVERED",
  "EVIDENCE_COMPLETE_AND_SOURCE_CLAIM_COVERED",
  "CONTENT_ENRICHED",
  "LANGUAGE_TERMINOLOGY_POLISHED",
  "CONTENT_ENRICHED_AND_LANGUAGE_TERMINOLOGY_POLISHED",
  "PUBLISH_READY",
  "GITHUB_MERGE_READY",
]);

const RFC3339_DATE_TIME = /^(\d{4})-(\d{2})-(\d{2})T(\d{2}):(\d{2}):(\d{2})(?:\.(\d+))?(Z|[+-]\d{2}:\d{2})$/;
const normalizeStatus = (value) => String(value).trim().toUpperCase();

const readJson = (path, label, code = "BLOCKED_STAGE_ARTIFACT_INVALID") => {
  let raw;
  try {
    raw = readFileSync(path, "utf8").replace(/^\uFEFF/, "");
  } catch (error) {
    fail(code, `${label}: 읽기 실패 — ${path}: ${error.message}`);
  }
  try {
    return JSON.parse(raw);
  } catch (error) {
    fail(code, `${label}: JSON 파싱 실패 — ${path}: ${error.message}`);
  }
};

const resolveRepoJson = (
  root,
  reference,
  label,
  code = "BLOCKED_STAGE_ARTIFACT_INVALID",
) => {
  if (typeof reference !== "string" || !reference.trim()) {
    fail(code, `${label}: 빈 reference`);
  }
  if (!reference.toLowerCase().endsWith(".json")) {
    fail(code, `${label}: JSON artifact여야 함 — ${reference}`);
  }
  const absoluteRoot = resolve(root);
  const absolute = resolve(absoluteRoot, reference);
  if (absolute !== absoluteRoot && !absolute.startsWith(`${absoluteRoot}${sep}`)) {
    fail(code, `${label}: repository 밖 경로 — ${reference}`);
  }
  if (!existsSync(absolute)) {
    fail(code, `${label}: 파일 없음 — ${reference}`);
  }
  const stat = statSync(absolute);
  if (!stat.isFile() || stat.size <= 0) {
    fail(code, `${label}: 비어 있거나 파일이 아님 — ${reference}`);
  }
  return absolute;
};

const extractStatus = (payload, label, reference) => {
  if (!payload || typeof payload !== "object" || Array.isArray(payload)) {
    fail("BLOCKED_STAGE_ARTIFACT_INVALID", `${label}: 최상위 JSON 객체 필요 — ${reference}`);
  }
  const marker = payload.status
    ?? payload.artifact_status
    ?? payload.validation_status
    ?? payload.state
    ?? payload.result;
  if (typeof marker !== "string" || !marker.trim()) {
    fail(
      "BLOCKED_STAGE_ARTIFACT_STATUS_MISSING",
      `${label}: status/artifact_status/validation_status/state/result 중 명시적 통과 상태 필요 — ${reference}`,
    );
  }
  return marker;
};

const requirePassingStatus = (payload, label, reference) => {
  const rawStatus = extractStatus(payload, label, reference);
  const normalized = normalizeStatus(rawStatus);
  if (!PASSING_STAGE_STATUSES.has(normalized)) {
    fail(
      "BLOCKED_STAGE_ARTIFACT_NOT_PASSING",
      `${label}: 허용된 통과 상태가 아님 — ${rawStatus} (${reference})`,
    );
  }
  return { rawStatus, normalized };
};

const validateStageArtifact = (root, reference, label) => {
  const absolute = resolveRepoJson(root, reference, label);
  const payload = readJson(absolute, label);
  const { rawStatus, normalized } = requirePassingStatus(payload, label, reference);
  return { reference, status: rawStatus, normalized_status: normalized };
};

const stableCanonicalize = (value) => {
  if (Array.isArray(value)) return value.map(stableCanonicalize);
  if (!value || typeof value !== "object") return value;
  return Object.fromEntries(
    Object.keys(value).sort().map((key) => [key, stableCanonicalize(value[key])]),
  );
};

const operationsSha256 = (operations) => createHash("sha256")
  .update(JSON.stringify(stableCanonicalize(operations)))
  .digest("hex");

const validateRfc3339DateTime = (value) => {
  if (typeof value !== "string") {
    fail("BLOCKED_OUTPUT_UPDATED_INVALID", "output_updated는 RFC 3339 date-time 문자열이어야 함");
  }
  const match = RFC3339_DATE_TIME.exec(value);
  if (!match) {
    fail("BLOCKED_OUTPUT_UPDATED_INVALID", `output_updated가 RFC 3339 date-time이 아님 — ${value}`);
  }
  const [, yearText, monthText, dayText, hourText, minuteText, secondText, , zone] = match;
  const year = Number(yearText);
  const month = Number(monthText);
  const day = Number(dayText);
  const hour = Number(hourText);
  const minute = Number(minuteText);
  const second = Number(secondText);
  const maxDay = new Date(Date.UTC(year, month, 0)).getUTCDate();
  if (month < 1 || month > 12 || day < 1 || day > maxDay
    || hour > 23 || minute > 59 || second > 59) {
    fail("BLOCKED_OUTPUT_UPDATED_INVALID", `output_updated 날짜·시간 범위 오류 — ${value}`);
  }
  if (zone !== "Z") {
    const offsetHour = Number(zone.slice(1, 3));
    const offsetMinute = Number(zone.slice(4, 6));
    if (offsetHour > 23 || offsetMinute > 59) {
      fail("BLOCKED_OUTPUT_UPDATED_INVALID", `output_updated timezone offset 오류 — ${value}`);
    }
  }
  if (Number.isNaN(Date.parse(value))) {
    fail("BLOCKED_OUTPUT_UPDATED_INVALID", `output_updated 파싱 실패 — ${value}`);
  }
};

const validateCompletenessBinding = (run, root) => {
  const label = "Stage 0.7C independent completeness";
  const reference = run.independent_completeness_ref;
  const absolute = resolveRepoJson(
    root,
    reference,
    label,
    "BLOCKED_COMPLETENESS_ARTIFACT_INVALID",
  );
  const payload = readJson(absolute, label, "BLOCKED_COMPLETENESS_ARTIFACT_INVALID");
  if (!payload || typeof payload !== "object" || Array.isArray(payload)) {
    fail("BLOCKED_COMPLETENESS_ARTIFACT_INVALID", `${label}: 최상위 JSON 객체 필요 — ${reference}`);
  }
  if (payload.stage !== "0.7C") {
    fail("BLOCKED_COMPLETENESS_ARTIFACT_INVALID", `${label}.stage는 0.7C여야 함`);
  }
  requirePassingStatus(payload, label, reference);

  const expectedBindings = {
    run_id: run.run_id,
    base_main_commit_sha: run.base_main_commit_sha,
    base_full_blob_sha: run.base_full_blob_sha,
    document_universe_manifest_ref: run.document_universe_manifest_ref,
    coverage_discovery_ref: run.coverage_discovery_ref,
  };
  for (const [key, expected] of Object.entries(expectedBindings)) {
    if (payload[key] !== expected) {
      fail(
        "BLOCKED_COMPLETENESS_BINDING_MISMATCH",
        `${label}.${key} ${String(payload[key])} != ${String(expected)}`,
      );
    }
  }

  const expectedOperationsSha = operationsSha256(run.operations);
  if (payload.reviewed_operations_sha256 !== expectedOperationsSha) {
    fail(
      "BLOCKED_COMPLETENESS_OPERATIONS_MISMATCH",
      `${label}.reviewed_operations_sha256가 현재 run operations와 불일치`,
    );
  }
  return {
    reference,
    run_id: payload.run_id,
    reviewed_operations_sha256: expectedOperationsSha,
  };
};

const validateRunReferences = (run, root = ".") => {
  if (!run || typeof run !== "object" || Array.isArray(run)) {
    fail("INVALID_RUN", "card-run 최상위 객체 필요");
  }
  if (!run.operations || typeof run.operations !== "object" || Array.isArray(run.operations)) {
    fail("INVALID_RUN", "operations 객체 필요");
  }
  validateRfc3339DateTime(run.output_updated);
  const completeness = validateCompletenessBinding(run, root);

  const validated = [];
  for (const kind of ["insert", "update", "related_add"]) {
    const operations = run.operations[kind];
    if (!Array.isArray(operations)) {
      fail("INVALID_RUN", `operations.${kind} 배열 필요`);
    }
    operations.forEach((operation, operationIndex) => {
      if (!operation || typeof operation !== "object" || Array.isArray(operation)) {
        fail("INVALID_RUN", `${kind}[${operationIndex}] 객체 필요`);
      }
      if (!Array.isArray(operation.stage_artifacts) || !operation.stage_artifacts.length) {
        fail("BLOCKED_STAGE_ARTIFACT_INVALID", `${kind}[${operationIndex}].stage_artifacts가 비어 있음`);
      }
      operation.stage_artifacts.forEach((reference, referenceIndex) => {
        validated.push(validateStageArtifact(
          root,
          reference,
          `${kind}[${operationIndex}].stage_artifacts[${referenceIndex}]`,
        ));
      });
    });
  }
  return { validated, completeness };
};

const runSelfTest = () => {
  const root = mkdtempSync(join(tmpdir(), "card-run-stage-status-"));
  try {
    mkdirSync(join(root, "artifacts"), { recursive: true });
    const write = (name, payload) => {
      const path = join(root, "artifacts", name);
      mkdirSync(dirname(path), { recursive: true });
      writeFileSync(path, `${JSON.stringify(payload, null, 2)}\n`);
      return `artifacts/${name}`;
    };

    const pass = write("pass.json", { stage: "C", status: "PASS" });
    const accepted = write("accepted.json", { stage: "C", state: "accepted_fact_safe" });
    const hold = write("hold.json", { stage: "C", status: "HOLD" });
    const skipped = write("skipped.json", { stage: "C", status: "SKIPPED" });
    const missing = write("missing.json", { stage: "C" });

    const makeRun = (reference = pass) => {
      const run = {
        run_id: "test-run",
        base_main_commit_sha: "a".repeat(40),
        base_full_blob_sha: "b".repeat(40),
        output_updated: "2026-08-02T12:00:00+09:00",
        document_universe_manifest_ref: "artifacts/stage-0.0d.json",
        coverage_discovery_ref: "artifacts/stage-0.0c.json",
        independent_completeness_ref: "artifacts/stage-0.7c.json",
        operations: {
          insert: [{ stage_artifacts: [reference] }],
          update: [],
          related_add: [],
        },
      };
      write("stage-0.7c.json", {
        stage: "0.7C",
        status: "PASS_WITH_DECLARED_RESIDUAL_RISK",
        run_id: run.run_id,
        base_main_commit_sha: run.base_main_commit_sha,
        base_full_blob_sha: run.base_full_blob_sha,
        document_universe_manifest_ref: run.document_universe_manifest_ref,
        coverage_discovery_ref: run.coverage_discovery_ref,
        reviewed_operations_sha256: operationsSha256(run.operations),
      });
      return run;
    };

    validateRunReferences(makeRun(pass), root);
    validateRunReferences(makeRun(accepted), root);

    for (const [reference, expected] of [
      [hold, "BLOCKED_STAGE_ARTIFACT_NOT_PASSING"],
      [skipped, "BLOCKED_STAGE_ARTIFACT_NOT_PASSING"],
      [missing, "BLOCKED_STAGE_ARTIFACT_STATUS_MISSING"],
    ]) {
      let caught = null;
      try {
        validateRunReferences(makeRun(reference), root);
      } catch (error) {
        caught = error;
      }
      if (!(caught instanceof ValidationError) || caught.code !== expected) {
        throw new Error(`${reference}: expected ${expected}, got ${caught?.code || "PASS"}`);
      }
    }

    for (const invalidDate of ["2026", "2026-08-02", "08/02/2026", "2026-02-30T00:00:00Z"]) {
      const run = makeRun(pass);
      run.output_updated = invalidDate;
      let caught = null;
      try {
        validateRunReferences(run, root);
      } catch (error) {
        caught = error;
      }
      if (!(caught instanceof ValidationError) || caught.code !== "BLOCKED_OUTPUT_UPDATED_INVALID") {
        throw new Error(`${invalidDate}: expected BLOCKED_OUTPUT_UPDATED_INVALID, got ${caught?.code || "PASS"}`);
      }
    }

    {
      const run = makeRun(pass);
      const path = join(root, run.independent_completeness_ref);
      const artifact = readJson(path, "test completeness");
      artifact.run_id = "another-run";
      writeFileSync(path, `${JSON.stringify(artifact, null, 2)}\n`);
      let caught = null;
      try {
        validateRunReferences(run, root);
      } catch (error) {
        caught = error;
      }
      if (!(caught instanceof ValidationError) || caught.code !== "BLOCKED_COMPLETENESS_BINDING_MISMATCH") {
        throw new Error(`stale completeness run: expected binding mismatch, got ${caught?.code || "PASS"}`);
      }
    }

    {
      const run = makeRun(pass);
      const path = join(root, run.independent_completeness_ref);
      const artifact = readJson(path, "test completeness");
      artifact.reviewed_operations_sha256 = "0".repeat(64);
      writeFileSync(path, `${JSON.stringify(artifact, null, 2)}\n`);
      let caught = null;
      try {
        validateRunReferences(run, root);
      } catch (error) {
        caught = error;
      }
      if (!(caught instanceof ValidationError) || caught.code !== "BLOCKED_COMPLETENESS_OPERATIONS_MISMATCH") {
        throw new Error(`stale completeness operations: expected operations mismatch, got ${caught?.code || "PASS"}`);
      }
    }

    console.log(
      "PASS: validate_card_run_stage_artifacts — exact status allowlist, RFC3339 output_updated, and 0.7C run/operations binding",
    );
  } finally {
    rmSync(root, { recursive: true, force: true });
  }
};

const parseArgs = (argv) => {
  const options = { run: null, selfTest: false };
  for (let index = 0; index < argv.length; index += 1) {
    const arg = argv[index];
    if (arg === "--self-test") options.selfTest = true;
    else if (arg === "--run") {
      const value = argv[index + 1];
      if (!value || value.startsWith("--")) fail("INVALID_ARGUMENT", "--run PATH가 필요함");
      options.run = value;
      index += 1;
    } else fail("INVALID_ARGUMENT", `지원하지 않는 인자 ${arg}`);
  }
  return options;
};

try {
  const options = parseArgs(process.argv.slice(2));
  if (options.selfTest) {
    runSelfTest();
    process.exit(0);
  }
  if (!options.run) fail("INVALID_ARGUMENT", "--run PATH가 필요함");
  const run = readJson(resolve(options.run), "card run", "INVALID_RUN");
  const { validated, completeness } = validateRunReferences(run, ".");
  console.log(JSON.stringify({
    status: "PASS",
    run_path: options.run,
    output_updated: run.output_updated,
    validated_stage_artifact_count: validated.length,
    allowed_statuses: [...PASSING_STAGE_STATUSES].sort(),
    completeness_binding: completeness,
    artifacts: validated,
  }, null, 2));
  console.log(
    `PASS: ${validated.length} stage artifacts pass; Stage 0.7C is bound to ${run.run_id}; output_updated is RFC3339`,
  );
} catch (error) {
  if (error instanceof ValidationError) {
    console.error(`FAIL [${error.code}]: ${error.message}`);
    process.exit(1);
  }
  throw error;
}
