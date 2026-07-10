#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
TMPDIR="$(mktemp -d)"
trap 'rm -rf "$TMPDIR"' EXIT

pass() {
  local name="$1"
  shift
  echo "[PASS expected] $name"
  "$@"
}

fail() {
  local name="$1"
  shift
  echo "[FAIL expected] $name"
  if "$@"; then
    echo "Expected failure but command passed: $name" >&2
    exit 1
  fi
}

cat > "$TMPDIR/stage_a_empty_format_tags_pass.json" <<'JSON'
{
  "strict_passed_specs": [
    {
      "spec_id": "SA_PASS",
      "source_story_ids": ["story-a"],
      "strict_pass_gate": {
        "status": "pass",
        "reason": "All strict-pass conditions satisfied.",
        "all_six_conditions_passed": true
      },
      "enhanced_selector_precision_version": "v1",
      "selector_policy_version": "v1",
      "strict_gate_check": "PASS",
      "format_risk_tags": [],
      "execution_anchor_type": "regulatory_decision",
      "execution_anchor_strength": "strong",
      "baseline_relation": "new_event",
      "duplicate_risk": "low",
      "staleness_decision": "fresh",
      "source_access_risk": "low",
      "stage_a_evidence_status": "not_evidence_complete_no_fetch",
      "stage_b_evidence_package_required": true,
      "primary_url_semantics": "provided_source_candidate_not_evidence"
    }
  ]
}
JSON

cat > "$TMPDIR/stage_a_fail_nonpass_gate.json" <<'JSON'
{
  "strict_passed_specs": [
    {
      "spec_id": "SA_FAIL",
      "source_story_ids": ["story-b"],
      "strict_pass_gate": {
        "status": "blocked_to_review_pool",
        "reason": "Not all strict-pass conditions were satisfied.",
        "all_six_conditions_passed": false
      },
      "enhanced_selector_precision_version": "v1",
      "selector_policy_version": "v1",
      "strict_gate_check": "PASS",
      "format_risk_tags": [],
      "execution_anchor_type": "regulatory_decision",
      "execution_anchor_strength": "strong",
      "baseline_relation": "new_event",
      "duplicate_risk": "low",
      "staleness_decision": "fresh",
      "source_access_risk": "low",
      "stage_a_evidence_status": "not_evidence_complete_no_fetch",
      "stage_b_evidence_package_required": true,
      "primary_url_semantics": "provided_source_candidate_not_evidence"
    }
  ]
}
JSON

cat > "$TMPDIR/stage_b_pass.json" <<'JSON'
{
  "strict_passed_spec_count": 1,
  "stage_b_accounting_matches_strict_passed_spec_count": true,
  "strict_passed_specs": [{"spec_id": "S1"}],
  "draft_cards": [{"source_spec_id": "S1"}],
  "draft_blocked": [],
  "draft_blocked_schema": [],
  "source_discovery_ledger": [{"query": "official source"}],
  "evidence_packages": [
    {
      "spec_id": "S1",
      "source_discovery_status": "completed_verified_source_found",
      "source_discovery_ledger": [{"query": "official source"}],
      "single_source_exception": {"allowed": true, "reason": "official primary source"},
      "sources": [
        {
          "source_url": "https://example.gov/news/release-1",
          "fetched": true,
          "source_quote": "Verified official statement.",
          "source_quote_status": "body_quote_verified",
          "evidence_role": "primary_event_evidence"
        }
      ]
    }
  ]
}
JSON

cat > "$TMPDIR/stage_b_blocked_reference_pass.json" <<'JSON'
{
  "strict_passed_spec_count": 1,
  "stage_b_accounting_matches_strict_passed_spec_count": true,
  "draft_cards": [],
  "draft_blocked": [
    {
      "source_spec_id": "S_BLOCK_REF",
      "source_discovery_status": "completed_no_verified_source",
      "source_discovery_ledger_reference": "top_level_source_discovery_ledger",
      "final_hold_or_reject_reason": "No body-level verified source found after documented search."
    }
  ],
  "draft_blocked_schema": [],
  "source_discovery_ledger": [
    {"query": "official source search", "result": "no verified source found"}
  ]
}
JSON

