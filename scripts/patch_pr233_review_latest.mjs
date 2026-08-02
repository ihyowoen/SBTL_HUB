import fs from 'node:fs';

function replaceAllExact(path, from, to, label) {
  let text = fs.readFileSync(path, 'utf8');
  const count = text.split(from).length - 1;
  if (count < 1) throw new Error(`${label}: target not found`);
  text = text.split(from).join(to);
  fs.writeFileSync(path, text);
}

function replaceOnce(path, from, to, label) {
  let text = fs.readFileSync(path, 'utf8');
  const count = text.split(from).length - 1;
  if (count !== 1) throw new Error(`${label}: expected 1 target, found ${count}`);
  text = text.replace(from, to);
  fs.writeFileSync(path, text);
}

const stageA = 'docs/llm_prompts/v1/01_PROMPT_0_1_Stage_A.md';
const override = 'docs/llm_prompts/v1/01A_PROMPT_0_1S_Structural_Value_Override.md';
for (const path of [stageA, override]) {
  replaceAllExact(path, '`structural_signal_review_pool`', '`structural_signal_review`', `${path} structural subtype`);
  replaceAllExact(path, '`earnings_deep_dive_pool`', '`earnings_deep_dive`', `${path} earnings subtype`);
  replaceAllExact(path, 'structural_signal_review_pool', 'structural_signal_review', `${path} raw structural subtype`);
  replaceAllExact(path, 'earnings_deep_dive_pool', 'earnings_deep_dive', `${path} raw earnings subtype`);
}

const baseline = 'docs/llm_prompts/v1/06_PROMPT_0_4_Baseline_Revalidation.md';
replaceOnce(baseline,
`- anchor_path_validation
  - selected_anchor_path: execution|v3_non_execution
  - anchor_path_qc_passed: true
  - execution_anchor_qc_status: pass|not_applicable
  - structural_value_override_qc_status: pass|not_applicable
  - non_applicable_anchor_path_reason`,
`- anchor_path_validation (required only when the item has non-empty \`format_risk_tags\`; ordinary items with no format risk must not invent this object)
  - selected_anchor_path: execution|v3_non_execution
  - anchor_path_qc_passed: true
  - execution_anchor_qc_status: pass|not_applicable
  - structural_value_override_qc_status: pass|not_applicable
  - non_applicable_anchor_path_reason`,
'baseline conditional anchor schema');

const polish = 'docs/llm_prompts/v1/08_PROMPT_0_6_Content_Polish.md';
replaceOnce(polish,
`Every \`content_enriched_and_language_polished[]\` item must emit its selected path and coherent route statuses. Final override: if lineage, route accounting, or anchor-path guard fails, the next recommended call must not be Prompt 0.7.`,
`Every \`content_enriched_and_language_polished[]\` item with non-empty \`format_risk_tags\` must emit its selected path and coherent route statuses. Ordinary items with no format risk must preserve the lineage guard but must not invent selected-path or route-status fields. Final override: if lineage, applicable route accounting, or the anchor-path guard fails, the next recommended call must not be Prompt 0.7.`,
'content polish output scope');
replaceOnce(polish,
`Required payload-item fields for every \`content_enriched_and_language_polished[]\` item:

\`\`\`json
"lineage_and_anchor_guard": {
  "status": "PASS",
  "source_spec_id": "...",
  "evidence_qc_lineage_passed": true,
  "anchor_path_qc_passed": true,
  "selected_anchor_path": "execution|v3_non_execution",
  "execution_anchor_qc_status": "pass|not_applicable",
  "structural_value_override_qc_status": "pass|not_applicable",
  "non_applicable_anchor_path_reason": "...",`,
`Required payload-item fields for every \`content_enriched_and_language_polished[]\` item begin with the ordinary lineage fields below. The anchor-path fields shown after them are required only when the item has non-empty \`format_risk_tags\`; ordinary items must omit them rather than invent a route.

\`\`\`json
"lineage_and_anchor_guard": {
  "status": "PASS",
  "source_spec_id": "...",
  "evidence_qc_lineage_passed": true,
  "anchor_path_qc_passed": "true for format-risk item; NOT_APPLICABLE_NO_FORMAT_RISK otherwise",
  "selected_anchor_path": "execution|v3_non_execution; omit for ordinary item",
  "execution_anchor_qc_status": "pass|not_applicable; omit for ordinary item",
  "structural_value_override_qc_status": "pass|not_applicable; omit for ordinary item",
  "non_applicable_anchor_path_reason": "required for the unselected route on format-risk item; omit for ordinary item",`,
'content polish payload conditional schema');

const testPath = 'validation_scripts/tests/test_pr233_latest_review_contracts.py';
fs.writeFileSync(testPath, `from pathlib import Path\nimport unittest\n\nROOT = Path(__file__).resolve().parents[2]\n\nclass TestPR233LatestReviewContracts(unittest.TestCase):\n    def test_review_pool_subtypes_are_canonical(self):\n        for rel in [\n            'docs/llm_prompts/v1/01_PROMPT_0_1_Stage_A.md',\n            'docs/llm_prompts/v1/01A_PROMPT_0_1S_Structural_Value_Override.md',\n        ]:\n            text = (ROOT / rel).read_text(encoding='utf-8')\n            self.assertNotIn('structural_signal_review_pool', text)\n            self.assertNotIn('earnings_deep_dive_pool', text)\n            self.assertIn('structural_signal_review', text)\n            self.assertIn('earnings_deep_dive', text)\n\n    def test_baseline_anchor_schema_is_format_risk_only(self):\n        text = (ROOT / 'docs/llm_prompts/v1/06_PROMPT_0_4_Baseline_Revalidation.md').read_text(encoding='utf-8')\n        self.assertIn('required only when the item has non-empty \\`format_risk_tags\\`', text)\n        self.assertIn('ordinary items with no format risk must not invent this object', text)\n\n    def test_content_polish_route_schema_is_format_risk_only(self):\n        text = (ROOT / 'docs/llm_prompts/v1/08_PROMPT_0_6_Content_Polish.md').read_text(encoding='utf-8')\n        self.assertIn('item with non-empty \\`format_risk_tags\\` must emit its selected path', text)\n        self.assertIn('ordinary items must omit them rather than invent a route', text)\n\nif __name__ == '__main__':\n    unittest.main()\n`, 'utf8');
