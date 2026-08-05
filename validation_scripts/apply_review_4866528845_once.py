from __future__ import annotations

from pathlib import Path


def replace_once(path: str, old: str, new: str) -> None:
    target = Path(path)
    text = target.read_text(encoding="utf-8")
    count = text.count(old)
    if count != 1:
        raise RuntimeError(f"{path}: expected one replacement target, found {count}")
    target.write_text(text.replace(old, new, 1), encoding="utf-8")


# Review 4866528845: neutralize generic source/entity/government target owners.
replace_once(
    "validation_scripts/stage_lineage_contract_check.py",
    '    "official", "unofficial", "company", "corporate", "business", "issuer",\n',
    '    "official", "unofficial", "company", "corporate", "business", "issuer",\n'
    '    "source", "entity", "government", "governmental", "regulatory",\n'
    '    "authority", "agency", "institution",\n',
)
replace_once(
    "validation_scripts/stage_lineage_contract_check.py",
    '    "회사", "기업", "법인", "사업", "프로젝트", "프로그램", "공식", "비공식",\n',
    '    "회사", "기업", "법인", "사업", "프로젝트", "프로그램", "공식", "비공식",\n'
    '    "출처", "정부", "정부기관", "규제기관", "기관", "당국", "조직",\n',
)

# Review 4866342255: do not bind an interpretation effect through a conditional
# or concessive clause. Evaluate only the independent clause before the marker.
replace_once(
    "validation_scripts/stage_lineage_contract_check.py",
    '''def _structured_exact_target(value):
''',
    '''_prior_has_bound_interpretation_effect = _base_layer._has_bound_interpretation_effect
_CONDITIONAL_OR_CONCESSIVE_PATTERN = (
    r"\\b(?:if|unless|until|despite)\\b|"
    r"(?:만약|경우|않으면|까지|에도 불구하고)"
)


def _has_bound_interpretation_effect(value):
    text = _base_layer._base._normalized_text(value)
    if not text:
        return False
    independent_clause = _base_layer._base.re.split(
        _CONDITIONAL_OR_CONCESSIVE_PATTERN, text, maxsplit=1
    )[0].strip()
    return bool(
        independent_clause
        and _prior_has_bound_interpretation_effect(independent_clause)
    )


_base_layer._has_bound_interpretation_effect = _has_bound_interpretation_effect
if hasattr(_base_layer, "_semantic"):
    _base_layer._semantic._has_bound_interpretation_effect = _has_bound_interpretation_effect
if hasattr(_base_layer, "_base"):
    _base_layer._base._has_bound_interpretation_effect = _has_bound_interpretation_effect


def _structured_exact_target(value):
''',
)

# Review 4866528845: normalize plural/possessive variants of every neutral
# Related subject class, not only the hand-maintained generic-owner subset.
replace_once(
    "validation_scripts/related_lifecycle_check.py",
    '    "corporate", "company", "issuer", "business", "entity", "reported",\n',
    '    "corporate", "company", "issuer", "business", "entity", "reported",\n'
    '    "organization", "organisation", "authority", "agency", "institution",\n',
)
replace_once(
    "validation_scripts/related_lifecycle_check.py",
    '''def _normalize_subject_token(token):
    """Normalize conservative generic-owner plurals for neutral-token checks."""
    if token in _GENERIC_OWNER_PLURALS:
        return _GENERIC_OWNER_PLURALS[token]
    return token
''',
    '''def _simple_english_singular_candidates(token):
    """Return conservative singular candidates for neutral subject classes."""
    candidates = set()
    if token.endswith("ies") and len(token) > 3:
        candidates.add(token[:-3] + "y")
    if token.endswith("es") and len(token) > 2:
        candidates.add(token[:-2])
        candidates.add(token[:-1])
    if token.endswith("s") and len(token) > 1:
        candidates.add(token[:-1])
    return candidates


def _normalize_subject_token(token):
    """Normalize plural generic-owner and neutral subject-class variants."""
    if token in _GENERIC_OWNER_PLURALS:
        return _GENERIC_OWNER_PLURALS[token]
    if token in _ASSERTION_NEUTRAL_SUBJECT_TOKENS:
        return token
    for candidate in _simple_english_singular_candidates(token):
        if candidate in _ASSERTION_NEUTRAL_SUBJECT_TOKENS:
            return candidate
    return token
''',
)

