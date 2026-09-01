#!/usr/bin/env node
import {
  cpSync,
  mkdtempSync,
  mkdirSync,
  readFileSync,
  writeFileSync,
} from "node:fs";
import { tmpdir } from "node:os";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";
import { spawnSync } from "node:child_process";

const sourceScript = join(dirname(fileURLToPath(import.meta.url)), "apply_card_run.mjs");
const temp = mkdtempSync(join(tmpdir(), "card-run-engine-"));
const run = (command, args, options = {}) => spawnSync(command, args, {
  cwd: temp,
  encoding: "utf8",
  ...options,
});
const mustPass = (result, label) => {
  if (result.status !== 0) throw new Error(`${label} expected PASS\n${result.stdout}\n${result.stderr}`);
};
const mustFail = (result, code, label) => {
  if (result.status === 0 || !result.stderr.includes(code)) {
    throw new Error(`${label} expected ${code}\n${result.stdout}\n${result.stderr}`);
  }
};

mkdirSync(join(temp, "data"), { recursive: true });
mkdirSync(join(temp, "public/data"), { recursive: true });
mkdirSync(join(temp, "runs/2026-08-02"), { recursive: true });
mkdirSync(join(temp, "scripts"), { recursive: true });
cpSync(sourceScript, join(temp, "scripts/apply_card_run.mjs"));

const baseline = {
  schema: "cards_full_test",
  total: 2,
  updated: "2026-08-01T00:00:00+09:00",
  cards: [
    {
      id: "2026-08-01_KR_01",
      date: "2026-08-01",
      title: "old title",
      related: ["LEGACY_DANGLING"],
      related_lineage: {
        relation_type: "new_unrelated_event",
        related_ids: [],
        reason: "기존 독립 판정"
      }
    },
    {
      id: "2026-07-31_US_01",
      date: "2026-07-31",
      title: "target",
      related: []
    }
  ]
};
const fullPath = join(temp, "data/cards.full.json");
const publicPath = join(temp, "public/data/cards.json");
const runPath = join(temp, "runs/2026-08-02/card-run.json");
const reportPath = join(temp, "runs/2026-08-02/apply-report.json");
const baselineBytes = Buffer.from(`${JSON.stringify(baseline, null, 2).replace(/\n/g, "\r\n")}\r\n`);
writeFileSync(fullPath, baselineBytes);
writeFileSync(publicPath, baselineBytes);

mustPass(run("git", ["init", "-q", "-b", "main"]), "git init");
mustPass(run("git", ["config", "user.email", "test@example.com"]), "git email");
mustPass(run("git", ["config", "user.name", "test"]), "git name");
mustPass(run("git", ["add", "."]), "git add");
mustPass(run("git", ["commit", "-qm", "baseline"]), "git commit");
const mainSha = run("git", ["rev-parse", "HEAD"]).stdout.trim();
const fullBlobSha = run("git", ["rev-parse", "HEAD:data/cards.full.json"]).stdout.trim();
mustPass(run("git", ["checkout", "-qb", "data-run"]), "git branch");

mkdirSync(join(temp, "artifacts/audit"), { recursive: true });
const writeArtifact = (path, payload) => writeFileSync(join(temp, path), `${JSON.stringify(payload, null, 2)}\n`);
writeArtifact("artifacts/stage-0.0d.json", {
  stage: "0.0D",
  status: "PASS",
  repository_head_sha: mainSha,
  canonical_full_blob_sha: fullBlobSha,
  unresolved_rule_conflicts: [],
  incomplete_universe_defects: [],
  all_docs_files_read_or_parsed: true,
  stage_0_0c_authorized: true
});
writeArtifact("artifacts/stage-0.0c.json", {
  stage: "0.0C",
  status: "PASS",
  document_universe_manifest_ref: "artifacts/stage-0.0d.json",
  base_full_blob_sha: fullBlobSha,
  original_input_accounted: true,
  stage_a_authorized: true
});
writeArtifact("artifacts/stage-0.7c.json", {
  stage: "0.7C",
  status: "PASS_WITH_DECLARED_RESIDUAL_RISK",
  source_universe_accounted: true,
  regional_search_complete: true,
  topic_search_complete: true,
  baseline_follow_up_review_complete: true,
  review_pool_rescue_complete: true,
  must_report_candidates_accounted: true,
  reviewer_independence: "SEPARATE_PASS",
  prompt_0_8_authorized: true
});
writeArtifact("artifacts/audit/test-run.json", { schema: "run_audit_v1", status: "PASS" });
writeArtifact("artifacts/stage-c.json", { stage: "C", status: "PASS" });
writeArtifact("artifacts/final-qc.json", { stage: "0.7", status: "PASS" });

