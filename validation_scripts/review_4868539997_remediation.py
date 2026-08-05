from __future__ import annotations

from pathlib import Path


def replace_exact(path: Path, old: str, new: str, label: str) -> None:
    content = path.read_text(encoding="utf-8")
    if content.count(old) != 1:
        raise SystemExit(f"{label} did not match exactly once")
    path.write_text(content.replace(old, new), encoding="utf-8")


def main() -> None:
    replace_exact(
        Path("validation_scripts/related_lifecycle_check.py"),
        '''_ASSERTION_EVENT_SUBJECT_TERMS = {
    "permit", "license", "agreement", "contract", "filing", "construction",
    "operation", "operations", "commissioning", "delivery", "shipment",
    "investment", "funding", "guidance", "forecast", "rule", "milestone",
    "허가", "인가", "계약", "공시", "건설", "운영", "가동", "상업운전",
    "납품", "출하", "투자", "금융", "전망", "규정", "이정표",
}
''',
        '''_ASSERTION_EVENT_SUBJECT_TERMS = {
    "permit", "license", "agreement", "contract", "filing", "construction",
    "operation", "operations", "commissioning", "launch", "start", "award",
    "delivery", "shipment", "investment", "funding", "guidance", "forecast",
    "rule", "milestone", "허가", "인가", "계약", "공시", "건설", "운영",
    "가동", "상업운전", "출시", "착수", "수주", "납품", "출하", "투자",
    "금융", "전망", "규정", "이정표",
}
''',
        "related event-subject block",
    )
    replace_exact(
        Path("validation_scripts/stage_lineage_contract_check.py"),
        '    r"as\\s+long\\s+as|so\\s+long\\s+as|"\n',
        '    r"conditional\\s+on|dependent\\s+on|as\\s+long\\s+as|so\\s+long\\s+as|"\n',
        "conditional boundary line",
    )

    Path("validation_scripts/tests/test_review_4868539997_contracts.py").write_text(
        '''from __future__ import annotations

import copy
import unittest

from validation_scripts import related_lifecycle_check as related
from validation_scripts import stage_lineage_contract_check as lineage
from validation_scripts.tests import test_review_4861791404_contracts as v3_contracts
from validation_scripts.tests import test_review_4862131806_contracts as related_contracts


class TestReview4868539997Contracts(unittest.TestCase):
    def base_v3_spec(self):
        return copy.deepcopy(
            v3_contracts.TestReview4861791404Contracts().base_v3_spec()
        )

    @staticmethod
    def confirmation_point(effect):
        return {
            "measurable_event_or_metric": "Project Alpha production milestone",
            "interpretation_effect": effect,
        }

    def test_conditional_on_and_dependent_on_do_not_bind_dependent_effects(self):
        for effect in (
            "Project Alpha production weakened conditional on the current demand outlook strengthened",
            "Project Alpha production weakened dependent on the current demand outlook strengthened",
        ):
            with self.subTest(effect=effect):
                self.assertFalse(lineage._has_bound_interpretation_effect(effect))
                self.assertFalse(
                    lineage._valid_confirmation_point(self.confirmation_point(effect))
                )

    def test_complete_v3_rejects_conditional_binding_bypasses(self):
        for effect in (
            "Project Alpha production weakened conditional on the current demand outlook strengthened",
            "Project Alpha production weakened dependent on the current demand outlook strengthened",
        ):
            with self.subTest(effect=effect):
                spec = self.base_v3_spec()
                spec["next_confirmation_points"] = [self.confirmation_point(effect)]
                messages = []
                self.assertFalse(
                    lineage.validate_stage_a_v3_override(
                        spec, spec["spec_id"], messages
                    )
                )

    def test_leading_conditional_phrases_preserve_real_main_effects(self):
        for effect in (
            "Conditional on Project Alpha production improving, "
            "the current demand outlook would strengthen",
            "Dependent on Project Alpha production improving, "
            "the current demand outlook would strengthen",
        ):
            with self.subTest(effect=effect):
                self.assertTrue(lineage._has_bound_interpretation_effect(effect))
                self.assertTrue(
                    lineage._valid_confirmation_point(self.confirmation_point(effect))
                )

    def test_named_nominal_execution_anchors_are_item_specific(self):
        for assertion in (
            "Project Alpha launch",
            "Project Alpha start",
            "Project Alpha award",
            "프로젝트 알파 출시",
            "프로젝트 알파 착수",
            "프로젝트 알파 수주",
        ):
            with self.subTest(assertion=assertion):
                self.assertTrue(related.item_specific_lineage_assertion(assertion))

    def test_strict_related_accepts_named_nominal_execution_anchors(self):
        fixture = related_contracts.TestReview4862131806Contracts()
        for assertion in (
            "Project Alpha launch",
            "Project Alpha start",
            "Project Alpha award",
        ):
            with self.subTest(assertion=assertion):
                fixture._assert_strict_success(assertion)

    def test_bare_execution_role_words_remain_rejected(self):
        fixture = related_contracts.TestReview4862131806Contracts()
        for assertion in ("launch", "start", "award"):
            with self.subTest(assertion=assertion):
                self.assertFalse(related.item_specific_lineage_assertion(assertion))
                fixture._assert_strict_failure(assertion)


if __name__ == "__main__":
    unittest.main()
''',
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
