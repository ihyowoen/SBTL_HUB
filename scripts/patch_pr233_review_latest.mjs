import fs from 'node:fs';

function replaceOnce(path, before, after, label) {
  const text = fs.readFileSync(path, 'utf8');
  const count = text.split(before).length - 1;
  if (count !== 1) throw new Error(`${label}: expected exactly one match, got ${count}`);
  fs.writeFileSync(path, text.replace(before, after));
}

replaceOnce(
  'docs/STRUCTURAL_NEWS_VALUE_SELECTION.md',
  `| REVIEW | PASS/REVIEW | 55–100 | \`candidate_review_pool[]\` or \`structural_signal_review_pool[]\` with a mandatory rescue question |\n| PASS/REVIEW | REVIEW | any | candidate review, earnings deep dive, reinforcement, or watchlist |`,
  `| REVIEW | PASS/REVIEW | 55–100 | \`candidate_review_pool[]\` with \`review_pool_subtype: structural_signal_review\` and a mandatory rescue question |\n| PASS/REVIEW | REVIEW | any | \`candidate_review_pool[]\` with the applicable subtype (including \`earnings_deep_dive\`), reinforcement, or watchlist |`,
  'canonical routing matrix'
);

replaceOnce(
  'docs/STRUCTURAL_NEWS_VALUE_SELECTION.md',
  `- \`candidate_review_pool[]\` — potentially cardable after bounded clarification;\n- \`structural_signal_review_pool[]\` — high structural potential requiring source, denominator, stage, or comparison rescue;\n- \`earnings_deep_dive_pool[]\` — earnings candidate lacking full call/Q&A or prior-period comparison;`,
  `- \`candidate_review_pool[]\` — the only top-level candidate review partition; every item must include \`review_pool_subtype\`.\n  - \`review_pool_subtype: structural_signal_review\` — high structural potential requiring source, denominator, stage, or comparison rescue;\n  - \`review_pool_subtype: earnings_deep_dive\` — earnings candidate lacking full call/Q&A or prior-period comparison;\n- \`structural_signal_review_pool[]\` and \`earnings_deep_dive_pool[]\` are prohibited as standalone top-level arrays; they are subtype views of \`candidate_review_pool[]\` only;`,
  'canonical review partitions'
);

replaceOnce(
  'docs/llm_prompts/v1/03_PROMPT_0_3_Stage_C_r0.md',
  `- fact_sources\n- anchor_path_validation\n  - selected_anchor_path: execution|v3_non_execution\n  - anchor_path_qc_passed: true\n  - execution_anchor_qc_status: pass|not_applicable\n  - structural_value_override_qc_status: pass|not_applicable\n  - non_applicable_anchor_path_reason\n- stage_c_findings`,
  `- fact_sources\n- \`anchor_path_validation\` only when the accepted item has non-empty \`format_risk_tags\`\n  - selected_anchor_path: execution|v3_non_execution\n  - anchor_path_qc_passed: true\n  - execution_anchor_qc_status: pass|not_applicable\n  - structural_value_override_qc_status: pass|not_applicable\n  - non_applicable_anchor_path_reason\n- ordinary accepted items without \`format_risk_tags\` must not invent or be required to emit \`anchor_path_validation\`\n- stage_c_findings`,
  'Stage C accepted schema scope'
);

replaceOnce(
  'docs/llm_prompts/v1/03_PROMPT_0_3_Stage_C_r0.md',
  `- \`distinct_follow_up\` requires a direct fresh execution anchor.`,
  `- \`distinct_follow_up\` requires a valid non-empty \`fresh_follow_up_anchor\`, a valid \`fresh_follow_up_anchor_class\` under \`docs/RELATED_LIFECYCLE_CONTRACT.md\`, and non-empty \`incremental_fact_vs_predecessor\` plus \`changed_judgment_vs_predecessor\`. A conventional execution anchor is required only when the selected anchor class is \`execution\`; valid policy, financial, strategic, technology, or probability anchors are permitted by the shared contract.`,
  'Stage C related overlay'
);

