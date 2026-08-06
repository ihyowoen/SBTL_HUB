import unittest
from pathlib import Path


class StructuralV3Review4839334318Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.prompt = Path(
            "docs/llm_prompts/v1/07_PROMPT_0_5_Evidence_QC.md"
        ).read_text(encoding="utf-8")

    def test_later_operational_guard_uses_exactly_one_two_path_contract(self) -> None:
        self.assertIn(
            "require the preserved `anchor_path_validation` to prove exactly one source-backed route",
            self.prompt,
        )
        self.assertIn("`selected_anchor_path = execution`", self.prompt)
        self.assertIn("`selected_anchor_path = v3_non_execution`", self.prompt)
        self.assertIn("`addable_hold_anchor_path_gap`", self.prompt)
        self.assertIn(
            "Do not require a conventional execution anchor when the complete V3 non-execution route is the single validated path.",
            self.prompt,
        )

    def test_residual_execution_only_guard_is_absent(self) -> None:
        self.assertNotIn(
            "For every candidate with `format_risk_tags` such as product/demo/PoC/component/interview/roundup/commentary/speech/personnel/partnership, require:\n\n- `execution_anchor_type` is not null;",
            self.prompt,
        )
        self.assertNotIn("`addable_hold_execution_anchor_gap`", self.prompt)


if __name__ == "__main__":
    unittest.main()
