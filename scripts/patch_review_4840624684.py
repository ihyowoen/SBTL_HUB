#!/usr/bin/env python3
from pathlib import Path


def replace_once(path: Path, old: str, new: str, label: str) -> None:
    text = path.read_text(encoding="utf-8")
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected exactly one match, found {count}")
    path.write_text(text.replace(old, new, 1), encoding="utf-8")


prompt = Path("docs/llm_prompts/v1/06_PROMPT_0_4_Baseline_Revalidation.md")
replace_once(
    prompt,
    """  - structural_value_override_applied: true\n  - anchor_classes[] with at least one valid non-execution class\n""",
    """  - structural_value_override_applied: true\n  - structural_value_override_reason\n  - anchor_classes[] with at least one valid non-execution class\n""",
    "baseline V3 override reason",
)
replace_once(
    prompt,
    """  - baseline_expectation_changed\n  - decision_relevance\n- event_fingerprint\n""",
    """  - baseline_expectation_changed\n  - decision_relevance\n  - next_confirmation_points[]\n- event_fingerprint\n""",
    "baseline V3 next confirmation points",
)

test_path = Path("validation_scripts/tests/test_review_4840624684_contracts.py")
test_path.write_text('''from __future__ import annotations\n\nimport unittest\nfrom pathlib import Path\n\nROOT = Path(__file__).resolve().parents[2]\nBASELINE = ROOT / "docs/llm_prompts/v1/06_PROMPT_0_4_Baseline_Revalidation.md"\nEVIDENCE = ROOT / "docs/llm_prompts/v1/07_PROMPT_0_5_Evidence_QC.md"\n\n\nclass TestReview4840624684Contracts(unittest.TestCase):\n    def test_baseline_v3_package_contains_every_reviewed_canonical_field(self):\n        text = BASELINE.read_text(encoding="utf-8")\n        start = text.index("- V3 override package (required and preserved byte-for-byte")\n        end = text.index("- event_fingerprint", start)\n        package = text[start:end]\n        for field in (\n            "structural_value_override_reason",\n            "next_confirmation_points[]",\n        ):\n            self.assertIn(field, package)\n\n    def test_evidence_qc_consumes_the_same_fields(self):\n        text = EVIDENCE.read_text(encoding="utf-8")\n        self.assertIn("structural_value_override_reason", text)\n        self.assertIn("next_confirmation_points[]", text)\n\n\nif __name__ == "__main__":\n    unittest.main()\n''', encoding="utf-8")
