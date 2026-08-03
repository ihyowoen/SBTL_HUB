from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def replace_once(path: Path, old: str, new: str, label: str) -> None:
    text = path.read_text(encoding="utf-8")
    count = text.count(old)
    if count != 1:
        raise RuntimeError(f"{label}: expected exactly one target, found {count}")
    path.write_text(text.replace(old, new, 1), encoding="utf-8")


final_qc = ROOT / "docs/llm_prompts/v1/09_PROMPT_0_7_Final_QC.md"
old_final_package = """For every format-risk `publish_ready[]` item with `selected_anchor_path = v3_non_execution`, preserve the complete same-run, source-backed Structural Value Override package byte-for-byte alongside the route fields:

- `structural_value_override_applied: true`
- non-empty valid `anchor_classes[]`
- non-empty item-specific `evidence_needed_for_stage_b[]`
- specific `why_execution_event_not_required`
- `prior_state`
- `new_verified_fact`
- `changed_judgment`
- applicable uncertainty / probability-change fields
- applicable baseline-expectation / before-after fields
- current-run source lineage that supports each package field

These fields must remain available to Prompt 0.8 and must not be summarized away, reconstructed from memory, or dropped by Final QC. If any required V3 package field is missing, altered, generic, unsupported, or inconsistent with the selected route, route the item to `final_qc_hold` or `needs_return_to_evidence_qc`; do not emit it in `publish_ready[]`.
"""
new_final_package = """For every format-risk `publish_ready[]` item with `selected_anchor_path = v3_non_execution`, preserve the complete same-run, source-backed canonical Structural Value Override package byte-for-byte alongside the route fields:

- `structural_value_override_applied: true`
- `structural_value_override_reason`
- non-empty valid `anchor_classes[]`
- `incremental_information`
- `decision_relevance`
- `baseline_expectation_changed`
- non-empty item-specific `evidence_needed_for_stage_b[]`
- non-empty measurable `next_confirmation_points[]`
- specific `why_execution_event_not_required`
- `prior_state`
- `new_verified_fact`
- `changed_judgment`
- applicable uncertainty / probability-change fields
- applicable baseline-expectation / before-after fields
- current-run source lineage that supports every package field

This list is the same canonical package emitted by Prompt 0.5 and Prompt 0.6; Final QC must not narrow it to a summary subset. These fields must remain available to Prompt 0.8 and must not be summarized away, reconstructed from memory, renamed, or dropped by Final QC. If any required V3 package field is missing, altered, generic, unsupported, or inconsistent with the selected route, route the item to `final_qc_hold` or `needs_return_to_evidence_qc`; do not emit it in `publish_ready[]`.
"""
replace_once(final_qc, old_final_package, new_final_package, "Final QC canonical V3 package")

merge_prep = ROOT / "docs/llm_prompts/v1/10_PROMPT_0_8_GitHub_Merge_Prep.md"
old_preconditions_tail = """- all registered validators and open-remediation checks required by Stage 0.0D.

## 3. Ordinary-run operations
"""
new_preconditions_tail = """- all registered validators and open-remediation checks required by Stage 0.0D.

### 2A. Stage 0.7C governance-preflight consumer gate

Before any card may enter `pr_candidate_payload`, Prompt 0.8 must validate the Stage 0.7C artifact itself rather than trusting its top-level PASS label.

The artifact must contain all of the following from the same repository revision used by Stage 0.7C:

- `status: PASS_WITH_DECLARED_RESIDUAL_RISK`;
- `prompt_0_8_authorized: true`;
- `governing_contracts_same_revision: true`;
- `v3_contract_preflight_passed: true`;
- `governing_contracts_read[]` containing exactly these required original documents:
  - `docs/EDITORIAL_VALUE_AND_COMPLETENESS_STANDARD.md`;
  - `docs/STRUCTURAL_NEWS_VALUE_SELECTION.md`;
  - `docs/llm_prompts/v1/01A_PROMPT_0_1S_Structural_Value_Override.md`;
  - `docs/RELATED_LIFECYCLE_CONTRACT.md`.

A summary, downstream excerpt, renamed substitute, missing path, duplicate path, mixed repository revision, false/absent preflight field, or internally inconsistent authorization is a hard consumer-side failure even when the Stage 0.7C artifact claims PASS. Stop before operation materialization and report:

```text
status: BLOCKED_STAGE_0_7C_GOVERNANCE_PREFLIGHT_INVALID
invalid_or_missing_stage_0_7c_fields: [...]
no pr_candidate_payload emitted
```

## 3. Ordinary-run operations
"""
replace_once(merge_prep, old_preconditions_tail, new_preconditions_tail, "Prompt 0.8 Stage 0.7C consumer gate")

