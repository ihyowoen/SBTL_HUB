import unittest

from validation_scripts import card_run_v4_binding_hardening as binding
from validation_scripts import stage_artifact_contract_check as stage_contract


DENSE_FACT = (
    "Previously planned at 1 GWh; commercial production started in 2026 at 2 GWh; "
    "target remains subject to certification."
)
NEW_DENSE_FACT = (
    "Previously planned at 1 GWh; commercial production started in 2026 at 2.5 GWh; "
    "target remains subject to certification."
)

SOURCE_QUOTE = (
    "Previously planned at 1 GWh; commercial production started in 2026 at 2 GWh "
    "and 2.5 GWh; target remains subject to certification; capacity is 10 MW / 10 MWh."
)
SOURCE = {
    "source_id": "SRC1",
    "source_url": "https://example.test/source",
    "source_quote": SOURCE_QUOTE,
    "source_quote_status": "body_quote_verified",
    "fetched": True,

}

VISIBLE = {
    "sub": "same sub",
    "gate": "same gate",
    "fact": DENSE_FACT,
    "implication": ["same implication"],
    "fact_sources": [SOURCE],
}


def density(*, supported=4, changed_state=True, bind_dimensions=False):
    values = {
        "prior_state": True,
        "changed_state": changed_state,
        "quantitative_anchor": True,
        "boundary_or_uncertainty": True,
        "transmission_path": False,
        "next_watchpoint": False,
    }
    if supported == 3:
        values["boundary_or_uncertainty"] = False
    elif supported == 5:
        values["transmission_path"] = True
    actual = sum(values.values())
    result = {
        "status": "PASS",
        "dimensions": values,
        "supported_dimension_count": actual,
        "evidence_notes": "Evidence-bounded density test.",
    }
    if bind_dimensions:
        result["dimension_evidence"] = {
            name: {"fields": ["fact"], "evidence_refs": ["SRC1"]}
            for name, enabled in values.items() if enabled
        }
    return result


def rows(row_06):
    source = dict(SOURCE)
    return {
        "B": [{"source_spec_id": "SPEC", "fact_sources": [source]}],
        "C": [{"source_spec_id": "SPEC", **VISIBLE, "fact_sources": [source]}],
        "0.4": [{"source_spec_id": "SPEC", "fact": VISIBLE["fact"]}],
        "0.5": [{"source_spec_id": "SPEC", "fact": VISIBLE["fact"]}],
        "0.6": [row_06],
    }


def audit(changed_fields, *, no_change=False, supported=4, reason="", bind_dimensions=True):
    return {
        "baseline_strategy": binding.CONTENT_BASELINE_STRATEGY,
        "changed_fields": changed_fields,
        "no_change_required": no_change,
        "no_change_reason": reason,
        "density_audit": density(
            supported=supported,
            bind_dimensions=bind_dimensions,
        ),
    }


def audit_for_dimensions(changed_fields, enabled, *, no_change=False, reason=""):
    values = {name: name in set(enabled) for name in binding.DENSITY_DIMENSIONS}
    return {
        "baseline_strategy": binding.CONTENT_BASELINE_STRATEGY,
        "changed_fields": changed_fields,
        "no_change_required": no_change,
        "no_change_reason": reason,
        "density_audit": {
            "status": "PASS",
            "dimensions": values,
            "supported_dimension_count": len(enabled),
            "evidence_notes": "Focused evidence-bounded density test.",
            "dimension_evidence": {
                name: {"fields": ["fact"], "evidence_refs": ["SRC1"]}
                for name in enabled
            },
        },
    }


def row06(**overrides):
    base = {
        "source_spec_id": "SPEC",
        **VISIBLE,
        "fact_sources": [dict(SOURCE)],
        "content_enriched": True,
    }
    base.update(overrides)
    return base


