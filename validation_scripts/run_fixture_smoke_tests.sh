#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
TMPDIR="$(mktemp -d)"
trap 'rm -rf "$TMPDIR"' EXIT

pass() {
  local name="$1"; shift
  echo "[PASS expected] $name"
  "$@"
}

fail() {
  local name="$1"; shift
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
      "spec_id": "A_PASS",
      "source_story_ids": ["S1"],
      "strict_pass_gate": {"status": "pass", "reason": "six conditions met", "all_six_conditions_passed": true},
      "enhanced_selector_precision_version": "v1",
      "selector_policy_version": "v1",
      "strict_gate_check": "PASS",
      "format_risk_tags": [],
      "execution_anchor_type": "regulatory_decision",
      "execution_anchor_strength": "strong",
      "baseline_relation": "new",
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
      "spec_id": "A_FAIL",
      "source_story_ids": ["S1"],
      "strict_pass_gate": {"status": "blocked_to_review_pool", "reason": "not strict pass", "all_six_conditions_passed": false},
      "enhanced_selector_precision_version": "v1",
      "selector_policy_version": "v1",
      "strict_gate_check": "PASS",
      "format_risk_tags": [],
      "execution_anchor_type": "regulatory_decision",
      "execution_anchor_strength": "strong",
      "baseline_relation": "new",
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

cat > "$TMPDIR/stage_b_evidence_pass.json" <<'JSON'
{
  "strict_passed_spec_count": 1,
  "stage_b_accounting_matches_strict_passed_spec_count": true,
  "strict_passed_specs": [{"spec_id": "B1"}],
  "draft_cards": [{"source_spec_id": "B1"}],
  "draft_blocked": [],
  "draft_blocked_schema": [],
  "evidence_packages": [
    {
      "spec_id": "B1",
      "source_discovery_status": "completed_verified_source_found",
      "source_discovery_ledger": [{"query": "official source"}],
      "single_source_exception": {"allowed": true, "reason": "official primary source"},
      "sources": [
        {"source_url": "https://example.gov/news/release-1", "fetched": true, "source_quote": "Verified quote", "source_quote_status": "body_quote_verified", "evidence_role": "primary_event_evidence"}
      ]
    }
  ]
}
JSON

cat > "$TMPDIR/stage_b_unverified_primary_fail.json" <<'JSON'
{
  "strict_passed_spec_count": 1,
  "stage_b_accounting_matches_strict_passed_spec_count": true,
  "draft_cards": [
    {"source_spec_id": "B_BAD", "evidence_package": {"source_discovery_status": "completed_verified_source_found", "source_discovery_ledger": [{"query": "q"}], "single_source_exception": {"allowed": true, "reason": "official"}, "sources": [{"source_url": "https://example.gov/news/bad", "fetched": true, "source_quote": "quote", "source_quote_status": "fetch_failed", "evidence_role": "primary_event_evidence"}]}}
  ],
  "draft_blocked": [],
  "draft_blocked_schema": []
}
JSON

cat > "$TMPDIR/stage_b_duplicate_fail.json" <<'JSON'
{
  "strict_passed_spec_count": 2,
  "stage_b_accounting_matches_strict_passed_spec_count": true,
  "draft_cards": [
    {"source_spec_id": "B_DUP", "evidence_package": {"source_discovery_status": "completed_verified_source_found", "source_discovery_ledger": [{"query": "q"}], "single_source_exception": {"allowed": true, "reason": "official"}, "sources": [{"source_url": "https://example.gov/news/a", "fetched": true, "source_quote": "quote", "source_quote_status": "body_quote_verified"}]}},
    {"source_spec_id": "B_DUP", "evidence_package": {"source_discovery_status": "completed_verified_source_found", "source_discovery_ledger": [{"query": "q"}], "single_source_exception": {"allowed": true, "reason": "official"}, "sources": [{"source_url": "https://example.gov/news/b", "fetched": true, "source_quote": "quote", "source_quote_status": "body_quote_verified"}]}}
  ],
  "draft_blocked": [],
  "draft_blocked_schema": []
}
JSON

cat > "$TMPDIR/stage_b_blocked_reference_pass.json" <<'JSON'
{
  "strict_passed_spec_count": 1,
  "stage_b_accounting_matches_strict_passed_spec_count": true,
  "draft_cards": [],
  "draft_blocked": [
    {"source_spec_id": "B_BLOCK", "source_discovery_status": "completed_no_verified_source", "source_discovery_ledger_reference": "top_level", "final_hold_or_reject_reason": "No verified source found."}
  ],
  "draft_blocked_schema": [],
  "source_discovery_ledger": [{"query": "q", "result": "no verified source"}]
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
      "spec_id": "PKG",
      "stage_a_support_sources_attempted": [{"source_url": "https://support.example/a"}],
      "source_independence_ledger": [{"host": "example.gov", "owner": "Example Government"}],
      "source_unique_url_count": 2,
      "source_unique_domain_count": 2,
      "source_independent_owner_count": 2,
      "source_role_coverage": {"primary_event_evidence": 1},
      "source_synthesis_plan": "Use primary and corroborating sources."
    }
  ]
}
JSON

