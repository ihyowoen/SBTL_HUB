#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def write(path: str, text: str) -> None:
    (ROOT / path).write_text(text, encoding="utf-8")


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise RuntimeError(f"{label}: expected exactly one match, found {count}")
    return text.replace(old, new, 1)


def replace_all(text: str, old: str, new: str, label: str, minimum: int = 1) -> str:
    count = text.count(old)
    if count < minimum:
        raise RuntimeError(f"{label}: expected at least {minimum} matches, found {count}")
    return text.replace(old, new)


def replace_between(text: str, start: str, end: str, replacement: str, label: str) -> str:
    start_count = text.count(start)
    end_count = text.count(end)
    if start_count != 1 or end_count < 1:
        raise RuntimeError(f"{label}: start={start_count}, end={end_count}")
    left, rest = text.split(start, 1)
    _, right = rest.split(end, 1)
    return left + replacement + end + right


old_docs = """1. docs/FACT_DISCIPLINE.md
2. docs/PROMPT_ABC_DEFAULT_MODE.md
3. docs/PROMPT_ABC_SUPPORTING_RULES.md
4. docs/FUTURE_CARD_STANDARD_FULL_SCHEMA.md
5. docs/CARD_ID_STANDARD.md
6. docs/WORKFLOW.md
7. docs/OPERATIONS.md
8. docs/POST_ACCEPTANCE_CONTENT_ENRICHMENT_QC.md"""
new_docs = """1. docs/FACT_DISCIPLINE.md
2. docs/STRUCTURAL_NEWS_VALUE_SELECTION.md
3. docs/llm_prompts/v1/01A_PROMPT_0_1S_Structural_Value_Override.md
4. docs/PROMPT_ABC_DEFAULT_MODE.md
5. docs/PROMPT_ABC_SUPPORTING_RULES.md
6. docs/FUTURE_CARD_STANDARD_FULL_SCHEMA.md
7. docs/CARD_ID_STANDARD.md
8. docs/WORKFLOW.md
9. docs/OPERATIONS.md
10. docs/POST_ACCEPTANCE_CONTENT_ENRICHMENT_QC.md"""

old_hierarchy = """1. docs/FACT_DISCIPLINE.md
2. docs/PROMPT_ABC_DEFAULT_MODE.md
3. docs/PROMPT_ABC_SUPPORTING_RULES.md
4. docs/FUTURE_CARD_STANDARD_FULL_SCHEMA.md
5. docs/CARD_ID_STANDARD.md
6. docs/WORKFLOW.md
7. docs/OPERATIONS.md
8. docs/POST_ACCEPTANCE_CONTENT_ENRICHMENT_QC.md"""
new_hierarchy = """1. docs/FACT_DISCIPLINE.md
2. docs/STRUCTURAL_NEWS_VALUE_SELECTION.md
3. docs/llm_prompts/v1/01A_PROMPT_0_1S_Structural_Value_Override.md
4. docs/PROMPT_ABC_DEFAULT_MODE.md
5. docs/PROMPT_ABC_SUPPORTING_RULES.md
6. docs/FUTURE_CARD_STANDARD_FULL_SCHEMA.md
7. docs/CARD_ID_STANDARD.md
8. docs/WORKFLOW.md
9. docs/OPERATIONS.md
10. docs/POST_ACCEPTANCE_CONTENT_ENRICHMENT_QC.md"""

