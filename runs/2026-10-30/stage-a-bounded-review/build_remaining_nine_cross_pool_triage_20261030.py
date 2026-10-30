#!/usr/bin/env python3
"""Create-only non-decisional source-body triage for the nine mixed-pool URL groups.

It retains all original Source IDs, score/pool observations, and known provenance;
no case in this artifact is a validated strict Stage A promotion.
"""

import argparse
import csv
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
SOURCE_SHA = "5e78420916b0c1d70ff56bf928779cd969b94fbb15dd4119c841872997486116"
PREVIOUS_FIVE = {
    "SOURCE_URL_OBSERVATION_5d3fdcc933c7f7a4",
    "SOURCE_URL_OBSERVATION_f44871dd75510fb2",
    "SOURCE_URL_OBSERVATION_92f1ea991802c759",
    "SOURCE_URL_OBSERVATION_94295fcc406594a2",
    "SOURCE_URL_OBSERVATION_fc68908b1bcbea62",
}

# These are evidence-bounded source-pair triage hypotheses. Where an article is a
# composite editorial roundup, its underlying acts remain explicitly unresolved.
# Scores are provisional Stage A dimensions, never the unchanged source metadata.
CASES = {
    "SOURCE_URL_OBSERVATION_7fd3a0e253a607f9": {
        "topic": "Korea–Australia 2026-09-22 leaders' discussion of LNG, clean energy and critical minerals",
        "economic_identity_status": "BILATERAL_SUMMIT_DISCUSSION_VERIFIED_NOT_NEW_SUPPLY_CONTRACT",
        "source_body_access": "Hankook Daily original inaccessible; Korean presidential office written briefing obtained",
        "actual_event_date": "2026-09-22", "official_publication_date": "2026-09-23",
        "before_after": "Two existing strategic partners discussed energy security and mineral/renewables potential; no newly signed mineral purchase or extraction project confirmed.",
        "execution_credibility_gate": "PASS", "independent_cardability_gate": "REVIEW",
        "score_breakdown": [13, 14, 0, 0, 4, 2, 2, 1], "novelty_cap_basis": "unsupported_political_rhetoric",
        "publication_urgency": "monitor", "related_and_date_role_hold": "Meeting Sep22 versus Sep23 reporting; find binding MoU or procurement and older bilateral agreements before any standalone card.",
        "source_owner_evidence": [{"owner": "Republic of Korea Presidential Office", "url": "https://www.korea.kr/briefing/presidentView.do?newsId=148972462", "role": "official_2026_09_23_summit_briefing"}],
        "evidence_gap": "Original target media body and binding minerals/ESS deal instrument not shown."
    },
    "SOURCE_URL_OBSERVATION_670c29a37b1d8295": {
        "topic": "OFweek opinion: vehicle OEM diversification away from exclusive CATL supply",
        "economic_identity_status": "MULTI_COMPANY_EDITORIAL_BUNDLE_NOT_AN_INDEPENDENT_DE_CATL_TERMINATION_EVENT",
        "source_body_access": "OFweek article dated Sep24 readable; multiple June and September OEM claims, unsigned editorial opinion",
        "actual_event_date": None, "official_publication_date": "2026-09-24",
        "before_after": "Article groups Xiaomi/LI Auto/AITO and other disparate supplier strategies; it explicitly acknowledges CATL persists. Supplier switches/investments cannot be merged into one 'collective breakup' decision.",
        "execution_credibility_gate": "REVIEW", "independent_cardability_gate": "REVIEW",
        "score_breakdown": [18, 13, 0, 2, 0, 2, 1, 1], "novelty_cap_basis": "repeated_announcement_no_new_fact",
        "publication_urgency": "monitor", "related_and_date_role_hold": "Each underlying OEM supplier/ownership action needs company statement and independent earliest event date; the Sep24 opinion dateline is not an event date.",
        "source_owner_evidence": [{"owner": "OFweek opinion by 车界锐评", "url": "https://libattery.ofweek.com/2026-09/ART-36001-12003-30704707.html", "role": "editorial_source_composite_not_original_company_owners"}],
        "evidence_gap": "Xiaomi battery brands, Li Auto–Sunwoda investment and AITO suppliers need bilateral first-party event evidence before cardability or economic grouping."
    },
    "SOURCE_URL_OBSERVATION_ed4e0049260cb066": {
        "topic": "OFweek CATL supply-chain-cycle commentary: shares repurchase, 587Ah listing, ESS price changes and OEM competition",
        "economic_identity_status": "BUNDLE_WITH_POTENTIALLY_DISTINCT_CAPITAL_MARKET_PRODUCT_PRICE_ACTS",
        "source_body_access": "OFweek article dated Sep24 readable; underlying CATL share buyback and store snapshots not independently retrieved",
        "actual_event_date": None, "official_publication_date": "2026-09-24",
        "before_after": "Source claims Sep21 CATL A-share buyback and 587Ah store listing, while discussing ESS 280/314Ah price increases and 2% battery excise tax. The latter was already recorded in locked Full card 2026-09-09_CN_01; tax authority confirms rule effective Sep1.",
        "execution_credibility_gate": "REVIEW", "independent_cardability_gate": "REVIEW",
        "score_breakdown": [18, 14, 0, 5, 0, 1, 1, 1], "novelty_cap_basis": "none",
        "publication_urgency": "monitor", "related_and_date_role_hold": "Resolve CATL issuer Sept21 buyback filing, exact cell SKU and Sep21 store price, and separate preexisting Sept1 tax/Sept9 Full price card; never use Sep24 commentary as fresh tax effective date.",
        "source_owner_evidence": [
            {"owner": "OFweek columnist 不慌实验室", "url": "https://libattery.ofweek.com/2026-09/ART-36001-12003-30704811.html", "role": "secondary_composite_with_unsourced_operating_claims"},
            {"owner": "China Ministry of Finance and State Tax Administration", "url": "https://fgk.chinatax.gov.cn/zcfgk/c102416/c5251171/content.html", "role": "primary_tax_instrument_2026_no20_2pct_from_sept01_4pct_from_2027_sept01"}
        ],
        "evidence_gap": "CATL stock-market buyback/commerce store first-party timestamp and new-offer scope unverified."
    },
    "SOURCE_URL_OBSERVATION_2b6ee2d0219d7b3f": {
        "topic": "Gaoneng Shuzhao sulfide all-solid-state wet-process small pilot manufacturing line promotional article",
        "economic_identity_status": "PROMOTIONAL_EQUIPMENT_OFFER_NO_INDEPENDENT_VALIDATION_OR_CONFIRMED_CUSTOMER_DELIVERY",
        "source_body_access": "Original OFweek unavailable; full self-promotional text mirrored by ChinaBattery/SMM",
        "actual_event_date": None, "official_publication_date": "2026-09-23",
        "before_after": "Content claims an engineered wet-process product-level sample platform with ±1.5% coating precision and 300–500mm line width, but provides no identifiable contract delivery/customer acceptance, independent yield data or industrial-scale commissioning.",
        "execution_credibility_gate": "REVIEW", "independent_cardability_gate": "REVIEW",
        "score_breakdown": [12, 9, 4, 3, 0, 2, 2, 1], "novelty_cap_basis": "company_target_without_validation_or_effect",
        "publication_urgency": "monitor", "related_and_date_role_hold": "Marketing repost publication cannot be treated as independent technology commercialization date or proven customer deliverable.",
        "source_owner_evidence": [{"owner": "高能数造头条 via Shanghai Metals Market", "url": "https://news.smm.cn/news/104132288", "role": "company_marketing_reprint_not_independent_test"}],
        "evidence_gap": "Original manufacturer technical document, named delivery/customer acceptance, test methods and verifiable yield/longevity."
    },
    "SOURCE_URL_OBSERVATION_89127d43510c41f2": {
        "topic": "DealSite Economy TV analysis: Korean battery companies ESS demand upside versus leverage/retrofit costs",
        "economic_identity_status": "ANALYTICAL_MULTICOMPANY_CONTEXT_NOT_NEW_SINGLE_FINANCIAL_EVENT",
        "source_body_access": "Original 176299 403; publisher indexed news-list synopsis available, Sep26 headline and intro",
        "actual_event_date": None, "official_publication_date": "2026-09-26",
        "before_after": "Multi-company commentary states LGES/Samsung SDI/SK On ESS demand may precede profit recovery and that transformation capex/debt are important; no issuer-period financial figures are proved by accessible article body.",
        "execution_credibility_gate": "REVIEW", "independent_cardability_gate": "REVIEW",
        "score_breakdown": [12, 14, 0, 5, 0, 2, 1, 1], "novelty_cap_basis": "repeated_announcement_no_new_fact",
        "publication_urgency": "monitor", "related_and_date_role_hold": "Need company-specific financial reports, net debt/working capital/capex before earnings_deep_dive and any new issuer event; do not infer a single earnings release date.",
        "source_owner_evidence": [{"owner": "DealSite Economy TV", "url": "https://news.dealsitetv.com/news/all?endDt=2026-09-26", "role": "publisher_owned_listing_with_synopsis_not_full_article"}],
        "evidence_gap": "Full 176299 body inaccessible; primary issuer filings and numbers not yet reconciled."
    },
    "SOURCE_URL_OBSERVATION_d1db33f824403da4": {
        "topic": "Sustainable Holdings (Japan) AirElixir off-grid PV-battery atmospheric-water system proposed package",
        "economic_identity_status": "FIRST_PARTY_OFFERING_PROPOSAL_NOT_TESTED_CUSTOMER_DEPLOYMENT",
        "source_body_access": "Issuer PR Times Sep25 full first-party press release readable",
        "actual_event_date": "2026-09-25", "official_publication_date": "2026-09-25",
        "before_after": "Company proposes bundled 74.8kW PV, industrial battery and water generator for off-grid use, with up-to-1,000L/day figure depending on conditions; no ESS energy MWh or customer installation proven.",
        "execution_credibility_gate": "PASS", "independent_cardability_gate": "REVIEW",
        "score_breakdown": [10, 8, 4, 2, 0, 2, 1, 1], "novelty_cap_basis": "company_target_without_validation_or_effect",
        "publication_urgency": "monitor", "related_and_date_role_hold": "Offer announcement is not deployment; assess direct battery-material relevance and subsequent signed order before separate card.",
        "source_owner_evidence": [{"owner": "Sustainable Holdings KK", "url": "https://prtimes.jp/main/html/rd/p/000000171.000096742.html", "role": "issuer_first_party_PR_times_original_sep25"}],
        "evidence_gap": "No actual sold systems, storage battery capacity, measured sustained water yield or certified installed plant."
    },
    "SOURCE_URL_OBSERVATION_a5a5b5c84847087e": {
        "topic": "Korea–Central Asia first summit and Seoul Declaration on minerals/energy cooperation",
        "economic_identity_status": "SEP16_DIPLOMATIC_INSTITUTIONAL_FRAMEWORK_NOT_EXECUTED_MINE_PURCHASE",
        "source_body_access": "Ajunews Sep23 full article and KIEP research institute Sep22 source summary retrieved",
        "actual_event_date": "2026-09-16", "official_publication_date": "2026-09-22",
        "before_after": "Korea and five Central Asian states institutionalized biennial summit format and adopted Seoul Declaration to expand ministers' dialogue and critical minerals/energy cooperation. It does not prove commercial mine/offtake/project capex.",
        "execution_credibility_gate": "PASS", "independent_cardability_gate": "REVIEW",
        "score_breakdown": [18, 14, 0, 2, 5, 2, 1, 1], "novelty_cap_basis": "none",
        "publication_urgency": "near_term", "related_and_date_role_hold": "Summit Sep16, KIEP research report Sep22, original news Sep23. Verify formal adopted text, country bilateral instrument, binding implementation and Full policy lineage.",
        "source_owner_evidence": [{"owner": "Korea Institute for International Economic Policy (KIEP)", "url": "https://www.kiep.go.kr/gallery.es?act=view&bid=0004&list_no=12613&mid=a10102030000", "role": "institute_first_party_report_sep22_on_sep16_meeting"}],
        "evidence_gap": "Original signed Seoul Declaration and each country mineral/energy business instrument not verified with content and legal enforceability."
    },
    "SOURCE_URL_OBSERVATION_3e86458f28b12b8e": {
        "topic": "Sep22 New York US–Japan leaders confirmed existing AI, semiconductor and critical-minerals cooperation",
        "economic_identity_status": "SUMMIT_REAFFIRMATION_NO_NEW_SEPARATE_BINDING_MINERALS_RULE",
        "source_body_access": "Asiatoday Sep23 full article and Japanese foreign ministry official meeting summary retrieved",
        "actual_event_date": "2026-09-22", "official_publication_date": "2026-09-22",
        "before_after": "Leaders agreed to further advance previously ongoing economic-security cooperation; no new export control, critical mineral procurement volume, financial facility or effective legal text in summit summary.",
        "execution_credibility_gate": "PASS", "independent_cardability_gate": "REVIEW",
        "score_breakdown": [12, 10, 0, 0, 4, 2, 2, 1], "novelty_cap_basis": "unsupported_political_rhetoric",
        "publication_urgency": "monitor", "related_and_date_role_hold": "Political meeting Sep22, media dated Sep23; existing US–Japan cooperative agreements may be predecessors. Treat as intention until binding instrument appears.",
        "source_owner_evidence": [{"owner": "Japan Ministry of Foreign Affairs", "url": "https://www.mofa.go.jp/mofaj/na/na1/us/pageit_000001_00012.html", "role": "official_summit_statement_sep22"}],
        "evidence_gap": "Distinct new signed mineral purchase/financing or mandatory regulation lacking."
    },
    "SOURCE_URL_OBSERVATION_88f3cedc0eff7bf3": {
        "topic": "Reuters Sep22 nickel commentary: market discounting Indonesian production curbs",
        "economic_identity_status": "COMMODITY_MARKET_ANALYSIS_OF_PRIOR_QUOTA_ACTION_NOT_NEW_SEP22_REGULATION",
        "source_body_access": "Reuters original direct page inaccessible; Reuters syndicated excerpts, and Indonesian energy ministry prior statement available",
        "actual_event_date": None, "official_publication_date": "2026-09-22",
        "before_after": "Indonesia imposed / evaluated nickel RKAB curbs in prior months; the Sept22 commentary discusses price/market reception, quota uncertainty, and Weda Bay operation re-start. Locked Full 2026-07-10_GL_01 already covers a particular quota-increase restriction stage.",
        "execution_credibility_gate": "REVIEW", "independent_cardability_gate": "REVIEW",
        "score_breakdown": [16, 20, 0, 3, 2, 1, 1, 1], "novelty_cap_basis": "none",
        "publication_urgency": "monitor", "related_and_date_role_hold": "Do not assign Sept22 as a new quota law date; compare June ministry unsigned annual quota, July Full restriction and August selective increases, then assess a new verifiable Weda Bay operational act separately.",
        "source_owner_evidence": [
            {"owner": "Indonesia Ministry of Energy and Mineral Resources (ESDM)", "url": "https://esdm.go.id/en/media-center/news-archives/kementerian-esdm-belum-putuskan-besaran-rkab-nikel-2026", "role": "first_party_prior_june25_statement_not_sep22_update"},
            {"owner": "Reuters reprint at Mining Weekly", "url": "https://www.miningweekly.com/article/indonesias-nickel-production-curbs-leave-market-unconvinced-2026-09-23", "role": "syndicated_analysis_original_direct_restricted"}
        ],
        "evidence_gap": "Exact September curtailment instrument, RKAB allocations, production figures, Eramet Weda Bay date and independent commodity price data unverified."
    },
}

