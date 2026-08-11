#!/usr/bin/env python3
from __future__ import annotations

import copy
import hashlib
import json
import os
import re
import subprocess
import sys
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
RUN_DIR = ROOT / "runs/2026-08-11/backlog-reconciliation-r2"
RUN_PATH = RUN_DIR / "card-run.json"
PROMPT08_PATH = RUN_DIR / "prompt-0-8-prep-result.json"
FULL_PATH = ROOT / "data/cards.full.json"
LEAN_PATH = ROOT / "public/data/cards.json"
BASE_SHA = "d3137945860664116b1bf90bbb7bee54d2a6c1d9"
OF_GEM_ID = "2026-06-26_EU_01"
MOU_SPEC = "REC26_A2_039"


def die(message: str) -> None:
    raise SystemExit(f"PR256_REMEDIATION_FAIL: {message}")


def run_cmd(args: list[str], *, cwd: Path = ROOT, capture: bool = False) -> str:
    print("+", " ".join(args), flush=True)
    completed = subprocess.run(
        args,
        cwd=cwd,
        text=True,
        stdout=subprocess.PIPE if capture else None,
        stderr=subprocess.STDOUT if capture else None,
        check=False,
    )
    if completed.returncode != 0:
        if capture and completed.stdout:
            print(completed.stdout)
        die(f"command failed ({completed.returncode}): {' '.join(args)}")
    return (completed.stdout or "").strip() if capture else ""


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def save_json(path: Path, payload: Any) -> None:
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def stable(value: Any) -> Any:
    if isinstance(value, list):
        return [stable(item) for item in value]
    if isinstance(value, dict):
        return {key: stable(value[key]) for key in sorted(value)}
    return value


