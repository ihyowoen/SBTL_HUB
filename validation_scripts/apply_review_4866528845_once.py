from __future__ import annotations

from pathlib import Path


def replace_once(path: str, old: str, new: str) -> None:
    target = Path(path)
    text = target.read_text(encoding="utf-8")
    count = text.count(old)
    if count != 1:
        raise RuntimeError(f"{path}: expected one replacement target, found {count}")
    target.write_text(text.replace(old, new, 1), encoding="utf-8")


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

TEST = '''from __future__ import annotations

import copy
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
from validation_scripts.tests import test_review_4861791404_contracts as prior_contracts


class TestReview4866528845ExactTargetContracts(unittest.TestCase):
    def base_v3_spec(self):
        return copy.deepcopy(
            prior_contracts.TestReview4861791404Contracts().base_v3_spec()
        )

    def test_generic_source_entity_and_government_targets_are_neutral(self):
        for value in (
            "source revenue",
            "entity margin",
            "government revenue",
            "sources' revenue",
            "entities margins",
            "governments' revenue",
            "authorities revenue",
            "agencies margin",
        ):
            with self.subTest(value=value):
                self.assertFalse(lineage._structured_exact_target(value))

    def test_named_or_dated_targets_remain_valid(self):
        for value in (
            "Project Alpha revenue",
            "Plant A inventory",
            "2027 government revenue",
            "Q2 agency margin",
        ):
            with self.subTest(value=value):
                self.assertTrue(lineage._structured_exact_target(value))

    def test_complete_v3_rejects_generic_target_bypass(self):
        spec = self.base_v3_spec()
        spec["evidence_needed_for_stage_b"] = [{
            "source_or_document_class": "official filing",
            "exact_claim_or_metric": "source revenue",
        }]
        spec["next_confirmation_points"] = [{
            "measurable_event_or_metric": "government revenue",
            "interpretation_effect": "would weaken the demand outlook",
        }]
        messages = []
        self.assertFalse(
            lineage.validate_stage_a_v3_override(spec, spec["spec_id"], messages)
        )
        self.assertTrue(
            any("exact claim, metric, stage, or date" in message for message in messages),
            messages,
        )
        self.assertTrue(
            any("measurable events or metrics" in message for message in messages),
            messages,
        )


class TestReview4866528845RelatedNeutralContracts(unittest.TestCase):
    @staticmethod
    def strict_follow_up(assertion: str):
        parent = {"id": "PARENT", "date": "2026-04-01", "related": []}
        child = {
            "id": "CHILD",
            "date": "2026-07-01",
            "related": ["PARENT"],
            "publish_ready": True,
            "related_lineage": {
                "status": "PASS",
                "relation_type": "distinct_follow_up",
                "related_ids": ["PARENT"],
                "reason": "The verified update materially changes the predecessor assessment.",
                "same_event_checked": True,
                "earliest_same_event_date_checked": True,
                "fresh_follow_up_anchor_class": "data_financial_anchor",
                "fresh_follow_up_anchor": assertion,
                "incremental_fact_vs_predecessor": assertion,
                "changed_judgment_vs_predecessor": assertion,
            },
        }
        return child, {"PARENT": parent, "CHILD": child}

    def test_plural_and_possessive_neutral_subjects_fail_strict_contract(self):
        for assertion in (
            "governments' Q2 revenue",
            "officials Q2 revenue",
            "organizations Q2 revenue",
            "authorities' Q2 revenue",
            "agencies Q2 margin",
        ):
            with self.subTest(assertion=assertion):
                self.assertFalse(related.item_specific_lineage_assertion(assertion))
                child, by_id = self.strict_follow_up(assertion)
                errors, warnings = related.check_card(
                    child, by_id, require_contract=True
                )
                self.assertEqual([], warnings)
                self.assertEqual(
                    3,
                    sum("item-specific" in message for message in errors),
                    errors,
                )

    def test_actual_named_and_lettered_subjects_remain_valid(self):
        for assertion in (
            "Project Alpha Q2 revenue",
            "Plant A Q2 inventory",
            "Facility B Q2 safety data",
        ):
            with self.subTest(assertion=assertion):
                self.assertTrue(related.item_specific_lineage_assertion(assertion))


class TestReview4866528845CsvScopeContracts(unittest.TestCase):
    LOADERS = (evidence_qc.load_ids, date_role.load_ids)

    def test_provisional_csv_columns_are_loaded(self):
        for header, value in (
            ("draft_id", "DRAFT_1"),
            ("source_spec_id", "SPEC_1"),
        ):
            with self.subTest(header=header):
                with tempfile.TemporaryDirectory() as directory:
                    path = Path(directory) / "ids.csv"
                    path.write_text(f"{header}\\n{value}\\n", encoding="utf-8")
                    for loader in self.LOADERS:
                        self.assertEqual({value}, loader(str(path)))

    def test_existing_csv_id_columns_remain_supported(self):
        for header in ("assigned_id", "id", "card_id"):
            with self.subTest(header=header):
                with tempfile.TemporaryDirectory() as directory:
                    path = Path(directory) / "ids.csv"
                    path.write_text(f"{header}\\nCARD_1\\n", encoding="utf-8")
                    for loader in self.LOADERS:
                        self.assertEqual({"CARD_1"}, loader(str(path)))


if __name__ == "__main__":
    unittest.main()
'''
Path("validation_scripts/tests/test_review_4866528845_contracts.py").write_text(
    TEST,
    encoding="utf-8",
)
