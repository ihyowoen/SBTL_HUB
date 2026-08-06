from __future__ import annotations

import copy
import unittest

from validation_scripts import stage_lineage_contract_check as lineage
from validation_scripts.tests import test_review_4861676549_contracts as prior_contracts


class TestReview4872596204Contracts(unittest.TestCase):
    def base_v3_spec(self):
        return copy.deepcopy(
            prior_contracts.TestReview4861676549Contracts().base_v3_spec()
        )

    @staticmethod
    def evidence_pairs():
        canonical = {
            "source_or_document_class": "official filing",
            "exact_claim_or_metric": "Project Alpha revenue increased 10 percent",
        }
        compatibility = {
            "source_class": "official filing",
            "verification_target": "Project Alpha revenue increased 10 percent",
        }
        return canonical, compatibility

    @staticmethod
    def confirmation_pairs():
        canonical = {
            "measurable_event_or_metric": "Project Alpha revenue increased 10 percent",
            "interpretation_effect": "would strengthen the demand outlook",
        }
        compatibility = {
            "confirmation_event": "Project Alpha revenue increased 10 percent",
            "confirm_weaken_invalidate": "would strengthen the demand outlook",
        }
        return canonical, compatibility

    def test_evidence_requires_exactly_one_complete_alias_pair(self):
        canonical, compatibility = self.evidence_pairs()
        self.assertTrue(lineage._valid_evidence_target(canonical))
        self.assertTrue(lineage._valid_evidence_target(compatibility))
        self.assertFalse(lineage._valid_evidence_target({
            "source_or_document_class": canonical["source_or_document_class"],
            "verification_target": compatibility["verification_target"],
        }))
        self.assertFalse(lineage._valid_evidence_target({
            "source_class": compatibility["source_class"],
            "exact_claim_or_metric": canonical["exact_claim_or_metric"],
        }))
        self.assertFalse(
            lineage._valid_evidence_target({**canonical, **compatibility})
        )

    def test_confirmation_requires_exactly_one_complete_alias_pair(self):
        canonical, compatibility = self.confirmation_pairs()
        self.assertTrue(lineage._valid_confirmation_point(canonical))
        self.assertTrue(lineage._valid_confirmation_point(compatibility))
        self.assertFalse(lineage._valid_confirmation_point({
            "measurable_event_or_metric": canonical["measurable_event_or_metric"],
            "confirm_weaken_invalidate": compatibility[
                "confirm_weaken_invalidate"
            ],
        }))
        self.assertFalse(lineage._valid_confirmation_point({
            "confirmation_event": compatibility["confirmation_event"],
            "interpretation_effect": canonical["interpretation_effect"],
        }))
        self.assertFalse(
            lineage._valid_confirmation_point({**canonical, **compatibility})
        )

    def test_complete_v3_override_rejects_mixed_and_dual_pairs(self):
        canonical_evidence, compatibility_evidence = self.evidence_pairs()
        canonical_confirmation, compatibility_confirmation = (
            self.confirmation_pairs()
        )
        invalid_cases = (
            (
                "evidence_needed_for_stage_b",
                {
                    "source_or_document_class": canonical_evidence[
                        "source_or_document_class"
                    ],
                    "verification_target": compatibility_evidence[
                        "verification_target"
                    ],
                },
            ),
            (
                "evidence_needed_for_stage_b",
                {**canonical_evidence, **compatibility_evidence},
            ),
            (
                "next_confirmation_points",
                {
                    "measurable_event_or_metric": canonical_confirmation[
                        "measurable_event_or_metric"
                    ],
                    "confirm_weaken_invalidate": compatibility_confirmation[
                        "confirm_weaken_invalidate"
                    ],
                },
            ),
            (
                "next_confirmation_points",
                {**canonical_confirmation, **compatibility_confirmation},
            ),
        )
        for field, value in invalid_cases:
            with self.subTest(field=field, value=value):
                spec = self.base_v3_spec()
                spec[field] = [value]
                messages = []
                self.assertFalse(
                    lineage.validate_stage_a_v3_override(
                        spec, spec["spec_id"], messages
                    ),
                    messages,
                )

    def test_complete_v3_override_accepts_each_single_alias_pair(self):
        canonical_evidence, compatibility_evidence = self.evidence_pairs()
        canonical_confirmation, compatibility_confirmation = (
            self.confirmation_pairs()
        )
        for evidence, confirmation in (
            (canonical_evidence, canonical_confirmation),
            (compatibility_evidence, compatibility_confirmation),
        ):
            with self.subTest(evidence=evidence, confirmation=confirmation):
                spec = self.base_v3_spec()
                spec["evidence_needed_for_stage_b"] = [evidence]
                spec["next_confirmation_points"] = [confirmation]
                messages = []
                self.assertTrue(
                    lineage.validate_stage_a_v3_override(
                        spec, spec["spec_id"], messages
                    ),
                    messages,
                )


if __name__ == "__main__":
    unittest.main()
