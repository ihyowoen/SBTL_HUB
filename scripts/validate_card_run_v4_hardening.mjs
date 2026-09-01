#!/usr/bin/env node
import { existsSync, mkdtempSync, mkdirSync, readFileSync, rmSync, writeFileSync } from "node:fs";
import { dirname, join, resolve, sep } from "node:path";
import { spawnSync } from "node:child_process";
import { tmpdir } from "node:os";

class ValidationError extends Error {
  constructor(code, message) { super(message); this.code = code; }
}
const fail = (code, message) => { throw new ValidationError(code, message); };
const isObject = (value) => Boolean(value) && typeof value === "object" && !Array.isArray(value);
const nonEmptyText = (value) => typeof value === "string" && Boolean(value.trim());
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
const requireArray = (payload, field, code, label) => {
  if (!Array.isArray(payload?.[field])) fail(code, `${label}.${field} must be an array`);
  return payload[field];
};
const requireObject = (payload, field, code, label, { nonEmpty = false } = {}) => {
  const value = payload?.[field];
  if (!isObject(value) || (nonEmpty && Object.keys(value).length === 0)) {
    fail(code, `${label}.${field} must be ${nonEmpty ? "a non-empty" : "an"} object`);
  }
  return value;
};
const requireEmptyArray = (payload, field, code, label) => {
  const value = requireArray(payload, field, code, label);
  if (value.length !== 0) fail(code, `${label}.${field} must be empty on PASS`);
};
const uniqueNonEmptyStrings = (values, code, label) => {
  if (values.some((value) => !nonEmptyText(value))) fail(code, `${label} must contain only non-empty strings`);
  if (new Set(values).size !== values.length) fail(code, `${label} must not contain duplicates`);
};

const COMPLETENESS_BOOLEANS = [
  "source_universe_accounted",
  "regional_search_complete",
  "topic_search_complete",
  "baseline_follow_up_review_complete",
  "review_pool_rescue_complete",
  "must_report_candidates_accounted",
];

const PREFLIGHT_DEFECT_ARRAYS = [
  "unclassified_paths",
  "unread_active_paths",
  "unresolved_dependencies",
  "unresolved_conflicts",
  "unregistered_active_looking_paths",
  "unresolved_rule_conflicts",
  "incomplete_universe_defects",
];
const PREFLIGHT_PATH_ARRAYS = [
  "active_canonical_paths",
  "active_validator_contract_paths",
  "applicable_remediation_or_migration",
  "superseded_or_reference_paths",
];

