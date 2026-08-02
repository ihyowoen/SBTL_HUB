from pathlib import Path


def replace_once(path: str, before: str, after: str, label: str) -> None:
    p = Path(path)
    text = p.read_text(encoding="utf-8")
    count = text.count(before)
    if count != 1:
        raise RuntimeError(f"{label}: expected exactly one match, got {count}")
    p.write_text(text.replace(before, after, 1), encoding="utf-8")


replace_once(
    "docs/STRUCTURAL_NEWS_VALUE_SELECTION.md",
    "| REVIEW | PASS/REVIEW | 55–100 | `candidate_review_pool[]` or `structural_signal_review_pool[]` with a mandatory rescue question |\n| PASS/REVIEW | REVIEW | any | candidate review, earnings deep dive, reinforcement, or watchlist |",
    "| REVIEW | PASS/REVIEW | 55–100 | `candidate_review_pool[]` with `review_pool_subtype: structural_signal_review` and a mandatory rescue question |\n| PASS/REVIEW | REVIEW | any | `candidate_review_pool[]` with the applicable subtype (including `earnings_deep_dive`), reinforcement, or watchlist |",
    "canonical routing matrix",
)
replace_once(
    "docs/STRUCTURAL_NEWS_VALUE_SELECTION.md",
    "- `candidate_review_pool[]` — potentially cardable after bounded clarification;\n- `structural_signal_review_pool[]` — high structural potential requiring source, denominator, stage, or comparison rescue;\n- `earnings_deep_dive_pool[]` — earnings candidate lacking full call/Q&A or prior-period comparison;",
    "- `candidate_review_pool[]` — the only top-level candidate review partition; every item must include `review_pool_subtype`.\n  - `review_pool_subtype: structural_signal_review` — high structural potential requiring source, denominator, stage, or comparison rescue;\n  - `review_pool_subtype: earnings_deep_dive` — earnings candidate lacking full call/Q&A or prior-period comparison;\n- `structural_signal_review_pool[]` and `earnings_deep_dive_pool[]` are prohibited as standalone top-level arrays; they are subtype views of `candidate_review_pool[]` only;",
    "canonical review partitions",
)
replace_once(
    "docs/llm_prompts/v1/03_PROMPT_0_3_Stage_C_r0.md",
    "- fact_sources\n- anchor_path_validation\n  - selected_anchor_path: execution|v3_non_execution\n  - anchor_path_qc_passed: true\n  - execution_anchor_qc_status: pass|not_applicable\n  - structural_value_override_qc_status: pass|not_applicable\n  - non_applicable_anchor_path_reason\n- stage_c_findings",
    "- fact_sources\n- `anchor_path_validation` only when the accepted item has non-empty `format_risk_tags`\n  - selected_anchor_path: execution|v3_non_execution\n  - anchor_path_qc_passed: true\n  - execution_anchor_qc_status: pass|not_applicable\n  - structural_value_override_qc_status: pass|not_applicable\n  - non_applicable_anchor_path_reason\n- ordinary accepted items without `format_risk_tags` must not invent or be required to emit `anchor_path_validation`\n- stage_c_findings",
    "Stage C accepted schema scope",
)
new_followup_rule = "- `distinct_follow_up` requires a valid non-empty `fresh_follow_up_anchor`, a valid `fresh_follow_up_anchor_class` under `docs/RELATED_LIFECYCLE_CONTRACT.md`, and non-empty `incremental_fact_vs_predecessor` plus `changed_judgment_vs_predecessor`. A conventional execution anchor is required only when the selected anchor class is `execution`; valid policy, financial, strategic, technology, or probability anchors are permitted by the shared contract."
replace_once(
    "docs/llm_prompts/v1/03_PROMPT_0_3_Stage_C_r0.md",
    "- `distinct_follow_up` requires a direct fresh execution anchor.",
    new_followup_rule,
    "Stage C related overlay",
)
replace_once(
    "validation_scripts/apply_prompt_contract_overlays.py",
    "- `distinct_follow_up` requires a direct fresh execution anchor.",
    new_followup_rule,
    "Stage C overlay generator",
)
replace_once(
    "docs/llm_prompts/v1/09A_PROMPT_0_7C_INDEPENDENT_COMPLETENESS_REVIEW.md",
    "### 3. Event-stage challenge\n\nVerify the exact stage, fresh execution anchor, predecessor, successor, contrary signals, and next milestone.",
    "### 3. Event-stage and anchor-path challenge\n\nFor every format-risk proposed card, verify the exact stage and the preserved `anchor_path_validation` using an exactly-one two-path check:\n\n1. `execution`: source-backed fresh execution anchor, valid type/strength, and the V3 override route marked not applicable with a specific reason; or\n2. `v3_non_execution`: complete source-backed Structural Value Override with valid `anchor_classes[]`, item-specific evidence targets, specific execution-not-required rationale, before-after change, changed judgment, and the execution route marked not applicable with a specific reason.\n\nAlso verify predecessor, successor, contrary signals, and next milestone. Do not reject a valid V3 non-execution route solely because no conventional execution event exists.",
    "0.7C anchor challenge",
)
replace_once(
    "docs/llm_prompts/v1/09A_PROMPT_0_7C_INDEPENDENT_COMPLETENESS_REVIEW.md",
    '  "review_pool_rescue_complete": false,\n  "must_report_candidates_accounted": false,',
    '  "review_pool_rescue_complete": false,\n  "must_report_candidates_accounted": false,\n  "format_risk_anchor_path_review_complete": false,\n  "anchor_path_review_results": [],',
    "0.7C output schema",
)
replace_once(
    "docs/llm_prompts/v1/09A_PROMPT_0_7C_INDEPENDENT_COMPLETENESS_REVIEW.md",
    "- a follow-up lacks an execution-stage comparison;",
    "- a format-risk proposed card lacks exactly one source-backed `execution` or complete `v3_non_execution` route, or has missing/contradictory route metadata;\n- a follow-up lacks a valid fresh V3 anchor-class comparison, incremental fact, or changed judgment versus its predecessor;",
    "0.7C blockers",
)

