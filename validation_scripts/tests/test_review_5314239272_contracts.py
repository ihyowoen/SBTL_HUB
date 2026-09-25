"""Regressions for PR #385 Codex review 5314239272.

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


class Review5314239272Contracts(unittest.TestCase):
    def validate(self, prior, current, quote, dimensions=("quantitative_anchor",)):
        chain = chain_for(prior, current, quote, dimensions)
        binding.validate_content_enrichment_delta(
            chain, "review 5314239272",
            operation_card=copy.deepcopy(chain["0.6"][0]),
            locked_prompt_version=V5,
        )
        return chain

    def blocked(self, *args, **kwargs):
        with self.assertRaises(binding.Blocked):
            return self.validate(*args, **kwargs)

    def standalone_findings(self, chain):
        return stage._content_enrichment_audit_findings(
            copy.deepcopy(chain["0.6"][0]), "review 5314239272"
        )

    def test_neither_nor_copular_complements_are_negative(self):
        prior = "Capacity is 10 MW."
        current = "Capacity is 20 MW. Alpha is profitable and sustainable."
        wrong = "Capacity is 20 MW. Alpha is neither profitable nor sustainable."
        chain = chain_for(prior, current, wrong)
        self.blocked(prior, current, wrong)
        self.assertTrue(self.standalone_findings(chain))
        good = self.validate(prior, current, current)
        self.assertFalse(self.standalone_findings(good))
        relations = binding._factual_predicate_subject_counter(wrong)
        self.assertGreater(relations[("alpha", "neg:be", "profitable")], 0)
        self.assertGreater(relations[("alpha", "neg:be", "sustainable")], 0)

    def test_named_months_bind_to_state_occurrences(self):
        prior = "Capacity is 10 MW. Alpha was approved in January and delayed in February."
        current = "Capacity is 20 MW. Alpha was approved in January and delayed in February."
        wrong = "Capacity is 20 MW. Alpha was approved in February and delayed in January."
        dims = ("quantitative_anchor", "changed_state")
        chain = chain_for(prior, current, wrong, dims)
        self.blocked(prior, current, wrong, dims)
        self.assertTrue(self.standalone_findings(chain))
        good = self.validate(prior, current, current, dims)
        self.assertFalse(self.standalone_findings(good))

    def test_quarters_are_period_bound_too(self):
        first = binding._state_subject_strength_occurrences(
            "Alpha was approved in Q1 and delayed in Q2."
        )
        swapped = binding._state_subject_strength_occurrences(
            "Alpha was approved in Q2 and delayed in Q1."
        )
        self.assertNotEqual(first, swapped)
        self.assertIn("alpha=>approval=>period:q1", first)
        self.assertIn("alpha=>delay=>period:q2", first)

    def test_lower_initial_camel_case_can_capitalize_anywhere_later(self):
        prior = "Capacity is 10 MW."
        for name in ("eBay", "macOS", "openAI", "youtubeMusic"):
            with self.subTest(name=name):
                current = f"Capacity is 20 MW. {name} sells hardware."
                wrong = "Capacity is 20 MW."
                chain = chain_for(prior, current, wrong)
                self.blocked(prior, current, wrong)
                self.assertTrue(self.standalone_findings(chain))
                good = self.validate(prior, current, current)
                self.assertFalse(self.standalone_findings(good))
                self.assertTrue(
                    any(span[2] == name.casefold() for span in binding._factual_identity_spans(current))
                )

    def test_earlier_postposed_condition_does_not_scope_later_subject(self):
        text = (
            "Previously at 10 MW; Alpha was approved if demand rises, and Beta started; "
            "target remains subject to certification."
        )
        approval_pattern = binding.DIMENSION_CANONICAL_SIGNAL_RES["changed_state"]["approval"]
        commencement_pattern = binding.DIMENSION_CANONICAL_SIGNAL_RES["changed_state"]["commencement"]
        approval = approval_pattern.search(text)
        commencement = commencement_pattern.search(text)
        self.assertEqual(atoms.state_observation(text, approval).strength, 0)
        self.assertEqual(atoms.state_observation(text, commencement).strength, 2)
        chain = self.validate(text, text, text, DENSE)
        self.assertFalse(self.standalone_findings(chain))

    def test_preposed_condition_still_scopes_coordinated_subjects(self):
        text = "If Alpha was approved and Beta was approved, demand rises."
        pattern = binding.DIMENSION_CANONICAL_SIGNAL_RES["changed_state"]["approval"]
        self.assertEqual(
            [atoms.state_observation(text, match).strength for match in pattern.finditer(text)],
            [0, 0],
        )

    def test_spaced_country_prefixed_dollars_keep_currency_identity(self):
        for text, code in (("A$ 10 million", "aud"), ("C$ 10 million", "cad")):
            with self.subTest(text=text):
                observed = atoms.quantitative_observations(text)[0]
                self.assertEqual(observed.currency_code, code)
        self.assertEqual(
            atoms.quantitative_observations("A$ 10 million")[0].identity,
            atoms.quantitative_observations("A$10 million")[0].identity,
        )
        self.assertEqual(
            atoms.quantitative_observations("C$ 10 million")[0].identity,
            atoms.quantitative_observations("CAD 10 million")[0].identity,
        )

        prior = "Capacity is 10 MW."
        current = "Capacity is 20 MW. Alpha raised A$ 10 million and C$ 20 million."
        wrong = "Capacity is 20 MW. Alpha raised A$ 20 million and C$ 10 million."
        chain = chain_for(prior, current, wrong)
        self.blocked(prior, current, wrong)
        self.assertTrue(self.standalone_findings(chain))
        good = self.validate(prior, current, current)
        self.assertFalse(self.standalone_findings(good))


if __name__ == "__main__":
    unittest.main()