stage_c_path = "docs/llm_prompts/v1/03_PROMPT_0_3_Stage_C_r0.md"
stage_c = read(stage_c_path)
stage_c = replace_once(stage_c, old_docs, new_docs, "Stage C required docs")
stage_c = replace_all(stage_c, "All 8 documents above are mandatory.", "All 10 documents above are mandatory.", "Stage C doc count")
stage_c = replace_all(stage_c, "list all 8 required docs", "list all 10 required docs", "Stage C report doc count", minimum=0) if "list all 8 required docs" in stage_c else stage_c
stage_c = replace_once(stage_c, old_hierarchy, new_hierarchy, "Stage C governance hierarchy")
stage_c = replace_once(
    stage_c,
    "- product/demo/PoC/pilot/prototype/component/interview/commentary/roundup/speech/personnel/partnership item lacks a concrete execution anchor",
    "- product/demo/PoC/pilot/prototype/component/interview/commentary/roundup/speech/personnel/partnership item has neither a source-backed concrete execution anchor nor a complete source-backed V3 non-execution Structural Value Override package",
    "Stage C reject blocker",
)
stage_c = replace_once(
    stage_c,
    "- product/demo/PoC/pilot/prototype/component/interview/commentary/roundup/speech/personnel/partnership wrapper is framed as independent strategic proof without a concrete execution anchor",
    "- product/demo/PoC/pilot/prototype/component/interview/commentary/roundup/speech/personnel/partnership wrapper is framed as independent strategic proof without either a source-backed concrete execution anchor or a complete source-backed V3 non-execution Structural Value Override package",
    "Stage C source-direction blocker",
)
old_stage_c_pass = """Pass 2A — Execution-anchor check for format-risk cards

If a draft card originates from product news, demo, PoC, pilot, prototype, component launch, interview, commentary, event roundup, speech, personnel coverage, or partnership/integration coverage, Stage C must confirm that the visible fields are built around a concrete execution anchor.

Valid anchors include signed contract, binding customer order, offtake, price floor/risk-sharing facility, commercial deployment, field installation, commissioning, production start, facility opening, certification/regulatory approval, regulatory decision/enforcement, public funding approval, binding procurement, measurable capacity addition, safety recall/regulatory safety action, named customer adoption, named deployment site with measurable pilot scale/duration/objective, factory/project groundbreaking, or final investment decision.

Decision rule:

- If the anchor exists but wording overclaims its maturity, use revise_required to narrow the card.
- If no concrete execution anchor exists and the draft depends on strategic speculation, reject or classify as support_source_only.
- Do not reject solely because the source format is product/demo/PoC/interview/roundup; reject only because the execution anchor is absent, unsupported, stale, or non-cardable.
"""
new_stage_c_pass = """Pass 2A — Anchor-path check for format-risk cards

If a draft card originates from product news, demo, PoC, pilot, prototype, component launch, interview, commentary, event roundup, speech, personnel coverage, or partnership/integration coverage, Stage C must confirm that the visible fields are built around exactly one source-backed path:

1. a concrete execution anchor; or
2. a complete V3 non-execution Structural Value Override.

Valid execution anchors include signed contract, binding customer order, offtake, price floor/risk-sharing facility, commercial deployment, field installation, commissioning, production start, facility opening, certification/regulatory approval, regulatory decision/enforcement, public funding approval, binding procurement, measurable capacity addition, safety recall/regulatory safety action, named customer adoption, named deployment site with measurable pilot scale/duration/objective, factory/project groundbreaking, or final investment decision.

A valid V3 non-execution path requires all of the following to remain source-supported and carried forward from Stage A/B:

- `structural_value_override_applied: true`
- one valid non-execution `anchor_class`
- concrete item-specific `evidence_needed_for_stage_b[]` targets verified by Stage B
- specific `why_execution_event_not_required`
- explicit before-after chain
- source-supported changed judgment
- no stage, scale, causality, market-effect, or commercialisation inflation

Decision rule:

- If the selected path exists but wording overclaims its maturity or class, use revise_required to narrow the card.
- If neither source-backed path exists, reject or classify as support_source_only.
- If both paths are claimed without a clear primary path, use revise_required and require one selected path plus a reason the other is not applicable.
- Do not reject solely because of source format; reject only because both paths are absent, unsupported, stale, contradictory, or non-cardable.

For every accepted_fact_safe or revise_required format-risk item, preserve the Stage A/B override metadata and emit:

```json
"anchor_path_validation": {
  "selected_anchor_path": "execution|v3_non_execution",
  "anchor_path_qc_passed": true,
  "execution_anchor_qc_status": "pass|not_applicable",
  "structural_value_override_qc_status": "pass|not_applicable",
  "non_applicable_anchor_path_reason": "..."
}
```

Exactly one route status must be `pass`; the other must be `not_applicable` with a specific reason.
"""
stage_c = replace_once(stage_c, old_stage_c_pass, new_stage_c_pass, "Stage C Pass 2A")
write(stage_c_path, stage_c)


