#!/usr/bin/env node
import { readFileSync } from "node:fs";
import { isDeepStrictEqual } from "node:util";

class ValidationError extends Error {
  constructor(code, message) { super(message); this.code = code; }
}
const fail = (code, message) => { throw new ValidationError(code, message); };
const readJson = (path, label) => {
  try { return JSON.parse(readFileSync(path, "utf8").replace(/^\uFEFF/, "")); }
  catch (error) { fail("BLOCKED_MANUAL_DIRECT_ADD_V4_HARDENING", `${label}: ${error.message}`); }
};
const same = (a, b) => isDeepStrictEqual(a, b);
const isObject = (value) => Boolean(value) && typeof value === "object" && !Array.isArray(value);
const finiteNumber = (value) => typeof value === "number" && Number.isFinite(value);
const cardMap = (doc, label) => {
  if (!Array.isArray(doc?.cards)) fail("BLOCKED_MANUAL_DIRECT_ADD_V4_HARDENING", `${label}.cards must be an array`);
  return new Map(doc.cards.map((card) => [card.id, card]));
};
const MIGRATION_MUTABLE_FIELDS = new Set(["id", "date", "region"]);
const RELATED_CONTAINERS = ["related", "related_ids", "related_lineage"];
const FORMAL_RUN_FIELDS = new Set([
  "stage_a_validity_status",
  "stage_b_validity_status",
  "stage_c_validity_status",
  "final_qc_status",
  "merge_status",
  "pipeline_lineage",
  "publish_ready",
  "github_merge_ready",
  "production_verified",
]);
const GOVERNED_PUBLISH_STATES = new Set(["publish_ready", "github_merge_ready", "production_verified"]);
const BREAKDOWN_MAX = {
  market_structure_competition: 25,
  supply_demand_price_utilisation: 25,
  technology_performance_safety: 20,
  cashflow_asset_value: 10,
  law_policy_market_access: 10,
  systemic_scale: 5,
  persistence_irreversibility: 3,
  decision_urgency_actionability: 2,
};
const TECHNOLOGY_EVIDENCE_CAPS = {
  not_applicable: 0,
  company_target_or_unsupported_claim: 4,
  laboratory_unvalidated: 7,
  pilot_precommercial: 11,
  independent_test_or_customer_qualification: 15,
  commercial_scale_or_long_duration_field: 20,
  material_failure_evidence: 20,
};
const POLICY_STAGE_TOTAL_CAPS = new Map([[0, 39], [1, 54], [2, 69]]);
const NOVELTY_TOTAL_CAPS = new Map([
  ["none", null],
  ["repeated_announcement_no_new_fact", 39],
  ["routine_progression_no_material_uncertainty", 54],
  ["company_target_without_validation_or_effect", 54],
  ["unsupported_political_rhetoric", 39],
]);
const RFC3339 = /^(\d{4})-(\d{2})-(\d{2})T(\d{2}):(\d{2}):(\d{2})(?:\.\d+)?(?:Z|[+-](\d{2}):(\d{2}))$/;

function changedTopLevelFields(before, after) {
  const keys = new Set([...Object.keys(before || {}), ...Object.keys(after || {})]);
  return [...keys].filter((key) => !same(before?.[key], after?.[key])).sort();
}

function validateStrictRfc3339(value) {
  if (typeof value !== "string") fail("BLOCKED_MANUAL_DIRECT_ADD_TIMESTAMP", "output_updated must be an RFC3339 string");
  const match = value.match(RFC3339);
  if (!match) fail("BLOCKED_MANUAL_DIRECT_ADD_TIMESTAMP", `output_updated must be RFC3339 — ${value}`);
  const [, ys, ms, ds, hs, mins, ss, offsetHs, offsetMins] = match;
  const year = Number(ys), month = Number(ms), day = Number(ds);
  const hour = Number(hs), minute = Number(mins), second = Number(ss);
  if (hour > 23 || minute > 59 || second > 59 || Number(offsetHs || 0) > 23 || Number(offsetMins || 0) > 59) {
    fail("BLOCKED_MANUAL_DIRECT_ADD_TIMESTAMP", `output_updated has an invalid time/offset — ${value}`);
  }
  const probe = new Date(Date.UTC(year, month - 1, day));
  if (probe.getUTCFullYear() !== year || probe.getUTCMonth() !== month - 1 || probe.getUTCDate() !== day) {
    fail("BLOCKED_MANUAL_DIRECT_ADD_TIMESTAMP", `output_updated contains a nonexistent calendar date — ${value}`);
  }
  if (Number.isNaN(Date.parse(value))) fail("BLOCKED_MANUAL_DIRECT_ADD_TIMESTAMP", `output_updated is not parseable — ${value}`);
}

