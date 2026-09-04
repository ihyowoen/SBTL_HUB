#!/usr/bin/env node
import { createHash } from "node:crypto";
import { readFileSync, writeFileSync } from "node:fs";
import { resolve } from "node:path";
import { spawnSync } from "node:child_process";
import { pathToFileURL } from "node:url";

export const GOVERNANCE_LOCK_SCHEMA = "governance_lock_v1";
export const REGISTRY_PATH = "docs/llm_prompts/v1/GOVERNANCE_LIFECYCLE_REGISTRY.json";
const STAGE_A_PATH = "docs/llm_prompts/v1/01_PROMPT_0_1_Stage_A.md";
const HEX40 = /^[0-9a-f]{40}$/;
const HEX64 = /^[0-9a-f]{64}$/;

class GovernanceLockError extends Error {
  constructor(code, message) {
    super(message);
    this.code = code;
  }
}
const fail = (code, message) => { throw new GovernanceLockError(code, message); };
const isObject = (value) => Boolean(value) && typeof value === "object" && !Array.isArray(value);
const nonEmptyText = (value) => typeof value === "string" && Boolean(value.trim());
const sortedUnique = (values) => [...new Set(values)].sort();
const sha256 = (text) => createHash("sha256").update(text).digest("hex");
const canonicalJson = (value) => {
  if (Array.isArray(value)) return `[${value.map(canonicalJson).join(",")}]`;
  if (isObject(value)) return `{${Object.keys(value).sort().map((key) => `${JSON.stringify(key)}:${canonicalJson(value[key])}`).join(",")}}`;
  return JSON.stringify(value);
};
const hashObject = (value) => sha256(canonicalJson(value));

function git(root, args, { allowFailure = false } = {}) {
  const result = spawnSync("git", ["-C", resolve(root), ...args], {
    encoding: "utf8",
    maxBuffer: 64 * 1024 * 1024,
  });
  if (result.error) fail("BLOCKED_GOVERNANCE_LOCK_GIT", `git ${args.join(" ")} failed: ${result.error.message}`);
  if (result.status !== 0 && !allowFailure) {
    fail("BLOCKED_GOVERNANCE_LOCK_GIT", `git ${args.join(" ")} failed: ${(result.stderr || result.stdout || "").trim()}`);
  }
  return { status: result.status, stdout: String(result.stdout || "").trim(), stderr: String(result.stderr || "").trim() };
}

function parseJson(text, label) {
  try { return JSON.parse(text.replace(/^\uFEFF/, "")); }
  catch (error) { fail("BLOCKED_GOVERNANCE_LOCK_JSON", `${label}: ${error.message}`); }
}

function stringArray(payload, field, { allowEmpty = true } = {}) {
  const value = payload?.[field];
  if (!Array.isArray(value)) fail("BLOCKED_GOVERNANCE_LOCK_REGISTRY", `registry.${field} must be an array`);
  if (!allowEmpty && value.length === 0) fail("BLOCKED_GOVERNANCE_LOCK_REGISTRY", `registry.${field} must be non-empty`);
  if (value.some((item) => !nonEmptyText(item))) fail("BLOCKED_GOVERNANCE_LOCK_REGISTRY", `registry.${field} must contain only non-empty strings`);
  if (new Set(value).size !== value.length) fail("BLOCKED_GOVERNANCE_LOCK_REGISTRY", `registry.${field} contains duplicates`);
  return value.map((item) => item.trim());
}