replaceOnce(
  'docs/llm_prompts/v1/09A_PROMPT_0_7C_INDEPENDENT_COMPLETENESS_REVIEW.md',
  `### 3. Event-stage challenge\n\nVerify the exact stage, fresh execution anchor, predecessor, successor, contrary signals, and next milestone.`,
  `### 3. Event-stage and anchor-path challenge\n\nFor every format-risk proposed card, verify the exact stage and the preserved \`anchor_path_validation\` using an exactly-one two-path check:\n\n1. \`execution\`: source-backed fresh execution anchor, valid type/strength, and the V3 override route marked not applicable with a specific reason; or\n2. \`v3_non_execution\`: complete source-backed Structural Value Override with valid \`anchor_classes[]\`, item-specific evidence targets, specific execution-not-required rationale, before-after change, changed judgment, and the execution route marked not applicable with a specific reason.\n\nAlso verify predecessor, successor, contrary signals, and next milestone. Do not reject a valid V3 non-execution route solely because no conventional execution event exists.`,
  '0.7C anchor challenge'
);

replaceOnce(
  'docs/llm_prompts/v1/09A_PROMPT_0_7C_INDEPENDENT_COMPLETENESS_REVIEW.md',
  `  "review_pool_rescue_complete": false,\n  "must_report_candidates_accounted": false,`,
  `  "review_pool_rescue_complete": false,\n  "must_report_candidates_accounted": false,\n  "format_risk_anchor_path_review_complete": false,\n  "anchor_path_review_results": [],`,
  '0.7C output schema'
);

replaceOnce(
  'docs/llm_prompts/v1/09A_PROMPT_0_7C_INDEPENDENT_COMPLETENESS_REVIEW.md',
  `- a follow-up lacks an execution-stage comparison;`,
  `- a format-risk proposed card lacks exactly one source-backed \`execution\` or complete \`v3_non_execution\` route, or has missing/contradictory route metadata;\n- a follow-up lacks a valid fresh V3 anchor-class comparison, incremental fact, or changed judgment versus its predecessor;`,
  '0.7C blockers'
);

const testPath = 'validation_scripts/tests/test_workflow_contracts.py';
let tests = fs.readFileSync(testPath, 'utf8');
const marker = '    def test_pr233_latest_review_contract_alignment(self):\n';
if (!tests.includes(marker)) {
  tests += `\n${marker}        structural = (ROOT / "docs/STRUCTURAL_NEWS_VALUE_SELECTION.md").read_text(encoding="utf-8")\n        stage_c = (ROOT / "docs/llm_prompts/v1/03_PROMPT_0_3_Stage_C_r0.md").read_text(encoding="utf-8")\n        review_07c = (ROOT / "docs/llm_prompts/v1/09A_PROMPT_0_7C_INDEPENDENT_COMPLETENESS_REVIEW.md").read_text(encoding="utf-8")\n\n        self.assertIn("review_pool_subtype: structural_signal_review", structural)\n        self.assertIn("review_pool_subtype: earnings_deep_dive", structural)\n        self.assertIn("prohibited as standalone top-level arrays", structural)\n        self.assertIn("anchor_path_validation` only when the accepted item has non-empty `format_risk_tags", stage_c)\n        self.assertIn("ordinary accepted items without `format_risk_tags` must not invent", stage_c)\n        self.assertIn("fresh_follow_up_anchor_class", stage_c)\n        self.assertNotIn("`distinct_follow_up` requires a direct fresh execution anchor.", stage_c)\n        self.assertIn("exactly-one two-path check", review_07c)\n        self.assertIn("format_risk_anchor_path_review_complete", review_07c)\n        self.assertIn("valid fresh V3 anchor-class comparison", review_07c)\n`;
  fs.writeFileSync(testPath, tests);
}
