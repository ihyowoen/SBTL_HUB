#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path


def replace_once(path: str, old: str, new: str, label: str) -> None:
    p = Path(path)
    text = p.read_text(encoding="utf-8")
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected exactly one target, found {count}")
    p.write_text(text.replace(old, new, 1), encoding="utf-8")


def append_once(path: str, marker: str, block: str) -> None:
    p = Path(path)
    text = p.read_text(encoding="utf-8")
    if marker in text:
        return
    p.write_text(text.rstrip() + "\n\n" + block.strip() + "\n", encoding="utf-8")


TEN_DOCS = """Before starting, read the latest versions of all required workflow docs from GitHub main:

1. docs/FACT_DISCIPLINE.md
2. docs/STRUCTURAL_NEWS_VALUE_SELECTION.md
3. docs/llm_prompts/v1/01A_PROMPT_0_1S_Structural_Value_Override.md
4. docs/PROMPT_ABC_DEFAULT_MODE.md
5. docs/PROMPT_ABC_SUPPORTING_RULES.md
6. docs/FUTURE_CARD_STANDARD_FULL_SCHEMA.md
7. docs/CARD_ID_STANDARD.md
8. docs/WORKFLOW.md
9. docs/OPERATIONS.md
10. docs/POST_ACCEPTANCE_CONTENT_ENRICHMENT_QC.md

Required-doc rule:

All 10 documents above are mandatory."""

EIGHT_DOCS = """Before starting, read the latest versions of all required workflow docs from GitHub main:

1. docs/FACT_DISCIPLINE.md
2. docs/PROMPT_ABC_DEFAULT_MODE.md
3. docs/PROMPT_ABC_SUPPORTING_RULES.md
4. docs/FUTURE_CARD_STANDARD_FULL_SCHEMA.md
5. docs/CARD_ID_STANDARD.md
6. docs/WORKFLOW.md
7. docs/OPERATIONS.md
8. docs/POST_ACCEPTANCE_CONTENT_ENRICHMENT_QC.md

Required-doc rule:

All 8 documents above are mandatory."""

# 1) Final QC must emit the route metadata that Prompt 0.8 consumes.
replace_once(
    "docs/llm_prompts/v1/09_PROMPT_0_7_Final_QC.md",
    """- urls
- related
- fact_sources
- evidence_complete: true""",
    """- urls
- related
- fact_sources

For every format-risk `publish_ready[]` item, the following route fields are mandatory and must be copied from the same-run Content Polish / Evidence QC lineage without alteration:

- `selected_anchor_path: execution|v3_non_execution`
- `anchor_path_qc_passed: true`
- `execution_anchor_qc_status: pass|not_applicable`
- `structural_value_override_qc_status: pass|not_applicable`
- `non_applicable_anchor_path_reason`

Exactly one route status must be `pass`; the other must be `not_applicable` with a specific reason. Missing, contradictory, dual-pass, or dual-not-applicable route metadata requires `final_qc_hold` or return to the earliest defective stage and must not enter `publish_ready[]`.

- evidence_complete: true""",
    "Final QC publish_ready route schema",
)

# 2) Stage C must validate the canonical plural anchor_classes[] field.
replace_once(
    "docs/llm_prompts/v1/03_PROMPT_0_3_Stage_C_r0.md",
    "- one valid non-execution `anchor_class`",
    "- `anchor_classes[]` containing at least one valid non-execution anchor class permitted by the canonical V3 policy",
    "Stage C canonical anchor_classes field",
)

