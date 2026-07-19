#!/usr/bin/env python3
import argparse
import json
import sys
from collections import defaultdict
from pathlib import Path
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

TRACKING = {
    "utm_source", "utm_medium", "utm_campaign", "utm_term", "utm_content",
    "gclid", "fbclid", "output",
}

STAGE_A_COLLECTIONS = (
    "strict_passed_spec",
    "candidate_review_pool",
    "watchlist_context_pool",
    "existing_reinforcement",
    "support_source_only",
    "rejected",
    "reject_or_support_only_pool",
)


def canon(url):
    if not url:
        return ""
    parsed = urlsplit(str(url).strip())
    query = sorted(
        (
            (key, value)
            for key, value in parse_qsl(parsed.query, keep_blank_values=True)
            if key.lower() not in TRACKING
        ),
        key=lambda item: (item[0], item[1]),
    )
    netloc = parsed.netloc.lower()
    if netloc.startswith("www."):
        netloc = netloc[4:]
    return urlunsplit((
        parsed.scheme.lower(),
        netloc,
        parsed.path.rstrip("/"),
        "",
        urlencode(query),
    ))


def load_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def url_values(record):
    values = []
    for field in ("primary_url", "url"):
        value = record.get(field)
        if isinstance(value, str) and value.strip():
            values.append(value)

    for field in ("source_urls", "urls"):
        value = record.get(field)
        if isinstance(value, str) and value.strip():
            values.append(value)
        elif isinstance(value, list):
            values.extend(
                item for item in value
                if isinstance(item, str) and item.strip()
            )

    for source in record.get("fact_sources", []) or []:
        if not isinstance(source, dict):
            continue
        for field in ("source_url", "url"):
            value = source.get(field)
            if isinstance(value, str) and value.strip():
                values.append(value)
    return values


def raw_story_containers(run):
    containers = []
    if isinstance(run.get("stories"), list):
        containers.append(("stories[]", run["stories"]))

    wrapped = run.get("final_news_llm_input")
    if isinstance(wrapped, dict) and isinstance(wrapped.get("stories"), list):
        containers.append((
            "final_news_llm_input.stories[]",
            wrapped["stories"],
        ))
    return containers


def collect_run_story_records(run):
    records = []
    detected = []

    def add(story_id, urls, container, record_index, role):
        if not story_id:
            return
        canonical_urls = sorted({
            canonical
            for url in urls
            if (canonical := canon(url))
        })
        records.append({
            "record_id": f"{container}#{record_index}",
            "story_id": story_id,
            "canonical_run_urls": canonical_urls,
            "run_url_missing": not canonical_urls,
            "source_container": container,
            "source_record_index": record_index,
            "source_record_role": role,
        })

    for container, stories in raw_story_containers(run):
        detected.append(container)
        for index, story in enumerate(stories):
            if isinstance(story, dict):
                add(
                    story.get("story_id"),
                    url_values(story),
                    container,
                    index,
                    "raw_story",
                )

    ledger = run.get("decision_ledger")
    if isinstance(ledger, list):
        detected.append("decision_ledger[]")
        for index, row in enumerate(ledger):
            if isinstance(row, dict):
                add(
                    row.get("story_id"),
                    url_values(row),
                    "decision_ledger[]",
                    index,
                    "decision_ledger",
                )

    for collection_name in STAGE_A_COLLECTIONS:
        collection = run.get(collection_name)
        if not isinstance(collection, list):
            continue
        container = f"{collection_name}[]"
        detected.append(container)

        for item_index, item in enumerate(collection):
            if not isinstance(item, dict):
                continue

            explicit_story_id = item.get("story_id")
            source_story_ids = item.get("source_story_ids") or []
            if not isinstance(source_story_ids, list):
                source_story_ids = []
            source_story_ids = [value for value in source_story_ids if value]

            # A representative story_id does not replace the grouped universe.
            # Record it separately only when it is not already one of the
            # source_story_ids that will be evaluated below.
            if explicit_story_id and explicit_story_id not in source_story_ids:
                add(
                    explicit_story_id,
                    url_values(item),
                    container,
                    item_index,
                    "single_story_item",
                )

            if not source_story_ids:
                if explicit_story_id:
                    add(
                        explicit_story_id,
                        url_values(item),
                        container,
                        item_index,
                        "single_story_item",
                    )
                continue

            plural_urls = []
            for field in ("source_urls", "urls"):
                value = item.get(field)
                if isinstance(value, list):
                    plural_urls = [
                        url for url in value
                        if isinstance(url, str) and url.strip()
                    ]
                    if plural_urls:
                        break

            if len(source_story_ids) == len(plural_urls):
                for position, (story_id, url) in enumerate(
                    zip(source_story_ids, plural_urls)
                ):
                    add(
                        story_id,
                        [url],
                        container,
                        f"{item_index}:{position}",
                        "grouped_positional_story",
                    )
                continue

            if len(source_story_ids) == 1:
                add(
                    source_story_ids[0],
                    url_values(item),
                    container,
                    f"{item_index}:0",
                    "grouped_single_story",
                )
                continue

            representative_id = (
                item.get("representative_story_id") or explicit_story_id
            )
            representative_urls = [
                value
                for value in (item.get("primary_url"), item.get("url"))
                if isinstance(value, str) and value.strip()
            ]
            for position, story_id in enumerate(source_story_ids):
                assigned = (
                    representative_urls
                    if story_id == representative_id
                    else []
                )
                add(
                    story_id,
                    assigned,
                    container,
                    f"{item_index}:{position}",
                    (
                        "grouped_representative_story"
                        if assigned
                        else "grouped_unmapped_story"
                    ),
                )

    unique = []
    seen = set()
    for record in records:
        key = (
            record["story_id"],
            tuple(record["canonical_run_urls"]),
            record["source_container"],
            str(record["source_record_index"]),
        )
        if key not in seen:
            seen.add(key)
            unique.append(record)
    return unique, sorted(set(detected))


