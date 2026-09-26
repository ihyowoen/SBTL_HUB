"""Regressions for PR #385 Codex review 5325104238.

Synthetic contract probes only; these do not certify live-source truth.
"""
import copy
import unittest

from validation_scripts import card_run_v4_binding_hardening as binding
from validation_scripts import content_claim_relations as relations
from validation_scripts import stage_artifact_contract_check as stage
from validation_scripts.tests.test_review_5265937741_contracts import chain_for

V5 = "PROMPT_0_6_V5_20260919"


class Review5325104238Contracts(unittest.TestCase):
    def validate(self, prior, current, quote, dimensions=("quantitative_anchor",)):
        chain = chain_for(prior, current, quote, dimensions)
        binding.validate_content_enrichment_delta(
            chain, "review 5325104238",
            operation_card=copy.deepcopy(chain["0.6"][0]),
            locked_prompt_version=V5,
        )
        return chain

    def blocked(self, *args, **kwargs):
        with self.assertRaises(binding.Blocked):
            return self.validate(*args, **kwargs)

    def standalone_findings(self, chain):
        return stage._content_enrichment_audit_findings(
            copy.deepcopy(chain["0.6"][0]), "review 5325104238"
        )

    def test_preposed_and_postposed_single_copular_period_are_equivalent(self):
        prior = "Capacity is 10 MW."
        current = "Capacity is 20 MW. Alpha was in 2025 profitable."
        quote = "Capacity is 20 MW. Alpha was profitable in 2025."
        good = self.validate(prior, current, quote)
        self.assertFalse(self.standalone_findings(good))
        current_rel = relations.english_copular_period_relations(current)
        quote_rel = relations.english_copular_period_relations(quote)
        self.assertEqual(current_rel, quote_rel)
        key = ("relation:en:copular:period", "alpha", "was", ("profitable",), "2025")
        self.assertEqual(current_rel[key], 1)

    def test_korean_metric_subject_is_local_per_match(self):
        prior = "용량은 10 MW이다."
        current = (
            "용량은 20 MW이다. "
            "알파 매출은 2025년부터 30 USD, 베타 이익은 2026년부터 40 USD이다."
        )
        quote = (
            "용량은 20 MW이다. "
            "알파 매출은 2025년부터 30 USD. "
            "베타 이익은 2026년부터 40 USD이다."
        )
        good = self.validate(prior, current, quote)
        self.assertFalse(self.standalone_findings(good))
        rel = relations.metric_quantity_relations(current, binding._claim_subjects_for_span)
        self.assertTrue(any(
            key[0] == "metric:quantity" and key[1] == "알파"
            and key[2] == "매출" and key[3] == "2025년부터"
            for key in rel
        ))
        self.assertTrue(any(
            key[0] == "metric:quantity" and key[1] == "베타"
            and key[2] == "이익" and key[3] == "2026년부터"
            for key in rel
        ))
        self.assertFalse(any(
            key[0] == "metric:quantity" and key[1] == "알파" and key[2] == "이익"
            for key in rel
        ))

    def test_compound_korean_metric_names_keep_distinct_identity(self):
        prior = "용량은 10 MW이다."
        current = (
            "용량은 20 MW이다. "
            "알파 영업이익은 2025년부터 30 USD이고 순이익은 2026년부터 40 USD이다."
        )
        wrong = (
            "용량은 20 MW이다. "
            "알파 영업이익은 2026년부터 40 USD이고 순이익은 2025년부터 30 USD이다."
        )
        self.blocked(prior, current, wrong)
        good = self.validate(prior, current, current)
        self.assertFalse(self.standalone_findings(good))
        rel = relations.metric_quantity_relations(current, binding._claim_subjects_for_span)
        self.assertTrue(any(key[0] == "metric:quantity" and key[2] == "영업이익" and key[3] == "2025년부터" for key in rel))
        self.assertTrue(any(key[0] == "metric:quantity" and key[2] == "순이익" and key[3] == "2026년부터" for key in rel))

    def test_negative_contrastive_korean_descriptions_keep_local_periods(self):
        prior = "용량은 10 MW이다."
        current = (
            "용량은 20 MW이다. "
            "알파는 2024년에 수익성이 높지 않았지만 "
            "2025년에 안정성이 낮지 않았지만 2026년에 효율성이 높았다."
        )
        wrong = (
            "용량은 20 MW이다. "
            "알파는 2025년에 수익성이 높지 않았지만 "
            "2024년에 안정성이 낮지 않았지만 2026년에 효율성이 높았다."
        )
        self.blocked(prior, current, wrong)
        good = self.validate(prior, current, current)
        self.assertFalse(self.standalone_findings(good))
        rel = relations.korean_period_relations(current)
        self.assertTrue(any(
            key[0] == "description:kr:period" and key[2] == "수익성"
            and key[4] == "neg:높" and key[-1] == "2024년"
            for key in rel
        ))
        self.assertTrue(any(
            key[0] == "description:kr:period" and key[2] == "안정성"
            and key[4] == "neg:낮" and key[-1] == "2025년"
            for key in rel
        ))


if __name__ == "__main__":
    unittest.main()