Path("validation_scripts/tests/test_structural_v3_review_latest.py").write_text(
    '''from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[2]


class StructuralV3LatestReviewTests(unittest.TestCase):
    def read(self, path):
        return (ROOT / path).read_text(encoding="utf-8")

    def test_canonical_review_pools_are_subtypes(self):
        text = self.read("docs/STRUCTURAL_NEWS_VALUE_SELECTION.md")
        self.assertIn("review_pool_subtype: structural_signal_review", text)
        self.assertIn("review_pool_subtype: earnings_deep_dive", text)
        self.assertIn("prohibited as standalone top-level arrays", text)

    def test_stage_c_anchor_path_is_format_risk_only(self):
        text = self.read("docs/llm_prompts/v1/03_PROMPT_0_3_Stage_C_r0.md")
        self.assertIn("anchor_path_validation` only when the accepted item has non-empty `format_risk_tags", text)
        self.assertIn("ordinary accepted items without `format_risk_tags` must not invent", text)

    def test_stage_c_followup_accepts_v3_anchor_classes(self):
        text = self.read("docs/llm_prompts/v1/03_PROMPT_0_3_Stage_C_r0.md")
        generator = self.read("validation_scripts/apply_prompt_contract_overlays.py")
        self.assertIn("fresh_follow_up_anchor_class", text)
        self.assertIn("fresh_follow_up_anchor_class", generator)
        self.assertNotIn("`distinct_follow_up` requires a direct fresh execution anchor.", text)
        self.assertNotIn("`distinct_follow_up` requires a direct fresh execution anchor.", generator)

    def test_independent_review_uses_two_path_gate(self):
        text = self.read("docs/llm_prompts/v1/09A_PROMPT_0_7C_INDEPENDENT_COMPLETENESS_REVIEW.md")
        self.assertIn("exactly-one two-path check", text)
        self.assertIn("format_risk_anchor_path_review_complete", text)
        self.assertIn("valid fresh V3 anchor-class comparison", text)


if __name__ == "__main__":
    unittest.main()
''',
    encoding="utf-8",
)
