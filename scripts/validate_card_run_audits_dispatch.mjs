#!/usr/bin/env node
import { createHash } from "node:crypto";
import { existsSync, mkdtempSync, mkdirSync, readFileSync, readdirSync, rmSync, writeFileSync } from "node:fs";
import { spawnSync } from "node:child_process";
import { tmpdir } from "node:os";
import { dirname, join, relative, resolve, sep } from "node:path";
import { fileURLToPath } from "node:url";

const HERE = dirname(fileURLToPath(import.meta.url));
const SELF = fileURLToPath(import.meta.url);
const AUDIT_VALIDATOR = resolve(HERE, "validate_card_run_audits.mjs");

class ValidationError extends Error {
  constructor(code, message) {
    super(message);
    this.code = code;
  }
}

const fail = (code, message) => { throw new ValidationError(code, message); };

const readJson = (path, label) => {
  try {
    return JSON.parse(readFileSync(path, "utf8").replace(/^\uFEFF/, ""));
  } catch (error) {
    fail("BLOCKED_RUN_AUDIT_INVALID", `${label}: ${error.message}`);
  }
};

const repoPath = (root, reference, label) => {
  if (typeof reference !== "string" || !reference.trim() || !reference.endsWith(".json")) {
    fail("BLOCKED_RUN_AUDIT_INVALID", `${label}: repository-relative JSON path required`);
  }
  const absoluteRoot = resolve(root);
  const absolute = resolve(absoluteRoot, reference);
  if (absolute !== absoluteRoot && !absolute.startsWith(`${absoluteRoot}${sep}`)) {
    fail("BLOCKED_RUN_AUDIT_INVALID", `${label}: repository-outside path ${reference}`);
  }
  if (!existsSync(absolute)) fail("BLOCKED_RUN_AUDIT_INVALID", `${label}: missing ${reference}`);
  return absolute;
};

const splitAuditRefs = (root, run) => {
  if (!Array.isArray(run.audit_refs) || !run.audit_refs.length) {
    fail("BLOCKED_RUN_AUDIT_MISSING", "audit_refs[] must be non-empty");
  }
  const audits = [];
  const mergePrep = [];
  run.audit_refs.forEach((reference, index) => {
    const absolute = repoPath(root, reference, `audit_refs[${index}]`);
    const payload = readJson(absolute, `audit_refs[${index}]`);
    if (payload?.stage === "0.8") mergePrep.push(reference);
    else audits.push(reference);
  });
  if (mergePrep.length !== 1) {
    fail("BLOCKED_PROMPT_0_8_ARTIFACT", `expected exactly one stage=0.8 audit artifact, found ${mergePrep.length}`);
  }
  if (!audits.length) {
    fail("BLOCKED_RUN_AUDIT_MISSING", "no card_run_audit_v1 reference remains after Prompt 0.8 dispatch");
  }
  return { audits, mergePrep: mergePrep[0] };
};

const parseArgs = (argv) => {
  const options = { run: null, full: "data/cards.full.json", lean: "public/data/cards.json", selfTest: false };
  for (let index = 0; index < argv.length; index += 1) {
    const arg = argv[index];
    if (arg === "--self-test") options.selfTest = true;
    else if (["--run", "--full", "--lean"].includes(arg)) {
      const value = argv[index + 1];
      if (!value || value.startsWith("--")) fail("INVALID_ARGUMENT", `${arg} PATH required`);
      options[arg.slice(2)] = value;
      index += 1;
    } else fail("INVALID_ARGUMENT", `unsupported argument ${arg}`);
  }
  return options;
};

const runAuditValidator = (root, runReference, fullReference, leanReference) => {
  const result = spawnSync(
    process.execPath,
    [AUDIT_VALIDATOR, "--run", runReference, "--full", fullReference, "--lean", leanReference],
    { cwd: root, text: true, encoding: "utf8" },
  );
  if (result.stdout) process.stdout.write(result.stdout);
  if (result.stderr) process.stderr.write(result.stderr);
  if (result.error) fail("BLOCKED_RUN_AUDIT_INVALID", `audit validator launch failed: ${result.error.message}`);
  return result.status ?? 1;
};

const auditOnlyLeftovers = (runDir) => (
  readdirSync(runDir).filter((name) => name.startsWith(".audit-only-") && name.endsWith(".json"))
);

const execute = (root, options) => {
  const runAbsolute = repoPath(root, options.run, "card run");
  const run = readJson(runAbsolute, "card run");
  const { audits, mergePrep } = splitAuditRefs(root, run);

  const runDir = dirname(runAbsolute);
  const tempAbsolute = join(runDir, `.audit-only-${process.pid}-${Date.now()}.json`);
  const tempReference = relative(resolve(root), tempAbsolute).replaceAll("\\", "/");
  let auditStatus = 1;
  try {
    writeFileSync(tempAbsolute, `${JSON.stringify({ ...run, audit_refs: audits }, null, 2)}\n`);
    auditStatus = runAuditValidator(root, tempReference, options.full, options.lean);
  } finally {
    rmSync(tempAbsolute, { force: true });
  }
  if (auditStatus !== 0) process.exit(auditStatus);
  return mergePrep;
};