cat > "$TMPDIR/stage_b_fail_missing_accounting.json" <<'JSON'
{
  "draft_cards": [],
  "draft_blocked": [],
  "draft_blocked_schema": []
}
JSON

cat > "$TMPDIR/stage_b_fail_unverified_primary_evidence.json" <<'JSON'
{
  "strict_passed_spec_count": 1,
  "stage_b_accounting_matches_strict_passed_spec_count": true,
  "draft_cards": [
    {"source_spec_id": "S_UNVERIFIED", "evidence_package": {"source_discovery_status": "completed_verified_source_found", "source_discovery_ledger": [{"query": "q"}], "single_source_exception": {"allowed": true, "reason": "official"}, "sources": [{"source_url": "https://example.gov/news/unverified", "fetched": true, "source_quote": "quote", "source_quote_status": "fetch_failed", "evidence_role": "primary_event_evidence"}] }}
  ],
  "draft_blocked": [],
  "draft_blocked_schema": []
}
JSON

cat > "$TMPDIR/stage_b_fail_duplicate_output_key.json" <<'JSON'
{
  "strict_passed_spec_count": 2,
  "stage_b_accounting_matches_strict_passed_spec_count": true,
  "draft_cards": [
    {"source_spec_id": "S_DUP", "evidence_package": {"source_discovery_status": "completed_verified_source_found", "source_discovery_ledger": [{"query": "q"}], "single_source_exception": {"allowed": true, "reason": "official"}, "sources": [{"source_url": "https://example.gov/news/a", "fetched": true, "source_quote": "quote", "source_quote_status": "body_quote_verified", "evidence_role": "primary_event_evidence"}] }},
    {"source_spec_id": "S_DUP", "evidence_package": {"source_discovery_status": "completed_verified_source_found", "source_discovery_ledger": [{"query": "q"}], "single_source_exception": {"allowed": true, "reason": "official"}, "sources": [{"source_url": "https://example.gov/news/b", "fetched": true, "source_quote": "quote", "source_quote_status": "body_quote_verified", "evidence_role": "primary_event_evidence"}] }}
  ],
  "draft_blocked": [],
  "draft_blocked_schema": []
}
JSON

cat > "$TMPDIR/stage_b_schema_blocked_pass.json" <<'JSON'
{
  "strict_passed_spec_count": 1,
  "stage_b_accounting_matches_strict_passed_spec_count": true,
  "strict_passed_specs": [{"spec_id": "S2"}],
  "draft_cards": [],
  "draft_blocked": [],
  "draft_blocked_schema": [{"source_spec_id": "S2", "schema_blocked_reason": "self-check failed"}]
}
JSON

cat > "$TMPDIR/stage_b_lineage_pass.json" <<'JSON'
{
  "lineage_integrity_status": "PASS",
  "stage_a_validity_guard_applied": true,
  "strict_gate_metadata_preserved": true,
  "execution_anchor_metadata_preserved": true,
  "superseded_lineage_mixed": false,
  "manual_integrated_rule_mixed": false,
  "previous_run_output_mixed": false,
  "stage_a_support_sources_attempted": [{"source_url": "https://support.example.com/a", "result": "checked"}],
  "source_independence_ledger": [{"host": "example.gov", "owner": "Example Government"}],
  "source_unique_url_count": 2,
  "source_unique_domain_count": 2,
  "source_independent_owner_count": 2,
  "source_role_coverage": {"primary_event_evidence": 1},
  "source_synthesis_plan": "Use primary source plus secondary corroboration."
}
JSON

