import unittest

from validation_scripts import card_run_v4_binding_hardening as binding
from validation_scripts import stage_artifact_contract_check as stage_contract


VISIBLE = {
    "sub": "same sub",
    "gate": "same gate",
    "fact": "same fact",
    "implication": ["same implication"],
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
    source = {"source_id": "SRC1", "source_url": "https://example.test/source"}
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


def row06(**overrides):
    base = {
        "source_spec_id": "SPEC",
        **VISIBLE,
        "fact_sources": [{"source_id": "SRC1", "source_url": "https://example.test/source"}],
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
            fact="changed fact",
            content_enrichment_audit=audit(["fact"]),
        )
        binding.validate_content_enrichment_delta(
            rows(row), "insert[0]",
            operation_card={**VISIBLE, "fact": "changed fact"},
        )

    def test_declared_changed_fields_are_order_independent(self):
        row = row06(
            sub="changed sub",
            fact="changed fact",
            content_enrichment_audit=audit(["fact", "sub"]),
        )
        binding.validate_content_enrichment_delta(
            rows(row), "insert[0]",
            operation_card={**VISIBLE, "sub": "changed sub", "fact": "changed fact"},
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
            fact="same   fact",
            content_enrichment_audit=audit(
                [], no_change=True, supported=4,
                reason="Already decision-useful.",
                bind_dimensions=True,
            ),
        )
        binding.validate_content_enrichment_delta(
            rows(row), "insert[0]",
            operation_card={**VISIBLE, "fact": "same fact"},
        )

    def test_markdown_only_difference_is_zero_delta(self):
        row = row06(
            fact="**same fact**",
            content_enrichment_audit=audit(
                [], no_change=True, supported=4,
                reason="Only presentation markup differs.",
                bind_dimensions=True,
            ),
        )
        binding.validate_content_enrichment_delta(
            rows(row), "insert[0]",
            operation_card={**VISIBLE, "fact": "same fact"},
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
            fact="changed fact",
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
        with self.assertRaisesRegex(binding.Blocked, "bound upstream source evidence tokens"):
            binding.validate_content_enrichment_delta(
                chain, "update[0]",
                operation_card={**VISIBLE, "fact": "changed fact"},
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

    def test_python_materializer_add_creates_missing_intermediate_objects_like_production_applier(self):
        card = {"id": "CARD1"}
        binding._apply_json_change(
            card,
            {"op": "add", "path": "/metadata/detail", "value": {"status": "ok"}},
            "update[0].changes[0]",
        )
        self.assertEqual(card["metadata"]["detail"], {"status": "ok"})

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



if __name__ == "__main__":
    unittest.main()
