from __future__ import annotations

import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
STAGE_07C = ROOT / "docs/llm_prompts/v1/09A_PROMPT_0_7C_INDEPENDENT_COMPLETENESS_REVIEW.md"


class TestReview4840691969Contracts(unittest.TestCase):
    def setUp(self):
        self.text = STAGE_07C.read_text(encoding="utf-8")

    def test_independent_review_reads_all_governing_v3_contracts(self):
        required_paths = (
            "docs/EDITORIAL_VALUE_AND_COMPLETENESS_STANDARD.md",
            "docs/STRUCTURAL_NEWS_VALUE_SELECTION.md",
            "docs/llm_prompts/v1/01A_PROMPT_0_1S_Structural_Value_Override.md",
            "docs/RELATED_LIFECYCLE_CONTRACT.md",
        )
        authority_start = self.text.index("**Authority hierarchy:**")
        input_end = self.text.index("## Review rounds", authority_start)
        preflight = self.text[authority_start:input_end]
        for path in required_paths:
            self.assertIn(path, preflight)

    def test_v3_preflight_is_machine_accounted_and_fail_closed(self):
        for field in (
            '"governing_contracts_read"',
            '"governing_contracts_same_revision"',
            '"v3_contract_preflight_passed"',
        ):
            self.assertIn(field, self.text)
        self.assertIn("v3_contract_preflight_passed != true", self.text)
        self.assertIn(
            "Only a documented `PASS_WITH_DECLARED_RESIDUAL_RISK` with "
            "`v3_contract_preflight_passed: true` may authorize Prompt 0.8.",
            self.text,
        )

    def test_contracts_cannot_be_replaced_by_summaries(self):
        self.assertIn(
            "no required document was substituted by a summary or downstream prompt excerpt",
            self.text,
        )
        self.assertIn(
            "was replaced by a summary/excerpt",
            self.text,
        )


if __name__ == "__main__":
    unittest.main()
