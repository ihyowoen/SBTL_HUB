#!/usr/bin/env node
import { readFileSync, writeFileSync, unlinkSync } from "node:fs";

const stageBPath = "docs/llm_prompts/v1/02_PROMPT_0_2_Stage_B_r0.md";
const finalQcPath = "docs/llm_prompts/v1/09_PROMPT_0_7_Final_QC.md";
const testsPath = "validation_scripts/tests/test_workflow_contracts.py";
const validationPath = "docs/validation/STRUCTURAL_NEWS_VALUE_V3_VALIDATION_20260802.md";
const selfPath = "scripts/patch_structural_v3_review_4837763004.mjs";
const workflowPath = ".github/workflows/patch-structural-v3-review-4837763004.yml";

function replaceOnce(text, oldText, newText, label) {
  const count = text.split(oldText).length - 1;
  if (count !== 1) throw new Error(`${label}: expected 1 target, found ${count}`);
  return text.replace(oldText, newText);
}

let stageB = readFileSync(stageBPath, "utf8");
stageB = replaceOnce(
  stageB,
  "All 8 documents above are mandatory.",
  "All 10 documents above are mandatory.",
  "Stage B required-doc count",
);
stageB = replaceOnce(
  stageB,
  "   - list all 8 required docs",
  "   - list all 10 required docs",
  "Stage B report required-doc count",
);
stageB = replaceOnce(
  stageB,
  "- product/demo/PoC/pilot/prototype/component/interview/commentary/roundup/speech/personnel/partnership format has no concrete execution anchor",
  "- product/demo/PoC/pilot/prototype/component/interview/commentary/roundup/speech/personnel/partnership format has neither a fetched source-backed concrete execution anchor nor a complete fetched source-backed V3 non-execution Structural Value Override package",
  "Stage B source-direction blocker",
);
stageB = replaceOnce(
  stageB,
  "- format-risk item has no fetched evidence for a concrete execution anchor",
  "- format-risk item has fetched evidence for neither a concrete execution anchor nor a complete V3 non-execution Structural Value Override package with a valid anchor class, item-specific evidence targets, specific why_execution_event_not_required, before-after chain, and changed judgment",
  "Stage B draft-blocked residual",
);
writeFileSync(stageBPath, stageB);

let finalQc = readFileSync(finalQcPath, "utf8");
finalQc = replaceOnce(
  finalQc,
  "All 8 documents above are mandatory.",
  "All 10 documents above are mandatory.",
  "Final QC required-doc count",
);
finalQc = replaceOnce(
  finalQc,
  "   - list all 8 required docs",
  "   - list all 10 required docs",
  "Final QC report required-doc count",
);
finalQc = replaceOnce(
  finalQc,
  "- They are subject to a strict-pass presumption block: without a concrete fresh execution anchor, they must not have entered `strict_passed_spec[]`; if they did, the downstream step must hold, reject, or return the item to the appropriate prior stage rather than polishing it forward.",
  "- They are subject to a strict-pass presumption block: without either a concrete fresh execution anchor or a complete V3 non-execution Structural Value Override, they must not have entered `strict_passed_spec[]`; if neither source-backed path is valid, the downstream step must hold, reject, or return the item to the appropriate prior stage rather than polishing it forward.",
  "Final QC residual selector overlay",
);
finalQc = replaceOnce(
  finalQc,
  `- a passed Evidence QC lineage declaration
- a passed execution-anchor QC summary
- \`lineage_and_anchor_guard.evidence_qc_lineage_passed: true\`
- \`lineage_and_anchor_guard.execution_anchor_qc_passed: true\`
- content polish accounting matches input`,
  `- a passed Evidence QC lineage declaration
- a passed anchor-path QC summary covering the selected execution or V3 non-execution route
- \`lineage_and_anchor_guard.evidence_qc_lineage_passed: true\`
- \`lineage_and_anchor_guard.anchor_path_qc_passed: true\`
- exactly one applicable route result: \`execution_anchor_qc_passed: true\` or \`structural_value_override_qc_passed: true\`; the non-applicable route must be explicitly marked not_applicable with a reason
- content polish accounting matches input`,
  "Final QC upstream anchor-path lineage gate",
);
finalQc = replaceOnce(
  finalQc,
  `A card with \`format_risk_tags\`, \`execution_anchor_type\`, or an execution/deployment implication may receive \`publish_ready=true\` only if Final QC confirms all of the following:

1. the execution anchor is explicitly covered by \`fact_sources\` and \`source_claim_coverage_map\`;
2. the visible fields do not overstate stage, scale, causality, market effect, or commercialization;
3. the card retains any necessary caveat when the event is pilot, demo, PoC, early deployment, or review-stage policy;
4. no selector-lineage defect is unresolved.`,
  `A card with \`format_risk_tags\`, anchor-path metadata, or an execution/deployment implication may receive \`publish_ready=true\` only if Final QC confirms all of the following:

1. exactly one source-backed path is complete: either (a) the concrete execution anchor is explicitly covered by \`fact_sources\` and \`source_claim_coverage_map\`, or (b) the V3 non-execution anchor class, every item-specific \`evidence_needed_for_stage_b[]\` target, before-after chain, changed judgment, and specific \`why_execution_event_not_required\` are explicitly covered;
2. the visible fields do not overstate stage, scale, causality, market effect, commercialization, or the selected non-execution anchor class;
3. the card retains any necessary caveat when the event is pilot, demo, PoC, early deployment, review-stage policy, preliminary financial data, strategic intent, or uncertain follow-up probability;
4. no selector-lineage or anchor-path defect is unresolved.`,
  "Final QC publish-ready two-path checklist",
);
finalQc = replaceOnce(
  finalQc,
  `  "format_risk_publish_ready_checked_count": 0,
  "format_risk_publish_ready_blocked_count": 0`,
  `  "format_risk_publish_ready_checked_count": 0,
  "format_risk_execution_path_pass_count": 0,
  "format_risk_non_execution_path_pass_count": 0,
  "format_risk_publish_ready_blocked_count": 0`,
  "Final QC selector-lineage output counts",
);
writeFileSync(finalQcPath, finalQc);

