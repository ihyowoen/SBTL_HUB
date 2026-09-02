import unittest

from validation_scripts.stage_a_v4_hardening import validate_stage_a_v4_hardening_payload


def make_spec(**overrides):
    spec = {
        "spec_id": "S-001",
        "anchor_classes": ["data_financial_anchor"],
        "technology_evidence_level": "not_applicable",
        "policy_stage": None,
        "novelty_cap_basis": "none",
        "decision_news_value_score": 60,
        "decision_value_breakdown": {
            "technology_performance_safety": 0,
            "systemic_scale": 2,
        },
        "systemic_scale_denominator": "Named program denominator.",
        "denominator_gap": None,
        "related_prepass": {
            "status": "PASS",
            "same_event_checked": True,
            "earliest_same_event_check_status": "PASS",
            "duplicate_disposition": "no_duplicate_found",
            "relation_candidates": [],
        },
    }
    spec.update(overrides)
    return spec


class StageAV4HardeningTests(unittest.TestCase):
    def messages_for(self, spec):
        return validate_stage_a_v4_hardening_payload(
            {"strict_passed_spec": [spec]}, require_contract=True
        )

    def test_valid_unconstrained_spec_passes(self):
        self.assertEqual(self.messages_for(make_spec()), [])

    def test_technology_evidence_cap_blocks_over_scoring(self):
        spec = make_spec(
            technology_evidence_level="company_target_or_unsupported_claim",
            decision_value_breakdown={"technology_performance_safety": 5, "systemic_scale": 2},
        )
        messages = self.messages_for(spec)
        self.assertTrue(any("exceeds" in message and "cap 4/20" in message for message in messages))

    def test_policy_stage_cap_blocks_over_scoring(self):
        spec = make_spec(
            anchor_classes=["policy_regulatory_anchor"],
            policy_stage=1,
            decision_news_value_score=55,
        )
        messages = self.messages_for(spec)
        self.assertTrue(any("policy_stage=1 cap 54" in message for message in messages))

    def test_novelty_cap_blocks_repeated_announcement(self):
        spec = make_spec(
            novelty_cap_basis="repeated_announcement_no_new_fact",
            decision_news_value_score=40,
        )
        messages = self.messages_for(spec)
        self.assertTrue(any("cap 39" in message for message in messages))

    def test_missing_denominator_caps_systemic_scale(self):
        spec = make_spec(
            systemic_scale_denominator=None,
            denominator_gap="No defensible denominator is available yet.",
            decision_value_breakdown={"technology_performance_safety": 0, "systemic_scale": 5},
        )
        messages = self.messages_for(spec)
        self.assertTrue(any("systemic_scale must be <=2" in message for message in messages))

    def test_no_duplicate_disposition_cannot_hide_duplicate_candidate(self):
        spec = make_spec(
            related_prepass={
                "status": "PASS",
                "same_event_checked": True,
                "earliest_same_event_check_status": "PASS",
                "duplicate_disposition": "no_duplicate_found",
                "relation_candidates": [
                    {
                        "proposed_relation_type": "existing_card_reinforcement",
                    }
                ],
            }
        )
        messages = self.messages_for(spec)
        self.assertTrue(any("contradicts" in message for message in messages))

    def test_policy_anchor_requires_stage(self):
        spec = make_spec(anchor_classes=["policy_regulatory_anchor"], policy_stage=None)
        messages = self.messages_for(spec)
        self.assertTrue(any("requires policy_stage" in message for message in messages))


if __name__ == "__main__":
    unittest.main()
