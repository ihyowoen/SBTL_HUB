"""Regressions for PR #385 Codex review 5314410221.

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


class Review5314410221Contracts(unittest.TestCase):
    def validate(self, prior, current, quote, dimensions=("quantitative_anchor",)):
        chain = chain_for(prior, current, quote, dimensions)
        binding.validate_content_enrichment_delta(
            chain, "review 5314410221",
            operation_card=copy.deepcopy(chain["0.6"][0]),
            locked_prompt_version=V5,
        )
        return chain

    def blocked(self, *args, **kwargs):
        with self.assertRaises(binding.Blocked):
            return self.validate(*args, **kwargs)

    def standalone_findings(self, chain):
        return stage._content_enrichment_audit_findings(
            copy.deepcopy(chain["0.6"][0]), "review 5314410221"
        )

    def test_modifier_before_neither_keeps_negative_complements(self):
        prior = "Capacity is 10 MW."
        current = "Capacity is 20 MW. Alpha is profitable and sustainable."
        wrong = "Capacity is 20 MW. Alpha is currently neither profitable nor sustainable."
        chain = chain_for(prior, current, wrong)
        self.blocked(prior, current, wrong)
        self.assertTrue(self.standalone_findings(chain))
        good = self.validate(prior, current, current)
        self.assertFalse(self.standalone_findings(good))
        relations = binding._factual_predicate_subject_counter(wrong)
        self.assertGreater(relations[("alpha", "neg:be", "profitable")], 0)
        self.assertGreater(relations[("alpha", "neg:be", "sustainable")], 0)

    def test_year_first_quarters_bind_as_compound_periods(self):
        prior = "Capacity is 10 MW. Alpha was approved during 2025 Q1 and delayed during 2025 Q2."
        current = "Capacity is 20 MW. Alpha was approved during 2025 Q1 and delayed during 2025 Q2."
        wrong = "Capacity is 20 MW. Alpha was approved during 2025 Q2 and delayed during 2025 Q1."
        dims = ("quantitative_anchor", "changed_state")
        chain = chain_for(prior, current, wrong, dims)
        self.blocked(prior, current, wrong, dims)
        self.assertTrue(self.standalone_findings(chain))
        good = self.validate(prior, current, current, dims)
        self.assertFalse(self.standalone_findings(good))
        state = binding._state_subject_strength_occurrences(current)
        self.assertIn("alpha=>approval=>period:2025 q1", state)
        self.assertIn("alpha=>delay=>period:2025 q2", state)

    def test_korean_year_first_quarter_is_one_period_identity(self):
        self.assertEqual(binding._canonical_state_period("2025년 1분기"), "2025 q1")
        self.assertEqual(binding._canonical_state_period("2025년 2분기"), "2025 q2")

    def test_intro_phrase_does_not_break_preposed_condition_scope(self):
        text = (
            "Previously, if Alpha was approved and Beta started at 10 MW because demand rose; "
            "target remains subject to certification."
        )
        approval_pattern = binding.DIMENSION_CANONICAL_SIGNAL_RES["changed_state"]["approval"]
        commencement_pattern = binding.DIMENSION_CANONICAL_SIGNAL_RES["changed_state"]["commencement"]
        approval = approval_pattern.search(text)
        commencement = commencement_pattern.search(text)
        self.assertEqual(atoms.state_observation(text, approval).strength, 0)
        self.assertEqual(atoms.state_observation(text, commencement).strength, 0)
        chain = chain_for(text, text, text, DENSE)
        with self.assertRaises(binding.Blocked):
            binding.validate_content_enrichment_delta(
                chain, "review 5314410221",
                operation_card=copy.deepcopy(chain["0.6"][0]),
                locked_prompt_version=V5,
            )
        self.assertTrue(self.standalone_findings(chain))

    def test_equivalent_quarter_spellings_share_identity(self):
        self.assertEqual(binding._canonical_state_period("Q1"), "q1")
        self.assertEqual(binding._canonical_state_period("first quarter"), "q1")
        self.assertEqual(binding._canonical_state_period("1분기"), "q1")
        self.assertEqual(binding._canonical_state_period("2025 Q1"), "2025 q1")
        self.assertEqual(binding._canonical_state_period("Q1 2025"), "2025 q1")
        self.assertEqual(binding._canonical_state_period("first quarter 2025"), "2025 q1")
        self.assertEqual(binding._canonical_state_period("2025년 1분기"), "2025 q1")

        prior = "Capacity is 10 MW."
        current = "Capacity is 20 MW. Alpha was approved in Q1."
        quote = "Capacity is 20 MW. Alpha was approved in first quarter."
        dims = ("quantitative_anchor", "changed_state")
        chain = self.validate(prior, current, quote, dims)
        self.assertFalse(self.standalone_findings(chain))


if __name__ == "__main__":
    unittest.main()
