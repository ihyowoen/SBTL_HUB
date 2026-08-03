from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VALIDATOR = ROOT / "validation_scripts/stage_lineage_contract_check.py"
TEST = ROOT / "validation_scripts/tests/test_review_latest_stage_a_routes.py"


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise RuntimeError(f"{label}: expected exactly one target, found {count}")
    return text.replace(old, new, 1)


text = VALIDATOR.read_text(encoding="utf-8")

old_terms = """STAGE_A_EVIDENCE_SOURCE_CLASS_TERMS = (
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
"""
new_terms = """STAGE_A_EVIDENCE_SOURCE_CLASS_TERMS = (
    'official', 'filing', 'rule', 'regulation', 'guidance', 'order', 'notice',
    'document', 'dataset', 'statistics', 'transcript', 'technical test',
    'test result', 'independent report', 'audit', 'contract', 'permit',
    'court decision', 'legislation', 'earnings release', 'prepared remarks',
    '공식', '공시', '규정', '지침', '명령', '고시', '문서', '데이터셋',
    '통계', '회의록', '시험', '시험결과', '보고서', '감사', '계약',
    '허가', '판결', '법률', '실적발표', '준비발언',
)
"""
text = replace_once(text, old_terms, new_terms, "evidence source terms")

old_target = """def _valid_evidence_target(value):
    if isinstance(value, dict):
        source_class = value.get('source_or_document_class') or value.get('source_class')
        exact_target = value.get('exact_claim_or_metric') or value.get('verification_target')
        return _specific_string(source_class) and _specific_string(exact_target)
    return (
        _specific_string(value)
        and _has_any_term(value, STAGE_A_EVIDENCE_SOURCE_CLASS_TERMS)
        and _has_any_term(value, STAGE_A_EVIDENCE_TARGET_TERMS)
    )
"""
new_target = """def _valid_evidence_target(value):
    if isinstance(value, dict):
        source_class = value.get('source_or_document_class') or value.get('source_class')
        exact_target = value.get('exact_claim_or_metric') or value.get('verification_target')
        return _specific_string(source_class) and _specific_string(exact_target)

    text = _normalized_text(value)
    if not text or _contains_generic_fragment(text):
        return False
    matched_source_terms = [term for term in STAGE_A_EVIDENCE_SOURCE_CLASS_TERMS if term in text]
    if not matched_source_terms:
        return False

    target_text = text
    for term in sorted(matched_source_terms, key=len, reverse=True):
        target_text = target_text.replace(term, ' ')
    target_tokens = [token for token in target_text.replace('/', ' ').replace(':', ' ').split() if token]
    has_exact_metric_or_date = any(any(char.isdigit() for char in token) for token in target_tokens)
    has_named_target = len(target_tokens) >= 2
    return has_exact_metric_or_date or has_named_target
"""
text = replace_once(text, old_target, new_target, "structured evidence target validation")

old_execution = """    execution_type = spec.get('execution_anchor_type')
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
"""
new_execution = """    execution_type = spec.get('execution_anchor_type')
    execution_strength = spec.get('execution_anchor_strength')
    execution_core_complete = (
        _nonempty_string(execution_type)
        and execution_strength in STAGE_A_ALLOWED_EXECUTION_ANCHOR_STRENGTH
    )
    override_marker = spec.get('structural_value_override_applied')
    residual_override_fields = [
        field for field in STAGE_A_V3_OVERRIDE_REQUIRED
        if spec.get(field) not in (None, '', [], {})
    ]
    execution_path_complete = (
        execution_core_complete
        and override_marker is False
        and not residual_override_fields
    )

    if has_format_risk:
        override_path_complete = validate_stage_a_v3_override(spec, spec_id, messages)
        if execution_core_complete and override_marker is not False:
            messages.append(
                f'{spec_id}: execution route requires structural_value_override_applied=false'
            )
        if execution_core_complete and residual_override_fields:
            messages.append(
                f'{spec_id}: execution route must leave override-only fields empty; '
                f'found {residual_override_fields}'
            )
        if execution_path_complete == override_path_complete:
            messages.append(
                f'{spec_id}: format-risk strict_passed_spec requires exactly one complete '
                'execution or v3_non_execution path'
            )
        if (execution_type or execution_strength) and not execution_core_complete:
            messages.append(f'{spec_id}: partial/invalid execution path metadata for format-risk strict_passed_spec')
"""
text = replace_once(text, old_execution, new_execution, "execution route residual validation")

VALIDATOR.write_text(text, encoding="utf-8")

TEST.write_text('''from __future__ import annotations

import copy
import io
import unittest
from contextlib import redirect_stdout

from validation_scripts import stage_lineage_contract_check as lineage
from validation_scripts.tests.test_review_4840844831_contracts import (
    TestReview4840844831Contracts,
)


class TestLatestStageARouteReview(unittest.TestCase):
    def base_v3_spec(self):
        return TestReview4840844831Contracts().base_spec()

    def run_stage_a(self, spec):
        stream = io.StringIO()
        with redirect_stdout(stream):
            result = lineage.check_stage_a({"strict_passed_spec": [spec]})
        return result, stream.getvalue()

    def clean_execution_spec(self):
        spec = self.base_v3_spec()
        spec["execution_anchor_type"] = "commercial_award"
        spec["execution_anchor_strength"] = "strong"
        spec["structural_value_override_applied"] = False
        for field in lineage.STAGE_A_V3_OVERRIDE_REQUIRED:
            spec[field] = [] if field in {"anchor_classes", "evidence_needed_for_stage_b", "next_confirmation_points"} else None
        return spec

    def test_clean_execution_route_passes(self):
        result, output = self.run_stage_a(self.clean_execution_spec())
        self.assertEqual(result, 0, output)
        self.assertIn("PASS_STAGE_A_SCHEMA_CONTRACT", output)

    def test_execution_route_requires_explicit_false_marker(self):
        spec = self.clean_execution_spec()
        spec.pop("structural_value_override_applied")
        result, output = self.run_stage_a(spec)
        self.assertEqual(result, 1)
        self.assertIn("requires structural_value_override_applied=false", output)

    def test_execution_route_rejects_residual_override_package(self):
        spec = self.clean_execution_spec()
        spec["structural_value_override_reason"] = "Residual strategic rationale must not remain on the execution path."
        spec["anchor_classes"] = ["strategic_behavior_anchor"]
        result, output = self.run_stage_a(spec)
        self.assertEqual(result, 1)
        self.assertIn("must leave override-only fields empty", output)

    def test_exact_unlisted_and_korean_targets_pass(self):
        for target in ("SEC filing 2027 revenue", "금감원 공시 2027년 매출"):
            with self.subTest(target=target):
                spec = copy.deepcopy(self.base_v3_spec())
                spec["evidence_needed_for_stage_b"] = [target]
                result, output = self.run_stage_a(spec)
                self.assertEqual(result, 0, output)

    def test_generic_target_still_fails(self):
        spec = self.base_v3_spec()
        spec["evidence_needed_for_stage_b"] = ["official sources for confirmation"]
        result, output = self.run_stage_a(spec)
        self.assertEqual(result, 1)
        self.assertIn("source/document class and an exact claim", output)


if __name__ == "__main__":
    unittest.main()
''', encoding="utf-8")
