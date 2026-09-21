import copy
import unittest

from validation_scripts import card_run_v4_binding_hardening as binding
from validation_scripts.tests.test_content_enrichment_delta_contract import (
    SOURCE, audit_for_dimensions, row06, rows,
)


def chain_for(prior, current, quote, dimensions=("quantitative_anchor",)):
    source = {**SOURCE, "source_quote": quote}
    unchanged = prior == current
    row = row06(fact=current, fact_sources=[source], content_enrichment_audit=
                audit_for_dimensions([] if unchanged else ["fact"], dimensions,
                                     no_change=unchanged, reason="Already dense."))
    chain = rows(row)
    for stage in ("B", "C"):
        chain[stage][0]["fact_sources"] = [copy.deepcopy(source)]
    for stage in ("C", "0.4", "0.5"):
        chain[stage][0]["fact"] = prior
    return chain


class Review5265937741Tests(unittest.TestCase):
    def validate(self, chain):
        binding.validate_content_enrichment_delta(chain, "review regression")

    def test_explicit_fetch_failures_override_positive_metadata(self):
        for failure in ({"fetched": False}, {"fetch_status": "fetch_failed"},
                        {"fetch_status": "failed"}, {"fetch_status": "timeout"}):
            with self.subTest(failure=failure):
                chain = chain_for("Capacity is 10 MW", "Capacity is 20 MW", "Capacity is 20 MW")
                for stage in ("B", "C"):
                    chain[stage][0]["fact_sources"][0].update(failure, fetched_at="2026-09-21")
                with self.assertRaises(binding.Blocked):
                    self.validate(chain)

    def test_timestamp_only_success_still_grounds(self):
        chain = chain_for("Capacity is 10 MW", "Capacity is 20 MW", "Capacity is 20 MW")
        for stage in ("B", "C"):
            source = chain[stage][0]["fact_sources"][0]
            source.pop("fetched")
            source["fetched_at"] = "2026-09-21"
        self.validate(chain)

    def test_subject_state_swap_is_checked_without_global_state_delta(self):
        prior = "Alpha may be delayed; Beta is delayed; capacity is 10 MW"
        current = "Alpha is delayed; Beta may be delayed; capacity is 20 MW"
        for dimensions in (("quantitative_anchor",), ("quantitative_anchor", "changed_state")):
            with self.subTest(dimensions=dimensions), self.assertRaises(binding.Blocked):
                self.validate(chain_for(prior, current,
                    "Alpha may be delayed; Beta is delayed; capacity is 20 MW", dimensions))

    def test_grounded_subject_state_swap_passes(self):
        prior = "Alpha may be delayed; Beta is delayed; capacity is 10 MW"
        current = "Alpha is delayed; Beta may be delayed; capacity is 20 MW"
        self.validate(chain_for(prior, current, current, ("quantitative_anchor", "changed_state")))

    def test_modal_predicates_cannot_hitchhike_on_quantity(self):
        for modal in ("can", "could", "may", "might", "will", "would", "must", "should"):
            with self.subTest(modal=modal), self.assertRaises(binding.Blocked):
                self.validate(chain_for("Capacity is 10 MW", f"Capacity is 20 MW and {modal} burn coal",
                                        "Capacity is 20 MW"))

    def test_grounded_modal_predicate_passes(self):
        current = "Capacity is 20 MW and can burn coal"
        self.validate(chain_for("Capacity is 10 MW", current, current))

    def test_predicate_objects_cannot_swap_subjects(self):
        for verb in ("burns", "uses", "can burn"):
            prior = f"Alpha {verb} coal. Beta {verb} gas. Capacity is 10 MW"
            current = f"Alpha {verb} gas. Beta {verb} coal. Capacity is 20 MW"
            with self.subTest(verb=verb), self.assertRaises(binding.Blocked):
                self.validate(chain_for(prior, current, prior.replace("10 MW", "20 MW")))

    def test_grounded_predicate_object_swap_passes(self):
        prior = "Alpha burns coal. Beta burns gas. Capacity is 10 MW"
        current = "Alpha burns gas. Beta burns coal. Capacity is 20 MW"
        self.validate(chain_for(prior, current, current))

    def test_neither_nor_cannot_manufacture_realized_density(self):
        text = "Previously, the planned 10 MW project was neither approved nor started because supply costs rose"
        self.assertFalse(binding._signal_counter("changed_state", text))
        with self.assertRaises(binding.Blocked):
            self.validate(chain_for(text, text, text,
                ("prior_state", "changed_state", "quantitative_anchor", "boundary_or_uncertainty", "transmission_path")))

    def test_neither_nor_scope_ends_at_affirmative_clause(self):
        text = "Alpha was neither approved nor started, but Beta was approved"
        self.assertEqual(binding._signal_counter("changed_state", text), {"approval": 1})

    def test_leading_spaced_numeric_operators_are_semantic(self):
        tail = "; Previously planned; construction started; target remains subject to certification"
        for operator in (">", "-", "+"):
            with self.subTest(operator=operator):
                current = f"{operator} 300 MW{tail}"
                self.assertEqual(binding._normalize_text(current), current)
                chain = chain_for(current, current, "300 MW" + tail,
                    ("prior_state", "changed_state", "quantitative_anchor", "boundary_or_uncertainty"))
                with self.assertRaises(binding.Blocked):
                    self.validate(chain)

    def test_presentation_list_and_blockquote_still_normalize(self):
        for marker in ("-", "+", ">"):
            self.assertEqual(binding._normalize_text(f"{marker} Capacity is 300 MW"), "Capacity is 300 MW")

    def test_zero_delta_requires_source_state_strength(self):
        text = "Previously planned at 10 MW; the project is delayed; target remains subject to certification"
        dimensions = ("prior_state", "changed_state", "quantitative_anchor", "boundary_or_uncertainty")
        with self.assertRaises(binding.Blocked):
            self.validate(chain_for(text, text, text.replace("is delayed", "may be delayed"), dimensions))
        self.validate(chain_for(text, text, text, dimensions))

    def test_exclusions_follow_aliases_within_and_across_stages(self):
        for exclusion_stage in ("C", "0.5"):
            for token_key, token in (("source_url", SOURCE["source_url"]), ("source_id", "SRC1")):
                with self.subTest(stage=exclusion_stage, key=token_key):
                    chain = chain_for("Capacity is 10 MW", "Capacity is 20 MW", "Capacity is 20 MW")
                    chain[exclusion_stage][0]["source_discovery_ledger"] = [
                        {token_key: token, "supporting_context_only_not_visible_claim_support": True}]
                    support = binding._upstream_evidence_token_support(chain, "test")
                    self.assertNotIn("SRC1", support)
                    self.assertNotIn(SOURCE["source_url"], support)
                    with self.assertRaises(binding.Blocked):
                        self.validate(chain)


if __name__ == "__main__":
    unittest.main()
