from __future__ import annotations

from pathlib import Path


stage = Path("validation_scripts/stage_lineage_contract_check.py")
text = stage.read_text(encoding="utf-8")
marker = "_CONDITIONAL_OR_CONCESSIVE_PATTERN"
if marker not in text:
    anchor = "\ndef _structured_exact_target(value):\n"
    patch = '''
_prior_has_bound_interpretation_effect = _base_layer._has_bound_interpretation_effect
_CONDITIONAL_OR_CONCESSIVE_PATTERN = (
    r"\\b(?:if|unless|until|despite)\\b|"
    r"(?:만약|경우|않으면|까지|에도 불구하고)"
)


def _has_bound_interpretation_effect(value):
    """Do not bind an interpretation effect through a dependent condition."""
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
'''
    if text.count(anchor) != 1:
        raise RuntimeError("structured exact-target insertion anchor changed")
    stage.write_text(text.replace(anchor, patch + anchor, 1), encoding="utf-8")

required_snippets = {
    "validation_scripts/stage_lineage_contract_check.py": (
        '"source", "entity", "government", "governmental", "regulatory"',
    ),
    "validation_scripts/related_lifecycle_check.py": (
        'def _simple_english_singular_candidates(token):',
        '"organization", "organisation", "authority", "agency", "institution"',
    ),
    "validation_scripts/evidence_qc_v8_check.py": (
        'row.get("draft_id") or row.get("source_spec_id")',
    ),
    "validation_scripts/date_role_freshness_check.py": (
        'row.get("draft_id") or row.get("source_spec_id")',
    ),
}
for filename, snippets in required_snippets.items():
    source = Path(filename).read_text(encoding="utf-8")
    missing = [snippet for snippet in snippets if snippet not in source]
    if missing:
        raise RuntimeError(f"{filename}: missing required review fix: {missing}")

Path("validation_scripts/tests/test_review_4866528845_contracts.py").write_text(
'''from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCRIPTS = ROOT / "validation_scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

from validation_scripts import date_role_freshness_check as date_role
from validation_scripts import evidence_qc_v8_check as evidence_qc
from validation_scripts import related_lifecycle_check as related
from validation_scripts import stage_lineage_contract_check as lineage


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
        self.assertTrue(lineage._has_bound_interpretation_effect(
            "The milestone confirmed the adoption thesis"
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
