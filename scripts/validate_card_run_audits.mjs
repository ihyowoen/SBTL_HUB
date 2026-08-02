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

const PASSING_AUDIT_STATUSES = new Set([
  "PASS",
  "PASSED",
  "PASS_WITH_DECLARED_RESIDUAL_RISK",
  "PASS_WITH_NOTES",
  "PASS_WITH_WARNINGS",
  "VERIFIED",
  "GITHUB_MERGE_READY",
]);
const STATUS_FIELDS = ["status", "artifact_status", "validation_status", "state", "result"];
const SHA1 = /^[0-9a-f]{40}$/;
const SHA256 = /^[0-9a-f]{64}$/;

const normalizeStatus = (value) => String(value).trim().toUpperCase();
const sha256 = (bytes) => createHash("sha256").update(bytes).digest("hex");

const stableCanonicalize = (value) => {
  if (Array.isArray(value)) return value.map(stableCanonicalize);
  if (!value || typeof value !== "object") return value;
  return Object.fromEntries(
    Object.keys(value).sort().map((key) => [key, stableCanonicalize(value[key])]),
  );
};

const operationsSha256 = (operations) => sha256(
  Buffer.from(JSON.stringify(stableCanonicalize(operations))),
);

const readJson = (path, label, code = "BLOCKED_RUN_AUDIT_INVALID") => {
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

const resolveRepoFile = (root, reference, label, { jsonOnly = false } = {}) => {
  if (typeof reference !== "string" || !reference.trim()) {
    fail("BLOCKED_RUN_AUDIT_INVALID", `${label}: 빈 reference`);
  }
  if (jsonOnly && !reference.toLowerCase().endsWith(".json")) {
    fail("BLOCKED_RUN_AUDIT_INVALID", `${label}: JSON audit artifact여야 함 — ${reference}`);
  }
  const absoluteRoot = resolve(root);
  const absolute = resolve(absoluteRoot, reference);
  if (absolute !== absoluteRoot && !absolute.startsWith(`${absoluteRoot}${sep}`)) {
    fail("BLOCKED_RUN_AUDIT_INVALID", `${label}: repository 밖 경로 — ${reference}`);
  }
  if (!existsSync(absolute)) {
    fail("BLOCKED_RUN_AUDIT_INVALID", `${label}: 파일 없음 — ${reference}`);
  }
  const stat = statSync(absolute);
  if (!stat.isFile() || stat.size <= 0) {
    fail("BLOCKED_RUN_AUDIT_INVALID", `${label}: 비어 있거나 파일이 아님 — ${reference}`);
  }
  return absolute;
};

const validateAllStatusMarkers = (payload, label, reference) => {
  const markers = [];
  for (const field of STATUS_FIELDS) {
    if (!Object.hasOwn(payload, field) || payload[field] === null || payload[field] === undefined) continue;
    if (typeof payload[field] !== "string" || !payload[field].trim()) {
      fail("BLOCKED_RUN_AUDIT_STATUS_INVALID", `${label}.${field}: 비어 있지 않은 문자열 필요`);
    }
    const normalized = normalizeStatus(payload[field]);
    markers.push({ field, raw: payload[field], normalized });
    if (!PASSING_AUDIT_STATUSES.has(normalized)) {
      fail(
        "BLOCKED_RUN_AUDIT_NOT_PASSING",
        `${label}.${field}: 비통과 audit 상태 ${payload[field]} — ${reference}`,
      );
    }
  }
  if (!markers.length) {
    fail(
      "BLOCKED_RUN_AUDIT_STATUS_MISSING",
      `${label}: ${STATUS_FIELDS.join("/")} 중 명시적 통과 상태 필요 — ${reference}`,
    );
  }
  return markers;
};

const assertObject = (value, label) => {
  if (!value || typeof value !== "object" || Array.isArray(value)) {
    fail("BLOCKED_RUN_AUDIT_INVALID", `${label}: 객체 필요`);
  }
};

const assertStringArray = (value, label) => {
  if (!Array.isArray(value) || value.some((entry) => typeof entry !== "string" || !entry.trim())) {
    fail("BLOCKED_RUN_AUDIT_INVALID", `${label}: 문자열 배열 필요`);
  }
  if (new Set(value).size !== value.length) {
    fail("BLOCKED_RUN_AUDIT_INVALID", `${label}: 중복 값 존재`);
  }
};

const sorted = (values) => [...values].sort();
const sameStringSet = (left, right) => JSON.stringify(sorted(left)) === JSON.stringify(sorted(right));

const declaredRelationKeys = (operations) => operations.related_add.map((operation) =>
  `${operation.direction}:${operation.source_id}->${operation.target_id}`);

const auditRelationKeys = (entries, label) => {
  if (!Array.isArray(entries)) {
    fail("BLOCKED_RUN_AUDIT_INVALID", `${label}: 배열 필요`);
  }
  const keys = entries.map((entry, index) => {
    assertObject(entry, `${label}[${index}]`);
    for (const field of ["source_id", "target_id", "direction"]) {
      if (typeof entry[field] !== "string" || !entry[field].trim()) {
        fail("BLOCKED_RUN_AUDIT_INVALID", `${label}[${index}].${field} 누락`);
      }
    }
    if (!["directional", "reciprocal"].includes(entry.direction)) {
      fail("BLOCKED_RUN_AUDIT_INVALID", `${label}[${index}].direction 오류`);
    }
    return `${entry.direction}:${entry.source_id}->${entry.target_id}`;
  });
  if (new Set(keys).size !== keys.length) {
    fail("BLOCKED_RUN_AUDIT_INVALID", `${label}: 중복 relation 존재`);
  }
  return keys;
};

const requireEqual = (actual, expected, label, code = "BLOCKED_RUN_AUDIT_BINDING_MISMATCH") => {
  if (actual !== expected) {
    fail(code, `${label}: ${String(actual)} != ${String(expected)}`);
  }
};

const validateAudit = (run, reference, index, root, fullPath, leanPath) => {
  const label = `audit_refs[${index}]`;
  const absolute = resolveRepoFile(root, reference, label, { jsonOnly: true });
  const payload = readJson(absolute, label);
  assertObject(payload, label);
  const markers = validateAllStatusMarkers(payload, label, reference);

  requireEqual(payload.schema, "card_run_audit_v1", `${label}.schema`, "BLOCKED_RUN_AUDIT_INVALID");
  requireEqual(payload.audit_complete, true, `${label}.audit_complete`, "BLOCKED_RUN_AUDIT_NOT_PASSING");
  requireEqual(
    payload.reviewer_independence,
    "SEPARATE_PASS",
    `${label}.reviewer_independence`,
    "BLOCKED_RUN_AUDIT_NOT_PASSING",
  );
  requireEqual(payload.zero_deletion_assertion, true, `${label}.zero_deletion_assertion`);
  requireEqual(payload.zero_related_remove_assertion, true, `${label}.zero_related_remove_assertion`);

  const expectedBindings = {
    run_id: run.run_id,
    base_main_commit_sha: run.base_main_commit_sha,
    base_full_blob_sha: run.base_full_blob_sha,
    document_universe_manifest_ref: run.document_universe_manifest_ref,
    coverage_discovery_ref: run.coverage_discovery_ref,
    independent_completeness_ref: run.independent_completeness_ref,
    expected_before: run.expected_before,
    expected_after: run.expected_after,
  };
  for (const [field, expected] of Object.entries(expectedBindings)) {
    requireEqual(payload[field], expected, `${label}.${field}`);
  }

  if (!SHA1.test(payload.base_main_commit_sha) || !SHA1.test(payload.base_full_blob_sha)) {
    fail("BLOCKED_RUN_AUDIT_INVALID", `${label}: baseline SHA 형식 오류`);
  }

  const expectedOperationsSha = operationsSha256(run.operations);
  requireEqual(
    payload.reviewed_operations_sha256,
    expectedOperationsSha,
    `${label}.reviewed_operations_sha256`,
    "BLOCKED_RUN_AUDIT_OPERATIONS_MISMATCH",
  );

  const expectedInsertedIds = run.operations.insert.map((operation) => operation.card.id);
  const expectedUpdatedIds = run.operations.update.map((operation) => operation.id);
  assertStringArray(payload.inserted_ids, `${label}.inserted_ids`);
  assertStringArray(payload.updated_ids, `${label}.updated_ids`);
  if (!sameStringSet(payload.inserted_ids, expectedInsertedIds)) {
    fail("BLOCKED_RUN_AUDIT_OPERATIONS_MISMATCH", `${label}.inserted_ids가 run insert와 불일치`);
  }
  if (!sameStringSet(payload.updated_ids, expectedUpdatedIds)) {
    fail("BLOCKED_RUN_AUDIT_OPERATIONS_MISMATCH", `${label}.updated_ids가 run update와 불일치`);
  }

  const expectedRelations = declaredRelationKeys(run.operations);
  const reviewedRelations = auditRelationKeys(payload.related_additions, `${label}.related_additions`);
  if (!sameStringSet(reviewedRelations, expectedRelations)) {
    fail("BLOCKED_RUN_AUDIT_OPERATIONS_MISMATCH", `${label}.related_additions가 run related_add와 불일치`);
  }

  if (typeof payload.full_output_sha256 !== "string" || !SHA256.test(payload.full_output_sha256)
    || typeof payload.lean_output_sha256 !== "string" || !SHA256.test(payload.lean_output_sha256)) {
    fail("BLOCKED_RUN_AUDIT_INVALID", `${label}: full/lean SHA-256 형식 오류`);
  }
  const actualFullSha = sha256(readFileSync(fullPath));
  const actualLeanSha = sha256(readFileSync(leanPath));
  requireEqual(
    payload.full_output_sha256,
    actualFullSha,
    `${label}.full_output_sha256`,
    "BLOCKED_RUN_AUDIT_OUTPUT_MISMATCH",
  );
  requireEqual(
    payload.lean_output_sha256,
    actualLeanSha,
    `${label}.lean_output_sha256`,
    "BLOCKED_RUN_AUDIT_OUTPUT_MISMATCH",
  );

  return {
    reference,
    markers,
    reviewed_operations_sha256: expectedOperationsSha,
    full_output_sha256: actualFullSha,
    lean_output_sha256: actualLeanSha,
  };
};

const validateRunAudits = (run, root = ".", fullReference = "data/cards.full.json", leanReference = "public/data/cards.json") => {
  assertObject(run, "card run");
  assertObject(run.operations, "card run.operations");
  for (const kind of ["insert", "update", "related_add"]) {
    if (!Array.isArray(run.operations[kind])) {
      fail("INVALID_RUN", `operations.${kind} 배열 필요`);
    }
  }
  if (!Array.isArray(run.audit_refs) || !run.audit_refs.length) {
    fail("BLOCKED_RUN_AUDIT_MISSING", "audit_refs는 비어 있지 않은 배열이어야 함");
  }
  const fullPath = resolveRepoFile(root, fullReference, "canonical full");
  const leanPath = resolveRepoFile(root, leanReference, "lean projection");
  return run.audit_refs.map((reference, index) =>
    validateAudit(run, reference, index, root, fullPath, leanPath));
};

const runSelfTest = () => {
  const root = mkdtempSync(join(tmpdir(), "card-run-audit-validation-"));
  try {
    mkdirSync(join(root, "runs"), { recursive: true });
    mkdirSync(join(root, "data"), { recursive: true });
    mkdirSync(join(root, "public/data"), { recursive: true });
    writeFileSync(join(root, "data/cards.full.json"), '{"cards":[{"id":"A"}]}\n');
    writeFileSync(join(root, "public/data/cards.json"), '[{"id":"A"}]\n');

    const run = {
      run_id: "audit-self-test",
      base_main_commit_sha: "a".repeat(40),
      base_full_blob_sha: "b".repeat(40),
      expected_before: 1,
      expected_after: 2,
      document_universe_manifest_ref: "runs/0.0d.json",
      coverage_discovery_ref: "runs/0.0c.json",
      independent_completeness_ref: "runs/0.7c.json",
      operations: {
        insert: [{ card: { id: "B" } }],
        update: [{ id: "A" }],
        related_add: [{ source_id: "A", target_id: "B", direction: "directional" }],
      },
      audit_refs: ["runs/audit.json"],
    };

    const makeAudit = () => ({
      schema: "card_run_audit_v1",
      status: "PASS",
      audit_complete: true,
      reviewer_independence: "SEPARATE_PASS",
      run_id: run.run_id,
      base_main_commit_sha: run.base_main_commit_sha,
      base_full_blob_sha: run.base_full_blob_sha,
      document_universe_manifest_ref: run.document_universe_manifest_ref,
      coverage_discovery_ref: run.coverage_discovery_ref,
      independent_completeness_ref: run.independent_completeness_ref,
      reviewed_operations_sha256: operationsSha256(run.operations),
      expected_before: run.expected_before,
      expected_after: run.expected_after,
      inserted_ids: ["B"],
      updated_ids: ["A"],
      related_additions: [{ source_id: "A", target_id: "B", direction: "directional" }],
      zero_deletion_assertion: true,
      zero_related_remove_assertion: true,
      full_output_sha256: sha256(readFileSync(join(root, "data/cards.full.json"))),
      lean_output_sha256: sha256(readFileSync(join(root, "public/data/cards.json"))),
    });

    const writeAudit = (payload) => {
      const path = join(root, "runs/audit.json");
      mkdirSync(dirname(path), { recursive: true });
      writeFileSync(path, `${JSON.stringify(payload, null, 2)}\n`);
    };

    writeAudit(makeAudit());
    validateRunAudits(run, root);

    const expectFailure = (mutate, expectedCode, label) => {
      const payload = makeAudit();
      mutate(payload);
      writeAudit(payload);
      let caught = null;
      try {
        validateRunAudits(run, root);
      } catch (error) {
        caught = error;
      }
      if (!(caught instanceof ValidationError) || caught.code !== expectedCode) {
        throw new Error(`${label}: expected ${expectedCode}, got ${caught?.code || "PASS"}`);
      }
    };

    expectFailure(
      (payload) => { payload.run_id = "another-run"; },
      "BLOCKED_RUN_AUDIT_BINDING_MISMATCH",
      "stale run binding",
    );
    expectFailure(
      (payload) => { payload.reviewed_operations_sha256 = "0".repeat(64); },
      "BLOCKED_RUN_AUDIT_OPERATIONS_MISMATCH",
      "stale operations binding",
    );
    expectFailure(
      (payload) => { payload.full_output_sha256 = "0".repeat(64); },
      "BLOCKED_RUN_AUDIT_OUTPUT_MISMATCH",
      "stale full output hash",
    );
    expectFailure(
      (payload) => { payload.validation_status = "FAIL"; },
      "BLOCKED_RUN_AUDIT_NOT_PASSING",
      "conflicting audit status",
    );

    console.log(
      "PASS: validate_card_run_audits — every audit is passing, independent, run-bound, operations-bound, and output-bound",
    );
  } finally {
    rmSync(root, { recursive: true, force: true });
  }
};

const parseArgs = (argv) => {
  const options = {
    run: null,
    full: "data/cards.full.json",
    lean: "public/data/cards.json",
    selfTest: false,
  };
  for (let index = 0; index < argv.length; index += 1) {
    const arg = argv[index];
    if (arg === "--self-test") options.selfTest = true;
    else if (["--run", "--full", "--lean"].includes(arg)) {
      const value = argv[index + 1];
      if (!value || value.startsWith("--")) fail("INVALID_ARGUMENT", `${arg} PATH가 필요함`);
      options[arg.slice(2)] = value;
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
  const runPath = resolveRepoFile(".", options.run, "card run", { jsonOnly: true });
  const run = readJson(runPath, "card run");
  const audits = validateRunAudits(run, ".", options.full, options.lean);
  console.log(JSON.stringify({
    status: "PASS",
    run_path: options.run,
    validated_audit_count: audits.length,
    audits,
  }, null, 2));
  console.log(`PASS: ${audits.length} independent run audits are bound to this run and submitted outputs`);
} catch (error) {
  if (error instanceof ValidationError) {
    console.error(`FAIL [${error.code}]: ${error.message}`);
    process.exit(1);
  }
  throw error;
}