# 3) Stage B revise must consume, preserve, or resolve anchor-path state.
replace_once(
    "docs/llm_prompts/v1/04_PROMPT_0_2R_Stage_B_Revise.md",
    EIGHT_DOCS,
    TEN_DOCS,
    "Stage B revise required docs",
)
replace_once(
    "docs/llm_prompts/v1/04_PROMPT_0_2R_Stage_B_Revise.md",
    """If any non-revise_required item is mixed in, exclude it and report mixed_input_excluded.

Role of this pass:""",
    """If any non-revise_required item is mixed in, exclude it and report mixed_input_excluded.

Anchor-path revise input rule:

For every format-risk `revise_required[]` item, consume the complete Stage C `anchor_path_validation` object.

- If the selected route was already settled and only visible wording requires revision, preserve `anchor_path_validation` byte-for-byte.
- If Stage C emitted `selected_anchor_path: unresolved`, this pass may resolve the route only from already-authorized, source-backed evidence in the current run. It must select exactly one of `execution` or `v3_non_execution`, set `anchor_path_qc_passed: true`, set exactly one route status to `pass`, set the other to `not_applicable`, and provide a specific `non_applicable_anchor_path_reason`.
- If the existing evidence cannot resolve exactly one route, do not manufacture a passing object. Route the item to the appropriate revise-blocked state and preserve the unresolved object plus the remaining issue.
- Source augmentation remains subject to the explicit authorization rule below.

Role of this pass:""",
    "Stage B revise anchor input rule",
)
replace_once(
    "docs/llm_prompts/v1/04_PROMPT_0_2R_Stage_B_Revise.md",
    """- related
- fact_sources
- stage_b_revise_only: true""",
    """- related
- fact_sources
- `anchor_path_validation` for every format-risk item
- `anchor_path_resolution_action: preserved|resolved_from_unresolved`
- stage_b_revise_only: true""",
    "Stage B revise item schema",
)
replace_once(
    "docs/llm_prompts/v1/04_PROMPT_0_2R_Stage_B_Revise.md",
    """- revision_change_log[]
- decision_ledger[]

Each revised_draft_card must include:""",
    """- revision_change_log[]
- decision_ledger[]
- anchor_path_revision_summary
  - format_risk_input_count
  - anchor_path_preserved_count
  - anchor_path_resolved_count
  - anchor_path_still_unresolved_count

Each revised_draft_card must include:""",
    "Stage B revise root accounting",
)

# 4) Stage C revise must validate the resolved route and emit it for Prompt 0.4.
replace_once(
    "docs/llm_prompts/v1/05_PROMPT_0_3R_Stage_C_Revise.md",
    EIGHT_DOCS,
    TEN_DOCS,
    "Stage C revise required docs",
)
replace_once(
    "docs/llm_prompts/v1/05_PROMPT_0_3R_Stage_C_Revise.md",
    """- verify signal/category changes are justified
- verify publish_ready remains false

Accounting rule:""",
    """- verify signal/category changes are justified
- verify publish_ready remains false
- for every format-risk item, consume the Stage B revise `anchor_path_validation` and validate exactly one source-backed route
- accept a format-risk item only when `selected_anchor_path` is `execution` or `v3_non_execution`, `anchor_path_qc_passed: true`, exactly one route status is `pass`, and the other is `not_applicable` with a specific reason
- if the route remains unresolved, contradictory, dual-pass, or unsupported, place the item in `revise_required_again` or an appropriate non-accepted state; never certify `accepted_fact_safe`

Accounting rule:""",
    "Stage C revise validation rules",
)
replace_once(
    "docs/llm_prompts/v1/05_PROMPT_0_3R_Stage_C_Revise.md",
    """- claim_coverage_review[]

Each accepted_fact_safe item must include:""",
    """- claim_coverage_review[]
- anchor_path_revision_validation_summary
  - format_risk_input_count
  - accepted_with_execution_path_count
  - accepted_with_v3_non_execution_path_count
  - unresolved_or_failed_path_count

Each accepted_fact_safe item must include:""",
    "Stage C revise root accounting",
)
replace_once(
    "docs/llm_prompts/v1/05_PROMPT_0_3R_Stage_C_Revise.md",
    """- related
- fact_sources
- stage_c_revise_only: true""",
    """- related
- fact_sources
- `anchor_path_validation` for every format-risk item, with a passing two-path schema
- stage_c_revise_only: true""",
    "Stage C revise accepted schema",
)
replace_once(
    "docs/llm_prompts/v1/05_PROMPT_0_3R_Stage_C_Revise.md",
    """- source_spec_id
- remaining_issue_type
- remaining_issue_detail""",
    """- source_spec_id
- `anchor_path_validation` when the item is format-risk, preserving the honest unresolved or failed state
- remaining_issue_type
- remaining_issue_detail""",
    "Stage C revise unresolved schema",
)

# 5) Retrospective must treat a complete V3 override as a valid alternative path.
replace_once(
    "docs/llm_prompts/v1/13_PROMPT_1_1_Retrospective.md",
    "5. Whether any product/demo/PoC/component/interview/commentary/personnel/consumer anecdote entered strict_passed_spec without a hard commercial/policy event.",
    "5. Whether any product/demo/PoC/component/interview/commentary/personnel/consumer anecdote entered `strict_passed_spec[]` without either a source-backed concrete execution anchor or a complete V3 non-execution Structural Value Override package.",
    "Retrospective selector forensic rule",
)
replace_once(
    "docs/llm_prompts/v1/13_PROMPT_1_1_Retrospective.md",
    "The following patterns must not enter `strict_passed_spec[]` unless a concrete battery/grid/ESS/EV/materials execution anchor is present:",
    "The following patterns must not enter `strict_passed_spec[]` unless either a source-backed concrete battery/grid/ESS/EV/materials execution anchor or a complete V3 non-execution Structural Value Override package is present:",
    "Retrospective negative-filter gate",
)
replace_once(
    "docs/llm_prompts/v1/13_PROMPT_1_1_Retrospective.md",
    "- trend/explainer items without a fresh execution or data-release anchor",
    "- trend/explainer items without either a fresh execution/data-release anchor or a complete V3 non-execution Structural Value Override package",
    "Retrospective trend filter",
)

