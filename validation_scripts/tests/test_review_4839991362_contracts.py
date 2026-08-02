from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[2]


class Review4839991362Contracts(unittest.TestCase):
    def _section(self, path: str, start: str, end: str) -> str:
        text = (ROOT / path).read_text(encoding="utf-8")
        self.assertIn(start, text)
        self.assertIn(end, text)
        return text.split(start, 1)[1].split(end, 1)[0]

    def test_evidence_qc_preserves_complete_canonical_v3_package(self) -> None:
        section = self._section(
            "docs/llm_prompts/v1/07_PROMPT_0_5_Evidence_QC.md",
            "Each evidence_complete_and_source_claim_covered item must include:",
            "Each addable_hold_source_gap item must include:",
        )
        for required in (
            "`structural_value_override_applied: true`",
            "`structural_value_override_reason`",
            "`anchor_classes[]`",
            "`incremental_information`",
            "`decision_relevance`",
            "`baseline_expectation_changed`",
            "`evidence_needed_for_stage_b[]`",
            "`next_confirmation_points[]`",
            "`why_execution_event_not_required`",
            "`prior_state`",
            "`new_verified_fact`",
            "`changed_judgment`",
            "current-run source lineage",
        ):
            self.assertIn(required, section)
        self.assertIn("byte-for-byte from Baseline Revalidation", section)

    def test_content_polish_preserves_complete_canonical_v3_package(self) -> None:
        section = self._section(
            "docs/llm_prompts/v1/08_PROMPT_0_6_Content_Polish.md",
            "Each content_enriched_and_language_polished item must include:",
            "Each content_hold_claim_narrowing_needed item must include:",
        )
        for required in (
            "`structural_value_override_applied: true`",
            "`structural_value_override_reason`",
            "`anchor_classes[]`",
            "`incremental_information`",
            "`decision_relevance`",
            "`baseline_expectation_changed`",
            "`evidence_needed_for_stage_b[]`",
            "`next_confirmation_points[]`",
            "`why_execution_event_not_required`",
            "`prior_state`",
            "`new_verified_fact`",
            "`changed_judgment`",
            "current-run source lineage",
        ):
            self.assertIn(required, section)
        self.assertIn("byte-for-byte from Evidence QC", section)
        self.assertIn("must not summarize away", section)

    def test_final_qc_uses_strict_related_contract_in_prompt_and_generator(self) -> None:
        expected = "`related_lifecycle_check.py --require-contract`"
        old = "`related_lifecycle_check.py`,"
        for path in (
            "docs/llm_prompts/v1/09_PROMPT_0_7_Final_QC.md",
            "validation_scripts/apply_prompt_contract_overlays.py",
        ):
            text = (ROOT / path).read_text(encoding="utf-8")
            self.assertIn(expected, text)
            self.assertNotIn(old, text)


if __name__ == "__main__":
    unittest.main()