export function normalizeRegistry(registry) {
  if (!isObject(registry) || registry.status !== "ACTIVE_VALIDATOR_CONTRACT") {
    fail("BLOCKED_GOVERNANCE_LOCK_REGISTRY", "lifecycle registry must be ACTIVE_VALIDATOR_CONTRACT");
  }
  if (registry.active_override_or_addendum_count !== 0) {
    fail("BLOCKED_GOVERNANCE_LOCK_REGISTRY", "active_override_or_addendum_count must be 0");
  }
  const activeCanonical = stringArray(registry, "active_canonical", { allowEmpty: false });
  const activeNamedPrompts = stringArray(registry, "active_named_prompts", { allowEmpty: false });
  const activeValidators = stringArray(registry, "active_validator_contracts", { allowEmpty: false });
  const openRemediations = stringArray(registry, "open_remediations");
  const activeMigrations = stringArray(registry, "activation_required_migrations");
  const superseded = stringArray(registry, "superseded");
  const referenceOnly = stringArray(registry, "reference_only");
  const bootstrapRead = stringArray(registry, "bootstrap_read", { allowEmpty: false });

  const categoryRows = [
    ["ACTIVE_CANONICAL", activeCanonical],
    ["ACTIVE_NAMED_PROMPT", activeNamedPrompts],
    ["ACTIVE_VALIDATOR_CONTRACT", activeValidators],
    ["OPEN_REMEDIATION", openRemediations],
    ["ACTIVE_MIGRATION", activeMigrations],
    ["SUPERSEDED", superseded],
    ["REFERENCE_ONLY", referenceOnly],
  ];
  const lifecycleByPath = new Map();
  for (const [lifecycle, paths] of categoryRows) {
    for (const path of paths) {
      if (lifecycleByPath.has(path)) {
        fail("BLOCKED_GOVERNANCE_LOCK_REGISTRY", `${path} is registered in multiple lifecycle classes`);
      }
      lifecycleByPath.set(path, lifecycle);
    }
  }

  const authorityPaths = sortedUnique([
    ...activeCanonical,
    ...activeNamedPrompts,
    ...activeValidators,
    ...openRemediations,
    ...activeMigrations,
  ]);
  const authoritySet = new Set(authorityPaths);
  for (const path of bootstrapRead) {
    if (!authoritySet.has(path)) fail("BLOCKED_GOVERNANCE_LOCK_REGISTRY", `bootstrap_read path is not active authority: ${path}`);
  }
  for (const required of [
    "docs/WORKFLOW.md",
    "docs/OPERATIONS.md",
    "docs/DOCUMENT_UNIVERSE_POLICY.md",
    "docs/RUN_GOVERNANCE_INDEX.md",
    "docs/llm_prompts/v1/PROMPT_MANIFEST.md",
    "docs/llm_prompts/v1/00_NEW_RUN_MASTER_PROMPT.md",
    "docs/llm_prompts/v1/00D_PROMPT_0_0D_DOCUMENT_UNIVERSE_PREFLIGHT.md",
    REGISTRY_PATH,
  ]) {
    if (!bootstrapRead.includes(required)) fail("BLOCKED_GOVERNANCE_LOCK_REGISTRY", `bootstrap_read must include ${required}`);
  }

  return {
    activeCanonical,
    activeNamedPrompts,
    activeValidators,
    openRemediations,
    activeMigrations,
    superseded,
    referenceOnly,
    bootstrapRead: sortedUnique(bootstrapRead),
    authorityPaths,
    lifecycleByPath,
  };
}

function readGitFile(root, commitSha, path) {
  return git(root, ["show", `${commitSha}:${path}`]).stdout;
}
function gitBlob(root, commitSha, path) {
  const blob = git(root, ["rev-parse", `${commitSha}:${path}`]).stdout;
  if (!HEX40.test(blob)) fail("BLOCKED_GOVERNANCE_LOCK_GIT", `invalid git blob for ${path}: ${blob}`);
  return blob;
}
function docsInventory(root, commitSha) {
  const output = git(root, ["ls-tree", "-r", "--name-only", commitSha, "--", "docs"]).stdout;
  return sortedUnique(output.split(/\r?\n/).map((line) => line.trim()).filter((line) => line.startsWith("docs/")));
}
function loadPolicyFor(path, registry) {
  if (registry.bootstrapRead.includes(path)) return "bootstrap";
  if (registry.activeNamedPrompts.includes(path)) return "jit_before_stage";
  return "locked_on_demand";
}