function validateEditorialHardCaps(manifest) {
  const additions = manifest?.editorial_attestation?.additions;
  if (!Array.isArray(additions)) {
    fail("BLOCKED_MANUAL_DIRECT_ADD_SCORE_CAP", "editorial_attestation.additions must be an array");
  }
  for (const [index, attestation] of additions.entries()) {
    if (!isObject(attestation)) fail("BLOCKED_MANUAL_DIRECT_ADD_SCORE_CAP", `addition[${index}] must be an object`);
    const id = typeof attestation.id === "string" && attestation.id.trim() ? attestation.id.trim() : `addition[${index}]`;
    const breakdown = attestation.decision_value_breakdown;
    if (!isObject(breakdown)) fail("BLOCKED_MANUAL_DIRECT_ADD_SCORE_CAP", `${id}: decision_value_breakdown is required`);
    const keys = Object.keys(breakdown).sort();
    const requiredKeys = Object.keys(BREAKDOWN_MAX).sort();
    if (!same(keys, requiredKeys)) {
      fail("BLOCKED_MANUAL_DIRECT_ADD_SCORE_CAP", `${id}: decision_value_breakdown must contain exactly the V4 eight components`);
    }
    let sum = 0;
    for (const [field, maximum] of Object.entries(BREAKDOWN_MAX)) {
      const value = breakdown[field];
      if (!finiteNumber(value) || value < 0 || value > maximum) {
        fail("BLOCKED_MANUAL_DIRECT_ADD_SCORE_CAP", `${id}: ${field} must be finite 0..${maximum}`);
      }
      sum += value;
    }
    if (!Number.isInteger(attestation.decision_news_value_score) || attestation.decision_news_value_score < 0 || attestation.decision_news_value_score > 100) {
      fail("BLOCKED_MANUAL_DIRECT_ADD_SCORE_CAP", `${id}: decision_news_value_score must be integer 0..100`);
    }
    if (sum !== attestation.decision_news_value_score) {
      fail("BLOCKED_MANUAL_DIRECT_ADD_SCORE_CAP", `${id}: breakdown sum ${sum} != total ${attestation.decision_news_value_score}`);
    }

    const techLevel = attestation.technology_evidence_level;
    if (!Object.prototype.hasOwnProperty.call(TECHNOLOGY_EVIDENCE_CAPS, techLevel)) {
      fail("BLOCKED_MANUAL_DIRECT_ADD_SCORE_CAP", `${id}: invalid technology_evidence_level`);
    }
    const techCap = TECHNOLOGY_EVIDENCE_CAPS[techLevel];
    if (breakdown.technology_performance_safety > techCap) {
      fail("BLOCKED_MANUAL_DIRECT_ADD_SCORE_CAP", `${id}: technology score ${breakdown.technology_performance_safety} exceeds ${techLevel} cap ${techCap}/20`);
    }

    const anchors = Array.isArray(attestation.anchor_classes) ? attestation.anchor_classes : [];
    const policyStage = attestation.policy_stage;
    if (policyStage !== null && (!Number.isInteger(policyStage) || policyStage < 0 || policyStage > 6)) {
      fail("BLOCKED_MANUAL_DIRECT_ADD_SCORE_CAP", `${id}: policy_stage must be null or integer 0..6`);
    }
    if (anchors.includes("policy_regulatory_anchor") && policyStage === null) {
      fail("BLOCKED_MANUAL_DIRECT_ADD_SCORE_CAP", `${id}: policy_regulatory_anchor requires policy_stage`);
    }
    if (POLICY_STAGE_TOTAL_CAPS.has(policyStage) && attestation.decision_news_value_score > POLICY_STAGE_TOTAL_CAPS.get(policyStage)) {
      fail("BLOCKED_MANUAL_DIRECT_ADD_SCORE_CAP", `${id}: total score exceeds policy_stage=${policyStage} cap ${POLICY_STAGE_TOTAL_CAPS.get(policyStage)}`);
    }

    const noveltyBasis = attestation.novelty_cap_basis;
    if (!NOVELTY_TOTAL_CAPS.has(noveltyBasis)) {
      fail("BLOCKED_MANUAL_DIRECT_ADD_SCORE_CAP", `${id}: invalid novelty_cap_basis`);
    }
    const noveltyCap = NOVELTY_TOTAL_CAPS.get(noveltyBasis);
    if (noveltyCap !== null && attestation.decision_news_value_score > noveltyCap) {
      fail("BLOCKED_MANUAL_DIRECT_ADD_SCORE_CAP", `${id}: total score exceeds novelty_cap_basis=${noveltyBasis} cap ${noveltyCap}`);
    }

    if (typeof attestation.denominator_gap !== "boolean") {
      fail("BLOCKED_MANUAL_DIRECT_ADD_SCORE_CAP", `${id}: denominator_gap must be boolean`);
    }
    if (attestation.denominator_gap === true && breakdown.systemic_scale > 2) {
      fail("BLOCKED_MANUAL_DIRECT_ADD_SCORE_CAP", `${id}: denominator_gap=true caps systemic_scale at 2/5`);
    }
    if (attestation.denominator_gap === false) {
      if (typeof attestation.systemic_scale_denominator !== "string" || !attestation.systemic_scale_denominator.trim()) {
        fail("BLOCKED_MANUAL_DIRECT_ADD_SCORE_CAP", `${id}: denominator_gap=false requires a defensible systemic_scale_denominator`);
      }
    }

    if (attestation.selection_route === "execution_anchor_route") {
      if (!anchors.includes("execution_event_anchor")) {
        fail("BLOCKED_MANUAL_DIRECT_ADD_ROUTE", `${id}: execution_anchor_route requires execution_event_anchor`);
      }
      if (attestation.structural_non_execution_reason !== null || attestation.why_execution_event_not_required !== null) {
        fail("BLOCKED_MANUAL_DIRECT_ADD_ROUTE", `${id}: execution_anchor_route requires structural-only reason fields to be null`);
      }
    } else if (attestation.selection_route === "structural_non_execution_route") {
      if (anchors.includes("execution_event_anchor")) {
        fail("BLOCKED_MANUAL_DIRECT_ADD_ROUTE", `${id}: structural_non_execution_route cannot carry execution_event_anchor`);
      }
      if (typeof attestation.structural_non_execution_reason !== "string" || !attestation.structural_non_execution_reason.trim()
        || typeof attestation.why_execution_event_not_required !== "string" || !attestation.why_execution_event_not_required.trim()) {
        fail("BLOCKED_MANUAL_DIRECT_ADD_ROUTE", `${id}: structural route requires both structural-only reason fields`);
      }
    } else {
      fail("BLOCKED_MANUAL_DIRECT_ADD_ROUTE", `${id}: invalid selection_route`);
    }
  }
}

