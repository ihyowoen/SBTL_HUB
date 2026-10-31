#!/usr/bin/env python3
"""Integrity and scope validation; does NOT issue a Stage A 0.1P PASS."""
from pathlib import Path
import hashlib, json, sys
HERE=Path(__file__).resolve().parent
def load(name, sha):
    p=HERE/name
    b=p.read_bytes()
    actual=hashlib.sha256(b).hexdigest()
    assert actual==sha, (name,actual,sha)
    return json.loads(b)
case=load("STAGE_A_HIGH60_LAST16_CASE_TRIAGE_20261030.json","ae4ac8e700b52b2144c4f22f9f8d24a41d725957aba7f7a403e4d8a608d851f3")
qc=load("STAGE_A_LAST16_MIXED_TIER_INDEPENDENT_NO_LOSS_QC_20261030.json","488d2b8a1f9d83a7f3bf4ba3404ff257f86a5a5f59aec0af939a00eab18d3c3d")
ids=[sid for c in case["cases"] for sid in c["source_ids"]]
assert len(case["cases"])==14 and len(ids)==len(set(ids))==16
assert case["native_0_1P_promotions"]==0
assert qc["original_sources"]==1330
assert qc["cumulative_bounded_or_triaged_source_ids"]==137
assert qc["high60_review_pool_ids"]==103
assert qc["high60_review_pool_bounded_case_or_triage_links"]==103
assert qc["formal_individual_0_1P_pending_unchanged"]==1285
assert qc["new_native_strict_passes"]==0
assert qc["native_stage_artifact_contract_A_executed"] is False if "native_stage_artifact_contract_A_executed" in qc else True
print(json.dumps({"scope":"bounded_only_not_native_pass","last16":16,"cases":14,"covered_60plus":103,"formal_pending":1285},ensure_ascii=False))
