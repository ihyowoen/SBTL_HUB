#!/usr/bin/env node
import { existsSync, mkdtempSync, mkdirSync, readFileSync, rmSync, writeFileSync } from "node:fs";
import { dirname, join, resolve, sep } from "node:path";
import { spawnSync } from "node:child_process";
import { tmpdir } from "node:os";
import { loadWorkflowV4CoverageAxes } from "./workflow_v4_coverage_axes.mjs";

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
  if (!nonEmptyText(reference) || !reference.endsWith(".json")) {
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
const sortedUnique = (values) => [...new Set(values)].sort();
const exactStringSet = (actual, expected, code, label) => {
  uniqueNonEmptyStrings(actual, code, label);
  const left = sortedUnique(actual);
  const right = sortedUnique(expected);
  if (JSON.stringify(left) !== JSON.stringify(right)) {
    const missing = right.filter((item) => !left.includes(item));
    const extra = left.filter((item) => !right.includes(item));
    fail(code, `${label} must match current lifecycle registry; missing=[${missing.join(",")}] extra=[${extra.join(",")}]`);
  }
};

const REGISTRY_PATH = "docs/llm_prompts/v1/GOVERNANCE_LIFECYCLE_REGISTRY.json";
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
let cachedCoverageAxes = null;
function requiredCoverageAxes() {
  if (cachedCoverageAxes) return cachedCoverageAxes;
  try {
    cachedCoverageAxes = loadWorkflowV4CoverageAxes();
    return cachedCoverageAxes;
  } catch (error) {
    fail("BLOCKED_COVERAGE_AXIS_CONTRACT", error.message);
  }
}

function lifecycleSets(root) {
  const registryPath = resolve(root, REGISTRY_PATH);
  if (!existsSync(registryPath)) fail("BLOCKED_DOCUMENT_UNIVERSE_REGISTRY", `current lifecycle registry missing: ${REGISTRY_PATH}`);
  const registry = readJson(registryPath, "lifecycle registry");
  if (registry.status !== "ACTIVE_VALIDATOR_CONTRACT") {
    fail("BLOCKED_DOCUMENT_UNIVERSE_REGISTRY", "lifecycle registry must be ACTIVE_VALIDATOR_CONTRACT");
  }
  const get = (field) => {
    const values = requireArray(registry, field, "BLOCKED_DOCUMENT_UNIVERSE_REGISTRY", "lifecycle registry");
    uniqueNonEmptyStrings(values, "BLOCKED_DOCUMENT_UNIVERSE_REGISTRY", `lifecycle registry.${field}`);
    return values;
  };
  return {
    activeCanonical: sortedUnique([...get("active_canonical"), ...get("active_named_prompts")]),
    activeValidators: sortedUnique(get("active_validator_contracts")),
    applicable: sortedUnique([...get("open_remediations"), ...get("activation_required_migrations")]),
    supersededReference: sortedUnique([...get("superseded"), ...get("reference_only")]),
  };
}

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
  for (const field of PREFLIGHT_DEFECT_ARRAYS) requireEmptyArray(artifact, field, "BLOCKED_DOCUMENT_UNIVERSE_DETAIL", label);
  for (const field of ["docs_inventory_count", "classified_count", "active_full_read_count", "active_override_or_addendum_count"]) {
    if (!Number.isInteger(artifact[field]) || artifact[field] < 0) {
      fail("BLOCKED_DOCUMENT_UNIVERSE_DETAIL", `${label}.${field} must be a non-negative integer`);
    }
  }
  if (artifact.classified_count !== artifact.docs_inventory_count) {
    fail("BLOCKED_DOCUMENT_UNIVERSE_DETAIL", "0.0D classified_count must equal docs_inventory_count on PASS");
  }

  const registry = lifecycleSets(root);
  exactStringSet(artifact.active_canonical_paths, registry.activeCanonical, "BLOCKED_DOCUMENT_UNIVERSE_REGISTRY", "0.0D active_canonical_paths");
  exactStringSet(artifact.active_validator_contract_paths, registry.activeValidators, "BLOCKED_DOCUMENT_UNIVERSE_REGISTRY", "0.0D active_validator_contract_paths");
  exactStringSet(artifact.applicable_remediation_or_migration, registry.applicable, "BLOCKED_DOCUMENT_UNIVERSE_REGISTRY", "0.0D applicable_remediation_or_migration");
  exactStringSet(artifact.superseded_or_reference_paths, registry.supersededReference, "BLOCKED_DOCUMENT_UNIVERSE_REGISTRY", "0.0D superseded_or_reference_paths");

  const requiredFullReadPaths = new Set([
    ...registry.activeCanonical,
    ...registry.activeValidators,
    ...registry.applicable,
  ]);
  if (artifact.active_full_read_count !== requiredFullReadPaths.size) {
    fail("BLOCKED_DOCUMENT_UNIVERSE_DETAIL", `0.0D active_full_read_count must exactly equal the registry-bound active/dependency closure (${requiredFullReadPaths.size})`);
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
function validateCoverageAxes(matrix, requiredAxes, label) {
  const value = requireObject({ matrix }, "matrix", "BLOCKED_COVERAGE_AXIS", label, { nonEmpty: true });
  for (const axis of requiredAxes) {
    const row = value[axis];
    if (!isObject(row)) fail("BLOCKED_COVERAGE_AXIS", `${label}.${axis} must be an object`);
    if (!new Set(["searched", "blocked"]).has(row.status)) {
      fail("BLOCKED_COVERAGE_AXIS", `${label}.${axis}.status must be searched or blocked`);
    }
    if (row.status === "blocked" && !nonEmptyText(row.reason)) {
      fail("BLOCKED_COVERAGE_AXIS", `${label}.${axis}.reason required when blocked`);
    }
  }
}

function validateCoverage(run, root) {
  const label = "Stage 0.0C";
  const path = resolveRepoJson(root, run.coverage_discovery_ref, "coverage_discovery_ref");
  const artifact = readJson(path, label);
  if (artifact.stage !== "0.0C" || artifact.status !== "PASS") fail("BLOCKED_COVERAGE_ENVELOPE", "coverage artifact must declare stage=0.0C and status=PASS");
  if (artifact.original_input_accounted !== true) fail("BLOCKED_COVERAGE_ENVELOPE", "0.0C original_input_accounted must be true");
  if (artifact.stage_a_authorized !== true) fail("BLOCKED_COVERAGE_ENVELOPE", "0.0C stage_a_authorized must be true");
  if (artifact.document_universe_manifest_ref !== run.document_universe_manifest_ref) fail("BLOCKED_COVERAGE_BINDING", "0.0C document_universe_manifest_ref must match the card run");
  if (artifact.base_full_blob_sha !== run.base_full_blob_sha) fail("BLOCKED_COVERAGE_BINDING", "0.0C base_full_blob_sha must match the card run");
  for (const field of COVERAGE_ARRAY_FIELDS) requireArray(artifact, field, "BLOCKED_COVERAGE_LEDGER", label);
  const axes = requiredCoverageAxes();
  validateCoverageAxes(artifact.regional_coverage_matrix, axes.regions, "0.0C regional_coverage_matrix");
  validateCoverageAxes(artifact.topic_coverage_matrix, axes.topics, "0.0C topic_coverage_matrix");

  const expansionIds = requireCandidateIds(artifact.source_universe_expansion_ledger, `${label}.source_universe_expansion_ledger`);
  const expansionSet = new Set(expansionIds);
  const requiredIds = new Set();
  for (const field of COVERAGE_CANDIDATE_FIELDS) {
    for (const id of requireCandidateIds(artifact[field], `${label}.${field}`)) requiredIds.add(id);
  }
  for (const id of requiredIds) if (!expansionSet.has(id)) fail("BLOCKED_COVERAGE_LEDGER", `0.0C candidate ${id} is absent from source_universe_expansion_ledger`);

  const terminalRows = artifact.terminal_discovery_disposition_ledger;
  const terminalIds = [];
  terminalRows.forEach((row, index) => {
    const id = candidateId(row);
    if (!id) fail("BLOCKED_COVERAGE_LEDGER", `${label}.terminal_discovery_disposition_ledger[${index}] missing candidate identity`);
    if (!nonEmptyText(row.disposition)) fail("BLOCKED_COVERAGE_LEDGER", `${label}.terminal_discovery_disposition_ledger[${index}].disposition must be non-empty`);
    terminalIds.push(id);
  });
  if (new Set(terminalIds).size !== terminalIds.length) fail("BLOCKED_COVERAGE_LEDGER", "0.0C terminal_discovery_disposition_ledger contains duplicate candidate identities");
  const terminalSet = new Set(terminalIds);
  for (const id of expansionSet) if (!terminalSet.has(id)) fail("BLOCKED_COVERAGE_LEDGER", `0.0C expanded candidate ${id} has no terminal discovery disposition`);
  for (const id of terminalSet) if (!expansionSet.has(id)) fail("BLOCKED_COVERAGE_LEDGER", `0.0C terminal disposition ${id} is not present in source_universe_expansion_ledger`);
  if (artifact.original_input_ledger.length > 0 && expansionSet.size === 0) fail("BLOCKED_COVERAGE_LEDGER", "0.0C cannot account original input with an empty expanded universe ledger");
  return artifact;
}

function validateCompleteness(run, root) {
  const path = resolveRepoJson(root, run.independent_completeness_ref, "independent_completeness_ref");
  const artifact = readJson(path, "Stage 0.7C");
  if (artifact.stage !== "0.7C") fail("BLOCKED_COMPLETENESS_ENVELOPE", "independent completeness stage must be 0.7C");
  if (artifact.status !== "PASS_WITH_DECLARED_RESIDUAL_RISK") fail("BLOCKED_COMPLETENESS_ENVELOPE", "0.7C status must be PASS_WITH_DECLARED_RESIDUAL_RISK");
  if (artifact.completeness_status !== artifact.status) fail("BLOCKED_COMPLETENESS_ENVELOPE", "0.7C completeness_status must exactly equal status");
  for (const field of COMPLETENESS_BOOLEANS) if (artifact[field] !== true) fail("BLOCKED_COMPLETENESS_ENVELOPE", `0.7C ${field} must be true`);
  if (artifact.reviewer_independence !== "SEPARATE_PASS") fail("BLOCKED_COMPLETENESS_ENVELOPE", "0.7C reviewer_independence must be SEPARATE_PASS");
  if (artifact.prompt_0_8_authorized !== true) fail("BLOCKED_COMPLETENESS_ENVELOPE", "0.7C prompt_0_8_authorized must be true");
  for (const field of ["material_exclusions", "known_unknowns", "residual_risks"]) if (!Array.isArray(artifact[field])) fail("BLOCKED_COMPLETENESS_ENVELOPE", `0.7C ${field} must be an array`);
  if (artifact.residual_risks.length === 0 || artifact.residual_risks.some((risk) => !nonEmptyText(risk))) {
    fail("BLOCKED_COMPLETENESS_ENVELOPE", "0.7C PASS_WITH_DECLARED_RESIDUAL_RISK requires at least one concrete non-empty residual risk");
  }
  for (const field of ["run_id", "base_main_commit_sha", "base_full_blob_sha"]) {
    if (artifact[field] !== run[field]) fail("BLOCKED_COMPLETENESS_ENVELOPE", `0.7C ${field} must match the current card run`);
  }
  if (artifact.document_universe_manifest_ref !== run.document_universe_manifest_ref || artifact.coverage_discovery_ref !== run.coverage_discovery_ref) {
    fail("BLOCKED_COMPLETENESS_ENVELOPE", "0.7C governance refs must match the current card run");
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
  if (typeof payload?.stage !== "string" || !payload.stage.trim()) return null;
  const raw = payload.stage.trim().toLowerCase();
  const explicit = new Map([
    ["a", "A"], ["stage_a", "A"], ["0.1", "A"],
    ["b", "B"], ["stage_b", "B"], ["0.2", "B"],
    ["c", "C"], ["stage_c", "C"], ["0.3", "C"],
    ["0.4", "0.4"], ["0.5", "0.5"], ["0.6", "0.6"], ["0.7", "0.7"],
  ]);
  return explicit.get(raw) || null;
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
function validateStageArtifact(path, payload, stage, run, label) {
  for (const field of ["run_id", "base_main_commit_sha", "base_full_blob_sha"]) {
    if (!nonEmptyText(payload[field]) || payload[field] !== run[field]) {
      fail("BLOCKED_STAGE_BASELINE_BINDING", `${label}: ${stage} artifact ${field} must exactly match the current card run`);
    }
  }
  runPythonChecker("validation_scripts/stage_artifact_contract_check.py", [stage, path], label);
  if (stage === "A") runPythonChecker("validation_scripts/stage_lineage_contract_check.py", ["stage_a", path], label);
}

// This working-tree map is only an early structural aid. The CLI always runs the
// authoritative Python binding checker afterward, which reconstructs identities
// from run.base_main_commit_sha/base_full_blob_sha. Update changes are also
// forbidden from mutating source_spec_id below, so a PR cannot self-authorize by
// rewriting identity before the baseline-bound checker runs.
function loadCanonicalSpecMap(root) {
  const path = resolve(root, "data/cards.full.json");
  if (!existsSync(path)) return new Map();
  const payload = readJson(path, "data/cards.full.json");
  if (!Array.isArray(payload?.cards)) fail("BLOCKED_OPERATION_IDENTITY", "data/cards.full.json.cards array required");
  const map = new Map();
  for (const card of payload.cards) if (nonEmptyText(card?.id) && nonEmptyText(card?.source_spec_id)) map.set(card.id.trim(), card.source_spec_id.trim());
  return map;
}
function declaredOperationSpec(operation, label) {
  if (!nonEmptyText(operation?.source_spec_id)) return null;
  return operation.source_spec_id.trim();
}
function operationSpecId(kind, operation, canonicalSpecMap, insertedSpecMap, label) {
  if (kind === "insert") {
    if (!isObject(operation.card) || !nonEmptyText(operation.card.source_spec_id)) fail("BLOCKED_OPERATION_IDENTITY", `${label}.card.source_spec_id is required to bind the formal stage chain`);
    return operation.card.source_spec_id.trim();
  }
  if (kind === "update") {
    if (!nonEmptyText(operation.id)) fail("BLOCKED_OPERATION_IDENTITY", `${label}.id required`);
    for (const [changeIndex, change] of (Array.isArray(operation.changes) ? operation.changes : []).entries()) {
      if (isObject(change) && nonEmptyText(change.path)
        && (change.path === "/source_spec_id" || change.path.startsWith("/source_spec_id/"))) {
        fail("BLOCKED_OPERATION_IDENTITY", `${label}.changes[${changeIndex}] cannot mutate source_spec_id; operation.source_spec_id is binding metadata only`);
      }
    }
    const id = operation.id.trim();
    const canonicalSpec = canonicalSpecMap.get(id) || insertedSpecMap.get(id) || null;
    const declaredSpec = declaredOperationSpec(operation, label);
    if (canonicalSpec && declaredSpec && canonicalSpec !== declaredSpec) fail("BLOCKED_OPERATION_IDENTITY", `${label}.source_spec_id contradicts canonical card ${id}`);
    const specId = declaredSpec || canonicalSpec;
    if (!specId) fail("BLOCKED_OPERATION_IDENTITY", `${label} legacy card ${id} requires operation.source_spec_id to bind the A→0.7 chain`);
    return specId;
  }
  if (kind === "related_add") {
    if (!nonEmptyText(operation.source_id) || !nonEmptyText(operation.target_id)) fail("BLOCKED_OPERATION_IDENTITY", `${label}.source_id and target_id required`);
    const sourceId = operation.source_id.trim();
    const targetId = operation.target_id.trim();
    const sourceSpec = insertedSpecMap.get(sourceId) || canonicalSpecMap.get(sourceId) || null;
    const targetSpec = insertedSpecMap.get(targetId) || canonicalSpecMap.get(targetId) || null;
    const declaredSpec = declaredOperationSpec(operation, label);
    if (declaredSpec) {
      if (!nonEmptyText(operation.identity_card_id) || !new Set([sourceId, targetId]).has(operation.identity_card_id.trim())) {
        fail("BLOCKED_OPERATION_IDENTITY", `${label}.identity_card_id must identify the Related endpoint governed by operation.source_spec_id`);
      }
      const identityId = operation.identity_card_id.trim();
      const mapped = identityId === sourceId ? sourceSpec : targetSpec;
      if (mapped && mapped !== declaredSpec) fail("BLOCKED_OPERATION_IDENTITY", `${label}.source_spec_id contradicts identity_card_id=${identityId}`);
      return declaredSpec;
    }
    const specId = sourceSpec || targetSpec;
    if (!specId) fail("BLOCKED_OPERATION_IDENTITY", `${label} legacy Related endpoints require operation.source_spec_id plus identity_card_id`);
    return specId;
  }
  fail("BLOCKED_OPERATION_IDENTITY", `${label}: unsupported operation kind ${kind}`);
}

function validateRun(run, root = ".") {
  if (!isObject(run)) fail("BLOCKED_V4_HARDENING_INVALID", "card-run object required");
  validateDocumentUniverse(run, root);
  validateCoverage(run, root);
  validateCompleteness(run, root);

  const canonicalSpecMap = loadCanonicalSpecMap(root);
  const workingTreeSpecCardIds = new Map();
  for (const [existingCardId, existingSpecId] of canonicalSpecMap.entries()) {
    if (!workingTreeSpecCardIds.has(existingSpecId)) workingTreeSpecCardIds.set(existingSpecId, new Set());
    workingTreeSpecCardIds.get(existingSpecId).add(existingCardId);
  }
  const insertedSpecMap = new Map();
  const insertedSpecIds = new Set();
  for (const [insertIndex, operation] of (run.operations?.insert || []).entries()) {
    if (!nonEmptyText(operation?.card?.id) || !nonEmptyText(operation?.card?.source_spec_id)) continue;
    const cardId = operation.card.id.trim();
    const specId = operation.card.source_spec_id.trim();
    if (insertedSpecIds.has(specId)) fail("BLOCKED_OPERATION_IDENTITY", `insert[${insertIndex}] reuses source_spec_id=${specId} within the same run`);
    const workingTreeCardIds = workingTreeSpecCardIds.get(specId);
    if (workingTreeCardIds && [...workingTreeCardIds].some((existingCardId) => existingCardId !== cardId)) {
      fail("BLOCKED_OPERATION_IDENTITY", `insert[${insertIndex}] reuses source_spec_id=${specId} already present on a different canonical card`);
    }
    insertedSpecIds.add(specId);
    insertedSpecMap.set(cardId, specId);
  }

  let validatedStageArtifacts = 0;
  let operationCount = 0;
  for (const kind of ["insert", "update", "related_add"]) {
    const operations = run.operations?.[kind];
    if (!Array.isArray(operations)) fail("BLOCKED_V4_HARDENING_INVALID", `operations.${kind} array required`);
    for (const [operationIndex, operation] of operations.entries()) {
      operationCount += 1;
      const operationLabel = `${kind}[${operationIndex}]`;
      if (!Array.isArray(operation?.stage_artifacts) || operation.stage_artifacts.length === 0) fail("BLOCKED_V4_HARDENING_INVALID", `${operationLabel}.stage_artifacts required`);
      const expectedSpecId = operationSpecId(kind, operation, canonicalSpecMap, insertedSpecMap, operationLabel);
      const matchedStages = new Map(REQUIRED_OPERATION_STAGES.map((stage) => [stage, 0]));
      const presentStages = new Set();
      for (const [referenceIndex, reference] of operation.stage_artifacts.entries()) {
        const label = `${operationLabel}.stage_artifacts[${referenceIndex}]`;
        const path = resolveRepoJson(root, reference, label);
        const payload = readJson(path, label);
        const stage = normalizeStage(payload);
        if (!stage || !REQUIRED_OPERATION_STAGES.includes(stage)) {
          fail("BLOCKED_OPERATION_STAGE_SUBSTITUTION", `${label}: explicit ordinary stage is required; declared=${String(payload?.stage ?? "<missing>")}`);
        }
        presentStages.add(stage);
        validateStageArtifact(path, payload, stage, run, label);
        validatedStageArtifacts += 1;
        if (stageCandidateIds(payload, stage).has(expectedSpecId)) matchedStages.set(stage, matchedStages.get(stage) + 1);
      }
      const missingStages = REQUIRED_OPERATION_STAGES.filter((stage) => !presentStages.has(stage));
      if (missingStages.length) fail("BLOCKED_OPERATION_STAGE_CHAIN_MISSING", `${operationLabel} missing mandatory stage artifacts: ${missingStages.join(", ")}`);
      const identityMismatches = REQUIRED_OPERATION_STAGES.filter((stage) => matchedStages.get(stage) === 0);
      if (identityMismatches.length) fail("BLOCKED_OPERATION_STAGE_IDENTITY_MISMATCH", `${operationLabel} stage chain is not bound to source_spec_id=${expectedSpecId} at: ${identityMismatches.join(", ")}`);
    }
  }
  return { stage_artifacts_validated: validatedStageArtifacts, operations_with_complete_stage_chain: operationCount };
}

const searchedMatrix = (axes) => Object.fromEntries(axes.map((axis) => [axis, { status: "searched" }]));
function selfTest() {
  const root = mkdtempSync(join(tmpdir(), "card-run-v4-hardening-"));
  try {
    mkdirSync(join(root, "artifacts"), { recursive: true });
    mkdirSync(join(root, "docs/llm_prompts/v1"), { recursive: true });
    mkdirSync(join(root, "data"), { recursive: true });
    const write = (name, payload) => {
      const path = join(root, "artifacts", name);
      mkdirSync(dirname(path), { recursive: true });
      writeFileSync(path, `${JSON.stringify(payload, null, 2)}\n`);
      return `artifacts/${name}`;
    };
    writeFileSync(join(root, REGISTRY_PATH), `${JSON.stringify({
      status: "ACTIVE_VALIDATOR_CONTRACT",
      active_canonical: ["docs/a.md"],
      active_named_prompts: ["docs/prompt.md"],
      active_validator_contracts: [REGISTRY_PATH],
      open_remediations: [],
      activation_required_migrations: [],
      superseded: ["docs/old.md"],
      reference_only: [],
    }, null, 2)}\n`);
    writeFileSync(join(root, "data/cards.full.json"), `${JSON.stringify({ cards: [] })}\n`);

    const runId = "run-self-test";
    const baseMainCommitSha = "b".repeat(40);
    const baseFullBlobSha = "a".repeat(40);
    const documentUniverseRef = write("0.0d.json", {
      stage: "0.0D", status: "PASS",
      repository_head_sha: baseMainCommitSha,
      canonical_full_blob_sha: baseFullBlobSha,
      docs_inventory_count: 4, classified_count: 4, active_full_read_count: 3,
      active_canonical_paths: ["docs/a.md", "docs/prompt.md"],
      active_validator_contract_paths: [REGISTRY_PATH],
      applicable_remediation_or_migration: [], superseded_or_reference_paths: ["docs/old.md"],
      unclassified_paths: [], unread_active_paths: [], unresolved_dependencies: [], unresolved_conflicts: [],
      unregistered_active_looking_paths: [], unresolved_rule_conflicts: [], incomplete_universe_defects: [],
      active_override_or_addendum_count: 0, stage_a_embedded_news_value_verified: true,
      all_docs_files_read_or_parsed: true, stage_0_0c_authorized: true,
    });
    const axes = requiredCoverageAxes();
    const coverageRef = write("0.0c.json", {
      stage: "0.0C", status: "PASS", original_input_accounted: true, stage_a_authorized: true,
      document_universe_manifest_ref: documentUniverseRef, base_full_blob_sha: baseFullBlobSha,
      original_input_ledger: [{ candidate_id: "CAND_1" }], discovered_missing_candidates: [], baseline_follow_up_candidates: [],
      existing_card_reinforcements: [], existing_card_update_candidates: [], correction_or_reversal_candidates: [], treasure_rescue_candidates: [],
      regional_coverage_matrix: searchedMatrix(axes.regions), topic_coverage_matrix: searchedMatrix(axes.topics),
      searched_but_no_material_event_ledger: [], source_universe_expansion_ledger: [{ candidate_id: "CAND_1", origin: "original_input" }],
      must_report_candidate_ledger: [], known_unknowns: [], residual_coverage_risks: [],
      terminal_discovery_disposition_ledger: [{ candidate_id: "CAND_1", disposition: "stage_a_universe" }],
    });
    const completenessRef = write("0.7c.json", {
      stage: "0.7C", status: "PASS_WITH_DECLARED_RESIDUAL_RISK", completeness_status: "PASS_WITH_DECLARED_RESIDUAL_RISK",
      run_id: runId, base_main_commit_sha: baseMainCommitSha, base_full_blob_sha: baseFullBlobSha,
      document_universe_manifest_ref: documentUniverseRef, coverage_discovery_ref: coverageRef,
      source_universe_accounted: true, regional_search_complete: true, topic_search_complete: true,
      baseline_follow_up_review_complete: true, review_pool_rescue_complete: true, must_report_candidates_accounted: true,
      material_exclusions: [], known_unknowns: [], residual_risks: ["Absolute global completeness beyond the bound universe is not claimed."], reviewer_independence: "SEPARATE_PASS", prompt_0_8_authorized: true,
    });
    const malformedStageA = write("stage-a.json", {
      stage: "A", status: "PASS", run_id: runId, base_main_commit_sha: baseMainCommitSha, base_full_blob_sha: baseFullBlobSha, strict_passed_spec: [{}],
    });
    const revise = write("stage-0.2r.json", { stage: "0.2R", status: "PASS", draft_cards: [{ source_spec_id: "SPEC_1" }] });
    const common = {
      run_id: runId,
      base_main_commit_sha: baseMainCommitSha, base_full_blob_sha: baseFullBlobSha,
      document_universe_manifest_ref: documentUniverseRef, coverage_discovery_ref: coverageRef, independent_completeness_ref: completenessRef,
    };

    let stageABlocked = false;
    try { validateRun({ ...common, operations: { insert: [{ card: { id: "CARD_1", source_spec_id: "SPEC_1" }, stage_artifacts: [malformedStageA] }], update: [], related_add: [] } }, root); }
    catch (error) { stageABlocked = error instanceof ValidationError && error.code === "BLOCKED_STAGE_CHAIN_CONTRACT"; }
    if (!stageABlocked) throw new Error("self-test failed to reject malformed Stage A artifact");

    let reviseBlocked = false;
    try { validateRun({ ...common, operations: { insert: [{ card: { id: "CARD_1", source_spec_id: "SPEC_1" }, stage_artifacts: [revise] }], update: [], related_add: [] } }, root); }
    catch (error) { reviseBlocked = error instanceof ValidationError && error.code === "BLOCKED_OPERATION_STAGE_SUBSTITUTION"; }
    if (!reviseBlocked) throw new Error("self-test failed to reject revise-stage substitution");

    const missingStage = write("stage-missing.json", { status: "PASS", run_id: runId, base_main_commit_sha: baseMainCommitSha, base_full_blob_sha: baseFullBlobSha, draft_cards: [{ source_spec_id: "SPEC_1" }] });
    let missingStageBlocked = false;
    try { validateRun({ ...common, operations: { insert: [{ card: { id: "CARD_1", source_spec_id: "SPEC_1" }, stage_artifacts: [missingStage] }], update: [], related_add: [] } }, root); }
    catch (error) { missingStageBlocked = error instanceof ValidationError && error.code === "BLOCKED_OPERATION_STAGE_SUBSTITUTION"; }
    if (!missingStageBlocked) throw new Error("self-test failed to reject stage-less bucket inference");

    const duplicateSpecRun = { ...common, operations: { insert: [
      { card: { id: "CARD_1", source_spec_id: "SPEC_DUP" }, stage_artifacts: [malformedStageA] },
      { card: { id: "CARD_2", source_spec_id: "SPEC_DUP" }, stage_artifacts: [malformedStageA] },
    ], update: [], related_add: [] } };
    let duplicateSpecBlocked = false;
    try { validateRun(duplicateSpecRun, root); }
    catch (error) { duplicateSpecBlocked = error instanceof ValidationError && error.code === "BLOCKED_OPERATION_IDENTITY"; }
    if (!duplicateSpecBlocked) throw new Error("self-test failed to reject duplicate insert source_spec_id");

    const badCompleteness = readJson(join(root, completenessRef), "completeness");
    badCompleteness.residual_risks = [];
    writeFileSync(join(root, completenessRef), `${JSON.stringify(badCompleteness, null, 2)}\n`);
    let residualRiskBlocked = false;
    try { validateRun({ ...common, operations: { insert: [], update: [], related_add: [] } }, root); }
    catch (error) { residualRiskBlocked = error instanceof ValidationError && error.code === "BLOCKED_COMPLETENESS_ENVELOPE"; }
    if (!residualRiskBlocked) throw new Error("self-test failed to reject empty declared residual-risk list");
    badCompleteness.residual_risks = ["Absolute global completeness beyond the bound universe is not claimed."];
    writeFileSync(join(root, completenessRef), `${JSON.stringify(badCompleteness, null, 2)}\n`);

    const badCoverage = readJson(join(root, coverageRef), "coverage");
    delete badCoverage.regional_coverage_matrix.korea;
    writeFileSync(join(root, coverageRef), `${JSON.stringify(badCoverage, null, 2)}\n`);
    let coverageBlocked = false;
    try { validateRun({ ...common, operations: { insert: [], update: [], related_add: [] } }, root); }
    catch (error) { coverageBlocked = error instanceof ValidationError && error.code === "BLOCKED_COVERAGE_AXIS"; }
    if (!coverageBlocked) throw new Error("self-test failed to reject missing 0.0C coverage axis");

    badCoverage.regional_coverage_matrix.korea = { status: "searched" };
    writeFileSync(join(root, coverageRef), `${JSON.stringify(badCoverage, null, 2)}\n`);
    const badPreflight = readJson(join(root, documentUniverseRef), "preflight");
    badPreflight.active_canonical_paths = [];
    writeFileSync(join(root, documentUniverseRef), `${JSON.stringify(badPreflight, null, 2)}\n`);
    let registryBlocked = false;
    try { validateRun({ ...common, operations: { insert: [], update: [], related_add: [] } }, root); }
    catch (error) { registryBlocked = error instanceof ValidationError && error.code === "BLOCKED_DOCUMENT_UNIVERSE_REGISTRY"; }
    if (!registryBlocked) throw new Error("self-test failed to bind 0.0D authority set to registry");

    console.log("PASS: formal V4 card-run hardening binds explicit A→0.7 stages, exact run/baseline envelope, non-empty 0.7C residual risk, 0.0D registry closure, shared 0.0C axes, immutable candidate identity, and unique insert source identity");
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
  // The Python binding checker is the authoritative second layer for declared-
  // baseline identity reconstruction and semantic Related-edge reconciliation.
  // Running it here makes this JS production gate fail-closed even when invoked
  // outside the GitHub workflow that also calls the checker explicitly.
  runPythonChecker("validation_scripts/card_run_v4_binding_hardening.py", ["--run", runPath], "authoritative baseline/Related binding");
  console.log(JSON.stringify({ status: "PASS", ...result, authoritative_binding: "PASS" }, null, 2));
  console.log(`PASS: formal V4 hardening; stage artifacts validated=${result.stage_artifacts_validated}; operations=${result.operations_with_complete_stage_chain}; baseline/Related binding=PASS`);
} catch (error) {
  if (error instanceof ValidationError) { console.error(`FAIL [${error.code}]: ${error.message}`); process.exit(1); }
  console.error(`FAIL [BLOCKED_V4_HARDENING_INTERNAL]: ${error?.message || String(error)}`);
  process.exit(1);
}
