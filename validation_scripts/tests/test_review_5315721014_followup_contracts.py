"""Regressions for PR #385 Codex review 5315721014 follow-up.

Synthetic contract probes only; these do not certify live-source truth.
"""
import copy
import unittest

from validation_scripts import card_run_v4_binding_hardening as binding
from validation_scripts import content_claim_relations as relations
from validation_scripts import stage_artifact_contract_check as stage
from validation_scripts.tests.test_review_5265937741_contracts import chain_for

V5 = "PROMPT_0_6_V5_20260919"


class Review5315721014FollowupContracts(unittest.TestCase):
    def validate(self, prior, current, quote, dimensions=("quantitative_anchor",)):
        chain = chain_for(prior, current, quote, dimensions)
        binding.validate_content_enrichment_delta(
            chain, "review 5315721014 followup",
            operation_card=copy.deepcopy(chain["0.6"][0]),
            locked_prompt_version=V5,
        )
        return chain

    def blocked(self, *args, **kwargs):
        with self.assertRaises(binding.Blocked):
            return self.validate(*args, **kwargs)

    def standalone_findings(self, chain):
        return stage._content_enrichment_audit_findings(
            copy.deepcopy(chain["0.6"][0]), "review 5315721014 followup"
        )

    def test_preposed_period_survives_when_tail_has_later_period(self):
        prior = "Capacity is 10 MW."
        for current, wrong in (
            (
                "Capacity is 20 MW. In 2025, Alpha sold coal and gas in 2026.",
                "Capacity is 20 MW. In 2024, Alpha sold coal and gas in 2026.",
            ),
            (
                "Capacity is 20 MW. Alpha in 2025 sold coal and gas in 2026.",
                "Capacity is 20 MW. Alpha in 2024 sold coal and gas in 2026.",
            ),
        ):
            with self.subTest(current=current):
                self.blocked(prior, current, wrong)
                good = self.validate(prior, current, current)
                self.assertFalse(self.standalone_findings(good))
                rel = relations.english_factual_period_relations(current)
                self.assertIn(
                    ("relation:en:period", "alpha", "", "sold", ("coal",), "2025"),
                    rel,
                )
                self.assertTrue(any(
                    key[0] == "relation:en:period"
                    and key[1] == "alpha"
                    and key[-1] == "2026"
                    for key in rel
                ))

    def test_repeated_metric_uses_its_own_suffix_period(self):
        prior = "Capacity is 10 MW."
        current = (
            "Capacity is 20 MW. Alpha revenue was 30 USD in January "
            "and capacity was 40 MW in February."
        )
        wrong = (
            "Capacity is 20 MW. Alpha revenue was 30 USD in January "
            "and capacity was 40 MW in March."
        )
        self.blocked(prior, current, wrong)
        good = self.validate(prior, current, current)
        self.assertFalse(self.standalone_findings(good))
        metric = relations.metric_quantity_relations(current, binding._claim_subjects_for_span)
        self.assertTrue(any(
            key[0] == "metric:quantity"
            and key[2] == "capacity"
            and key[3] == "february"
            and key[4].startswith("40 ")
            for key in metric
        ))
        self.assertFalse(any(
            key[0] == "metric:quantity"
            and key[2] == "capacity"
            and key[3] == "january"
            for key in metric
        ))

    def test_leading_metric_range_keeps_complete_range_identity(self):
        prior = "Capacity is 10 MW."
        current = "Capacity is 20 MW. From March to June 2025, Alpha revenue was 30 USD."
        wrong = "Capacity is 20 MW. From April to June 2025, Alpha revenue was 30 USD."
        self.blocked(prior, current, wrong)
        good = self.validate(prior, current, current)
        self.assertFalse(self.standalone_findings(good))
        metric = relations.metric_quantity_relations(current, binding._claim_subjects_for_span)
        self.assertTrue(any(
            key[0] == "metric:quantity"
            and key[2] == "revenue"
            and key[3] == "march 2025-to-june 2025"
            for key in metric
        ))

    def test_elliptical_passive_objects_bind_local_periods(self):
        prior = "Capacity is 10 MW."
        current = (
            "Capacity is 20 MW. Some coal was sold by Alpha in 2025 "
            "and gas in 2026."
        )
        wrong = (
            "Capacity is 20 MW. Some coal was sold by Alpha in 2026 "
            "and gas in 2025."
        )
        self.blocked(prior, current, wrong)
        good = self.validate(prior, current, current)
        self.assertFalse(self.standalone_findings(good))
        rel = relations.english_factual_period_relations(current)
        self.assertIn(
            ("relation:en:passive:period", "alpha", "was", "sold", ("some", "coal"), "2025"),
            rel,
        )
        self.assertIn(
            ("relation:en:passive:period", "alpha", "was", "sold", ("gas",), "2026"),
            rel,
        )


if __name__ == "__main__":
    unittest.main()
