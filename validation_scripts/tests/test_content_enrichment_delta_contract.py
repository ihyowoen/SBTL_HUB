import unittest

from validation_scripts import card_run_v4_binding_hardening as binding
from validation_scripts import stage_artifact_contract_check as stage_contract


def density(*, supported=4, changed_state=True):
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
    return {
        "status": "PASS",
        "dimensions": values,
        "supported_dimension_count": actual,
        "evidence_notes": "Evidence-bounded density test.",
    }


def rows(row_06):
    return {
        "C": [{
            "source_spec_id": "SPEC",
            "sub": "same sub",
            "gate": "same gate",
            "fact": "same fact",
            "implication": ["same implication"],
        }],
        "0.4": [{"source_spec_id": "SPEC", "fact": "same fact"}],
        "0.5": [{"source_spec_id": "SPEC", "fact": "same fact"}],
        "0.6": [row_06],
    }


def audit(changed_fields, *, no_change=False, supported=4, reason=""):
    return {
        "baseline_strategy": binding.CONTENT_BASELINE_STRATEGY,
        "changed_fields": changed_fields,
        "no_change_required": no_change,
        "no_change_reason": reason,
        "density_audit": density(supported=supported),
    }


class ContentEnrichmentDeltaTests(unittest.TestCase):
    def test_zero_delta_falls_back_through_05_and_04_to_stage_c_and_blocks_boolean_only(self):
        row = {
            "source_spec_id": "SPEC",
            "sub": "same sub",
            "gate": "same gate",
            "fact": "same fact",
            "implication": ["same implication"],
            "content_enriched": True,
            "content_enrichment_audit": audit([], no_change=False),
        }
        with self.assertRaisesRegex(binding.Blocked, "zero visible-copy delta"):
            binding.validate_content_enrichment_delta(rows(row), "insert[0]")

    def test_actual_fact_change_passes_and_missing_05_fields_do_not_create_false_delta(self):
        row = {
            "source_spec_id": "SPEC",
            "sub": "same sub",
            "gate": "same gate",
            "fact": "changed fact",
            "implication": ["same implication"],
            "content_enriched": True,
            "content_enrichment_audit": audit(["fact"]),
        }
        binding.validate_content_enrichment_delta(rows(row), "insert[0]")

    def test_declared_changed_fields_must_equal_actual_delta(self):
        row = {
            "source_spec_id": "SPEC",
            "sub": "same sub",
            "gate": "same gate",
            "fact": "changed fact",
            "implication": ["same implication"],
            "content_enriched": True,
            "content_enrichment_audit": audit(["sub"]),
        }
        with self.assertRaisesRegex(binding.Blocked, "does not equal actual visible-copy delta"):
            binding.validate_content_enrichment_delta(rows(row), "insert[0]")

    def test_explicit_sufficient_density_no_change_exception_passes(self):
        row = {
            "source_spec_id": "SPEC",
            "sub": "same sub",
            "gate": "same gate",
            "fact": "same fact",
            "implication": ["same implication"],
            "content_enriched": True,
            "content_enrichment_audit": audit(
                [], no_change=True, supported=4,
                reason="Upstream copy already expresses the verified state, number, boundary and watchpoint.",
            ),
        }
        binding.validate_content_enrichment_delta(rows(row), "insert[0]")

    def test_zero_delta_weak_density_is_blocked(self):
        row = {
            "source_spec_id": "SPEC",
            "sub": "same sub",
            "gate": "same gate",
            "fact": "same fact",
            "implication": ["same implication"],
            "content_enriched": True,
            "content_enrichment_audit": audit(
                [], no_change=True, supported=3,
                reason="Claims to be sufficient.",
            ),
        }
        with self.assertRaisesRegex(binding.Blocked, "at least four"):
            binding.validate_content_enrichment_delta(rows(row), "insert[0]")

    def test_stage_06_contract_requires_structured_audit(self):
        findings = stage_contract._content_enrichment_audit_findings(
            {"source_spec_id": "SPEC", "content_enriched": True}, "SPEC"
        )
        self.assertTrue(any(x.get("field") == "content_enrichment_audit" for x in findings))


if __name__ == "__main__":
    unittest.main()