cat > "$TMPDIR/stage_b_lineage_missing_fail.json" <<'JSON'
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

cat > "$TMPDIR/stage_c_missing_lineage_fail.json" <<'JSON'
{"accepted_fact_safe": [{"id": "C1", "state": "accepted_fact_safe", "stage_c_only": true}]}
JSON

cat > "$TMPDIR/evidence_qc_primary_exception_pass.json" <<'JSON'
{
  "evidence_complete_and_source_claim_covered": [
    {
      "id": "EQ_PRIMARY",
      "title": "Safety announcement from primary company source",
      "signal": "high",
      "source_diversity_status": "PASS_OFFICIAL_OR_PRIMARY_SINGLE_SOURCE_EXCEPTION",
      "urls": ["https://company.example.com/news/safety"],
      "source_discovery_ledger": [{"query": "corroboration", "result": "none"}],
      "single_source_exception": {"allowed": true, "reason": "company primary announcement; visible claims limited to announcement"},
      "fact_sources": [{"source_url": "https://company.example.com/news/safety", "evidence_role": "primary_event_evidence", "source_type": "company_primary_announcement"}]
    }
  ]
}
JSON

cat > "$TMPDIR/evidence_qc_hold_single_pass.json" <<'JSON'
{
  "needs_source_augmentation": [
    {
      "id": "EQ_HOLD",
      "source_diversity_status": "HOLD_NEEDS_SOURCE_AUGMENTATION",
      "urls": ["https://news.example.com/one"],
      "single_source_exception": {"allowed": false, "reason": "needs corroboration"},
      "fact_sources": [{"source_url": "https://news.example.com/one", "evidence_role": "primary_event_evidence"}]
    }
  ]
}
JSON

cat > "$TMPDIR/evidence_qc_same_owner_fail.json" <<'JSON'
{
  "evidence_complete_and_source_claim_covered": [
    {
      "id": "EQ_OWNER",
      "source_diversity_status": "PASS_MULTI_SOURCE",
      "source_independent_owner_count": 1,
      "source_independence_ledger": [{"host": "wire1.example.com", "owner": "WireCo"}, {"host": "wire2.example.com", "owner": "WireCo"}],
      "urls": ["https://wire1.example.com/a", "https://wire2.example.com/b"],
      "source_discovery_ledger": [{"query": "q"}],
      "fact_sources": [{"source_url": "https://wire1.example.com/a", "evidence_role": "primary_event_evidence"}, {"source_url": "https://wire2.example.com/b", "evidence_role": "secondary_event_evidence"}]
    }
  ]
}
JSON

