"""Regressions for PR #385 Codex review 5318539093.

Synthetic contract probes only; these do not certify live-source truth.
"""
import copy
import unittest

from validation_scripts import card_run_v4_binding_hardening as binding
from validation_scripts import content_claim_relations as relations
from validation_scripts import stage_artifact_contract_check as stage
from validation_scripts.tests.test_review_5265937741_contracts import chain_for

V5 = "PROMPT_0_6_V5_20260919"


class Review5318539093Contracts(unittest.TestCase):
    def validate(self, prior, current, quote, dimensions=("quantitative_anchor",)):
        chain = chain_for(prior, current, quote, dimensions)
        binding.validate_content_enrichment_delta(
            chain, "review 5318539093",
            operation_card=copy.deepcopy(chain["0.6"][0]),
            locked_prompt_version=V5,
        )
        return chain

    def blocked(self, *args, **kwargs):
        with self.assertRaises(binding.Blocked):
            return self.validate(*args, **kwargs)

    def standalone_findings(self, chain):
        return stage._content_enrichment_audit_findings(
            copy.deepcopy(chain["0.6"][0]), "review 5318539093"
        )

    def test_comma_wrapped_precopula_period_keeps_complement_locality(self):
        prior = "Capacity is 10 MW."
        current = (
            "Capacity is 20 MW. "
            "Alpha, in 2025, was profitable and sustainable in 2026."
        )
        wrong = (
            "Capacity is 20 MW. "
            "Alpha, in 2026, was profitable and sustainable in 2025."
        )
        self.blocked(prior, current, wrong)
        good = self.validate(prior, current, current)
        self.assertFalse(self.standalone_findings(good))
        rel = relations.english_copular_period_relations(current)
        self.assertIn(
            ("relation:en:copular:period", "alpha", "was", ("profitable",), "2025"),
            rel,
        )
        self.assertIn(
            ("relation:en:copular:period", "alpha", "was", ("sustainable",), "2026"),
            rel,
        )

    def test_comma_wrapped_period_after_active_subject_is_bound(self):
        prior = "Capacity is 10 MW."
        current = "Capacity is 20 MW. Alpha, in 2025, sold coal."
        wrong = "Capacity is 20 MW. Alpha, in 2026, sold coal."
        self.blocked(prior, current, wrong)
        good = self.validate(prior, current, current)
        self.assertFalse(self.standalone_findings(good))
        self.assertIn(
            ("relation:en:period", "alpha", "", "sold", ("coal",), "2025"),
            relations.english_factual_period_relations(current),
        )

    def test_korean_period_predicate_comma_is_local(self):
        prior = "용량은 10 MW이다."
        current = (
            "용량은 20 MW이다. "
            "알파는 석탄을 2025년에, 판매하고 가스를 2026년에, 판매했다."
        )
        wrong = (
            "용량은 20 MW이다. "
            "알파는 석탄을 2026년에, 판매하고 가스를 2025년에, 판매했다."
        )
        self.blocked(prior, current, wrong)
        good = self.validate(prior, current, current)
        self.assertFalse(self.standalone_findings(good))
        rel = relations.korean_period_relations(current)
        self.assertIn(
            ("relation:kr:local-period", "알파", "판매", ("석탄",), "2025년"),
            rel,
        )
        self.assertIn(
            ("relation:kr:local-period", "알파", "판매", ("가스",), "2026년"),
            rel,
        )

    def test_mixed_case_korean_subject_does_not_change_local_object(self):
        prior = "용량은 10 MW이다."
        current = "용량은 20 MW이다. Alpha는 석탄을 2025년에 판매했다."
        quote = "용량은 20 MW이다. alpha는 석탄을 2025년에 판매했다."
        good = self.validate(prior, current, quote)
        self.assertFalse(self.standalone_findings(good))
        self.assertEqual(
            relations.korean_period_relations(current),
            relations.korean_period_relations(quote),
        )
        self.assertIn(
            ("relation:kr:local-period", "alpha", "판매", ("석탄",), "2025년"),
            relations.korean_period_relations(current),
        )

    def test_comma_wrapped_masked_passive_aux_is_equivalent(self):
        prior = "Capacity is 10 MW."
        current = "Capacity is 20 MW. Coal had in 2025 been sold by Alpha."
        quote = "Capacity is 20 MW. Coal had, in 2025, been sold by Alpha."
        good = self.validate(prior, current, quote)
        self.assertFalse(self.standalone_findings(good))
        self.assertEqual(
            binding._factual_claim_counter(current),
            binding._factual_claim_counter(quote),
        )
        current_rel = relations.english_factual_period_relations(current)
        quote_rel = relations.english_factual_period_relations(quote)
        self.assertEqual(current_rel, quote_rel)
        self.assertTrue(any(
            key[0] == "relation:en:passive:period"
            and key[1] == "alpha"
            and key[2] == "had been"
            and key[-1] == "2025"
            for key in quote_rel
        ))

    def test_korean_long_object_modifiers_do_not_collapse(self):
        prior = "용량은 10 MW이다."
        current = (
            "용량은 20 MW이다. "
            "알파는 고급 호주산 저유황 발전용 석탄을 2025년에 판매하고 "
            "저급 호주산 저유황 발전용 석탄을 2026년에 판매했다."
        )
        wrong = (
            "용량은 20 MW이다. "
            "알파는 고급 호주산 저유황 발전용 석탄을 2026년에 판매하고 "
            "저급 호주산 저유황 발전용 석탄을 2025년에 판매했다."
        )
        self.blocked(prior, current, wrong)
        good = self.validate(prior, current, current)
        self.assertFalse(self.standalone_findings(good))
        rel = relations.korean_period_relations(current)
        self.assertIn(
            (
                "relation:kr:local-period", "알파", "판매",
                ("고급", "호주산", "저유황", "발전용", "석탄"), "2025년",
            ),
            rel,
        )
        self.assertIn(
            (
                "relation:kr:local-period", "알파", "판매",
                ("저급", "호주산", "저유황", "발전용", "석탄"), "2026년",
            ),
            rel,
        )

    def test_korean_negative_local_verbs_keep_period_ownership(self):
        prior = "용량은 10 MW이다."
        current = (
            "용량은 20 MW이다. "
            "알파는 석탄을 2025년에 판매하지 않고 "
            "가스를 2026년에 사용하지 않는다."
        )
        wrong = (
            "용량은 20 MW이다. "
            "알파는 석탄을 2026년에 판매하지 않고 "
            "가스를 2025년에 사용하지 않는다."
        )
        self.blocked(prior, current, wrong)
        good = self.validate(prior, current, current)
        self.assertFalse(self.standalone_findings(good))
        rel = relations.korean_period_relations(current)
        self.assertIn(
            ("relation:kr:local-period", "알파", "neg:판매", ("석탄",), "2025년"),
            rel,
        )
        self.assertIn(
            ("relation:kr:local-period", "알파", "neg:사용", ("가스",), "2026년"),
            rel,
        )


if __name__ == "__main__":
    unittest.main()
