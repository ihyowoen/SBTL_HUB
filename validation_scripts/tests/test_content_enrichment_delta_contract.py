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
    return {
        "C": [{"source_spec_id": "SPEC", **VISIBLE}],
        "0.4": [{"source_spec_id": "SPEC", "fact": VISIBLE["fact"]}],
        "0.5": [{"source_spec_id": "SPEC", "fact": VISIBLE["fact"]}],
        "0.6": [row_06],
    }


def audit(changed_fields, *, no_change=False, supported=4, reason="", bind_dimensions=False):
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

    def test_operation_copy_must_match_audited_06_copy(self):
        row = row06(
            fact="changed fact",
            content_enrichment_audit=audit(["fact"]),
        )
        with self.assertRaisesRegex(binding.Blocked, "applied operation visible copy"):
            binding.validate_content_enrichment_delta(
                rows(row), "insert[0]", operation_card=VISIBLE,
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


if __name__ == "__main__":
    unittest.main()
