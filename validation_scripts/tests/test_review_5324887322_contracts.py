"""Regressions for PR #385 Codex review 5324887322.

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


class Review5324887322Contracts(unittest.TestCase):
    def validate(self, prior, current, quote, dimensions=("quantitative_anchor",)):
        chain = chain_for(prior, current, quote, dimensions)
        binding.validate_content_enrichment_delta(
            chain, "review 5324887322",
            operation_card=copy.deepcopy(chain["0.6"][0]),
            locked_prompt_version=V5,
        )
        return chain

    def blocked(self, *args, **kwargs):
        with self.assertRaises(binding.Blocked):
            return self.validate(*args, **kwargs)

    def standalone_findings(self, chain):
        return stage._content_enrichment_audit_findings(
            copy.deepcopy(chain["0.6"][0]), "review 5324887322"
        )

    def test_from_is_a_boundary_operator(self):
        prior = "Capacity is 10 MW."
        current = "Capacity is 20 MW. Alpha sold coal from 2025."
        wrong = "Capacity is 20 MW. Alpha sold coal in 2025."
        self.blocked(prior, current, wrong)
        good = self.validate(prior, current, current)
        self.assertFalse(self.standalone_findings(good))
        self.assertEqual(atoms.temporal_period_observations("from 2025")[0][-1], "from:2025")
        self.assertEqual(
            atoms.temporal_period_observations("from March to June")[0][-1],
            "march-to-june",
        )

    def test_multiple_preposed_copular_periods_follow_complements(self):
        prior = "Capacity is 10 MW."
        current = "Capacity is 20 MW. Alpha was in 2025 profitable and in 2026 sustainable."
        wrong = "Capacity is 20 MW. Alpha was in 2026 profitable and in 2025 sustainable."
        self.blocked(prior, current, wrong)
        good = self.validate(prior, current, current)
        self.assertFalse(self.standalone_findings(good))
        rel = relations.english_copular_period_relations(current)
        self.assertIn(("relation:en:copular:period", "alpha", "was", ("profitable",), "2025"), rel)
        self.assertIn(("relation:en:copular:period", "alpha", "was", ("sustainable",), "2026"), rel)

    def test_korean_year_form_suffix_do_is_nonsemantic(self):
        prior = "용량은 10 MW이다."
        current = "용량은 20 MW이다. 알파는 2025년도 석탄을 판매했다."
        quote = "용량은 20 MW이다. 알파는 2025년 석탄을 판매했다."
        good = self.validate(prior, current, quote)
        self.assertFalse(self.standalone_findings(good))
        self.assertEqual(atoms.temporal_period_observations("2025년도")[0][-1], "2025년")
        self.assertEqual(atoms.temporal_period_observations("2025년부터")[0][-1], "2025년부터")
        self.assertEqual(atoms.temporal_period_observations("2025년까지")[0][-1], "2025년까지")

    def test_coordinated_korean_descriptions_keep_local_periods(self):
        prior = "용량은 10 MW이다."
        current = "용량은 20 MW이다. 알파는 2025년에 수익성이 높고 2026년에 안정성이 높았다."
        wrong = "용량은 20 MW이다. 알파는 2026년에 수익성이 높고 2025년에 안정성이 높았다."
        self.blocked(prior, current, wrong)
        good = self.validate(prior, current, current)
        self.assertFalse(self.standalone_findings(good))
        rel = relations.korean_period_relations(current)
        self.assertTrue(any(key[0] == "description:kr:period" and key[2] == "수익성" and key[-1] == "2025년" for key in rel))
        self.assertTrue(any(key[0] == "description:kr:period" and key[2] == "안정성" and key[-1] == "2026년" for key in rel))

    def test_korean_contrastive_action_endings_keep_period_ownership(self):
        prior = "용량은 10 MW이다."
        current = "용량은 20 MW이다. 알파는 석탄을 2024년에 판매했지만 가스를 2025년에 사용했지만 석유를 2026년에 구매했다."
        wrong = "용량은 20 MW이다. 알파는 석탄을 2025년에 판매했지만 가스를 2024년에 사용했지만 석유를 2026년에 구매했다."
        self.blocked(prior, current, wrong)
        good = self.validate(prior, current, current)
        self.assertFalse(self.standalone_findings(good))
        rel = relations.korean_period_relations(current)
        self.assertIn(("relation:kr:local-period", "알파", "판매", ("석탄",), "2024년"), rel)
        self.assertIn(("relation:kr:local-period", "알파", "사용", ("가스",), "2025년"), rel)

    def test_digit_leading_named_subject_keeps_dated_relations(self):
        prior = "Capacity is 10 MW."
        current = "Capacity is 20 MW. 3M sold coal in 2025 and gas in 2026."
        wrong = "Capacity is 20 MW. 3M sold coal in 2026 and gas in 2025."
        self.blocked(prior, current, wrong)
        good = self.validate(prior, current, current)
        self.assertFalse(self.standalone_findings(good))
        rel = relations.english_factual_period_relations(current)
        self.assertIn(("relation:en:period", "3m", "", "sold", ("coal",), "2025"), rel)
        self.assertIn(("relation:en:period", "3m", "", "sold", ("gas",), "2026"), rel)

    def test_changed_state_retains_boundary_operator(self):
        prior = "Capacity is 10 MW."
        current = "Capacity is 20 MW. Alpha suspended operations since 2025."
        wrong = "Capacity is 20 MW. Alpha suspended operations until 2025."
        dimensions = ("quantitative_anchor", "changed_state")
        self.blocked(prior, current, wrong, dimensions)
        good = self.validate(prior, current, current, dimensions)
        self.assertFalse(self.standalone_findings(good))
        identities = binding._state_subject_strength_occurrences(current)
        self.assertTrue(any(key.endswith("=>period:since:2025") for key in identities))

    def test_metric_quantity_retains_boundary_periods(self):
        prior = "Capacity is 10 MW."
        current = "Capacity is 20 MW. Alpha revenue since 2025 was 30 USD and profit since 2026 was 40 USD."
        wrong = "Capacity is 20 MW. Alpha revenue since 2026 was 30 USD and profit since 2025 was 40 USD."
        self.blocked(prior, current, wrong)
        good = self.validate(prior, current, current)
        self.assertFalse(self.standalone_findings(good))
        rel = relations.metric_quantity_relations(current,binding._claim_subjects_for_span)
        self.assertTrue(any(key[0] == "metric:quantity" and key[2] == "revenue" and key[3] == "since:2025" for key in rel))
        self.assertTrue(any(key[0] == "metric:quantity" and key[2] == "profit" and key[3] == "since:2026" for key in rel))

    def test_parenthesized_period_after_auxiliary_is_bound(self):
        prior = "Capacity is 10 MW."
        current = "Capacity is 20 MW. Alpha had (in 2025) sold coal."
        wrong = "Capacity is 20 MW. Alpha had (in 2026) sold coal."
        self.blocked(prior, current, wrong)
        good = self.validate(prior, current, current)
        self.assertFalse(self.standalone_findings(good))
        self.assertIn(
            ("relation:en:period", "alpha", "had", "sold", ("coal",), "2025"),
            relations.english_factual_period_relations(current),
        )


if __name__ == "__main__":
    unittest.main()
