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

const normalizeStatus = (value) => String(value).trim().toUpperCase();

const readJson = (path, label) => {
  let raw;
  try {
    raw = readFileSync(path, "utf8").replace(/^\uFEFF/, "");
  } catch (error) {
    fail("BLOCKED_STAGE_ARTIFACT_INVALID", `${label}: 읽기 실패 — ${path}: ${error.message}`);
  }
  try {
    return JSON.parse(raw);
  } catch (error) {
    fail("BLOCKED_STAGE_ARTIFACT_INVALID", `${label}: JSON 파싱 실패 — ${path}: ${error.message}`);
  }
};

const resolveRepoJson = (root, reference, label) => {
  if (typeof reference !== "string" || !reference.trim()) {
    fail("BLOCKED_STAGE_ARTIFACT_INVALID", `${label}: 빈 reference`);
  }
  if (!reference.toLowerCase().endsWith(".json")) {
    fail("BLOCKED_STAGE_ARTIFACT_INVALID", `${label}: stage artifact는 JSON이어야 함 — ${reference}`);
  }
  const absoluteRoot = resolve(root);
  const absolute = resolve(absoluteRoot, reference);
  if (absolute !== absoluteRoot && !absolute.startsWith(`${absoluteRoot}${sep}`)) {
    fail("BLOCKED_STAGE_ARTIFACT_INVALID", `${label}: repository 밖 경로 — ${reference}`);
  }
  if (!existsSync(absolute)) {
    fail("BLOCKED_STAGE_ARTIFACT_INVALID", `${label}: 파일 없음 — ${reference}`);
  }
  const stat = statSync(absolute);
  if (!stat.isFile() || stat.size <= 0) {
    fail("BLOCKED_STAGE_ARTIFACT_INVALID", `${label}: 비어 있거나 파일이 아님 — ${reference}`);
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

const validateStageArtifact = (root, reference, label) => {
  const absolute = resolveRepoJson(root, reference, label);
  const payload = readJson(absolute, label);
  const rawStatus = extractStatus(payload, label, reference);
  const normalized = normalizeStatus(rawStatus);
  if (!PASSING_STAGE_STATUSES.has(normalized)) {
    fail(
      "BLOCKED_STAGE_ARTIFACT_NOT_PASSING",
      `${label}: 허용된 통과 상태가 아님 — ${rawStatus} (${reference})`,
    );
  }
  return { reference, status: rawStatus, normalized_status: normalized };
};

const validateRunReferences = (run, root = ".") => {
  if (!run || typeof run !== "object" || Array.isArray(run)) {
    fail("INVALID_RUN", "card-run 최상위 객체 필요");
  }
  if (!run.operations || typeof run.operations !== "object" || Array.isArray(run.operations)) {
    fail("INVALID_RUN", "operations 객체 필요");
  }

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
  return validated;
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

    const makeRun = (reference) => ({
      operations: {
        insert: [{ stage_artifacts: [reference] }],
        update: [],
        related_add: [],
      },
    });

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
    console.log("PASS: validate_card_run_stage_artifacts — exact pass allowlist, HOLD/SKIPPED/missing blocked");
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
  const run = readJson(resolve(options.run), "card run");
  const validated = validateRunReferences(run, ".");
  console.log(JSON.stringify({
    status: "PASS",
    run_path: options.run,
    validated_stage_artifact_count: validated.length,
    allowed_statuses: [...PASSING_STAGE_STATUSES].sort(),
    artifacts: validated,
  }, null, 2));
  console.log(`PASS: ${validated.length} per-operation stage artifacts carry explicit allowed passing status`);
} catch (error) {
  if (error instanceof ValidationError) {
    console.error(`FAIL [${error.code}]: ${error.message}`);
    process.exit(1);
  }
  throw error;
}
