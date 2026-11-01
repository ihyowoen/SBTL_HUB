#!/usr/bin/env python3
"""Independent fail-closed QC: CP16 -> CP18 six-source formal Stage A delta.

This is deliberately separate from the code that writes the Stage A artifact.
Native artifact and lineage validators must also be run; this script checks
source identity, arithmetic, economic-act separation, and preservation.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter
from pathlib import Path
from urllib.parse import parse_qs, urlsplit


def sha(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def load(path: Path) -> dict:
    with path.open(encoding="utf-8") as f:
        return json.load(f)


def main() -> None:
    ap = argparse.ArgumentParser()
    for item in ("baseline", "current", "full", "pre_native", "corrected_cp17", "cp17_qc", "receipt", "out"):
        ap.add_argument("--" + item.replace("_", "-"), type=Path, required=True)
    p = ap.parse_args()
    b, d, full = load(p.baseline), load(p.current), load(p.full)
    pre, cp17, cp17qc, rec = (load(x) for x in (p.pre_native,p.corrected_cp17,p.cp17_qc,p.receipt))
    B, D = b["decision_ledger"], d["decision_ledger"]
    checks: dict[str, bool] = {}
    checks["base_file_matches_anchored_sha"] = sha(p.baseline) == "d36893b263dfed269388d40680a7896ebee0b68127619cded66baeb951084fef"
    checks["full_file_matches_anchored_sha"] = sha(p.full) == "d22f0d4e39e035b9537b3e9abdf48abe6b7eb80f7e477e87aff1284f9e27e0d9"
    checks["receipt_matches_current_file"] = rec["output_sha256"] == sha(p.current)
    checks["original_source_1330_identity_and_order"] = (
        len(B) == len(D) == 1330 and
        len({r["story_id"] for r in D}) == 1330 and
        all((x["story_id"],x["source_row_index"],x["headline_raw"],x["primary_url"])
            == (y["story_id"],y["source_row_index"],y["headline_raw"],y["primary_url"])
            for x,y in zip(B,D))
    )
    old_byid={r["story_id"]:r for r in B}
    new_byid={r["story_id"]:r for r in D}
    affected={8,48,228,244,614,916}
    checks["exactly_six_source_rows_have_decision_change"] = (
        {int(k["source_row_index"]) for k in D if k != old_byid.get(k["story_id"])} == affected
    )
    previous_formal={r["candidate_id"]:r for r in b["promotion_reassessment_ledger"]}
    current_formal={r["candidate_id"]:r for r in d["promotion_reassessment_ledger"]}
    checks["99_prior_formal_decisions_untouched"] = (
        len(previous_formal) == 99 and
        all(current_formal.get(sid)==record for sid,record in previous_formal.items())
    )
    new_formal=set(current_formal)-set(previous_formal)
    expected_sids={B[i]["story_id"] for i in affected}
    checks["six_formal_additions_match_exact_source_ids"] = (
        len(current_formal)==105 and new_formal==expected_sids
        and all(current_formal[sid]["promotion_reassessment_status"].startswith(("PROMOTED_","FORMAL_"))
                for sid in new_formal)
    )
    spec=b["strict_passed_spec"]
    cur=d["strict_passed_spec"]
    checks["prior_18_strict_specs_identical"] = len(spec)==18 and cur[:18]==spec
    checks["strict_20_no_stage_b_fact_or_card_write"] = (
        len(cur)==20 and
        all(s.get("stage_b_authorized") is not True
            and s.get("accepted_facts_approved") is not True
            and s.get("canonical_card_write_allowed") is not True
            for s in cur)
    )
    reps={s["source_row_index"]:s for s in cur[18:]}
    checks["two_independent_strict_representatives"] = set(reps)=={48,244}
    checks["strict_ids_and_events_distinct_from_existing_full"] = (
        len({s["economic_event_cluster_id"] for s in cur})==len(cur)
        and all(s["economic_event_cluster_id"] not in {"KR_ESS_CENTRAL_TENDER_1180MW_20260922","2026-09-22_KR_01"}
                for s in cur[18:])
    )
    checks["commercial_contract_primary_owner_and_contract_stage"] = (
        "askinno.com/archives/171570" in json.dumps(reps.get(48,{}),ensure_ascii=False)
        and "20260917800658" in json.dumps(reps.get(48,{}),ensure_ascii=False)
        and "161,733,060,000" in json.dumps(reps.get(48,{}),ensure_ascii=False)
        and "not cash received" in json.dumps(reps.get(48,{}),ensure_ascii=False)
    )
    checks["magnet_mou_official_owner_and_estimate_not_actual"] = (
        "newsId=156782918" in json.dumps(reps.get(244,{}),ensure_ascii=False)
        and "14,000" in json.dumps(reps.get(244,{}),ensure_ascii=False)
        and "15 metric tonnes" in json.dumps(reps.get(244,{}),ensure_ascii=False)
        and "NOT magnets recovered" in json.dumps(reps.get(244,{}),ensure_ascii=False)
        and "policy_regulatory_anchor" not in reps.get(244,{}).get("anchor_classes",[])
    )
    edges={i:D[i].get("formal_0_1P_cp18_source_to_economic_act_edges_20261101",[]) for i in affected}
    checks["every_affected_source_contains_multiple_economic_act_edges"] = all(len(v)>=2 for v in edges.values())
    checks["mixed_ESS_source_keeps_LNF_and_tender_distinct"] = all(
        {"KR_SKON_LNF_LFP_CATHODE_SUPPLY_CONTRACT_20260917","KR_ESS_CENTRAL_TENDER_1180MW_20260922"}
        <= {v["event"] for v in edges[i]} for i in (48,228)
    )
    checks["mixed_magnet_source_keeps_MOU_and_tender_distinct"] = all(
        {"KR_EOL_EV_HEV_MOTOR_RE_MAGNET_PILOT_MOU_20260922","KR_ESS_CENTRAL_TENDER_1180MW_20260922"}
        <= {v["event"] for v in edges[i]} for i in (244,614)
    )
    checks["same_impacton_article_source_ids_both_preserved"] = (
        urlsplit(B[244]["primary_url"]).netloc==urlsplit(B[614]["primary_url"]).netloc
        and B[244]["primary_url"]==B[614]["primary_url"]
        and D[614].get("same_exact_article_url_duplicate_of")==B[244]["story_id"]
    )
    checks["factorial_existing_strict_and_historical_deal_not_double_promoted"] = (
        D[8].get("factorial_owner_prior_agreement_date")=="2026-02-05"
        and any(x["event"]=="FACTORIAL_KARMA_20260205" for x in edges[8])
        and current_formal[B[8]["story_id"]]["after_pool"]=="reject_or_support_only_pool"
    )
    checks["kpx_registration_followup_not_award"] = (
        D[916].get("actual_registration_quantity_verified") is False
        and D[916].get("not_second_tender_announcement") is True
        and current_formal[B[916]["story_id"]]["after_pool"]=="watchlist_context_pool"
    )
    checks["pool_and_review_partition_exact"] = (
        {key:len(d[key]) for key in ("strict_passed_spec","candidate_review_pool",
           "watchlist_context_pool","reject_or_support_only_pool","existing_reinforcement")}
        == {"strict_passed_spec":20,"candidate_review_pool":581,"watchlist_context_pool":660,
            "reject_or_support_only_pool":39,"existing_reinforcement":30}
        and len(d["review_pool_resolution_ledger"])==1280
    )
    checks["sum_disjoint_final_pool_partition_1330"] = (
        sum(len(d[key]) for key in ("strict_passed_spec","candidate_review_pool",
          "watchlist_context_pool","reject_or_support_only_pool","existing_reinforcement"))==1330
    )
    checks["remaining_1225_and_cumulative_105"] = (
        len(D)-len(current_formal)==1225 and rec["formal_pending"]==1225
        and d["summary"]["processed_priority_source_observations"]==105
        and d["summary"]["unprocessed_editorial_observations"]==1225
    )
    original54 = {i for g in pre["case_definitions"] for i in g["source_row_indices"]}
    formally_index={r["source_row_index"] for r in D if r["story_id"] in current_formal}
    checks["pre_native_54_fully_formal"] = len(original54)==54 and original54<=formally_index
    checks["cp17_correction_independent_QC_pass"] = cp17qc["status"]=="PASS" and all(cp17qc["checks"].values())
    cp17roster={r["source_row_index"]:r for r in cp17["source_roster"]}
    checks["DAPA_query_docSeq_not_bbsSeq_separated"] = (
        len(cp17roster)==1231
        and parse_qs(urlsplit(B[1297]["primary_url"]).query).get("docSeq")
            !=parse_qs(urlsplit(B[1309]["primary_url"]).query).get("docSeq")
        and cp17roster[1297]["source_review_unit_id"]!=cp17roster[1309]["source_review_unit_id"]
    )
    checks["cp17_corrected_units_not_claimed_as_formal_events"] = (
        len(cp17["source_review_units"])==1130
        and cp17["quality_summary"]["new_formal_decisions"]==0
    )
    checks["global_hold_production_main_unmodified"] = (
        d["formal_0_1P_cp18_completed_original54_20261101"]["global_stage_a_status"]=="HOLD_OPEN_1225_UNADJUDICATED"
        and d["formal_0_1P_cp18_completed_original54_20261101"]["canonical_main_full_related_mutations"]==0
        and d["formal_0_1P_cp18_completed_original54_20261101"]["stage_b_executed"] is False
    )
    result={
        "status":"PASS" if all(checks.values()) else "FAIL",
        "checks":checks,
        "counts_independent":{
            "source_ids":len(D),"old_formal":len(previous_formal),"new_formal":len(new_formal),
            "cumulative_formal":len(current_formal),"pending":len(D)-len(current_formal),
            "strict":len(cur),"corrected_cp17_source_review_units":len(cp17["source_review_units"]),
            "pre_native_source_ids_all_resolved":len(original54),
        },
        "sha256":{
            "baseline_native":sha(p.baseline),"formal_cp18":sha(p.current),
            "full_reference":sha(p.full),"corrected_cp17":sha(p.corrected_cp17),
            "cp17_independent_qc":sha(p.cp17_qc),"receipt":sha(p.receipt),
        },
        "interpretation":"Source-level and partition-level independent QC. Native artifact+lineage checks separately required. Two strict selectors do not authorize Stage B or publication.",
    }
    p.out.write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({"status":result["status"],"count":len(checks),
                      "failed":[key for key,valid in checks.items() if not valid],
                      "counts":result["counts_independent"]},ensure_ascii=False,indent=2))
    if result["status"]!="PASS":
        raise SystemExit(1)


if __name__=="__main__":
    main()
