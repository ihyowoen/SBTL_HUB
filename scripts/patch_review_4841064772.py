from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VALIDATOR = ROOT / "validation_scripts/stage_lineage_contract_check.py"
TEST_FILE = ROOT / "validation_scripts/tests/test_review_4841064772_contracts.py"


def replace_once(path: Path, old: str, new: str, label: str) -> None:
    text = path.read_text(encoding="utf-8")
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected one match, found {count}")
    path.write_text(text.replace(old, new, 1), encoding="utf-8")


replace_once(
    VALIDATOR,
    """STAGE_A_V3_OVERRIDE_REQUIRED = [
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
    'uncertainty_resolved',
    'remaining_uncertainty',
]
""",
    """STAGE_A_V3_OVERRIDE_REQUIRED = [
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
    'uncertainty_resolved',
    'remaining_uncertainty',
]
STAGE_A_V3_NARRATIVE_FIELDS = (
    'structural_value_override_reason',
    'incremental_information',
    'decision_relevance',
    'why_execution_event_not_required',
    'prior_state',
    'new_verified_fact',
    'changed_judgment',
    'uncertainty_resolved',
    'remaining_uncertainty',
)
""",
    "narrative field contract",
)

replace_once(
    VALIDATOR,
    """def _specific_string(value):
    text = _normalized_text(value)
    return bool(text) and len(text.split()) >= 4 and not _contains_generic_fragment(text)


def _has_any_term(value, terms):
""",
    """def _specific_string(value):
    text = _normalized_text(value)
    return bool(text) and len(text.split()) >= 4 and not _contains_generic_fragment(text)


def _item_specific_narrative(value):
    if not isinstance(value, str):
        return False
    text = value.strip()
    return len(text) >= 8 and not _contains_generic_fragment(text)


def _structured_component(value):
    if not isinstance(value, str):
        return False
    text = value.strip()
    return len(text) >= 2 and not _contains_generic_fragment(text)


def _has_any_term(value, terms):
""",
    "semantic component helpers",
)

replace_once(
    VALIDATOR,
    """def _valid_evidence_target(value):
    if isinstance(value, dict):
        source_class = value.get('source_or_document_class') or value.get('source_class')
        exact_target = value.get('exact_claim_or_metric') or value.get('verification_target')
        return _specific_string(source_class) and _specific_string(exact_target)
""",
    """def _valid_evidence_target(value):
    if isinstance(value, dict):
        source_class = value.get('source_or_document_class') or value.get('source_class')
        exact_target = value.get('exact_claim_or_metric') or value.get('verification_target')
        return _structured_component(source_class) and _structured_component(exact_target)
""",
    "structured evidence target validation",
)

replace_once(
    VALIDATOR,
    """def _valid_confirmation_point(value):
    if isinstance(value, dict):
        measurable = value.get('measurable_event_or_metric') or value.get('confirmation_event')
        interpretation_effect = value.get('interpretation_effect') or value.get('confirm_weaken_invalidate')
        return _specific_string(measurable) and _specific_string(interpretation_effect)
""",
    """def _valid_confirmation_point(value):
    if isinstance(value, dict):
        measurable = value.get('measurable_event_or_metric') or value.get('confirmation_event')
        interpretation_effect = value.get('interpretation_effect') or value.get('confirm_weaken_invalidate')
        return _structured_component(measurable) and _structured_component(interpretation_effect)
""",
    "structured confirmation validation",
)

replace_once(
    VALIDATOR,
    """    for field in STAGE_A_V3_OVERRIDE_REQUIRED:
        if missing_nonempty(spec, field):
            messages.append(f'{spec_id}: incomplete V3 override package missing {field}')
            valid = False

    classes = spec.get('anchor_classes')
""",
    """    for field in STAGE_A_V3_OVERRIDE_REQUIRED:
        if missing_nonempty(spec, field):
            messages.append(f'{spec_id}: incomplete V3 override package missing {field}')
            valid = False

    for field in STAGE_A_V3_NARRATIVE_FIELDS:
        if not _item_specific_narrative(spec.get(field)):
            messages.append(f'{spec_id}: {field} must be item-specific narrative text')
            valid = False

    if spec.get('baseline_expectation_changed') is not True:
        messages.append(f'{spec_id}: baseline_expectation_changed must be true for v3_non_execution')
        valid = False

    classes = spec.get('anchor_classes')
""",
    "narrative semantic validation",
)