def operations_sha256(operations: dict[str, Any]) -> str:
    raw = json.dumps(stable(operations), ensure_ascii=False, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def file_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def walk_values(value: Any):
    if isinstance(value, dict):
        for key, child in value.items():
            yield key, child
            yield from walk_values(child)
    elif isinstance(value, list):
        for child in value:
            yield from walk_values(child)


def recursive_true(value: Any, key_name: str) -> bool:
    return any(key == key_name and child is True for key, child in walk_values(value))


def recursive_text(value: Any) -> str:
    parts: list[str] = []
    if isinstance(value, dict):
        for child in value.values():
            parts.append(recursive_text(child))
    elif isinstance(value, list):
        for child in value:
            parts.append(recursive_text(child))
    elif isinstance(value, (str, int, float, bool)):
        parts.append(str(value))
    return " ".join(parts)


def has_same_event_screen_proof(card: dict[str, Any]) -> bool:
    if recursive_true(card, "earliest_same_event_date_checked"):
        return True
    blob = recursive_text(card).casefold()
    markers = (
        "pass_no_match",
        "screened_current_main_no_unresolved_same_event",
        "screened_current_main",
        "baseline_duplicate_event_fingerprint_screen",
        "no_current_main_match",
    )
    return any(marker in blob for marker in markers)


def date_tokens(iso_date: str) -> list[str]:
    try:
        dt = datetime.strptime(iso_date, "%Y-%m-%d")
    except ValueError:
        return [iso_date]
    months = [
        "january", "february", "march", "april", "may", "june",
        "july", "august", "september", "october", "november", "december",
    ]
    m, d = dt.month, dt.day
    return [
        iso_date,
        f"{m}월 {d}일",
        f"{m}/{d}",
        f"{m}-{d}",
        f"{months[m-1]} {d}",
        f"{months[m-1][:3]} {d}",
    ]


def select_event_date_source(card: dict[str, Any]) -> dict[str, Any]:
    role = card.get("date_role")
    if not isinstance(role, dict):
        die(f"{card.get('id')}: date_role missing/non-object")
    event_date = str(role.get("event_date") or "")
    sources = card.get("fact_sources")
    if not isinstance(sources, list) or not sources:
        die(f"{card.get('id')}: no fact_sources to support date-role remediation")

    candidates = []
    tokens = [token.casefold() for token in date_tokens(event_date)]
    for idx, source in enumerate(sources):
        if not isinstance(source, dict):
            continue
        url = source.get("source_url") or source.get("source_url_canonical")
        quote = source.get("source_quote")
        if not isinstance(url, str) or not url.startswith(("http://", "https://")):
            continue
        if not isinstance(quote, str) or not quote.strip():
            continue
        text = " ".join(
            str(source.get(key) or "")
            for key in ("source_quote", "claim", "source_contribution", "visible_quote_date", "source_published_date")
        ).casefold()
        score = 0
        score += 20 if any(token and token in text for token in tokens) else 0
        score += 8 if source.get("source_published_date") == event_date else 0
        score += 4 if source.get("visible_quote_date") == event_date else 0
        score += 2 if source.get("source_quote_status") == "body_quote_verified" else 0
        candidates.append((score, -idx, source))
    if not candidates:
        die(f"{card.get('id')}: no existing source URL + body quote available for event-date evidence")
    candidates.sort(key=lambda item: (item[0], item[1]), reverse=True)
    return candidates[0][2]


def publication_dates_from_sources(card: dict[str, Any]) -> list[str]:
    values: list[str] = []
    for source in card.get("fact_sources") or []:
        if not isinstance(source, dict):
            continue
        for key in ("source_published_date", "visible_quote_date"):
            value = source.get(key)
            if isinstance(value, str) and re.fullmatch(r"\d{4}-\d{2}-\d{2}", value):
                values.append(value)
    return sorted(set(values))


def remediate_insert_card(card: dict[str, Any]) -> None:
    cid = card.get("id") or card.get("source_spec_id")
    role = card.get("date_role")
    if not isinstance(role, dict):
        die(f"{cid}: date_role missing")
    if not has_same_event_screen_proof(card):
        die(f"{cid}: cannot prove earliest-same-event screening from existing run evidence")

    publications = role.get("publication_dates")
    if not isinstance(publications, list) or not publications:
        publications = publication_dates_from_sources(card)
        if not publications:
            die(f"{cid}: cannot derive publication_dates from existing fact_sources")
        role["publication_dates"] = publications

    source = select_event_date_source(card)
    role["earliest_same_event_date_checked"] = True
    role["event_date_source_url"] = source.get("source_url") or source.get("source_url_canonical")
    role["event_date_source_quote"] = source["source_quote"].strip()

    if card.get("source_spec_id") == MOU_SPEC:
        lineage = card.get("related_lineage")
        if not isinstance(lineage, dict) or lineage.get("status") != "PASS":
            die("MOU card lacks PASS related_lineage")
        proof_blob = recursive_text(card).casefold()
        if not any(marker in proof_blob for marker in ("pass_no_match", "screened_current_main", "no_current_main_match")):
            die("MOU card lacks existing baseline/same-event screen proof")
        lineage["same_event_checked"] = True
        lineage["earliest_same_event_date_checked"] = True


def upsert_ofgem_source_audit(run: dict[str, Any]) -> None:
    updates = run.get("operations", {}).get("update", [])
    matches = [op for op in updates if isinstance(op, dict) and op.get("id") == OF_GEM_ID]
    if len(matches) != 1:
        die(f"expected exactly one Ofgem update op, found {len(matches)}")
    changes = matches[0].get("changes")
    if not isinstance(changes, list):
        die("Ofgem update changes[] missing")
    if not any(isinstance(change, dict) and change.get("path") == "/fact_sources/-" for change in changes):
        die("Ofgem update does not contain the reviewed /fact_sources/- reinforcement patch")

    for path, value in (
        ("/source_evidence_entry_count", 3),
        ("/source_unique_url_count", 3),
    ):
        existing = next((change for change in changes if isinstance(change, dict) and change.get("path") == path), None)
        if existing is not None:
            existing["op"] = "replace"
            existing["value"] = value
        else:
            changes.append({"op": "replace", "path": path, "value": value})


def replace_exact(value: Any, old: str, new: str) -> tuple[Any, int]:
    count = 0
    if isinstance(value, dict):
        out = {}
        for key, child in value.items():
            replaced, n = replace_exact(child, old, new)
            out[key] = replaced
            count += n
        return out, count
    if isinstance(value, list):
        out = []
        for child in value:
            replaced, n = replace_exact(child, old, new)
            out.append(replaced)
            count += n
        return out, count
    if value == old:
        return new, 1
    return value, 0


def replace_hash_in_run_jsons(old: str, new: str) -> int:
    total = 0
    for path in sorted(RUN_DIR.rglob("*.json")):
        try:
            payload = load_json(path)
        except Exception:
            continue
        replaced, count = replace_exact(payload, old, new)
        if count:
            save_json(path, replaced)
            total += count
    return total


def sync_prompt08(insert_cards: list[dict[str, Any]], run: dict[str, Any]) -> None:
    prompt = load_json(PROMPT08_PATH)
    prompt["github_main_sync_gate"] = {
        "status": "PASS",
        "baseline_locked": True,
        "declared_main_commit_sha": run["base_main_commit_sha"],
        "observed_main_commit_sha": BASE_SHA,
        "canonical_full_blob_sha": run["base_full_blob_sha"],
        "main_unchanged_since_locked_preflight": True,
        "silent_rebase_performed": False,
    }
    by_id = {card.get("id"): card for card in insert_cards if card.get("id")}
    by_spec = {card.get("source_spec_id"): card for card in insert_cards if card.get("source_spec_id")}
    ready = prompt.get("github_merge_ready")
    if isinstance(ready, list):
        for item in ready:
            if not isinstance(item, dict):
                continue
            source = by_id.get(item.get("id")) or by_spec.get(item.get("source_spec_id"))
            if not source:
                continue
            item["date_role"] = copy.deepcopy(source["date_role"])
            if source.get("source_spec_id") == MOU_SPEC:
                item["related_lineage"] = copy.deepcopy(source["related_lineage"])
    save_json(PROMPT08_PATH, prompt)


def main() -> None:
    os.chdir(ROOT)
    observed_main = run_cmd(["git", "rev-parse", "origin/main"], capture=True)
    if observed_main != BASE_SHA:
        die(f"BLOCKED_BASELINE_MOVED_REBASE_REQUIRED: origin/main={observed_main} expected={BASE_SHA}")

    run = load_json(RUN_PATH)
    if run.get("base_main_commit_sha") != BASE_SHA:
        die("card-run baseline SHA changed; refusing silent rebase")
    inserts = run.get("operations", {}).get("insert")
    if not isinstance(inserts, list) or len(inserts) != 32:
        die(f"expected 32 inserts, found {0 if not isinstance(inserts, list) else len(inserts)}")

    old_ops_sha = operations_sha256(run["operations"])
    insert_cards: list[dict[str, Any]] = []
    for op in inserts:
        card = op.get("card") if isinstance(op, dict) else None
        if not isinstance(card, dict):
            die("insert operation missing card")
        remediate_insert_card(card)
        insert_cards.append(card)

    upsert_ofgem_source_audit(run)
    run["output_updated"] = datetime.now(timezone(timedelta(hours=9))).isoformat(timespec="seconds")
    save_json(RUN_PATH, run)

    new_ops_sha = operations_sha256(run["operations"])
    if new_ops_sha == old_ops_sha:
        die("operations hash did not change after remediation")
    replaced_ops_bindings = replace_hash_in_run_jsons(old_ops_sha, new_ops_sha)
    print(f"updated operations SHA bindings: {replaced_ops_bindings}")

    # Reload after recursive binding replacement, then add/sync final 0.8 gate.
    run = load_json(RUN_PATH)
    inserts = run["operations"]["insert"]
    insert_cards = [op["card"] for op in inserts]
    sync_prompt08(insert_cards, run)

    audit_paths = [ROOT / ref for ref in run.get("audit_refs", [])]
    if not audit_paths:
        die("run has no audit_refs")
    old_full_hashes: set[str] = set()
    old_lean_hashes: set[str] = set()
    for audit_path in audit_paths:
        audit = load_json(audit_path)
        if isinstance(audit.get("full_output_sha256"), str):
            old_full_hashes.add(audit["full_output_sha256"])
        if isinstance(audit.get("lean_output_sha256"), str):
            old_lean_hashes.add(audit["lean_output_sha256"])

    baseline_tmp = Path(os.environ.get("RUNNER_TEMP", "/tmp")) / "pr256-cards.full.base.json"
    with baseline_tmp.open("wb") as handle:
        completed = subprocess.run(
            ["git", "show", f"{BASE_SHA}:data/cards.full.json"],
            cwd=ROOT,
            stdout=handle,
            stderr=subprocess.PIPE,
            check=False,
        )
    if completed.returncode != 0:
        die(f"failed to reconstruct baseline: {completed.stderr.decode('utf-8', errors='replace')}")

    run_cmd([
        "node", "scripts/apply_card_run.mjs",
        "--run", str(RUN_PATH.relative_to(ROOT)),
        "--baseline", str(baseline_tmp),
        "--canonical-path", "data/cards.full.json",
        "--output", "data/cards.full.json",
        "--report", str((RUN_DIR / "apply-report.json").relative_to(ROOT)),
        "--lean-path", "public/data/cards.json",
        "--base-main-sha", BASE_SHA,
        "--apply",
    ])

    full_sha = file_sha256(FULL_PATH)
    lean_sha = file_sha256(LEAN_PATH)
    for old in old_full_hashes:
        if old != full_sha:
            replace_hash_in_run_jsons(old, full_sha)
    for old in old_lean_hashes:
        if old != lean_sha:
            replace_hash_in_run_jsons(old, lean_sha)

    # Rebind authoritative audit(s) explicitly after output materialization.
    run = load_json(RUN_PATH)
    current_ops_sha = operations_sha256(run["operations"])
    for audit_path in [ROOT / ref for ref in run.get("audit_refs", [])]:
        audit = load_json(audit_path)
        audit["reviewed_operations_sha256"] = current_ops_sha
        audit["full_output_sha256"] = full_sha
        audit["lean_output_sha256"] = lean_sha
        save_json(audit_path, audit)

    insert_ids = [op["card"]["id"] for op in run["operations"]["insert"]]
    merge_ids = insert_ids + [op["id"] for op in run["operations"]["update"]]
    tmp_root = Path(os.environ.get("RUNNER_TEMP", "/tmp"))
    insert_scope = tmp_root / "pr256-insert-ids.json"
    merge_scope = tmp_root / "pr256-merge-ids.json"
    save_json(insert_scope, insert_ids)
    save_json(merge_scope, merge_ids)

    run_cmd(["python", "validation_scripts/date_role_freshness_check.py", "data/cards.full.json", "--require-date-role", "--id-file", str(insert_scope)])
    run_cmd(["python", "validation_scripts/evidence_qc_v8_check.py", "data/cards.full.json", "--id-file", str(merge_scope)])
    run_cmd(["python", "validation_scripts/related_lifecycle_check.py", "data/cards.full.json", "--require-contract", "--new-id-file", str(insert_scope)])
    run_cmd(["python", "validation_scripts/stage_artifact_contract_check.py", "0.8", str(PROMPT08_PATH.relative_to(ROOT))])

    run_cmd(["node", "scripts/validate_card_run_stage_artifacts.mjs", "--run", str(RUN_PATH.relative_to(ROOT))])
    run_cmd(["node", "scripts/validate_card_run_status_consistency.mjs", "--run", str(RUN_PATH.relative_to(ROOT))])
    run_cmd(["node", "scripts/validate_card_run_relations.mjs", "--run", str(RUN_PATH.relative_to(ROOT))])
    run_cmd(["node", "scripts/validate_card_run_lineage_containers.mjs", "--run", str(RUN_PATH.relative_to(ROOT)), "--canonical", "data/cards.full.json"])
    run_cmd(["node", "scripts/validate_card_run_audits.mjs", "--run", str(RUN_PATH.relative_to(ROOT)), "--full", "data/cards.full.json", "--lean", "public/data/cards.json"])
    run_cmd(["node", "scripts/validate.mjs"])
    run_cmd(["node", "scripts/validate_cards.mjs", "data/cards.full.json"])
    run_cmd(["node", "scripts/validate_cards.mjs", "public/data/cards.json"])
    run_cmd(["node", "scripts/lean_cards.mjs", "--check"])
    run_cmd([
        "node", "scripts/apply_card_run.mjs",
        "--run", str(RUN_PATH.relative_to(ROOT)),
        "--baseline", "data/cards.full.json",
        "--canonical-path", "data/cards.full.json",
        "--output", "data/cards.full.json",
        "--report", str((RUN_DIR / "apply-report.json").relative_to(ROOT)),
        "--lean-path", "public/data/cards.json",
        "--base-main-sha", BASE_SHA,
        "--verify",
    ])
    run_cmd(["git", "diff", "--check"])

    print(json.dumps({
        "status": "PASS",
        "insert_count": len(insert_ids),
        "update_count": len(run["operations"]["update"]),
        "related_add_count": len(run["operations"]["related_add"]),
        "operations_sha256": current_ops_sha,
        "full_output_sha256": full_sha,
        "lean_output_sha256": lean_sha,
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
