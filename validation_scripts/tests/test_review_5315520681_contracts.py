"""Regressions for PR #385 Codex review 5315520681.

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
DENSE = ("prior_state", "changed_state", "quantitative_anchor", "boundary_or_uncertainty")


class Review5315520681Contracts(unittest.TestCase):
    def validate(self, prior, current, quote, dimensions=("quantitative_anchor",)):
        chain = chain_for(prior, current, quote, dimensions)
        binding.validate_content_enrichment_delta(
            chain, "review 5315520681",
            operation_card=copy.deepcopy(chain["0.6"][0]),
            locked_prompt_version=V5,
        )
        return chain

    def blocked(self, *args, **kwargs):
        with self.assertRaises(binding.Blocked):
            return self.validate(*args, **kwargs)

    def standalone_findings(self, chain):
        return stage._content_enrichment_audit_findings(
            copy.deepcopy(chain["0.6"][0]), "review 5315520681"
        )

    def test_subordinate_auxiliary_chain_keeps_lexical_predicate(self):
        prior = "Capacity is 10 MW."
        current = "Capacity is 20 MW. Alpha is profitable because Beta had collapsed."
        wrong = "Capacity is 20 MW. Alpha is profitable because Beta had expanded."
        dims = ("quantitative_anchor", "transmission_path")
        self.blocked(prior, current, wrong, dims)
        good = self.validate(prior, current, current, dims)
        self.assertFalse(self.standalone_findings(good))
        rel = relations.copular_subordinate_relations(current)
        self.assertIn(("relation:en:subordinate", "beta", "had", "collapsed", ()), rel)

    def test_coordinated_copular_complements_bind_local_periods(self):
        prior = "Capacity is 10 MW."
        current = "Capacity is 20 MW. Alpha is profitable in 2025 and sustainable in 2026."
        wrong = "Capacity is 20 MW. Alpha is profitable in 2026 and sustainable in 2025."
        self.blocked(prior, current, wrong)
        good = self.validate(prior, current, current)
        self.assertFalse(self.standalone_findings(good))
        rel = relations.english_copular_period_relations(current)
        self.assertIn(("relation:en:copular:period", "alpha", "is", ("profitable",), "2025"), rel)
        self.assertIn(("relation:en:copular:period", "alpha", "is", ("sustainable",), "2026"), rel)

    def test_coordinated_copular_subject_retains_later_period(self):
        prior = "Capacity is 10 MW."
        current = "Capacity is 20 MW. Alpha is stable and Beta is profitable in 2025."
        wrong = "Capacity is 20 MW. Alpha is stable and Beta is profitable in 2026."
        self.blocked(prior, current, wrong)
        good = self.validate(prior, current, current)
        self.assertFalse(self.standalone_findings(good))
        rel = relations.english_copular_period_relations(current)
        self.assertIn(("relation:en:copular:period", "beta", "is", ("profitable",), "2025"), rel)

    def test_coordinated_passives_bind_each_local_period(self):
        prior = "Capacity is 10 MW."
        current = (
            "Capacity is 20 MW. Coal was sold by Alpha in 2025 and "
            "gas was sold by Alpha in 2026."
        )
        wrong = (
            "Capacity is 20 MW. Coal was sold by Alpha in 2026 and "
            "gas was sold by Alpha in 2025."
        )
        self.blocked(prior, current, wrong)
        good = self.validate(prior, current, current)
        self.assertFalse(self.standalone_findings(good))
        rel = relations.english_factual_period_relations(current)
        self.assertIn(("relation:en:passive:period", "alpha", "was", "sold", ("coal",), "2025"), rel)
        self.assertIn(("relation:en:passive:period", "alpha", "was", "sold", ("gas",), "2026"), rel)

    def test_metric_context_carries_into_coordinated_period_value(self):
        prior = "Capacity is 10 MW."
        current = "Capacity is 20 MW. Alpha revenue in January was 30 USD and in February was 40 USD."
        wrong = "Capacity is 20 MW. Alpha revenue in January was 30 USD and in March was 40 USD."
        self.blocked(prior, current, wrong)
        good = self.validate(prior, current, current)
        self.assertFalse(self.standalone_findings(good))
        metric = relations.metric_quantity_relations(current, binding._claim_subjects_for_span)
        self.assertTrue(any(key[0] == "metric:quantity" and key[3] == "february"
                            and key[4].startswith("40 ") for key in metric))

    def test_preposed_period_binds_active_relation(self):
        prior = "Capacity is 10 MW."
        current = "Capacity is 20 MW. In 2025, Alpha sold coal."
        wrong = "Capacity is 20 MW. In 2026, Alpha sold coal."
        self.blocked(prior, current, wrong)
        rel = relations.english_factual_period_relations(current)
        self.assertIn(("relation:en:period", "alpha", "", "sold", ("coal",), "2025"), rel)

    def test_preposed_period_binds_passive_relation(self):
        prior = "Capacity is 10 MW."
        current = "Capacity is 20 MW. In 2025, coal was sold by Alpha."
        wrong = "Capacity is 20 MW. In 2026, coal was sold by Alpha."
        self.blocked(prior, current, wrong)
        rel = relations.english_factual_period_relations(current)
        self.assertIn(("relation:en:passive:period", "alpha", "was", "sold", ("coal",), "2025"), rel)

    def test_period_before_copula_is_bound(self):
        prior = "Capacity is 10 MW."
        current = "Capacity is 20 MW. Alpha in 2025 was profitable."
        wrong = "Capacity is 20 MW. Alpha in 2026 was profitable."
        self.blocked(prior, current, wrong)
        good = self.validate(prior, current, current)
        self.assertFalse(self.standalone_findings(good))
        rel = relations.english_copular_period_relations(current)
        self.assertIn(("relation:en:copular:period", "alpha", "was", ("profitable",), "2025"), rel)

    def test_metric_period_after_quantity_is_bound(self):
        prior = "Capacity is 10 MW."
        current = "Capacity is 20 MW. Alpha revenue was 30 USD in January."
        wrong = "Capacity is 20 MW. Alpha revenue was 30 USD in February."
        self.blocked(prior, current, wrong)
        metric = relations.metric_quantity_relations(current, binding._claim_subjects_for_span)
        self.assertTrue(any(key[0] == "metric:quantity" and key[3] == "january"
                            and key[4].startswith("30 ") for key in metric))

    def test_general_finite_action_gets_period_relation(self):
        prior = "Capacity is 10 MW."
        current = "Capacity is 20 MW. Alpha expanded in 2025."
        wrong = "Capacity is 20 MW. Alpha expanded in 2026."
        self.blocked(prior, current, wrong)
        good = self.validate(prior, current, current)
        self.assertFalse(self.standalone_findings(good))
        rel = relations.english_factual_period_relations(current)
        self.assertIn(("relation:en:period", "alpha", "", "expanded", (), "2025"), rel)

    def test_qualified_month_range_preserves_both_endpoints(self):
        current = "Capacity is 20 MW. Alpha was approved from March 2025 to June 2025."
        wrong = "Capacity is 20 MW. Alpha was approved from March 2025 to July 2025."
        prior = "Capacity is 10 MW. Alpha was approved from February 2025 to June 2025."
        dims = ("quantitative_anchor", "changed_state")
        self.assertTrue(atoms.temporal_period_spans(current))
        state = binding._state_subject_strength_occurrences(current)
        self.assertIn("alpha=>approval=>period:march 2025-to-june 2025", state)
        self.blocked(prior, current, wrong, dims)
        good = self.validate(prior, current, current, dims)
        self.assertFalse(self.standalone_findings(good))

    def test_for_period_intro_is_already_scoped_correctly(self):
        text = (
            "Previously, for 2025, if Alpha was approved and Beta started at 10 MW "
            "because demand rose; target remains subject to certification."
        )
        approval = binding.DIMENSION_CANONICAL_SIGNAL_RES["changed_state"]["approval"].search(text)
        commencement = binding.DIMENSION_CANONICAL_SIGNAL_RES["changed_state"]["commencement"].search(text)
        self.assertEqual(atoms.state_observation(text, approval).strength, 0)
        self.assertEqual(atoms.state_observation(text, commencement).strength, 0)


if __name__ == "__main__":
    unittest.main()
