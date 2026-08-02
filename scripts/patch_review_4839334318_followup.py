from pathlib import Path


def replace_once(path: str, old: str, new: str) -> None:
    p = Path(path)
    text = p.read_text(encoding="utf-8")
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{path}: expected one match, found {count}")
    p.write_text(text.replace(old, new, 1), encoding="utf-8")


replace_once(
    "docs/llm_prompts/v1/01A_PROMPT_0_1S_Structural_Value_Override.md",
    "- place the candidate in strict or `earnings_deep_dive[]` according to current Stage A evidence and cardability;",
    "- place the candidate in strict or `candidate_review_pool[]` with `review_pool_subtype: earnings_deep_dive` according to current Stage A evidence and cardability;",
)

baseline_path = "docs/llm_prompts/v1/06_PROMPT_0_4_Baseline_Revalidation.md"
baseline_old = """- anchor_path_validation (required only when the item has non-empty format_risk_tags; ordinary items with no format risk must not invent this object)
  - selected_anchor_path: execution|v3_non_execution
  - anchor_path_qc_passed: true
  - execution_anchor_qc_status: pass|not_applicable
  - structural_value_override_qc_status: pass|not_applicable
  - non_applicable_anchor_path_reason
- event_fingerprint
"""
baseline_new = """- anchor_path_validation (required only when the item has non-empty format_risk_tags; ordinary items with no format risk must not invent this object)
  - selected_anchor_path: execution|v3_non_execution
  - anchor_path_qc_passed: true
  - execution_anchor_qc_status: pass|not_applicable
  - structural_value_override_qc_status: pass|not_applicable
  - non_applicable_anchor_path_reason
- V3 override package (required and preserved byte-for-byte when `selected_anchor_path = v3_non_execution`; omit for the execution route and ordinary non-format-risk items)
  - structural_value_override_applied: true
  - anchor_classes[] with at least one valid non-execution class
  - evidence_needed_for_stage_b[] with item-specific evidence targets
  - why_execution_event_not_required
  - prior_state
  - new_verified_fact
  - changed_judgment
  - uncertainty_resolved
  - remaining_uncertainty
  - incremental_information
  - baseline_expectation_changed
  - decision_relevance
- event_fingerprint
"""
replace_once(baseline_path, baseline_old, baseline_new)

for path in (
    "validation_scripts/apply_prompt_contract_overlays.py",
    "docs/llm_prompts/v1/03_PROMPT_0_3_Stage_C_r0.md",
):
    replace_once(
        path,
        "selected anchor class is `execution`",
        "selected anchor class is `execution_event_anchor`",
    )

Path("validation_scripts/tests/test_review_4839334318_followup.py").write_text(
    '''from pathlib import Path\nimport unittest\n\n\nROOT = Path(__file__).resolve().parents[2]\n\n\nclass Review4839334318FollowupTests(unittest.TestCase):\n    def test_earnings_review_routes_through_candidate_pool(self):\n        text = (ROOT / "docs/llm_prompts/v1/01A_PROMPT_0_1S_Structural_Value_Override.md").read_text(encoding="utf-8")\n        self.assertIn("`candidate_review_pool[]` with `review_pool_subtype: earnings_deep_dive`", text)\n        self.assertNotIn("strict or `earnings_deep_dive[]`", text)\n\n    def test_baseline_preserves_complete_v3_package(self):\n        text = (ROOT / "docs/llm_prompts/v1/06_PROMPT_0_4_Baseline_Revalidation.md").read_text(encoding="utf-8")\n        for field in (\n            "structural_value_override_applied: true",\n            "anchor_classes[]",\n            "evidence_needed_for_stage_b[]",\n            "why_execution_event_not_required",\n            "prior_state",\n            "new_verified_fact",\n            "changed_judgment",\n            "baseline_expectation_changed",\n        ):\n            self.assertIn(field, text)\n        self.assertIn("selected_anchor_path = v3_non_execution", text)\n\n    def test_execution_event_anchor_class_is_canonical(self):\n        generator = (ROOT / "validation_scripts/apply_prompt_contract_overlays.py").read_text(encoding="utf-8")\n        stage_c = (ROOT / "docs/llm_prompts/v1/03_PROMPT_0_3_Stage_C_r0.md").read_text(encoding="utf-8")\n        self.assertIn("selected anchor class is `execution_event_anchor`", generator)\n        self.assertIn("selected anchor class is `execution_event_anchor`", stage_c)\n        self.assertNotIn("selected anchor class is `execution`;", generator)\n        self.assertNotIn("selected anchor class is `execution`;", stage_c)\n\n\nif __name__ == "__main__":\n    unittest.main()\n''',
    encoding="utf-8",
)
