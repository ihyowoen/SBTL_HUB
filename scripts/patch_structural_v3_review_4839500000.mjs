import fs from 'node:fs';

function replaceOnce(path, before, after, label) {
  const text = fs.readFileSync(path, 'utf8');
  const count = text.split(before).length - 1;
  if (count !== 1) throw new Error(`${label}: expected 1 target, found ${count}`);
  fs.writeFileSync(path, text.replace(before, after));
}

replaceOnce(
  'docs/STRUCTURAL_NEWS_VALUE_SELECTION.md',
  '| REVIEW | PASS/REVIEW | 55–100 | `candidate_review_pool[]` or `structural_signal_review_pool[]` with a mandatory rescue question |\n| PASS/REVIEW | REVIEW | any | candidate review, earnings deep dive, reinforcement, or watchlist |',
  '| REVIEW | PASS/REVIEW | 55–100 | `candidate_review_pool[]` with `review_pool_subtype: structural_signal_review_pool` and a mandatory rescue question |\n| PASS/REVIEW | REVIEW | any | `candidate_review_pool[]` with the applicable `review_pool_subtype` (`structural_signal_review_pool` or `earnings_deep_dive_pool`), reinforcement, or watchlist |',
  'canonical routing matrix'
);
replaceOnce(
  'docs/STRUCTURAL_NEWS_VALUE_SELECTION.md',
  '- `candidate_review_pool[]` — potentially cardable after bounded clarification;\n- `structural_signal_review_pool[]` — high structural potential requiring source, denominator, stage, or comparison rescue;\n- `earnings_deep_dive_pool[]` — earnings candidate lacking full call/Q&A or prior-period comparison;',
  '- `candidate_review_pool[]` — the only top-level review partition for potentially cardable items after bounded clarification;\n  - `review_pool_subtype: structural_signal_review_pool` — high structural potential requiring source, denominator, stage, or comparison rescue;\n  - `review_pool_subtype: earnings_deep_dive_pool` — earnings candidate lacking full call/Q&A or prior-period comparison;\n- `structural_signal_review_pool[]` and `earnings_deep_dive_pool[]` must not be emitted as standalone top-level arrays;',
  'canonical review partitions'
);

replaceOnce(
  'docs/llm_prompts/v1/03_PROMPT_0_3_Stage_C_r0.md',
  '- fact_sources\n- anchor_path_validation\n  - selected_anchor_path: execution|v3_non_execution\n  - anchor_path_qc_passed: true\n  - execution_anchor_qc_status: pass|not_applicable\n  - structural_value_override_qc_status: pass|not_applicable\n  - non_applicable_anchor_path_reason\n- stage_c_findings',
  '- fact_sources\n- `anchor_path_validation` only when `format_risk_tags` is non-empty\n  - selected_anchor_path: execution|v3_non_execution\n  - anchor_path_qc_passed: true\n  - execution_anchor_qc_status: pass|not_applicable\n  - structural_value_override_qc_status: pass|not_applicable\n  - non_applicable_anchor_path_reason\n- ordinary accepted items with no `format_risk_tags` must not invent or be required to emit an anchor-path route\n- stage_c_findings',
  'Stage C accepted schema scope'
);
replaceOnce(
  'docs/llm_prompts/v1/03_PROMPT_0_3_Stage_C_r0.md',
  '- `distinct_follow_up` requires a direct fresh execution anchor.',
  '- `distinct_follow_up` requires a valid fresh V3 anchor class recorded in `fresh_follow_up_anchor_class`, plus non-empty `fresh_follow_up_anchor`, `incremental_fact_vs_predecessor`, and `changed_judgment_vs_predecessor`; a conventional execution anchor is not mandatory when another permitted V3 anchor class proves the material follow-up.',
  'Stage C related overlay'
);

replaceOnce(
  'docs/llm_prompts/v1/09A_PROMPT_0_7C_INDEPENDENT_COMPLETENESS_REVIEW.md',
  '**Authority:** `docs/EDITORIAL_VALUE_AND_COMPLETENESS_STANDARD.md`',
  '**Authority:** `docs/EDITORIAL_VALUE_AND_COMPLETENESS_STANDARD.md`, `docs/STRUCTURAL_NEWS_VALUE_SELECTION.md`, and `docs/llm_prompts/v1/01A_PROMPT_0_1S_Structural_Value_Override.md`',
  '0.7C authority'
);
replaceOnce(
  'docs/llm_prompts/v1/09A_PROMPT_0_7C_INDEPENDENT_COMPLETENESS_REVIEW.md',
  'Verify the exact stage, fresh execution anchor, predecessor, successor, contrary signals, and next milestone.',
  'For every format-risk card, verify exactly one preserved source-backed anchor path: either a concrete fresh execution route or a complete V3 non-execution Structural Value Override. Verify the selected route, predecessor, successor, contrary signals, next milestone, route-specific status, and specific non-applicable-route reason. Do not reject a valid V3 non-execution route solely because a conventional execution anchor is absent.',
  '0.7C event-stage challenge'
);
replaceOnce(
  'docs/llm_prompts/v1/09A_PROMPT_0_7C_INDEPENDENT_COMPLETENESS_REVIEW.md',
  '- a follow-up lacks an execution-stage comparison;',
  '- a follow-up lacks a valid fresh V3 anchor-class comparison, incremental fact versus predecessor, or changed judgment versus predecessor;\n- a format-risk card lacks exactly one passing source-backed anchor path, has dual/contradictory route claims, or omits the non-applicable-route reason;',
  '0.7C hard blockers'
);

const testPath = 'validation_scripts/tests/test_structural_v3_review_4839334318_followup.py';
fs.writeFileSync(testPath, `from pathlib import Path\nimport unittest\n\nROOT = Path(__file__).resolve().parents[2]\n\nclass StructuralV3FollowupReviewTests(unittest.TestCase):\n    def read(self, path):\n        return (ROOT / path).read_text(encoding='utf-8')\n\n    def test_canonical_review_pools_are_subtypes(self):\n        text = self.read('docs/STRUCTURAL_NEWS_VALUE_SELECTION.md')\n        self.assertIn('review_pool_subtype: structural_signal_review_pool', text)\n        self.assertIn('review_pool_subtype: earnings_deep_dive_pool', text)\n        self.assertIn('must not be emitted as standalone top-level arrays', text)\n\n    def test_stage_c_anchor_path_is_format_risk_only(self):\n        text = self.read('docs/llm_prompts/v1/03_PROMPT_0_3_Stage_C_r0.md')\n        self.assertIn('anchor_path_validation\\` only when \\`format_risk_tags\\` is non-empty'.replace('\\\\`','`'), text)\n        self.assertIn('must not invent or be required to emit an anchor-path route', text)\n\n    def test_stage_c_followup_accepts_v3_anchor_classes(self):\n        text = self.read('docs/llm_prompts/v1/03_PROMPT_0_3_Stage_C_r0.md')\n        self.assertIn('fresh_follow_up_anchor_class', text)\n        self.assertNotIn('distinct_follow_up\\` requires a direct fresh execution anchor'.replace('\\\\`','`'), text)\n\n    def test_independent_review_uses_two_path_gate(self):\n        text = self.read('docs/llm_prompts/v1/09A_PROMPT_0_7C_INDEPENDENT_COMPLETENESS_REVIEW.md')\n        self.assertIn('exactly one preserved source-backed anchor path', text)\n        self.assertIn('complete V3 non-execution Structural Value Override', text)\n        self.assertIn('specific non-applicable-route reason', text)\n\nif __name__ == '__main__':\n    unittest.main()\n`);
