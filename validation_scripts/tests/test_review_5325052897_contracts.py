"""Regressions for PR #385 Codex review 5325052897.

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


class Review5325052897Contracts(unittest.TestCase):
    def validate(self, prior, current, quote, dimensions=("quantitative_anchor",)):
        chain = chain_for(prior, current, quote, dimensions)
        binding.validate_content_enrichment_delta(
            chain, "review 5325052897",
            operation_card=copy.deepcopy(chain["0.6"][0]),
            locked_prompt_version=V5,
        )
        return chain

    def blocked(self, *args, **kwargs):
        with self.assertRaises(binding.Blocked):
            return self.validate(*args, **kwargs)

    def standalone_findings(self, chain):
        return stage._content_enrichment_audit_findings(
            copy.deepcopy(chain["0.6"][0]), "review 5325052897"
        )

    def test_comma_delimited_preposed_copular_periods_follow_complements(self):
        prior = "Capacity is 10 MW."
        current = "Capacity is 20 MW. Alpha was in 2025 profitable, in 2026 sustainable."
        wrong = "Capacity is 20 MW. Alpha was in 2026 profitable, in 2025 sustainable."
        self.blocked(prior, current, wrong)
        good = self.validate(prior, current, current)
        self.assertFalse(self.standalone_findings(good))
        rel = relations.english_copular_period_relations(current)
        self.assertIn(("relation:en:copular:period", "alpha", "was", ("profitable",), "2025"), rel)
        self.assertIn(("relation:en:copular:period", "alpha", "was", ("sustainable",), "2026"), rel)

    def test_present_negative_korean_contrastive_endings_keep_local_periods(self):
        prior = "용량은 10 MW이다."
        current = (
            "용량은 20 MW이다. "
            "알파는 석탄을 2024년에 판매하지 않지만 "
            "가스를 2025년에 사용하지 않지만 석유를 2026년에 구매하지 않는다."
        )
        wrong = (
            "용량은 20 MW이다. "
            "알파는 석탄을 2025년에 판매하지 않지만 "
            "가스를 2024년에 사용하지 않지만 석유를 2026년에 구매하지 않는다."
        )
        self.blocked(prior, current, wrong)
        good = self.validate(prior, current, current)
        self.assertFalse(self.standalone_findings(good))
        rel = relations.korean_period_relations(current)
        self.assertIn(("relation:kr:local-period", "알파", "neg:판매", ("석탄",), "2024년"), rel)
        self.assertIn(("relation:kr:local-period", "알파", "neg:사용", ("가스",), "2025년"), rel)

    def test_contrastive_korean_descriptions_keep_local_periods(self):
        prior = "용량은 10 MW이다."
        current = (
            "용량은 20 MW이다. "
            "알파는 2024년에 수익성이 높았지만 "
            "2025년에 안정성이 낮았지만 2026년에 효율성이 높았다."
        )
        wrong = (
            "용량은 20 MW이다. "
            "알파는 2025년에 수익성이 높았지만 "
            "2024년에 안정성이 낮았지만 2026년에 효율성이 높았다."
        )
        self.blocked(prior, current, wrong)
        good = self.validate(prior, current, current)
        self.assertFalse(self.standalone_findings(good))
        rel = relations.korean_period_relations(current)
        self.assertTrue(any(key[0] == "description:kr:period" and key[2] == "수익성" and key[-1] == "2024년" for key in rel))
        self.assertTrue(any(key[0] == "description:kr:period" and key[2] == "안정성" and key[-1] == "2025년" for key in rel))

    def test_korean_boundary_suffixes_bind_metric_quantities(self):
        prior = "용량은 10 MW이다."
        current = "용량은 20 MW이다. 알파 매출은 2025년부터 30 USD이고 이익은 2026년부터 40 USD이다."
        wrong = "용량은 20 MW이다. 알파 매출은 2026년부터 30 USD이고 이익은 2025년부터 40 USD이다."
        self.blocked(prior, current, wrong)
        good = self.validate(prior, current, current)
        self.assertFalse(self.standalone_findings(good))
        rel = relations.metric_quantity_relations(current, binding._claim_subjects_for_span)
        self.assertTrue(any(key[0] == "metric:quantity" and key[1] == "알파" and key[2] == "매출" and key[3] == "2025년부터" for key in rel))
        self.assertTrue(any(key[0] == "metric:quantity" and key[1] == "알파" and key[2] == "이익" and key[3] == "2026년부터" for key in rel))

    def test_digit_leading_subjects_propagate_to_state_and_metric_binding(self):
        prior = "Capacity is 10 MW."
        dimensions = ("quantitative_anchor", "changed_state")
        current_state = "Capacity is 20 MW. 3M suspended operations since 2025."
        wrong_state = "Capacity is 20 MW. 7Eleven suspended operations since 2025."
        self.blocked(prior, current_state, wrong_state, dimensions)
        good = self.validate(prior, current_state, current_state, dimensions)
        self.assertFalse(self.standalone_findings(good))
        identities = binding._state_subject_strength_occurrences(current_state)
        self.assertTrue(any(key.startswith("3m=>") for key in identities))

        current_metric = (
            "Capacity is 20 MW. "
            "3M revenue since 2025 was 30 USD and profit since 2026 was 40 USD."
        )
        wrong_metric = (
            "Capacity is 20 MW. "
            "3M revenue since 2026 was 30 USD and profit since 2025 was 40 USD."
        )
        self.blocked(prior, current_metric, wrong_metric)
        rel = relations.metric_quantity_relations(current_metric, binding._claim_subjects_for_span)
        self.assertTrue(any(key[0] == "metric:quantity" and key[1] == "3m" and key[3] == "since:2025" for key in rel))

    def test_korean_year_form_particles_are_consumed_as_one_period(self):
        prior = "용량은 10 MW이다."
        current = "용량은 20 MW이다. 알파는 2025년도에 석탄을 판매했다."
        quote = "용량은 20 MW이다. 알파는 2025년에 석탄을 판매했다."
        good = self.validate(prior, current, quote)
        self.assertFalse(self.standalone_findings(good))
        self.assertEqual(atoms.temporal_period_observations("2025년도에")[0][-1], "2025년")
        self.assertEqual(atoms.temporal_period_observations("2025년도부터")[0][-1], "2025년부터")
        self.assertEqual(atoms.temporal_period_observations("2025년도까지")[0][-1], "2025년까지")


if __name__ == "__main__":
    unittest.main()