old_merge_package = """The execution route must retain its source-backed execution evidence. The V3 non-execution route must retain its verified anchor class, item-specific evidence targets, before-after chain, changed judgment, and specific `why_execution_event_not_required`. Absence of a conventional execution event is not itself a defect when the V3 non-execution route passed.
"""
new_merge_package = """The execution route must retain its source-backed execution evidence.

For `selected_anchor_path: v3_non_execution`, Prompt 0.8 must verify and preserve the complete canonical package byte-for-byte from Final QC:

- `structural_value_override_applied: true`;
- `structural_value_override_reason`;
- non-empty valid `anchor_classes[]`;
- `incremental_information`;
- `decision_relevance`;
- `baseline_expectation_changed`;
- non-empty item-specific `evidence_needed_for_stage_b[]`;
- non-empty measurable `next_confirmation_points[]`;
- specific `why_execution_event_not_required`;
- `prior_state`;
- `new_verified_fact`;
- `changed_judgment`;
- applicable uncertainty / probability-change fields;
- applicable baseline-expectation / before-after fields;
- current-run source lineage supporting every package field.

Missing, renamed, summarized, reconstructed, generic, altered, unsupported, or internally inconsistent package data requires `BLOCKED_FINAL_QC_ANCHOR_PATH_INVALID`; it must not enter `pr_candidate_payload`. Absence of a conventional execution event is not itself a defect when the complete V3 non-execution route passed.
"""
replace_once(merge_prep, old_merge_package, new_merge_package, "Prompt 0.8 canonical V3 package")

validator = ROOT / "validation_scripts/stage_lineage_contract_check.py"
old_required = """    'strict_gate_check', 'format_risk_tags', 'execution_anchor_type',
    'execution_anchor_strength', 'baseline_relation', 'duplicate_risk',
"""
new_required = """    'strict_gate_check', 'format_risk_tags', 'baseline_relation', 'duplicate_risk',
"""
replace_once(validator, old_required, new_required, "Stage A base required fields")

old_constants = """STAGE_A_ALLOWED_EXECUTION_ANCHOR_STRENGTH = {'strong', 'moderate'}

STAGE_B_EXPECTED_TOP_LEVEL = {
"""
new_constants = """STAGE_A_ALLOWED_EXECUTION_ANCHOR_STRENGTH = {'strong', 'moderate'}
STAGE_A_NON_EXECUTION_ANCHOR_CLASSES = {
    'policy_regulatory_anchor',
    'data_financial_anchor',
    'strategic_behavior_anchor',
    'technology_commercialization_anchor',
    'follow_up_probability_anchor',
}
STAGE_A_V3_OVERRIDE_REQUIRED = [
    'structural_value_override_reason',
    'anchor_classes',
    'incremental_information',
    'decision_relevance',
    'baseline_expectation_changed',
    'evidence_needed_for_stage_b',
    'next_confirmation_points',
    'why_execution_event_not_required',
    'prior_state',
    'new_verified_fact',
    'changed_judgment',
]
STAGE_A_GENERIC_OVERRIDE_TEXT = {
    'official sources', 'company materials', 'media reports',
    'additional confirmation', 'more evidence', 'tbd', 'unknown',
}

STAGE_B_EXPECTED_TOP_LEVEL = {
"""
replace_once(validator, old_constants, new_constants, "Stage A V3 constants")

