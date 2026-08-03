from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def replace_once(path: Path, old: str, new: str, label: str) -> None:
    text = path.read_text(encoding="utf-8")
    count = text.count(old)
    if count != 1:
        raise RuntimeError(f"{label}: expected exactly one target, found {count}")
    path.write_text(text.replace(old, new, 1), encoding="utf-8")


stage_a = ROOT / "docs/llm_prompts/v1/01_PROMPT_0_1_Stage_A.md"
old_schema = """- structural_value_override_applied
- anchor_classes
- evidence_needed_for_stage_b
- why_execution_event_not_required
- strict_pass_gate
"""
new_schema = """- structural_value_override_applied
- structural_value_override_reason
- anchor_classes
- incremental_information
- decision_relevance
- baseline_expectation_changed
- evidence_needed_for_stage_b
- next_confirmation_points
- why_execution_event_not_required
- prior_state
- new_verified_fact
- changed_judgment
- uncertainty_resolved
- remaining_uncertainty
- strict_pass_gate
"""
replace_once(stage_a, old_schema, new_schema, "Stage A complete V3 producer schema")

old_strength = """execution_anchor_strength must be one of:

- strong
- moderate
- weak
- none
- unknown

Each review_pool item must include:
"""
new_strength = """Anchor-route contract for `strict_passed_spec[]`:

For every item with non-empty `format_risk_tags`, exactly one route must be complete:

1. execution route
   - non-empty `execution_anchor_type`;
   - `execution_anchor_strength: strong | moderate`;
   - `structural_value_override_applied: false`;
   - override-only fields are null or empty.
2. V3 non-execution route
   - execution-route fields are null or empty, not `weak`, `none`, or `unknown` placeholders;
   - `structural_value_override_applied: true`;
   - non-empty item-specific `structural_value_override_reason`;
   - at least one valid non-execution `anchor_classes[]` value;
   - non-empty `incremental_information`, `decision_relevance`, and `baseline_expectation_changed`;
   - non-empty `evidence_needed_for_stage_b[]`, where every entry identifies both a source/document/dataset/transcript/filing/test/report class and the exact claim, metric, stage, or date to verify;
   - non-empty `next_confirmation_points[]`, where every entry identifies a measurable event or metric that can confirm, weaken, or invalidate the interpretation;
   - specific `why_execution_event_not_required`;
   - complete before-after chain: `prior_state`, `new_verified_fact`, `changed_judgment`, `uncertainty_resolved`, and `remaining_uncertainty`.

Partial execution metadata, a generic or incomplete V3 package, dual-complete routes, or neither route complete must not enter `strict_passed_spec[]`; route the item to the appropriate review/support/reject partition.

For an ordinary strict item with empty `format_risk_tags`, `execution_anchor_type` must be non-empty and `execution_anchor_strength` must be `strong | moderate`.

Generic variants such as `official sources for confirmation`, `more evidence on adoption`, `additional data needed`, or equivalent wording do not satisfy the V3 evidence or confirmation-point contract.

Each review_pool item must include:
"""
replace_once(stage_a, old_strength, new_strength, "Stage A exactly-one route contract")

validator = ROOT / "validation_scripts/stage_lineage_contract_check.py"
old_required = """    'prior_state',
    'new_verified_fact',
    'changed_judgment',
]
STAGE_A_GENERIC_OVERRIDE_TEXT = {
    'official sources', 'company materials', 'media reports',
    'additional confirmation', 'more evidence', 'tbd', 'unknown',
}
"""
new_required = """    'prior_state',
    'new_verified_fact',
    'changed_judgment',
    'uncertainty_resolved',
    'remaining_uncertainty',
]
STAGE_A_GENERIC_OVERRIDE_FRAGMENTS = (
    'official source',
    'company material',
    'media report',
    'additional confirmation',
    'more evidence',
    'further evidence',
    'more data',
    'additional data',
    'further confirmation',
    'needs confirmation',
    'confirmation needed',
    'to be confirmed',
    'tbd',
    'unknown',
)
STAGE_A_EVIDENCE_SOURCE_CLASS_TERMS = (
    'official', 'filing', 'rule', 'regulation', 'guidance', 'order', 'notice',
    'document', 'dataset', 'statistics', 'transcript', 'technical test',
    'test result', 'independent report', 'audit', 'contract', 'permit',
    'court decision', 'legislation', 'earnings release', 'prepared remarks',
)
STAGE_A_EVIDENCE_TARGET_TERMS = (
    'claim', 'metric', 'date', 'stage', 'effective', 'eligibility', 'amount',
    'capacity', 'volume', 'price', 'cost', 'margin', 'schedule', 'probability',
    'approval', 'qualification', 'shipment', 'production', 'utilisation',
    'utilization', 'market access', 'adoption rate', 'test result', 'threshold',
)
STAGE_A_CONFIRMATION_EVENT_TERMS = (
    'publication', 'filing', 'guidance', 'approval', 'decision', 'contract',
    'award', 'permit', 'launch', 'production', 'shipment', 'qualification',
    'test result', 'effective date', 'deadline', 'schedule', 'capacity',
    'volume', 'price', 'cost', 'margin', 'utilisation', 'utilization',
    'adoption rate', 'threshold', 'probability', 'metric',
)
"""
replace_once(validator, old_required, new_required, "Stage A required package and structure constants")

