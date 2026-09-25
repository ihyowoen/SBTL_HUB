"""Regressions for PR #385 Codex review 5316239913.

Synthetic contract probes only; these do not certify live-source truth.
"""
import copy
import unittest

from validation_scripts import card_run_v4_binding_hardening as binding
from validation_scripts import content_claim_relations as relations
from validation_scripts import stage_artifact_contract_check as stage
from validation_scripts.tests.test_review_5265937741_contracts import chain_for

V5 = "PROMPT_0_6_V5_20260919"


class Review5316239913Contracts(unittest.TestCase):
    def validate(self, prior, current, quote, dimensions=("quantitative_anchor",)):
        chain = chain_for(prior, current, quote, dimensions)
        binding.validate_content_enrichment_delta(
            chain, "review 5316239913",
            operation_card=copy.deepcopy(chain["0.6"][0]),
            locked_prompt_version=V5,
        )
        return chain

    def blocked(self, *args, **kwargs):
        with self.assertRaises(binding.Blocked):
            return self.validate(*args, **kwargs)

    def standalone_findings(self, chain):
        return stage._content_enrichment_audit_findings(
            copy.deepcopy(chain["0.6"][0]), "review 5316239913"
        )

    def test_intransitive_preposed_period_survives_later_tail_period(self):
        prior = "Capacity is 10 MW."
        current = "Capacity is 20 MW. In 2025, Alpha expanded and contracted in 2026."
        wrong = "Capacity is 20 MW. In 2024, Alpha expanded and contracted in 2026."
        self.blocked(prior, current, wrong)
        good = self.validate(prior, current, current)
        self.assertFalse(self.standalone_findings(good))
        rel = relations.english_factual_period_relations(current)
        self.assertIn(("relation:en:period", "alpha", "", "expanded", (), "2025"), rel)
        self.assertIn(("relation:en:period", "alpha", "", "contracted", (), "2026"), rel)

    def test_passive_leading_period_and_elliptical_object_both_survive(self):
        prior = "Capacity is 10 MW."
        current = (
            "Capacity is 20 MW. In 2025, some coal was sold by Alpha "
            "and gas in 2026."
        )
        wrong = (
            "Capacity is 20 MW. In 2024, some coal was sold by Alpha "
            "and gas in 2026."
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

    def test_period_inside_passive_predicate_is_bound(self):
        prior = "Capacity is 10 MW."
        for current, wrong in (
            (
                "Capacity is 20 MW. Some coal in 2025 was sold by Alpha.",
                "Capacity is 20 MW. Some coal in 2024 was sold by Alpha.",
            ),
            (
                "Capacity is 20 MW. Some coal was sold in 2025 by Alpha.",
                "Capacity is 20 MW. Some coal was sold in 2024 by Alpha.",
            ),
        ):
            with self.subTest(current=current):
                self.blocked(prior, current, wrong)
                good = self.validate(prior, current, current)
                self.assertFalse(self.standalone_findings(good))
                rel = relations.english_factual_period_relations(current)
                self.assertIn(
                    ("relation:en:passive:period", "alpha", "was", "sold", ("some", "coal"), "2025"),
                    rel,
                )

    def test_copular_leading_period_survives_later_tail_period(self):
        prior = "Capacity is 10 MW."
        current = (
            "Capacity is 20 MW. In 2025, Alpha is profitable "
            "and sustainable in 2026."
        )
        wrong = (
            "Capacity is 20 MW. In 2024, Alpha is profitable "
            "and sustainable in 2026."
        )
        self.blocked(prior, current, wrong)
        good = self.validate(prior, current, current)
        self.assertFalse(self.standalone_findings(good))
        rel = relations.english_copular_period_relations(current)
        self.assertIn(
            ("relation:en:copular:period", "alpha", "is", ("profitable",), "2025"),
            rel,
        )
        self.assertIn(
            ("relation:en:copular:period", "alpha", "is", ("sustainable",), "2026"),
            rel,
        )

    def test_korean_factual_relation_preserves_period(self):
        prior = "용량은 10 MW이다."
        current = "용량은 20 MW이다. 알파는 석탄을 2025년에 판매했다."
        wrong = "용량은 20 MW이다. 알파는 석탄을 2024년에 판매했다."
        self.blocked(prior, current, wrong)
        good = self.validate(prior, current, current)
        self.assertFalse(self.standalone_findings(good))
        rel = relations.korean_period_relations(current)
        self.assertIn(
            ("relation:kr:period", "알파", "판매했다", ("석탄",), "2025년"),
            rel,
        )

    def test_possessive_subject_is_supported_by_dated_action_parser(self):
        prior = "Capacity is 10 MW."
        current = "Capacity is 20 MW. Alpha's plant sold coal in 2025."
        wrong = "Capacity is 20 MW. Alpha's plant sold coal in 2024."
        self.blocked(prior, current, wrong)
        good = self.validate(prior, current, current)
        self.assertFalse(self.standalone_findings(good))
        rel = relations.english_factual_period_relations(current)
        self.assertIn(
            ("relation:en:period", "alpha's plant", "", "sold", ("coal",), "2025"),
            rel,
        )


if __name__ == "__main__":
    unittest.main()
