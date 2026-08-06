from __future__ import annotations

import unittest
from pathlib import Path

# This regression locks the complete Prompt 0.4 producer package consumed by Prompt 0.5.
ROOT = Path(__file__).resolve().parents[2]
BASELINE = ROOT / "docs/llm_prompts/v1/06_PROMPT_0_4_Baseline_Revalidation.md"
EVIDENCE = ROOT / "docs/llm_prompts/v1/07_PROMPT_0_5_Evidence_QC.md"


class TestReview4840624684Contracts(unittest.TestCase):
    def test_baseline_v3_package_contains_every_reviewed_canonical_field(self):
        text = BASELINE.read_text(encoding="utf-8")
        start = text.index("- V3 override package (required and preserved byte-for-byte")
        end = text.index("- event_fingerprint", start)
        package = text[start:end]
        for field in (
            "structural_value_override_reason",
            "next_confirmation_points[]",
        ):
            self.assertIn(field, package)

    def test_evidence_qc_consumes_the_same_fields(self):
        text = EVIDENCE.read_text(encoding="utf-8")
        self.assertIn("structural_value_override_reason", text)
        self.assertIn("next_confirmation_points[]", text)


if __name__ == "__main__":
    unittest.main()