def baseline_indexes(baseline):
    story_to_cards = defaultdict(list)
    card_urls = defaultdict(set)
    for card in baseline.get("cards", []):
        card_id = card.get("id")
        if not card_id:
            continue

        for story_id in card.get("source_story_ids", []) or []:
            if story_id:
                story_to_cards[story_id].append(card_id)

        for url in url_values(card):
            canonical = canon(url)
            if canonical:
                card_urls[card_id].add(canonical)
    return story_to_cards, card_urls


def classify_records(run_records, story_to_cards, card_urls):
    trusted_records = []
    collision_records = []

    for record in run_records:
        baseline_cards = sorted(set(
            story_to_cards.get(record["story_id"], [])
        ))
        if not baseline_cards:
            continue

        run_urls = set(record["canonical_run_urls"])
        trusted_cards = []
        collision_cards = []
        card_results = []

        for card_id in baseline_cards:
            baseline_urls = set(card_urls.get(card_id, set()))
            matching_urls = sorted(run_urls.intersection(baseline_urls))
            trusted = bool(matching_urls)
            card_results.append({
                "baseline_card_id": card_id,
                "canonical_baseline_urls": sorted(baseline_urls),
                "matching_urls": matching_urls,
                "identity_route_trusted": trusted,
            })
            (trusted_cards if trusted else collision_cards).append(card_id)

        classified = {
            **record,
            "story_id_baseline_cards": baseline_cards,
            "trusted_baseline_card_ids": trusted_cards,
            "collision_baseline_card_ids": collision_cards,
            "baseline_card_results": card_results,
            "partial_identity_match": bool(
                trusted_cards and collision_cards
            ),
        }
        if collision_cards:
            collision_records.append(classified)
        else:
            trusted_records.append(classified)

    return trusted_records, collision_records


def declared_collision_count(stage_a_results, top_level_audit):
    candidates = (
        top_level_audit.get("collision_count"),
        top_level_audit.get("story_id_collision_count"),
        stage_a_results.get("story_id_collision_count"),
        (stage_a_results.get("summary") or {}).get(
            "story_id_collision_count"
        ),
    )
    for value in candidates:
        if isinstance(value, int) and not isinstance(value, bool):
            return value
    return None


