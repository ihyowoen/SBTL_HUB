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


def canon(url):
    if not url:
        return ""
    parsed = urlsplit(url.strip())
    query = [
        (key, value)
        for key, value in parse_qsl(parsed.query, keep_blank_values=True)
        if key.lower() not in TRACKING
    ]
    return urlunsplit((
        parsed.scheme.lower(),
        parsed.netloc.lower().replace("www.", ""),
        parsed.path.rstrip("/"),
        "",
        urlencode(query),
    ))


def load_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


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
        "status": "PASS" if not missing_or_invalid and top_level_valid else "FAIL",
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
            url_to_cards[canon(source.get("source_url"))].add(card.get("id"))

    collisions, trusted = [], []
    for story in run.get("stories", []):
        story_id = story.get("story_id")
        matched_cards = story_to_cards.get(story_id, [])
        if not matched_cards:
            continue
        exact_url_cards = set()
        for url in [story.get("primary_url"), *(story.get("source_urls") or [])]:
            exact_url_cards |= url_to_cards.get(canon(url), set())
        row = {
            "story_id": story_id,
            "story_id_baseline_cards": matched_cards,
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
        "story_id_cross_run_match_count": len(collisions) + len(trusted),
        "trusted_identity_match_count": len(trusted),
        "collision_count": len(collisions),
        "trusted": trusted,
        "collisions": collisions,
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