evidence_path = "docs/llm_prompts/v1/07_PROMPT_0_5_Evidence_QC.md"
evidence = read(evidence_path)
evidence = replace_once(evidence, old_docs, new_docs, "Evidence required docs")
evidence = replace_all(evidence, "All 8 documents above are mandatory.", "All 10 documents above are mandatory.", "Evidence doc count")
evidence = replace_all(evidence, "list all 8 required docs", "list all 10 required docs", "Evidence report doc count", minimum=0) if "list all 8 required docs" in evidence else evidence
evidence = replace_once(evidence, old_hierarchy, new_hierarchy, "Evidence governance hierarchy")
evidence_start = "## Execution-anchor and selector-lineage safety overlay — 2026-05-05\n"
evidence_end = "## Operational integrated rule — NO_UNVERIFIED_HOLD_OR_DELETE_RULE_20260507_V2"
new_evidence_overlay = """## Anchor-path and selector-lineage safety overlay — V3

This overlay prevents post-acceptance steps from laundering a weak or superseded Stage A/B/C lineage into evidence-complete status.

Terminology lock:

- Do not use a format-based hard-exclude rule.
- Product, demo, PoC, component, interview, commentary, roundup, speech, or personnel formats are not automatically rejected.
- A format-risk item must carry exactly one source-backed path: a concrete execution anchor or a complete V3 non-execution Structural Value Override.
- If neither path is valid, hold, reject, or return the item to the earliest defective stage.

### Required upstream lineage gate for Evidence QC

Before Evidence QC begins, verify that `BASELINE_REVALIDATION_JSON` carries a valid current-run lineage declaration directly or through `upstream_lineage` / `stage_a_lineage`:

- `stage_a_validity_status: PASS`
- `artifact_consistency_gate.status: PASS`
- `structural_selector_policy_version: STRUCTURAL_NEWS_VALUE_SELECTION_V3`
- every addable candidate originated from current-run Stage C `accepted_fact_safe[]`
- every format-risk item carries Stage C `anchor_path_validation`
- no candidate came from a review, blocked, rejected, support-only, revise-required, or superseded lineage without an explicit authorized reopen

If any field is missing, contradictory, or stale, stop with `BLOCKED_UPSTREAM_LINEAGE_INVALID` and perform no evidence QC.

### Anchor-path evidence check

For every format-risk `addable_merge_safe[]` item, Evidence QC must verify exactly one route:

Execution route:

- body-level or official evidence supports the concrete execution anchor;
- visible fields do not overstate execution stage, scale, timing, causality, or commercial maturity.

V3 non-execution route:

- `structural_value_override_applied: true`;
- the non-execution anchor class is valid;
- every item-specific `evidence_needed_for_stage_b[]` claim, metric, stage, date, and uncertainty is covered by body-level or official evidence;
- `why_execution_event_not_required`, before-after chain, and changed judgment are specific and source-supported;
- the card does not launder strategic intent, preliminary data, policy discussion, technical possibility, or follow-up probability into execution.

Exactly one route may pass. The other must be `not_applicable` with a specific reason. If neither route passes, use `addable_hold_claim_gap`, `addable_hold_source_gap`, `needs_source_augmentation`, or `evidence_qc_rejected`. Do not repair an anchor-path defect by prose rewriting alone.

### Output requirement

Add to Evidence QC JSON:

```json
"upstream_lineage_validation": {
  "stage_a_validity_status": "PASS|FAIL|MISSING",
  "artifact_consistency_status": "PASS|FAIL|MISSING",
  "structural_selector_policy_version": "STRUCTURAL_NEWS_VALUE_SELECTION_V3",
  "superseded_lineage_detected": false,
  "decision": "pass|blocked"
},
"anchor_path_qc_summary": {
  "format_risk_input_count": 0,
  "anchor_path_pass_count": 0,
  "execution_path_pass_count": 0,
  "v3_non_execution_path_pass_count": 0,
  "anchor_path_hold_count": 0,
  "anchor_path_rejected_count": 0,
  "item_results": [
    {
      "source_spec_id": "...",
      "selected_anchor_path": "execution|v3_non_execution",
      "anchor_path_qc_passed": true,
      "execution_anchor_qc_status": "pass|not_applicable",
      "structural_value_override_qc_status": "pass|not_applicable",
      "non_applicable_anchor_path_reason": "..."
    }
  ]
}
```

Final override: if `upstream_lineage_validation.decision != "pass"` or any promoted format-risk item lacks a passing item result, the next recommended call must be upstream repair, not Prompt 0.6.

"""
evidence = replace_between(evidence, evidence_start, evidence_end, new_evidence_overlay, "Evidence overlay")
write(evidence_path, evidence)