cat > "$TMPDIR/stage_b_lineage_package_pass.json" <<'JSON'
{
  "lineage_integrity_status": "PASS",
  "stage_a_validity_guard_applied": true,
  "strict_gate_metadata_preserved": true,
  "execution_anchor_metadata_preserved": true,
  "superseded_lineage_mixed": false,
  "manual_integrated_rule_mixed": false,
  "previous_run_output_mixed": false,
  "evidence_packages": [
    {
      "spec_id": "S_PACKAGE",
      "stage_a_support_sources_attempted": [{"source_url": "https://support.example.com/a", "result": "checked"}],
      "source_independence_ledger": [{"host": "example.gov", "owner": "Example Government"}],
      "source_unique_url_count": 2,
      "source_unique_domain_count": 2,
      "source_independent_owner_count": 2,
      "source_role_coverage": {"primary_event_evidence": 1},
      "source_synthesis_plan": "Use package-level source diversity lineage."
    }
  ]
}
JSON

cat > "$TMPDIR/stage_b_lineage_fail_missing_source_diversity.json" <<'JSON'
{
  "lineage_integrity_status": "PASS",
  "stage_a_validity_guard_applied": true,
  "strict_gate_metadata_preserved": true,
  "execution_anchor_metadata_preserved": true,
  "superseded_lineage_mixed": false,
  "manual_integrated_rule_mixed": false,
  "previous_run_output_mixed": false
}
JSON

cat > "$TMPDIR/stage_c_fail_missing_lineage.json" <<'JSON'
{
  "accepted_fact_safe": [
    {"id": "C1", "state": "accepted_fact_safe", "stage_c_only": true}
  ]
}
JSON

cat > "$TMPDIR/evidence_qc_primary_exception_pass.json" <<'JSON'
{
  "evidence_complete_and_source_claim_covered": [
    {
      "id": "C_PRIMARY",
      "title": "Safety announcement from primary company source",
      "signal": "high",
      "source_diversity_status": "PASS_OFFICIAL_OR_PRIMARY_SINGLE_SOURCE_EXCEPTION",
      "urls": ["https://company.example.com/news/safety-announcement"],
      "source_discovery_ledger": [{"query": "independent corroboration", "result": "none found"}],
      "single_source_exception": {"allowed": true, "reason": "Company announcement is the primary source for its own release; visible claims are limited to the announcement."},
      "fact_sources": [
        {"source_url": "https://company.example.com/news/safety-announcement", "evidence_role": "primary_event_evidence", "source_type": "company_primary_announcement"}
      ]
    }
  ]
}
JSON

cat > "$TMPDIR/evidence_qc_hold_single_caveat_pass.json" <<'JSON'
{
  "needs_source_augmentation": [
    {
      "id": "C_HOLD_SINGLE",
      "source_diversity_status": "HOLD_NEEDS_SOURCE_AUGMENTATION",
      "urls": ["https://news.example.com/one-source"],
      "single_source_exception": {"allowed": false, "reason": "Needs corroboration before completion."},
      "fact_sources": [
        {"source_url": "https://news.example.com/one-source", "evidence_role": "primary_event_evidence"}
      ]
    }
  ]
}
JSON

cat > "$TMPDIR/evidence_qc_fail_same_owner_multi.json" <<'JSON'
{
  "evidence_complete_and_source_claim_covered": [
    {
      "id": "C_SAME_OWNER",
      "source_diversity_status": "PASS_MULTI_SOURCE",
      "source_independent_owner_count": 1,
      "source_independence_ledger": [
        {"host": "wire1.example.com", "owner": "WireCo"},
        {"host": "wire2.example.com", "owner": "WireCo"}
      ],
      "urls": ["https://wire1.example.com/a", "https://wire2.example.com/b"],
      "source_discovery_ledger": [{"query": "q"}],
      "fact_sources": [
        {"source_url": "https://wire1.example.com/a", "evidence_role": "primary_event_evidence"},
        {"source_url": "https://wire2.example.com/b", "evidence_role": "secondary_event_evidence"}
      ]
    }
  ]
}
JSON