function validateMigrationContent(manifest, baseMap, fullMap) {
  for (const migration of manifest.operations?.id_migration || []) {
    const before = baseMap.get(migration.old_id);
    const after = fullMap.get(migration.new_id);
    if (!before || !after) fail("BLOCKED_MANUAL_DIRECT_ADD_MIGRATION_SCOPE", `migration card missing ${migration.old_id} → ${migration.new_id}`);
    const changed = changedTopLevelFields(before, after);
    const forbidden = changed.filter((field) => !MIGRATION_MUTABLE_FIELDS.has(field));
    if (forbidden.length) {
      fail(
        "BLOCKED_MANUAL_DIRECT_ADD_MIGRATION_SCOPE",
        `${migration.old_id} → ${migration.new_id}: migration may change only id/date/region; forbidden=[${forbidden.join(",")}]`,
      );
    }
  }
}

function fabricatedFormalFields(card) {
  const fields = [...FORMAL_RUN_FIELDS].filter((field) => Object.prototype.hasOwnProperty.call(card, field));
  if (GOVERNED_PUBLISH_STATES.has(card?.state)) fields.push(`state=${card.state}`);
  return fields;
}

function validateAddedCards(manifest, baseMap, fullMap) {
  for (const id of manifest.operations?.add || []) {
    if (baseMap.has(id) || !fullMap.has(id)) fail("BLOCKED_MANUAL_DIRECT_ADD_V4_HARDENING", `invalid added card ${id}`);
    const card = fullMap.get(id);
    if (Object.prototype.hasOwnProperty.call(card, "related")) {
      if (!Array.isArray(card.related) || card.related.length !== 0) {
        fail("BLOCKED_MANUAL_DIRECT_ADD_RELATED", `${id}: direct-added card must leave related empty; establish lineage through formal Related review`);
      }
    }
    if (Object.prototype.hasOwnProperty.call(card, "related_ids")) {
      if (!Array.isArray(card.related_ids) || card.related_ids.length !== 0) {
        fail("BLOCKED_MANUAL_DIRECT_ADD_RELATED", `${id}: direct-added card must leave related_ids empty`);
      }
    }
    if (Object.prototype.hasOwnProperty.call(card, "related_lineage")) {
      const lineage = card.related_lineage;
      if (lineage !== null && (!lineage || typeof lineage !== "object" || Array.isArray(lineage)
        || (Array.isArray(lineage.related_ids) && lineage.related_ids.length !== 0))) {
        fail("BLOCKED_MANUAL_DIRECT_ADD_RELATED", `${id}: direct-added related_lineage may not establish targets`);
      }
    }
    const fabricated = fabricatedFormalFields(card);
    if (fabricated.length) {
      fail(
        "BLOCKED_MANUAL_DIRECT_ADD_FORMAL_PROVENANCE",
        `${id}: direct-add cannot claim formal-run state/provenance fields [${fabricated.join(",")}]`,
      );
    }
  }
}

