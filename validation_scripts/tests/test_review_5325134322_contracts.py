"""Regression for PR #385 Codex review 5325134322.

Synthetic contract probe only; this does not certify live-source truth.
"""
import copy
import unittest

from validation_scripts import card_run_v4_binding_hardening as binding
from validation_scripts import content_claim_relations as relations
from validation_scripts import stage_artifact_contract_check as stage
from validation_scripts.tests.test_review_5265937741_contracts import chain_for

V5 = "PROMPT_0_6_V5_20260919"


class Review5325134322Contracts(unittest.TestCase):
    def validate(self, prior, current, quote, dimensions=("quantitative_anchor",)):
        chain = chain_for(prior, current, quote, dimensions)
        binding.validate_content_enrichment_delta(
            chain, "review 5325134322",
            operation_card=copy.deepcopy(chain["0.6"][0]),
            locked_prompt_version=V5,
        )
        return chain

    def blocked(self, *args, **kwargs):
        with self.assertRaises(binding.Blocked):
            return self.validate(*args, **kwargs)

    def standalone_findings(self, chain):
        return stage._content_enrichment_audit_findings(
            copy.deepcopy(chain["0.6"][0]), "review 5325134322"
        )

    def test_repeated_compound_korean_metric_multiplicity_is_preserved(self):
        prior = "용량은 10 MW이다."
        current = (
            "용량은 20 MW이다. "
            "알파 영업이익은 2025년부터 30 USD이고 "
            "영업이익은 2025년부터 30 USD이고 "
            "순이익은 2025년부터 30 USD이다."
        )
        wrong = (
            "용량은 20 MW이다. "
            "알파 영업이익은 2025년부터 30 USD이고 "
            "순이익은 2025년부터 30 USD이고 "
            "순이익은 2025년부터 30 USD이다."
        )
        self.blocked(prior, current, wrong)
        good = self.validate(prior, current, current)
        self.assertFalse(self.standalone_findings(good))

        rel = relations.metric_quantity_relations(
            current, binding._claim_subjects_for_span
        )
        earnings = [
            (key, count) for key, count in rel.items()
            if key[0] == "metric:quantity" and key[1] == "알파"
        ]
        operating = [count for key, count in earnings if key[2] == "영업이익"]
        net = [count for key, count in earnings if key[2] == "순이익"]
        self.assertEqual(operating, [2])
        self.assertEqual(net, [1])


if __name__ == "__main__":
    unittest.main()