cat > "$TMPDIR/evidence_qc_fail_addable_merge_safe_input.json" <<'JSON'
{
  "addable_merge_safe": [
    {
      "id": "C_INPUT",
      "source_diversity_status": "BOGUS",
      "urls": ["https://news.example.com/input"],
      "fact_sources": [
        {"source_url": "https://news.example.com/input", "evidence_role": "primary_event_evidence"}
      ]
    }
  ]
}
JSON

cat > "$TMPDIR/evidence_qc_fail_complete_bucket_hold.json" <<'JSON'
{
  "evidence_complete_and_source_claim_covered": [
    {
      "id": "C1",
      "source_diversity_status": "HOLD_NEEDS_SOURCE_AUGMENTATION",
      "urls": ["https://news.example.com/a"],
      "source_discovery_ledger": [{"query": "q"}],
      "single_source_exception": {"allowed": true, "reason": "temporary"},
      "fact_sources": [
        {"source_url": "https://news.example.com/a", "evidence_role": "primary_event_evidence"}
      ]
    }
  ]
}
JSON

cat > "$TMPDIR/evidence_qc_fail_pass_multi_single.json" <<'JSON'
{
  "evidence_complete_and_source_claim_covered": [
    {
      "id": "C2",
      "source_diversity_status": "PASS_MULTI_SOURCE",
      "urls": ["https://news.example.com/a"],
      "source_discovery_ledger": [{"query": "q"}],
      "single_source_exception": {"allowed": true, "reason": "temporary"},
      "fact_sources": [
        {"source_url": "https://news.example.com/a", "evidence_role": "primary_event_evidence"}
      ]
    }
  ]
}
JSON

cat > "$TMPDIR/evidence_qc_fail_bogus_multi_status.json" <<'JSON'
{
  "evidence_complete_and_source_claim_covered": [
    {
      "id": "C3",
      "source_diversity_status": "BOGUS",
      "urls": ["https://news1.example.com/a", "https://news2.example.com/b"],
      "source_discovery_ledger": [{"query": "q"}],
      "fact_sources": [
        {"source_url": "https://news1.example.com/a", "evidence_role": "primary_event_evidence"},
        {"source_url": "https://news2.example.com/b", "evidence_role": "secondary_event_evidence"}
      ]
    }
  ]
}
JSON

cat > "$TMPDIR/evidence_qc_fail_omitted_bucket.json" <<'JSON'
{
  "addable_hold_claim_gap": [
    {
      "id": "C4",
      "source_diversity_status": "BOGUS",
      "urls": ["https://news.example.com/claim-gap"],
      "fact_sources": [
        {"source_url": "https://news.example.com/claim-gap", "evidence_role": "primary_event_evidence"}
      ]
    }
  ]
}
JSON

cat > "$TMPDIR/content_audit_fail_missing_coverage.json" <<'JSON'
{
  "content_enriched_and_language_polished": [
    {"id": "C1"},
    {"id": "C2"}
  ],
  "card_claim_diversity_audit": [{"card_id": "C1"}],
  "related_coverage_audit": [{"card_id": "C1"}, {"card_id": "C2"}]
}
JSON

cat > "$TMPDIR/content_audit_fail_omitted_bucket.json" <<'JSON'
{
  "content_hold_language_issue": [
    {"id": "C_HOLD"}
  ],
  "card_claim_diversity_audit": [{"card_id": "OTHER"}],
  "related_coverage_audit": [{"card_id": "OTHER"}]
}
JSON

