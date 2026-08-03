from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def replace_once(path: Path, old: str, new: str, label: str) -> None:
    text = path.read_text(encoding="utf-8")
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected exactly one match, found {count}")
    path.write_text(text.replace(old, new, 1), encoding="utf-8")


validator = ROOT / "validation_scripts/stage_lineage_contract_check.py"
replace_once(
    validator,
    """STAGE_A_V3_NARRATIVE_FIELDS = (\n    'structural_value_override_reason',\n    'incremental_information',\n    'decision_relevance',\n    'why_execution_event_not_required',\n""",
    """STAGE_A_V3_NARRATIVE_FIELDS = (\n    'structural_value_override_reason',\n    'incremental_information',\n    'decision_relevance',\n    'baseline_expectation_changed',\n    'why_execution_event_not_required',\n""",
    "include baseline change in narrative validation",
)
replace_once(
    validator,
    """    if spec.get('baseline_expectation_changed') is not True:\n        messages.append(f'{spec_id}: baseline_expectation_changed must be true for v3_non_execution')\n        valid = False\n\n""",
    "",
    "remove boolean-only baseline requirement",
)

fixture = ROOT / "validation_scripts/tests/test_review_4840783305_contracts.py"
replace_once(
    fixture,
    '            "baseline_expectation_changed": True,\n',
    '            "baseline_expectation_changed": "The baseline changed from discretionary eligibility to mandatory screening.",\n',
    "update canonical baseline fixture",
)

final_qc = ROOT / "docs/llm_prompts/v1/09_PROMPT_0_7_Final_QC.md"
replace_once(
    final_qc,
    """- `changed_judgment`\n- applicable uncertainty / probability-change fields\n- applicable baseline-expectation / before-after fields\n""",
    """- `changed_judgment`\n- `uncertainty_resolved`\n- `remaining_uncertainty`\n- applicable probability-change fields\n- applicable baseline-expectation / before-after fields\n""",
    "enumerate Final QC uncertainty fields",
)

merge_prep = ROOT / "docs/llm_prompts/v1/10_PROMPT_0_8_GitHub_Merge_Prep.md"
replace_once(
    merge_prep,
    """- `changed_judgment`;\n- applicable uncertainty / probability-change fields;\n- applicable baseline-expectation / before-after fields;\n""",
    """- `changed_judgment`;\n- `uncertainty_resolved`;\n- `remaining_uncertainty`;\n- applicable probability-change fields;\n- applicable baseline-expectation / before-after fields;\n""",
    "enumerate merge-prep uncertainty fields",
)

test = ROOT / "validation_scripts/tests/test_review_baseline_uncertainty_contracts.py"
test.write_text(
    '''"""Regression coverage for the latest PR 233 baseline/uncertainty review."""\n\nfrom __future__ import annotations\n\nimport copy\nimport io\nimport unittest\nfrom contextlib import redirect_stdout\nfrom pathlib import Path\n\nfrom validation_scripts import stage_lineage_contract_check as lineage\nfrom validation_scripts.tests.test_review_4840844831_contracts import (\n    TestReview4840844831Contracts,\n)\n\nROOT = Path(__file__).resolve().parents[2]\nFINAL_QC = ROOT / "docs/llm_prompts/v1/09_PROMPT_0_7_Final_QC.md"\nMERGE_PREP = ROOT / "docs/llm_prompts/v1/10_PROMPT_0_8_GitHub_Merge_Prep.md"\n\n\nclass TestLatestBaselineUncertaintyContracts(unittest.TestCase):\n    def base_spec(self):\n        return TestReview4840844831Contracts().base_spec()\n\n    def run_stage_a(self, spec):\n        stream = io.StringIO()\n        with redirect_stdout(stream):\n            result = lineage.check_stage_a({"strict_passed_spec": [spec]})\n        return result, stream.getvalue()\n\n    def test_item_specific_baseline_change_narrative_passes(self):\n        spec = self.base_spec()\n        spec["baseline_expectation_changed"] = (\n            "The baseline changed from optional screening to mandatory eligibility review."\n        )\n        result, output = self.run_stage_a(spec)\n        self.assertEqual(result, 0, output)\n\n    def test_boolean_baseline_change_is_rejected(self):\n        spec = copy.deepcopy(self.base_spec())\n        spec["baseline_expectation_changed"] = True\n        result, output = self.run_stage_a(spec)\n        self.assertEqual(result, 1)\n        self.assertIn(\n            "baseline_expectation_changed must be item-specific narrative text",\n            output,\n        )\n\n    def test_placeholder_baseline_change_is_rejected(self):\n        spec = copy.deepcopy(self.base_spec())\n        spec["baseline_expectation_changed"] = "currently unknown"\n        result, output = self.run_stage_a(spec)\n        self.assertEqual(result, 1)\n        self.assertIn(\n            "baseline_expectation_changed must be item-specific narrative text",\n            output,\n        )\n\n    def test_final_qc_and_merge_prep_preserve_uncertainty_fields_by_name(self):\n        final_text = FINAL_QC.read_text(encoding="utf-8")\n        final_start = final_text.index(\n            "For every format-risk `publish_ready[]` item with `selected_anchor_path = v3_non_execution`"\n        )\n        final_end = final_text.index("- evidence_complete: true", final_start)\n        final_block = final_text[final_start:final_end]\n\n        merge_text = MERGE_PREP.read_text(encoding="utf-8")\n        merge_start = merge_text.index("For `selected_anchor_path: v3_non_execution`")\n        merge_end = merge_text.index("If metadata is missing", merge_start)\n        merge_block = merge_text[merge_start:merge_end]\n\n        for block in (final_block, merge_block):\n            self.assertIn("`uncertainty_resolved`", block)\n            self.assertIn("`remaining_uncertainty`", block)\n            self.assertNotIn("applicable uncertainty / probability-change fields", block)\n\n\nif __name__ == "__main__":\n    unittest.main()\n''',
    encoding="utf-8",
)
