#!/usr/bin/env python3
"""Read-only, lossless Stage A source-review batching for the outstanding 1,231 IDs.

This script does NOT decide economic-event identity, reuse an existing Full card as a
new fact, or mutate the 0.1P native artifact. Exact article identity is distinct
from an economic event; a roundup may contain multiple events and a single event
may appear in several publications.
"""

from __future__ import annotations

import argparse
import collections
import csv
import hashlib
import json
import re
from datetime import datetime, timezone
from difflib import SequenceMatcher
from pathlib import Path
from urllib.parse import parse_qsl, unquote, urlsplit


IDENTITY_PARAMS = {
    "idxno", "no", "id", "idx", "article_id", "articleid", "art_id",
    "article_seq", "seq", "newsid", "news_id", "newsno", "list_no",
    "nttid", "wr_id", "document_srl", "aid", "content_id", "contentid",
    "post_id", "postid", "uuid", "item_id", "serial", "sno", "docseq",
    "docid", "noticeid", "dtlbizmntno", "newsseq", "seqno",
}
OPTIONAL_SCOPE_PARAMS = {"bid", "bbsseq", "board", "board_id", "category"}
TRACKING_PARAMS = {
    "ref", "source", "fbclid", "gclid", "mc_cid", "mc_eid", "outputtype",
    "amp", "s_cat", "s_keyword", "spm", "npage", "page", "lang",
    "language", "tag", "utm_source", "utm_campaign", "utm_medium",
    "utm_term", "utm_content", "_ga", "_gl",
}
GENERIC_ENDPOINTS = {
    "/", "/index.html", "/news", "/news/", "/news/article.html",
    "/news/articleview.html", "/board.es", "/view", "/article",
    "/detail", "/news/detail", "/articleview.html", "/news/view",
    "/news/article", "/news/", "/news/index.html", "/search",
}
STAGE_PATTERN = re.compile(
    r"입찰|낙찰|계약|상업운전|가동|착공|준공|인허가|승인|시행|비축|"
    r"발주|수주|협약|양산|공급|조달|금융종결|실증|투자|공시|보증|대출|증설|인수|광물|희토류|"
    r"招标|投标|中标|签约|签订|并网|开工|投产|达产|批准|收购|投资|融资|增产|"
    r"量产|交付|冶炼|回收|关税|出口管制|定增|减持|订单|采购|补贴|政策|发布|"
    r"入札|落札|契約|運転開始|稼働|着工|竣工|建設|認可|投資|融資|買収|"
    r"増産|調達|発表|供給|量産|規制|許可|"
    r"\b(?:ess|bess|battery storage|grid battery|critical minerals?|lithium|"
    r"tender|auction|award|contract|loan|drawdown|commissioning|commercial operation|"
    r"energiz(?:e|ation)|construction|groundbreak|financial close|final investment|"
    r"acquisition|production|policy|regulation|permit|recycling|capacity|subsidy|"
    r"grid connection|power purchase|offtake|factory|storage project)\b",
    re.IGNORECASE,
)
CONTEXT_PATTERN = re.compile(
    r"시장|가격|전망|분석|기고|인터뷰|축사|동향|주간|review|forecast|"
    r"outlook|market report|price index|weekly|analysis|opinion",
    re.IGNORECASE,
)
MIXED_PATTERN = re.compile(
    r"종합|주간|주요 뉴스|동향|정리|라운드업|\b(?:roundup|weekly digest|"
    r"news in brief|several projects|multiple deals|16 projects|and other)\b",
    re.IGNORECASE,
)
PUBLIC_OWNER = re.compile(
    r"(?:^|\.)(?:go\.kr|gov|gov\.uk|europa\.eu|ec\.europa\.eu|"
    r"ofgem\.gov\.uk|energy\.gov|kpx\.or\.kr|motir\.go\.kr|"
    r"meti\.go\.jp|ecb\.europa\.eu)$",
    re.IGNORECASE,
)


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def article_url_key(raw: str) -> tuple[str | None, str]:
    """Conservative article key. Never drop query IDs like ?idxno= or ?no=."""
    try:
        parsed = urlsplit((raw or "").strip())
        if parsed.scheme.lower() not in ("https", "http") or not parsed.hostname:
            return None, "NON_HTTP_OR_INVALID"
        host = parsed.hostname.lower().removeprefix("www.")
        path = unquote(parsed.path or "/").rstrip("/") or "/"
        params = [(k.lower(), v.strip()) for k, v in parse_qsl(parsed.query, keep_blank_values=False)]
        identity = sorted((k, v) for k, v in params if k in IDENTITY_PARAMS and v)
        nontracking = sorted(
            (k, v) for k, v in params
            if not k.startswith("utm_") and k not in TRACKING_PARAMS and v
        )
        if identity:
            # All non-tracking fields are retained: CMS-specific document IDs
            # are unknown a priori. Board identifier bbsSeq is NOT a doc ID.
            query = "&".join(f"{k}={v}" for k, v in nontracking)
            return f"{host}{path}?{query}", "ARTICLE_QUERY_ID"

        normalized_path = path.lower()
        terminal = path.split("/")[-1]
        digits = bool(re.search(r"\d{3,}", terminal))
        uuidish = bool(re.search(r"[a-fA-F0-9]{10,}", terminal))
        substantial_slug = len(terminal) >= 24 and (
            terminal.count("-") >= 2 or terminal.count("_") >= 2
        )
        url_segments = [p for p in path.split("/") if p]
        article_id_in_parent = (
            len(url_segments) >= 3
            and any(
                re.fullmatch(r"\d{3,}", s)
                and not re.fullmatch(r"(?:19|20)\d{2}", s)
                for s in url_segments[:-1]
            )
        )
        strong_path = (
            normalized_path not in GENERIC_ENDPOINTS
            and bool(url_segments)
            and (digits or uuidish or substantial_slug or article_id_in_parent)
        )
        if strong_path:
            # Distinct variants may be substantial separate articles or stages.
            query = "?" + "&".join(f"{k}={v}" for k, v in nontracking) if nontracking else ""
            return f"{host}{path}{query}", "ARTICLE_PATH_ID"

        remaining = nontracking
        if remaining:
            # Nonstandard CMS parameters: retain as a *candidate*, never auto-merge.
            query = "&".join(f"{k}={v}" for k, v in remaining)
            return f"{host}{path}?{query}", "UNKNOWN_QUERY_REVIEW"
        return None, "GENERIC_OR_INSUFFICIENT_URL"
    except (ValueError, AttributeError):
        return None, "MALFORMED_URL"


