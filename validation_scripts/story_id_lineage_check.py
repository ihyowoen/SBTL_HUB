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
)


def canon(url):
    if not url:
        return ""
    parsed = urlsplit(str(url).strip())
    query = sorted(
        (
            (key, value)
            for key, value in parse_qsl(
                parsed.query, keep_blank_values=True
            )
            if key.lower() not in TRACKING
        ),
        key=lambda item: (item[0], item[1]),
    )
    return urlunsplit((
        parsed.scheme.lower(),
        parsed.netloc.lower().replace("www.", ""),
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
                item
                for item in value
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


def collect_run_story_urls(run):
    story_urls = defaultdict(set)

    def add(story_id, urls):
        if not story_id:
            return
        for url in urls:
            canonical = canon(url)
            if canonical:
                story_urls[story_id].add(canonical)

    # Raw run contract.
    for story in run.get("stories", []) or []:
        if isinstance(story, dict):
            add(story.get("story_id"), url_values(story))

    # Stage A decision-ledger contract (`url` may be the only URL field).
    for row in run.get("decision_ledger", []) or []:
        if isinstance(row, dict):
            add(row.get("story_id"), url_values(row))

    # Stage A grouped specs. Pair one URL to one story ID whenever the arrays
    # have equal length. This avoids assigning every grouped URL to every ID.
    for collection_name in STAGE_A_COLLECTIONS:
        for item in run.get(collection_name, []) or []:
            if not isinstance(item, dict):
                continue

            story_id = item.get("story_id")
            if story_id:
                add(story_id, url_values(item))
                continue

            story_ids = item.get("source_story_ids") or []
            if not isinstance(story_ids, list):
                continue
            story_ids = [value for value in story_ids if value]

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

            if story_ids and len(story_ids) == len(plural_urls):
                for source_story_id, source_url in zip(
                    story_ids, plural_urls
                ):
                    add(source_story_id, [source_url])
            elif len(story_ids) == 1:
                add(story_ids[0], url_values(item))
            else:
                representative_story_id = item.get(
                    "representative_story_id"
                )
                if representative_story_id:
                    add(
                        representative_story_id,
                        [
                            item.get("primary_url"),
                            item.get("url"),
                        ],
                    )

    return story_urls


def quarantine_audit(stage_a_results, collisions):
    ledger_by_story_id = {
        row.get("story_id"): row
        for row in stage_a_results.get("decision_ledger", [])
        if row.get("story_id")
    }
    top_level_audit = stage_a_results.get("story_id_lineage_audit", {})

    missing_or_invalid = []
    for collision in collisions:
        story_id = collision["story_id"]
        row = ledger_by_story_id.get(story_id)
        audit = row.get("story_id_lineage_audit", {}) if row else {}
        required = {
            "ledger_row_present": row is not None,
            "story_id_collision_detected": (
                audit.get("story_id_collision_detected") is True
            ),
            "story_id_match_trusted_false": (
                audit.get("story_id_match_trusted") is False
            ),
            "duplicate_decision_ignored_story_id": (
                audit.get("duplicate_decision_ignored_story_id") is True
            ),
        }
        if not all(required.values()):
            missing_or_invalid.append({
                "story_id": story_id,
                "required_quarantine_checks": required,
            })

    top_level_valid = (
        top_level_audit.get("story_id_used_for_duplicate_routing") is False
        and top_level_audit.get("collision_count") == len(collisions)
        and stage_a_results.get("story_id_lineage_audit_status")
        == "PASS_COLLISIONS_QUARANTINED"
    )

    return {
        "status": (
            "PASS"
            if not missing_or_invalid and top_level_valid
            else "FAIL"
        ),
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
            "Optional Stage A result artifact. Required when collisions are "
            "detected and the caller wants to prove they were quarantined."
        ),
    )
    args = parser.parse_args()

    run = load_json(args.run_json)
    baseline = load_json(args.baseline_cards_json)

    story_to_cards = defaultdict(list)
    url_to_cards = defaultdict(set)
    for card in baseline.get("cards", []):
        for story_id in card.get("source_story_ids", []):
            story_to_cards[story_id].append(card.get("id"))
        for url in card.get("urls", []):
            url_to_cards[canon(url)].add(card.get("id"))
        for source in card.get("fact_sources", []):
            url_to_cards[canon(source.get("source_url"))].add(
                card.get("id")
            )

    run_story_urls = collect_run_story_urls(run)
    collisions, trusted = [], []
    for story_id, run_urls in sorted(run_story_urls.items()):
        matched_cards = story_to_cards.get(story_id, [])
        if not matched_cards:
            continue

        exact_url_cards = set()
        for url in run_urls:
            exact_url_cards |= url_to_cards.get(url, set())

        row = {
            "story_id": story_id,
            "story_id_baseline_cards": matched_cards,
            "canonical_run_urls": sorted(run_urls),
            "exact_url_cards": sorted(exact_url_cards),
        }
        if exact_url_cards.intersection(matched_cards):
            trusted.append(row)
        else:
            collisions.append(row)

    quarantine = None
    if collisions:
        if not args.stage_a_results:
            status = "BLOCKED_STORY_ID_COLLISIONS_UNQUARANTINED"
            exit_code = 2
        else:
            stage_a_results = load_json(args.stage_a_results)
            quarantine = quarantine_audit(stage_a_results, collisions)
            if quarantine["status"] == "PASS":
                status = "PASS_COLLISIONS_QUARANTINED"
                exit_code = 0
            else:
                status = "BLOCKED_STORY_ID_COLLISIONS_UNQUARANTINED"
                exit_code = 2
    else:
        status = "PASS_NO_COLLISIONS"
        exit_code = 0

    print(json.dumps({
        "status": status,
        "run_story_record_count": len(run_story_urls),
        "story_id_cross_run_match_count": (
            len(collisions) + len(trusted)
        ),
        "trusted_identity_match_count": len(trusted),
        "collision_count": len(collisions),
        "trusted": trusted,
        "collisions": collisions,
        "quarantine_audit": quarantine,
        "required_action_when_blocked": (
            "Run Stage A with story-ID collision quarantine fields and rerun "
            "this validator with --stage-a-results."
            if exit_code
            else None
        ),
    }, ensure_ascii=False, indent=2))
    return exit_code


if __name__ == "__main__":
    sys.exit(main())