class ContentEnrichmentDeltaTests(unittest.TestCase):
    def test_zero_delta_falls_back_through_05_and_04_to_stage_c_and_blocks_boolean_only(self):
        row = row06(content_enrichment_audit=audit([], no_change=False))
        with self.assertRaisesRegex(binding.Blocked, "zero visible-copy delta"):
            binding.validate_content_enrichment_delta(rows(row), "insert[0]")

    def test_actual_fact_change_passes_and_missing_05_fields_do_not_create_false_delta(self):
        row = row06(
            fact=NEW_DENSE_FACT,
            content_enrichment_audit=audit(["fact"]),
        )
        binding.validate_content_enrichment_delta(
            rows(row), "insert[0]",
            operation_card={**VISIBLE, "fact": NEW_DENSE_FACT},
        )

    def test_declared_changed_fields_are_order_independent(self):
        row = row06(
            sub="changed sub",
            fact=NEW_DENSE_FACT,
            content_enrichment_audit=audit(["fact", "sub"]),
        )
        binding.validate_content_enrichment_delta(
            rows(row), "insert[0]",
            operation_card={**VISIBLE, "sub": "changed sub", "fact": NEW_DENSE_FACT},
        )

    def test_declared_changed_fields_must_equal_actual_delta(self):
        row = row06(
            fact="changed fact",
            content_enrichment_audit=audit(["sub"]),
        )
        with self.assertRaisesRegex(binding.Blocked, "does not equal actual visible-copy delta"):
            binding.validate_content_enrichment_delta(rows(row), "insert[0]")

    def test_removal_or_empty_visible_copy_cannot_count_as_enrichment(self):
        row = row06(content_enrichment_audit=audit(["fact"]))
        row.pop("fact")
        with self.assertRaisesRegex(binding.Blocked, "removal/empty value for fact"):
            binding.validate_content_enrichment_delta(rows(row), "insert[0]")

    def test_formatting_only_difference_is_zero_delta(self):
        row = row06(
            fact=DENSE_FACT.replace("commercial production", "commercial   production"),
            content_enrichment_audit=audit(
                [], no_change=True, supported=4,
                reason="Already decision-useful.",
                bind_dimensions=True,
            ),
        )
        binding.validate_content_enrichment_delta(
            rows(row), "insert[0]",
            operation_card=VISIBLE,
        )

    def test_markdown_only_difference_is_zero_delta(self):
        row = row06(
            fact=f"**{DENSE_FACT}**",
            content_enrichment_audit=audit(
                [], no_change=True, supported=4,
                reason="Only presentation markup differs.",
                bind_dimensions=True,
            ),
        )
        binding.validate_content_enrichment_delta(
            rows(row), "insert[0]",
            operation_card=VISIBLE,
        )

    def test_presentation_only_empty_copy_is_treated_as_removal(self):
        row = row06(
            fact="**",
            content_enrichment_audit=audit(["fact"]),
        )
        with self.assertRaisesRegex(binding.Blocked, "removal/empty value for fact"):
            binding.validate_content_enrichment_delta(rows(row), "insert[0]")

    def test_presentation_only_empty_intermediate_does_not_mask_stage_c(self):
        row = row06(
            content_enrichment_audit=audit(
                [], no_change=True, supported=4,
                reason="Presentation-only intermediate copy cannot mask Stage C.",
                bind_dimensions=True,
            ),
        )
        chain = rows(row)
        chain["0.5"][0]["fact"] = "**"
        chain["0.4"][0]["fact"] = None
        binding.validate_content_enrichment_delta(
            chain, "insert[0]", operation_card=VISIBLE,
        )

    def test_literal_asterisks_survive_markup_normalization(self):
        for value in ("capacity is 2 * 3 GWh", "rating moved to A*"):
            self.assertEqual(binding._normalize_text(value), value)
            self.assertEqual(stage_contract._normalize_text(value), value)
        self.assertEqual(binding._normalize_text("**same fact**"), "same fact")
        self.assertEqual(stage_contract._normalize_text("**same fact**"), "same fact")

    def test_strikethrough_remains_semantically_distinct(self):
        plain = "Project approved"
        struck = "~~Project approved~~"
        self.assertNotEqual(binding._normalize_text(plain), binding._normalize_text(struck))
        self.assertNotEqual(stage_contract._normalize_text(plain), stage_contract._normalize_text(struck))
        self.assertEqual(binding._normalize_text(struck), struck)
        self.assertEqual(stage_contract._normalize_text(struck), struck)

    def test_html_deletion_tags_remain_semantically_distinct(self):
        plain = "Project approved"
        for deleted in ("<del>Project approved</del>", "<s>Project approved</s>"):
            self.assertNotEqual(binding._normalize_text(plain), binding._normalize_text(deleted))
            self.assertNotEqual(stage_contract._normalize_text(plain), stage_contract._normalize_text(deleted))
            self.assertEqual(binding._normalize_text(deleted), deleted)
            self.assertEqual(stage_contract._normalize_text(deleted), deleted)

    def test_comparison_expressions_survive_markup_normalization(self):
        self.assertEqual(
            binding._normalize_text("loss <0.7% and density >300 kW/L"),
            "loss <0.7% and density >300 kW/L",
        )
        self.assertEqual(
            stage_contract._normalize_text("loss <70% and density >300 kW/L"),
            "loss <70% and density >300 kW/L",
        )
        self.assertNotEqual(
            binding._normalize_text("loss <0.7% and density >300 kW/L"),
            binding._normalize_text("loss <70% and density >300 kW/L"),
        )

    def test_known_html_presentation_tags_are_still_normalized_out(self):
        self.assertEqual(
            binding._normalize_text("<strong>same fact</strong>"),
            "same fact",
        )
        self.assertEqual(
            stage_contract._normalize_text("<em>same fact</em>"),
            "same fact",
        )

    def test_empty_intermediate_values_fall_back_to_earlier_nonempty_copy(self):
        row = row06(
            content_enrichment_audit=audit(
                [], no_change=True, supported=4,
                reason="0.5 and 0.4 empty values cannot mask Stage C.",
                bind_dimensions=True,
            ),
        )
        chain = rows(row)
        chain["0.5"][0]["fact"] = ""
        chain["0.4"][0]["fact"] = None
        binding.validate_content_enrichment_delta(
            chain, "insert[0]", operation_card=VISIBLE,
        )

    def test_operation_copy_must_match_audited_06_copy(self):
        row = row06(
            fact=NEW_DENSE_FACT,
            content_enrichment_audit=audit(["fact"]),
        )
        with self.assertRaisesRegex(binding.Blocked, "applied operation visible copy"):
            binding.validate_content_enrichment_delta(
                rows(row), "insert[0]", operation_card=VISIBLE,
            )

    def test_changed_string_without_supported_deep_summary_dimension_is_blocked(self):
        empty_density = {
            "status": "PASS",
            "dimensions": {name: False for name in binding.DENSITY_DIMENSIONS},
            "supported_dimension_count": 0,
            "evidence_notes": "Only terminology changed.",
            "dimension_evidence": {},
        }
        row = row06(
            fact="terminology-only wording",
            content_enrichment_audit={
                "baseline_strategy": binding.CONTENT_BASELINE_STRATEGY,
                "changed_fields": ["fact"],
                "no_change_required": False,
                "no_change_reason": "",
                "density_audit": empty_density,
            },
        )
        with self.assertRaisesRegex(binding.Blocked, "at least one evidence-supported"):
            binding.validate_content_enrichment_delta(
                rows(row), "insert[0]",
                operation_card={**VISIBLE, "fact": "terminology-only wording"},
            )

    def test_changed_delta_dimension_must_bind_to_an_actually_changed_field(self):
        row = row06(
            sub="changed sub",
            content_enrichment_audit=audit(["sub"]),
        )
        # Default helper maps supported dimensions only to fact, which is unchanged here.
        with self.assertRaisesRegex(binding.Blocked, "actually changed governed field"):
            binding.validate_content_enrichment_delta(
                rows(row), "insert[0]",
                operation_card={**VISIBLE, "sub": "changed sub"},
            )

    def test_terminology_only_synonym_does_not_count_as_substantive_dimension_delta(self):
        prior = "Production rose in 2026"
        current = "Production increased in 2026"
        row = row06(
            fact=current,
            content_enrichment_audit=audit_for_dimensions(["fact"], ["changed_state"]),
        )
        chain = rows(row)
        chain["C"][0]["fact"] = prior
        chain["0.4"][0]["fact"] = prior
        chain["0.5"][0]["fact"] = prior
        with self.assertRaisesRegex(binding.Blocked, "claimed but not expressed|machine-detectable newly added/deepened"):
            binding.validate_content_enrichment_delta(
                chain, "update[0]",
                operation_card={**VISIBLE, "fact": current},
            )

    def test_prior_state_synonyms_share_one_canonical_marker(self):
        prior = "Project was previously planned"
        current = "Project was formerly planned"
        row = row06(
            fact=current,
            content_enrichment_audit=audit_for_dimensions(["fact"], ["prior_state"]),
        )
        chain = rows(row)
        for stage in ("C", "0.4", "0.5"):
            chain[stage][0]["fact"] = prior
        with self.assertRaisesRegex(binding.Blocked, "machine-detectable newly added/deepened"):
            binding.validate_content_enrichment_delta(
                chain, "update[0]",
                operation_card={**VISIBLE, "fact": current},
            )

    def test_commencement_synonyms_share_one_canonical_marker(self):
        prior = "Production began in 2026"
        current = "Production started in 2026"
        row = row06(
            fact=current,
            content_enrichment_audit=audit_for_dimensions(["fact"], ["changed_state"]),
        )
        chain = rows(row)
        for stage in ("C", "0.4", "0.5"):
            chain[stage][0]["fact"] = prior
        with self.assertRaisesRegex(binding.Blocked, "machine-detectable newly added/deepened"):
            binding.validate_content_enrichment_delta(
                chain, "update[0]",
                operation_card={**VISIBLE, "fact": current},
            )

    def test_large_grouped_numeric_anchor_canonicalizes_full_number(self):
        self.assertEqual(
            binding._signal_values("quantitative_anchor", "Capacity is 1,000,000 MW"),
            binding._signal_values("quantitative_anchor", "Capacity is 1000000 MW"),
        )
        self.assertIn(
            "1000000 mw",
            binding._signal_values("quantitative_anchor", "Capacity is 1,000,000 MW"),
        )

    def test_quantitative_signal_preserves_number_unit_pair_with_spacing(self):
        self.assertIn("10 mw", binding._signal_values("quantitative_anchor", "The project is 10 MW"))
        self.assertIn("10 mwh", binding._signal_values("quantitative_anchor", "The project is 10 MW / 10 MWh"))
        self.assertNotEqual(
            binding._signal_values("quantitative_anchor", "The project is 10 MW"),
            binding._signal_values("quantitative_anchor", "The project is 10 MW / 10 MWh"),
        )

    def test_added_energy_capacity_anchor_qualifies(self):
        prior = "The project is 10 MW"
        current = "The project is 10 MW / 10 MWh"
        row = row06(
            fact=current,
            content_enrichment_audit=audit_for_dimensions(["fact"], ["quantitative_anchor"]),
        )
        chain = rows(row)
        for stage in ("C", "0.4", "0.5"):
            chain[stage][0]["fact"] = prior
        binding.validate_content_enrichment_delta(
            chain, "update[0]",
            operation_card={**VISIBLE, "fact": current},
        )

    def test_numeric_formatting_variants_share_canonical_anchor(self):
        self.assertEqual(
            binding._signal_values("quantitative_anchor", "Capacity is 10 MW and 1,000 MWh"),
            binding._signal_values("quantitative_anchor", "Capacity is 10.0 MW and 1000 MWh"),
        )

    def test_numeric_formatting_only_change_does_not_qualify(self):
        prior = "Capacity is 10 MW"
        current = "Capacity is 10.0 MW"
        row = row06(
            fact=current,
            content_enrichment_audit=audit_for_dimensions(["fact"], ["quantitative_anchor"]),
        )
        chain = rows(row)
        for stage in ("C", "0.4", "0.5"):
            chain[stage][0]["fact"] = prior
        with self.assertRaisesRegex(binding.Blocked, "machine-detectable newly added/deepened"):
            binding.validate_content_enrichment_delta(
                chain, "update[0]",
                operation_card={**VISIBLE, "fact": current},
            )

    def test_relocating_existing_signal_between_fields_is_not_enrichment(self):
        upstream_fact = "Commercial production started in 2026 at 2 GWh"
        upstream_sub = "Project overview"
        current_fact = upstream_sub
        current_sub = upstream_fact
        focused = audit_for_dimensions(["sub", "fact"], ["changed_state"])
        focused["density_audit"]["dimension_evidence"]["changed_state"]["fields"] = ["sub"]
        row = row06(
            sub=current_sub,
            fact=current_fact,
            content_enrichment_audit=focused,
        )
        chain = rows(row)
        chain["C"][0].update({"sub": upstream_sub, "fact": upstream_fact})
        chain["0.4"][0]["fact"] = upstream_fact
        chain["0.5"][0]["fact"] = upstream_fact
        with self.assertRaisesRegex(binding.Blocked, "whole upstream governed copy"):
            binding.validate_content_enrichment_delta(
                chain, "update[0]",
                operation_card={**VISIBLE, "sub": current_sub, "fact": current_fact},
            )

    def test_zero_delta_claimed_dimensions_must_exist_in_mapped_text(self):
        placeholder = {
            "sub": "s", "gate": "g", "fact": "f", "implication": ["i"],
        }
        row = row06(
            **placeholder,
            content_enrichment_audit=audit(
                [], no_change=True, supported=4,
                reason="Placeholder text must not satisfy density.",
                bind_dimensions=True,
            ),
        )
        chain = rows(row)
        chain["C"][0].update(placeholder)
        chain["0.4"][0]["fact"] = "f"
        chain["0.5"][0]["fact"] = "f"
        with self.assertRaisesRegex(binding.Blocked, "claimed but not expressed"):
            binding.validate_content_enrichment_delta(
                chain, "insert[0]", operation_card=placeholder,
            )

    def test_explicit_sufficient_density_no_change_exception_passes_with_bound_dimension_evidence(self):
        row = row06(
            content_enrichment_audit=audit(
                [], no_change=True, supported=4,
                reason="Upstream copy already expresses the verified state, number and boundary.",
                bind_dimensions=True,
            ),
        )
        binding.validate_content_enrichment_delta(
            rows(row), "insert[0]", operation_card=VISIBLE,
        )

    def test_planned_production_does_not_satisfy_changed_state(self):
        planned = (
            "Previously, planned production of 10 MW remains subject to approval "
            "because supply costs may rise."
        )
        focused = audit(
            [], no_change=True, supported=5,
            reason="Planned production is not a realized current-state change.",
            bind_dimensions=True,
        )
        row = row06(fact=planned, content_enrichment_audit=focused)
        chain = rows(row)
        chain["C"][0]["fact"] = planned
        chain["0.4"][0]["fact"] = planned
        chain["0.5"][0]["fact"] = planned
        with self.assertRaisesRegex(binding.Blocked, "changed_state.*claimed but not expressed|claimed but not expressed"):
            binding.validate_content_enrichment_delta(
                chain, "insert[0]",
                operation_card={**VISIBLE, "fact": planned},
            )

    def test_zero_delta_weak_density_is_blocked(self):
        row = row06(
            content_enrichment_audit=audit(
                [], no_change=True, supported=3,
                reason="Claims to be sufficient.",
                bind_dimensions=True,
            ),
        )
        with self.assertRaisesRegex(binding.Blocked, "at least four"):
            binding.validate_content_enrichment_delta(rows(row), "insert[0]")

    def test_zero_delta_self_declared_dimensions_without_bindings_are_blocked(self):
        row = row06(
            content_enrichment_audit=audit(
                [], no_change=True, supported=4,
                reason="Claims to be sufficient.",
                bind_dimensions=False,
            ),
        )
        with self.assertRaisesRegex(binding.Blocked, "dimension_evidence"):
            binding.validate_content_enrichment_delta(rows(row), "insert[0]")

    def test_dimension_evidence_cannot_inject_new_06_only_source(self):
        injected = audit(
            [], no_change=True, supported=4,
            reason="Injected source must not authorize unchanged content.",
            bind_dimensions=True,
        )
        for entry in injected["density_audit"]["dimension_evidence"].values():
            entry["evidence_refs"] = ["INJECTED"]
        row = row06(
            fact_sources=[{"source_id": "INJECTED", "source_url": "https://example.test/injected"}],
            content_enrichment_audit=injected,
        )
        with self.assertRaisesRegex(binding.Blocked, "unbound evidence refs"):
            binding.validate_content_enrichment_delta(rows(row), "insert[0]")

    def test_changed_delta_cannot_use_06_only_source_when_upstream_has_no_evidence_token(self):
        row = row06(
            fact="changed fact",
            fact_sources=[{"source_id": "SRC1", "source_url": "https://example.test/source"}],
            content_enrichment_audit=audit(["fact"]),
        )
        chain = rows(row)
        chain["B"][0].pop("fact_sources", None)
        chain["C"][0].pop("fact_sources", None)
        with self.assertRaisesRegex(binding.Blocked, "bound upstream source evidence support"):
            binding.validate_content_enrichment_delta(
                chain, "update[0]",
                operation_card={**VISIBLE, "fact": "changed fact"},
            )

    def test_checked_not_used_source_cannot_support_fact_dimension(self):
        row = row06(
            fact=NEW_DENSE_FACT,
            content_enrichment_audit=audit(["fact"]),
        )
        chain = rows(row)
        unsupported = {
            "source_id": "SRC1",
            "source_url": "https://example.test/source",
            "role": "checked_not_used_for_visible_claims",
            "visible_claim_support": [],
        }
        chain["B"][0]["fact_sources"] = [unsupported]
        chain["C"][0]["fact_sources"] = [unsupported]
        with self.assertRaisesRegex(binding.Blocked, "bound upstream source evidence support|do not support mapped visible fields"):
            binding.validate_content_enrichment_delta(
                chain, "update[0]",
                operation_card={**VISIBLE, "fact": NEW_DENSE_FACT},
            )

    def test_claim_coverage_cannot_restore_explicitly_excluded_source(self):
        row = row06(
            fact=NEW_DENSE_FACT,
            content_enrichment_audit=audit(["fact"]),
        )
        chain = rows(row)
        excluded = {
            "source_id": "SRC1",
            "source_url": "https://example.test/source",
            "role": "checked_not_used_for_visible_claims",
            "visible_claim_support": [],
        }
        for stage in ("B", "C"):
            chain[stage][0]["fact_sources"] = [excluded]
            chain[stage][0]["claim_source_coverage"] = {
                "visible_fact": {"supported_by_source_ids": ["SRC1"]}
            }
        with self.assertRaisesRegex(
            binding.Blocked,
            "bound upstream source evidence support|unbound evidence refs|do not support mapped visible fields",
        ):
            binding.validate_content_enrichment_delta(
                chain, "update[0]",
                operation_card={**VISIBLE, "fact": NEW_DENSE_FACT},
            )

    def test_explicit_source_field_support_is_enforced(self):
        row = row06(
            fact=NEW_DENSE_FACT,
            content_enrichment_audit=audit(["fact"]),
        )
        chain = rows(row)
        source = {
            "source_id": "SRC1",
            "source_url": "https://example.test/source",
            "visible_claim_support": ["sub"],
        }
        chain["B"][0]["fact_sources"] = [source]
        chain["C"][0]["fact_sources"] = [source]
        with self.assertRaisesRegex(binding.Blocked, "do not support mapped visible fields"):
            binding.validate_content_enrichment_delta(
                chain, "update[0]",
                operation_card={**VISIBLE, "fact": NEW_DENSE_FACT},
            )

    def test_canonical_visible_supports_field_limits_ledger_scope(self):
        row = row06(
            fact=NEW_DENSE_FACT,
            content_enrichment_audit=audit(["fact"]),
        )
        chain = rows(row)
        ledger = [{
            "source_id": "SRC1",
            "source_url": "https://example.test/source",
            "outcome": "used_in_fact_sources",
            "visible_supports": ["sub"],
        }]
        chain["B"][0].pop("fact_sources", None)
        chain["C"][0].pop("fact_sources", None)
        chain["B"][0]["source_discovery_ledger"] = ledger
        chain["C"][0]["source_discovery_ledger"] = ledger
        with self.assertRaisesRegex(binding.Blocked, "do not support mapped visible fields"):
            binding.validate_content_enrichment_delta(
                chain, "update[0]",
                operation_card={**VISIBLE, "fact": NEW_DENSE_FACT},
            )

    def test_nearest_stage_exclusion_overrides_older_positive_evidence(self):
        row = row06(
            fact=NEW_DENSE_FACT,
            content_enrichment_audit=audit(["fact"]),
        )
        chain = rows(row)
        chain["0.5"][0]["fact_sources"] = [{
            "source_id": "SRC1",
            "source_url": "https://example.test/source",
            "role": "checked_not_used_for_visible_claims",
            "visible_claim_support": [],
        }]
        with self.assertRaisesRegex(
            binding.Blocked,
            "bound upstream source evidence support|unbound evidence refs|do not support mapped visible fields",
        ):
            binding.validate_content_enrichment_delta(
                chain, "update[0]",
                operation_card={**VISIBLE, "fact": NEW_DENSE_FACT},
            )

    def test_stage_checker_honors_canonical_visible_supports_scope(self):
        item = row06(
            fact=NEW_DENSE_FACT,
            content_enrichment_audit=audit(["fact"]),
            fact_sources=[],
            source_discovery_ledger=[{
                "source_id": "SRC1",
                "source_url": "https://example.test/source",
                "outcome": "used_in_fact_sources",
                "visible_supports": ["sub"],
            }],
        )
        findings = stage_contract._content_enrichment_audit_findings(item, "SPEC")
        self.assertTrue(any(
            "do not support the mapped visible fields" in x.get("message", "")
            for x in findings
        ))

    def test_added_quantitative_signal_must_exist_in_referenced_upstream_evidence(self):
        prior = "Capacity is 10 MW"
        current = "Capacity is 999 MW"
        focused = audit_for_dimensions(["fact"], ["quantitative_anchor"])
        row = row06(
            fact=current,
            fact_sources=[{
                "source_id": "SRC1",
                "source_url": "https://example.test/source",
                "source_quote": "The project has a capacity of 10 MW.",
            }],
            content_enrichment_audit=focused,
        )
        chain = rows(row)
        source_10 = {
            "source_id": "SRC1",
            "source_url": "https://example.test/source",
            "source_quote": "The project has a capacity of 10 MW.",
        }
        for stage in ("B", "C"):
            chain[stage][0]["fact_sources"] = [source_10]
        for stage in ("C", "0.4", "0.5"):
            chain[stage][0]["fact"] = prior
        with self.assertRaisesRegex(binding.Blocked, "not grounded.*source quote/claim evidence"):
            binding.validate_content_enrichment_delta(
                chain, "update[0]",
                operation_card={**VISIBLE, "fact": current, "fact_sources": [source_10]},
            )

    def test_negated_changed_state_markers_do_not_count_as_realized_state(self):
        text = (
            "Previously planned 10 MW project has not started and is not approved "
            "because supply costs may rise."
        )
        focused = audit(
            [], no_change=True, supported=5,
            reason="Negated execution markers are not realized current state.",
            bind_dimensions=True,
        )
        row = row06(fact=text, content_enrichment_audit=focused)
        chain = rows(row)
        for stage in ("C", "0.4", "0.5"):
            chain[stage][0]["fact"] = text
        with self.assertRaisesRegex(binding.Blocked, "changed_state.*claimed but not expressed|claimed but not expressed"):
            binding.validate_content_enrichment_delta(
                chain, "insert[0]",
                operation_card={**VISIBLE, "fact": text},
            )

    def test_leading_zero_numeric_anchor_is_canonicalized(self):
        self.assertEqual(
            binding._signal_values("quantitative_anchor", "Capacity is 10 MW"),
            binding._signal_values("quantitative_anchor", "Capacity is 010 MW"),
        )

    def test_leading_zero_numeric_formatting_only_change_does_not_qualify(self):
        prior = "Capacity is 10 MW"
        current = "Capacity is 010 MW"
        row = row06(
            fact=current,
            content_enrichment_audit=audit_for_dimensions(["fact"], ["quantitative_anchor"]),
        )
        chain = rows(row)
        for stage in ("C", "0.4", "0.5"):
            chain[stage][0]["fact"] = prior
        with self.assertRaisesRegex(binding.Blocked, "machine-detectable newly added/deepened"):
            binding.validate_content_enrichment_delta(
                chain, "update[0]",
                operation_card={**VISIBLE, "fact": current},
            )

    def test_malformed_locked_base_sha_fails_closed(self):
        locked, declared, error = stage_contract._artifact_locked_prompt_06_version({
            "base_main_commit_sha": "abc123",
            "prompt_provenance": {"prompt_version": "PROMPT_0_6_V4_20260901"},
        })
        self.assertIsNone(locked)
        self.assertEqual(declared, "PROMPT_0_6_V4_20260901")
        self.assertIn("malformed", error)

    def test_materialized_operation_must_preserve_bound_evidence_package(self):
        row = row06(
            fact=NEW_DENSE_FACT,
            content_enrichment_audit=audit(["fact"]),
        )
        operation = {**VISIBLE, "fact": NEW_DENSE_FACT}
        operation.pop("fact_sources", None)
        with self.assertRaisesRegex(binding.Blocked, "does not preserve bound evidence ref SRC1"):
            binding.validate_content_enrichment_delta(
                rows(row), "update[0]", operation_card=operation,
            )

    def test_zero_delta_dimensions_must_be_grounded_in_referenced_evidence(self):
        unsupported_source = {
            "source_id": "SRC1",
            "source_url": "https://example.test/source",
            "source_quote": "This quote discusses an unrelated corporate announcement.",
        }
        row = row06(
            fact_sources=[unsupported_source],
            content_enrichment_audit=audit(
                [], no_change=True, supported=4,
                reason="Visible copy cannot self-ground without matching source evidence.",
                bind_dimensions=True,
            ),
        )
        chain = rows(row)
        for stage in ("B", "C"):
            chain[stage][0]["fact_sources"] = [unsupported_source]
        with self.assertRaisesRegex(binding.Blocked, "zero-delta.*not grounded"):
            binding.validate_content_enrichment_delta(
                chain, "insert[0]",
                operation_card={**VISIBLE, "fact_sources": [unsupported_source]},
            )

    def test_materialized_operation_must_preserve_quote_and_verification_status(self):
        verified_source = {
            "source_id": "SRC1",
            "source_url": "https://example.test/source",
            "source_quote": SOURCE_QUOTE,
            "source_quote_status": "body_quote_verified",
            "fetched": True,
            "resolved_article_matches_quote": True,
        }
        row = row06(
            fact=NEW_DENSE_FACT,
            fact_sources=[verified_source],
            content_enrichment_audit=audit(["fact"]),
        )
        chain = rows(row)
        for stage in ("B", "C"):
            chain[stage][0]["fact_sources"] = [verified_source]
        stripped_source = {
            "source_id": "SRC1",
            "source_url": "https://example.test/source",
            "visible_claim_support": ["fact"],
        }
        with self.assertRaisesRegex(binding.Blocked, "does not preserve.*quote/claim.*verification-status"):
            binding.validate_content_enrichment_delta(
                chain, "update[0]",
                operation_card={
                    **VISIBLE,
                    "fact": NEW_DENSE_FACT,
                    "fact_sources": [stripped_source],
                },
            )

    def test_added_governed_signal_outside_declared_dimension_map_is_blocked(self):
        prior = "Capacity is 10 MW"
        current = "Capacity is 20 MW and the project was canceled"
        source = {
            "source_id": "SRC1",
            "source_url": "https://example.test/source",
            "source_quote": "Capacity is 20 MW.",
            "source_quote_status": "body_quote_verified",
            "fetched": True,
        }
        row = row06(
            fact=current,
            fact_sources=[source],
            content_enrichment_audit=audit_for_dimensions(
                ["fact"], ["quantitative_anchor"]
            ),
        )
        chain = rows(row)
        for stage in ("B", "C"):
            chain[stage][0]["fact_sources"] = [source]
        for stage in ("C", "0.4", "0.5"):
            chain[stage][0]["fact"] = prior
        with self.assertRaisesRegex(binding.Blocked, "introduces undeclared governed changed_state"):
            binding.validate_content_enrichment_delta(
                chain, "update[0]",
                operation_card={**VISIBLE, "fact": current, "fact_sources": [source]},
            )

    def test_enrichment_cannot_delete_verified_upstream_quantitative_signal(self):
        prior = "Capacity is 10 MW / 20 MWh"
        current = "Capacity is 10 MW and the project was approved"
        source = {
            "source_id": "SRC1",
            "source_url": "https://example.test/source",
            "source_quote": "The project was approved; capacity remains 10 MW / 20 MWh.",
            "source_quote_status": "body_quote_verified",
            "fetched": True,
        }
        row = row06(
            fact=current,
            fact_sources=[source],
            content_enrichment_audit=audit_for_dimensions(
                ["fact"], ["changed_state"]
            ),
        )
        chain = rows(row)
        for stage in ("B", "C"):
            chain[stage][0]["fact_sources"] = [source]
        for stage in ("C", "0.4", "0.5"):
            chain[stage][0]["fact"] = prior
        with self.assertRaisesRegex(binding.Blocked, "deletes verified upstream quantitative_anchor signals"):
            binding.validate_content_enrichment_delta(
                chain, "update[0]",
                operation_card={**VISIBLE, "fact": current, "fact_sources": [source]},
            )

    def test_evidence_backed_modality_deepening_qualifies(self):
        prior = "The project may be delayed"
        current = "The project is delayed"
        source = {
            "source_id": "SRC1",
            "source_url": "https://example.test/source",
            "source_quote": "The project is delayed.",
            "source_quote_status": "body_quote_verified",
            "fetched": True,
        }
        row = row06(
            fact=current,
            fact_sources=[source],
            content_enrichment_audit=audit_for_dimensions(
                ["fact"], ["changed_state"]
            ),
        )
        chain = rows(row)
        for stage in ("B", "C"):
            chain[stage][0]["fact_sources"] = [source]
        for stage in ("C", "0.4", "0.5"):
            chain[stage][0]["fact"] = prior
        binding.validate_content_enrichment_delta(
            chain, "update[0]",
            operation_card={**VISIBLE, "fact": current, "fact_sources": [source]},
        )

    def test_spelled_magnitude_and_currency_code_are_part_of_quantitative_identity(self):
        million = binding._signal_values(
            "quantitative_anchor", "Investment is 10 million USD"
        )
        billion = binding._signal_values(
            "quantitative_anchor", "Investment is 10 billion USD"
        )
        self.assertIn("10 m usd", million)
        self.assertIn("10 bn usd", billion)
        self.assertNotEqual(million, billion)

    def test_spelled_magnitude_mismatch_cannot_ground_enrichment(self):
        prior = "Investment is 5 million USD"
        current = "Investment is 10 billion USD"
        source = {
            "source_id": "SRC1",
            "source_url": "https://example.test/source",
            "source_quote": "Investment is 10 million USD.",
            "source_quote_status": "body_quote_verified",
            "fetched": True,
        }
        row = row06(
            fact=current,
            fact_sources=[source],
            content_enrichment_audit=audit_for_dimensions(
                ["fact"], ["quantitative_anchor"]
            ),
        )
        chain = rows(row)
        for stage in ("B", "C"):
            chain[stage][0]["fact_sources"] = [source]
        for stage in ("C", "0.4", "0.5"):
            chain[stage][0]["fact"] = prior
        with self.assertRaisesRegex(binding.Blocked, "not grounded.*(?:nearest-stage|source quote/claim evidence)"):
            binding.validate_content_enrichment_delta(
                chain, "update[0]",
                operation_card={**VISIBLE, "fact": current, "fact_sources": [source]},
            )

    def test_grounding_text_uses_nearest_authoritative_stage_only(self):
        prior = "Capacity is 10 MW"
        current = "Capacity is 999 MW"
        source_near = {
            "source_id": "SRC1",
            "source_url": "https://example.test/source",
            "source_quote": "Capacity is 10 MW.",
            "source_quote_status": "body_quote_verified",
            "fetched": True,
        }
        source_stale = {
            "source_id": "SRC1",
            "source_url": "https://example.test/source",
            "source_quote": "Capacity is 999 MW.",
            "source_quote_status": "body_quote_verified",
            "fetched": True,
        }
        row = row06(
            fact=current,
            fact_sources=[source_near],
            content_enrichment_audit=audit_for_dimensions(
                ["fact"], ["quantitative_anchor"]
            ),
        )
        chain = rows(row)
        chain["0.5"][0]["fact_sources"] = [source_near]
        chain["C"][0]["fact_sources"] = [source_stale]
        chain["B"][0]["fact_sources"] = [source_stale]
        for stage in ("C", "0.4", "0.5"):
            chain[stage][0]["fact"] = prior
        with self.assertRaisesRegex(binding.Blocked, "not grounded.*(?:nearest-stage|source quote/claim evidence)"):
            binding.validate_content_enrichment_delta(
                chain, "update[0]",
                operation_card={**VISIBLE, "fact": current, "fact_sources": [source_near]},
            )

    def test_construction_noun_with_following_negation_is_not_realized_changed_state(self):
        text = (
            "Previously, construction has not started for the planned 10 MW project "
            "because supply costs may rise."
        )
        focused = audit(
            [], no_change=True, supported=5,
            reason="Negated construction noun is not a realized current state.",
            bind_dimensions=True,
        )
        source = {
            "source_id": "SRC1",
            "source_url": "https://example.test/source",
            "source_quote": text,
            "source_quote_status": "body_quote_verified",
            "fetched": True,
        }
        row = row06(
            fact=text,
            fact_sources=[source],
            content_enrichment_audit=focused,
        )
        chain = rows(row)
        for stage in ("B", "C"):
            chain[stage][0]["fact_sources"] = [source]
        for stage in ("C", "0.4", "0.5"):
            chain[stage][0]["fact"] = text
        with self.assertRaisesRegex(binding.Blocked, "changed_state.*claimed but not expressed|claimed but not expressed"):
            binding.validate_content_enrichment_delta(
                chain, "insert[0]",
                operation_card={**VISIBLE, "fact": text, "fact_sources": [source]},
            )

    def test_stage_checker_requires_dimension_grounding_in_referenced_quote(self):
        unrelated = {
            "source_id": "SRC1",
            "source_url": "https://example.test/source",
            "source_quote": "Unrelated corporate announcement.",
            "source_quote_status": "body_quote_verified",
            "fetched": True,
        }
        item = row06(
            fact_sources=[unrelated],
            content_enrichment_audit=audit(
                [], no_change=True, supported=4,
                reason="Standalone must ground dimensions in evidence text.",
                bind_dimensions=True,
            ),
        )
        findings = stage_contract._content_enrichment_audit_findings(item, "SPEC")
        self.assertTrue(any(
            "not grounded in the referenced quote/claim evidence" in x.get("message", "")
            for x in findings
        ))

    def test_explicitly_unverified_quote_cannot_ground_enrichment(self):
        prior = "Capacity is 10 MW"
        current = "Capacity is 20 MW"
        failed = {
            "source_id": "SRC1",
            "source_url": "https://example.test/source",
            "source_quote": "Capacity is 20 MW.",
            "source_quote_status": "fetch_failed",
            "fetched": False,
        }
        row = row06(
            fact=current,
            fact_sources=[failed],
            content_enrichment_audit=audit_for_dimensions(
                ["fact"], ["quantitative_anchor"]
            ),
        )
        chain = rows(row)
        for stage in ("B", "C"):
            chain[stage][0]["fact_sources"] = [failed]
        for stage in ("C", "0.4", "0.5"):
            chain[stage][0]["fact"] = prior
        with self.assertRaisesRegex(binding.Blocked, "not grounded.*(?:nearest-stage|source quote/claim evidence)"):
            binding.validate_content_enrichment_delta(
                chain, "update[0]",
                operation_card={**VISIBLE, "fact": current, "fact_sources": [failed]},
            )

    def test_repeated_evidence_backed_status_occurrence_qualifies(self):
        prior = "The site permit was approved"
        current = (
            "The site permit was approved; project financing was approved"
        )
        source = {
            "source_id": "SRC1",
            "source_url": "https://example.test/source",
            "source_quote": current + ".",
            "source_quote_status": "body_quote_verified",
            "fetched": True,
        }
        row = row06(
            fact=current,
            fact_sources=[source],
            content_enrichment_audit=audit_for_dimensions(
                ["fact"], ["changed_state"]
            ),
        )
        chain = rows(row)
        for stage in ("B", "C"):
            chain[stage][0]["fact_sources"] = [source]
        for stage in ("C", "0.4", "0.5"):
            chain[stage][0]["fact"] = prior
        binding.validate_content_enrichment_delta(
            chain, "update[0]",
            operation_card={**VISIBLE, "fact": current, "fact_sources": [source]},
        )

    def test_duplicate_evidence_refs_cannot_double_count_one_quote(self):
        prior = "The site permit was approved"
        current = "The site permit was approved; project financing was approved"
        source = {
            "source_id": "SRC1",
            "source_url": "https://example.test/source",
            "source_quote": "Project financing was approved.",
            "source_quote_status": "body_quote_verified",
            "fetched": True,
        }
        focused = audit_for_dimensions(["fact"], ["changed_state"])
        focused["density_audit"]["dimension_evidence"]["changed_state"]["evidence_refs"] = [
            "SRC1", " SRC1 "
        ]
        row = row06(
            fact=current,
            fact_sources=[source],
            content_enrichment_audit=focused,
        )
        chain = rows(row)
        for stage in ("B", "C"):
            chain[stage][0]["fact_sources"] = [source]
        for stage in ("C", "0.4", "0.5"):
            chain[stage][0]["fact"] = prior
        with self.assertRaisesRegex(binding.Blocked, "evidence_refs must be unique after normalization"):
            binding.validate_content_enrichment_delta(
                chain, "update[0]",
                operation_card={**VISIBLE, "fact": current, "fact_sources": [source]},
            )

    def test_nearest_stage_duplicate_token_packages_are_rejected_as_ambiguous(self):
        prior = "Capacity is 10 MW"
        current = "Capacity is 20 MW"
        source_20 = {
            "source_id": "SRC1",
            "source_url": "https://example.test/source",
            "source_quote": "Capacity is 20 MW.",
            "source_quote_status": "body_quote_verified",
            "fetched": True,
        }
        source_10 = {
            "source_id": "SRC1",
            "source_url": "https://example.test/source",
            "source_quote": "Capacity is 10 MW.",
            "source_quote_status": "body_quote_verified",
            "fetched": True,
        }
        row = row06(
            fact=current,
            fact_sources=[source_20],
            content_enrichment_audit=audit_for_dimensions(
                ["fact"], ["quantitative_anchor"]
            ),
        )
        chain = rows(row)
        chain["0.5"][0]["fact_sources"] = [source_20, source_10]
        for stage in ("C", "0.4", "0.5"):
            chain[stage][0]["fact"] = prior
        with self.assertRaisesRegex(binding.Blocked, "evidence token SRC1 is ambiguous"):
            binding.validate_content_enrichment_delta(
                chain, "update[0]",
                operation_card={**VISIBLE, "fact": current, "fact_sources": [source_20]},
            )

    def test_clause_level_negation_blocks_distant_not_started(self):
        text = (
            "Previously, the planned 10 MW project has not as of this week started "
            "because supply costs may rise."
        )
        source = {
            "source_id": "SRC1",
            "source_url": "https://example.test/source",
            "source_quote": text,
            "source_quote_status": "body_quote_verified",
            "fetched": True,
        }
        row = row06(
            fact=text,
            fact_sources=[source],
            content_enrichment_audit=audit(
                [], no_change=True, supported=5,
                reason="Clause-level negation prevents realized changed-state.",
                bind_dimensions=True,
            ),
        )
        chain = rows(row)
        for stage in ("B", "C"):
            chain[stage][0]["fact_sources"] = [source]
        for stage in ("C", "0.4", "0.5"):
            chain[stage][0]["fact"] = text
        with self.assertRaisesRegex(binding.Blocked, "changed_state.*claimed but not expressed|claimed but not expressed"):
            binding.validate_content_enrichment_delta(
                chain, "insert[0]",
                operation_card={**VISIBLE, "fact": text, "fact_sources": [source]},
            )

    def test_quantitative_polarity_and_bounds_are_part_of_claim_identity(self):
        self.assertNotEqual(
            binding._signal_values("quantitative_anchor", "Capacity is -10 MW"),
            binding._signal_values("quantitative_anchor", "Capacity is 10 MW"),
        )
        self.assertNotEqual(
            binding._signal_values("quantitative_anchor", "Capacity is >20 MW"),
            binding._signal_values("quantitative_anchor", "Capacity is <20 MW"),
        )
        self.assertIn("-10 mw", binding._signal_values("quantitative_anchor", "Capacity is -10 MW"))
        self.assertIn(">20 mw", binding._signal_values("quantitative_anchor", "Capacity is >20 MW"))
        self.assertIn("<20 mw", binding._signal_values("quantitative_anchor", "Capacity is <20 MW"))

    def test_quantitative_polarity_mismatch_cannot_ground_enrichment(self):
        prior = "Capacity is 5 MW"
        current = "Capacity is -10 MW"
        positive = {
            "source_id": "SRC1",
            "source_url": "https://example.test/source",
            "source_quote": "Capacity is 10 MW.",
            "source_quote_status": "body_quote_verified",
            "fetched": True,
        }
        row = row06(
            fact=current,
            fact_sources=[positive],
            content_enrichment_audit=audit_for_dimensions(
                ["fact"], ["quantitative_anchor"]
            ),
        )
        chain = rows(row)
        for stage in ("B", "C"):
            chain[stage][0]["fact_sources"] = [positive]
        for stage in ("C", "0.4", "0.5"):
            chain[stage][0]["fact"] = prior
        with self.assertRaisesRegex(binding.Blocked, "not grounded.*(?:nearest-stage|source quote/claim evidence)"):
            binding.validate_content_enrichment_delta(
                chain, "update[0]",
                operation_card={**VISIBLE, "fact": current, "fact_sources": [positive]},
            )

    def test_factual_location_addition_outside_dimension_taxonomy_requires_grounding(self):
        prior = "Capacity is 10 MW"
        current = "Capacity is 20 MW at the Mars facility"
        source = {
            "source_id": "SRC1",
            "source_url": "https://example.test/source",
            "source_quote": "Capacity is 20 MW.",
            "source_quote_status": "body_quote_verified",
            "fetched": True,
        }
        row = row06(
            fact=current,
            fact_sources=[source],
            content_enrichment_audit=audit_for_dimensions(
                ["fact"], ["quantitative_anchor"]
            ),
        )
        chain = rows(row)
        for stage in ("B", "C"):
            chain[stage][0]["fact_sources"] = [source]
        for stage in ("C", "0.4", "0.5"):
            chain[stage][0]["fact"] = prior
        with self.assertRaisesRegex(binding.Blocked, "factual identity/location/predicate tokens not grounded"):
            binding.validate_content_enrichment_delta(
                chain, "update[0]",
                operation_card={**VISIBLE, "fact": current, "fact_sources": [source]},
            )

    def test_standalone_duplicate_evidence_refs_are_reported(self):
        item = row06(
            content_enrichment_audit=audit(
                [], no_change=True, supported=4,
                reason="Duplicate refs must not double-count evidence.",
                bind_dimensions=True,
            ),
        )
        item["content_enrichment_audit"]["density_audit"]["dimension_evidence"]["changed_state"]["evidence_refs"] = [
            "SRC1", " SRC1 "
        ]
        findings = stage_contract._content_enrichment_audit_findings(item, "SPEC")
        self.assertTrue(any(
            "duplicate evidence refs" in x.get("message", "")
            for x in findings
        ))

    def test_pending_review_quote_without_fetch_proof_cannot_ground(self):
        prior = "Capacity is 5 MW"
        current = "Capacity is 10 MW"
        pending = {
            "source_id": "SRC1",
            "source_url": "https://example.test/source",
            "source_quote": "Capacity is 10 MW.",
            "source_quote_status": "pending_review",
        }
        row = row06(
            fact=current,
            fact_sources=[pending],
            content_enrichment_audit=audit_for_dimensions(
                ["fact"], ["quantitative_anchor"]
            ),
        )
        chain = rows(row)
        for stage in ("B", "C"):
            chain[stage][0]["fact_sources"] = [pending]
        for stage in ("C", "0.4", "0.5"):
            chain[stage][0]["fact"] = prior
        with self.assertRaisesRegex(binding.Blocked, "not grounded|no preserved upstream quote/claim"):
            binding.validate_content_enrichment_delta(
                chain, "update[0]",
                operation_card={**VISIBLE, "fact": current, "fact_sources": [pending]},
            )

    def test_prefix_currency_code_is_part_of_quantitative_identity(self):
        usd = binding._signal_values(
            "quantitative_anchor", "Budget is USD 10 million"
        )
        eur = binding._signal_values(
            "quantitative_anchor", "Budget is EUR 10 million"
        )
        self.assertIn("10 m usd", usd)
        self.assertIn("10 m eur", eur)
        self.assertNotEqual(usd, eur)

    def test_prefix_currency_code_mismatch_cannot_ground_enrichment(self):
        prior = "Budget is USD 5 million"
        current = "Budget is USD 10 million"
        wrong = {
            "source_id": "SRC1",
            "source_url": "https://example.test/source",
            "source_quote": "Budget is EUR 10 million.",
            "source_quote_status": "body_quote_verified",
            "fetched": True,
        }
        row = row06(
            fact=current,
            fact_sources=[wrong],
            content_enrichment_audit=audit_for_dimensions(
                ["fact"], ["quantitative_anchor"]
            ),
        )
        chain = rows(row)
        for stage in ("B", "C"):
            chain[stage][0]["fact_sources"] = [wrong]
        for stage in ("C", "0.4", "0.5"):
            chain[stage][0]["fact"] = prior
        with self.assertRaisesRegex(binding.Blocked, "not grounded.*(?:nearest-stage|source quote/claim evidence)"):
            binding.validate_content_enrichment_delta(
                chain, "update[0]",
                operation_card={**VISIBLE, "fact": current, "fact_sources": [wrong]},
            )

    def test_lowercase_factual_predicate_addition_requires_grounding(self):
        prior = "Capacity is 10 MW"
        current = "Capacity is 20 MW and uses recycled feedstock"
        source = {
            "source_id": "SRC1",
            "source_url": "https://example.test/source",
            "source_quote": "Capacity is 20 MW.",
            "source_quote_status": "body_quote_verified",
            "fetched": True,
        }
        row = row06(
            fact=current,
            fact_sources=[source],
            content_enrichment_audit=audit_for_dimensions(
                ["fact"], ["quantitative_anchor"]
            ),
        )
        chain = rows(row)
        for stage in ("B", "C"):
            chain[stage][0]["fact_sources"] = [source]
        for stage in ("C", "0.4", "0.5"):
            chain[stage][0]["fact"] = prior
        with self.assertRaisesRegex(binding.Blocked, "predicate tokens not grounded"):
            binding.validate_content_enrichment_delta(
                chain, "update[0]",
                operation_card={**VISIBLE, "fact": current, "fact_sources": [source]},
            )

    def test_calendar_may_does_not_count_as_uncertainty(self):
        text = "Previously, commercial production started in May 2026"
        self.assertNotIn(
            "uncertain_conditional",
            binding._signal_values("boundary_or_uncertainty", text),
        )
        source = {
            "source_id": "SRC1",
            "source_url": "https://example.test/source",
            "source_quote": text,
            "source_quote_status": "body_quote_verified",
            "fetched": True,
        }
        focused = audit(
            [], no_change=True, supported=4,
            reason="Calendar month May must not manufacture uncertainty.",
            bind_dimensions=True,
        )
        row = row06(
            fact=text,
            fact_sources=[source],
            content_enrichment_audit=focused,
        )
        chain = rows(row)
        for stage in ("B", "C"):
            chain[stage][0]["fact_sources"] = [source]
        for stage in ("C", "0.4", "0.5"):
            chain[stage][0]["fact"] = text
        with self.assertRaisesRegex(binding.Blocked, "boundary_or_uncertainty.*claimed but not expressed|claimed but not expressed"):
            binding.validate_content_enrichment_delta(
                chain, "insert[0]",
                operation_card={**VISIBLE, "fact": text, "fact_sources": [source]},
            )

    def test_negation_scope_stops_at_independent_conjunct(self):
        text = "The permit was not approved in May and construction started in June"
        signals = binding._signal_values("changed_state", text)
        self.assertNotIn("approval", signals)
        self.assertIn("construction", signals)
        self.assertIn("commencement", signals)

    def test_multiline_markdown_wrapper_is_presentation_only(self):
        wrapped = "**Capacity is 10 MW\nand approved**"
        plain = "Capacity is 10 MW\nand approved"
        self.assertEqual(binding._normalize_text(wrapped), binding._normalize_text(plain))
        self.assertEqual(stage_contract._normalize_text(wrapped), stage_contract._normalize_text(plain))

    def test_factual_identity_deletion_is_blocked(self):
        prior = "Capacity is 10 MW at the Mars facility"
        current = "Capacity is 20 MW"
        source = {
            "source_id": "SRC1",
            "source_url": "https://example.test/source",
            "source_quote": "Capacity is 20 MW.",
            "source_quote_status": "body_quote_verified",
            "fetched": True,
        }
        row = row06(
            fact=current,
            fact_sources=[source],
            content_enrichment_audit=audit_for_dimensions(
                ["fact"], ["quantitative_anchor"]
            ),
        )
        chain = rows(row)
        for stage in ("B", "C"):
            chain[stage][0]["fact_sources"] = [source]
        for stage in ("C", "0.4", "0.5"):
            chain[stage][0]["fact"] = prior
        with self.assertRaisesRegex(binding.Blocked, "deletes verified upstream factual"):
            binding.validate_content_enrichment_delta(
                chain, "update[0]",
                operation_card={**VISIBLE, "fact": current, "fact_sources": [source]},
            )

    def test_modality_deepening_is_occurrence_aware(self):
        prior = "The project may be delayed; the permit is delayed"
        current = "The project is delayed; the permit is delayed"
        source = {
            "source_id": "SRC1",
            "source_url": "https://example.test/source",
            "source_quote": current + ".",
            "source_quote_status": "body_quote_verified",
            "fetched": True,
        }
        row = row06(
            fact=current,
            fact_sources=[source],
            content_enrichment_audit=audit_for_dimensions(
                ["fact"], ["changed_state"]
            ),
        )
        chain = rows(row)
        for stage in ("B", "C"):
            chain[stage][0]["fact_sources"] = [source]
        for stage in ("C", "0.4", "0.5"):
            chain[stage][0]["fact"] = prior
        binding.validate_content_enrichment_delta(
            chain, "update[0]",
            operation_card={**VISIBLE, "fact": current, "fact_sources": [source]},
        )

    def test_boolean_supported_dimension_count_is_rejected(self):
        one_dimension = {
            "status": "PASS",
            "dimensions": {
                "prior_state": False,
                "changed_state": True,
                "quantitative_anchor": False,
                "boundary_or_uncertainty": False,
                "transmission_path": False,
                "next_watchpoint": False,
            },
            "supported_dimension_count": True,
            "evidence_notes": "Malformed boolean count.",
            "dimension_evidence": {
                "changed_state": {"fields": ["fact"], "evidence_refs": ["SRC1"]}
            },
        }
        row = row06(
            fact="changed fact",
            content_enrichment_audit={
                "baseline_strategy": binding.CONTENT_BASELINE_STRATEGY,
                "changed_fields": ["fact"],
                "no_change_required": False,
                "no_change_reason": "",
                "density_audit": one_dimension,
            },
        )
        with self.assertRaisesRegex(binding.Blocked, "non-boolean integer"):
            binding.validate_content_enrichment_delta(rows(row), "insert[0]")

    def test_explicit_v4_artifact_is_backward_compatible(self):
        row = row06(
            prompt_provenance_0_6={"prompt_version": "PROMPT_0_6_V4_20260901"},
        )
        binding.validate_content_enrichment_delta(
            rows(row), "historical",
            locked_prompt_version="PROMPT_0_6_V4_20260901",
        )
        self.assertFalse(stage_contract._requires_v5_content_audit(
            row, locked_prompt_version="PROMPT_0_6_V4_20260901"
        ))

    def test_locked_v5_contract_cannot_be_spoofed_by_v4_row_provenance(self):
        row = row06(
            prompt_provenance_0_6={"prompt_version": "PROMPT_0_6_V4_20260901"},
        )
        with self.assertRaisesRegex(binding.Blocked, "does not match locked baseline"):
            binding.validate_content_enrichment_delta(
                rows(row), "new-run",
                locked_prompt_version="PROMPT_0_6_V5_20260919",
            )

    def test_stage_06_v5_contract_requires_structured_audit(self):
        item = row06()
        findings = stage_contract._content_enrichment_audit_findings(item, "SPEC")
        self.assertTrue(any(x.get("field") == "content_enrichment_audit" for x in findings))

    def test_stage_checker_rejects_declared_changed_field_without_visible_copy(self):
        item = row06(content_enrichment_audit=audit(["fact"]))
        item.pop("fact")
        findings = stage_contract._content_enrichment_audit_findings(item, "SPEC")
        self.assertTrue(any(
            x.get("field") == "content_enrichment_audit.changed_fields"
            and "fact" in (x.get("actual") or [])
            for x in findings
        ))

    def test_stage_checker_reports_unreadable_locked_prompt(self):
        locked, declared, error = stage_contract._artifact_locked_prompt_06_version({
            "base_main_commit_sha": "0" * 40,
            "prompt_provenance": {"prompt_version": "PROMPT_0_6_V4_20260901"},
        })
        self.assertIsNone(locked)
        self.assertEqual(declared, "PROMPT_0_6_V4_20260901")
        self.assertTrue(error)

    def test_stage_06_checker_enforces_no_change_invariants_and_dimension_binding(self):
        item = row06(
            content_enrichment_audit=audit(
                [], no_change=True, supported=4,
                reason="Already sufficiently deep.",
                bind_dimensions=True,
            ),
        )
        self.assertEqual(stage_contract._content_enrichment_audit_findings(item, "SPEC"), [])

        bad = row06(
            content_enrichment_audit=audit(
                [], no_change=False, supported=4,
                reason="",
                bind_dimensions=False,
            ),
        )
        findings = stage_contract._content_enrichment_audit_findings(bad, "SPEC")
        self.assertTrue(any(
            x.get("field") == "content_enrichment_audit.no_change_required"
            for x in findings
        ))

    def test_stage_checker_rejects_checked_not_used_source_for_fact_dimension(self):
        item = row06(
            content_enrichment_audit=audit_for_dimensions(["fact"], ["changed_state"]),
            fact_sources=[{
                "source_id": "SRC1",
                "source_url": "https://example.test/source",
                "role": "checked_not_used_for_visible_claims",
                "visible_claim_support": [],
            }],
        )
        findings = stage_contract._content_enrichment_audit_findings(item, "SPEC")
        self.assertTrue(any(
            "do not support the mapped visible fields" in x.get("message", "")
            or "concrete upstream evidence tokens" in x.get("message", "")
            for x in findings
        ))

    def test_stage_checker_rejects_nonmatching_source_field_support(self):
        item = row06(
            content_enrichment_audit=audit_for_dimensions(["fact"], ["changed_state"]),
            fact_sources=[{
                "source_id": "SRC1",
                "source_url": "https://example.test/source",
                "visible_claim_support": ["sub"],
            }],
        )
        findings = stage_contract._content_enrichment_audit_findings(item, "SPEC")
        self.assertTrue(any(
            "do not support the mapped visible fields" in x.get("message", "")
            for x in findings
        ))

    def test_stage_checker_zero_delta_dimensions_must_be_expressed_by_mapped_text(self):
        placeholder = {"sub": "s", "gate": "g", "fact": "f", "implication": ["i"]}
        item = row06(
            **placeholder,
            content_enrichment_audit=audit(
                [], no_change=True, supported=4,
                reason="Placeholder copy must not pass standalone density.",
                bind_dimensions=True,
            ),
        )
        findings = stage_contract._content_enrichment_audit_findings(item, "SPEC")
        self.assertTrue(any(
            "claimed but not expressed" in x.get("message", "")
            for x in findings
        ))

    def test_stage_checker_claim_coverage_cannot_restore_excluded_source(self):
        item = row06(
            fact=NEW_DENSE_FACT,
            content_enrichment_audit=audit(["fact"]),
            fact_sources=[{
                "source_id": "SRC1",
                "source_url": "https://example.test/source",
                "role": "checked_not_used_for_visible_claims",
                "visible_claim_support": [],
            }],
            claim_source_coverage={
                "visible_fact": {"supported_by_source_ids": ["SRC1"]}
            },
        )
        findings = stage_contract._content_enrichment_audit_findings(item, "SPEC")
        self.assertTrue(any(
            "unbound references" in x.get("message", "")
            or "do not support the mapped visible fields" in x.get("message", "")
            or "concrete upstream evidence tokens" in x.get("message", "")
            for x in findings
        ))

    def test_stage_checker_malformed_dimension_fields_returns_finding_not_typeerror(self):
        malformed = audit_for_dimensions(["fact"], ["changed_state"])
        malformed["density_audit"]["dimension_evidence"]["changed_state"]["fields"] = None
        item = row06(content_enrichment_audit=malformed)
        findings = stage_contract._content_enrichment_audit_findings(item, "SPEC")
        self.assertTrue(any(
            x.get("field", "").endswith("dimension_evidence.changed_state.fields")
            for x in findings
        ))

    def test_duplicate_update_targets_are_rejected_before_materialization(self):
        with self.assertRaisesRegex(binding.Blocked, "duplicate target id CARD1"):
            binding._validate_unique_update_targets([
                {"id": "CARD1", "changes": [{"op": "replace", "path": "/fact", "value": "a"}]},
                {"id": "CARD1", "changes": [{"op": "replace", "path": "/fact", "value": "b"}]},
            ])

    def test_python_materializer_rejects_empty_update_change_list(self):
        with self.assertRaisesRegex(binding.Blocked, "non-empty array"):
            binding._materialized_operation_card(
                "update",
                {"id": "CARD1", "changes": []},
                None, None, None,
                {"CARD1": {"id": "CARD1", **VISIBLE}},
                {}, {}, "update[0]",
            )

    def test_python_materializer_rejects_duplicate_update_paths(self):
        operation = {
            "id": "CARD1",
            "changes": [
                {"op": "replace", "path": "/fact", "value": NEW_DENSE_FACT},
                {"op": "replace", "path": "/fact", "value": DENSE_FACT},
            ],
        }
        with self.assertRaisesRegex(binding.Blocked, "duplicate paths"):
            binding._materialized_operation_card(
                "update",
                operation,
                None, None, None,
                {"CARD1": {"id": "CARD1", **VISIBLE}},
                {}, {}, "update[0]",
            )

    def test_python_materializer_add_creates_missing_intermediate_objects_like_production_applier(self):
        card = {"id": "CARD1"}
        binding._apply_json_change(
            card,
            {"op": "add", "path": "/metadata/detail", "value": {"status": "ok"}},
            "update[0].changes[0]",
        )
        self.assertEqual(card["metadata"]["detail"], {"status": "ok"})

    def test_python_materializer_rejects_value_less_add_and_replace(self):
        for op in ("add", "replace"):
            card = {"id": "CARD1", "metadata": {}} if op == "add" else {"id": "CARD1", "metadata": {"detail": "old"}}
            with self.assertRaisesRegex(binding.Blocked, f"{op} requires value"):
                binding._apply_json_change(
                    card,
                    {"op": op, "path": "/metadata/detail"},
                    "update[0].changes[0]",
                )

    def test_python_materializer_rejects_value_on_remove(self):
        card = {"id": "CARD1", "metadata": {"detail": "old"}}
        with self.assertRaisesRegex(binding.Blocked, "remove must not include value"):
            binding._apply_json_change(
                card,
                {"op": "remove", "path": "/metadata/detail", "value": None},
                "update[0].changes[0]",
            )

    def test_python_materializer_add_rejects_existing_final_path(self):
        card = {"id": "CARD1", "metadata": {"detail": "old"}}
        with self.assertRaisesRegex(binding.Blocked, "add target already exists"):
            binding._apply_json_change(
                card,
                {"op": "add", "path": "/metadata/detail", "value": "new"},
                "update[0].changes[0]",
            )

    def test_python_materializer_replace_does_not_create_missing_intermediate_objects(self):
        card = {"id": "CARD1"}
        with self.assertRaisesRegex(binding.Blocked, "cannot resolve token 'metadata'"):
            binding._apply_json_change(
                card,
                {"op": "replace", "path": "/metadata/detail", "value": "new"},
                "update[0].changes[0]",
            )

    def test_python_materializer_rejects_production_forbidden_update_roots(self):
        cases = [
            ("/id", "NEWID"),
            ("/source_spec_id", "OTHER"),
            ("/related", []),
            ("/related_ids", []),
            ("/related_lineage", {}),
        ]
        for pointer, value in cases:
            card = {
                "id": "CARD1",
                "source_spec_id": "SPEC",
                "related": [],
                "related_ids": [],
                "related_lineage": {},
            }
            with self.assertRaises(binding.Blocked):
                binding._apply_json_change(
                    card,
                    {"op": "replace", "path": pointer, "value": value},
                    "update[0].changes[0]",
                )

    def test_python_materializer_rejects_noncanonical_array_indices(self):
        for path in ("/implication/01", "/implication/+1"):
            card = {"id": "CARD1", "implication": ["a", "b"]}
            with self.assertRaisesRegex(binding.Blocked, "canonical array index syntax"):
                binding._apply_json_change(
                    card,
                    {"op": "replace", "path": path, "value": "x"},
                    "update[0].changes[0]",
                )

    def test_python_materializer_accepts_canonical_array_index(self):
        card = {"id": "CARD1", "implication": ["a", "b"]}
        binding._apply_json_change(
            card,
            {"op": "replace", "path": "/implication/1", "value": "x"},
            "update[0].changes[0]",
        )
        self.assertEqual(card["implication"], ["a", "x"])


    def test_zero_delta_quantitative_grounding_requires_every_visible_signal(self):
        text = (
            "Previously, commercial production started at 10 MW and 999 MW; "
            "target remains subject to certification."
        )
        source = {
            "source_id": "SRC1",
            "source_url": "https://example.test/source",
            "source_quote": (
                "Previously, commercial production started at 10 MW; "
                "target remains subject to certification."
            ),
            "source_quote_status": "body_quote_verified",
            "fetched": True,
        }
        row = row06(
            fact=text,
            fact_sources=[source],
            content_enrichment_audit=audit(
                [], no_change=True, supported=4,
                reason="Every visible quantitative signal must be grounded.",
                bind_dimensions=True,
            ),
        )
        chain = rows(row)
        for stage in ("B", "C"):
            chain[stage][0]["fact_sources"] = [source]
        for stage in ("C", "0.4", "0.5"):
            chain[stage][0]["fact"] = text
        with self.assertRaisesRegex(binding.Blocked, "not grounded"):
            binding.validate_content_enrichment_delta(
                chain, "insert[0]",
                operation_card={**VISIBLE, "fact": text, "fact_sources": [source]},
            )

    def test_stage_checker_quantitative_grounding_requires_every_visible_signal(self):
        text = (
            "Previously, commercial production started at 10 MW and 999 MW; "
            "target remains subject to certification."
        )
        source = {
            "source_id": "SRC1",
            "source_url": "https://example.test/source",
            "source_quote": (
                "Previously, commercial production started at 10 MW; "
                "target remains subject to certification."
            ),
            "source_quote_status": "body_quote_verified",
            "fetched": True,
        }
        item = row06(
            fact=text,
            fact_sources=[source],
            content_enrichment_audit=audit(
                [], no_change=True, supported=4,
                reason="Standalone grounding must cover all mapped signals.",
                bind_dimensions=True,
            ),
        )
        findings = stage_contract._content_enrichment_audit_findings(item, "SPEC")
        self.assertTrue(any(
            "not grounded" in finding.get("message", "")
            and "999 mw" in str(finding.get("actual", "")).lower()
            for finding in findings
        ))

    def test_stage_checker_fact_source_exclusion_is_sticky_across_duplicate_tokens(self):
        excluded = {
            "source_id": "SRC1",
            "source_url": "https://example.test/source",
            "role": "checked_not_used_for_visible_claims",
            "visible_claim_support": [],
        }
        later_positive = {
            "source_id": "SRC1",
            "source_url": "https://example.test/source",
            "supports": ["fact"],
            "source_quote": "Commercial production started.",
            "source_quote_status": "body_quote_verified",
            "fetched": True,
        }
        item = row06(
            fact="Commercial production started.",
            fact_sources=[excluded, later_positive],
            content_enrichment_audit=audit_for_dimensions(
                ["fact"], ["changed_state"]
            ),
        )
        findings = stage_contract._content_enrichment_audit_findings(item, "SPEC")
        self.assertTrue(any(
            "unbound references" in finding.get("message", "")
            or "concrete upstream evidence tokens" in finding.get("message", "")
            for finding in findings
        ))

    def test_stage_checker_non_string_dimension_field_returns_finding(self):
        malformed = audit_for_dimensions(["fact"], ["changed_state"])
        malformed["density_audit"]["dimension_evidence"]["changed_state"]["fields"] = [{}]
        item = row06(content_enrichment_audit=malformed)
        findings = stage_contract._content_enrichment_audit_findings(item, "SPEC")
        self.assertTrue(any(
            finding.get("field", "").endswith(
                "dimension_evidence.changed_state.fields"
            )
            for finding in findings
        ))

    def test_new_changed_state_marker_requires_equal_or_stronger_evidence_modality(self):
        prior = "Capacity is 10 MW"
        current = "Capacity is 10 MW; the project is delayed"
        weak = {
            "source_id": "SRC1",
            "source_url": "https://example.test/source",
            "source_quote": "Capacity is 10 MW; the project may be delayed.",
            "source_quote_status": "body_quote_verified",
            "fetched": True,
        }
        row = row06(
            fact=current,
            fact_sources=[weak],
            content_enrichment_audit=audit_for_dimensions(
                ["fact"], ["changed_state"]
            ),
        )
        chain = rows(row)
        for stage in ("B", "C"):
            chain[stage][0]["fact_sources"] = [weak]
        for stage in ("C", "0.4", "0.5"):
            chain[stage][0]["fact"] = prior
        with self.assertRaisesRegex(
            binding.Blocked, "required_current_strengths|introduces/deepens"
        ):
            binding.validate_content_enrichment_delta(
                chain, "update[0]",
                operation_card={**VISIBLE, "fact": current, "fact_sources": [weak]},
            )

    def test_quantitative_entity_value_swap_requires_pair_grounding(self):
        prior = "Alpha has capacity of 10 MW; Beta has capacity of 20 MW"
        current = (
            "Alpha has capacity of 20 MW; Beta has capacity of 10 MW; "
            "Total capacity is 30 MW"
        )
        total_only = {
            "source_id": "SRC1",
            "source_url": "https://example.test/source",
            "source_quote": "Alpha has capacity of 10 MW; Beta has capacity of 20 MW; Total capacity is 30 MW.",
            "source_quote_status": "body_quote_verified",
            "fetched": True,
        }
        row = row06(
            fact=current,
            fact_sources=[total_only],
            content_enrichment_audit=audit_for_dimensions(
                ["fact"], ["quantitative_anchor"]
            ),
        )
        chain = rows(row)
        for stage in ("B", "C"):
            chain[stage][0]["fact_sources"] = [total_only]
        for stage in ("C", "0.4", "0.5"):
            chain[stage][0]["fact"] = prior
        with self.assertRaisesRegex(
            binding.Blocked, "rebinds/adds quantitative claims to factual entities"
        ):
            binding.validate_content_enrichment_delta(
                chain, "update[0]",
                operation_card={**VISIBLE, "fact": current, "fact_sources": [total_only]},
            )


    def test_evidence_aliases_for_same_source_cannot_double_count_occurrences(self):
        prior = "The site permit was approved"
        current = "The site permit was approved; project financing was approved"
        source = {
            "source_id": "SRC1",
            "source_url": "https://example.test/source",
            "source_quote": "Project financing was approved.",
            "source_quote_status": "body_quote_verified",
            "fetched": True,
        }
        focused = audit_for_dimensions(["fact"], ["changed_state"])
        focused["density_audit"]["dimension_evidence"]["changed_state"]["evidence_refs"] = [
            "SRC1", "https://example.test/source"
        ]
        row = row06(
            fact=current,
            fact_sources=[source],
            content_enrichment_audit=focused,
        )
        chain = rows(row)
        for stage in ("B", "C"):
            chain[stage][0]["fact_sources"] = [source]
        for stage in ("C", "0.4", "0.5"):
            chain[stage][0]["fact"] = prior
        with self.assertRaisesRegex(binding.Blocked, "aliases.*same resolved source/evidence package"):
            binding.validate_content_enrichment_delta(
                chain, "update[0]",
                operation_card={**VISIBLE, "fact": current, "fact_sources": [source]},
            )

    def test_generic_unlisted_factual_predicate_must_be_grounded(self):
        prior = "Capacity is 10 MW"
        current = "Capacity is 20 MW and burns coal"
        source = {
            "source_id": "SRC1",
            "source_url": "https://example.test/source",
            "source_quote": "Capacity is 20 MW.",
            "source_quote_status": "body_quote_verified",
            "fetched": True,
        }
        row = row06(
            fact=current,
            fact_sources=[source],
            content_enrichment_audit=audit_for_dimensions(
                ["fact"], ["quantitative_anchor"]
            ),
        )
        chain = rows(row)
        for stage in ("B", "C"):
            chain[stage][0]["fact_sources"] = [source]
        for stage in ("C", "0.4", "0.5"):
            chain[stage][0]["fact"] = prior
        with self.assertRaisesRegex(binding.Blocked, "predicate tokens not grounded"):
            binding.validate_content_enrichment_delta(
                chain, "update[0]",
                operation_card={**VISIBLE, "fact": current, "fact_sources": [source]},
            )

    def test_postpositive_entity_quantitative_swap_is_grounded_by_following_entity(self):
        prior = "10 MW for Alpha and 20 MW for Beta"
        current = "20 MW for Alpha and 10 MW for Beta, plus 30 MW for Beta"
        source = {
            "source_id": "SRC1",
            "source_url": "https://example.test/source",
            "source_quote": "10 MW for Alpha and 20 MW for Beta; 30 MW for Beta.",
            "source_quote_status": "body_quote_verified",
            "fetched": True,
        }
        row = row06(
            fact=current,
            fact_sources=[source],
            content_enrichment_audit=audit_for_dimensions(
                ["fact"], ["quantitative_anchor"]
            ),
        )
        chain = rows(row)
        for stage in ("B", "C"):
            chain[stage][0]["fact_sources"] = [source]
        for stage in ("C", "0.4", "0.5"):
            chain[stage][0]["fact"] = prior
        with self.assertRaisesRegex(
            binding.Blocked, "rebinds/adds quantitative claims to factual entities"
        ):
            binding.validate_content_enrichment_delta(
                chain, "update[0]",
                operation_card={**VISIBLE, "fact": current, "fact_sources": [source]},
            )

    def test_changed_state_modality_is_bound_to_claim_subject(self):
        prior = "Alpha may be delayed; Beta is delayed"
        current = "Alpha is delayed; Beta may be delayed; Gamma is approved"
        source = {
            "source_id": "SRC1",
            "source_url": "https://example.test/source",
            "source_quote": "Alpha may be delayed; Beta is delayed; Gamma is approved.",
            "source_quote_status": "body_quote_verified",
            "fetched": True,
        }
        row = row06(
            fact=current,
            fact_sources=[source],
            content_enrichment_audit=audit_for_dimensions(
                ["fact"], ["changed_state"]
            ),
        )
        chain = rows(row)
        for stage in ("B", "C"):
            chain[stage][0]["fact_sources"] = [source]
        for stage in ("C", "0.4", "0.5"):
            chain[stage][0]["fact"] = prior
        with self.assertRaisesRegex(binding.Blocked, "subject/modality claims"):
            binding.validate_content_enrichment_delta(
                chain, "update[0]",
                operation_card={**VISIBLE, "fact": current, "fact_sources": [source]},
            )

    def test_changed_path_grounds_every_declared_true_dimension(self):
        prior = "Previously, capacity was 10 MW"
        current = "Previously, capacity is 20 MW"
        source = {
            "source_id": "SRC1",
            "source_url": "https://example.test/source",
            "source_quote": "Capacity is 20 MW.",
            "source_quote_status": "body_quote_verified",
            "fetched": True,
        }
        focused = audit_for_dimensions(
            ["fact"], ["prior_state", "quantitative_anchor"]
        )
        row = row06(
            fact=current,
            fact_sources=[source],
            content_enrichment_audit=focused,
        )
        chain = rows(row)
        for stage in ("B", "C"):
            chain[stage][0]["fact_sources"] = [source]
        for stage in ("C", "0.4", "0.5"):
            chain[stage][0]["fact"] = prior
        with self.assertRaisesRegex(binding.Blocked, "dimension prior_state is not grounded"):
            binding.validate_content_enrichment_delta(
                chain, "update[0]",
                operation_card={**VISIBLE, "fact": current, "fact_sources": [source]},
            )

    def test_spatial_next_to_does_not_satisfy_next_watchpoint(self):
        text = "Previously, construction started at 10 MW next to the depot"
        self.assertNotIn(
            "generic_watch",
            binding._signal_values("next_watchpoint", text),
        )
        source = {
            "source_id": "SRC1",
            "source_url": "https://example.test/source",
            "source_quote": text,
            "source_quote_status": "body_quote_verified",
            "fetched": True,
        }
        values = {name: False for name in binding.DENSITY_DIMENSIONS}
        for name in ("prior_state", "changed_state", "quantitative_anchor", "next_watchpoint"):
            values[name] = True
        focused = {
            "baseline_strategy": binding.CONTENT_BASELINE_STRATEGY,
            "changed_fields": [],
            "no_change_required": True,
            "no_change_reason": "Spatial next-to must not manufacture a watchpoint.",
            "density_audit": {
                "status": "PASS",
                "dimensions": values,
                "supported_dimension_count": 4,
                "evidence_notes": "Focused spatial-next regression.",
                "dimension_evidence": {
                    name: {"fields": ["fact"], "evidence_refs": ["SRC1"]}
                    for name, enabled in values.items() if enabled
                },
            },
        }
        row = row06(
            fact=text,
            fact_sources=[source],
            content_enrichment_audit=focused,
        )
        chain = rows(row)
        for stage in ("B", "C"):
            chain[stage][0]["fact_sources"] = [source]
        for stage in ("C", "0.4", "0.5"):
            chain[stage][0]["fact"] = text
        with self.assertRaisesRegex(binding.Blocked, "next_watchpoint.*claimed but not expressed|claimed but not expressed"):
            binding.validate_content_enrichment_delta(
                chain, "insert[0]",
                operation_card={**VISIBLE, "fact": text, "fact_sources": [source]},
            )

    def test_materialized_operation_cannot_add_new_governed_evidence_text(self):
        prior = "Capacity is 10 MW"
        current = "Capacity is 20 MW"
        source = {
            "source_id": "SRC1",
            "source_url": "https://example.test/source",
            "source_quote": "Capacity is 20 MW.",
            "source_quote_status": "body_quote_verified",
            "fetched": True,
        }
        row = row06(
            fact=current,
            fact_sources=[source],
            content_enrichment_audit=audit_for_dimensions(
                ["fact"], ["quantitative_anchor"]
            ),
        )
        chain = rows(row)
        for stage in ("B", "C"):
            chain[stage][0]["fact_sources"] = [source]
        for stage in ("C", "0.4", "0.5"):
            chain[stage][0]["fact"] = prior
        injected = {**source, "claim": "Capacity is 999 MW."}
        with self.assertRaisesRegex(binding.Blocked, "does not preserve.*upstream quote/claim"):
            binding.validate_content_enrichment_delta(
                chain, "update[0]",
                operation_card={**VISIBLE, "fact": current, "fact_sources": [injected]},
            )

    def test_compound_production_commencement_synonym_does_not_manufacture_delta(self):
        prior = "Production began in 2026 at 10 MW"
        current = "Commercial production started in 2026 at 10 MW"
        source = {
            "source_id": "SRC1",
            "source_url": "https://example.test/source",
            "source_quote": current + ".",
            "source_quote_status": "body_quote_verified",
            "fetched": True,
        }
        self.assertEqual(
            binding._signal_values("changed_state", prior),
            binding._signal_values("changed_state", current),
        )
        row = row06(
            fact=current,
            fact_sources=[source],
            content_enrichment_audit=audit_for_dimensions(
                ["fact"], ["changed_state"]
            ),
        )
        chain = rows(row)
        for stage in ("B", "C"):
            chain[stage][0]["fact_sources"] = [source]
        for stage in ("C", "0.4", "0.5"):
            chain[stage][0]["fact"] = prior
        with self.assertRaisesRegex(binding.Blocked, "machine-detectable newly added/deepened"):
            binding.validate_content_enrichment_delta(
                chain, "update[0]",
                operation_card={**VISIBLE, "fact": current, "fact_sources": [source]},
            )

    def test_stage_checker_reports_source_alias_double_counting(self):
        item = row06(
            content_enrichment_audit=audit(
                [], no_change=True, supported=4,
                reason="Aliases must resolve to one evidence identity.",
                bind_dimensions=True,
            )
        )
        item["content_enrichment_audit"]["density_audit"]["dimension_evidence"]["changed_state"]["evidence_refs"] = [
            "SRC1", "https://example.test/source"
        ]
        findings = stage_contract._content_enrichment_audit_findings(item, "SPEC")
        self.assertTrue(any(
            "aliases" in str(finding.get("message", "")).lower()
            for finding in findings
        ))



if __name__ == "__main__":
    unittest.main()
