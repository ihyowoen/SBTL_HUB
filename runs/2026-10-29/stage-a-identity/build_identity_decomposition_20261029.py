#!/usr/bin/env python3
"""Create-only, evidence-bound Stage A case graph; never asserts formal 0.1P PASS."""
from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[3]
WORKSPACE = ROOT.parent
OUT = Path(__file__).resolve().parent
PRIOR = WORKSPACE / "stagea_reconciliation_20261028"
SOURCE = WORKSPACE / "STAGE_A_REASSESSMENT_LEDGER_1330_20261027.source.csv"
QUEUE = PRIOR / "STAGE_A_1285_IDENTITY_PENDING_QUEUE_20261028.csv"
SPEC = OUT / "IDENTITY_DECOMPOSITION_INPUT_20261029.json"
EXPECTED_SOURCE_SHA = "5e78420916b0c1d70ff56bf928779cd969b94fbb15dd4119c841872997486116"
EXPECTED_FULL_BLOB = "07a91714e56be2a8bfad10ab63822f0c5cb3f06e"


def digest(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def load_csv(path: Path) -> list[dict]:
    with path.open(encoding="utf-8-sig", newline="") as stream:
        return list(csv.DictReader(stream))


def put_json(filename: str, obj: object) -> Path:
    p = OUT / filename
    with p.open("x", encoding="utf-8", newline="\n") as stream:
        json.dump(obj, stream, ensure_ascii=False, indent=2)
        stream.write("\n")
    return p


def put_csv(filename: str, rows: list[dict], fields: list[str]) -> Path:
    p = OUT / filename
    with p.open("x", encoding="utf-8-sig", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)
    return p


def main() -> None:
    assert digest(SOURCE) == EXPECTED_SOURCE_SHA, "Locked 1330 baseline CSV changed"
    baseline_blob = subprocess.check_output(
        ["git", "-C", str(ROOT), "rev-parse", "HEAD:data/cards.full.json"], text=True
    ).strip()
    assert baseline_blob == EXPECTED_FULL_BLOB, "Locked canonical Full blob changed"
    baseline = load_csv(SOURCE)
    pending = load_csv(QUEUE)
    src_id_key = "candidate_id"
    original_ids = [r[src_id_key] for r in baseline]
    queue_ids = [r[src_id_key] for r in pending]
    assert len(baseline) == 1330 and len(set(original_ids)) == 1330
    assert len(pending) == 1285 and len(set(queue_ids)) == 1285
    assert set(queue_ids) <= set(original_ids)

    spec = json.loads(SPEC.read_text(encoding="utf-8"))
    prior_groups = {}
    for group, name in spec["prior_case_groups"].items():
        p = PRIOR / name
        prior_groups[group] = json.loads(p.read_text(encoding="utf-8"))

    # Lexical shortlist across all 1,676 locked cards; NOT a semantic Related gate.
    cards_obj = json.loads((ROOT / "data/cards.full.json").read_text(encoding="utf-8"))
    cards = cards_obj["cards"]
    assert cards_obj["total"] == len(cards) == 1676
    assert len(set(c["id"] for c in cards)) == 1676
    terms = {
        "EVE_IAA_AGREEMENTS_20260919": ["EVE Energy", "EVE ", "이브에너지", "亿纬"],
        "ECOPROBM_CATL_TALKS_202609": ["에코프로비엠", "Ecopro BM"],
        "NIO_GEELY_20260927_DUAL_EQUITY": ["NIO", "니오", "Geely", "지리차"],
        "NYSERDA_BULK_BESS_AWARDS_20260923": ["NYSERDA", "KCE NY", "뉴욕주"],
        "BORZESTI_918MWH_CEE_202609": ["Borzesti", "보르제스티", "Renovatio"],
        "GLOBAL_LITHIUM_TITAN_SID_20260921": ["Global Lithium", "글로벌리튬", "Manna"],
        "GRIDSTOR_WHITE_TANK_FINANCING_202609": ["GridStor", "White Tank"],
        "JUPITER_FOUR_FINANCINGS_PORTFOLIO_20260916": ["Jupiter Power", "주피터파워"],
        "KEPCO_KPS_HASANG_STAKE_20260922": ["Hasang", "하상", "한전KPS"],
        "RWE_MOERDIJK_FID_20260921": ["Moerdijk", "모어다이크", "RWE"],
        "FORM_ENERGY_CREDIT_20260921": ["Form Energy", "폼 에너지"],
        "ZHEJIANG_ESS_SPOT_NOTICE_20260923": ["Zhejiang", "저장성", "浙江"],
        "KPX_ESS_SHEET_FORMULA_20261014": ["KPX", "전력거래소", "중앙계약시장"],
        "EREX_SANBU_BESS_COD_20261020": ["eRex", "이렉스", "イーレックス", "山武"],
        "HITACHI_CANADA_PRESSBOARD_20261016": ["Hitachi Energy", "히타치에너지", "pressboard", "프레스보드"],
    }
    assert set(terms) == {c["package_id"] for c in spec["cases"]}
    package_records = []
    source_to_package = {}
    unit_ids = set()
    prior_id_count = 0
    new_id_count = 0
    for case in spec["cases"]:
        package_id = case["package_id"]
        if "prior_group" in case:
            group = prior_groups[case["prior_group"]]
            old_case = (group["reviewed_cases"] if case["prior_group"] == "five" else group["cases"])[case["prior_index"]]
            source_ids = old_case.get("source_ids") or old_case["original_source_ids"]
            old_url = old_case.get("issuer_url") or old_case.get("authority_url") or old_case.get("primary_owner_url") or old_case.get("observation_url")
            assert old_url, f"Missing prior owner/source URL: {package_id}"
            assert old_url.rstrip("/") == case["owner_url"].rstrip("/"), f"Prior evidence URL unexpectedly diverged: {package_id}"
            prior_id_count += len(source_ids)
        else:
            source_ids = case["new_case_original_source_ids"]
            new_id_count += len(source_ids)
        assert len(source_ids) == len(set(source_ids)) and source_ids
        assert set(source_ids) <= set(queue_ids)
        representative = case.get("representative_source_id", source_ids[0])
        assert representative in source_ids
        for i in source_ids:
            assert i not in source_to_package, f"Source ID placed in two packages: {i}"
            source_to_package[i] = (package_id, representative)
        units = []
        for u in case["units"]:
            item = dict(u)
            item["event_unit_id"] = f"{package_id}::{u['id']}"
            assert item["event_unit_id"] not in unit_ids
            unit_ids.add(item["event_unit_id"])
            assert item["actor_asset"] and item["action"] and item["date_role"] and item["status"]
            units.append(item)
        assert units
        search = []
        for card in cards:
            blob = " ".join(str(card.get(k, "")) for k in ("title", "sub", "summary", "desc"))
            matching = [t for t in terms[package_id] if t.casefold() in blob.casefold()]
            if matching:
                search.append({"card_id": card["id"], "card_date": card.get("date"), "title": card.get("title"), "matched_search_terms": matching, "semantic_related_verdict": "NOT_ADJUDICATED"})
        package_records.append({
            "package_id": package_id,
            "original_source_ids": source_ids,
            "representative_observation_id_for_review_not_final_article": representative,
            "support_observation_ids": [i for i in source_ids if i != representative],
            "original_metadata_score_by_source_id": {r["candidate_id"]: r["metadata_score_not_a_final_rank"] for r in pending if r["candidate_id"] in source_ids},
            "original_pool_by_source_id": {r["candidate_id"]: r["original_pool"] for r in pending if r["candidate_id"] in source_ids},
            "primary_or_reporting_evidence_url": case["owner_url"],
            "evidence_locator": case["source_locator"],
            "underlying_units": units,
            "nonexecuted_terms": case.get("nonexecuted_terms", []),
            "package_fact": case.get("package_fact"),
            "hold_reason": case["hold_reason"],
            "full_1676_lexical_search_shortlist_only": search,
            "lexical_matches_are_not_same_event_or_related_pass": True,
            "formal_stage_a_0_1p_status": "HOLD_NOT_NATIVE_ADJUDICATED",
            "final_independent_card_count": None,
        })

    assert len(spec["cases"]) == 15 and len(source_to_package) == 25
    assert prior_id_count == 23 and new_id_count == 2
    assert len(unit_ids) == 27
    assert len(set(source_to_package)) == 25
    assert sum(len(p["original_source_ids"]) for p in package_records) == 25

    cases_by_id = {p["package_id"]: p for p in package_records}
    assert len(cases_by_id["NIO_GEELY_20260927_DUAL_EQUITY"]["underlying_units"]) == 2
    assert len(cases_by_id["NYSERDA_BULK_BESS_AWARDS_20260923"]["underlying_units"]) == 8
    assert len(cases_by_id["JUPITER_FOUR_FINANCINGS_PORTFOLIO_20260916"]["underlying_units"]) == 4
    assert sum(u["usd_million"] for u in cases_by_id["JUPITER_FOUR_FINANCINGS_PORTFOLIO_20260916"]["underlying_units"]) == 1369
    assert len(cases_by_id["KPX_ESS_SHEET_FORMULA_20261014"]["underlying_units"]) == 2
    assert sum(1 for p in package_records if "watchlist_context_pool" in p["original_pool_by_source_id"].values()) == 1

    overlay = []
    for orig in baseline:
        sid = orig["candidate_id"]
        case_link = source_to_package.get(sid)
        if case_link:
            p = cases_by_id[case_link[0]]
            state = "EVIDENCE_BOUND_CASE_LINK_RESEARCHED_BUT_0_1P_PENDING"
        else:
            p = None
            state = "UNREVIEWED_0_1P_PENDING" if sid in queue_ids else "PRIOR_0_1P_SCOPE_UNCHANGED"
        overlay.append({
            "candidate_id": sid,
            "original_pool": orig["stage_a_pool"],
            "original_economic_event_cluster_id": orig.get("economic_event_cluster_id", ""),
            "original_gate_status": orig["assessment_status"],
            "original_reassessment_status": orig["promotion_reassessment_status"],
            "original_metadata_score_not_final_rank": orig["decision_news_value_score"],
            "original_date_role_sha256_not_reclassified": hashlib.sha256(orig["date_role"].encode("utf-8")).hexdigest(),
            "original_related_prepass_sha256_not_reclassified": hashlib.sha256(orig["related_prepass"].encode("utf-8")).hexdigest(),
            "baseline_source_row_unchanged": "true",
            "incremental_identity_research_state": state,
            "evidence_bound_case_package_id": case_link[0] if case_link else "",
            "representative_observation_id_not_final": case_link[1] if case_link else "",
            "case_unit_count_not_final_article_count": str(len(p["underlying_units"])) if p else "",
            "evidence_url_not_source_substitution": p["primary_or_reporting_evidence_url"] if p else "",
            "formal_0_1P_new_pass": "false",
        })
    assert [o["candidate_id"] for o in overlay] == original_ids
    assert len(overlay) == 1330
    assert all(o["original_pool"] and o["original_gate_status"] for o in overlay)
    assert [o["original_pool"] for o in overlay] == [r["stage_a_pool"] for r in baseline]
    assert [o["original_gate_status"] for o in overlay] == [r["assessment_status"] for r in baseline]
    assert Counter(r["incremental_identity_research_state"] for r in overlay) == {
        "EVIDENCE_BOUND_CASE_LINK_RESEARCHED_BUT_0_1P_PENDING": 25,
        "UNREVIEWED_0_1P_PENDING": 1260,
        "PRIOR_0_1P_SCOPE_UNCHANGED": 45,
    }

    source_edges = []
    for p in package_records:
        for sid in p["original_source_ids"]:
            source_edges.append({
                "original_source_id": sid,
                "original_pool": p["original_pool_by_source_id"][sid],
                "provisional_case_package_id": p["package_id"],
                "observation_role_in_this_research": "review_observation" if sid == p["representative_observation_id_for_review_not_final_article"] else "additional_observation",
                "underlying_event_unit_ids_from_package_owner_not_article_claimed": "|".join(u["event_unit_id"] for u in p["underlying_units"]),
                "issuer_or_reporting_owner_url": p["primary_or_reporting_evidence_url"],
                "formal_0_1P_disposition": "HOLD",
            })
    assert len(source_edges) == 25
    assert all(r["original_source_id"] in queue_ids for r in source_edges)

    produced = []
    produced.append(put_json("STAGE_A_15_CASE_EVENT_DECOMPOSITION_V2_20261029.json", {
        "schema": spec["schema"],
        "stage": "A_0_1P_IDENTITY_RESEARCH_NOT_FORMAL_PASS",
        "as_of_kst": spec["as_of_kst"],
        "source_to_package_to_underlying_unit_semantics": "Source IDs are observations. Case packages group evidence; underlying units separate actions/assets. A unit is not automatically one eligible card.",
        "source_original_1330_sha256": digest(SOURCE),
        "locked_full_git_blob": baseline_blob,
        "packages": package_records,
    }))
    produced.append(put_csv("STAGE_A_25_SOURCE_TO_CASE_EDGES_V2_20261029.csv", source_edges, list(source_edges[0])))
    produced.append(put_csv("STAGE_A_1330_SOURCE_NO_LOSS_IDENTITY_OVERLAY_V2_20261029.csv", overlay, list(overlay[0])))

    receipt = {
        "as_of_kst": spec["as_of_kst"],
        "validator": "independent_create_only_identity_accounting_QC_not_native_stage_a_validator",
        "result": "PASS_ACCOUNTING_AND_EVIDENCE_BOUND_GRAPH_ONLY",
        "native_stage_a_artifact_contract": "NOT_EXECUTED_NO_FORMAL_STAGE_A_ARTIFACT",
        "native_stage_a_lineage_contract": "NOT_EXECUTED_NO_FORMAL_STAGE_A_ARTIFACT",
        "baseline_source_count": 1330,
        "baseline_source_id_unique_count": 1330,
        "prior_0_1P_individually_judged_source_ids_unchanged": 45,
        "original_0_1P_pending_source_ids_unchanged": 1285,
        "pending_source_ids_with_additional_evidence_link": 25,
        "pending_source_ids_without_this_case_bound_evidence": 1260,
        "new_strict_promotions": 0,
        "final_exclusions": 0,
        "source_ids_dropped": 0,
        "packages_with_identity_evidence": 15,
        "distinct_underlying_action_asset_units_in_these_packages": 27,
        "underlying_units_are_not_article_count": True,
        "watch_source_ids_identity_reopened_without_formal_pool_change": 2,
        "locked_full_count": len(cards),
        "locked_full_git_blob": baseline_blob,
        "full_keyword_lookups_done_per_case": 15,
        "lexical_shortlists_are_not_same_event_or_related_decisions": True,
        "key_boundary_checks": [
            "NIO: two conditional equity subscriptions, not a single executed sale; RMB16bn post-money valuation differs from RMB640m cash consideration",
            "NYSERDA: eight distinct award assets and aggregate 950MW, no already operating assets inferred; separate non-ESS renewable awards",
            "Jupiter: four financing closes April-July for 10 assets, $1,369m rounded amounts, issuer 3,600MWh not input 3,800MWh",
            "KPX: two different amended tender spreadsheets, not a new awarded ESS procurement",
            "WATCH Hasang: signed contract remains in WATCH until formal Stage A reclassification"
        ],
        "input_sha256": {str(p.name): digest(p) for p in [SOURCE, QUEUE, SPEC] + [PRIOR / n for n in spec["prior_case_groups"].values()]},
        "output_sha256": {p.name: digest(p) for p in produced},
        "next_single_bottleneck": "Complete case-specific semantic Related and four Stage A V4 gates, starting with NIO two-equity package and NYSERDA eight-award package; then create a full-source-native Stage A artifact if eligible."
    }
    produced.append(put_json("STAGE_A_15_CASE_IDENTITY_GRAPH_QC_RECEIPT_V2_20261029.json", receipt))
    print(json.dumps({"result": receipt["result"], "counts": [1330, 1285, 25, 15, 27, 1260], "files": [p.name for p in produced]}, ensure_ascii=False))


if __name__ == "__main__":
    main()