const validRun = {
  schema: "card_run_v1",
  run_id: "2026-08-02-test",
  base_main_commit_sha: mainSha,
  base_full_blob_sha: fullBlobSha,
  expected_before: 2,
  output_updated: "2026-08-02T08:00:00+09:00",
  operations: {
    insert: [{
      card: {
        id: "2026-08-02_GL_01",
        date: "2026-08-02",
        title: "new",
        related: []
      },
      stage_artifacts: ["artifacts/stage-c.json"],
      evidence_refs: ["https://example.com/source-1"]
    }],
    update: [{
      id: "2026-07-31_US_01",
      changes: [{ op: "replace", path: "/title", value: "corrected title" }],
      reason: "official correction",
      stage_artifacts: ["artifacts/final-qc.json"],
      evidence_refs: ["https://example.com/official-source"]
    }],
    related_add: [{
      source_id: "2026-08-01_KR_01",
      target_id: "2026-08-02_GL_01",
      relation_type: "distinct_follow_up",
      lineage_reason: "계획이 계약 단계로 전환",
      event_stage_relationship: "plan → contract",
      direction: "directional",
      stage_artifacts: ["artifacts/final-qc.json"],
      evidence_refs: ["https://example.com/source-1"],
      patches: [
        { card_id: "2026-08-01_KR_01", op: "add", path: "/related/-", value: "2026-08-02_GL_01" },
        { card_id: "2026-08-01_KR_01", op: "add", path: "/related_lineage/related_ids/-", value: "2026-08-02_GL_01" },
        { card_id: "2026-08-01_KR_01", op: "replace", path: "/related_lineage/relation_type", value: "distinct_follow_up" },
        { card_id: "2026-08-01_KR_01", op: "replace", path: "/related_lineage/reason", value: "계획이 계약 단계로 전환" }
      ]
    }]
  },
  expected_after: 3,
  audit_refs: ["artifacts/audit/test-run.json"],
  document_universe_manifest_ref: "artifacts/stage-0.0d.json",
  coverage_discovery_ref: "artifacts/stage-0.0c.json",
  independent_completeness_ref: "artifacts/stage-0.7c.json"
};

const invoke = (runDoc, extra = [], { main = mainSha } = {}) => {
  writeFileSync(runPath, JSON.stringify(runDoc));
  return run(process.execPath, [
    "scripts/apply_card_run.mjs",
    "--run", "runs/2026-08-02/card-run.json",
    "--baseline", "data/cards.full.json",
    "--canonical-path", "data/cards.full.json",
    "--output", "data/cards.full.json",
    "--report", "runs/2026-08-02/apply-report.json",
    "--base-main-sha", main,
    "--lean-path", "public/data/cards.json",
    ...extra,
  ]);
};

