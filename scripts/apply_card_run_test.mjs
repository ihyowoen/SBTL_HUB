#!/usr/bin/env node
import { createHash } from "node:crypto";
import { mkdtempSync, readFileSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { spawnSync } from "node:child_process";

const script = new URL("./apply_card_run.mjs", import.meta.url).pathname;
const mainSha = "a".repeat(40);
const blobSha = (bytes) => createHash("sha1")
  .update(Buffer.from(`blob ${bytes.length}\0`))
  .update(bytes)
  .digest("hex");

const temp = mkdtempSync(join(tmpdir(), "card-run-test-"));
const baselinePath = join(temp, "cards.full.json");
const runPath = join(temp, "card-run.json");
const outputPath = join(temp, "out.json");
const reportPath = join(temp, "report.json");
const baseline = {
  schema: "cards_full_test",
  cards: [
    {
      id: "2026-01-02_US_01",
      title: "old title",
      related: ["LEGACY_DANGLING"],
      related_lineage: { LEGACY_DANGLING: { reason: "preserve" } }
    },
    { id: "2026-01-01_US_01", title: "target", related: [] }
  ]
};
const baselineBytes = Buffer.from(JSON.stringify(baseline));
writeFileSync(baselinePath, baselineBytes);

const validRun = {
  schema: "card_run_v1",
  run_id: "test-run",
  base_main_commit_sha: mainSha,
  base_full_blob_sha: blobSha(baselineBytes),
  expected_before: 2,
  operations: {
    insert: [{
      card: { id: "2026-01-03_US_01", title: "new", related: [] },
      stage_artifacts: ["stage-c.json"],
      evidence_refs: ["source-1"]
    }],
    update: [{
      id: "2026-01-02_US_01",
      changes: [{ op: "replace", path: "/title", value: "corrected title" }],
      reason: "official correction",
      stage_artifacts: ["final-qc.json"],
      evidence_refs: ["official-source"]
    }],
    related_add: [{
      source_id: "2026-01-02_US_01",
      target_id: "2026-01-03_US_01",
      relation_type: "distinct_follow_up",
      lineage_reason: "plan advanced to contract",
      event_stage_relationship: "plan → contract",
      direction: "directional",
      evidence_refs: ["source-1"],
      patches: [
        { card_id: "2026-01-02_US_01", op: "add", path: "/related/-", value: "2026-01-03_US_01" },
        { card_id: "2026-01-02_US_01", op: "add", path: "/related_lineage/2026-01-03_US_01", value: { type: "distinct_follow_up" } }
      ]
    }]
  },
  expected_after: 3,
  audit_refs: ["audit/test-run.json"],
  document_universe_manifest_ref: "stage-0.0d.json",
  coverage_discovery_ref: "stage-0.0c.json",
  independent_completeness_ref: "stage-0.7c.json"
};

const invoke = (run, extra = []) => {
  writeFileSync(runPath, JSON.stringify(run));
  return spawnSync(process.execPath, [
    script,
    "--run", runPath,
    "--baseline", baselinePath,
    "--output", outputPath,
    "--report", reportPath,
    "--base-main-sha", mainSha,
    ...extra,
  ], { encoding: "utf8" });
};

const expectPass = (result, label) => {
  if (result.status !== 0) throw new Error(`${label} expected PASS\n${result.stdout}\n${result.stderr}`);
};
const expectFail = (result, code, label) => {
  if (result.status === 0 || !result.stderr.includes(code)) {
    throw new Error(`${label} expected ${code}\n${result.stdout}\n${result.stderr}`);
  }
};

expectPass(invoke(validRun, ["--apply", "--skip-lean"]), "valid apply");
const output = JSON.parse(readFileSync(outputPath, "utf8"));
const source = output.cards.find((card) => card.id === "2026-01-02_US_01");
if (output.cards.length !== 3) throw new Error("count mismatch");
if (output.cards[0].id !== "2026-01-03_US_01") throw new Error("latest-first insert order mismatch");
if (source.title !== "corrected title") throw new Error("update missing");
if (!source.related.includes("LEGACY_DANGLING")) throw new Error("legacy related lost");
if (!source.related.includes("2026-01-03_US_01")) throw new Error("new related missing");
const report = JSON.parse(readFileSync(reportPath, "utf8"));
if (report.github_merge_ready || report.delete_count !== 0 || report.related_remove_count !== 0) {
  throw new Error("report contract mismatch");
}

const stale = structuredClone(validRun);
stale.base_full_blob_sha = "b".repeat(40);
expectFail(invoke(stale), "BLOCKED_BASELINE_MOVED_REBASE_REQUIRED", "stale blob");

const deleteRun = structuredClone(validRun);
deleteRun.operations.delete = [];
expectFail(invoke(deleteRun), "FORBIDDEN_OPERATION", "delete forbidden");

const relationViaUpdate = structuredClone(validRun);
relationViaUpdate.operations.update[0].changes = [{ op: "add", path: "/related/-", value: "2026-01-01_US_01" }];
expectFail(invoke(relationViaUpdate), "RELATION_UPDATE_FORBIDDEN", "relation update forbidden");

const missingTarget = structuredClone(validRun);
missingTarget.operations.related_add[0].target_id = "MISSING";
missingTarget.operations.related_add[0].patches[0].value = "MISSING";
expectFail(invoke(missingTarget), "BLOCKED_NEW_MISSING_RELATED_TARGETS", "missing relation target");

const wrongCount = structuredClone(validRun);
wrongCount.expected_after = 4;
expectFail(invoke(wrongCount), "COUNT_RECONCILIATION_FAILED", "count mismatch");

console.log("PASS: apply_card_run_test — positive + 5 blockers");
