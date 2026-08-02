#!/usr/bin/env python3
from pathlib import Path


def replace_once(path: str, old: str, new: str, label: str) -> None:
    p = Path(path)
    text = p.read_text(encoding="utf-8")
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected one match, found {count}")
    p.write_text(text.replace(old, new, 1), encoding="utf-8")


# Prompt 0.8 canonical entry point: explicitly supersede the subordinate execution-only rule
# and materialize the V3 route schema at merge preparation.
replace_once(
    "docs/llm_prompts/v1/10_PROMPT_0_8_GitHub_Merge_Prep.md",
    """- replace-all is the only permitted merge model;\n- a fixed eight-document read is complete governance proof.\n\nAll compatible evidence, lineage, duplicate, schema, source-diversity, accounting, PR, and production-boundary safeguards remain in force.\n\n## 6. Exit\n""",
    """- replace-all is the only permitted merge model;\n- a fixed eight-document read is complete governance proof;\n- a conventional execution event is the sole valid strict-pass route for a format-risk card;\n- a merge-prep lineage gate may omit the selected V3 anchor path, route-specific statuses, or non-applicable-route reason.\n\nAll compatible evidence, lineage, duplicate, schema, source-diversity, accounting, PR, and production-boundary safeguards remain in force.\n\n## 5A. V3 anchor-path merge-prep gate\n\nThe subordinate legacy execution-only overlay is non-operative. Before any format-risk `publish_ready[]` card may enter `pr_candidate_payload`, Prompt 0.8 must verify the Final QC output preserves exactly one source-backed route:\n\n1. `selected_anchor_path: execution` with `execution_anchor_qc_status: pass` and `structural_value_override_qc_status: not_applicable`; or\n2. `selected_anchor_path: v3_non_execution` with `structural_value_override_qc_status: pass` and `execution_anchor_qc_status: not_applicable`.\n\nBoth routes require:\n\n- `anchor_path_qc_passed: true`;\n- a specific `non_applicable_anchor_path_reason`;\n- exact current-run lineage from Stage A through Final QC;\n- no route switch, status rewrite, or evidence laundering during merge preparation.\n\nThe execution route must retain its source-backed execution evidence. The V3 non-execution route must retain its verified anchor class, item-specific evidence targets, before-after chain, changed judgment, and specific `why_execution_event_not_required`. Absence of a conventional execution event is not itself a defect when the V3 non-execution route passed.\n\nIf metadata is missing, contradictory, stale, or unsupported, return:\n\n```text\nstatus: BLOCKED_FINAL_QC_ANCHOR_PATH_INVALID\nmerge_prep_hold_count: [...]\nno PR candidate emitted for affected items\n```\n\nAdd to Prompt 0.8 JSON:\n\n```json\n\"lineage_merge_gate\": {\n  \"final_qc_lineage_passed\": true,\n  \"anchor_path_lineage_passed\": true,\n  \"publish_ready_lineage_checked_count\": 0,\n  \"execution_path_checked_count\": 0,\n  \"v3_non_execution_path_checked_count\": 0,\n  \"anchor_path_hold_count\": 0,\n  \"github_ready_allowed\": true\n}\n```\n\n## 6. Exit\n""",
    "Prompt 0.8 V3 merge gate",
)