content_path = "docs/llm_prompts/v1/08_PROMPT_0_6_Content_Polish.md"
content = read(content_path)
content = replace_once(content, old_docs, new_docs, "Content required docs")
content = replace_all(content, "All 8 documents above are mandatory.", "All 10 documents above are mandatory.", "Content doc count")
content = replace_all(content, "list all 8 required docs", "list all 10 required docs", "Content report doc count", minimum=0) if "list all 8 required docs" in content else content
content = replace_once(content, old_hierarchy, new_hierarchy, "Content governance hierarchy")
content_start = "## Execution-anchor and selector-lineage safety overlay — 2026-05-05\n"
content_end = "## Operational integrated rule — NO_UNVERIFIED_HOLD_OR_DELETE_RULE_20260507_V2"
new_content_overlay = """## Anchor-path and selector-lineage safety overlay — V3

This overlay prevents Content Polish from laundering an unsupported execution or non-execution path into Final QC.

Terminology lock:

- Do not use a format-based hard-exclude rule.
- A format-risk item must have exactly one Evidence-QC-validated path: execution or V3 non-execution.
- Content Polish may narrow language but may not switch the selected path, invent missing evidence, or upgrade stage, scale, causality, market effect, commercialisation, policy status, financial certainty, strategic intent, technical maturity, or follow-up probability.

### Required upstream lineage gate for Content Polish

Before content enrichment begins, verify that `EVIDENCE_QC_RESULTS_JSON` includes:

- `upstream_lineage_validation.decision: pass`
- `anchor_path_qc_summary`
- a passing item result for every format-risk input
- exactly one route status `pass` and the other `not_applicable` with a specific reason for each item
- `evidence_qc_accounting_matches_input_count: true`

If these are missing or failed, stop with `BLOCKED_EVIDENCE_QC_LINEAGE_OR_ANCHOR_INVALID` and perform no content enrichment or language polish.

### Content polish boundary for format-risk cards

Do not turn demo into deployment, PoC into rollout, partnership/MOU into implementation, interview/commentary into an execution event, product launch into adoption, policy discussion into enactment, preliminary data into settled performance, strategy into binding action, technical possibility into commercialisation, or probability into certainty.

All polished visible fields must remain within the selected Evidence-QC-validated route. If an anchor-path gap is found, route the item to `needs_return_to_evidence_qc` or `content_hold_claim_narrowing_needed`; do not polish it forward.

### Output requirement

At root level emit:

```json
"lineage_and_anchor_guard": {
  "evidence_qc_lineage_passed": true,
  "anchor_path_qc_passed": true,
  "execution_path_item_count": 0,
  "v3_non_execution_path_item_count": 0,
  "route_status_accounting_complete": true,
  "format_risk_claims_narrowed_count": 0,
  "returned_to_evidence_qc_count": 0
}
```

Every `content_enriched_and_language_polished[]` item must emit its selected path and coherent route statuses. Final override: if lineage, route accounting, or anchor-path guard fails, the next recommended call must not be Prompt 0.7.

"""
content = replace_between(content, content_start, content_end, new_content_overlay, "Content overlay")
old_root_guard = """"lineage_and_anchor_guard": {
  "status": "PASS",
  "evidence_qc_lineage_passed": true,
  "execution_anchor_qc_passed": true,
  "source_strength_caveat_preserved": true,
  "publish_ready_remains_false": true,
  "content_polish_modified_visible_fields_only": true,
  "fact_sources_unchanged_unless_authorized_supplemental": true,
  "source_quote_unchanged_unless_authorized_supplemental": true,
  "no_silent_downstream_enrichment": true,
  "supplemental_pass_accounting_preserved": true
}"""
new_root_guard = """"lineage_and_anchor_guard": {
  "status": "PASS",
  "evidence_qc_lineage_passed": true,
  "anchor_path_qc_passed": true,
  "execution_path_item_count": 0,
  "v3_non_execution_path_item_count": 0,
  "route_status_accounting_complete": true,
  "source_strength_caveat_preserved": true,
  "publish_ready_remains_false": true,
  "content_polish_modified_visible_fields_only": true,
  "fact_sources_unchanged_unless_authorized_supplemental": true,
  "source_quote_unchanged_unless_authorized_supplemental": true,
  "no_silent_downstream_enrichment": true,
  "supplemental_pass_accounting_preserved": true
}"""
content = replace_once(content, old_root_guard, new_root_guard, "Content root guard")
old_item_guard = """"lineage_and_anchor_guard": {
  "status": "PASS",
  "source_spec_id": "...",
  "evidence_qc_lineage_passed": true,
  "execution_anchor_qc_passed": true,
  "source_strength_caveat_preserved": true,
  "publish_ready_remains_false": true,
  "visible_field_change_log_ref": "...",
  "fact_sources_change_status": "unchanged|authorized_supplemental_metadata_only|authorized_supplemental_source_added",
  "source_quote_change_status": "unchanged|authorized_supplemental_quote_added",
  "reason_if_any_source_field_changed": "...|not_applicable"
}"""
new_item_guard = """"lineage_and_anchor_guard": {
  "status": "PASS",
  "source_spec_id": "...",
  "evidence_qc_lineage_passed": true,
  "anchor_path_qc_passed": true,
  "selected_anchor_path": "execution|v3_non_execution",
  "execution_anchor_qc_status": "pass|not_applicable",
  "structural_value_override_qc_status": "pass|not_applicable",
  "non_applicable_anchor_path_reason": "...",
  "source_strength_caveat_preserved": true,
  "publish_ready_remains_false": true,
  "visible_field_change_log_ref": "...",
  "fact_sources_change_status": "unchanged|authorized_supplemental_metadata_only|authorized_supplemental_source_added",
  "source_quote_change_status": "unchanged|authorized_supplemental_quote_added",
  "reason_if_any_source_field_changed": "...|not_applicable"
}"""
content = replace_once(content, old_item_guard, new_item_guard, "Content item guard")
write(content_path, content)