# 6) Add explicit regression coverage for all four review findings.
TEST_MARKER = "class StructuralV3Review4838187744RegressionTest"
TEST_BLOCK = r'''
class StructuralV3Review4838187744RegressionTest(unittest.TestCase):
    @staticmethod
    def read_prompt(path: str) -> str:
        return (ROOT.parent / path).read_text(encoding="utf-8")

    def test_final_qc_publish_ready_emits_route_metadata(self):
        text = self.read_prompt("docs/llm_prompts/v1/09_PROMPT_0_7_Final_QC.md")
        self.assertIn("For every format-risk `publish_ready[]` item", text)
        for field in (
            "selected_anchor_path: execution|v3_non_execution",
            "anchor_path_qc_passed: true",
            "execution_anchor_qc_status: pass|not_applicable",
            "structural_value_override_qc_status: pass|not_applicable",
            "non_applicable_anchor_path_reason",
        ):
            self.assertIn(field, text)

    def test_revise_loop_preserves_and_validates_anchor_path(self):
        stage_b_revise = self.read_prompt("docs/llm_prompts/v1/04_PROMPT_0_2R_Stage_B_Revise.md")
        stage_c_revise = self.read_prompt("docs/llm_prompts/v1/05_PROMPT_0_3R_Stage_C_Revise.md")
        for text in (stage_b_revise, stage_c_revise):
            self.assertIn("All 10 documents above are mandatory.", text)
            self.assertNotIn("All 8 documents above are mandatory.", text)
            self.assertIn("anchor_path_validation", text)
        self.assertIn("anchor_path_resolution_action: preserved|resolved_from_unresolved", stage_b_revise)
        self.assertIn("accepted_with_v3_non_execution_path_count", stage_c_revise)

    def test_stage_c_uses_canonical_anchor_classes_array(self):
        text = self.read_prompt("docs/llm_prompts/v1/03_PROMPT_0_3_Stage_C_r0.md")
        self.assertIn("`anchor_classes[]` containing at least one valid non-execution anchor class", text)
        self.assertNotIn("one valid non-execution `anchor_class`", text)

    def test_retrospective_accepts_complete_v3_override(self):
        text = self.read_prompt("docs/llm_prompts/v1/13_PROMPT_1_1_Retrospective.md")
        self.assertIn("without either a source-backed concrete execution anchor or a complete V3 non-execution Structural Value Override package", text)
        self.assertIn("unless either a source-backed concrete battery/grid/ESS/EV/materials execution anchor or a complete V3 non-execution Structural Value Override package is present", text)
        self.assertNotIn("without a hard commercial/policy event", text)
        self.assertNotIn("unless a concrete battery/grid/ESS/EV/materials execution anchor is present", text)
'''
replace_once(
    "validation_scripts/tests/test_workflow_contracts.py",
    "\n\nclass RelatedMalformedAnchorClassTest(unittest.TestCase):",
    "\n\n" + TEST_BLOCK.strip() + "\n\n\nclass RelatedMalformedAnchorClassTest(unittest.TestCase):",
    "Review 4838187744 regression tests",
)

append_once(
    "docs/validation/STRUCTURAL_NEWS_VALUE_V3_VALIDATION_20260802.md",
    "REVIEW_4838187744_ADDRESSING",
    """
## REVIEW_4838187744_ADDRESSING

The review's four findings are addressed as one end-to-end contract correction:

- Final QC now emits item-level anchor-path metadata required by Prompt 0.8.
- Stage B/C revise prompts consume, preserve, resolve, validate, and carry `anchor_path_validation` into Baseline Revalidation.
- Stage C validates the canonical `anchor_classes[]` array rather than an undefined singular key.
- Prompt 1.1 retrospective recognizes a complete source-backed V3 non-execution override as the alternative to an execution anchor.

Regression coverage is included in `validation_scripts/tests/test_workflow_contracts.py`.
""",
)

print("review 4838187744 patch applied")