# The subordinate legacy body is still assembled, so align the active overlay itself rather
# than relying only on a supersession sentence in the canonical entry point.
replace_once(
    "docs/llm_prompts/v1/legacy/10_PROMPT_0_8_GitHub_Merge_Prep_LEGACY_BODY.md",
    """## Execution-anchor and selector-lineage safety overlay — 2026-05-05\n\nThis overlay is downstream of the Stage A safe-selector integrated rule. It prevents post-acceptance steps from laundering a weak or superseded Stage A/B/C lineage into publish-ready or production status.\n\nTerminology lock:\n\n- Do not use or enforce a format-based hard-exclude rule.\n- Product, demo, PoC, component, interview, commentary, roundup, speech, or personnel formats are not automatically rejected by format alone.\n- They are subject to a strict-pass presumption block: without a concrete fresh execution anchor, they must not have entered `strict_passed_spec[]`; if they did, the downstream step must hold, reject, or return the item to the appropriate prior stage rather than polishing it forward.\n- Concrete execution anchors include signed contract, binding customer order, offtake, commercial deployment, field installation, commissioning, production start, facility opening, certification, regulatory decision, public funding approval, binding procurement, measurable capacity addition, safety recall/regulatory action, or named customer adoption.\n""",
    """## Anchor-path and selector-lineage safety overlay — V3\n\nThis overlay is downstream of the Stage A V3 selector rule. It prevents merge preparation from laundering a weak or superseded lineage while preserving valid execution and V3 non-execution routes.\n\nTerminology lock:\n\n- Do not use or enforce a format-based hard-exclude rule.\n- Product, demo, PoC, component, interview, commentary, roundup, speech, or personnel formats are not automatically rejected by format alone.\n- A format-risk card may enter merge preparation only when exactly one source-backed route passed Final QC: a concrete execution anchor or a complete V3 non-execution Structural Value Override.\n- The selected route, route-specific statuses, non-applicable-route reason, narrowed visible wording, and source coverage must remain unchanged through merge preparation.\n- A valid V3 non-execution route is not defective merely because no conventional execution event exists.\n""",
    "Prompt 0.8 legacy terminology lock",
)

replace_once(
    "docs/llm_prompts/v1/legacy/10_PROMPT_0_8_GitHub_Merge_Prep_LEGACY_BODY.md",
    """- `selector_lineage_final_gate.upstream_lineage_passed: true`\n- `selector_lineage_final_gate.artifact_consistency_passed: true`\n- `selector_lineage_final_gate.superseded_lineage_detected: false`\n- `final_qc_accounting_matches_input_count: true`\n- `publish_ready[]` only from current-run validated lineage\n""",
    """- `selector_lineage_final_gate.upstream_lineage_passed: true`\n- `selector_lineage_final_gate.artifact_consistency_passed: true`\n- `selector_lineage_final_gate.superseded_lineage_detected: false`\n- `final_qc_accounting_matches_input_count: true`\n- `publish_ready[]` only from current-run validated lineage\n- every format-risk item has `anchor_path_qc_passed: true`\n- every format-risk item has `selected_anchor_path: execution|v3_non_execution`\n- exactly one route status is `pass`; the other is `not_applicable` with a specific reason\n- execution-route evidence or the complete V3 non-execution evidence package is preserved without route switching\n""",
    "Prompt 0.8 legacy upstream gate",
)

replace_once(
    "docs/llm_prompts/v1/legacy/10_PROMPT_0_8_GitHub_Merge_Prep_LEGACY_BODY.md",
    """\"lineage_merge_gate\": {\n  \"final_qc_lineage_passed\": true,\n  \"publish_ready_lineage_checked_count\": 0,\n  \"publish_ready_lineage_hold_count\": 0,\n  \"github_ready_allowed\": true\n}\n""",
    """\"lineage_merge_gate\": {\n  \"final_qc_lineage_passed\": true,\n  \"anchor_path_lineage_passed\": true,\n  \"publish_ready_lineage_checked_count\": 0,\n  \"execution_path_checked_count\": 0,\n  \"v3_non_execution_path_checked_count\": 0,\n  \"publish_ready_lineage_hold_count\": 0,\n  \"github_ready_allowed\": true\n}\n""",
    "Prompt 0.8 legacy output schema",
)

