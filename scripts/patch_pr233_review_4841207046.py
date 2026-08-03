from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def replace_once(path: Path, old: str, new: str, label: str) -> None:
    text = path.read_text(encoding="utf-8")
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected exactly one match, found {count}")
    path.write_text(text.replace(old, new), encoding="utf-8")


related_path = ROOT / "validation_scripts/related_lifecycle_check.py"
replace_once(
    related_path,
    '''    if unresolved and card.get("state") in {"github_merge_ready", "production_verified"}:
        errors.append("unresolved related_candidate_spec_ids remain after merge prep")
''',
    '''    if unresolved and not allow_provisional_related:
        errors.append("unresolved related_candidate_spec_ids remain after merge prep")
''',
    "reject unresolved provisional edges whenever the explicit allowance is absent",
)

stage_path = ROOT / "validation_scripts/stage_lineage_contract_check.py"
replace_once(
    stage_path,
    '''STAGE_A_GENERIC_OVERRIDE_FRAGMENTS = (
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
''',
    '''STAGE_A_GENERIC_OVERRIDE_FRAGMENTS = (
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
STAGE_A_PLACEHOLDER_NARRATIVE_PHRASES = {
    'not provided', 'not available', 'not specified', 'not applicable',
    'no information', 'no details', 'no data', 'none provided',
    'placeholder', 'dummy text', 'n/a', 'na', 'nil', 'none',
    '미제공', '정보 없음', '자료 없음', '해당 없음', '확인 불가',
}
STAGE_A_PLACEHOLDER_NARRATIVE_TOKENS = {
    'not', 'provided', 'available', 'specified', 'applicable', 'no',
    'information', 'details', 'data', 'none', 'placeholder', 'dummy',
    'text', 'n/a', 'na', 'nil', 'yet', '미제공', '정보', '자료', '없음',
    '해당', '확인', '불가',
}
STAGE_A_EXACT_TARGET_TERMS = (
    'revenue', 'sales', 'ebitda', 'ebit', 'profit', 'margin', 'cost',
    'price', 'volume', 'capacity', 'utilisation', 'utilization', 'yield',
    'throughput', 'capex', 'opex', 'deadline', 'date', 'stage', 'status',
    'probability', 'adoption', 'approval', 'production', 'shipment',
    '매출', '영업이익', '이익', '마진', '원가', '가격', '물량', '용량',
    '가동률', '수율', '투자', '기한', '날짜', '단계', '상태', '확률',
    '채택', '승인', '생산', '출하',
)
STAGE_A_INTERPRETATION_EFFECT_TERMS = (
    'confirm', 'strengthen', 'support', 'weaken', 'invalidate', 'reject',
    'revise', 'change', 'raise', 'lower', 'increase', 'decrease', 'hold',
    '확인', '강화', '지지', '약화', '무효', '기각', '수정', '변경',
    '상향', '하향', '증가', '감소', '유지',
)
STAGE_A_EVIDENCE_SOURCE_CLASS_TERMS = (
''',
    "add placeholder and structured-role vocabularies",
)

replace_once(
    stage_path,
    '''def _item_specific_narrative(value):
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
''',
    '''def _placeholder_only_text(value):
    text = _normalized_text(value)
    if not text:
        return True
    normalized = ' '.join(
        text.replace('.', ' ').replace(',', ' ').replace(':', ' ')
        .replace(';', ' ').replace('-', ' ').strip().split()
    )
    if normalized in STAGE_A_PLACEHOLDER_NARRATIVE_PHRASES:
        return True
    tokens = normalized.split()
    return bool(tokens) and len(tokens) <= 4 and all(
        token in STAGE_A_PLACEHOLDER_NARRATIVE_TOKENS for token in tokens
    )


def _item_specific_narrative(value):
    if not isinstance(value, str):
        return False
    text = value.strip()
    return (
        len(text) >= 8
        and not _contains_generic_fragment(text)
        and not _placeholder_only_text(text)
    )


def _structured_component(value):
    if not isinstance(value, str):
        return False
    text = value.strip()
    return (
        len(text) >= 2
        and not _contains_generic_fragment(text)
        and not _placeholder_only_text(text)
    )


def _structured_source_class(value):
    return _structured_component(value) and _has_any_term(
        value, STAGE_A_EVIDENCE_SOURCE_CLASS_TERMS
    )


def _structured_exact_target(value):
    if not _structured_component(value):
        return False
    text = _normalized_text(value)
    tokens = [token for token in text.replace('/', ' ').replace(':', ' ').split() if token]
    has_number_or_date = any(any(char.isdigit() for char in token) for token in tokens)
    has_named_target = len(tokens) >= 2
    return (
        has_number_or_date
        or has_named_target
        or _has_any_term(value, STAGE_A_EXACT_TARGET_TERMS)
    )


def _structured_interpretation_effect(value):
    return _structured_component(value) and _has_any_term(
        value, STAGE_A_INTERPRETATION_EFFECT_TERMS
    )


def _has_any_term(value, terms):
''',
    "validate placeholder narratives and structured component roles",
)