old_before_validator = """def validate_stage_a_spec(spec, index, messages):
"""
new_before_validator = """def _nonempty_string(value):
    return isinstance(value, str) and bool(value.strip())


def _specific_string(value):
    return _nonempty_string(value) and value.strip().lower() not in STAGE_A_GENERIC_OVERRIDE_TEXT


def validate_stage_a_v3_override(spec, spec_id, messages):
    if spec.get('structural_value_override_applied') is not True:
        return False

    valid = True
    for field in STAGE_A_V3_OVERRIDE_REQUIRED:
        if missing_nonempty(spec, field):
            messages.append(f'{spec_id}: incomplete V3 override package missing {field}')
            valid = False

    classes = spec.get('anchor_classes')
    if not isinstance(classes, list) or not classes:
        messages.append(f'{spec_id}: anchor_classes must be a non-empty array for v3_non_execution')
        valid = False
    else:
        invalid_classes = [value for value in classes if value not in STAGE_A_NON_EXECUTION_ANCHOR_CLASSES]
        if invalid_classes:
            messages.append(f'{spec_id}: invalid non-execution anchor_classes={invalid_classes}')
            valid = False

    evidence_targets = spec.get('evidence_needed_for_stage_b')
    if not isinstance(evidence_targets, list) or not evidence_targets:
        valid = False
    elif any(not _specific_string(value) for value in evidence_targets):
        messages.append(f'{spec_id}: evidence_needed_for_stage_b must contain item-specific targets')
        valid = False

    confirmation_points = spec.get('next_confirmation_points')
    if not isinstance(confirmation_points, list) or not confirmation_points:
        valid = False
    elif any(not _specific_string(value) for value in confirmation_points):
        messages.append(f'{spec_id}: next_confirmation_points must contain measurable item-specific points')
        valid = False

    if not _specific_string(spec.get('structural_value_override_reason')):
        messages.append(f'{spec_id}: structural_value_override_reason must be item-specific')
        valid = False
    if not _specific_string(spec.get('why_execution_event_not_required')):
        messages.append(f'{spec_id}: why_execution_event_not_required must be item-specific')
        valid = False

    return valid


def validate_stage_a_spec(spec, index, messages):
"""
replace_once(validator, old_before_validator, new_before_validator, "Stage A V3 helper insertion")

old_strength_check = """    if spec.get('execution_anchor_strength') not in STAGE_A_ALLOWED_EXECUTION_ANCHOR_STRENGTH:
        messages.append(f'{spec_id}: execution_anchor_strength must be strong or moderate for strict_passed_spec')
"""
new_strength_check = """    format_risk_tags = spec.get('format_risk_tags')
    has_format_risk = isinstance(format_risk_tags, list) and bool(format_risk_tags)
    execution_type = spec.get('execution_anchor_type')
    execution_strength = spec.get('execution_anchor_strength')
    execution_path_complete = _nonempty_string(execution_type) and execution_strength in STAGE_A_ALLOWED_EXECUTION_ANCHOR_STRENGTH

    if has_format_risk:
        override_path_complete = validate_stage_a_v3_override(spec, spec_id, messages)
        if execution_path_complete == override_path_complete:
            messages.append(
                f'{spec_id}: format-risk strict_passed_spec requires exactly one complete '
                'execution or v3_non_execution path'
            )
        if (execution_type or execution_strength) and not execution_path_complete:
            messages.append(f'{spec_id}: partial/invalid execution path metadata for format-risk strict_passed_spec')
    else:
        if not _nonempty_string(execution_type):
            messages.append(f'{spec_id}: missing execution_anchor_type')
        if execution_strength not in STAGE_A_ALLOWED_EXECUTION_ANCHOR_STRENGTH:
            messages.append(f'{spec_id}: execution_anchor_strength must be strong or moderate for strict_passed_spec')
"""
replace_once(validator, old_strength_check, new_strength_check, "Stage A two-path validation")