mustPass(invoke(validRun, ["--apply", "--skip-lean"]), "valid apply");
const appliedBytes = readFileSync(fullPath);
const appliedText = appliedBytes.toString("utf8");
if (!appliedText.includes("\r\n  \"schema\"")) throw new Error("CRLF/indent format not preserved");
if (/[^\r]\n/.test(appliedText)) throw new Error("lone LF introduced");
const output = JSON.parse(appliedText);
const source = output.cards.find((card) => card.id === "2026-08-01_KR_01");
const updated = output.cards.find((card) => card.id === "2026-07-31_US_01");
if (output.cards.length !== 3 || output.total !== 3) throw new Error("count/total mismatch");
if (output.updated !== validRun.output_updated) throw new Error("updated metadata mismatch");
if (output.cards[0].id !== "2026-08-02_GL_01") throw new Error("latest-first mismatch");
if (updated.title !== "corrected title") throw new Error("update missing");
if (!source.related.includes("LEGACY_DANGLING")) throw new Error("legacy dangling lost");
if (!source.related.includes("2026-08-02_GL_01")) throw new Error("new relation missing");
if (!source.related_lineage.related_ids.includes("2026-08-02_GL_01")) throw new Error("lineage target missing");

mustPass(invoke(validRun, ["--apply", "--skip-lean"]), "idempotent reapply");
const idempotentReport = JSON.parse(readFileSync(reportPath, "utf8"));
if (idempotentReport.status !== "ALREADY_APPLIED") throw new Error("idempotent state mismatch");
if (!readFileSync(fullPath).equals(appliedBytes)) throw new Error("idempotent bytes changed");

writeFileSync(fullPath, JSON.stringify(output));
mustPass(invoke(validRun, ["--apply", "--skip-lean"]), "format normalization");
const normalizedReport = JSON.parse(readFileSync(reportPath, "utf8"));
if (normalizedReport.status !== "FORMATTING_NORMALIZED") throw new Error("format normalization state mismatch");
if (!readFileSync(fullPath).equals(appliedBytes)) throw new Error("format normalization failed");

const staleMain = structuredClone(validRun);
mustFail(invoke(staleMain, ["--check"], { main: "f".repeat(40) }), "BLOCKED_BASELINE_MOVED_REBASE_REQUIRED", "stale main");

const staleBlob = structuredClone(validRun);
staleBlob.base_full_blob_sha = "b".repeat(40);
mustFail(invoke(staleBlob), "BLOCKED_GOVERNANCE_ARTIFACT_STALE", "stale blob governance binding");

writeArtifact("artifacts/stage-0.0d.json", {
  stage: "0.0D", status: "PASS", repository_head_sha: mainSha,
  canonical_full_blob_sha: "b".repeat(40), unresolved_rule_conflicts: [],
  incomplete_universe_defects: [], all_docs_files_read_or_parsed: true,
  stage_0_0c_authorized: true
});
writeArtifact("artifacts/stage-0.0c.json", {
  stage: "0.0C", status: "PASS",
  document_universe_manifest_ref: "artifacts/stage-0.0d.json",
  base_full_blob_sha: "b".repeat(40), original_input_accounted: true,
  stage_a_authorized: true
});
mustFail(invoke(staleBlob), "BLOCKED_BASELINE_MOVED_REBASE_REQUIRED", "forged stale blob blocked by git");
writeArtifact("artifacts/stage-0.0d.json", {
  stage: "0.0D", status: "PASS", repository_head_sha: mainSha,
  canonical_full_blob_sha: fullBlobSha, unresolved_rule_conflicts: [],
  incomplete_universe_defects: [], all_docs_files_read_or_parsed: true,
  stage_0_0c_authorized: true
});
writeArtifact("artifacts/stage-0.0c.json", {
  stage: "0.0C", status: "PASS",
  document_universe_manifest_ref: "artifacts/stage-0.0d.json",
  base_full_blob_sha: fullBlobSha, original_input_accounted: true,
  stage_a_authorized: true
});

const forbidden = structuredClone(validRun);
forbidden.operations.delete = [];
mustFail(invoke(forbidden), "FORBIDDEN_OPERATION", "delete forbidden");

const relationViaUpdate = structuredClone(validRun);
relationViaUpdate.operations.update[0].changes = [
  { op: "add", path: "/related/-", value: "2026-08-02_GL_01" }
];
mustFail(invoke(relationViaUpdate), "RELATION_UPDATE_FORBIDDEN", "relation via update");