replace_once(
    stage_path,
    '''        return _structured_component(source_class) and _structured_component(exact_target)
''',
    '''        return _structured_source_class(source_class) and _structured_exact_target(exact_target)
''',
    "validate structured evidence source and exact-target roles",
)

replace_once(
    stage_path,
    '''        return _structured_component(measurable) and _structured_component(interpretation_effect)
''',
    '''        return _structured_exact_target(measurable) and _structured_interpretation_effect(interpretation_effect)
''',
    "validate structured confirmation metric and interpretation roles",
)

test_path = ROOT / "validation_scripts/tests/test_review_4841207046_contracts.py"
test_path.write_text(
    '''from __future__ import annotations

import copy
import io
import unittest
from contextlib import redirect_stdout

from validation_scripts import related_lifecycle_check as related
from validation_scripts import stage_lineage_contract_check as lineage
from validation_scripts.tests.test_review_4840844831_contracts import (
    TestReview4840844831Contracts,
)


class TestReview4841207046Contracts(unittest.TestCase):
    def base_spec(self):
        return TestReview4840844831Contracts().base_spec()

    def run_stage_a(self, spec):
        stream = io.StringIO()
        with redirect_stdout(stream):
            result = lineage.check_stage_a({"strict_passed_spec": [spec]})
        return result, stream.getvalue()

    def test_placeholder_narratives_fail_closed(self):
        for placeholder in ("not provided", "not provided yet", "N/A", "정보 없음"):
            with self.subTest(placeholder=placeholder):
                spec = copy.deepcopy(self.base_spec())
                for field in lineage.STAGE_A_V3_NARRATIVE_FIELDS:
                    spec[field] = placeholder
                result, output = self.run_stage_a(spec)
                self.assertEqual(result, 1)
                self.assertIn("must be item-specific narrative text", output)

    def test_meaningless_structured_evidence_target_fails(self):
        spec = copy.deepcopy(self.base_spec())
        spec["evidence_needed_for_stage_b"] = [{
            "source_or_document_class": "xx",
            "exact_claim_or_metric": "yy",
        }]
        result, output = self.run_stage_a(spec)
        self.assertEqual(result, 1)
        self.assertIn("source/document class and an exact claim", output)

    def test_meaningless_structured_confirmation_fails(self):
        spec = copy.deepcopy(self.base_spec())
        spec["next_confirmation_points"] = [{
            "measurable_event_or_metric": "xx",
            "interpretation_effect": "yy",
        }]
        result, output = self.run_stage_a(spec)
        self.assertEqual(result, 1)
        self.assertIn("measurable events or metrics", output)

    def test_concise_role_valid_structured_values_still_pass(self):
        spec = copy.deepcopy(self.base_spec())
        spec["evidence_needed_for_stage_b"] = [{
            "source_or_document_class": "SEC filing",
            "exact_claim_or_metric": "2027 revenue",
        }]
        spec["next_confirmation_points"] = [{
            "measurable_event_or_metric": "2027 revenue",
            "interpretation_effect": "confirm thesis",
        }]
        result, output = self.run_stage_a(spec)
        self.assertEqual(result, 0, output)

    def test_merge_prep_rejects_provisional_edges_regardless_of_state(self):
        parent = {"id": "PARENT", "date": "2026-08-01"}
        child = {
            "id": "CHILD",
            "date": "2026-08-02",
            "related": ["PARENT"],
            "related_candidate_spec_ids": ["DRAFT_OTHER"],
            "related_lineage": {
                "status": "PASS",
                "same_event_checked": True,
                "earliest_same_event_date_checked": True,
                "relation_type": "program_lineage",
                "related_ids": ["PARENT"],
                "reason": "Final edge exists but one provisional edge is still unresolved.",
            },
        }
        errors, warnings = related.check_card(
            child,
            {"PARENT": parent, "CHILD": child},
            require_contract=True,
            allow_provisional_related=False,
        )
        self.assertEqual(warnings, [])
        self.assertIn(
            "unresolved related_candidate_spec_ids remain after merge prep",
            errors,
        )


if __name__ == "__main__":
    unittest.main()
''',
    encoding="utf-8",
)