def cleaned_title(text: str | None) -> str:
    text = re.sub(r"\s+", " ", (text or "").strip().casefold())
    return re.sub(r"[\s\u2018\u2019\"'\u201c\u201d,.:;!?\[\](){}]+", " ", text).strip()


def source_risk(row: dict, group: dict) -> list[str]:
    title = str(row.get("headline_raw") or row.get("headline") or "")
    out = []
    if STAGE_PATTERN.search(title):
        out.append("ECONOMIC_OR_POLICY_STAGE_WORDS_NEED_OWNER_CHECK")
    if MIXED_PATTERN.search(title):
        out.append("POSSIBLE_MULTI_EVENT_ARTICLE_SPLIT_REQUIRED")
    if CONTEXT_PATTERN.search(title):
        out.append("CONTEXT_OR_AGGREGATE_CAUTION")
    score = row.get("decision_news_value_score")
    if isinstance(score, (float, int)) and score <= 30 and STAGE_PATTERN.search(title):
        out.append("LOW_METADATA_SCORE_STRUCTURAL_RESCUE")
    if group["article_identity_quality"] not in ("ARTICLE_QUERY_ID", "ARTICLE_PATH_ID"):
        out.append("ARTICLE_IDENTITY_REQUIRES_MANUAL_CHECK")
    if group["full_card_ids"]:
        out.append("FULL_SOURCE_URL_OVERLAP_NOT_EVENT_DUPLICATE_PROOF")
    if len(group["full_card_ids"]) > 1:
        out.append("FULL_ONE_SOURCE_MULTIPLE_CARDS_SPLIT_RISK")
    if group["previously_formal_source_ids"]:
        out.append("PREVIOUS_FORMAL_SOURCE_URL_OVERLAP_RECHECK_EVENT")
    if group["title_variance_warning"]:
        out.append("ONE_URL_DIVERGENT_HEADLINES_SPLIT_RISK")
    parsed = urlsplit(str(row.get("primary_url") or ""))
    if parsed.hostname and PUBLIC_OWNER.search(parsed.hostname):
        out.append("PUBLIC_PRIMARY_DOCUMENT_POSSIBLE")
    if not row.get("headline_raw"):
        out.append("NO_RAW_HEADLINE_USE_SOURCE_AND_ROW_CONTEXT")
    return out


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--stage", type=Path, required=True)
    parser.add_argument("--full", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)
    original_stage_sha, original_full_sha = sha256_file(args.stage), sha256_file(args.full)
    with args.stage.open("r", encoding="utf-8") as stream:
        doc = json.load(stream)
    with args.full.open("r", encoding="utf-8") as stream:
        full = json.load(stream)
    original = doc["decision_ledger"]
    finished = {r["candidate_id"] for r in doc["promotion_reassessment_ledger"]}
    assert len(original) == 1330 and len(finished) == 99
    assert len({r["story_id"] for r in original}) == len(original)
    pending = [r for r in original if r["story_id"] not in finished]
    assert len(pending) == 1231

    full_by_url = collections.defaultdict(set)
    for card in full["cards"]:
        for url in card.get("urls", []) or []:
            key, kind = article_url_key(url)
            if key and kind in ("ARTICLE_QUERY_ID", "ARTICLE_PATH_ID"):
                full_by_url[key].add(card["id"])
    formal_by_url = collections.defaultdict(set)
    for row in original:
        if row["story_id"] in finished:
            key, kind = article_url_key(row.get("primary_url"))
            if key and kind in ("ARTICLE_QUERY_ID", "ARTICLE_PATH_ID"):
                formal_by_url[key].add(row["story_id"])

    provisional_groups = collections.defaultdict(list)
    for row in pending:
        key, kind = article_url_key(row.get("primary_url"))
        # Nonstandard query URLs are isolated until human identity review.
        group_key = key if kind in ("ARTICLE_QUERY_ID", "ARTICLE_PATH_ID") else None
        stable_key = group_key or f"unresolved-source:{row['story_id']}"
        provisional_groups[stable_key].append((row, group_key, kind))

    groups = []
    roster = []
    for stable_key, records in sorted(provisional_groups.items()):
        rows = [r[0] for r in records]
        ids = [r["story_id"] for r in rows]
        titles = [cleaned_title(r.get("headline_raw")) for r in rows if r.get("headline_raw")]
        min_sim = 1.0
        if len(set(titles)) > 1:
            representatives = list(dict.fromkeys(titles))
            min_sim = min(
                SequenceMatcher(None, a, b).ratio()
                for i, a in enumerate(representatives)
                for b in representatives[i + 1 :]
            )
        stable_id = "SRU-" + hashlib.sha256(stable_key.encode()).hexdigest()[:14].upper()
        key, quality = records[0][1], records[0][2]
        fids = sorted(full_by_url.get(key, set())) if key else []
        pids = sorted(formal_by_url.get(key, set())) if key else []
        group = {
            "source_review_unit_id": stable_id,
            "source_article_url_key": key,
            "article_identity_quality": quality,
            "source_ids": ids,
            "source_row_indices": [r.get("source_row_index") for r in rows],
            "source_observation_count": len(rows),
            "representative_headline": next((r.get("headline_raw") for r in rows if r.get("headline_raw")), None),
            "representative_primary_url": rows[0]["primary_url"],
            "distinct_cleaned_headlines": len(set(titles)),
            "minimum_headline_similarity": round(min_sim, 4),
            "title_variance_warning": min_sim < 0.65,
            "full_card_ids": fids,
            "previously_formal_source_ids": pids,
            "economic_event_count": None,
            "review_status": "SOURCE_CLUSTER_ONLY_EVENT_SPLIT_AND_OWNER_VERIFICATION_PENDING",
            "formal_0_1P_disposition": None,
        }
        local_flags = sorted({flag for row in rows for flag in source_risk(row, group)})
        group["review_flags"] = local_flags
        weight = (
            110 if "ONE_URL_DIVERGENT_HEADLINES_SPLIT_RISK" in local_flags else 0
        ) + (90 if pids else 0) + (80 if fids else 0) + (
            65 if "LOW_METADATA_SCORE_STRUCTURAL_RESCUE" in local_flags else 0
        ) + (50 if "POSSIBLE_MULTI_EVENT_ARTICLE_SPLIT_REQUIRED" in local_flags else 0) + (
            45 if "ECONOMIC_OR_POLICY_STAGE_WORDS_NEED_OWNER_CHECK" in local_flags else 0
        ) + (30 if "PUBLIC_PRIMARY_DOCUMENT_POSSIBLE" in local_flags else 0)
        group["review_priority_score_not_news_value"] = weight
        group["review_lane"] = (
            "SOURCE_OR_EVENT_AMBIGUITY" if group["title_variance_warning"] or len(fids) > 1
            else "EXISTING_LINEAGE_FIRST" if pids or fids
            else "LOW_SCORE_HIGH_IMPACT_RESCUE" if "LOW_METADATA_SCORE_STRUCTURAL_RESCUE" in local_flags
            else "MULTI_ACT_SPLIT" if "POSSIBLE_MULTI_EVENT_ARTICLE_SPLIT_REQUIRED" in local_flags
            else "OWNER_STAGE_VERIFICATION" if "ECONOMIC_OR_POLICY_STAGE_WORDS_NEED_OWNER_CHECK" in local_flags
            else "PRIMARY_DOCUMENT" if "PUBLIC_PRIMARY_DOCUMENT_POSSIBLE" in local_flags
            else "CONTEXT_OR_STRUCTURE_REVIEW"
        )
        groups.append(group)
        for row in rows:
            roster.append({
                "source_id": row["story_id"],
                "source_row_index": row.get("source_row_index"),
                "headline_raw": row.get("headline_raw"),
                "primary_url": row["primary_url"],
                "legacy_stage_a_pool": row.get("stage_a_pool"),
                "legacy_metadata_score": row.get("decision_news_value_score"),
                "source_review_unit_id": stable_id,
                "safe_article_url_key": key,
                "url_identity_kind": quality,
                "review_flags": source_risk(row, group),
                "full_source_overlap_card_ids": fids,
                "previously_formal_source_overlap_ids": pids,
                "proposed_economic_event_count": None,
                "formal_status": "PENDING_INDEPENDENT_OWNER_STAGE_REVIEW",
            })

    # Title similarity is advisory. Never union two article-source clusters on it.
    cross_group_edges = []
    try:
        from sklearn.feature_extraction.text import TfidfVectorizer

        long_titles = [(i, cleaned_title(r.get("headline_raw"))) for i, r in enumerate(roster)]
        long_titles = [(i, t) for i, t in long_titles if len(t) >= 21]
        if long_titles:
            vector = TfidfVectorizer(analyzer="char", ngram_range=(3, 5), min_df=1)
            matrix = vector.fit_transform([t for _, t in long_titles])
            hits = (matrix @ matrix.T).tocoo()
            by_pair = {}
            for idx, jdx, sim in zip(hits.row, hits.col, hits.data):
                if idx >= jdx or sim < 0.82:
                    continue
                i, j = long_titles[idx][0], long_titles[jdx][0]
                a, b = roster[i], roster[j]
                if a["source_review_unit_id"] == b["source_review_unit_id"]:
                    continue
                unit_pair = tuple(sorted((a["source_review_unit_id"], b["source_review_unit_id"])))
                old = by_pair.get(unit_pair)
                if old is None or sim > old["headline_similarity"]:
                    by_pair[unit_pair] = {
                        "source_review_unit_ids": list(unit_pair),
                        "example_source_ids": [a["source_id"], b["source_id"]],
                        "example_headlines": [a["headline_raw"], b["headline_raw"]],
                        "headline_similarity": round(float(sim), 4),
                        "status": "TITLE_ONLY_CROSS_ARTICLE_EVENT_IDENTITY_NOT_PROVEN",
                        "required_check": "Compare owner, asset, geography, date, and economic act stage; split follow-ups.",
                    }
            cross_group_edges = sorted(by_pair.values(), key=lambda x: -x["headline_similarity"])
    except ImportError:
        pass

    roster.sort(key=lambda x: x["source_row_index"])
    groups.sort(key=lambda g: (-g["review_priority_score_not_news_value"], -g["source_observation_count"], g["source_review_unit_id"]))
    source_counts = collections.Counter(f for r in roster for f in r["review_flags"])
    lanes = collections.Counter(g["review_lane"] for g in groups)
    quality = collections.Counter(g["article_identity_quality"] for g in groups)
    summary = {
        "checkpoint": 17,
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "scope": "read_only_provisional_source_article_triage_not_formal_0_1P_adjudication",
        "native_stage_a_sha256_before_and_after": original_stage_sha,
        "full_reference_sha256_before_and_after": original_full_sha,
        "all_source_ids": len(original),
        "prior_formal_source_ids": len(finished),
        "pending_source_ids": len(pending),
        "pending_source_review_units": len(groups),
        "observation_reduction_from_repeated_exact_article_urls": len(pending) - len(groups),
        "multi_observation_source_units": sum(len(g["source_ids"]) > 1 for g in groups),
        "pending_observations_in_multi_source_units": sum(len(g["source_ids"]) for g in groups if len(g["source_ids"]) > 1),
        "near_title_cross_article_proposals_not_confirmed_events": len(cross_group_edges),
        "full_overlap_observations_not_events": sum(bool(r["full_source_overlap_card_ids"]) for r in roster),
        "formal_overlap_observations_not_decisions": sum(bool(r["previously_formal_source_overlap_ids"]) for r in roster),
        "low_score_structural_rescue_observations": source_counts["LOW_METADATA_SCORE_STRUCTURAL_RESCUE"],
        "source_ids_missing_headline_raw": sum(not r["headline_raw"] for r in roster),
        "identity_quality_by_review_unit": dict(sorted(quality.items())),
        "review_units_by_lane": dict(sorted(lanes.items())),
        "risk_flag_counts_by_source_observation": dict(sorted(source_counts.items())),
        "new_formal_decisions": 0,
        "new_full_cards": 0,
        "stage_a_global_status": "HOLD",
        "stage_b_authorized": False,
        "explanation": (
            "URL identity only groups repeated source-document observations. Headline "
            "similarity proposes cross-document checks; it cannot establish an economic "
            "event. No low-score source is excluded, no multi-act article is forced into "
            "one event, no Full URL overlap is treated as automatic duplicate, and "
            "all 1,231 pending source IDs remain pending until independent official review."
        ),
    }
    output = {
        "schema": "SBTL_STAGE_A_BULK_SOURCE_REVIEW_TRIAGE_CP17_V1",
        "quality_summary": summary,
        "source_roster": roster,
        "source_review_units": groups,
        "cross_article_title_review_proposals": cross_group_edges,
    }
    with (args.out / "STAGE_A_CP17_BULK_TRIAGE.json").open("w", encoding="utf-8") as stream:
        json.dump(output, stream, ensure_ascii=False, indent=2)
    with (args.out / "STAGE_A_CP17_DATA_QUALITY.json").open("w", encoding="utf-8") as stream:
        json.dump(summary, stream, ensure_ascii=False, indent=2)
    with (args.out / "STAGE_A_CP17_REVIEW_QUEUE.csv").open("w", encoding="utf-8", newline="") as stream:
        fields = [
            "source_review_unit_id", "review_lane", "review_priority_score_not_news_value",
            "source_observation_count", "source_ids", "representative_headline",
            "representative_primary_url", "article_identity_quality", "full_card_ids",
            "previously_formal_source_ids", "review_flags", "review_status",
        ]
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        for g in groups:
            writer.writerow({
                f: " | ".join(map(str, g[f])) if isinstance(g[f], list) else g[f]
                for f in fields
            })
    # The repeatable, human/AI research contract: each row starts as one *source*
    # unit. Reviewers must duplicate a worksheet row for every independent economic
    # act in a roundup; source ID coverage must then be checked many-to-many.
    with (args.out / "STAGE_A_CP17_ADJUDICATION_WORKSHEET.csv").open(
        "w", encoding="utf-8", newline=""
    ) as stream:
        fields = [
            "source_review_unit_id", "review_lane", "review_priority_score_not_news_value",
            "source_ids", "headline_raw", "primary_url", "full_source_card_ids",
            "suggested_split_risk", "economic_event_index_in_source", "owner_entity",
            "asset_or_policy_id", "geography", "economic_act_type", "prior_state",
            "new_verified_fact", "event_effective_date", "publication_date", "date_role",
            "execution_or_policy_stage", "numerator_and_denominator", "unit_check",
            "owner_original_url_1", "owner_original_url_2", "official_fact_status",
            "baseline_full_relation", "lineage_stage_relation", "independent_event_key",
            "stage_a_disposition", "stage_a_disposition_reason", "remaining_uncertainty",
            "next_confirmation_trigger", "reviewer", "review_timestamp_utc", "review_status",
        ]
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        for g in groups:
            writer.writerow({
                "source_review_unit_id": g["source_review_unit_id"],
                "review_lane": g["review_lane"],
                "review_priority_score_not_news_value": g["review_priority_score_not_news_value"],
                "source_ids": " | ".join(g["source_ids"]),
                "headline_raw": g["representative_headline"],
                "primary_url": g["representative_primary_url"],
                "full_source_card_ids": " | ".join(g["full_card_ids"]),
                "suggested_split_risk": (
                    "CHECK_MULTI_ACT" if "POSSIBLE_MULTI_EVENT_ARTICLE_SPLIT_REQUIRED" in g["review_flags"]
                    else "CHECK_ONE_SOURCE_MANY_ACTS"
                ),
                "economic_event_index_in_source": "UNASSIGNED",
                "official_fact_status": "NOT_VERIFIED",
                "review_status": "RESEARCH_REQUIRED_NOT_FORMAL",
            })
    assert sha256_file(args.stage) == original_stage_sha
    assert sha256_file(args.full) == original_full_sha
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