function validateUpdatedCards(manifest, baseMap, fullMap) {
  for (const id of manifest.operations?.update || []) {
    const before = baseMap.get(id);
    const after = fullMap.get(id);
    if (!before || !after) fail("BLOCKED_MANUAL_DIRECT_ADD_V4_HARDENING", `update card missing ${id}`);
    for (const field of RELATED_CONTAINERS) {
      if (!same(before?.[field], after?.[field])) {
        fail("BLOCKED_MANUAL_DIRECT_ADD_RELATED", `${id}: direct update cannot change ${field}; use formal Related review`);
      }
    }
    const changedFormal = [...FORMAL_RUN_FIELDS].filter((field) => !same(before?.[field], after?.[field]));
    if (!same(before?.state, after?.state) && (GOVERNED_PUBLISH_STATES.has(before?.state) || GOVERNED_PUBLISH_STATES.has(after?.state))) {
      changedFormal.push("state");
    }
    if (changedFormal.length) {
      fail(
        "BLOCKED_MANUAL_DIRECT_ADD_FORMAL_PROVENANCE",
        `${id}: direct update cannot add/change formal publication state [${changedFormal.join(",")}]`,
      );
    }
  }
}

function validate(manifest, base, full) {
  if (manifest?.schema !== "manual_direct_add_v2") {
    fail("BLOCKED_MANUAL_DIRECT_ADD_V4_HARDENING", "active hardening accepts manual_direct_add_v2 only");
  }
  if (manifest.formal_full_run_claimed !== false) {
    fail("BLOCKED_MANUAL_DIRECT_ADD_FORMAL_PROVENANCE", "manual direct-add must declare formal_full_run_claimed=false");
  }
  validateStrictRfc3339(manifest.output_updated);
  validateEditorialHardCaps(manifest);
  const baseMap = cardMap(base, "base");
  const fullMap = cardMap(full, "full");
  validateMigrationContent(manifest, baseMap, fullMap);
  validateAddedCards(manifest, baseMap, fullMap);
  validateUpdatedCards(manifest, baseMap, fullMap);
  return {
    migrations_checked: (manifest.operations?.id_migration || []).length,
    additions_checked: (manifest.operations?.add || []).length,
    updates_checked: (manifest.operations?.update || []).length,
    editorial_score_caps_checked: (manifest.editorial_attestation?.additions || []).length,
  };
}

