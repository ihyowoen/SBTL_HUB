"""Regressions for PR #385 Codex review 5315721014.

Synthetic contract probes only; these do not certify live-source truth.
"""
import copy
import unittest

from validation_scripts import card_run_v4_binding_hardening as binding
from validation_scripts import content_claim_relations as relations
from validation_scripts import content_semantic_atoms as atoms
from validation_scripts import stage_artifact_contract_check as stage
from validation_scripts.tests.test_review_5265937741_contracts import chain_for

V5 = "PROMPT_0_6_V5_20260919"


class Review5315721014Contracts(unittest.TestCase):
    def validate(self, prior, current, quote, dimensions=("quantitative_anchor",)):
        chain = chain_for(prior, current, quote, dimensions)
        binding.validate_content_enrichment_delta(
            chain, "review 5315721014",
            operation_card=copy.deepcopy(chain["0.6"][0]),
            locked_prompt_version=V5,
        )
        return chain

    def blocked(self, *args, **kwargs):
        with self.assertRaises(binding.Blocked):
            return self.validate(*args, **kwargs)

    def standalone_findings(self, chain):
        return stage._content_enrichment_audit_findings(
            copy.deepcopy(chain["0.6"][0]), "review 5315721014"
        )

    def test_coordinated_precopula_subjects_keep_local_periods(self):
        prior = "Capacity is 10 MW."
        current = (
            "Capacity is 20 MW. Alpha in 2025 was profitable and "
            "Beta in 2026 was sustainable."
        )
        wrong = (
            "Capacity is 20 MW. Alpha in 2026 was profitable and "
            "Beta in 2025 was sustainable."
        )
        self.blocked(prior, current, wrong)
        good = self.validate(prior, current, current)
        self.assertFalse(self.standalone_findings(good))
        rel = relations.english_copular_period_relations(current)
        self.assertIn(
            ("relation:en:copular:period", "alpha", "was", ("profitable",), "2025"),
            rel,
        )
        self.assertIn(
            ("relation:en:copular:period", "beta", "was", ("sustainable",), "2026"),
            rel,
        )

    def test_intransitive_coordinated_actions_keep_first_period(self):
        prior = "Capacity is 10 MW."
        current = "Capacity is 20 MW. Alpha expanded in 2025 and contracted in 2026."
        wrong = "Capacity is 20 MW. Alpha expanded in 2024 and contracted in 2026."
        self.blocked(prior, current, wrong)
        good = self.validate(prior, current, current)
        self.assertFalse(self.standalone_findings(good))
        rel = relations.english_factual_period_relations(current)
        self.assertIn(("relation:en:period", "alpha", "", "expanded", (), "2025"), rel)
        self.assertIn(("relation:en:period", "alpha", "", "contracted", (), "2026"), rel)

    def test_period_between_active_subject_and_verb_is_bound(self):
        prior = "Capacity is 10 MW."
        current = "Capacity is 20 MW. Alpha in 2025 sold coal."
        wrong = "Capacity is 20 MW. Alpha in 2026 sold coal."
        self.blocked(prior, current, wrong)
        rel = relations.english_factual_period_relations(current)
        self.assertIn(("relation:en:period", "alpha", "", "sold", ("coal",), "2025"), rel)

    def test_lone_month_range_year_propagates_to_both_endpoints(self):
        a = atoms.canonical_temporal_period("March to June 2025")
        b = atoms.canonical_temporal_period("March 2025 to June 2025")
        self.assertEqual(a, "march 2025-to-june 2025")
        self.assertEqual(a, b)

        prior = "Capacity is 10 MW. Alpha was approved from February to June 2025."
        current = "Capacity is 20 MW. Alpha was approved from March to June 2025."
        quote = "Capacity is 20 MW. Alpha was approved from March 2025 to June 2025."
        dims = ("quantitative_anchor", "changed_state")
        chain = self.validate(prior, current, quote, dims)
        self.assertFalse(self.standalone_findings(chain))

    def test_metric_context_carries_into_post_quantity_period(self):
        prior = "Capacity is 10 MW."
        current = (
            "Capacity is 20 MW. Alpha revenue was 30 USD in January "
            "and 40 USD in February."
        )
        wrong = (
            "Capacity is 20 MW. Alpha revenue was 30 USD in January "
            "and 40 USD in March."
        )
        self.blocked(prior, current, wrong)
        metric = relations.metric_quantity_relations(current, binding._claim_subjects_for_span)
        self.assertTrue(any(
            key[0] == "metric:quantity" and key[3] == "february"
            and key[4].startswith("40 ")
            for key in metric
        ))

    def test_metric_name_accepts_month_range(self):
        prior = "Capacity is 10 MW."
        current = "Capacity is 20 MW. Alpha revenue from March to June 2025 was 30 USD."
        wrong = "Capacity is 20 MW. Alpha revenue from April to June 2025 was 30 USD."
        self.blocked(prior, current, wrong)
        good = self.validate(prior, current, current)
        self.assertFalse(self.standalone_findings(good))
        metric = relations.metric_quantity_relations(current, binding._claim_subjects_for_span)
        self.assertTrue(any(
            key[0] == "metric:quantity"
            and key[3] == "march 2025-to-june 2025"
            and key[4].startswith("30 ")
            for key in metric
        ))

    def test_contracted_subordinate_auxiliaries_are_normalized(self):
        prior = "Capacity is 10 MW."
        dims = ("quantitative_anchor", "transmission_path")
        for current, wrong, expected_aux, expected_verb in (
            (
                "Capacity is 20 MW. Alpha is profitable because Beta hadn't collapsed.",
                "Capacity is 20 MW. Alpha is profitable because Beta hadn't expanded.",
                "had not",
                "collapsed",
            ),
            (
                "Capacity is 20 MW. Alpha is profitable because Beta didn't collapse.",
                "Capacity is 20 MW. Alpha is profitable because Beta didn't expand.",
                "did not",
                "collapse",
            ),
            (
                "Capacity is 20 MW. Alpha is profitable because Beta wouldn't collapse.",
                "Capacity is 20 MW. Alpha is profitable because Beta wouldn't expand.",
                "would not",
                "collapse",
            ),
        ):
            with self.subTest(current=current):
                self.blocked(prior, current, wrong, dims)
                good = self.validate(prior, current, current, dims)
                self.assertFalse(self.standalone_findings(good))
                rel = relations.copular_subordinate_relations(current)
                self.assertTrue(any(
                    key[0] == "relation:en:subordinate"
                    and key[1] == "beta"
                    and key[2] == expected_aux
                    and key[3] == expected_verb
                    for key in rel
                ))


if __name__ == "__main__":
    unittest.main()