const runSelfTest = () => {
  const root = mkdtempSync(join(tmpdir(), "card-run-audit-dispatch-"));
  try {
    mkdirSync(join(root, "runs"), { recursive: true });
    mkdirSync(join(root, "data"), { recursive: true });
    mkdirSync(join(root, "public/data"), { recursive: true });
    writeFileSync(join(root, "data/cards.full.json"), '{"cards":[{"id":"A"}]}\n');
    writeFileSync(join(root, "public/data/cards.json"), '[{"id":"A"}]\n');

    const operations = { insert: [], update: [], related_add: [] };
    const stable = (value) => {
      if (Array.isArray(value)) return value.map(stable);
      if (!value || typeof value !== "object") return value;
      return Object.fromEntries(Object.keys(value).sort().map((key) => [key, stable(value[key])]));
    };
    const hash = (bytes) => createHash("sha256").update(bytes).digest("hex");
    const operationsHash = hash(Buffer.from(JSON.stringify(stable(operations))));
    const fullHash = hash(readFileSync(join(root, "data/cards.full.json")));
    const leanHash = hash(readFileSync(join(root, "public/data/cards.json")));

    const run = {
      run_id: "dispatch-self-test",
      base_main_commit_sha: "a".repeat(40),
      base_full_blob_sha: "b".repeat(40),
      document_universe_manifest_ref: "runs/0.0d.json",
      coverage_discovery_ref: "runs/0.0c.json",
      independent_completeness_ref: "runs/0.7c.json",
      expected_before: 1,
      expected_after: 1,
      operations,
      audit_refs: ["runs/audit.json", "runs/merge-prep.json"],
    };
    const audit = {
      schema: "card_run_audit_v1",
      status: "PASS",
      validation_status: "PASS",
      audit_complete: true,
      reviewer_independence: "SEPARATE_PASS",
      run_id: run.run_id,
      base_main_commit_sha: run.base_main_commit_sha,
      base_full_blob_sha: run.base_full_blob_sha,
      document_universe_manifest_ref: run.document_universe_manifest_ref,
      coverage_discovery_ref: run.coverage_discovery_ref,
      independent_completeness_ref: run.independent_completeness_ref,
      expected_before: 1,
      expected_after: 1,
      reviewed_operations_sha256: operationsHash,
      inserted_ids: [],
      updated_ids: [],
      related_additions: [],
      zero_deletion_assertion: true,
      zero_related_remove_assertion: true,
      full_output_sha256: fullHash,
      lean_output_sha256: leanHash,
    };
    writeFileSync(join(root, "runs/run.json"), `${JSON.stringify(run)}\n`);
    writeFileSync(join(root, "runs/audit.json"), `${JSON.stringify(audit)}\n`);
    writeFileSync(join(root, "runs/merge-prep.json"), '{"stage":"0.8","status":"PASS"}\n');

    const mergePrep = execute(root, { run: "runs/run.json", full: "data/cards.full.json", lean: "public/data/cards.json" });
    if (mergePrep !== "runs/merge-prep.json") throw new Error("Prompt 0.8 ref was not dispatched");
    const originalRun = readFileSync(join(root, "runs/run.json"), "utf8");
    if (!originalRun.includes("merge-prep.json")) throw new Error("original run fixture was modified");
    const successLeftovers = auditOnlyLeftovers(join(root, "runs"));
    if (successLeftovers.length) throw new Error(`ephemeral audit-only run leaked after success: ${successLeftovers.join(", ")}`);

    const failingAudit = { ...audit };
    delete failingAudit.audit_complete;
    writeFileSync(join(root, "runs/audit.json"), `${JSON.stringify(failingAudit)}\n`);
    const failed = spawnSync(
      process.execPath,
      [SELF, "--run", "runs/run.json", "--full", "data/cards.full.json", "--lean", "public/data/cards.json"],
      { cwd: root, text: true, encoding: "utf8" },
    );
    if (failed.error) throw failed.error;
    if (failed.status === 0) throw new Error("failing audit fixture unexpectedly passed dispatch");
    const failureLeftovers = auditOnlyLeftovers(join(root, "runs"));
    if (failureLeftovers.length) throw new Error(`ephemeral audit-only run leaked after failure: ${failureLeftovers.join(", ")}`);

    console.log("PASS: card-run audit dispatch validates repository-relative audit refs and cleans ephemeral runs after both success and failure");
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
  if (!options.run) fail("INVALID_ARGUMENT", "--run PATH required");
  execute(resolve("."), options);
} catch (error) {
  if (error instanceof ValidationError) {
    console.error(`FAIL [${error.code}]: ${error.message}`);
    process.exit(1);
  }
  console.error(`FAIL [BLOCKED_RUN_AUDIT_DISPATCH_INTERNAL]: ${error.message}`);
  process.exit(1);
}