def quarantine_audit(stage_a_results, collision_story_ids):
    rows_by_story_id = defaultdict(list)
    for row in stage_a_results.get("decision_ledger", []) or []:
        if isinstance(row, dict) and row.get("story_id"):
            rows_by_story_id[row["story_id"]].append(row)

    missing_or_invalid = []
    for story_id in sorted(set(collision_story_ids)):
        rows = rows_by_story_id.get(story_id, [])
        checks = []
        for row in rows:
            audit = row.get("story_id_lineage_audit", {})
            checks.append({
                "story_id_collision_detected": (
                    audit.get("story_id_collision_detected") is True
                ),
                "story_id_match_trusted_false": (
                    audit.get("story_id_match_trusted") is False
                ),
                "duplicate_decision_ignored_story_id": (
                    audit.get("duplicate_decision_ignored_story_id") is True
                ),
            })

        required = {
            "ledger_row_present": bool(rows),
            "all_ledger_rows_quarantined": bool(rows) and all(
                all(check.values()) for check in checks
            ),
        }
        if not all(required.values()):
            missing_or_invalid.append({
                "story_id": story_id,
                "required_quarantine_checks": required,
                "ledger_row_checks": checks,
            })

    expected_count = len(set(collision_story_ids))
    top = stage_a_results.get("story_id_lineage_audit", {}) or {}
    reported_count = declared_collision_count(stage_a_results, top)
    audit_status = (
        stage_a_results.get("story_id_lineage_audit_status")
        or top.get("status")
    )
    top_level_valid = (
        top.get("story_id_used_for_duplicate_routing") is False
        and reported_count == expected_count
        and audit_status == "PASS_COLLISIONS_QUARANTINED"
    )
    return {
        "status": (
            "PASS"
            if not missing_or_invalid and top_level_valid
            else "FAIL"
        ),
        "expected_unique_collision_story_id_count": expected_count,
        "reported_collision_count": reported_count,
        "accepted_collision_count_fields": [
            "story_id_lineage_audit.collision_count",
            "story_id_lineage_audit.story_id_collision_count",
            "story_id_collision_count",
            "summary.story_id_collision_count",
        ],
        "top_level_quarantine_valid": top_level_valid,
        "missing_or_invalid_collision_rows": missing_or_invalid,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("run_json")
    parser.add_argument("baseline_cards_json")
    parser.add_argument(
        "--stage-a-results",
        help=(
            "Optional Stage A artifact used to prove detected collisions "
            "were quarantined and ignored for duplicate routing."
        ),
    )
    args = parser.parse_args()

    run = load_json(args.run_json)
    baseline = load_json(args.baseline_cards_json)
    run_records, detected = collect_run_story_records(run)
    story_to_cards, card_urls = baseline_indexes(baseline)
    trusted_records, collision_records = classify_records(
        run_records,
        story_to_cards,
        card_urls,
    )

    all_cross_run = trusted_records + collision_records
    cross_run_story_ids = sorted({
        record["story_id"] for record in all_cross_run
    })
    collision_story_ids = sorted({
        record["story_id"] for record in collision_records
    })
    trusted_only_story_ids = sorted(
        {record["story_id"] for record in trusted_records}
        - set(collision_story_ids)
    )

    quarantine = None
    if collision_records and not args.stage_a_results:
        status = "BLOCKED_STORY_ID_COLLISIONS_UNQUARANTINED"
        exit_code = 2
    elif collision_records:
        quarantine = quarantine_audit(
            load_json(args.stage_a_results),
            collision_story_ids,
        )
        status = (
            "PASS_COLLISIONS_QUARANTINED"
            if quarantine["status"] == "PASS"
            else "BLOCKED_STORY_ID_COLLISIONS_UNQUARANTINED"
        )
        exit_code = 0 if quarantine["status"] == "PASS" else 2
    else:
        status = "PASS_NO_COLLISIONS"
        exit_code = 0

    print(json.dumps({
        "status": status,
        "input_containers_detected": detected,
        "run_story_record_count": len(run_records),
        "cross_run_record_count": len(all_cross_run),
        "story_id_cross_run_match_count": len(cross_run_story_ids),
        "trusted_identity_match_count": len(trusted_only_story_ids),
        "trusted_record_count": len(trusted_records),
        "trusted_pair_count": sum(
            len(record["trusted_baseline_card_ids"])
            for record in all_cross_run
        ),
        "collision_count": len(collision_story_ids),
        "collision_record_count": len(collision_records),
        "collision_pair_count": sum(
            len(record["collision_baseline_card_ids"])
            for record in collision_records
        ),
        "url_missing_collision_count": sum(
            1 for record in collision_records
            if record["run_url_missing"]
        ),
        "partial_identity_match_record_count": sum(
            1 for record in collision_records
            if record["partial_identity_match"]
        ),
        "trusted_story_ids": trusted_only_story_ids,
        "collision_story_ids": collision_story_ids,
        "trusted": trusted_records,
        "collisions": collision_records,
        "quarantine_audit": quarantine,
        "required_action_when_blocked": (
            "Run Stage A with story-ID collision quarantine fields and rerun "
            "this validator with --stage-a-results."
            if exit_code else None
        ),
    }, ensure_ascii=False, indent=2))
    return exit_code


if __name__ == "__main__":
    sys.exit(main())