replace_once(
    VALIDATOR,
    """    if not _specific_string(spec.get('structural_value_override_reason')):
        messages.append(f'{spec_id}: structural_value_override_reason must be item-specific')
        valid = False
    if not _specific_string(spec.get('why_execution_event_not_required')):
        messages.append(f'{spec_id}: why_execution_event_not_required must be item-specific')
        valid = False

    return valid
""",
    """    return valid
""",
    "remove duplicate prose heuristics",
)

TEST_FILE.write_text(
    '''from __future__ import annotations

import copy
import io
import unittest
from contextlib import redirect_stdout

from validation_scripts import stage_lineage_contract_check as lineage
from validation_scripts.tests.test_review_4840844831_contracts import (
    TestReview4840844831Contracts,
)


class TestReview4841064772Contracts(unittest.TestCase):
    def base_spec(self):
        return TestReview4840844831Contracts().base_spec()

    def run_stage_a(self, spec):
        stream = io.StringIO()
        with redirect_stdout(stream):
            result = lineage.check_stage_a({"strict_passed_spec": [spec]})
        return result, stream.getvalue()

    def test_every_narrative_field_requires_item_specific_string(self):
        for field in lineage.STAGE_A_V3_NARRATIVE_FIELDS:
            with self.subTest(field=field):
                spec = copy.deepcopy(self.base_spec())
                spec[field] = False
                result, output = self.run_stage_a(spec)
                self.assertEqual(result, 1)
                self.assertIn(f"{field} must be item-specific narrative text", output)

    def test_unrelated_container_is_not_narrative_content(self):
        spec = copy.deepcopy(self.base_spec())
        spec["changed_judgment"] = {"status": "present"}
        result, output = self.run_stage_a(spec)
        self.assertEqual(result, 1)
        self.assertIn("changed_judgment must be item-specific narrative text", output)

    def test_baseline_expectation_changed_must_be_true(self):
        spec = copy.deepcopy(self.base_spec())
        spec["baseline_expectation_changed"] = False
        result, output = self.run_stage_a(spec)
        self.assertEqual(result, 1)
        self.assertIn("baseline_expectation_changed must be true", output)

    def test_concise_structured_evidence_targets_pass(self):
        targets = (
            {
                "source_or_document_class": "SEC filing",
                "exact_claim_or_metric": "2027 revenue",
            },
            {
                "source_or_document_class": "금감원 공시",
                "exact_claim_or_metric": "2027년 매출",
            },
        )
        for target in targets:
            with self.subTest(target=target):
                spec = copy.deepcopy(self.base_spec())
                spec["evidence_needed_for_stage_b"] = [target]
                result, output = self.run_stage_a(spec)
                self.assertEqual(result, 0, output)

    def test_generic_structured_target_still_fails(self):
        spec = copy.deepcopy(self.base_spec())
        spec["evidence_needed_for_stage_b"] = [{
            "source_or_document_class": "official source",
            "exact_claim_or_metric": "more evidence",
        }]
        result, output = self.run_stage_a(spec)
        self.assertEqual(result, 1)
        self.assertIn("source/document class and an exact claim", output)

    def test_concise_structured_confirmation_point_passes(self):
        spec = copy.deepcopy(self.base_spec())
        spec["next_confirmation_points"] = [{
            "measurable_event_or_metric": "2027 revenue",
            "interpretation_effect": "confirm thesis",
        }]
        result, output = self.run_stage_a(spec)
        self.assertEqual(result, 0, output)


if __name__ == "__main__":
    unittest.main()
''',
    encoding="utf-8",
)