export function lockCoreFromGit({ root = ".", baseMainSha, baseFullBlobSha }) {
  if (!HEX40.test(String(baseMainSha || ""))) fail("BLOCKED_GOVERNANCE_LOCK_BINDING", "40-char base_main_commit_sha required");
  const actualFullBlob = gitBlob(root, baseMainSha, "data/cards.full.json");
  const expectedFullBlob = baseFullBlobSha || actualFullBlob;
  if (!HEX40.test(String(expectedFullBlob || ""))) fail("BLOCKED_GOVERNANCE_LOCK_BINDING", "40-char base_full_blob_sha required");
  if (actualFullBlob !== expectedFullBlob) {
    fail("BLOCKED_GOVERNANCE_LOCK_BINDING", `data/cards.full.json blob mismatch: ${actualFullBlob} != ${expectedFullBlob}`);
  }

  const registryText = readGitFile(root, baseMainSha, REGISTRY_PATH);
  const registryPayload = parseJson(registryText, REGISTRY_PATH);
  const registry = normalizeRegistry(registryPayload);
  const inventory = docsInventory(root, baseMainSha);
  const inventorySet = new Set(inventory);
  const registered = new Set(registry.lifecycleByPath.keys());
  const unclassified = inventory.filter((path) => !registered.has(path));
  const missingRegistered = [...registered].filter((path) => !inventorySet.has(path)).sort();
  if (unclassified.length || missingRegistered.length) {
    fail(
      "BLOCKED_GOVERNANCE_LOCK_CLASSIFICATION",
      `registry/docs mismatch; unclassified=[${unclassified.join(",")}] missing_registered=[${missingRegistered.join(",")}]`,
    );
  }

  const classificationRows = inventory.map((path) => ({
    path,
    lifecycle: registry.lifecycleByPath.get(path),
    blob_sha: gitBlob(root, baseMainSha, path),
  }));
  const lockedAuthorities = registry.authorityPaths.map((path) => ({
    path,
    lifecycle: registry.lifecycleByPath.get(path),
    blob_sha: gitBlob(root, baseMainSha, path),
    load_policy: loadPolicyFor(path, registry),
  }));
  const stageAText = readGitFile(root, baseMainSha, STAGE_A_PATH);
  const stageAEmbedded = stageAText.includes("EMBEDDED_NEWS_VALUE_SELECTION_V4") && stageAText.includes("related_prepass");
  if (!stageAEmbedded) fail("BLOCKED_GOVERNANCE_LOCK_STAGE_A", "locked Stage A lacks embedded news-value/Related pre-pass contract");

  const core = {
    schema: GOVERNANCE_LOCK_SCHEMA,
    repository_head_sha: baseMainSha,
    canonical_full_blob_sha: expectedFullBlob,
    registry_path: REGISTRY_PATH,
    registry_blob_sha: gitBlob(root, baseMainSha, REGISTRY_PATH),
    docs_inventory_count: inventory.length,
    classification_digest_sha256: hashObject(classificationRows),
    locked_authority_count: lockedAuthorities.length,
    bootstrap_read_count: registry.bootstrapRead.length,
    bootstrap_read_paths: registry.bootstrapRead,
    locked_authorities: lockedAuthorities,
  };
  return {
    registry,
    registryPayload,
    inventory,
    classificationRows,
    core,
    lock: { ...core, lock_sha256: hashObject(core) },
  };
}

export function emitGovernanceArtifact({ root = ".", baseMainSha, baseFullBlobSha }) {
  const built = lockCoreFromGit({ root, baseMainSha, baseFullBlobSha });
  const { registry, inventory, lock } = built;
  return {
    stage: "0.0D",
    status: "PASS",
    repository_head_sha: lock.repository_head_sha,
    canonical_full_blob_sha: lock.canonical_full_blob_sha,
    docs_inventory_count: inventory.length,
    classified_count: inventory.length,
    locked_authority_count: lock.locked_authority_count,
    bootstrap_read_count: lock.bootstrap_read_count,
    bootstrap_read_paths: lock.bootstrap_read_paths,
    active_canonical_paths: sortedUnique([...registry.activeCanonical, ...registry.activeNamedPrompts]),
    active_validator_contract_paths: sortedUnique(registry.activeValidators),
    applicable_remediation_or_migration: sortedUnique([...registry.openRemediations, ...registry.activeMigrations]),
    superseded_or_reference_paths: sortedUnique([...registry.superseded, ...registry.referenceOnly]),
    unclassified_paths: [],
    unread_active_paths: [],
    unresolved_dependencies: [],
    unresolved_conflicts: [],
    unregistered_active_looking_paths: [],
    active_override_or_addendum_count: 0,
    stage_a_embedded_news_value_verified: true,
    all_docs_files_read_or_parsed: true,
    unresolved_rule_conflicts: [],
    incomplete_universe_defects: [],
    stage_0_0c_authorized: true,
    active_full_read_count: lock.locked_authority_count,
    governance_lock: lock,
  };
}

