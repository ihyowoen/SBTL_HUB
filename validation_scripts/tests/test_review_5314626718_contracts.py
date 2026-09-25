"""Regressions for PR #385 Codex review 5314626718.

Synthetic contract probes only; these do not certify live-source truth.
"""
import copy
import unittest

from validation_scripts import card_run_v4_binding_hardening as binding
from validation_scripts import content_semantic_atoms as atoms
from validation_scripts import stage_artifact_contract_check as stage
from validation_scripts.tests.test_review_5265937741_contracts import chain_for

V5 = "PROMPT_0_6_V5_20260919"
DENSE = ("prior_state", "changed_state", "quantitative_anchor", "boundary_or_uncertainty")


class Review5314626718Contracts(unittest.TestCase):
    def validate(self, prior, current, quote, dimensions=("quantitative_anchor",)):
        chain = chain_for(prior, current, quote, dimensions)
        binding.validate_content_enrichment_delta(
            chain, "review 5314626718",
            operation_card=copy.deepcopy(chain["0.6"][0]),
            locked_prompt_version=V5,
        )
        return chain

    def blocked(self, *args, **kwargs):
        with self.assertRaises(binding.Blocked):
            return self.validate(*args, **kwargs)

    def standalone_findings(self, chain):
        return stage._content_enrichment_audit_findings(
            copy.deepcopy(chain["0.6"][0]), "review 5314626718"
        )

    def test_ordinary_first_is_not_a_global_stopword(self):
        prior = "Alpha project. Capacity is 10 MW."
        current = "Alpha project. Capacity is 20 MW. Alpha is first."
        wrong = "Alpha project. Capacity is 20 MW."
        chain = chain_for(prior, current, wrong)
        self.blocked(prior, current, wrong)
        self.assertTrue(self.standalone_findings(chain))
        good = self.validate(prior, current, current)
        self.assertFalse(self.standalone_findings(good))
        self.assertIn(("alpha", "be", "first"), binding._factual_predicate_subject_counter(current))

    def test_equivalent_quarters_align_state_quantity_and_factual_grounding(self):
        prior = "Capacity is 10 MW."
        dims = ("quantitative_anchor", "changed_state")
        pairs = (
            (
                "Capacity is 20 MW. Alpha was approved during 2025 first quarter.",
                "Capacity is 20 MW. Alpha was approved during 2025 Q1.",
            ),
            (
                "Capacity is 20 MW. Alpha was approved in first quarter.",
                "Capacity is 20 MW. Alpha was approved in Q1.",
            ),
        )
        for current, quote in pairs:
            with self.subTest(current=current, quote=quote):
                chain = self.validate(prior, current, quote, dims)
                self.assertFalse(self.standalone_findings(chain))
                self.assertEqual(
                    binding._state_subject_strength_occurrences(current),
                    binding._state_subject_strength_occurrences(quote),
                )

    def test_temporal_period_spans_filter_only_recognized_periods(self):
        period_text = "Alpha was approved during 2025 first quarter."
        spans = atoms.temporal_period_spans(period_text)
        self.assertTrue(any("2025 first quarter" in raw for _, _, raw in spans))
        self.assertNotIn("2025", atoms.quantitative_signals(period_text))
        self.assertEqual(atoms.temporal_period_spans("Alpha is first."), ())

    def test_compound_period_intro_keeps_preposed_condition_scope(self):
        texts = (
            "Previously, in 2025 Q1, if Alpha was approved and Beta started at 10 MW because demand rose; target remains subject to certification.",
            "Previously, in Q1 2025, if Alpha was approved and Beta started at 10 MW because demand rose; target remains subject to certification.",
            "Previously, in first quarter 2025, if Alpha was approved and Beta started at 10 MW because demand rose; target remains subject to certification.",
        )
        approval_pattern = binding.DIMENSION_CANONICAL_SIGNAL_RES["changed_state"]["approval"]
        commencement_pattern = binding.DIMENSION_CANONICAL_SIGNAL_RES["changed_state"]["commencement"]
        for text in texts:
            with self.subTest(text=text):
                approval = approval_pattern.search(text)
                commencement = commencement_pattern.search(text)
                self.assertEqual(atoms.state_observation(text, approval).strength, 0)
                self.assertEqual(atoms.state_observation(text, commencement).strength, 0)
                chain = chain_for(text, text, text, DENSE)
                with self.assertRaises(binding.Blocked):
                    binding.validate_content_enrichment_delta(
                        chain, "review 5314626718",
                        operation_card=copy.deepcopy(chain["0.6"][0]),
                        locked_prompt_version=V5,
                    )
                self.assertTrue(self.standalone_findings(chain))

    def test_forward_period_belongs_to_following_explicit_subject(self):
        prior = "Capacity is 10 MW. Alpha was approved and Beta was delayed."
        current = "Capacity is 20 MW. Alpha was approved and in Q1 Beta was delayed."
        quote = "Capacity is 20 MW. Alpha was approved and Beta was delayed in Q1."
        dims = ("quantitative_anchor", "changed_state")
        chain = self.validate(prior, current, quote, dims)
        self.assertFalse(self.standalone_findings(chain))
        current_states = binding._state_subject_strength_occurrences(current)
        self.assertNotIn("alpha=>approval=>period:q1", current_states)
        self.assertIn("beta=>delay=>period:q1", current_states)

    def test_subordinate_neither_does_not_negate_main_complement(self):
        prior = "Capacity is 10 MW."
        current = "Capacity is 20 MW. Alpha is not Beta."
        wrong = (
            "Capacity is 20 MW. "
            "Alpha is profitable because neither Beta nor Gamma competes."
        )
        chain = chain_for(prior, current, wrong)
        current_relations = binding._factual_predicate_subject_counter(current)
        evidence_relations = binding._factual_predicate_subject_counter(wrong)
        self.assertIn(("alpha", "neg:be", "beta"), current_relations)
        self.assertNotIn(("alpha", "neg:be", "beta"), evidence_relations)
        self.blocked(prior, current, wrong)
        self.assertTrue(self.standalone_findings(chain))
        good = self.validate(prior, current, current)
        self.assertFalse(self.standalone_findings(good))


if __name__ == "__main__":
    unittest.main()
