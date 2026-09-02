#!/usr/bin/env node
import { mkdtempSync, mkdirSync, readFileSync, rmSync, writeFileSync } from "node:fs";
import { spawnSync } from "node:child_process";
import { tmpdir } from "node:os";
import { join, resolve } from "node:path";

class ValidationError extends Error {
  constructor(code, message) {
    super(message);
    this.code = code;
  }
}
const fail = (code, message) => { throw new ValidationError(code, message); };

const run = (command, args, options = {}) => {
  const result = spawnSync(command, args, { text: true, encoding: "utf8", ...options });
  if (result.error) fail("BLOCKED_MANUAL_DIRECT_ADD_HISTORY", `${command} launch failed: ${result.error.message}`);
  return result;
};

const git = (root, args, { allowFailure = false } = {}) => {
  const result = run("git", ["-C", root, ...args]);
  if (result.status !== 0 && !allowFailure) {
    fail("BLOCKED_MANUAL_DIRECT_ADD_HISTORY", `git ${args.join(" ")} failed: ${(result.stderr || result.stdout).trim()}`);
  }
  return result;
};

const parseSchemaText = (raw, label) => {
  let payload;
  try { payload = JSON.parse(raw.replace(/^\uFEFF/, "")); }
  catch (error) { fail("BLOCKED_MANUAL_DIRECT_ADD_HISTORY", `${label}: invalid JSON: ${error.message}`); }
  return typeof payload?.schema === "string" ? payload.schema : "";
};

const schemaAt = (root, ref, path) => {
  const exists = git(root, ["cat-file", "-e", `${ref}:${path}`], { allowFailure: true });
  if (exists.status !== 0) return null;
  const shown = git(root, ["show", `${ref}:${path}`]);
  return parseSchemaText(shown.stdout, `${ref}:${path}`);
};

const currentSchema = (root, path) => {
  try { return parseSchemaText(readFileSync(resolve(root, path), "utf8"), path); }
  catch (error) {
    if (error instanceof ValidationError) throw error;
    fail("BLOCKED_MANUAL_DIRECT_ADD_HISTORY", `${path}: read failed: ${error.message}`);
  }
};

const changedRows = (root, range) => {
  const result = git(root, [
    "diff", "-M", "--diff-filter=ACMRD", "--name-status", range, "--", ":(glob)direct-adds/**/direct-add.json",
  ]);
  return result.stdout.split(/\r?\n/).filter(Boolean).map((line) => {
    const fields = line.split("\t");
    const status = fields[0];
    if (status.startsWith("R")) {
      if (fields.length < 3) fail("BLOCKED_MANUAL_DIRECT_ADD_HISTORY", `malformed rename row: ${line}`);
      return { status, basePath: fields[1], currentPath: fields[2] };
    }
    if (fields.length < 2) fail("BLOCKED_MANUAL_DIRECT_ADD_HISTORY", `malformed diff row: ${line}`);
    return { status, basePath: fields[1], currentPath: status.startsWith("D") ? null : fields[1] };
  });
};

const classify = (root, base, range) => changedRows(root, range).map((row) => {
  const baseSchema = schemaAt(root, base, row.basePath);
  const current = row.currentPath ? currentSchema(root, row.currentPath) : null;
  const historicalV1 = baseSchema === "manual_direct_add_v1"
    && (row.currentPath === null || current === "manual_direct_add_v1");
  const downgradeToV1 = current === "manual_direct_add_v1" && baseSchema !== "manual_direct_add_v1";
  return { ...row, baseSchema, currentSchema: current, historicalV1, downgradeToV1 };
});

const requireSingleHistorical = (rows) => {
  if (rows.length !== 1 || !rows[0].historicalV1 || rows[0].downgradeToV1) {
    fail("BLOCKED_MANUAL_DIRECT_ADD_HISTORY", "audit-only exception requires exactly one already-V1 base manifest that remains V1 or is deleted");
  }
};

const validateChanged = (root, rows, schemaPath, validatorPath) => {
  let historical = 0;
  let validated = 0;
  for (const row of rows) {
    if (row.downgradeToV1) {
      fail("BLOCKED_MANUAL_DIRECT_ADD_HISTORY", `cannot downgrade non-V1 base manifest to retired V1: ${row.basePath} -> ${row.currentPath}`);
    }
    if (row.historicalV1) {
      historical += 1;
      continue;
    }
    if (row.currentPath === null) {
      fail("BLOCKED_MANUAL_DIRECT_ADD_HISTORY", `only historical V1 manifests may be deleted: ${row.basePath}`);
    }
    if (row.currentSchema !== "manual_direct_add_v2") {
      fail("BLOCKED_MANUAL_DIRECT_ADD_HISTORY", `unsupported direct-add schema '${row.currentSchema}' in ${row.currentPath}`);
    }
    const result = run(process.execPath, [validatorPath, "--schema", schemaPath, "--instance", row.currentPath], { cwd: root });
    if (result.stdout) process.stdout.write(result.stdout);
    if (result.stderr) process.stderr.write(result.stderr);
    if (result.status !== 0) process.exit(result.status ?? 1);
    validated += 1;
  }
  return { historical, validated };
};

