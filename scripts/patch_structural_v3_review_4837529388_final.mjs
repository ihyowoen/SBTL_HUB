#!/usr/bin/env node
import { readFileSync, writeFileSync, unlinkSync } from "node:fs";

const stageAPath = "docs/llm_prompts/v1/01_PROMPT_0_1_Stage_A.md";
const validatorPath = "validation_scripts/related_lifecycle_check.py";
const testsPath = "validation_scripts/tests/test_workflow_contracts.py";
const validationPath = "docs/validation/STRUCTURAL_NEWS_VALUE_V3_VALIDATION_20260802.md";
const selfPath = "scripts/patch_structural_v3_review_4837529388_final.mjs";
const workflowPath = ".github/workflows/patch-structural-v3-review-4837529388-final.yml";

function replaceOnce(text, oldText, newText, label) {
  const count = text.split(oldText).length - 1;
  if (count !== 1) throw new Error(`${label}: expected 1 target, found ${count}`);
  return text.replace(oldText, newText);
}

function replaceAllExact(text, oldText, newText, expectedCount, label) {
  const count = text.split(oldText).length - 1;
  if (count !== expectedCount) throw new Error(`${label}: expected ${expectedCount}, found ${count}`);
  return text.split(oldText).join(newText);
}

let stageA = readFileSync(stageAPath, "utf8");
const oldDocBlock = `1. docs/FACT_DISCIPLINE.md
2. docs/PROMPT_ABC_DEFAULT_MODE.md
3. docs/PROMPT_ABC_SUPPORTING_RULES.md
4. docs/FUTURE_CARD_STANDARD_FULL_SCHEMA.md
5. docs/CARD_ID_STANDARD.md
6. docs/WORKFLOW.md
7. docs/OPERATIONS.md
8. docs/POST_ACCEPTANCE_CONTENT_ENRICHMENT_QC.md`;
const newDocBlock = `1. docs/FACT_DISCIPLINE.md
2. docs/STRUCTURAL_NEWS_VALUE_SELECTION.md
3. docs/llm_prompts/v1/01A_PROMPT_0_1S_Structural_Value_Override.md
4. docs/PROMPT_ABC_DEFAULT_MODE.md
5. docs/PROMPT_ABC_SUPPORTING_RULES.md
6. docs/FUTURE_CARD_STANDARD_FULL_SCHEMA.md
7. docs/CARD_ID_STANDARD.md
8. docs/WORKFLOW.md
9. docs/OPERATIONS.md
10. docs/POST_ACCEPTANCE_CONTENT_ENRICHMENT_QC.md`;
stageA = replaceAllExact(stageA, oldDocBlock, newDocBlock, 2, "Stage A governance hierarchy blocks");
stageA = replaceOnce(stageA, "All 8 documents above are mandatory.", "All 10 documents above are mandatory.", "Stage A required-doc count");
stageA = replaceOnce(stageA, "A. Read all 8 required docs from GitHub main.", "A. Read all 10 required docs from GitHub main.", "Stage A task required-doc count");
stageA = replaceOnce(
  stageA,
  "   - If no concrete execution anchor is visible in upstream metadata, source_packets, usable_text, or the available content preview, the story must not enter strict_passed_spec[].",
  "   - If neither a concrete execution anchor nor a complete V3 Structural Value Override is visible in upstream metadata, source_packets, usable_text, or the available content preview, the story must not enter strict_passed_spec[]. A valid override requires a supported non-execution anchor class, item-specific Stage B evidence targets, and a specific explanation of why a conventional execution event is unnecessary.",
  "Stage A operative format-risk gate",
);
stageA = replaceOnce(
  stageA,
`   - format_risk_tags
   - execution_anchor_type
   - execution_anchor_strength
   - strict_pass_gate`,
`   - format_risk_tags
   - execution_anchor_type
   - execution_anchor_strength
   - structural_value_override_applied
   - anchor_classes
   - evidence_needed_for_stage_b
   - why_execution_event_not_required
   - strict_pass_gate`,
  "Stage A operative format-risk metadata",
);
stageA = replaceOnce(
  stageA,
  '   A format-risk item may enter strict_passed_spec only when strict_pass_gate.status = "pass" and execution_anchor_strength is "strong" or "moderate".',
  '   A format-risk item may enter strict_passed_spec only when strict_pass_gate.status = "pass" and either (a) execution_anchor_strength is "strong" or "moderate", or (b) structural_value_override_applied is true with at least one valid non-execution anchor class, non-empty item-specific evidence_needed_for_stage_b, and non-empty specific why_execution_event_not_required.',
  "Stage A operative pass condition",
);
stageA = replaceOnce(
  stageA,
`- event_anchor
- format_risk_tags
- execution_anchor_type
- execution_anchor_strength
- strict_pass_gate
- title_raw`,
`- event_anchor
- format_risk_tags
- execution_anchor_type
- execution_anchor_strength
- structural_value_override_applied
- anchor_classes
- evidence_needed_for_stage_b
- why_execution_event_not_required
- strict_pass_gate
- title_raw`,
  "Stage A strict item object",
);
writeFileSync(stageAPath, stageA);