cat > "$TMPDIR/evidence_qc_addable_merge_safe_fail.json" <<'JSON'
{
  "addable_merge_safe": [
    {"id": "EQ_INPUT", "source_diversity_status": "BOGUS", "urls": ["https://news.example.com/a"], "fact_sources": [{"source_url": "https://news.example.com/a", "evidence_role": "primary_event_evidence"}]}
  ]
}
JSON

cat > "$TMPDIR/content_audit_pass.json" <<'JSON'
{
  "content_enriched_and_language_polished": [{"id": "P1"}],
  "card_claim_diversity_audit": [{"card_id": "P1"}],
  "related_coverage_audit": [{"card_id": "P1"}]
}
JSON

cat > "$TMPDIR/content_audit_omitted_bucket_fail.json" <<'JSON'
{
  "content_hold_language_issue": [{"id": "HOLD1"}],
  "card_claim_diversity_audit": [{"card_id": "OTHER"}],
  "related_coverage_audit": [{"card_id": "OTHER"}]
}
JSON

pass "Stage A empty format_risk_tags pass" python3 "$ROOT/validation_scripts/stage_lineage_contract_check.py" stage_a "$TMPDIR/stage_a_empty_format_tags_pass.json"
fail "Stage A non-pass strict gate fail" python3 "$ROOT/validation_scripts/stage_lineage_contract_check.py" stage_a "$TMPDIR/stage_a_fail_nonpass_gate.json"
pass "Stage B evidence pass" python3 "$ROOT/validation_scripts/stage_b_evidence_gate.py" "$TMPDIR/stage_b_evidence_pass.json"
pass "Stage B blocked ledger reference pass" python3 "$ROOT/validation_scripts/stage_b_evidence_gate.py" "$TMPDIR/stage_b_blocked_reference_pass.json"
fail "Stage B unverified primary evidence fail" python3 "$ROOT/validation_scripts/stage_b_evidence_gate.py" "$TMPDIR/stage_b_unverified_primary_fail.json"
fail "Stage B duplicate output key fail" python3 "$ROOT/validation_scripts/stage_b_evidence_gate.py" "$TMPDIR/stage_b_duplicate_fail.json"
pass "Stage B package lineage pass" python3 "$ROOT/validation_scripts/stage_lineage_contract_check.py" stage_b "$TMPDIR/stage_b_lineage_package_pass.json"
fail "Stage B missing source-diversity lineage fail" python3 "$ROOT/validation_scripts/stage_lineage_contract_check.py" stage_b "$TMPDIR/stage_b_lineage_missing_fail.json"
fail "Stage C missing source-diversity lineage fail" python3 "$ROOT/validation_scripts/stage_lineage_contract_check.py" stage_c "$TMPDIR/stage_c_missing_lineage_fail.json"
pass "Evidence QC primary-source exception pass" python3 "$ROOT/validation_scripts/evidence_qc_v8_check.py" "$TMPDIR/evidence_qc_primary_exception_pass.json"
pass "Evidence QC held one-source caveat pass" python3 "$ROOT/validation_scripts/evidence_qc_v8_check.py" "$TMPDIR/evidence_qc_hold_single_pass.json"
fail "Evidence QC same-owner multi-source fail" python3 "$ROOT/validation_scripts/evidence_qc_v8_check.py" "$TMPDIR/evidence_qc_same_owner_fail.json"
fail "Evidence QC addable_merge_safe input bucket fail" python3 "$ROOT/validation_scripts/evidence_qc_v8_check.py" "$TMPDIR/evidence_qc_addable_merge_safe_fail.json"
pass "Content audit pass" python3 "$ROOT/validation_scripts/content_audit_check.py" "$TMPDIR/content_audit_pass.json"
fail "Content audit omitted bucket coverage fail" python3 "$ROOT/validation_scripts/content_audit_check.py" "$TMPDIR/content_audit_omitted_bucket_fail.json"

echo "All validation script smoke tests behaved as expected."