const parseArgs = (argv) => {
  const options = {
    root: ".", base: null, range: null, auditOnly: false, validateChanged: false,
    schema: "schemas/manual-direct-add.v2.schema.json",
    validator: "scripts/validate_json_schema_subset.mjs",
    selfTest: false,
  };
  for (let index = 0; index < argv.length; index += 1) {
    const arg = argv[index];
    if (arg === "--audit-only") options.auditOnly = true;
    else if (arg === "--validate-changed") options.validateChanged = true;
    else if (arg === "--self-test") options.selfTest = true;
    else if (["--root", "--base", "--range", "--schema", "--validator"].includes(arg)) {
      const value = argv[index + 1];
      if (!value || value.startsWith("--")) fail("INVALID_ARGUMENT", `${arg} VALUE required`);
      options[arg.slice(2).replace(/-([a-z])/g, (_, c) => c.toUpperCase())] = value;
      index += 1;
    } else fail("INVALID_ARGUMENT", `unsupported argument ${arg}`);
  }
  return options;
};

const commitAll = (root, message) => {
  git(root, ["add", "."]);
  git(root, ["commit", "-m", message]);
};

const runSelfTest = () => {
  const root = mkdtempSync(join(tmpdir(), "manual-direct-add-v1-history-"));
  try {
    git(root, ["init"]);
    git(root, ["config", "user.email", "selftest@example.com"]);
    git(root, ["config", "user.name", "selftest"]);
    mkdirSync(join(root, "direct-adds/old"), { recursive: true });
    writeFileSync(join(root, "direct-adds/old/direct-add.json"), '{"schema":"manual_direct_add_v1"}\n');
    commitAll(root, "base v1");
    const base = git(root, ["rev-parse", "HEAD"]).stdout.trim();
    mkdirSync(join(root, "direct-adds/new"), { recursive: true });
    git(root, ["mv", "direct-adds/old/direct-add.json", "direct-adds/new/direct-add.json"]);
    const rows = classify(root, base, `${base}...HEAD`);
    // Three-dot against an uncommitted worktree does not include the move; commit it first.
    commitAll(root, "rename v1");
    const renamed = classify(root, base, `${base}...HEAD`);
    requireSingleHistorical(renamed);
    if (renamed[0].basePath !== "direct-adds/old/direct-add.json" || renamed[0].currentPath !== "direct-adds/new/direct-add.json") {
      throw new Error("rename did not preserve old base path and new current path");
    }

    const root2 = mkdtempSync(join(tmpdir(), "manual-direct-add-v1-downgrade-"));
    try {
      git(root2, ["init"]);
      git(root2, ["config", "user.email", "selftest@example.com"]);
      git(root2, ["config", "user.name", "selftest"]);
      mkdirSync(join(root2, "direct-adds/v2"), { recursive: true });
      writeFileSync(join(root2, "direct-adds/v2/direct-add.json"), '{"schema":"manual_direct_add_v2"}\n');
      commitAll(root2, "base v2");
      const base2 = git(root2, ["rev-parse", "HEAD"]).stdout.trim();
      writeFileSync(join(root2, "direct-adds/v2/direct-add.json"), '{"schema":"manual_direct_add_v1"}\n');
      commitAll(root2, "bad downgrade");
      const downgraded = classify(root2, base2, `${base2}...HEAD`);
      let caught = null;
      try { requireSingleHistorical(downgraded); } catch (error) { caught = error; }
      if (!(caught instanceof ValidationError)) throw new Error("V2 -> V1 downgrade unexpectedly grandfathered");
    } finally {
      rmSync(root2, { recursive: true, force: true });
    }

    console.log("PASS: historical direct-add V1 classification preserves rename/delete base identity, rejects V2-to-V1 downgrade, and centralizes grandfathering");
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
  if (!options.base || !options.range) fail("INVALID_ARGUMENT", "--base REF and --range RANGE required");
  if (options.auditOnly === options.validateChanged) fail("INVALID_ARGUMENT", "choose exactly one of --audit-only or --validate-changed");
  const root = resolve(options.root);
  const rows = classify(root, options.base, options.range);
  if (options.auditOnly) {
    requireSingleHistorical(rows);
    console.log(JSON.stringify({ status: "PASS", historical_audit_only: true, row: rows[0] }));
  } else {
    const result = validateChanged(root, rows, options.schema, options.validator);
    console.log(`PASS: validated ${result.validated} V2 manifest(s); preserved/deleted ${result.historical} historical V1 audit manifest(s)`);
  }
} catch (error) {
  if (error instanceof ValidationError) {
    console.error(`FAIL [${error.code}]: ${error.message}`);
    process.exit(1);
  }
  console.error(`FAIL [BLOCKED_MANUAL_DIRECT_ADD_HISTORY_INTERNAL]: ${error.message}`);
  process.exit(1);
}
