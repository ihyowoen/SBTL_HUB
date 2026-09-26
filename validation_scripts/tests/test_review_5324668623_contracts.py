"""Regressions for PR #385 Codex review 5324668623.

Synthetic contract probes only; these do not certify live-source truth.
"""
import copy
import unittest

from validation_scripts import card_run_v4_binding_hardening as binding
from validation_scripts import content_claim_relations as relations
from validation_scripts import content_semantic_atoms as atoms
from validation_scripts import stage_artifact_contract_check as stage
from validation_scripts.tests.test_review_5265937741_contracts import chain_for

V5 = "PROMPT_0_6_V5_20260919"


class Review5324668623Contracts(unittest.TestCase):
    def validate(self, prior, current, quote, dimensions=("quantitative_anchor",)):
        chain = chain_for(prior, current, quote, dimensions)
        binding.validate_content_enrichment_delta(
            chain, "review 5324668623",
            operation_card=copy.deepcopy(chain["0.6"][0]),
            locked_prompt_version=V5,
        )
        return chain

    def blocked(self, *args, **kwargs):
        with self.assertRaises(binding.Blocked):
            return self.validate(*args, **kwargs)

    def standalone_findings(self, chain):
        return stage._content_enrichment_audit_findings(
            copy.deepcopy(chain["0.6"][0]), "review 5324668623"
        )

    def test_active_contrastive_actions_keep_local_periods(self):
        prior = "Capacity is 10 MW."
        current = (
            "Capacity is 20 MW. "
            "Alpha, in 2025, sold coal but bought gas in 2026."
        )
        wrong = (
            "Capacity is 20 MW. "
            "Alpha, in 2026, sold coal but bought gas in 2025."
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

    def test_copular_contrastive_complements_keep_local_periods(self):
        prior = "Capacity is 10 MW."
        current = (
            "Capacity is 20 MW. "
            "Alpha, in 2025, was profitable but sustainable in 2026."
        )
        wrong = (
            "Capacity is 20 MW. "
            "Alpha, in 2026, was profitable but sustainable in 2025."
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

    def test_korean_bounded_modifier_before_period_keeps_object_locality(self):
        prior = "용량은 10 MW이다."
        current = (
            "용량은 20 MW이다. "
            "알파는 석탄을 주로 2025년에 판매하고 가스를 주로 2026년에 판매했다."
        )
        wrong = (
            "용량은 20 MW이다. "
            "알파는 석탄을 주로 2026년에 판매하고 가스를 주로 2025년에 판매했다."
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

    def test_passive_comma_coordinator_wrapper_is_equivalent(self):
        prior = "Capacity is 10 MW."
        current = (
            "Capacity is 20 MW. "
            "Coal, in 2025, and gas, in 2026, were sold by Alpha."
        )
        quote = (
            "Capacity is 20 MW. "
            "Coal in 2025 and gas in 2026 were sold by Alpha."
        )
        good = self.validate(prior, current, quote)
        self.assertFalse(self.standalone_findings(good))
        self.assertEqual(
            relations.english_factual_period_relations(current),
            relations.english_factual_period_relations(quote),
        )

    def test_parenthesized_subject_period_is_bound(self):
        prior = "Capacity is 10 MW."
        current = "Capacity is 20 MW. Alpha (in 2025) sold coal."
        wrong = "Capacity is 20 MW. Alpha (in 2026) sold coal."
        self.blocked(prior, current, wrong)
        good = self.validate(prior, current, current)
        self.assertFalse(self.standalone_findings(good))
        self.assertIn(
            ("relation:en:period", "alpha", "", "sold", ("coal",), "2025"),
            relations.english_factual_period_relations(current),
        )

    def test_korean_past_conjunctive_endings_keep_period_ownership(self):
        prior = "용량은 10 MW이다."
        current = (
            "용량은 20 MW이다. "
            "알파는 석탄을 2024년에 판매하지 않았으며 "
            "가스를 2025년에 사용하지 않았으며 "
            "석유를 2026년에 구매하지 않는다."
        )
        wrong = (
            "용량은 20 MW이다. "
            "알파는 석탄을 2025년에 판매하지 않았으며 "
            "가스를 2024년에 사용하지 않았으며 "
            "석유를 2026년에 구매하지 않는다."
        )
        self.blocked(prior, current, wrong)
        good = self.validate(prior, current, current)
        self.assertFalse(self.standalone_findings(good))
        rel = relations.korean_period_relations(current)
        self.assertIn(
            ("relation:kr:local-period", "알파", "neg:판매", ("석탄",), "2024년"),
            rel,
        )
        self.assertIn(
            ("relation:kr:local-period", "알파", "neg:사용", ("가스",), "2025년"),
            rel,
        )
        self.assertIn(
            ("relation:kr:local-period", "알파", "neg:구매", ("석유",), "2026년"),
            rel,
        )

    def test_temporal_boundary_operator_is_part_of_identity(self):
        prior = "Capacity is 10 MW."
        current = "Capacity is 20 MW. Alpha sold coal since 2025."
        wrong = "Capacity is 20 MW. Alpha sold coal until 2025."
        self.blocked(prior, current, wrong)
        good = self.validate(prior, current, current)
        self.assertFalse(self.standalone_findings(good))
        self.assertEqual(
            atoms.temporal_period_observations("since 2025")[0][-1],
            "since:2025",
        )
        self.assertEqual(
            atoms.temporal_period_observations("until 2025")[0][-1],
            "until:2025",
        )
        self.assertEqual(
            atoms.temporal_period_observations("in 2025")[0][-1],
            atoms.temporal_period_observations("during 2025")[0][-1],
        )

    def test_korean_locative_year_particle_is_nonsemantic(self):
        prior = "용량은 10 MW이다."
        current = "용량은 20 MW이다. 알파는 2025년에 석탄을 판매했다."
        quote = "용량은 20 MW이다. 알파는 2025년 석탄을 판매했다."
        good = self.validate(prior, current, quote)
        self.assertFalse(self.standalone_findings(good))
        self.assertEqual(
            atoms.temporal_period_observations("2025년에")[0][-1],
            "2025년",
        )
        self.assertEqual(
            atoms.temporal_period_observations("2025년")[0][-1],
            "2025년",
        )
        self.assertEqual(
            atoms.temporal_period_observations("2025년부터")[0][-1],
            "2025년부터",
        )
        self.assertEqual(
            atoms.temporal_period_observations("2025년까지")[0][-1],
            "2025년까지",
        )


if __name__ == "__main__":
    unittest.main()