test_path = ROOT / "validation_scripts/tests/test_review_4840783305_contracts.py"
test_path.write_text('''from __future__ import annotations

import copy
import io
import unittest
from contextlib import redirect_stdout
from pathlib import Path

from validation_scripts import stage_lineage_contract_check as lineage

ROOT = Path(__file__).resolve().parents[2]
FINAL_QC = ROOT / "docs/llm_prompts/v1/09_PROMPT_0_7_Final_QC.md"
MERGE_PREP = ROOT / "docs/llm_prompts/v1/10_PROMPT_0_8_GitHub_Merge_Prep.md"

CANONICAL_V3_FIELDS = (
    "structural_value_override_reason",
    "anchor_classes[]",
    "incremental_information",
    "decision_relevance",
    "baseline_expectation_changed",
    "evidence_needed_for_stage_b[]",
    "next_confirmation_points[]",
    "why_execution_event_not_required",
    "prior_state",
    "new_verified_fact",
    "changed_judgment",
)


class TestReview4840783305Contracts(unittest.TestCase):
    def test_final_qc_and_merge_prep_preserve_full_canonical_package(self):
        final_text = FINAL_QC.read_text(encoding="utf-8")
        merge_text = MERGE_PREP.read_text(encoding="utf-8")
        final_start = final_text.index("For every format-risk `publish_ready[]` item with `selected_anchor_path = v3_non_execution`")
        final_end = final_text.index("- evidence_complete: true", final_start)
        final_block = final_text[final_start:final_end]
        merge_start = merge_text.index("For `selected_anchor_path: v3_non_execution`")
        merge_end = merge_text.index("If metadata is missing", merge_start)
        merge_block = merge_text[merge_start:merge_end]
        for field in CANONICAL_V3_FIELDS:
            self.assertIn(field, final_block)
            self.assertIn(field, merge_block)

    def test_merge_prep_consumes_stage_07c_governance_proof(self):
        text = MERGE_PREP.read_text(encoding="utf-8")
        section_start = text.index("### 2A. Stage 0.7C governance-preflight consumer gate")
        section_end = text.index("## 3. Ordinary-run operations", section_start)
        section = text[section_start:section_end]
        for field in (
            "governing_contracts_read[]",
            "governing_contracts_same_revision: true",
            "v3_contract_preflight_passed: true",
            "prompt_0_8_authorized: true",
            "BLOCKED_STAGE_0_7C_GOVERNANCE_PREFLIGHT_INVALID",
        ):
            self.assertIn(field, section)
        for path in (
            "docs/EDITORIAL_VALUE_AND_COMPLETENESS_STANDARD.md",
            "docs/STRUCTURAL_NEWS_VALUE_SELECTION.md",
            "docs/llm_prompts/v1/01A_PROMPT_0_1S_Structural_Value_Override.md",
            "docs/RELATED_LIFECYCLE_CONTRACT.md",
        ):
            self.assertIn(path, section)

    def valid_stage_a_spec(self):
        return {
            "spec_id": "SPEC_V3_001",
            "source_story_ids": ["STORY_1"],
            "strict_pass_gate": {"status": "pass", "reason": "all gates", "all_six_conditions_passed": True},
            "enhanced_selector_precision_version": "v3",
            "selector_policy_version": "STRUCTURAL_NEWS_VALUE_SELECTION_V3",
            "strict_gate_check": "pass",
            "format_risk_tags": ["interview"],
            "baseline_relation": "new",
            "duplicate_risk": "low",
            "staleness_decision": "current",
            "source_access_risk": "low",
            "stage_a_evidence_status": "not_evidence_complete_no_fetch",
            "stage_b_evidence_package_required": True,
            "primary_url_semantics": "provided_source_candidate_not_evidence",
            "same_event_source_cluster": "cluster-1",
            "support_source_candidates": [],
            "source_domain_candidates": [],
            "source_diversity_path": {"status": "planned"},
            "source_cluster_preserved": True,
            "structural_value_override_applied": True,
            "structural_value_override_reason": "The verified policy change alters market-access eligibility for this project.",
            "anchor_classes": ["policy_regulatory_anchor"],
            "incremental_information": "The eligibility rule changed from discretionary to mandatory screening.",
            "decision_relevance": "The change alters supplier qualification and timing decisions.",
            "baseline_expectation_changed": True,
            "evidence_needed_for_stage_b": ["Official rule text confirming the eligibility clause and effective date"],
            "next_confirmation_points": ["Publication of implementing guidance with the final effective date"],
            "why_execution_event_not_required": "The operative legal eligibility change is decision-useful before a commercial execution event.",
            "prior_state": "Eligibility was uncertain under draft guidance.",
            "new_verified_fact": "The final rule establishes the new eligibility condition.",
            "changed_judgment": "Market-access probability is now lower for non-compliant suppliers.",
        }

    def run_stage_a(self, spec):
        stream = io.StringIO()
        with redirect_stdout(stream):
            result = lineage.check_stage_a({"strict_passed_spec": [spec]})
        return result, stream.getvalue()

    def test_stage_a_validator_accepts_complete_non_execution_route(self):
        result, output = self.run_stage_a(self.valid_stage_a_spec())
        self.assertEqual(result, 0, output)
        self.assertIn("PASS_STAGE_A_SCHEMA_CONTRACT", output)

    def test_stage_a_validator_rejects_incomplete_or_dual_route(self):
        incomplete = self.valid_stage_a_spec()
        incomplete.pop("structural_value_override_reason")
        result, output = self.run_stage_a(incomplete)
        self.assertEqual(result, 1)
        self.assertIn("incomplete V3 override package", output)

        dual = copy.deepcopy(self.valid_stage_a_spec())
        dual["execution_anchor_type"] = "commercial_award"
        dual["execution_anchor_strength"] = "strong"
        result, output = self.run_stage_a(dual)
        self.assertEqual(result, 1)
        self.assertIn("requires exactly one complete execution or v3_non_execution path", output)


if __name__ == "__main__":
    unittest.main()
''', encoding="utf-8")
