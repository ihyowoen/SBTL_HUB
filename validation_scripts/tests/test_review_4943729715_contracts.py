from __future__ import annotations

import copy
import io
import unittest
from contextlib import redirect_stdout

from validation_scripts import stage_a_full_v3_completeness_review4943656188_final as final
from validation_scripts import stage_lineage_contract_check as lineage
from validation_scripts.tests.test_review_4943695732_contracts import (
    Review4943695732Contracts,
)
from validation_scripts.tests.test_stage_a_full_v3_artifact_completeness import (
    TestStageAFullV3ArtifactCompleteness,
)


class Review4943729715Contracts(unittest.TestCase):
    def full_artifact(self):
        return TestStageAFullV3ArtifactCompleteness().full_artifact()

    def validate_full(self, artifact):
        return final.validate_full_stage_a_artifact(artifact, lineage._compat_module)

    def test_reinforcement_and_support_outcomes_require_complete_contracts(self):
        messages: list[str] = []
        final._validate_nonreview_outcome_contracts(
            {
                "existing_reinforcement": [{"story_id": "REINF_001"}],
                "support_source_only": [{"story_id": "SUPPORT_001"}],
            },
            messages,
        )
        self.assertTrue(
            any("missing required existing_reinforcement field reinforcement_type" in message for message in messages),
            messages,
        )
        self.assertTrue(
            any("missing required existing_reinforcement field reason_not_new_card" in message for message in messages),
            messages,
        )
        self.assertTrue(
            any("missing required support_source_only field potential_supported_topic" in message for message in messages),
            messages,
        )
        self.assertTrue(
            any("missing required support_source_only field reason_not_independent_card" in message for message in messages),
            messages,
        )

    def test_malformed_summary_id_array_fails_closed_without_typeerror(self):
        artifact = self.full_artifact()
        artifact["summary"]["critical_structural_candidate_ids"] = [{}]
        stream = io.StringIO()
        with redirect_stdout(stream):
            result = lineage.check_stage_a(artifact)
        self.assertEqual(result, 1, stream.getvalue())
        self.assertIn(
            "critical_structural_candidate_ids must contain only non-empty story/spec IDs",
            stream.getvalue(),
        )

    def test_review_resolution_ledger_rows_require_complete_contract(self):
        review_item = Review4943695732Contracts().review_item()
        messages: list[str] = []
        final._validate_review_resolution_ledger(
            {
                "candidate_review_pool": [review_item],
                "watchlist_context_pool": [],
                "reject_or_support_only_pool": [],
                "review_pool": [],
                "review_pool_resolution_ledger": [
                    {"review_pool_item_id": review_item["review_pool_item_id"]}
                ],
            },
            messages,
        )
        for field in (
            "original_review_pool_partition",
            "current_disposition",
            "disposition_basis",
            "carry_forward_policy",
            "next_action_condition",
            "whether_user_authorization_required",
        ):
            self.assertTrue(
                any(f"missing required review-resolution field {field}" in message for message in messages),
                messages,
            )
        self.assertTrue(
            any("requires story_id or non-empty grouped_story_ids" in message for message in messages),
            messages,
        )

    def test_strict_bucket_rejects_duplicate_fatal_and_stale_values(self):
        mutations = (
            ("baseline_relation", "duplicate_of_main"),
            ("duplicate_risk", "fatal"),
            ("staleness_decision", "stale"),
        )
        for field, value in mutations:
            with self.subTest(field=field, value=value):
                artifact = self.full_artifact()
                artifact["strict_passed_spec"][0][field] = value
                messages = self.validate_full(artifact)
                self.assertTrue(
                    any(
                        f"strict_passed_spec cannot use {field}={value}" in message
                        for message in messages
                    ),
                    messages,
                )

    def test_complete_nonreview_outcome_contracts_pass_targeted_validation(self):
        messages: list[str] = []
        final._validate_nonreview_outcome_contracts(
            {
                "existing_reinforcement": [
                    {
                        "story_id": "REINF_002",
                        "baseline_card_id": "CARD_001",
                        "reinforcement_type": "source_reinforcement",
                        "reason_not_new_card": "The article adds corroboration but no new event or changed judgment.",
                        "notes": "Synthetic reinforcement fixture.",
                    }
                ],
                "support_source_only": [
                    {
                        "story_id": "SUPPORT_002",
                        "potential_supported_topic": "named battery supply-chain event",
                        "reason_not_independent_card": "The source is useful corroboration but does not establish an independent current event.",
                        "possible_target_card_or_spec": "CARD_001",
                        "notes": "Synthetic support-source fixture.",
                    }
                ],
            },
            messages,
        )
        self.assertEqual(messages, [])


if __name__ == "__main__":
    unittest.main()
