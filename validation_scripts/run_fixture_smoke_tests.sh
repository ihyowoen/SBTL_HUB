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

cat > "$TMPDIR/stage_b_fail_missing_accounting.json" <<'JSON'
{
  "draft_cards": [],
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
  "stage_a_support_sources_attempted": true,
  "source_independence_ledger": [{"host": "example.gov"}],
  "source_unique_primary_count": 1,
  "source_unique_secondary_count": 1,
  "source_role_coverage": {"primary_event_evidence": 1},
  "source_synthesis_plan": "Use primary source plus secondary corroboration."
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

pass "stage_b evidence pass" python3 "$ROOT/validation_scripts/stage_b_evidence_gate.py" "$TMPDIR/stage_b_pass.json"
pass "stage_b schema-blocked accounting pass" python3 "$ROOT/validation_scripts/stage_b_evidence_gate.py" "$TMPDIR/stage_b_schema_blocked_pass.json"
fail "stage_b missing accounting fail" python3 "$ROOT/validation_scripts/stage_b_evidence_gate.py" "$TMPDIR/stage_b_fail_missing_accounting.json"
fail "stage_b duplicate output key fail" python3 "$ROOT/validation_scripts/stage_b_evidence_gate.py" "$TMPDIR/stage_b_fail_duplicate_output_key.json"
pass "stage_b lineage pass" python3 "$ROOT/validation_scripts/stage_lineage_contract_check.py" stage_b "$TMPDIR/stage_b_lineage_pass.json"
fail "stage_b lineage missing source-diversity fail" python3 "$ROOT/validation_scripts/stage_lineage_contract_check.py" stage_b "$TMPDIR/stage_b_lineage_fail_missing_source_diversity.json"
fail "stage_c missing lineage fail" python3 "$ROOT/validation_scripts/stage_lineage_contract_check.py" stage_c "$TMPDIR/stage_c_fail_missing_lineage.json"
fail "evidence complete bucket cannot hold HOLD status" python3 "$ROOT/validation_scripts/evidence_qc_v8_check.py" "$TMPDIR/evidence_qc_fail_complete_bucket_hold.json"
fail "single-source PASS_MULTI_SOURCE fail" python3 "$ROOT/validation_scripts/evidence_qc_v8_check.py" "$TMPDIR/evidence_qc_fail_pass_multi_single.json"
fail "content audit missing per-card coverage fail" python3 "$ROOT/validation_scripts/content_audit_check.py" "$TMPDIR/content_audit_fail_missing_coverage.json"

echo "All validation script smoke tests behaved as expected."
