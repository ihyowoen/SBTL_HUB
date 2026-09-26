"""Regressions for PR #385 Codex review 5315392951.

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


class Review5315392951Contracts(unittest.TestCase):
    def validate(self, prior, current, quote, dimensions=("quantitative_anchor",)):
        chain = chain_for(prior, current, quote, dimensions)
        binding.validate_content_enrichment_delta(
            chain, "review 5315392951",
            operation_card=copy.deepcopy(chain["0.6"][0]),
            locked_prompt_version=V5,
        )
        return chain

    def blocked(self, *args, **kwargs):
        with self.assertRaises(binding.Blocked):
            return self.validate(*args, **kwargs)

    def standalone_findings(self, chain):
        return stage._content_enrichment_audit_findings(
            copy.deepcopy(chain["0.6"][0]), "review 5315392951"
        )

    def test_subordinate_reason_parses_general_finite_verbs(self):
        prior = "Capacity is 10 MW."
        current = "Capacity is 20 MW. Alpha is profitable because Beta collapsed."
        wrong = "Capacity is 20 MW. Alpha is profitable because Beta expanded."
        dims = ("quantitative_anchor", "transmission_path")
        chain = chain_for(prior, current, wrong, dims)
        self.blocked(prior, current, wrong, dims)
        self.assertTrue(self.standalone_findings(chain))
        good = self.validate(prior, current, current, dims)
        self.assertFalse(self.standalone_findings(good))
        rel = binding._factual_predicate_subject_counter(current)
        self.assertIn(("relation:en:subordinate", "beta", "collapsed", ()), rel)

    def test_coordinated_objects_bind_each_local_period(self):
        prior = "Capacity is 10 MW."
        current = "Capacity is 20 MW. Alpha sold coal in 2025 and gas in 2026."
        wrong = "Capacity is 20 MW. Alpha sold coal in 2026 and gas in 2025."
        self.blocked(prior, current, wrong)
        good = self.validate(prior, current, current)
        self.assertFalse(self.standalone_findings(good))
        rel = relations.english_factual_period_relations(current)
        self.assertIn(("relation:en:period", "alpha", "", "sold", ("coal",), "2025"), rel)
        self.assertIn(("relation:en:period", "alpha", "", "sold", ("gas",), "2026"), rel)

    def test_metric_named_months_are_period_bound(self):
        prior = "Capacity is 10 MW."
        current = (
            "Capacity is 20 MW. Alpha revenue in January was 30 USD and "
            "Alpha revenue in February was 40 USD."
        )
        wrong = (
            "Capacity is 20 MW. Alpha revenue in January was 40 USD and "
            "Alpha revenue in February was 30 USD."
        )
        self.blocked(prior, current, wrong)
        good = self.validate(prior, current, current)
        self.assertFalse(self.standalone_findings(good))
        metric = relations.metric_quantity_relations(current, binding._claim_subjects_for_span)
        self.assertTrue(any(key[0] == "metric:quantity" and key[3] == "january"
                            and key[4].startswith("30 ") for key in metric))
        self.assertTrue(any(key[0] == "metric:quantity" and key[3] == "february"
                            and key[4].startswith("40 ") for key in metric))

    def test_bare_month_ranges_after_from_are_temporal(self):
        prior = "Capacity is 10 MW. Alpha was approved from February to June."
        current = "Capacity is 20 MW. Alpha was approved from March to June."
        wrong = "Capacity is 20 MW. Alpha was approved from April to June."
        dims = ("quantitative_anchor", "changed_state")
        self.assertTrue(atoms.temporal_period_spans(current))
        states = binding._state_subject_strength_occurrences(current)
        self.assertIn("alpha=>approval=>period:march-to-june", states)
        self.blocked(prior, current, wrong, dims)
        good = self.validate(prior, current, current, dims)
        self.assertFalse(self.standalone_findings(good))

    def test_pronoun_dated_action_resolves_immediate_topic(self):
        prior = "Capacity is 10 MW. Alpha project. It sold coal in 2024."
        current = "Capacity is 20 MW. Alpha project. It sold coal in 2025."
        wrong = "Capacity is 20 MW. Alpha project. It sold coal in 2026."
        self.blocked(prior, current, wrong)
        good = self.validate(prior, current, current)
        self.assertFalse(self.standalone_findings(good))
        rel = relations.english_factual_period_relations(current)
        self.assertIn(("relation:en:period", "alpha", "", "sold", ("coal",), "2025"), rel)

    def test_copular_claims_preserve_local_periods(self):
        prior = "Capacity is 10 MW. Alpha is profitable in 2024."
        for current, wrong, period in (
            (
                "Capacity is 20 MW. Alpha is profitable in 2025.",
                "Capacity is 20 MW. Alpha is profitable in 2026.",
                "2025",
            ),
            (
                "Capacity is 20 MW. Alpha is profitable since 2025.",
                "Capacity is 20 MW. Alpha is profitable since 2026.",
                "since:2025",
            ),
        ):
            with self.subTest(current=current):
                self.blocked(prior, current, wrong)
                good = self.validate(prior, current, current)
                self.assertFalse(self.standalone_findings(good))
                rel = relations.english_copular_period_relations(current)
                self.assertTrue(any(key[-1] == period and "profitable" in key[-2]
                                    for key in rel))

    def test_for_period_in_preposed_condition_intro(self):
        text = (
            "Previously, for 2025, if Alpha was approved and Beta started at 10 MW "
            "because demand rose; target remains subject to certification."
        )
        approval_pattern = binding.DIMENSION_CANONICAL_SIGNAL_RES["changed_state"]["approval"]
        commencement_pattern = binding.DIMENSION_CANONICAL_SIGNAL_RES["changed_state"]["commencement"]
        self.assertEqual(atoms.state_observation(text, approval_pattern.search(text)).strength, 0)
        self.assertEqual(atoms.state_observation(text, commencement_pattern.search(text)).strength, 0)
        chain = chain_for(text, text, text, DENSE)
        with self.assertRaises(binding.Blocked):
            binding.validate_content_enrichment_delta(
                chain, "review 5315392951",
                operation_card=copy.deepcopy(chain["0.6"][0]),
                locked_prompt_version=V5,
            )
        self.assertTrue(self.standalone_findings(chain))

    def test_passive_factual_relations_bind_periods(self):
        prior = "Capacity is 10 MW. Coal was sold by Alpha in 2024."
        current = "Capacity is 20 MW. Coal was sold by Alpha in 2025."
        wrong = "Capacity is 20 MW. Coal was sold by Alpha in 2026."
        self.blocked(prior, current, wrong)
        good = self.validate(prior, current, current)
        self.assertFalse(self.standalone_findings(good))
        rel = relations.english_factual_period_relations(current)
        self.assertIn(
            ("relation:en:passive:period", "alpha", "was", "sold", ("coal",), "2025"),
            rel,
        )


if __name__ == "__main__":
    unittest.main()