function exactJson(left, right) { return canonicalJson(left) === canonicalJson(right); }

export function validateGovernanceLockStructure(artifact, registryPayload) {
  if (!isObject(artifact) || artifact.stage !== "0.0D" || artifact.status !== "PASS") {
    fail("BLOCKED_GOVERNANCE_LOCK_ARTIFACT", "0.0D artifact must declare stage=0.0D and status=PASS");
  }
  if (!isObject(artifact.governance_lock)) {
    fail("BLOCKED_GOVERNANCE_LOCK_MISSING", "0.0D governance_lock is mandatory; legacy count-only self-attestation is not accepted");
  }
  const registry = normalizeRegistry(registryPayload);
  const lock = artifact.governance_lock;
  if (lock.schema !== GOVERNANCE_LOCK_SCHEMA) fail("BLOCKED_GOVERNANCE_LOCK_ARTIFACT", `governance_lock.schema must be ${GOVERNANCE_LOCK_SCHEMA}`);
  if (!HEX40.test(String(lock.registry_blob_sha || ""))) fail("BLOCKED_GOVERNANCE_LOCK_ARTIFACT", "governance_lock.registry_blob_sha must be a git blob SHA");
  if (!HEX64.test(String(lock.classification_digest_sha256 || ""))) fail("BLOCKED_GOVERNANCE_LOCK_ARTIFACT", "governance_lock.classification_digest_sha256 must be sha256");
  if (!HEX64.test(String(lock.lock_sha256 || ""))) fail("BLOCKED_GOVERNANCE_LOCK_ARTIFACT", "governance_lock.lock_sha256 must be sha256");
  const { lock_sha256: suppliedHash, ...core } = lock;
  if (hashObject(core) !== suppliedHash) fail("BLOCKED_GOVERNANCE_LOCK_HASH", "governance_lock.lock_sha256 does not match lock payload");
  if (!Array.isArray(lock.locked_authorities) || lock.locked_authorities.length !== registry.authorityPaths.length) {
    fail("BLOCKED_GOVERNANCE_LOCK_AUTHORITY", `locked_authorities must contain the exact registry authority set (${registry.authorityPaths.length})`);
  }
  const paths = lock.locked_authorities.map((row) => row?.path);
  if (!exactJson(sortedUnique(paths), registry.authorityPaths)) fail("BLOCKED_GOVERNANCE_LOCK_AUTHORITY", "locked_authorities paths do not match registry authority set");
  for (const row of lock.locked_authorities) {
    if (!isObject(row) || !nonEmptyText(row.path) || !HEX40.test(String(row.blob_sha || ""))) {
      fail("BLOCKED_GOVERNANCE_LOCK_AUTHORITY", "every locked authority requires path + git blob SHA");
    }
    const expectedLifecycle = registry.lifecycleByPath.get(row.path);
    if (row.lifecycle !== expectedLifecycle) fail("BLOCKED_GOVERNANCE_LOCK_AUTHORITY", `${row.path} lifecycle mismatch`);
    const expectedPolicy = loadPolicyFor(row.path, registry);
    if (row.load_policy !== expectedPolicy) fail("BLOCKED_GOVERNANCE_LOCK_AUTHORITY", `${row.path} load_policy must be ${expectedPolicy}`);
  }
  if (lock.locked_authority_count !== registry.authorityPaths.length || artifact.locked_authority_count !== lock.locked_authority_count) {
    fail("BLOCKED_GOVERNANCE_LOCK_AUTHORITY", "locked_authority_count mismatch");
  }
  if (!exactJson(lock.bootstrap_read_paths, registry.bootstrapRead)
    || !exactJson(artifact.bootstrap_read_paths, registry.bootstrapRead)
    || lock.bootstrap_read_count !== registry.bootstrapRead.length
    || artifact.bootstrap_read_count !== registry.bootstrapRead.length) {
    fail("BLOCKED_GOVERNANCE_LOCK_BOOTSTRAP", "bootstrap_read paths/count must exactly match registry.bootstrap_read");
  }
  if (artifact.repository_head_sha !== lock.repository_head_sha || artifact.canonical_full_blob_sha !== lock.canonical_full_blob_sha) {
    fail("BLOCKED_GOVERNANCE_LOCK_BINDING", "top-level 0.0D baseline bindings must match governance_lock");
  }
  if (artifact.active_full_read_count !== lock.locked_authority_count) {
    fail("BLOCKED_GOVERNANCE_LOCK_COMPAT", "legacy active_full_read_count compatibility mirror must equal locked_authority_count; it is not read evidence");
  }
  return true;
}

