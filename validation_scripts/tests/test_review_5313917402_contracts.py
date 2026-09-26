"""Regressions for PR #385 Codex review 5313917402.

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


class Review5313917402Contracts(unittest.TestCase):
    def validate(self, prior, current, quote, dimensions=("quantitative_anchor",)):
        chain = chain_for(prior, current, quote, dimensions)
        binding.validate_content_enrichment_delta(
            chain, "review 5313917402",
            operation_card=copy.deepcopy(chain["0.6"][0]),
            locked_prompt_version=V5,
        )
        return chain

    def blocked(self, *args, **kwargs):
        with self.assertRaises(binding.Blocked):
            return self.validate(*args, **kwargs)

    def standalone_findings(self, chain):
        return stage._content_enrichment_audit_findings(
            copy.deepcopy(chain["0.6"][0]), "review 5313917402"
        )

    def test_copular_complements_preserve_local_negation(self):
        prior = "Capacity is 10 MW."
        current = "Capacity is 20 MW. Alpha is profitable but not sustainable."
        wrong = "Capacity is 20 MW. Alpha is not profitable but sustainable."
        chain = chain_for(prior, current, wrong)
        self.blocked(prior, current, wrong)
        self.assertTrue(self.standalone_findings(chain))
        good = self.validate(prior, current, current)
        self.assertFalse(self.standalone_findings(good))

    def test_later_subject_condition_does_not_retroactively_scope_first_state(self):
        text = (
            "Previously, Alpha was approved and Beta starts if demand rises at 10 MW "
            "because supply changed; target remains subject to certification."
        )
        approval = binding.DIMENSION_CANONICAL_SIGNAL_RES["changed_state"]["approval"].search(text)
        self.assertEqual(atoms.state_observation(text, approval).strength, 2)
        chain = self.validate(text, text, text, DENSE)
        self.assertFalse(self.standalone_findings(chain))

    def test_state_occurrences_bind_their_local_periods(self):
        prior = "Capacity is 10 MW. Alpha was approved in 2025 and delayed in 2026."
        current = "Capacity is 20 MW. Alpha was approved in 2025 and delayed in 2026."
        wrong = "Capacity is 20 MW. Alpha was approved in 2026 and delayed in 2025."
        dims = ("quantitative_anchor", "changed_state")
        chain = chain_for(prior, current, wrong, dims)
        self.blocked(prior, current, wrong, dims)
        self.assertTrue(self.standalone_findings(chain))
        good = self.validate(prior, current, current, dims)
        self.assertFalse(self.standalone_findings(good))

    def test_lower_initial_camel_case_subjects_require_grounding(self):
        prior = "Capacity is 10 MW."
        current = "Capacity is 20 MW. eBay sells hardware."
        wrong = "Capacity is 20 MW."
        chain = chain_for(prior, current, wrong)
        self.blocked(prior, current, wrong)
        self.assertTrue(self.standalone_findings(chain))
        good = self.validate(prior, current, current)
        self.assertFalse(self.standalone_findings(good))
        self.assertTrue(any(span[2] == "ebay" for span in binding._factual_identity_spans(current)))

    def test_country_prefixed_dollars_keep_currency_identity(self):
        aud = atoms.quantitative_observations("A$10 million")[0]
        cad = atoms.quantitative_observations("C$10 million")[0]
        self.assertEqual(aud.currency_code, "aud")
        self.assertEqual(cad.currency_code, "cad")
        self.assertNotEqual(aud.identity, cad.identity)
        self.assertEqual(
            atoms.quantitative_observations("A$10 million")[0].identity,
            atoms.quantitative_observations("AUD 10 million")[0].identity,
        )

        prior = "Capacity is 10 MW."
        current = "Capacity is 20 MW. Alpha raised A$10 million and C$20 million."
        wrong = "Capacity is 20 MW. Alpha raised A$20 million and C$10 million."
        chain = chain_for(prior, current, wrong)
        self.blocked(prior, current, wrong)
        self.assertTrue(self.standalone_findings(chain))
        good = self.validate(prior, current, current)
        self.assertFalse(self.standalone_findings(good))


if __name__ == "__main__":
    unittest.main()