# Stage C: accepted items must be passing, while revise-required items may honestly carry
# an unresolved or failed path that the revision must resolve.
replace_once(
    "docs/llm_prompts/v1/03_PROMPT_0_3_Stage_C_r0.md",
    """For every accepted_fact_safe or revise_required format-risk item, preserve the Stage A/B override metadata and emit:\n\n```json\n\"anchor_path_validation\": {\n  \"selected_anchor_path\": \"execution|v3_non_execution\",\n  \"anchor_path_qc_passed\": true,\n  \"execution_anchor_qc_status\": \"pass|not_applicable\",\n  \"structural_value_override_qc_status\": \"pass|not_applicable\",\n  \"non_applicable_anchor_path_reason\": \"...\"\n}\n```\n\nExactly one route status must be `pass`; the other must be `not_applicable` with a specific reason.\n""",
    """For every accepted_fact_safe format-risk item, preserve the Stage A/B override metadata and emit a passing object:\n\n```json\n\"anchor_path_validation\": {\n  \"selected_anchor_path\": \"execution|v3_non_execution\",\n  \"anchor_path_qc_passed\": true,\n  \"execution_anchor_qc_status\": \"pass|not_applicable\",\n  \"structural_value_override_qc_status\": \"pass|not_applicable\",\n  \"non_applicable_anchor_path_reason\": \"...\"\n}\n```\n\nExactly one accepted-item route status must be `pass`; the other must be `not_applicable` with a specific reason.\n\nA revise_required format-risk item may use the same passing object when the route is settled and only visible wording needs revision. When the route itself is unresolved, contradicted, or dual-claimed, emit an honest unresolved object instead of certifying PASS:\n\n```json\n\"anchor_path_validation\": {\n  \"selected_anchor_path\": \"unresolved\",\n  \"anchor_path_qc_passed\": false,\n  \"execution_anchor_qc_status\": \"unresolved|failed|not_applicable\",\n  \"structural_value_override_qc_status\": \"unresolved|failed|not_applicable\",\n  \"non_applicable_anchor_path_reason\": null,\n  \"anchor_path_issue\": \"...\",\n  \"required_resolution\": \"select and source-validate exactly one route\"\n}\n```\n\nAn unresolved revise_required item must not enter `accepted_fact_safe[]`, Baseline Revalidation, or Evidence QC until a Stage C revise pass resolves exactly one route and emits the passing schema.\n""",
    "Stage C accepted versus revise anchor schema",
)

replace_once(
    "docs/llm_prompts/v1/03_PROMPT_0_3_Stage_C_r0.md",
    """- needs_source_augmentation: true/false\n- recommended_next_action\n\nAllowed issue_type values:\n""",
    """- needs_source_augmentation: true/false\n- recommended_next_action\n- anchor_path_validation, required for format-risk revise items\n  - either the accepted-style passing schema when only wording needs revision\n  - or the unresolved schema with `anchor_path_qc_passed: false`, `anchor_path_issue`, and `required_resolution`\n\nAllowed issue_type values:\n""",
    "Stage C revise item schema",
)

# Validator: malformed list/object values must produce a finding, not raise TypeError.
replace_once(
    "validation_scripts/related_lifecycle_check.py",
    """        anchor_class = lineage.get(\"fresh_follow_up_anchor_class\")\n        if anchor_class not in FRESH_FOLLOW_UP_ANCHOR_CLASSES:\n            errors.append(\"distinct_follow_up requires valid fresh_follow_up_anchor_class\")\n""",
    """        anchor_class = lineage.get(\"fresh_follow_up_anchor_class\")\n        if not isinstance(anchor_class, str) or anchor_class not in FRESH_FOLLOW_UP_ANCHOR_CLASSES:\n            errors.append(\"distinct_follow_up requires valid fresh_follow_up_anchor_class\")\n""",
    "Related anchor class type check",
)

# Regression tests for all three findings.
test_path = "validation_scripts/tests/test_workflow_contracts.py"
p = Path(test_path)
text = p.read_text(encoding="utf-8")
marker = '\n\nif __name__ == "__main__":\n    unittest.main()\n'
if text.count(marker) != 1:
    raise SystemExit("test insertion marker not unique")