const goodAttestation = () => ({
  id: "2026-01-02_KR_01",
  execution_credibility_gate: "PASS",
  independent_cardability_gate: "PASS",
  anchor_classes: ["data_financial_anchor"],
  selection_route: "structural_non_execution_route",
  decision_news_value_score: 60,
  decision_value_breakdown: {
    market_structure_competition: 20,
    supply_demand_price_utilisation: 20,
    technology_performance_safety: 0,
    cashflow_asset_value: 8,
    law_policy_market_access: 5,
    systemic_scale: 2,
    persistence_irreversibility: 3,
    decision_urgency_actionability: 2,
  },
  decision_value_classification: "material_industry_signal",
  publication_urgency: "near_term",
  technology_evidence_level: "not_applicable",
  policy_stage: null,
  novelty_cap_basis: "none",
  systemic_scale_denominator: "named market/program denominator",
  denominator_gap: false,
  prior_state: "old",
  new_verified_fact: "new",
  changed_judgment: "changed",
  evidence_review_summary: "official evidence reviewed",
  next_confirmation_points: ["next metric"],
  inclusion_decision: "standard_include",
  owner_override_reason: null,
  structural_non_execution_reason: "material data change",
  why_execution_event_not_required: "decision-useful without transaction",
});

function selfTest() {
  const base = { cards: [
    { id: "2026-01-01_KR_01", date: "2026-01-01", region: "KR", title: "A", urls: ["https://a.example"], related: [], related_ids: [], related_lineage: { relation_type: "new_unrelated_event", related_ids: [] } },
    { id: "2026-01-03_KR_01", date: "2026-01-03", region: "KR", title: "U", urls: ["https://u.example"], related: [], related_ids: [], related_lineage: { relation_type: "new_unrelated_event", related_ids: [] } },
  ] };
  const manifest = {
    schema: "manual_direct_add_v2",
    formal_full_run_claimed: false,
    output_updated: "2026-08-29T22:30:00+09:00",
    operations: {
      add: ["2026-01-02_KR_01"],
      update: ["2026-01-03_KR_01"],
      id_migration: [{ old_id: "2026-01-01_KR_01", new_id: "2025-12-31_KR_01" }],
    },
    editorial_attestation: { additions: [goodAttestation()], updates: [] },
  };
  const good = { cards: [
    { id: "2025-12-31_KR_01", date: "2025-12-31", region: "KR", title: "A", urls: ["https://a.example"], related: [], related_ids: [], related_lineage: { relation_type: "new_unrelated_event", related_ids: [] } },
    { id: "2026-01-03_KR_01", date: "2026-01-03", region: "KR", title: "U corrected", urls: ["https://u.example"], related: [], related_ids: [], related_lineage: { relation_type: "new_unrelated_event", related_ids: [] } },
    { id: "2026-01-02_KR_01", date: "2026-01-02", region: "KR", title: "B", related: [], related_ids: [] },
  ] };
  validate(manifest, base, good);

  const contentSwap = structuredClone(good);
  contentSwap.cards[0].title = "Different event";
  let migrationBlocked = false;
  try { validate(manifest, base, contentSwap); }
  catch (error) { migrationBlocked = error instanceof ValidationError && error.code === "BLOCKED_MANUAL_DIRECT_ADD_MIGRATION_SCOPE"; }
  if (!migrationBlocked) throw new Error("self-test failed to reject migration content mutation");

  const withRelated = structuredClone(good);
  withRelated.cards[2].related = ["2025-12-31_KR_01"];
  let relatedBlocked = false;
  try { validate(manifest, base, withRelated); }
  catch (error) { relatedBlocked = error instanceof ValidationError && error.code === "BLOCKED_MANUAL_DIRECT_ADD_RELATED"; }
  if (!relatedBlocked) throw new Error("self-test failed to reject direct-add Related edge");

  const updateLineage = structuredClone(good);
  updateLineage.cards[1].related_lineage = { relation_type: "direct_follow_up", related_ids: ["2026-01-02_KR_01"] };
  let updateRelatedBlocked = false;
  try { validate(manifest, base, updateLineage); }
  catch (error) { updateRelatedBlocked = error instanceof ValidationError && error.code === "BLOCKED_MANUAL_DIRECT_ADD_RELATED"; }
  if (!updateRelatedBlocked) throw new Error("self-test failed to reject direct update Related mutation");

  const withFormalState = structuredClone(good);
  withFormalState.cards[2].publish_ready = true;
  let provenanceBlocked = false;
  try { validate(manifest, base, withFormalState); }
  catch (error) { provenanceBlocked = error instanceof ValidationError && error.code === "BLOCKED_MANUAL_DIRECT_ADD_FORMAL_PROVENANCE"; }
  if (!provenanceBlocked) throw new Error("self-test failed to reject fabricated publication state");

  const withStateAlias = structuredClone(good);
  withStateAlias.cards[2].state = "github_merge_ready";
  let stateAliasBlocked = false;
  try { validate(manifest, base, withStateAlias); }
  catch (error) { stateAliasBlocked = error instanceof ValidationError && error.code === "BLOCKED_MANUAL_DIRECT_ADD_FORMAL_PROVENANCE"; }
  if (!stateAliasBlocked) throw new Error("self-test failed to reject governed publication state alias");

  const invalidDate = structuredClone(manifest);
  invalidDate.output_updated = "2026-02-30T12:00:00Z";
  let invalidDateBlocked = false;
  try { validate(invalidDate, base, good); }
  catch (error) { invalidDateBlocked = error instanceof ValidationError && error.code === "BLOCKED_MANUAL_DIRECT_ADD_TIMESTAMP"; }
  if (!invalidDateBlocked) throw new Error("self-test failed to reject nonexistent calendar date");

  const inflatedTech = structuredClone(manifest);
  inflatedTech.editorial_attestation.additions[0].technology_evidence_level = "company_target_or_unsupported_claim";
  inflatedTech.editorial_attestation.additions[0].decision_value_breakdown.technology_performance_safety = 10;
  inflatedTech.editorial_attestation.additions[0].decision_value_breakdown.market_structure_competition = 10;
  let techBlocked = false;
  try { validate(inflatedTech, base, good); }
  catch (error) { techBlocked = error instanceof ValidationError && error.code === "BLOCKED_MANUAL_DIRECT_ADD_SCORE_CAP"; }
  if (!techBlocked) throw new Error("self-test failed to enforce technology evidence cap");

  const denominatorGap = structuredClone(manifest);
  denominatorGap.editorial_attestation.additions[0].denominator_gap = true;
  denominatorGap.editorial_attestation.additions[0].systemic_scale_denominator = null;
  denominatorGap.editorial_attestation.additions[0].decision_value_breakdown.systemic_scale = 5;
  denominatorGap.editorial_attestation.additions[0].decision_value_breakdown.market_structure_competition = 17;
  let denominatorBlocked = false;
  try { validate(denominatorGap, base, good); }
  catch (error) { denominatorBlocked = error instanceof ValidationError && error.code === "BLOCKED_MANUAL_DIRECT_ADD_SCORE_CAP"; }
  if (!denominatorBlocked) throw new Error("self-test failed to enforce systemic denominator cap");

  const contradictoryExecution = structuredClone(manifest);
  const execution = contradictoryExecution.editorial_attestation.additions[0];
  execution.selection_route = "execution_anchor_route";
  execution.anchor_classes = ["execution_event_anchor"];
  let routeBlocked = false;
  try { validate(contradictoryExecution, base, good); }
  catch (error) { routeBlocked = error instanceof ValidationError && error.code === "BLOCKED_MANUAL_DIRECT_ADD_ROUTE"; }
  if (!routeBlocked) throw new Error("self-test failed to reject structural-only reasons on execution route");

  console.log("PASS: manual direct-add V4 hardening closes score-cap, route, migration, Related, publication-state, and timestamp bypasses");
}

const args = process.argv.slice(2);
const arg = (name) => { const index = args.indexOf(name); return index >= 0 ? args[index + 1] : null; };
try {
  if (args.includes("--self-test")) { selfTest(); process.exit(0); }
  const manifestPath = arg("--manifest");
  const basePath = arg("--base");
  const fullPath = arg("--full");
  if (!manifestPath || !basePath || !fullPath) fail("INVALID_ARGUMENT", "--manifest --base --full required");
  const result = validate(readJson(manifestPath, "manifest"), readJson(basePath, "base"), readJson(fullPath, "full"));
  console.log(JSON.stringify({ status: "PASS", ...result }, null, 2));
  console.log(`PASS: manual direct-add V4 hardening; add=${result.additions_checked}; update=${result.updates_checked}; migration=${result.migrations_checked}; score_caps=${result.editorial_score_caps_checked}`);
} catch (error) {
  if (error instanceof ValidationError) { console.error(`FAIL [${error.code}]: ${error.message}`); process.exit(1); }
  throw error;
}