let validator = readFileSync(validatorPath, "utf8");
validator = replaceOnce(
  validator,
  '    if relation_type == "distinct_follow_up":\n        if not lineage.get("fresh_follow_up_anchor"):',
  '    if require_contract and relation_type == "distinct_follow_up":\n        if not lineage.get("fresh_follow_up_anchor"):',
  "Related strict-field scope",
);
writeFileSync(validatorPath, validator);

let tests = readFileSync(testsPath, "utf8");
tests = replaceOnce(
  tests,
`    def test_duplicate_cannot_publish(self):
        self.child["related_lineage"]["relation_type"] = "same_event_duplicate"
        errors, _ = check_card(self.child, self.by_id, True)
        self.assertTrue(any("may not use" in error for error in errors))`,
`    def test_legacy_mode_does_not_require_v2_follow_up_fields(self):
        child = deepcopy(self.child)
        child["related_lineage"].pop("fresh_follow_up_anchor_class")
        child["related_lineage"].pop("incremental_fact_vs_predecessor")
        child["related_lineage"].pop("changed_judgment_vs_predecessor")
        by_id = {self.parent["id"]: self.parent, child["id"]: child}
        errors, _ = check_card(child, by_id, False)
        strict_field_names = (
            "fresh_follow_up_anchor_class",
            "incremental_fact_vs_predecessor",
            "changed_judgment_vs_predecessor",
        )
        self.assertFalse(any(any(name in error for name in strict_field_names) for error in errors))

    def test_duplicate_cannot_publish(self):
        self.child["related_lineage"]["relation_type"] = "same_event_duplicate"
        errors, _ = check_card(self.child, self.by_id, True)
        self.assertTrue(any("may not use" in error for error in errors))`,
  "Related legacy-mode regression test",
);
writeFileSync(testsPath, tests);

let validation = readFileSync(validationPath, "utf8");
validation = replaceOnce(
  validation,
  "- the Related production validator enforces fresh anchor class, incremental fact, and changed judgment for every `distinct_follow_up`;",
  "- the Related production validator enforces fresh anchor class, incremental fact, and changed judgment for every current-run `distinct_follow_up` under `--require-contract`, while preserving legacy unflagged validation behavior;",
  "Validation strict-scope statement",
);
writeFileSync(validationPath, validation);

for (const [path, needles] of [
  [stageAPath, [
    "All 10 documents above are mandatory.",
    "complete V3 Structural Value Override is visible",
    "- structural_value_override_applied\n- anchor_classes\n- evidence_needed_for_stage_b\n- why_execution_event_not_required\n- strict_pass_gate",
  ]],
  [validatorPath, ['if require_contract and relation_type == "distinct_follow_up":']],
  [testsPath, ["test_legacy_mode_does_not_require_v2_follow_up_fields"]],
  [validationPath, ["while preserving legacy unflagged validation behavior"]],
]) {
  const body = readFileSync(path, "utf8");
  const missing = needles.filter((needle) => !body.includes(needle));
  if (missing.length) throw new Error(`${path}: missing ${missing.join(", ")}`);
}

unlinkSync(selfPath);
unlinkSync(workflowPath);
console.log("PASS: final V3 Stage A and Related strict-scope alignment applied");
