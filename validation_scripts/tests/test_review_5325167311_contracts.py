"""Regression for PR #385 Codex review 5325167311.

Synthetic contract probe only; this does not certify live-source truth.
"""
import copy
import unittest

from validation_scripts import card_run_v4_binding_hardening as binding
from validation_scripts import content_claim_relations as relations
from validation_scripts import stage_artifact_contract_check as stage
from validation_scripts.tests.test_review_5265937741_contracts import chain_for

V5 = "PROMPT_0_6_V5_20260919"


class Review5325167311Contracts(unittest.TestCase):
    def validate(self, prior, current, quote):
        chain = chain_for(prior, current, quote, ("quantitative_anchor",))
        binding.validate_content_enrichment_delta(
            chain, "review 5325167311",
            operation_card=copy.deepcopy(chain["0.6"][0]),
            locked_prompt_version=V5,
        )
        return chain

    def test_korean_metric_overlap_reconciles_per_source_occurrence(self):
        prior = "용량은 10 MW이다."
        current = (
            "용량은 20 MW이다. "
            "알파공장 소개, 베타 매출은 2025년부터 30 USD이다. "
            "베타 매출은 30 USD, 2025년부터이다."
        )
        wrong = (
            "용량은 20 MW이다. "
            "알파공장 소개, 베타 매출은 2025년부터 30 USD이다. "
            "감마 매출은 30 USD, 2025년부터이다."
        )
        with self.assertRaises(binding.Blocked):
            self.validate(prior, current, wrong)

        good = self.validate(prior, current, current)
        self.assertFalse(stage._content_enrichment_audit_findings(
            copy.deepcopy(good["0.6"][0]), "review 5325167311"
        ))

        rel = relations.metric_quantity_relations(
            current, binding._claim_subjects_for_span
        )
        beta = [
            count for key,count in rel.items()
            if key[0] == "metric:quantity"
            and key[1] == "베타"
            and key[2] == "매출"
            and key[3] == "2025년부터"
        ]
        self.assertEqual(beta, [2])


if __name__ == "__main__":
    unittest.main()
