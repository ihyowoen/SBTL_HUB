"""Regressions for PR #385 Codex review 5318161551.

Synthetic contract probes only; these do not certify live-source truth.
"""
import copy
import unittest

from validation_scripts import card_run_v4_binding_hardening as binding
from validation_scripts import content_claim_relations as relations
from validation_scripts import stage_artifact_contract_check as stage
from validation_scripts.tests.test_review_5265937741_contracts import chain_for

V5 = "PROMPT_0_6_V5_20260919"


class Review5318161551Contracts(unittest.TestCase):
    def validate(self, prior, current, quote, dimensions=("quantitative_anchor",)):
        chain = chain_for(prior, current, quote, dimensions)
        binding.validate_content_enrichment_delta(
            chain, "review 5318161551",
            operation_card=copy.deepcopy(chain["0.6"][0]),
            locked_prompt_version=V5,
        )
        return chain

    def blocked(self, *args, **kwargs):
        with self.assertRaises(binding.Blocked):
            return self.validate(*args, **kwargs)

    def standalone_findings(self, chain):
        return stage._content_enrichment_audit_findings(
            copy.deepcopy(chain["0.6"][0]), "review 5318161551"
        )

    def test_korean_object_before_period_binds_local_object(self):
        prior = "용량은 10 MW이다."
        current = (
            "용량은 20 MW이다. "
            "알파는 석탄을 2025년에 판매하고 가스를 2026년에 판매했다."
        )
        wrong = (
            "용량은 20 MW이다. "
            "알파는 석탄을 2026년에 판매하고 가스를 2025년에 판매했다."
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

    def test_masked_multiword_passive_aux_whitespace_is_canonical(self):
        prior = "Capacity is 10 MW."
        current = "Capacity is 20 MW. Coal had in 2025 been sold by Alpha."
        quote = "Capacity is 20 MW. Coal in 2025 had been sold by Alpha."
        good = self.validate(prior, current, quote)
        self.assertFalse(self.standalone_findings(good))
        current_rel = relations.english_factual_period_relations(current)
        quote_rel = relations.english_factual_period_relations(quote)
        self.assertEqual(current_rel, quote_rel)
        self.assertTrue(any(
            key[0] == "relation:en:passive:period"
            and key[1] == "alpha"
            and key[2] == "had been"
            and key[-1] == "2025"
            for key in current_rel
        ))

    def test_comma_wrapped_auxiliary_preverb_period_is_bound(self):
        prior = "Capacity is 10 MW."
        current = "Capacity is 20 MW. Alpha had, in 2025, sold coal."
        wrong = "Capacity is 20 MW. Alpha had, in 2026, sold coal."
        self.blocked(prior, current, wrong)
        good = self.validate(prior, current, current)
        self.assertFalse(self.standalone_findings(good))
        rel = relations.english_factual_period_relations(current)
        self.assertIn(
            ("relation:en:period", "alpha", "had", "sold", ("coal",), "2025"),
            rel,
        )

    def test_comma_wrapped_precopula_period_is_bound(self):
        prior = "Capacity is 10 MW."
        current = "Capacity is 20 MW. Alpha, in 2025, was profitable."
        wrong = "Capacity is 20 MW. Alpha, in 2026, was profitable."
        self.blocked(prior, current, wrong)
        good = self.validate(prior, current, current)
        self.assertFalse(self.standalone_findings(good))
        rel = relations.english_copular_period_relations(current)
        self.assertIn(
            ("relation:en:copular:period", "alpha", "was", ("profitable",), "2025"),
            rel,
        )


if __name__ == "__main__":
    unittest.main()
