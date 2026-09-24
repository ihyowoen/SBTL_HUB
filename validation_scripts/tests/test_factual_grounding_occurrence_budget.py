import unittest

from validation_scripts import card_run_v4_binding_hardening as binding
from validation_scripts.tests.test_review_5265937741_contracts import chain_for


class FactualGroundingOccurrenceBudgetTests(unittest.TestCase):
    def test_overlapping_english_recognizers_count_each_literal_occurrence_once(self):
        text = (
            "Fox ESS launched AirGate in Australia as a whole-home backup solution. "
            "AirGate provides whole-home backup of up to 63A, supporting up to 14.5 kW "
            "(single-phase) or 43.5 kW (three-phase)."
        )
        counts = binding._factual_claim_counter(text)
        self.assertEqual(counts["provides"], 1)
        self.assertEqual(counts["supporting"], 1)
        self.assertEqual(counts["airgate"], 2)
        self.assertEqual(counts["whole-home"], 2)

    def test_real_repeated_wording_keeps_occurrence_budget(self):
        text = "Alpha sold coal. Alpha sold coal."
        counts = binding._factual_claim_counter(text)
        self.assertEqual(counts["alpha"], 2)
        self.assertEqual(counts["sold"], 2)
        self.assertEqual(counts["coal"], 2)

    def test_literal_real_source_sentence_is_grounded_by_identical_quote(self):
        prior = "Fox ESS launched AirGate in Australia as a whole-home backup solution."
        current = (
            prior + " AirGate provides whole-home backup of up to 63A, supporting up to "
            "14.5 kW (single-phase) or 43.5 kW (three-phase)."
        )
        binding.validate_content_enrichment_delta(
            chain_for(prior, current, current), "real-source-regression"
        )

    def test_same_numbers_do_not_hide_ungrounded_predicate(self):
        prior = "Fox ESS launched AirGate in Australia as a whole-home backup solution."
        current = (
            prior + " AirGate provides whole-home backup of up to 63A, supporting up to "
            "14.5 kW (single-phase) or 43.5 kW (three-phase)."
        )
        quote = (
            prior + " AirGate limits whole-home backup to 63A, with ratings of "
            "14.5 kW (single-phase) or 43.5 kW (three-phase)."
        )
        with self.assertRaises(binding.Blocked):
            binding.validate_content_enrichment_delta(
                chain_for(prior, current, quote), "real-source-negative-control"
            )


if __name__ == "__main__":
    unittest.main()
