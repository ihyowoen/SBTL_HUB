"""Regressions for PR #385 Codex review 5317503137.

Synthetic contract probes only; these do not certify live-source truth.
"""
import copy
import unittest

from validation_scripts import card_run_v4_binding_hardening as binding
from validation_scripts import content_claim_relations as relations
from validation_scripts import stage_artifact_contract_check as stage
from validation_scripts.tests.test_review_5265937741_contracts import chain_for

V5 = "PROMPT_0_6_V5_20260919"


class Review5317503137Contracts(unittest.TestCase):
    def validate(self, prior, current, quote, dimensions=("quantitative_anchor",)):
        chain = chain_for(prior, current, quote, dimensions)
        binding.validate_content_enrichment_delta(
            chain, "review 5317503137",
            operation_card=copy.deepcopy(chain["0.6"][0]),
            locked_prompt_version=V5,
        )
        return chain

    def blocked(self, *args, **kwargs):
        with self.assertRaises(binding.Blocked):
            return self.validate(*args, **kwargs)

    def standalone_findings(self, chain):
        return stage._content_enrichment_audit_findings(
            copy.deepcopy(chain["0.6"][0]), "review 5317503137"
        )

    def test_coordinated_preposed_period_parses_repeated_subject(self):
        prior = "Capacity is 10 MW."
        current = (
            "Capacity is 20 MW. In 2025, Alpha sold coal "
            "and in 2026 Alpha bought gas."
        )
        wrong = (
            "Capacity is 20 MW. In 2026, Alpha sold coal "
            "and in 2025 Alpha bought gas."
        )
        self.blocked(prior, current, wrong)
        good = self.validate(prior, current, current)
        self.assertFalse(self.standalone_findings(good))
        rel = relations.english_factual_period_relations(current)
        self.assertIn(
            ("relation:en:period", "alpha", "", "sold", ("coal",), "2025"),
            rel,
        )
        self.assertIn(
            ("relation:en:period", "alpha", "", "bought", ("gas",), "2026"),
            rel,
        )

    def test_korean_coordinated_periods_bind_local_objects(self):
        prior = "용량은 10 MW이다."
        current = (
            "용량은 20 MW이다. "
            "알파는 2025년에 석탄을 판매하고 2026년에 가스를 판매했다."
        )
        wrong = (
            "용량은 20 MW이다. "
            "알파는 2026년에 석탄을 판매하고 2025년에 가스를 판매했다."
        )
        self.blocked(prior, current, wrong)
        good = self.validate(prior, current, current)
        self.assertFalse(self.standalone_findings(good))
        rel = relations.korean_period_relations(current)
        self.assertIn(
            ("relation:kr:local-period", "알파", "판매", ("석탄",), "2025년에"),
            rel,
        )
        self.assertIn(
            ("relation:kr:local-period", "알파", "판매", ("가스",), "2026년에"),
            rel,
        )

    def test_passive_preaux_periods_bind_local_objects(self):
        prior = "Capacity is 10 MW."
        current = "Capacity is 20 MW. Coal in 2025 and gas in 2026 were sold by Alpha."
        wrong = "Capacity is 20 MW. Coal in 2026 and gas in 2025 were sold by Alpha."
        self.blocked(prior, current, wrong)
        good = self.validate(prior, current, current)
        self.assertFalse(self.standalone_findings(good))
        rel = relations.english_factual_period_relations(current)
        self.assertIn(
            ("relation:en:passive:period", "alpha", "were", "sold", ("coal",), "2025"),
            rel,
        )
        self.assertIn(
            ("relation:en:passive:period", "alpha", "were", "sold", ("gas",), "2026"),
            rel,
        )

    def test_auxiliary_before_preverb_period_is_bound(self):
        prior = "Capacity is 10 MW."
        current = "Capacity is 20 MW. Alpha had in 2025 sold coal."
        wrong = "Capacity is 20 MW. Alpha had in 2026 sold coal."
        self.blocked(prior, current, wrong)
        good = self.validate(prior, current, current)
        self.assertFalse(self.standalone_findings(good))
        rel = relations.english_factual_period_relations(current)
        self.assertIn(
            ("relation:en:period", "alpha", "had", "sold", ("coal",), "2025"),
            rel,
        )


if __name__ == "__main__":
    unittest.main()
