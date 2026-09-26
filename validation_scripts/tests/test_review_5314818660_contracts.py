"""Regressions for PR #385 Codex review 5314818660.

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


class Review5314818660Contracts(unittest.TestCase):
    def validate(self, prior, current, quote, dimensions=("quantitative_anchor",)):
        chain = chain_for(prior, current, quote, dimensions)
        binding.validate_content_enrichment_delta(
            chain, "review 5314818660",
            operation_card=copy.deepcopy(chain["0.6"][0]),
            locked_prompt_version=V5,
        )
        return chain

    def blocked(self, *args, **kwargs):
        with self.assertRaises(binding.Blocked):
            return self.validate(*args, **kwargs)

    def standalone_findings(self, chain):
        return stage._content_enrichment_audit_findings(
            copy.deepcopy(chain["0.6"][0]), "review 5314818660"
        )

    def test_subordinate_copular_reason_retains_independent_factual_claim(self):
        prior = "Capacity is 10 MW."
        current = "Capacity is 20 MW. Alpha is profitable because Beta sells coal."
        wrong = "Capacity is 20 MW. Alpha is profitable because Beta sells gas."
        dims = ("quantitative_anchor", "transmission_path")
        chain = chain_for(prior, current, wrong, dims)
        self.blocked(prior, current, wrong, dims)
        self.assertTrue(self.standalone_findings(chain))
        good = self.validate(prior, current, current, dims)
        self.assertFalse(self.standalone_findings(good))
        current_rel = binding._factual_predicate_subject_counter(current)
        self.assertTrue(any(key[0] == "relation:en" and key[1] == "beta"
                            and key[3] == "sells" and "coal" in key[4]
                            for key in current_rel if isinstance(key, tuple)))

    def test_ordinal_quarter_metric_quantities_bind_periods(self):
        prior = "Capacity is 10 MW."
        current = (
            "Capacity is 20 MW. Alpha capacity in first quarter was 30 MW "
            "and Alpha capacity in second quarter was 40 MW."
        )
        wrong = (
            "Capacity is 20 MW. Alpha capacity in first quarter was 40 MW "
            "and Alpha capacity in second quarter was 30 MW."
        )
        self.blocked(prior, current, wrong)
        good = self.validate(prior, current, current)
        self.assertFalse(self.standalone_findings(good))
        metric = relations.metric_quantity_relations(
            current, binding._claim_subjects_for_span
        )
        self.assertTrue(any(key[0] == "metric:quantity" and key[3] == "q1"
                            and key[4].startswith("30 ") for key in metric))
        self.assertTrue(any(key[0] == "metric:quantity" and key[3] == "q2"
                            and key[4].startswith("40 ") for key in metric))

    def test_month_named_counterparties_are_not_temporal_masked(self):
        prior = "Capacity is 10 MW."
        current = "Capacity is 20 MW. Alpha buys from March Ltd."
        wrong = "Capacity is 20 MW. Alpha buys from June Ltd."
        self.assertEqual(atoms.temporal_period_spans("Alpha buys from March Ltd."), ())
        self.assertEqual(atoms.temporal_period_spans("Alpha buys from June Ltd."), ())
        self.blocked(prior, current, wrong)
        good = self.validate(prior, current, current)
        self.assertFalse(self.standalone_findings(good))

    def test_the_and_of_quarter_intro_keeps_condition_scope(self):
        texts = (
            "Previously, in the first quarter of 2025, if Alpha was approved and Beta started at 10 MW because demand rose; target remains subject to certification.",
            "Previously, in Q1 of 2025, if Alpha was approved and Beta started at 10 MW because demand rose; target remains subject to certification.",
        )
        approval_pattern = binding.DIMENSION_CANONICAL_SIGNAL_RES["changed_state"]["approval"]
        commencement_pattern = binding.DIMENSION_CANONICAL_SIGNAL_RES["changed_state"]["commencement"]
        for text in texts:
            with self.subTest(text=text):
                self.assertEqual(atoms.state_observation(text, approval_pattern.search(text)).strength, 0)
                self.assertEqual(atoms.state_observation(text, commencement_pattern.search(text)).strength, 0)
                chain = chain_for(text, text, text, DENSE)
                with self.assertRaises(binding.Blocked):
                    binding.validate_content_enrichment_delta(
                        chain, "review 5314818660",
                        operation_card=copy.deepcopy(chain["0.6"][0]),
                        locked_prompt_version=V5,
                    )

    def test_comma_before_following_period_bound_subject(self):
        prior = "Capacity is 10 MW. Alpha was approved and Beta was delayed."
        current = "Capacity is 20 MW. Alpha was approved and in Q1, Beta was delayed."
        quote = "Capacity is 20 MW. Alpha was approved and Beta was delayed in Q1."
        dims = ("quantitative_anchor", "changed_state")
        chain = self.validate(prior, current, quote, dims)
        self.assertFalse(self.standalone_findings(chain))
        states = binding._state_subject_strength_occurrences(current)
        self.assertNotIn("alpha=>approval=>period:q1", states)
        self.assertIn("beta=>delay=>period:q1", states)

    def test_ordinary_factual_relations_bind_local_years_before_masking(self):
        prior = "Capacity is 10 MW."
        current = (
            "Capacity is 20 MW. Alpha sold coal in 2025 and "
            "Alpha sold gas in 2026."
        )
        wrong = (
            "Capacity is 20 MW. Alpha sold coal in 2026 and "
            "Alpha sold gas in 2025."
        )
        self.blocked(prior, current, wrong)
        good = self.validate(prior, current, current)
        self.assertFalse(self.standalone_findings(good))
        period_rel = relations.english_factual_period_relations(current)
        self.assertTrue(any(key[-1] == "2025" and "coal" in key[-2]
                            for key in period_rel))
        self.assertTrue(any(key[-1] == "2026" and "gas" in key[-2]
                            for key in period_rel))

    def test_for_metric_year_is_temporal_and_matches_in_wording(self):
        prior = "Capacity is 10 MW."
        current = "Capacity is 20 MW. Alpha capacity for 2025 was 30 MW."
        quote = "Capacity is 20 MW. Alpha capacity in 2025 was 30 MW."
        self.assertTrue(atoms.temporal_period_spans(current))
        self.assertNotIn("2025 was", atoms.quantitative_signals(current))
        chain = self.validate(prior, current, quote)
        self.assertFalse(self.standalone_findings(chain))
        current_metric = relations.metric_quantity_relations(
            current, binding._claim_subjects_for_span
        )
        quote_metric = relations.metric_quantity_relations(
            quote, binding._claim_subjects_for_span
        )
        self.assertEqual(current_metric, quote_metric)


if __name__ == "__main__":
    unittest.main()