export function verifyGovernanceArtifactFromGit(artifact, { root = ".", baseMainSha, baseFullBlobSha }) {
  const expected = emitGovernanceArtifact({ root, baseMainSha, baseFullBlobSha });
  validateGovernanceLockStructure(artifact, lockCoreFromGit({ root, baseMainSha, baseFullBlobSha }).registryPayload);
  const deterministicKeys = [
    "repository_head_sha",
    "canonical_full_blob_sha",
    "docs_inventory_count",
    "classified_count",
    "locked_authority_count",
    "bootstrap_read_count",
    "bootstrap_read_paths",
    "active_canonical_paths",
    "active_validator_contract_paths",
    "applicable_remediation_or_migration",
    "superseded_or_reference_paths",
    "active_override_or_addendum_count",
    "stage_a_embedded_news_value_verified",
    "active_full_read_count",
    "governance_lock",
  ];
  for (const key of deterministicKeys) {
    if (!exactJson(artifact[key], expected[key])) fail("BLOCKED_GOVERNANCE_LOCK_REPLAY", `0.0D.${key} does not match deterministic locked-main replay`);
  }
  for (const key of [
    "unclassified_paths",
    "unread_active_paths",
    "unresolved_dependencies",
    "unresolved_conflicts",
    "unregistered_active_looking_paths",
    "unresolved_rule_conflicts",
    "incomplete_universe_defects",
  ]) {
    if (!Array.isArray(artifact[key]) || artifact[key].length !== 0) fail("BLOCKED_GOVERNANCE_LOCK_DEFECT", `0.0D.${key} must be empty on PASS`);
  }
  if (artifact.all_docs_files_read_or_parsed !== true || artifact.stage_0_0c_authorized !== true) {
    fail("BLOCKED_GOVERNANCE_LOCK_ARTIFACT", "0.0D compatibility PASS booleans must be true");
  }
  return true;
}

function parseArgs(argv) {
  const out = { root: ".", emit: false, verify: false, selfTest: false };
  for (let index = 0; index < argv.length; index += 1) {
    const arg = argv[index];
    if (arg === "--emit") out.emit = true;
    else if (arg === "--verify") out.verify = true;
    else if (arg === "--self-test") out.selfTest = true;
    else if (["--root", "--base-main-sha", "--base-full-blob-sha", "--output", "--artifact"].includes(arg)) {
      const value = argv[index + 1];
      if (!value || value.startsWith("--")) fail("INVALID_ARGUMENT", `${arg} value required`);
      index += 1;
      if (arg === "--root") out.root = value;
      if (arg === "--base-main-sha") out.baseMainSha = value;
      if (arg === "--base-full-blob-sha") out.baseFullBlobSha = value;
      if (arg === "--output") out.output = value;
      if (arg === "--artifact") out.artifact = value;
    } else fail("INVALID_ARGUMENT", `unsupported argument ${arg}`);
  }
  return out;
}

