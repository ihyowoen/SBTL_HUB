#!/usr/bin/env python3
from __future__ import annotations

import argparse
import copy
import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
V9_PATH = ROOT / "scripts/prompt_0_7c_0_8_r6_combined9_v9.py"
SOURCE_INDEX = ROOT / "runs/2026-09-03/current_authoritative_632_event_identity_source_index_R1.json"

spec = importlib.util.spec_from_file_location("r6_combined9_v9", V9_PATH)
v9 = importlib.util.module_from_spec(spec)
assert spec and spec.loader
spec.loader.exec_module(v9)

core = v9.core


def _load(path: Path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def _source_index_by_key() -> dict[str, dict]:
    payload = _load(SOURCE_INDEX)
    if payload.get("status") != "PASS_SOURCE_BOUND_EVENT_IDENTITY_INDEX":
        raise AssertionError("632 source index is not authoritative PASS")
    if payload.get("current_main_sha") != core.MAIN or payload.get("canonical_blob_sha") != core.BLOB:
        raise AssertionError("632 source index baseline binding mismatch")
    rows = payload.get("observations")
    if not isinstance(rows, list) or len(rows) != 632:
        raise AssertionError("632 source index observation count mismatch")
    out: dict[str, dict] = {}
    for row in rows:
        if not isinstance(row, dict):
            raise AssertionError("source index observation must be object")
        key = row.get("observation_key")
        if not isinstance(key, str) or not key:
            raise AssertionError("source index observation_key missing")
        if key in out:
            raise AssertionError(f"duplicate source-index observation_key: {key}")
        out[key] = row
    return out


def _pick_exact_event_date_observation(card: dict, stage_c_row: dict, by_key: dict[str, dict], event_date: str) -> dict:
    story_ids = stage_c_row.get("source_story_ids")
    if not isinstance(story_ids, list) or not story_ids:
        raise AssertionError(f"{card.get('id')}: Stage C source_story_ids missing")

    candidates: list[dict] = []
    for key in story_ids:
        row = by_key.get(str(key))
        if not isinstance(row, dict):
            raise AssertionError(f"{card.get('id')}: source_story_id not in exact 632 index: {key}")
        if row.get("event_date") != event_date:
            continue
        url = row.get("source_url")
        title = row.get("title")
        binding = row.get("binding")
        if not isinstance(binding, dict):
            raise AssertionError(f"{card.get('id')}: exact observation lacks immutable binding: {key}")
        if isinstance(url, str) and url.startswith(("http://", "https://")) and isinstance(title, str) and title.strip():
            candidates.append(row)

    if not candidates:
        raise AssertionError(f"{card.get('id')}: no exact source-bound observation for Stage C event_date {event_date}")

    # Prefer a source already present in the final evidence URL set. If none exists,
    # retain a member of the exact Stage-A event cluster. Among otherwise equivalent
    # rows, choose the shortest exact title to avoid carrying body-like feed text.
    card_urls = {str(u) for u in card.get("urls", []) if isinstance(u, str)}
    candidates.sort(
        key=lambda row: (
            0 if row.get("source_url") in card_urls else 1,
            len(str(row.get("title", ""))),
            str(row.get("observation_key", "")),
        )
    )
    return candidates[0]


def _normalize_date_role(card: dict, source: dict, by_key: dict[str, dict]) -> dict:
    sid = card.get("source_spec_id") or card.get("spec_id")
    if not isinstance(sid, str) or not sid:
        raise AssertionError(f"{card.get('id')}: source_spec_id missing")

    source_role = source.get("date_role")
    source_lineage = source.get("related_lineage")
    if not isinstance(source_role, dict) or source_role.get("status") != "PASS":
        raise AssertionError(f"{sid}: validated Stage C date_role PASS package missing")
    if not isinstance(source_lineage, dict) or not v9._pass_marker(source_lineage.get("earliest_date_check")):
        raise AssertionError(f"{sid}: Stage C earliest_date_check not PASS")

    event_date = source_role.get("representative_event_date")
    if not isinstance(event_date, str) or len(event_date) != 10:
        raise AssertionError(f"{sid}: Stage C representative_event_date missing")
    if card.get("date") != event_date:
        raise AssertionError(f"{sid}: card.date {card.get('date')} != Stage C event date {event_date}")

    publications = source_role.get("source_publication_dates") or source_role.get("publication_dates")
    if not isinstance(publications, list) or not publications:
        raise AssertionError(f"{sid}: Stage C source publication dates missing")

    observation = _pick_exact_event_date_observation(card, source, by_key, event_date)
    exact_url = observation["source_url"]
    exact_title = observation["title"].strip()

    role = copy.deepcopy(card.get("date_role") if isinstance(card.get("date_role"), dict) else {})
    for key, value in source_role.items():
        role.setdefault(key, copy.deepcopy(value))
    role["representative_date"] = event_date
    role["event_date"] = event_date
    role["publication_dates"] = copy.deepcopy(publications)
    role["earliest_same_event_date_checked"] = True
    role["event_date_source_url"] = exact_url
    # This is an exact source-bound headline/title from the immutable 632 observation
    # index, not an analyst summary or a newly synthesized sentence.
    role["event_date_source_quote"] = exact_title
    return role


def build_operations_with_exact_date_role_contract(final_rows, stage_refs):
    operations = v9.build_operations_with_stage_c_insert_contract(final_rows, stage_refs)
    stage_c = v9._stage_c_by_spec()
    by_key = _source_index_by_key()

    for op in operations.get("insert", []):
        card = op.get("card") if isinstance(op, dict) else None
        if not isinstance(card, dict):
            raise AssertionError("insert card missing")
        sid = card.get("source_spec_id") or card.get("spec_id")
        source = stage_c.get(sid)
        if not isinstance(source, dict):
            raise AssertionError(f"{card.get('id')}: exact Stage C row missing for {sid}")
        card["date_role"] = _normalize_date_role(card, source, by_key)

    return operations


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("phase", choices=["prepare", "finalize-audit"])
    args = parser.parse_args()

    v9.v5.v4.v3.bind_validated_stage_b_rereview()
    v9.v5.v4.bind_validated_stage_a_relation_rereview()
    core.build_operations = build_operations_with_exact_date_role_contract

    if args.phase == "prepare":
        core.prepare()
        v9.v5.v4.v3.v2.normalize_document_universe_bridge()
    else:
        core.finalize_audit()


if __name__ == "__main__":
    main()