COMPONENTS = [
    "market_structure_competition", "supply_demand_price_utilisation", "technology_performance_safety",
    "cashflow_asset_value", "law_policy_market_access", "systemic_scale",
    "persistence_irreversibility", "decision_urgency_actionability",
]
MAXIMUMS = [25, 25, 20, 10, 10, 5, 3, 2]


def label(score):
    if score >= 85:
        return "critical_structural_85_100"
    if score >= 70:
        return "high_decision_value_70_84"
    if score >= 55:
        return "material_industry_signal_55_69"
    if score >= 40:
        return "standard_monitoring_40_54"
    if score >= 25:
        return "context_reinforcement_25_39"
    return "low_independent_value_0_24"


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--source-ledger", required=True, type=Path)
    args = p.parse_args()
    assert hashlib.sha256(args.source_ledger.read_bytes()).hexdigest() == SOURCE_SHA
    with args.source_ledger.open(encoding="utf-8-sig", newline="") as stream:
        rows = list(csv.DictReader(stream))
    assert len(rows) == len({r["candidate_id"] for r in rows}) == 1330
    by_id = {r["candidate_id"]: r for r in rows}
    graph = json.loads((HERE / "STAGE_A_1330_SOURCE_URL_OBSERVATION_EQUIVALENCE_20261030.json").read_text(encoding="utf-8"))
    all_mixed = {g["source_url_observation_group_id"]: g for g in graph["all_repeat_url_source_groups"] if g["mixed_original_pool"]}
    assert len(all_mixed) == 14
    assert set(CASES) == set(all_mixed).difference(PREVIOUS_FIVE)
    assert len(CASES) == 9
    evidences = []
    ids = set()
    for gid, case in sorted(CASES.items()):
        g = all_mixed[gid]
        score = case["score_breakdown"]
        assert len(score) == len(COMPONENTS)
        assert all(isinstance(v, int) and 0 <= v <= upper for v, upper in zip(score, MAXIMUMS))
        assert score[5] <= 2
        assert score[2] <= 4  # all nine: no independently verified pilot or customer qualification
        total = sum(score)
        if case["novelty_cap_basis"] in ("repeated_announcement_no_new_fact", "unsupported_political_rhetoric"):
            assert total <= 39
        if case["novelty_cap_basis"] == "company_target_without_validation_or_effect":
            assert total <= 54
        assert case["execution_credibility_gate"] in ("PASS", "REVIEW", "FAIL")
        assert case["independent_cardability_gate"] in ("PASS", "REVIEW", "FAIL")
        assert case["publication_urgency"] in ("immediate", "near_term", "monitor")
        assert case["related_and_date_role_hold"] and case["evidence_gap"]
        assert len(g["source_ids"]) == 2
        for source_id, pool, original_score in zip(g["source_ids"], g["source_row_original_pools"], g["source_row_original_scores"]):
            original = by_id[source_id]
            assert original["stage_a_pool"] == pool
            assert int(original["decision_news_value_score"]) == original_score
            assert not original["economic_event_cluster_id"]
            ids.add(source_id)
        evidence = {
            "source_url_observation_group_id": gid,
            "source_url": g["query_aware_url"],
            "original_source_ids": g["source_ids"],
            "original_pools": g["source_row_original_pools"],
            "original_metadata_scores": g["source_row_original_scores"],
            "no_economic_event_merge_from_url": True,
            "bounded_four_judgments_not_native_pass": {
                "execution_credibility_gate": case["execution_credibility_gate"],
                "independent_cardability_gate": case["independent_cardability_gate"],
                "decision_news_value_score_provisional": total,
                "decision_value_breakdown": dict(zip(COMPONENTS, score)),
                "decision_value_classification": label(total),
                "systemic_scale_denominator": None,
                "denominator_gap": "Neither verified sector-wide addressable capacity denominator nor attributable volume provided by the original claim; systemic score capped at 2.",
                "technology_evidence_level": "company_target_or_unsupported_claim" if score[2] else "not_applicable",
                "policy_stage": None,
                "novelty_cap_basis": case["novelty_cap_basis"],
                "publication_urgency": case["publication_urgency"],
            },
            "formal_related_prepass_status": "HOLD",
            "formal_stage_a_disposition": "HOLD_ORIGINAL_ID_UNADJUDICATED",
        }
        evidence.update({k: v for k, v in case.items() if k not in ("execution_credibility_gate", "independent_cardability_gate", "score_breakdown", "novelty_cap_basis", "publication_urgency")})
        evidences.append(evidence)
    assert len(ids) == 18
    all_previous = set()
    for gid in PREVIOUS_FIVE:
        all_previous.update(all_mixed[gid]["source_ids"])
    assert len(all_previous) == 10 and ids.isdisjoint(all_previous)
    assert len(ids | all_previous) == 28
    doc = {
        "artifact_type": "STAGE_A_CROSS_POOL_NINE_REMAINING_GROUPS_BOUNDED_TRIAGE_NON_DECISIONAL",
        "date_kst": "2026-10-30",
        "original_1330_source_sha256": SOURCE_SHA,
        "locked_full_git_blob": "07a91714e56be2a8bfad10ab63822f0c5cb3f06e",
        "original_population": 1330,
        "mixed_pool_group_total": 14,
        "original_source_ids_in_all_mixed_pool_groups": 28,
        "five_groups_previous_research_source_ids": 10,
        "remaining_nine_groups_touched_source_ids": 18,
        "all_14_groups_first_level_triage_covered": True,
        "not_full_primary_body_verification": True,
        "not_native_pass": True,
        "formal_original_0_1P_unadjudicated_count_remains": 1285,
        "formal_strict_promotions": 0,
        "triage_records": evidences,
        "warning": "These are source observation groups, not 14 unique economic events. Some articles bundle multiple economic acts. Neither these group-level provisional scores nor publication urgency creates formal Stage A outcomes.",
        "next_single_bottleneck": "Complete the identified original-source blockers and split multi-act editorial roundups into primary-confirmed economic events, before exhaustive 1,285 original-ID native Stage A adjudication."
    }
    out = HERE / "STAGE_A_NINE_REMAINING_MIXED_POOL_GROUPS_EVIDENCE_TRIAGE_20261030.json"
    with out.open("x", encoding="utf-8", newline="\n") as stream:
        json.dump(doc, stream, ensure_ascii=False, indent=2)
        stream.write("\n")
    print(json.dumps({"scope_status": "PASS_9_GROUPS_TRIAGED_WITH_OPEN_BLOCKERS_NOT_NATIVE_PASS", "original_ids": 1330, "mixed_groups": 14, "cross_pool_ids": 28, "newly_touched_ids": 18, "formal_unadjudicated": 1285, "strict_promotions": 0}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
