from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TARGET = ROOT / "validation_scripts/stage_lineage_contract_check.py"


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected one match, found {count}")
    return text.replace(old, new)


text = TARGET.read_text(encoding="utf-8")
text = replace_once(
    text,
    "import json\nimport sys\n",
    "import json\nimport re\nimport sys\n",
    "add regex import",
)
text = replace_once(
    text,
    """STAGE_A_PLACEHOLDER_NARRATIVE_TOKENS = {
    'not', 'provided', 'available', 'specified', 'applicable', 'no',
    'information', 'details', 'data', 'none', 'placeholder', 'dummy',
    'text', 'n/a', 'na', 'nil', 'yet', '미제공', '정보', '자료', '없음',
    '해당', '확인', '불가',
}
""",
    """STAGE_A_PLACEHOLDER_NARRATIVE_TOKENS = {
    'not', 'provided', 'available', 'specified', 'applicable', 'disclosed',
    'known', 'no', 'information', 'details', 'data', 'none', 'placeholder',
    'dummy', 'text', 'n/a', 'na', 'nil', 'yet', 'unavailable', 'undisclosed',
    'missing', 'unknown', '미제공', '미공개', '비공개', '정보', '자료', '내용',
    '없음', '해당', '확인', '불가', '아직',
}
STAGE_A_PLACEHOLDER_NARRATIVE_PATTERNS = (
    r'\\b(?:not|no|none)\\s+(?:yet\\s+)?(?:provided|available|specified|applicable|disclosed|known)\\b',
    r'\\b(?:information|details|data)\\s+(?:is\\s+)?(?:not\\s+)?(?:available|unavailable|missing|unknown|undisclosed)\\b',
    r'\\b(?:unavailable|undisclosed|unknown)\\s+(?:information|details|data)\\b',
)
""",
    "expand placeholder semantics",
)
text = replace_once(
    text,
    """def _placeholder_only_text(value):
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
""",
    """def _placeholder_only_text(value):
    text = _normalized_text(value)
    if not text:
        return True
    normalized = ' '.join(
        text.replace('.', ' ').replace(',', ' ').replace(':', ' ')
        .replace(';', ' ').replace('-', ' ').strip().split()
    )
    if normalized in STAGE_A_PLACEHOLDER_NARRATIVE_PHRASES:
        return True
    if any(re.fullmatch(pattern, normalized) for pattern in STAGE_A_PLACEHOLDER_NARRATIVE_PATTERNS):
        return True
    tokens = normalized.split()
    if bool(tokens) and len(tokens) <= 5 and all(
        token in STAGE_A_PLACEHOLDER_NARRATIVE_TOKENS for token in tokens
    ):
        return True
    korean_absence = ('없음', '미제공', '미공개', '비공개', '불가')
    korean_subject = ('정보', '자료', '내용', '세부', '사항')
    return (
        len(tokens) <= 5
        and any(marker in normalized for marker in korean_absence)
        and any(subject in normalized for subject in korean_subject)
    )
""",
    "semantic placeholder detection",
)
text = replace_once(
    text,
    """def _structured_exact_target(value):
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
""",
    """def _structured_exact_target(value):
    if not _structured_component(value):
        return False
    text = _normalized_text(value)
    tokens = [token for token in text.replace('/', ' ').replace(':', ' ').split() if token]
    has_named_target = len(tokens) >= 2 and any(
        re.search(r'[a-z가-힣]', token) for token in tokens
    )
    is_explicit_date = bool(re.fullmatch(
        r'(?:19|20|21)\\d{2}(?:[-/.](?:0?[1-9]|1[0-2])(?:[-/.](?:0?[1-9]|[12]\\d|3[01]))?|년(?:\\s*(?:0?[1-9]|1[0-2])월(?:\\s*(?:0?[1-9]|[12]\\d|3[01])일)?)?)?',
        text,
    ))
    has_qualified_numeric_target = (
        any(char.isdigit() for char in text)
        and any(re.search(r'[a-z가-힣]', token) for token in tokens)
        and (has_named_target or _has_any_term(value, STAGE_A_EXACT_TARGET_TERMS))
    )
    return (
        is_explicit_date
        or has_qualified_numeric_target
        or has_named_target
        or _has_any_term(value, STAGE_A_EXACT_TARGET_TERMS)
    )
""",
    "require qualified numeric targets",
)
text = replace_once(
    text,
    """def _has_any_term(value, terms):
    text = _normalized_text(value)
    return any(term in text for term in terms)
""",
    """def _term_pattern(term):
    return rf'(?<![\\w]){re.escape(term)}(?![\\w])'


def _matching_terms(value, terms):
    text = _normalized_text(value)
    return [
        term for term in sorted(terms, key=len, reverse=True)
        if re.search(_term_pattern(term), text)
    ]


def _has_any_term(value, terms):
    return bool(_matching_terms(value, terms))
""",
    "match role keywords as complete terms",
)
text = replace_once(
    text,
    """    matched_source_terms = [term for term in STAGE_A_EVIDENCE_SOURCE_CLASS_TERMS if term in text]
    if not matched_source_terms:
        return False

    target_text = text
    for term in sorted(matched_source_terms, key=len, reverse=True):
        target_text = target_text.replace(term, ' ')
""",
    """    matched_source_terms = _matching_terms(text, STAGE_A_EVIDENCE_SOURCE_CLASS_TERMS)
    if not matched_source_terms:
        return False

    target_text = text
    for term in matched_source_terms:
        target_text = re.sub(_term_pattern(term), ' ', target_text)
""",
    "use complete-term source matching",
)
TARGET.write_text(text, encoding="utf-8")