old_helpers = """def _nonempty_string(value):
    return isinstance(value, str) and bool(value.strip())


def _specific_string(value):
    return _nonempty_string(value) and value.strip().lower() not in STAGE_A_GENERIC_OVERRIDE_TEXT


def validate_stage_a_v3_override(spec, spec_id, messages):
"""
new_helpers = """def _nonempty_string(value):
    return isinstance(value, str) and bool(value.strip())


def _normalized_text(value):
    return value.strip().lower() if isinstance(value, str) else ''


def _contains_generic_fragment(value):
    text = _normalized_text(value)
    return any(fragment in text for fragment in STAGE_A_GENERIC_OVERRIDE_FRAGMENTS)


def _specific_string(value):
    text = _normalized_text(value)
    return bool(text) and len(text.split()) >= 4 and not _contains_generic_fragment(text)


def _has_any_term(value, terms):
    text = _normalized_text(value)
    return any(term in text for term in terms)


def _valid_evidence_target(value):
    if isinstance(value, dict):
        source_class = value.get('source_or_document_class') or value.get('source_class')
        exact_target = value.get('exact_claim_or_metric') or value.get('verification_target')
        return _specific_string(source_class) and _specific_string(exact_target)
    return (
        _specific_string(value)
        and _has_any_term(value, STAGE_A_EVIDENCE_SOURCE_CLASS_TERMS)
        and _has_any_term(value, STAGE_A_EVIDENCE_TARGET_TERMS)
    )


def _valid_confirmation_point(value):
    if isinstance(value, dict):
        measurable = value.get('measurable_event_or_metric') or value.get('confirmation_event')
        interpretation_effect = value.get('interpretation_effect') or value.get('confirm_weaken_invalidate')
        return _specific_string(measurable) and _specific_string(interpretation_effect)
    return _specific_string(value) and _has_any_term(value, STAGE_A_CONFIRMATION_EVENT_TERMS)


def validate_stage_a_v3_override(spec, spec_id, messages):
"""
replace_once(validator, old_helpers, new_helpers, "Stage A structured target helpers")

old_target_checks = """    evidence_targets = spec.get('evidence_needed_for_stage_b')
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
"""
new_target_checks = """    evidence_targets = spec.get('evidence_needed_for_stage_b')
    if not isinstance(evidence_targets, list) or not evidence_targets:
        valid = False
    elif any(not _valid_evidence_target(value) for value in evidence_targets):
        messages.append(
            f'{spec_id}: evidence_needed_for_stage_b entries must identify both '
            'a source/document class and an exact claim, metric, stage, or date'
        )
        valid = False

    confirmation_points = spec.get('next_confirmation_points')
    if not isinstance(confirmation_points, list) or not confirmation_points:
        valid = False
    elif any(not _valid_confirmation_point(value) for value in confirmation_points):
        messages.append(
            f'{spec_id}: next_confirmation_points entries must identify measurable '
            'events or metrics, not generic confirmation requests'
        )
        valid = False
"""
replace_once(validator, old_target_checks, new_target_checks, "Stage A structured target validation")

