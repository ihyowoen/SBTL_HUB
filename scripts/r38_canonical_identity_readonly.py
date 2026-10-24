#!/usr/bin/env python3
"""R38 read-only canonical Full / Lean event-source identity export.
Runs on an isolated audit branch. Emits no card edits and no source article bodies.
"""
from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MAIN = "805c2718d6daf40a219ae94242d9687e33ac3e88"
FULL_SHA = "07a91714e56be2a8bfad10ab63822f0c5cb3f06e"
LEAN_SHA = "8ebad37e98639ad97a30e52063d7325da77be650"
OUT = Path(os.environ.get("RUNNER_TEMP", "/tmp")) / "r38_canonical_index"
OUT.mkdir(parents=True, exist_ok=True)

def git(*args):
    p = subprocess.run(["git", *args], cwd=ROOT, capture_output=True, text=True, check=True)
    return p.stdout.strip()

def digest(data):
    return hashlib.sha256(data).hexdigest()

def dump_json(name, body):
    raw = (json.dumps(body, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode("utf-8")
    (OUT / name).write_bytes(raw)
    return {"filename": name, "sha256": digest(raw), "bytes": len(raw)}

def main():
    observed_main = git("rev-parse", "refs/remotes/origin/main")
    full_blob = git("rev-parse", MAIN + ":data/cards.full.json")
    lean_blob = git("rev-parse", MAIN + ":public/data/cards.json")
    assert (observed_main, full_blob, lean_blob) == (MAIN, FULL_SHA, LEAN_SHA), {
        "observed_main": observed_main, "full_blob": full_blob, "lean_blob": lean_blob
    }
    raw_full = (ROOT / "data/cards.full.json").read_bytes()
    raw_lean = (ROOT / "public/data/cards.json").read_bytes()
    full = json.loads(raw_full)
    lean = json.loads(raw_lean)
    full_cards = full.get("cards") if isinstance(full, dict) else full
    lean_cards = lean.get("cards") if isinstance(lean, dict) else lean
    assert len(full_cards) == len(lean_cards) == 1676, (
        len(full_cards), len(lean_cards)
    )
    full_sig = [(str(x.get("id", "")),str(x.get("date", "")),str(x.get("title", ""))) for x in full_cards]
    lean_sig = [(str(x.get("id", "")),str(x.get("date", "")),str(x.get("title", ""))) for x in lean_cards]
    assert full_sig == lean_sig, "FULL_LEAN_ID_DATE_TITLE_MISMATCH"
    assert len(set(x[0] for x in full_sig)) == 1676, "DUPLICATE_CARD_IDS"
    ids = {x[0] for x in full_sig}
    records, dangling, edge_count, fingerprint_count = [], [], 0, 0
    url_counts = Counter()
    for c in full_cards:
        if not isinstance(c, dict): raise ValueError("NON_OBJECT_CARD")
        fp = c.get("event_fingerprint")
        raw_fp = fp if isinstance(fp, str) else None
        if not isinstance(fp, dict): fp = {}
        if fp: fingerprint_count += 1
        raw_sources = c.get("fact_sources") or []
        src_urls = [str(x.get("source_url", "")) for x in raw_sources
                    if isinstance(x, dict) and x.get("source_url")]
        orig_urls = [str(u) for u in c.get("urls", []) if isinstance(u, str)]
        fp_urls = [str(u) for u in (fp.get("source_url_cluster") or []) if isinstance(u,str)]
        related = [str(v) for v in c.get("related", []) if isinstance(v,str)]
        for target in related:
            edge_count += 1
            if target not in ids: dangling.append({"source":c.get("id"),"target":target})
        for u in set(orig_urls + src_urls + fp_urls):
            url_counts[u] += 1
        records.append({
            "id": c.get("id"),
            "date": c.get("date"),
            "title": c.get("title"),
            "region": c.get("region"),
            "cat": c.get("cat"),
            "sub_cat": c.get("sub_cat"),
            "urls": orig_urls,
            "fact_sources_urls": list(dict.fromkeys(src_urls)),
            "event_fingerprint_urls": list(dict.fromkeys(fp_urls)),
            "event_fingerprint_raw_string": raw_fp,
            "fact_sources_count": len(raw_sources),
            "fact_sources_missing_source_url_count": sum(1 for x in raw_sources if isinstance(x, dict) and not x.get("source_url")),
            "event_fingerprint": {
                key: fp.get(key) for key in
                ("actor","asset_or_policy","location","event_type","event_date",
                 "factual_anchor","predecessor_card_id")
                if fp.get(key) is not None
            },
            "related": related,
        })
    summary = {
        "run": "R38_READONLY_CANONICAL_IDENTITY_BASELINE",
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "locked_main_commit_sha": MAIN,
        "full_blob_sha": FULL_SHA,
        "lean_blob_sha": LEAN_SHA,
        "full_original_bytes_sha256": digest(raw_full),
        "lean_original_bytes_sha256": digest(raw_lean),
        "full_card_count":len(full_cards),
        "lean_card_count":len(lean_cards),
        "id_date_title_mismatch_count": sum(a != b for a,b in zip(full_sig,lean_sig)),
        "event_fingerprint_present_cards": fingerprint_count,
        "event_fingerprint_string_cards": sum(bool(x.get("event_fingerprint_raw_string")) for x in records),
        "fact_sources_present_cards": sum(x.get("fact_sources_count", 0) > 0 for x in records),
        "fact_sources_cards_with_no_url": sum(x.get("fact_sources_count", 0) > 0 and len(x.get("fact_sources_urls",[])) == 0 for x in records),
        "related_present_cards": sum(bool(x.get("related")) for x in records),
        "related_edges": edge_count,
        "legacy_dangling_related_edges": len(dangling),
        "distinct_literal_source_urls": len(url_counts),
        "branch_head": git("rev-parse","HEAD"),
        "data_mutations":False,
        "no_article_body_dump":True
    }
    f_index = dump_json("R38_CANONICAL_1676_EVENT_SOURCE_INDEX.json",records)
    f_stats = dump_json("R38_CANONICAL_BASELINE_METRICS.json",summary)
    f_dangling = dump_json("R38_EXISTING_DANGLING_REFS.json",dangling)
    manifest = dump_json("R38_OUTPUT_SHA256_MANIFEST.json",{
        "inputs": {
            "full_git_blob":FULL_SHA,"lean_git_blob":LEAN_SHA,
            "full_sha256": digest(raw_full),"lean_sha256":digest(raw_lean)
        },
        "outputs":[f_index,f_stats,f_dangling]
    })
    print(json.dumps({"status":"PASS_READ_ONLY_INDEX","metrics":summary,"manifest":manifest},indent=2))
    return 0

if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as e:
        print(json.dumps({"status":"BLOCKED_EXPORT","error":str(e)}),file=sys.stderr)
        sys.exit(1)