function expectBlocked(fn, code) {
  let blocked = false;
  try { fn(); }
  catch (error) { blocked = error instanceof GovernanceLockError && error.code === code; }
  if (!blocked) throw new Error(`self-test expected ${code}`);
}

function selfTest() {
  const root = resolve(".");
  const head = git(root, ["rev-parse", "HEAD"]).stdout;
  const fullBlob = gitBlob(root, head, "data/cards.full.json");
  const artifact = emitGovernanceArtifact({ root, baseMainSha: head, baseFullBlobSha: fullBlob });
  verifyGovernanceArtifactFromGit(artifact, { root, baseMainSha: head, baseFullBlobSha: fullBlob });

  const legacyCountOnly = structuredClone(artifact);
  delete legacyCountOnly.governance_lock;
  legacyCountOnly.active_full_read_count = artifact.locked_authority_count;
  const registryPayload = parseJson(readGitFile(root, head, REGISTRY_PATH), REGISTRY_PATH);
  expectBlocked(() => validateGovernanceLockStructure(legacyCountOnly, registryPayload), "BLOCKED_GOVERNANCE_LOCK_MISSING");

  const tampered = structuredClone(artifact);
  tampered.governance_lock.locked_authorities[0].blob_sha = "0".repeat(40);
  const { lock_sha256: _old, ...tamperedCore } = tampered.governance_lock;
  tampered.governance_lock.lock_sha256 = hashObject(tamperedCore);
  expectBlocked(
    () => verifyGovernanceArtifactFromGit(tampered, { root, baseMainSha: head, baseFullBlobSha: fullBlob }),
    "BLOCKED_GOVERNANCE_LOCK_REPLAY",
  );

  const jit = artifact.governance_lock.locked_authorities.filter((row) => row.load_policy === "jit_before_stage");
  if (jit.length === 0) throw new Error("self-test expected JIT named-stage prompt entries");
  if (artifact.bootstrap_read_count >= artifact.locked_authority_count) throw new Error("bootstrap set must be smaller than locked authority set");
  console.log(`PASS: deterministic governance lock; docs=${artifact.docs_inventory_count}; locked=${artifact.locked_authority_count}; bootstrap=${artifact.bootstrap_read_count}; jit=${jit.length}; legacy count-only attestation rejected`);
}

function main() {
  const options = parseArgs(process.argv.slice(2));
  if (options.selfTest) return selfTest();
  if (options.emit === options.verify) fail("INVALID_ARGUMENT", "choose exactly one of --emit or --verify");
  if (!options.baseMainSha) fail("INVALID_ARGUMENT", "--base-main-sha required");
  const fullBlob = options.baseFullBlobSha || gitBlob(options.root, options.baseMainSha, "data/cards.full.json");
  if (options.emit) {
    const artifact = emitGovernanceArtifact({ root: options.root, baseMainSha: options.baseMainSha, baseFullBlobSha: fullBlob });
    const text = `${JSON.stringify(artifact, null, 2)}\n`;
    if (options.output) writeFileSync(resolve(options.root, options.output), text);
    else process.stdout.write(text);
    return;
  }
  if (!options.artifact) fail("INVALID_ARGUMENT", "--artifact required with --verify");
  const artifact = parseJson(readFileSync(resolve(options.root, options.artifact), "utf8"), options.artifact);
  verifyGovernanceArtifactFromGit(artifact, { root: options.root, baseMainSha: options.baseMainSha, baseFullBlobSha: fullBlob });
  console.log("PASS: deterministic governance lock matches locked main git tree");
}

if (process.argv[1] && import.meta.url === pathToFileURL(resolve(process.argv[1])).href) {
  try { main(); }
  catch (error) {
    if (error instanceof GovernanceLockError) {
      console.error(`FAIL [${error.code}]: ${error.message}`);
      process.exit(1);
    }
    console.error(`FAIL [BLOCKED_GOVERNANCE_LOCK_INTERNAL]: ${error?.message || String(error)}`);
    process.exit(1);
  }
}