const identityMetadata = structuredClone(validRun);
identityMetadata.operations.update[0].source_spec_id = "LEGACY_UPDATE_SPEC";
identityMetadata.operations.related_add[0].source_spec_id = "LEGACY_RELATED_SPEC";
identityMetadata.operations.related_add[0].identity_card_id = "2026-08-01_KR_01";
mustPass(invoke(identityMetadata, ["--check"]), "metadata-only legacy identities accepted by low-level engine");

const identityMutation = structuredClone(validRun);
identityMutation.operations.update[0].changes = [
  { op: "add", path: "/source_spec_id", value: "FORGED_SPEC" }
];
mustFail(invoke(identityMutation), "IMMUTABLE_SOURCE_SPEC_ID", "source identity mutation forbidden");

const missingTarget = structuredClone(validRun);
missingTarget.operations.related_add[0].target_id = "MISSING";
missingTarget.operations.related_add[0].patches[0].value = "MISSING";
missingTarget.operations.related_add[0].patches[1].value = "MISSING";
mustFail(invoke(missingTarget), "BLOCKED_NEW_MISSING_RELATED_TARGETS", "missing target");

const smuggled = structuredClone(validRun);
smuggled.operations.related_add[0].patches.push({
  card_id: "2026-08-01_KR_01",
  op: "add",
  path: "/related/-",
  value: "2026-07-31_US_01"
});
mustFail(invoke(smuggled), "UNDECLARED_RELATED_EDGE", "third edge smuggling");

const wrongCount = structuredClone(validRun);
wrongCount.expected_after = 4;
mustFail(invoke(wrongCount), "COUNT_RECONCILIATION_FAILED", "count mismatch");

const prelinkedInsert = structuredClone(validRun);
prelinkedInsert.operations.insert[0].card.related = ["2026-08-01_KR_01"];
mustFail(invoke(prelinkedInsert), "INVALID_INSERT", "insert relation must be declared");

const lineageSmuggle = structuredClone(validRun);
lineageSmuggle.operations.related_add[0].patches.push({
  card_id: "2026-08-01_KR_01", op: "add",
  path: "/related_lineage/related_ids/-", value: "2026-07-31_US_01"
});
mustFail(invoke(lineageSmuggle), "UNDECLARED_RELATED_EDGE", "lineage third target smuggling");

const missingUniverse = structuredClone(validRun);
missingUniverse.document_universe_manifest_ref = "artifacts/missing-0.0d.json";
mustFail(invoke(missingUniverse), "BLOCKED_GOVERNANCE_REFERENCE", "missing document universe");

writeArtifact("artifacts/stage-0.7c-blocked.json", {
  stage: "0.7C", status: "BLOCKED_EDITORIAL_COMPLETENESS_UNPROVEN",
  prompt_0_8_authorized: false
});
const blockedCompleteness = structuredClone(validRun);
blockedCompleteness.independent_completeness_ref = "artifacts/stage-0.7c-blocked.json";
mustFail(invoke(blockedCompleteness), "BLOCKED_GOVERNANCE_ARTIFACT_NOT_PASSING", "blocked completeness");

const missingStageArtifact = structuredClone(validRun);
missingStageArtifact.operations.insert[0].stage_artifacts = ["artifacts/missing-stage.json"];
mustFail(invoke(missingStageArtifact), "BLOCKED_GOVERNANCE_REFERENCE", "missing stage artifact");

const invalidEvidence = structuredClone(validRun);
invalidEvidence.operations.update[0].evidence_refs = ["missing-evidence-file"];
mustFail(invoke(invalidEvidence), "BLOCKED_EVIDENCE_REFERENCE_INVALID", "invalid evidence reference");

// Restore baseline, introduce an undeclared branch edit, and confirm the engine refuses it.
writeFileSync(fullPath, JSON.stringify({ ...baseline, cards: baseline.cards.map((card, i) => i ? card : { ...card, title: "silent edit" }) }));
mustFail(invoke(validRun), "BLOCKED_UNDECLARED_CARD_DIFF", "undeclared working diff");

console.log("PASS: apply_card_run_test — positive, idempotent, CRLF format, governance, metadata-only legacy identities, and identity-mutation blocking");