new_tests = r'''

class StructuralV3MergePrepAndRevisionContractTest(unittest.TestCase):
    @staticmethod
    def read_prompt(path: str) -> str:
        return (ROOT.parent / path).read_text(encoding="utf-8")

    def test_merge_prep_accepts_both_v3_routes(self):
        canonical = self.read_prompt("docs/llm_prompts/v1/10_PROMPT_0_8_GitHub_Merge_Prep.md")
        legacy = self.read_prompt("docs/llm_prompts/v1/legacy/10_PROMPT_0_8_GitHub_Merge_Prep_LEGACY_BODY.md")
        self.assertIn("V3 anchor-path merge-prep gate", canonical)
        self.assertIn("selected_anchor_path: execution", canonical)
        self.assertIn("selected_anchor_path: v3_non_execution", canonical)
        self.assertIn("anchor_path_lineage_passed", canonical)
        self.assertIn("Anchor-path and selector-lineage safety overlay — V3", legacy)
        self.assertIn("exactly one source-backed route passed Final QC", legacy)
        self.assertNotIn("without a concrete fresh execution anchor, they must not have entered", legacy)

    def test_stage_c_allows_unresolved_route_only_for_revise_required(self):
        text = self.read_prompt("docs/llm_prompts/v1/03_PROMPT_0_3_Stage_C_r0.md")
        self.assertIn("For every accepted_fact_safe format-risk item", text)
        self.assertIn("A revise_required format-risk item may use", text)
        self.assertIn('"selected_anchor_path": "unresolved"', text)
        self.assertIn('"anchor_path_qc_passed": false', text)
        self.assertIn("must not enter `accepted_fact_safe[]`", text)
        self.assertNotIn("For every accepted_fact_safe or revise_required format-risk item", text)


class RelatedMalformedAnchorClassTest(unittest.TestCase):
    def test_unhashable_anchor_class_returns_validation_error(self):
        parent = {"id": "PARENT", "date": "2026-01-01", "related": []}
        child = {
            "id": "CHILD",
            "date": "2026-02-01",
            "state": "publish_ready",
            "publish_ready": True,
            "related": ["PARENT"],
            "related_lineage": {
                "status": "PASS",
                "same_event_checked": True,
                "earliest_same_event_date_checked": True,
                "relation_type": "distinct_follow_up",
                "related_ids": ["PARENT"],
                "reason": "new development",
                "fresh_follow_up_anchor": "new evidence",
                "fresh_follow_up_anchor_class": ["execution_event_anchor"],
                "incremental_fact_vs_predecessor": "New evidence is available.",
                "changed_judgment_vs_predecessor": "The assessment changed.",
            },
        }
        errors, _ = check_card(child, {"PARENT": parent, "CHILD": child}, True)
        self.assertTrue(any("fresh_follow_up_anchor_class" in error for error in errors))
'''
p.write_text(text.replace(marker, new_tests + marker, 1), encoding="utf-8")

# Append review closure to the validation record.
validation = Path("docs/validation/STRUCTURAL_NEWS_VALUE_V3_VALIDATION_20260802.md")
validation.write_text(
    validation.read_text(encoding="utf-8")
    + """\n## Review 4838143604 closure\n\n- Prompt 0.8 canonical and subordinate legacy merge-prep overlays now preserve exactly one source-backed execution or V3 non-execution route.\n- Stage C certifies a passing route only for `accepted_fact_safe`; format-risk `revise_required` items may honestly carry an unresolved/failed route object until a revise pass resolves it.\n- `fresh_follow_up_anchor_class` is type-checked before membership validation, so malformed arrays or objects return findings instead of aborting the validator.\n- Regression tests cover merge-prep route compatibility, revise-required unresolved status, and malformed anchor-class types.\n""",
    encoding="utf-8",
)
