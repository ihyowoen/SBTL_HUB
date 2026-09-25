"""Regressions for PR #385 Codex review 5316785571.

Synthetic contract probes only; these do not certify live-source truth.
"""
import copy
import unittest

from validation_scripts import card_run_v4_binding_hardening as binding
from validation_scripts import content_claim_relations as relations
from validation_scripts import stage_artifact_contract_check as stage
from validation_scripts.tests.test_review_5265937741_contracts import chain_for

V5 = "PROMPT_0_6_V5_20260919"


class Review5316785571Contracts(unittest.TestCase):
    def validate(self, prior, current, quote, dimensions=("quantitative_anchor",)):
        chain = chain_for(prior, current, quote, dimensions)
        binding.validate_content_enrichment_delta(
            chain, "review 5316785571",
            operation_card=copy.deepcopy(chain["0.6"][0]),
            locked_prompt_version=V5,
        )
        return chain

    def blocked(self, *args, **kwargs):
        with self.assertRaises(binding.Blocked):
            return self.validate(*args, **kwargs)

    def standalone_findings(self, chain):
        return stage._content_enrichment_audit_findings(
            copy.deepcopy(chain["0.6"][0]), "review 5316785571"
        )

    def test_masked_passive_periods_keep_local_objects(self):
        prior = "Capacity is 10 MW."
        current = (
            "Capacity is 20 MW. Some coal was sold in 2025 by Alpha "
            "and gas in 2026."
        )
        wrong = (
            "Capacity is 20 MW. Some coal was sold in 2026 by Alpha "
            "and gas in 2025."
        )
        self.blocked(prior, current, wrong)
        good = self.validate(prior, current, current)
        self.assertFalse(self.standalone_findings(good))
        rel = relations.english_factual_period_relations(current)
        self.assertIn(
            ("relation:en:passive:period", "alpha", "was", "sold", ("some", "coal"), "2025"),
            rel,
        )
        self.assertIn(
            ("relation:en:passive:period", "alpha", "was", "sold", ("gas",), "2026"),
            rel,
        )

    def test_korean_period_before_object_particle_is_bound(self):
        prior = "용량은 10 MW이다."
        current = "용량은 20 MW이다. 알파는 2025년에 석탄을 판매했다."
        wrong = "용량은 20 MW이다. 알파는 2024년에 석탄을 판매했다."
        self.blocked(prior, current, wrong)
        good = self.validate(prior, current, current)
        self.assertFalse(self.standalone_findings(good))
        rel = relations.korean_period_relations(current)
        self.assertTrue(any(
            key[0] == "relation:kr:period"
            and key[1] == "알파"
            and key[2] == "판매했다"
            and key[3] == ("석탄",)
            and key[-1] == "2025년에"
            for key in rel
        ))

    def test_korean_description_and_copular_facts_keep_periods(self):
        prior = "용량은 10 MW이다."
        cases = (
            (
                "용량은 20 MW이다. 알파는 2025년에 수익성이 높았다.",
                "용량은 20 MW이다. 알파는 2024년에 수익성이 높았다.",
                "description:kr:period",
            ),
            (
                "용량은 20 MW이다. 알파는 2025년에 선도 기업이었다.",
                "용량은 20 MW이다. 알파는 2024년에 선도 기업이었다.",
                "copular:kr:period",
            ),
        )
        for current, wrong, kind in cases:
            with self.subTest(kind=kind):
                self.blocked(prior, current, wrong)
                good = self.validate(prior, current, current)
                self.assertFalse(self.standalone_findings(good))
                rel = relations.korean_period_relations(current)
                self.assertTrue(any(key[0] == kind and key[-1] == "2025년에" for key in rel))

    def test_period_immediately_after_copula_binds_following_complement(self):
        prior = "Capacity is 10 MW."
        current = "Capacity is 20 MW. Alpha was, in 2025, profitable."
        wrong = "Capacity is 20 MW. Alpha was, in 2024, profitable."
        self.blocked(prior, current, wrong)
        good = self.validate(prior, current, current)
        self.assertFalse(self.standalone_findings(good))
        rel = relations.english_copular_period_relations(current)
        self.assertIn(
            ("relation:en:copular:period", "alpha", "was", ("profitable",), "2025"),
            rel,
        )

    def test_coordinated_preposed_period_binds_following_action(self):
        prior = "Capacity is 10 MW."
        current = "Capacity is 20 MW. In 2025, Alpha sold coal and in 2026 bought gas."
        wrong = "Capacity is 20 MW. In 2026, Alpha sold coal and in 2025 bought gas."
        self.blocked(prior, current, wrong)
        good = self.validate(prior, current, current)
        self.assertFalse(self.standalone_findings(good))
        rel = relations.english_factual_period_relations(current)
        self.assertIn(("relation:en:period", "alpha", "", "sold", ("coal",), "2025"), rel)
        self.assertIn(("relation:en:period", "alpha", "", "bought", ("gas",), "2026"), rel)


if __name__ == "__main__":
    unittest.main()