let tests = readFileSync(testsPath, "utf8");
const testClass = `

class StructuralV3PromptRegressionTest(unittest.TestCase):
    def read_prompt(self, relative_path: str) -> str:
        return (ROOT.parent / relative_path).read_text(encoding="utf-8")

    def test_stage_b_has_ten_required_docs_and_no_execution_only_blockers(self):
        text = self.read_prompt("docs/llm_prompts/v1/02_PROMPT_0_2_Stage_B_r0.md")
        self.assertIn("All 10 documents above are mandatory.", text)
        self.assertIn("list all 10 required docs", text)
        self.assertNotIn("All 8 documents above are mandatory.", text)
        self.assertNotIn("list all 8 required docs", text)
        self.assertNotIn("format has no concrete execution anchor", text)
        self.assertNotIn("format-risk item has no fetched evidence for a concrete execution anchor", text)
        self.assertIn("neither a fetched source-backed concrete execution anchor nor a complete fetched source-backed V3 non-execution Structural Value Override package", text)
        self.assertIn("has fetched evidence for neither a concrete execution anchor nor a complete V3 non-execution Structural Value Override package", text)

    def test_final_qc_overlay_accepts_both_source_backed_paths(self):
        text = self.read_prompt("docs/llm_prompts/v1/09_PROMPT_0_7_Final_QC.md")
        self.assertIn("All 10 documents above are mandatory.", text)
        self.assertIn("list all 10 required docs", text)
        self.assertNotIn("All 8 documents above are mandatory.", text)
        self.assertNotIn("list all 8 required docs", text)
        self.assertNotIn("without a concrete fresh execution anchor, they must not have entered", text)
        self.assertNotIn("the execution anchor is explicitly covered by `fact_sources` and `source_claim_coverage_map`;", text)
        self.assertIn("without either a concrete fresh execution anchor or a complete V3 non-execution Structural Value Override", text)
        self.assertIn("exactly one source-backed path is complete", text)
        self.assertIn("lineage_and_anchor_guard.anchor_path_qc_passed: true", text)
`;
tests = replaceOnce(
  tests,
  '\n\nif __name__ == "__main__":\n    unittest.main()\n',
  `${testClass}\n\nif __name__ == "__main__":\n    unittest.main()\n`,
  "Prompt regression test insertion",
);
writeFileSync(testsPath, tests);

let validation = readFileSync(validationPath, "utf8");
validation += `\n## Review 4837763004 downstream residual closure\n\n- Stage B source-direction and draft-blocked lists now reject format-risk items only when neither the source-backed execution path nor the complete source-backed V3 non-execution path is available.\n- Final QC's later safety overlay and publish-ready checklist now validate both source-backed paths and carry explicit anchor-path QC status.\n- Stage B and Final QC required-doc accounting now consistently requires all ten governance documents.\n- Regression tests fail on the removed execution-only blocker phrases or any return to eight-document accounting.\n`;
writeFileSync(validationPath, validation);

for (const [path, forbidden] of [
  [stageBPath, [
    "All 8 documents above are mandatory.",
    "list all 8 required docs",
    "format has no concrete execution anchor",
    "format-risk item has no fetched evidence for a concrete execution anchor",
  ]],
  [finalQcPath, [
    "All 8 documents above are mandatory.",
    "list all 8 required docs",
    "without a concrete fresh execution anchor, they must not have entered",
    "the execution anchor is explicitly covered by `fact_sources` and `source_claim_coverage_map`;",
  ]],
]) {
  const text = readFileSync(path, "utf8");
  for (const needle of forbidden) {
    if (text.includes(needle)) throw new Error(`${path}: residual forbidden phrase: ${needle}`);
  }
}

unlinkSync(selfPath);
unlinkSync(workflowPath);