function validateDocumentUniverse(run, root) {
  const label = "Stage 0.0D";
  const path = resolveRepoJson(root, run.document_universe_manifest_ref, "document_universe_manifest_ref");
  const artifact = readJson(path, label);
  if (artifact.stage !== "0.0D" || artifact.status !== "PASS") {
    fail("BLOCKED_DOCUMENT_UNIVERSE_ENVELOPE", "0.0D artifact must declare stage=0.0D and status=PASS");
  }
  if (artifact.repository_head_sha !== run.base_main_commit_sha) {
    fail("BLOCKED_DOCUMENT_UNIVERSE_BINDING", "0.0D repository_head_sha must match base_main_commit_sha");
  }
  if (artifact.canonical_full_blob_sha !== run.base_full_blob_sha) {
    fail("BLOCKED_DOCUMENT_UNIVERSE_BINDING", "0.0D canonical_full_blob_sha must match base_full_blob_sha");
  }
  for (const field of PREFLIGHT_PATH_ARRAYS) {
    const values = requireArray(artifact, field, "BLOCKED_DOCUMENT_UNIVERSE_DETAIL", label);
    uniqueNonEmptyStrings(values, "BLOCKED_DOCUMENT_UNIVERSE_DETAIL", `${label}.${field}`);
  }
  for (const field of PREFLIGHT_DEFECT_ARRAYS) {
    requireEmptyArray(artifact, field, "BLOCKED_DOCUMENT_UNIVERSE_DETAIL", label);
  }
  for (const field of ["docs_inventory_count", "classified_count", "active_full_read_count", "active_override_or_addendum_count"]) {
    if (!Number.isInteger(artifact[field]) || artifact[field] < 0) {
      fail("BLOCKED_DOCUMENT_UNIVERSE_DETAIL", `${label}.${field} must be a non-negative integer`);
    }
  }
  if (artifact.classified_count !== artifact.docs_inventory_count) {
    fail("BLOCKED_DOCUMENT_UNIVERSE_DETAIL", "0.0D classified_count must equal docs_inventory_count on PASS");
  }
  const requiredFullReadPaths = new Set([
    ...artifact.active_canonical_paths,
    ...artifact.active_validator_contract_paths,
    ...artifact.applicable_remediation_or_migration,
  ]);
  if (artifact.active_full_read_count < requiredFullReadPaths.size) {
    fail("BLOCKED_DOCUMENT_UNIVERSE_DETAIL", "0.0D active_full_read_count is smaller than the required active/dependency path set");
  }
  if (artifact.active_full_read_count > artifact.docs_inventory_count) {
    fail("BLOCKED_DOCUMENT_UNIVERSE_DETAIL", "0.0D active_full_read_count cannot exceed docs_inventory_count");
  }
  if (artifact.active_override_or_addendum_count !== 0) {
    fail("BLOCKED_DOCUMENT_UNIVERSE_DETAIL", "0.0D active_override_or_addendum_count must be 0");
  }
  if (artifact.stage_a_embedded_news_value_verified !== true) {
    fail("BLOCKED_DOCUMENT_UNIVERSE_DETAIL", "0.0D stage_a_embedded_news_value_verified must be true");
  }
  if (artifact.all_docs_files_read_or_parsed !== true || artifact.stage_0_0c_authorized !== true) {
    fail("BLOCKED_DOCUMENT_UNIVERSE_ENVELOPE", "0.0D compatibility PASS booleans must both be true");
  }
  return artifact;
}

const COVERAGE_ARRAY_FIELDS = [
  "original_input_ledger",
  "discovered_missing_candidates",
  "baseline_follow_up_candidates",
  "existing_card_reinforcements",
  "existing_card_update_candidates",
  "correction_or_reversal_candidates",
  "treasure_rescue_candidates",
  "searched_but_no_material_event_ledger",
  "source_universe_expansion_ledger",
  "must_report_candidate_ledger",
  "known_unknowns",
  "residual_coverage_risks",
  "terminal_discovery_disposition_ledger",
];
const COVERAGE_CANDIDATE_FIELDS = [
  "original_input_ledger",
  "discovered_missing_candidates",
  "baseline_follow_up_candidates",
  "existing_card_reinforcements",
  "existing_card_update_candidates",
  "correction_or_reversal_candidates",
  "treasure_rescue_candidates",
  "must_report_candidate_ledger",
];
const candidateId = (row) => {
  if (!isObject(row)) return null;
  for (const field of ["candidate_id", "story_id", "source_story_id", "spec_id", "source_spec_id", "id"]) {
    if (nonEmptyText(row[field])) return row[field].trim();
  }
  return null;
};

function requireCandidateIds(rows, label) {
  const ids = [];
  rows.forEach((row, index) => {
    const id = candidateId(row);
    if (!id) fail("BLOCKED_COVERAGE_LEDGER", `${label}[${index}] must carry candidate_id (or a governed identity alias)`);
    ids.push(id);
  });
  if (new Set(ids).size !== ids.length) fail("BLOCKED_COVERAGE_LEDGER", `${label} contains duplicate candidate identities`);
  return ids;
}