final_path = "docs/llm_prompts/v1/09_PROMPT_0_7_Final_QC.md"
final = read(final_path)
final = replace_once(
    final,
    "- exactly one applicable route result: `execution_anchor_qc_passed: true` or `structural_value_override_qc_passed: true`; the non-applicable route must be explicitly marked not_applicable with a reason",
    "- every format-risk item guard has `selected_anchor_path: execution|v3_non_execution`\n- exactly one item route status is `pass`: `execution_anchor_qc_status` or `structural_value_override_qc_status`; the other is `not_applicable`\n- every non-applicable route has a specific `non_applicable_anchor_path_reason`",
    "Final QC producer-consumer schema",
)
write(final_path, final)


test_path = "validation_scripts/tests/test_workflow_contracts.py"
tests = read(test_path)
new_tests = '''

class StructuralV3InterveningStageContractTest(unittest.TestCase):
    @staticmethod
    def read_prompt(path: str) -> str:
        return (ROOT.parent / path).read_text(encoding="utf-8")

    def test_stage_c_uses_two_path_anchor_gate(self):
        text = self.read_prompt("docs/llm_prompts/v1/03_PROMPT_0_3_Stage_C_r0.md")
        self.assertIn("All 10 documents above are mandatory.", text)
        self.assertIn("Pass 2A — Anchor-path check for format-risk cards", text)
        self.assertIn("exactly one source-backed path", text)
        self.assertIn("structural_value_override_qc_status", text)
        self.assertNotIn("item lacks a concrete execution anchor", text)
        self.assertNotIn("without a concrete execution anchor", text)

    def test_evidence_qc_emits_route_specific_anchor_results(self):
        text = self.read_prompt("docs/llm_prompts/v1/07_PROMPT_0_5_Evidence_QC.md")
        self.assertIn("All 10 documents above are mandatory.", text)
        self.assertIn("anchor_path_qc_summary", text)
        self.assertIn("execution_anchor_qc_status", text)
        self.assertIn("structural_value_override_qc_status", text)
        self.assertNotIn("without a concrete fresh execution anchor", text)
        self.assertNotIn("Execution-anchor evidence check", text)

    def test_content_polish_produces_final_qc_guard_schema(self):
        text = self.read_prompt("docs/llm_prompts/v1/08_PROMPT_0_6_Content_Polish.md")
        self.assertIn("All 10 documents above are mandatory.", text)
        self.assertIn("anchor_path_qc_passed", text)
        self.assertIn("selected_anchor_path", text)
        self.assertIn("execution_anchor_qc_status", text)
        self.assertIn("structural_value_override_qc_status", text)
        self.assertIn("non_applicable_anchor_path_reason", text)
        self.assertNotIn('"execution_anchor_qc_passed": true', text)
        self.assertNotIn("without a concrete fresh execution anchor", text)

    def test_final_qc_consumes_route_status_schema(self):
        text = self.read_prompt("docs/llm_prompts/v1/09_PROMPT_0_7_Final_QC.md")
        self.assertIn("execution_anchor_qc_status", text)
        self.assertIn("structural_value_override_qc_status", text)
        self.assertIn("non_applicable_anchor_path_reason", text)
        self.assertNotIn("execution_anchor_qc_passed: true` or `structural_value_override_qc_passed: true", text)
'''
marker = '\n\nif __name__ == "__main__":\n    unittest.main()\n'
tests = replace_once(tests, marker, new_tests + marker, "workflow regression insertion")
write(test_path, tests)

# The one-shot helper and workflow must not remain in the final PR diff.
for relative in [
    "scripts/patch_structural_v3_review_4838008669.py",
    ".github/workflows/patch-structural-v3-review-4838008669.yml",
]:
    path = ROOT / relative
    if path.exists():
        path.unlink()

print("patched Structural V3 intervening stages and producer-consumer guard schema")