TEST = ROOT / "validation_scripts/tests/test_review_4841207046_followup_contracts.py"
TEST.write_text(r'''from __future__ import annotations

import copy
import io
import sys
import unittest
from contextlib import redirect_stdout
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from validation_scripts import stage_lineage_contract_check as lineage
from validation_scripts.tests.test_review_4840844831_contracts import (
    TestReview4840844831Contracts,
)


class TestReview4841207046FollowupContracts(unittest.TestCase):
    def base_spec(self):
        return TestReview4840844831Contracts().base_spec()

    def run_stage_a(self, spec):
        stream = io.StringIO()
        with redirect_stdout(stream):
            result = lineage.check_stage_a({"strict_passed_spec": [spec]})
        return result, stream.getvalue()

    def test_placeholder_semantic_variants_fail(self):
        for placeholder in (
            "not disclosed",
            "information unavailable",
            "아직 정보 없음",
            "세부 자료 미공개",
        ):
            with self.subTest(placeholder=placeholder):
                spec = copy.deepcopy(self.base_spec())
                for field in lineage.STAGE_A_V3_NARRATIVE_FIELDS:
                    spec[field] = placeholder
                result, output = self.run_stage_a(spec)
                self.assertEqual(result, 1)
                self.assertIn("must be item-specific narrative text", output)

    def test_bare_number_is_not_exact_or_measurable_target(self):
        for field, entry in (
            ("evidence_needed_for_stage_b", {
                "source_or_document_class": "SEC filing",
                "exact_claim_or_metric": "99",
            }),
            ("next_confirmation_points", {
                "measurable_event_or_metric": "99",
                "interpretation_effect": "confirm thesis",
            }),
        ):
            with self.subTest(field=field):
                spec = copy.deepcopy(self.base_spec())
                spec[field] = [entry]
                result, _ = self.run_stage_a(spec)
                self.assertEqual(result, 1)

    def test_explicit_year_and_qualified_metric_still_pass(self):
        spec = copy.deepcopy(self.base_spec())
        spec["evidence_needed_for_stage_b"] = [{
            "source_or_document_class": "SEC filing",
            "exact_claim_or_metric": "2027 revenue",
        }]
        spec["next_confirmation_points"] = [{
            "measurable_event_or_metric": "2027",
            "interpretation_effect": "confirm thesis",
        }]
        result, output = self.run_stage_a(spec)
        self.assertEqual(result, 0, output)

    def test_source_and_effect_terms_require_complete_word_matches(self):
        invalid_cases = (
            ("evidence_needed_for_stage_b", {
                "source_or_document_class": "unofficial rumor",
                "exact_claim_or_metric": "2027 revenue",
            }),
            ("next_confirmation_points", {
                "measurable_event_or_metric": "2027 revenue",
                "interpretation_effect": "unchanged",
            }),
        )
        for field, entry in invalid_cases:
            with self.subTest(field=field):
                spec = copy.deepcopy(self.base_spec())
                spec[field] = [entry]
                result, _ = self.run_stage_a(spec)
                self.assertEqual(result, 1)


if __name__ == "__main__":
    unittest.main()
''', encoding="utf-8")