pass "stage_a empty format tags pass" python3 "$ROOT/validation_scripts/stage_lineage_contract_check.py" stage_a "$TMPDIR/stage_a_empty_format_tags_pass.json"
fail "stage_a non-pass strict gate fail" python3 "$ROOT/validation_scripts/stage_lineage_contract_check.py" stage_a "$TMPDIR/stage_a_fail_nonpass_gate.json"
pass "stage_b evidence pass" python3 "$ROOT/validation_scripts/stage_b_evidence_gate.py" "$TMPDIR/stage_b_pass.json"
pass "stage_b blocked ledger reference pass" python3 "$ROOT/validation_scripts/stage_b_evidence_gate.py" "$TMPDIR/stage_b_blocked_reference_pass.json"
pass "stage_b schema-blocked accounting pass" python3 "$ROOT/validation_scripts/stage_b_evidence_gate.py" "$TMPDIR/stage_b_schema_blocked_pass.json"
fail "stage_b missing accounting fail" python3 "$ROOT/validation_scripts/stage_b_evidence_gate.py" "$TMPDIR/stage_b_fail_missing_accounting.json"
fail "stage_b unverified primary evidence fail" python3 "$ROOT/validation_scripts/stage_b_evidence_gate.py" "$TMPDIR/stage_b_fail_unverified_primary_evidence.json"
fail "stage_b duplicate output key fail" python3 "$ROOT/validation_scripts/stage_b_evidence_gate.py" "$TMPDIR/stage_b_fail_duplicate_output_key.json"
pass "stage_b lineage root pass" python3 "$ROOT/validation_scripts/stage_lineage_contract_check.py" stage_b "$TMPDIR/stage_b_lineage_pass.json"
pass "stage_b lineage package pass" python3 "$ROOT/validation_scripts/stage_lineage_contract_check.py" stage_b "$TMPDIR/stage_b_lineage_package_pass.json"
fail "stage_b lineage missing source-diversity fail" python3 "$ROOT/validation_scripts/stage_lineage_contract_check.py" stage_b "$TMPDIR/stage_b_lineage_fail_missing_source_diversity.json"
fail "stage_c missing lineage fail" python3 "$ROOT/validation_scripts/stage_lineage_contract_check.py" stage_c "$TMPDIR/stage_c_fail_missing_lineage.json"
pass "Evidence QC primary-source exception pass" python3 "$ROOT/validation_scripts/evidence_qc_v8_check.py" "$TMPDIR/evidence_qc_primary_exception_pass.json"
pass "Evidence QC held one-source caveat pass" python3 "$ROOT/validation_scripts/evidence_qc_v8_check.py" "$TMPDIR/evidence_qc_hold_single_caveat_pass.json"
fail "Evidence QC same-owner multi-source fail" python3 "$ROOT/validation_scripts/evidence_qc_v8_check.py" "$TMPDIR/evidence_qc_fail_same_owner_multi.json"
fail "Evidence QC addable_merge_safe input bucket fail" python3 "$ROOT/validation_scripts/evidence_qc_v8_check.py" "$TMPDIR/evidence_qc_fail_addable_merge_safe_input.json"
fail "evidence complete bucket cannot hold HOLD status" python3 "$ROOT/validation_scripts/evidence_qc_v8_check.py" "$TMPDIR/evidence_qc_fail_complete_bucket_hold.json"
fail "single-source PASS_MULTI_SOURCE fail" python3 "$ROOT/validation_scripts/evidence_qc_v8_check.py" "$TMPDIR/evidence_qc_fail_pass_multi_single.json"
fail "multi-source bogus source_diversity_status fail" python3 "$ROOT/validation_scripts/evidence_qc_v8_check.py" "$TMPDIR/evidence_qc_fail_bogus_multi_status.json"
fail "Evidence QC omitted bucket coverage fail" python3 "$ROOT/validation_scripts/evidence_qc_v8_check.py" "$TMPDIR/evidence_qc_fail_omitted_bucket.json"
fail "content audit missing per-card coverage fail" python3 "$ROOT/validation_scripts/content_audit_check.py" "$TMPDIR/content_audit_fail_missing_coverage.json"
fail "Content audit omitted bucket coverage fail" python3 "$ROOT/validation_scripts/content_audit_check.py" "$TMPDIR/content_audit_fail_omitted_bucket.json"

echo "All validation script smoke tests behaved as expected."