test_path = ROOT / "validation_scripts/tests/test_review_4840844831_contracts.py"
test_path.write_text('''from __future__ import annotations

import copy
import io
import unittest
from contextlib import redirect_stdout
from pathlib import Path

from validation_scripts import stage_lineage_contract_check as lineage
from validation_scripts.tests.test_review_4840783305_contracts import (
    TestReview4840783305Contracts,
)

ROOT = Path(__file__).resolve().parents[2]
STAGE_A_PROMPT = ROOT / "docs/llm_prompts/v1/01_PROMPT_0_1_Stage_A.md"

CANONICAL_STAGE_A_FIELDS = (
    "structural_value_override_reason",
    "anchor_classes",
    "incremental_information",
    "decision_relevance",
    "baseline_expectation_changed",
    "evidence_needed_for_stage_b",
    "next_confirmation_points",
    "why_execution_event_not_required",
    "prior_state",
    "new_verified_fact",
    "changed_judgment",
    "uncertainty_resolved",
    "remaining_uncertainty",
)


class TestReview4840844831Contracts(unittest.TestCase):
    def base_spec(self):
        spec = TestReview4840783305Contracts().valid_stage_a_spec()
        spec["uncertainty_resolved"] = "The final rule resolves whether the eligibility condition is mandatory."
        spec["remaining_uncertainty"] = "Implementation timing remains subject to the final agency guidance."
        return spec

    def run_stage_a(self, spec):
        stream = io.StringIO()
        with redirect_stdout(stream):
            result = lineage.check_stage_a({"strict_passed_spec": [spec]})
        return result, stream.getvalue()

    def test_stage_a_producer_enumerates_complete_exactly_one_route_contract(self):
        text = STAGE_A_PROMPT.read_text(encoding="utf-8")
        schema_start = text.index("Each strict_passed_spec must include:")
        schema_end = text.index("stage_b_requirement_note must state:", schema_start)
        schema = text[schema_start:schema_end]
        for field in CANONICAL_STAGE_A_FIELDS:
            self.assertIn(field, schema)

        route_start = text.index("Anchor-route contract for `strict_passed_spec[]`:")
        route_end = text.index("Each review_pool item must include:", route_start)
        route = text[route_start:route_end]
        self.assertIn("exactly one route must be complete", route)
        self.assertIn("Partial execution metadata", route)
        self.assertIn("both a source/document/dataset/transcript/filing/test/report class", route)
        self.assertIn("measurable event or metric", route)

    def test_complete_structured_v3_route_passes(self):
        result, output = self.run_stage_a(self.base_spec())
        self.assertEqual(result, 0, output)
        self.assertIn("PASS_STAGE_A_SCHEMA_CONTRACT", output)

    def test_generic_evidence_variants_are_rejected(self):
        for generic in (
            "official sources for confirmation",
            "more evidence on adoption",
            "additional data needed for the claim",
        ):
            with self.subTest(generic=generic):
                spec = copy.deepcopy(self.base_spec())
                spec["evidence_needed_for_stage_b"] = [generic]
                result, output = self.run_stage_a(spec)
                self.assertEqual(result, 1)
                self.assertIn("source/document class and an exact claim", output)

    def test_non_measurable_confirmation_variants_are_rejected(self):
        for generic in (
            "additional confirmation from the market",
            "more evidence will be needed later",
            "company commentary may provide context",
        ):
            with self.subTest(generic=generic):
                spec = copy.deepcopy(self.base_spec())
                spec["next_confirmation_points"] = [generic]
                result, output = self.run_stage_a(spec)
                self.assertEqual(result, 1)
                self.assertIn("measurable events or metrics", output)

    def test_missing_uncertainty_chain_is_rejected(self):
        spec = self.base_spec()
        spec.pop("remaining_uncertainty")
        result, output = self.run_stage_a(spec)
        self.assertEqual(result, 1)
        self.assertIn("incomplete V3 override package missing remaining_uncertainty", output)


if __name__ == "__main__":
    unittest.main()
''', encoding="utf-8")

validation_log = ROOT / "docs/validation/STRUCTURAL_NEWS_VALUE_V3_VALIDATION_20260802.md"
log_text = validation_log.read_text(encoding="utf-8")
marker = "## Review 4840844831\n"
if marker not in log_text:
    validation_log.write_text(
        log_text.rstrip()
        + "\n\n## Review 4840844831\n\n"
        + "- Stage A `strict_passed_spec[]` producer schema now enumerates the complete canonical V3 non-execution package and the same exactly-one route contract enforced by the lineage validator.\n"
        + "- Stage A V3 evidence targets must encode both a source/document class and an exact claim, metric, stage, or date; substring variants of generic placeholders fail closed.\n"
        + "- `next_confirmation_points[]` must identify measurable events or metrics; generic future-confirmation wording is rejected.\n"
        + "- Focused regression covers complete-route PASS, generic-evidence FAIL, non-measurable-confirmation FAIL, and missing uncertainty-chain FAIL.\n",
        encoding="utf-8",
    )
