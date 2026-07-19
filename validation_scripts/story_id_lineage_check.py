#!/usr/bin/env python3
import argparse, json
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

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("run_json")
    ap.add_argument("baseline_cards_json")
    args = ap.parse_args()
    run = json.loads(Path(args.run_json).read_text(encoding="utf-8"))
    baseline = json.loads(
        Path(args.baseline_cards_json).read_text(encoding="utf-8")
    )

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

    print(json.dumps({
        "status": "PASS",
        "story_id_cross_run_match_count": len(collisions) + len(trusted),
        "trusted_identity_match_count": len(trusted),
        "collision_count": len(collisions),
        "trusted": trusted,
        "collisions": collisions,
    }, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