function validateCoverage(run, root) {
  const label = "Stage 0.0C";
  const path = resolveRepoJson(root, run.coverage_discovery_ref, "coverage_discovery_ref");
  const artifact = readJson(path, label);
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
  for (const field of COVERAGE_ARRAY_FIELDS) requireArray(artifact, field, "BLOCKED_COVERAGE_LEDGER", label);
  requireObject(artifact, "regional_coverage_matrix", "BLOCKED_COVERAGE_LEDGER", label, { nonEmpty: true });
  requireObject(artifact, "topic_coverage_matrix", "BLOCKED_COVERAGE_LEDGER", label, { nonEmpty: true });

  const expansionIds = requireCandidateIds(artifact.source_universe_expansion_ledger, `${label}.source_universe_expansion_ledger`);
  const expansionSet = new Set(expansionIds);
  const requiredIds = new Set();
  for (const field of COVERAGE_CANDIDATE_FIELDS) {
    for (const id of requireCandidateIds(artifact[field], `${label}.${field}`)) requiredIds.add(id);
  }
  for (const id of requiredIds) {
    if (!expansionSet.has(id)) fail("BLOCKED_COVERAGE_LEDGER", `0.0C candidate ${id} is absent from source_universe_expansion_ledger`);
  }

  const terminalRows = artifact.terminal_discovery_disposition_ledger;
  const terminalIds = [];
  terminalRows.forEach((row, index) => {
    const id = candidateId(row);
    if (!id) fail("BLOCKED_COVERAGE_LEDGER", `${label}.terminal_discovery_disposition_ledger[${index}] missing candidate identity`);
    if (!nonEmptyText(row.disposition)) {
      fail("BLOCKED_COVERAGE_LEDGER", `${label}.terminal_discovery_disposition_ledger[${index}].disposition must be non-empty`);
    }
    terminalIds.push(id);
  });
  if (new Set(terminalIds).size !== terminalIds.length) {
    fail("BLOCKED_COVERAGE_LEDGER", "0.0C terminal_discovery_disposition_ledger contains duplicate candidate identities");
  }
  const terminalSet = new Set(terminalIds);
  for (const id of expansionSet) {
    if (!terminalSet.has(id)) fail("BLOCKED_COVERAGE_LEDGER", `0.0C expanded candidate ${id} has no terminal discovery disposition`);
  }
  for (const id of terminalSet) {
    if (!expansionSet.has(id)) fail("BLOCKED_COVERAGE_LEDGER", `0.0C terminal disposition ${id} is not present in source_universe_expansion_ledger`);
  }
  if (artifact.original_input_ledger.length > 0 && expansionSet.size === 0) {
    fail("BLOCKED_COVERAGE_LEDGER", "0.0C cannot account original input with an empty expanded universe ledger");
  }
  return artifact;
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

const REQUIRED_OPERATION_STAGES = ["A", "B", "C", "0.4", "0.5", "0.6", "0.7"];
const STAGE_BUCKETS = {
  A: ["strict_passed_spec"],
  B: ["draft_cards", "draft_card"],
  C: ["accepted_fact_safe"],
  "0.4": ["addable_merge_safe"],
  "0.5": ["evidence_complete_and_source_claim_covered"],
  "0.6": ["content_enriched_and_language_polished"],
  "0.7": ["publish_ready"],
};
const normalizeStage = (payload) => {
  const raw = typeof payload?.stage === "string" ? payload.stage.trim().toLowerCase() : "";
  const explicit = new Map([
    ["a", "A"], ["stage_a", "A"], ["0.1", "A"],
    ["b", "B"], ["stage_b", "B"], ["0.2", "B"],
    ["c", "C"], ["stage_c", "C"], ["0.3", "C"],
    ["0.4", "0.4"], ["0.5", "0.5"], ["0.6", "0.6"], ["0.7", "0.7"],
  ]);
  if (explicit.has(raw)) return explicit.get(raw);
  for (const stage of REQUIRED_OPERATION_STAGES) {
    if (STAGE_BUCKETS[stage].some((bucket) => Object.prototype.hasOwnProperty.call(payload || {}, bucket))) return stage;
  }
  return null;
};
const stageItems = (payload, stage) => {
  const items = [];
  for (const bucket of STAGE_BUCKETS[stage] || []) {
    const value = payload?.[bucket];
    if (Array.isArray(value)) items.push(...value.filter(isObject));
    else if (isObject(value)) items.push(value);
  }
  return items;
};
const stageCandidateIds = (payload, stage) => new Set(stageItems(payload, stage)
  .map((item) => stage === "A" ? item.spec_id : item.source_spec_id)
  .filter(nonEmptyText)
  .map((value) => value.trim()));

function runPythonChecker(checker, args, label) {
  const result = spawnSync("python3", [resolve(checker), ...args], { encoding: "utf8" });
  if (result.error) fail("BLOCKED_STAGE_CHAIN_CONTRACT", `${label}: checker 실행 실패 — ${result.error.message}`);
  if (result.status !== 0) {
    const detail = (result.stdout || result.stderr || "stage contract failed").trim();
    fail("BLOCKED_STAGE_CHAIN_CONTRACT", `${label}: ${detail}`);
  }
}

function validateStageArtifact(path, stage, label) {
  runPythonChecker("validation_scripts/stage_artifact_contract_check.py", [stage, path], label);
  if (stage === "A") runPythonChecker("validation_scripts/stage_lineage_contract_check.py", ["stage_a", path], label);
}

function loadCanonicalSpecMap(root) {
  const path = resolve(root, "data/cards.full.json");
  if (!existsSync(path)) return new Map();
  const payload = readJson(path, "data/cards.full.json");
  if (!Array.isArray(payload?.cards)) fail("BLOCKED_OPERATION_IDENTITY", "data/cards.full.json.cards array required");
  const map = new Map();
  for (const card of payload.cards) {
    if (nonEmptyText(card?.id) && nonEmptyText(card?.source_spec_id)) map.set(card.id.trim(), card.source_spec_id.trim());
  }
  return map;
}

function operationSpecId(kind, operation, canonicalSpecMap, insertedSpecMap, label) {
  if (kind === "insert") {
    if (!isObject(operation.card) || !nonEmptyText(operation.card.source_spec_id)) {
      fail("BLOCKED_OPERATION_IDENTITY", `${label}.card.source_spec_id is required to bind the formal stage chain`);
    }
    return operation.card.source_spec_id.trim();
  }
  if (kind === "update") {
    if (!nonEmptyText(operation.id)) fail("BLOCKED_OPERATION_IDENTITY", `${label}.id required`);
    const id = operation.id.trim();
    const specId = canonicalSpecMap.get(id) || insertedSpecMap.get(id);
    if (!specId) fail("BLOCKED_OPERATION_IDENTITY", `${label} cannot resolve source_spec_id for card ${id}`);
    return specId;
  }
  if (kind === "related_add") {
    if (!nonEmptyText(operation.source_id) || !nonEmptyText(operation.target_id)) {
      fail("BLOCKED_OPERATION_IDENTITY", `${label}.source_id and target_id required`);
    }
    const sourceId = operation.source_id.trim();
    const targetId = operation.target_id.trim();
    const sourceSpec = insertedSpecMap.get(sourceId) || canonicalSpecMap.get(sourceId);
    const targetSpec = insertedSpecMap.get(targetId) || canonicalSpecMap.get(targetId);
    const specId = sourceSpec || targetSpec;
    if (!specId) fail("BLOCKED_OPERATION_IDENTITY", `${label} cannot resolve a governed source_spec_id from either Related endpoint`);
    return specId;
  }
  fail("BLOCKED_OPERATION_IDENTITY", `${label}: unsupported operation kind ${kind}`);
}

function validateRun(run, root = ".") {
  if (!run || typeof run !== "object" || Array.isArray(run)) fail("BLOCKED_V4_HARDENING_INVALID", "card-run object required");
  validateDocumentUniverse(run, root);
  validateCoverage(run, root);
  validateCompleteness(run, root);

  const canonicalSpecMap = loadCanonicalSpecMap(root);
  const insertedSpecMap = new Map();
  for (const operation of run.operations?.insert || []) {
    if (nonEmptyText(operation?.card?.id) && nonEmptyText(operation?.card?.source_spec_id)) {
      insertedSpecMap.set(operation.card.id.trim(), operation.card.source_spec_id.trim());
    }
  }

  let validatedStageArtifacts = 0;
  let operationCount = 0;
  for (const kind of ["insert", "update", "related_add"]) {
    const operations = run.operations?.[kind];
    if (!Array.isArray(operations)) fail("BLOCKED_V4_HARDENING_INVALID", `operations.${kind} array required`);
    for (const [operationIndex, operation] of operations.entries()) {
      operationCount += 1;
      const operationLabel = `${kind}[${operationIndex}]`;
      if (!Array.isArray(operation?.stage_artifacts) || operation.stage_artifacts.length === 0) {
        fail("BLOCKED_V4_HARDENING_INVALID", `${operationLabel}.stage_artifacts required`);
      }
      const expectedSpecId = operationSpecId(kind, operation, canonicalSpecMap, insertedSpecMap, operationLabel);
      const matchedStages = new Map(REQUIRED_OPERATION_STAGES.map((stage) => [stage, 0]));
      const presentStages = new Set();
      for (const [referenceIndex, reference] of operation.stage_artifacts.entries()) {
        const label = `${operationLabel}.stage_artifacts[${referenceIndex}]`;
        const path = resolveRepoJson(root, reference, label);
        const payload = readJson(path, label);
        const stage = normalizeStage(payload);
        if (!stage || !REQUIRED_OPERATION_STAGES.includes(stage)) continue;
        presentStages.add(stage);
        validateStageArtifact(path, stage, label);
        validatedStageArtifacts += 1;
        if (stageCandidateIds(payload, stage).has(expectedSpecId)) {
          matchedStages.set(stage, matchedStages.get(stage) + 1);
        }
      }
      const missingStages = REQUIRED_OPERATION_STAGES.filter((stage) => !presentStages.has(stage));
      if (missingStages.length) {
        fail("BLOCKED_OPERATION_STAGE_CHAIN_MISSING", `${operationLabel} missing mandatory stage artifacts: ${missingStages.join(", ")}`);
      }
      const identityMismatches = REQUIRED_OPERATION_STAGES.filter((stage) => matchedStages.get(stage) === 0);
      if (identityMismatches.length) {
        fail(
          "BLOCKED_OPERATION_STAGE_IDENTITY_MISMATCH",
          `${operationLabel} stage chain is not bound to source_spec_id=${expectedSpecId} at: ${identityMismatches.join(", ")}`,
        );
      }
    }
  }
  return { stage_artifacts_validated: validatedStageArtifacts, operations_with_complete_stage_chain: operationCount };
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
    const baseMainCommitSha = "b".repeat(40);
    const baseFullBlobSha = "a".repeat(40);
    const documentUniverseRef = "artifacts/0.0d.json";
    write("0.0d.json", {
      stage: "0.0D", status: "PASS",
      repository_head_sha: baseMainCommitSha,
      canonical_full_blob_sha: baseFullBlobSha,
      docs_inventory_count: 3,
      classified_count: 3,
      active_full_read_count: 2,
      active_canonical_paths: ["docs/a.md"],
      active_validator_contract_paths: ["docs/b.md"],
      applicable_remediation_or_migration: [],
      superseded_or_reference_paths: ["docs/c.md"],
      unclassified_paths: [], unread_active_paths: [], unresolved_dependencies: [],
      unresolved_conflicts: [], unregistered_active_looking_paths: [],
      active_override_or_addendum_count: 0,
      stage_a_embedded_news_value_verified: true,
      all_docs_files_read_or_parsed: true,
      unresolved_rule_conflicts: [], incomplete_universe_defects: [],
      stage_0_0c_authorized: true,
    });
    const coverageRef = write("0.0c.json", {
      stage: "0.0C", status: "PASS",
      original_input_accounted: true, stage_a_authorized: true,
      document_universe_manifest_ref: documentUniverseRef,
      base_full_blob_sha: baseFullBlobSha,
      original_input_ledger: [{ candidate_id: "CAND_1" }],
      discovered_missing_candidates: [], baseline_follow_up_candidates: [],
      existing_card_reinforcements: [], existing_card_update_candidates: [],
      correction_or_reversal_candidates: [], treasure_rescue_candidates: [],
      regional_coverage_matrix: { global: { status: "searched" } },
      topic_coverage_matrix: { battery: { status: "searched" } },
      searched_but_no_material_event_ledger: [],
      source_universe_expansion_ledger: [{ candidate_id: "CAND_1", origin: "original_input" }],
      must_report_candidate_ledger: [], known_unknowns: [], residual_coverage_risks: [],
      terminal_discovery_disposition_ledger: [{ candidate_id: "CAND_1", disposition: "stage_a_universe" }],
    });
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
    const nonStageA = write("stage-0.4.json", { stage: "0.4", status: "PASS", lineage_guard: "PASS", addable_merge_safe: [] });
    const common = {
      base_main_commit_sha: baseMainCommitSha,
      document_universe_manifest_ref: documentUniverseRef,
      coverage_discovery_ref: coverageRef,
      independent_completeness_ref: completenessRef,
      base_full_blob_sha: baseFullBlobSha,
    };
    const run = {
      ...common,
      operations: { insert: [{ card: { id: "CARD_1", source_spec_id: "SPEC_1" }, stage_artifacts: [malformedStageA] }], update: [], related_add: [] },
    };
    let stageABlocked = false;
    try { validateRun(run, root); } catch (error) { stageABlocked = error instanceof ValidationError && error.code === "BLOCKED_STAGE_CHAIN_CONTRACT"; }
    if (!stageABlocked) throw new Error("self-test failed to reject malformed Stage A artifact");

    let missingStageABlocked = false;
    try {
      validateRun({
        ...common,
        operations: { insert: [{ card: { id: "CARD_1", source_spec_id: "SPEC_1" }, stage_artifacts: [nonStageA] }], update: [], related_add: [] },
      }, root);
    } catch (error) {
      missingStageABlocked = error instanceof ValidationError && error.code === "BLOCKED_OPERATION_STAGE_CHAIN_MISSING";
    }
    if (!missingStageABlocked) throw new Error("self-test failed to require the complete stage chain per operation");

    const badCoverage = readJson(join(root, coverageRef), "test coverage");
    badCoverage.original_input_accounted = false;
    writeFileSync(join(root, coverageRef), `${JSON.stringify(badCoverage, null, 2)}\n`);
    let coverageBlocked = false;
    try { validateRun({ ...common, operations: { insert: [], update: [], related_add: [] } }, root); }
    catch (error) { coverageBlocked = error instanceof ValidationError && error.code === "BLOCKED_COVERAGE_ENVELOPE"; }
    if (!coverageBlocked) throw new Error("self-test failed to reject incomplete 0.0C envelope");

    const goodCoverage = { ...badCoverage, original_input_accounted: true };
    writeFileSync(join(root, coverageRef), `${JSON.stringify(goodCoverage, null, 2)}\n`);
    const badPreflight = readJson(join(root, documentUniverseRef), "test preflight");
    badPreflight.classified_count = 0;
    writeFileSync(join(root, documentUniverseRef), `${JSON.stringify(badPreflight, null, 2)}\n`);
    let preflightBlocked = false;
    try { validateRun({ ...common, operations: { insert: [], update: [], related_add: [] } }, root); }
    catch (error) { preflightBlocked = error instanceof ValidationError && error.code === "BLOCKED_DOCUMENT_UNIVERSE_DETAIL"; }
    if (!preflightBlocked) throw new Error("self-test failed to reject contradictory 0.0D detail");

    badPreflight.classified_count = badPreflight.docs_inventory_count;
    writeFileSync(join(root, documentUniverseRef), `${JSON.stringify(badPreflight, null, 2)}\n`);
    const badCompleteness = readJson(join(root, completenessRef), "test completeness");
    badCompleteness.source_universe_accounted = false;
    writeFileSync(join(root, completenessRef), `${JSON.stringify(badCompleteness, null, 2)}\n`);
    let completenessBlocked = false;
    try { validateRun({ ...common, operations: { insert: [], update: [], related_add: [] } }, root); }
    catch (error) { completenessBlocked = error instanceof ValidationError && error.code === "BLOCKED_COMPLETENESS_ENVELOPE"; }
    if (!completenessBlocked) throw new Error("self-test failed to reject incomplete 0.7C envelope");
    console.log("PASS: formal V4 card-run hardening reconciles 0.0D/0.0C, requires complete candidate-bound A→0.7 chains, and enforces 0.7C conclusions");
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
  console.log(`PASS: formal V4 hardening; stage artifacts validated=${result.stage_artifacts_validated}; operations=${result.operations_with_complete_stage_chain}`);
} catch (error) {
  if (error instanceof ValidationError) { console.error(`FAIL [${error.code}]: ${error.message}`); process.exit(1); }
  throw error;
}
