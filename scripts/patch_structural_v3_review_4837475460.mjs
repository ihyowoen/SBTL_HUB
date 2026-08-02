#!/usr/bin/env node
import { readFileSync, writeFileSync, unlinkSync } from "node:fs";

const promptPath = "docs/llm_prompts/v1/01A_PROMPT_0_1S_Structural_Value_Override.md";
const canonicalPath = "docs/STRUCTURAL_NEWS_VALUE_SELECTION.md";
const selfPath = "scripts/patch_structural_v3_review_4837475460.mjs";
const workflowPath = ".github/workflows/patch-structural-v3-review-4837475460.yml";

function replaceOnce(text, oldText, newText, label) {
  const first = text.indexOf(oldText);
  if (first < 0) throw new Error(`${label}: target not found`);
  if (text.indexOf(oldText, first + oldText.length) >= 0) {
    throw new Error(`${label}: target is not unique`);
  }
  return text.slice(0, first) + newText + text.slice(first + oldText.length);
}

let prompt = readFileSync(promptPath, "utf8");
prompt = replaceOnce(
  prompt,
  "- `evidence_needed_for_stage_b[]` must contain concrete official, filing, dataset, transcript, technical-validation, or independent-reporting paths required to validate the override;",
  [
    "- `evidence_needed_for_stage_b[]` must be a non-empty array of item-specific verification targets;",
    "- every evidence entry must identify both (a) the source, document, dataset, transcript, filing, technical test, or independent-reporting class and (b) the exact claim, metric, stage, date, or uncertainty to verify;",
    "- generic placeholders such as `official sources`, `company materials`, `media reports`, `additional confirmation`, `more evidence`, or equivalent wording are invalid;",
  ].join("\n"),
  "prompt override evidence rule",
);
prompt = replaceOnce(
  prompt,
  "- `structural_value_override_applied: true` is used while `evidence_needed_for_stage_b[]` is missing or empty, or `why_execution_event_not_required` is missing, null, generic, or non-specific;",
  "- `structural_value_override_applied: true` is used while `evidence_needed_for_stage_b` is not an array, is empty, contains blank, generic, placeholder, duplicate-only, or non-item-specific entries, fails to identify both the evidence target and the exact claim or uncertainty to verify, or while `why_execution_event_not_required` is missing, null, generic, or non-specific;",
  "prompt hard blocker",
);
writeFileSync(promptPath, prompt);

let canonical = readFileSync(canonicalPath, "utf8");
canonical = replaceOnce(
  canonical,
  '  "structural_value_override_applied": false,\n  "structural_value_override_reason": null,\n  "prior_state": "",',
  '  "structural_value_override_applied": false,\n  "structural_value_override_reason": null,\n  "evidence_needed_for_stage_b": [],\n  "why_execution_event_not_required": null,\n  "prior_state": "",',
  "canonical required object",
);
canonical = replaceOnce(
  canonical,
  "Only a non-earnings candidate may use `earnings_deep_dive_required: false` and `qna_status: not_applicable`.\n\n---\n\n## 16. Stage A summary and decision ledger",
  [
    "Only a non-earnings candidate may use `earnings_deep_dive_required: false` and `qna_status: not_applicable`.",
    "",
    "When `structural_value_override_applied: true`, materialise all override fields as follows:",
    "",
    "- `structural_value_override_reason` must be non-empty and item-specific;",
    "- `anchor_classes[]` must contain at least one valid non-execution anchor class;",
    "- `evidence_needed_for_stage_b[]` must be a non-empty array of item-specific verification targets;",
    "- every evidence entry must identify both (a) the source, document, dataset, transcript, filing, technical test, or independent-reporting class and (b) the exact claim, metric, stage, date, or uncertainty to verify;",
    "- generic placeholders such as `official sources`, `company materials`, `media reports`, `additional confirmation`, `more evidence`, or equivalent wording are invalid;",
    "- `why_execution_event_not_required` must be non-empty and explain why the verified change is independently decision-useful without a conventional execution event;",
    "- `next_confirmation_points[]` must identify the measurable event or metric that would confirm, weaken, or invalidate the interpretation.",
    "",
    "A false override may use empty or null values for the override-only fields.",
    "",
    "---",
    "",
    "## 16. Stage A summary and decision ledger",
  ].join("\n"),
  "canonical override materialization",
);
canonical = replaceOnce(
  canonical,
  "- `structural_value_override_applied`\n- `structural_value_override_reason`\n- `incremental_information`",
  "- `structural_value_override_applied`\n- `structural_value_override_reason`\n- `evidence_needed_for_stage_b`\n- `why_execution_event_not_required`\n- `incremental_information`",
  "canonical decision ledger",
);
canonical = replaceOnce(
  canonical,
  "- a high-potential structural item is rejected solely for lacking a conventional execution event;\n- a high-value review item lacks a concrete rescue question;",
  "- a high-potential structural item is rejected solely for lacking a conventional execution event;\n- `structural_value_override_applied: true` is used while `evidence_needed_for_stage_b` is not an array, is empty, contains blank, generic, placeholder, duplicate-only, or non-item-specific entries, fails to identify both the evidence target and the exact claim or uncertainty to verify, or while `why_execution_event_not_required` is missing, null, generic, or non-specific;\n- a high-value review item lacks a concrete rescue question;",
  "canonical hard blocker",
);
writeFileSync(canonicalPath, canonical);

for (const [path, required] of [
  [promptPath, [
    '"evidence_needed_for_stage_b": []',
    '"why_execution_event_not_required": null',
    "generic placeholders such as `official sources`",
    "fails to identify both the evidence target and the exact claim or uncertainty to verify",
  ]],
  [canonicalPath, [
    '"evidence_needed_for_stage_b": []',
    '"why_execution_event_not_required": null',
    "- `evidence_needed_for_stage_b`",
    "- `why_execution_event_not_required`",
    "generic placeholders such as `official sources`",
    "fails to identify both the evidence target and the exact claim or uncertainty to verify",
  ]],
]) {
  const text = readFileSync(path, "utf8");
  const missing = required.filter((needle) => !text.includes(needle));
  if (missing.length) throw new Error(`${path}: missing ${missing.join(", ")}`);
}

unlinkSync(selfPath);
unlinkSync(workflowPath);
console.log("PASS: review 4837475460 patch applied and temporary files removed");