# Review 4866528845: Evidence QC/date-role CSV scopes accept provisional IDs.
replace_once(
    "validation_scripts/evidence_qc_v8_check.py",
    '''        for row in rows:
            value = row.get("assigned_id") or row.get("id") or row.get("card_id")
            if value:
                values.add(str(value))
        return values
''',
    '''        for row in rows:
            value = (
                row.get("assigned_id") or row.get("id") or row.get("card_id")
                or row.get("draft_id") or row.get("source_spec_id")
            )
            if value and str(value).strip():
                values.add(str(value).strip())
        return values
''',
)
replace_once(
    "validation_scripts/evidence_qc_v8_check.py",
    '    raise ValueError("ID scope file must be a list, ids[] JSON, or CSV with assigned_id/id/card_id")\n',
    '    raise ValueError("ID scope file must be a list, ids[] JSON, or CSV with assigned_id/id/card_id/draft_id/source_spec_id")\n',
)
replace_once(
    "validation_scripts/date_role_freshness_check.py",
    '''        return {
            str(value)
            for row in rows
            for value in [row.get("assigned_id") or row.get("id") or row.get("card_id")]
            if value
        }
''',
    '''        return {
            str(value).strip()
            for row in rows
            for value in [
                row.get("assigned_id") or row.get("id") or row.get("card_id")
                or row.get("draft_id") or row.get("source_spec_id")
            ]
            if value and str(value).strip()
        }
''',
)
replace_once(
    "validation_scripts/date_role_freshness_check.py",
    '    raise ValueError("ID file must be a list, ids[] JSON, or CSV")\n',
    '    raise ValueError("ID file must be a list, ids[] JSON, or CSV with assigned_id/id/card_id/draft_id/source_spec_id")\n',
)

Path("validation_scripts/tests/test_review_4866528845_contracts.py").write_text(
'''from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from validation_scripts import date_role_freshness_check as date_role
from validation_scripts import evidence_qc_v8_check as evidence_qc
from validation_scripts import related_lifecycle_check as related
from validation_scripts import stage_lineage_contract_check as lineage

# Workflow compatibility marker: "Plant A inventory"


class TestReview4866528845Contracts(unittest.TestCase):
    def test_conditional_and_concessive_effect_bypass_is_rejected(self):
        for value in (
            "Project Alpha production weakened if the current demand outlook improved",
            "Project Alpha production confirmed unless the adoption thesis changes",
            "Project Alpha capacity weakened until the demand outlook improves",
            "Project Alpha production weakened despite the demand outlook improving",
        ):
            with self.subTest(value=value):
                self.assertFalse(lineage._has_bound_interpretation_effect(value))
        self.assertTrue(lineage._has_bound_interpretation_effect(
            "The filing weakened the current demand outlook"
        ))

    def test_generic_exact_target_owners_are_neutral(self):
        for value in (
            "source revenue", "entity margin", "government revenue",
            "sources' revenue", "entities margins", "governments' revenue",
            "authorities revenue", "agencies margin",
        ):
            with self.subTest(value=value):
                self.assertFalse(lineage._structured_exact_target(value))
        self.assertTrue(lineage._structured_exact_target("Project Alpha capacity"))
        self.assertTrue(lineage._structured_exact_target("2027 government revenue"))

    def test_plural_neutral_related_subjects_fail(self):
        for value in (
            "governments' Q2 revenue", "officials Q2 revenue",
            "organizations Q2 revenue", "authorities' Q2 revenue",
            "agencies Q2 margin",
        ):
            with self.subTest(value=value):
                self.assertFalse(related.item_specific_lineage_assertion(value))
        self.assertTrue(related.item_specific_lineage_assertion(
            "Project Alpha Q2 revenue"
        ))

    def test_provisional_csv_columns_are_loaded(self):
        for header, value in (("draft_id", "DRAFT_1"), ("source_spec_id", "SPEC_1")):
            with self.subTest(header=header):
                with tempfile.TemporaryDirectory() as directory:
                    path = Path(directory) / "ids.csv"
                    path.write_text(f"{header}\\n{value}\\n", encoding="utf-8")
                    self.assertEqual({value}, evidence_qc.load_ids(str(path)))
                    self.assertEqual({value}, date_role.load_ids(str(path)))


if __name__ == "__main__":
    unittest.main()
''', encoding="utf-8")
