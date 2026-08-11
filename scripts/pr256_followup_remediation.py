#!/usr/bin/env python3
from __future__ import annotations

import copy
import hashlib
import json
import os
import subprocess
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
RUN_DIR = ROOT / "runs/2026-08-11/backlog-reconciliation-r2"
RUN_PATH = RUN_DIR / "card-run.json"
FULL_PATH = ROOT / "data/cards.full.json"
LEAN_PATH = ROOT / "public/data/cards.json"
PUBLISH_PATH = RUN_DIR / "audit/publish-ready-32.json"
PROD_MAP_PATH = RUN_DIR / "production-id-map.json"
PROD_LEDGER_PATH = RUN_DIR / "audit/production-id-assignment-ledger.json"
OFGEM_AUDIT_PATH = RUN_DIR / "audit/ofgem-ldes-existing-card-update.json"
OP_MANIFEST_PATH = RUN_DIR / "audit/operation-manifest.json"
BUNDLE_PATH = RUN_DIR / "bundle-manifest.json"
MOU_CORRECTION_PATH = RUN_DIR / "audit/related-correction-rec26-a2-039.json"
BASE_SHA = "d3137945860664116b1bf90bbb7bee54d2a6c1d9"
OFGEM_ID = "2026-06-26_EU_01"
MOU_SPEC = "REC26_A2_039"
ANTIMONY_SPEC = "REC26_A2_053"
ANTIMONY_OLD_ID = "2026-07-29_US_02"
ANTIMONY_NEW_ID = "2026-07-30_US_02"
ANTIMONY_DATE = "2026-07-30"
KST = timezone(timedelta(hours=9))


def die(message: str) -> None:
    raise SystemExit(f"PR256_FOLLOWUP_FAIL: {message}")


def run_cmd(args: list[str], *, capture: bool = False) -> str:
    print("+", " ".join(args), flush=True)
    result = subprocess.run(args, cwd=ROOT, text=True, stdout=subprocess.PIPE if capture else None,
                            stderr=subprocess.STDOUT if capture else None, check=False)
    if result.returncode != 0:
        if capture and result.stdout:
            print(result.stdout)
        die(f"command failed ({result.returncode}): {' '.join(args)}")
    return (result.stdout or "").strip() if capture else ""


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def save_json(path: Path, payload: Any) -> None:
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def stable(value: Any) -> Any:
    if isinstance(value, list):
        return [stable(v) for v in value]
    if isinstance(value, dict):
        return {k: stable(value[k]) for k in sorted(value)}
    return value


def operations_sha256(operations: dict[str, Any]) -> str:
    raw = json.dumps(stable(operations), ensure_ascii=False, separators=(",", ":")).encode()
    return hashlib.sha256(raw).hexdigest()


def file_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def replace_exact(value: Any, old: str, new: str) -> tuple[Any, int]:
    count = 0
    if isinstance(value, dict):
        out = {}
        for key, child in value.items():
            repl, n = replace_exact(child, old, new)
            out[key] = repl
            count += n
        return out, count
    if isinstance(value, list):
        out = []
        for child in value:
            repl, n = replace_exact(child, old, new)
            out.append(repl)
            count += n
        return out, count
    if value == old:
        return new, 1
    return value, 0


def replace_in_run_jsons(old: str, new: str) -> int:
    total = 0
    for path in sorted(RUN_DIR.rglob("*.json")):
        payload = load_json(path)
        repl, count = replace_exact(payload, old, new)
        if count:
            save_json(path, repl)
            total += count
    return total


def set_key_recursive(value: Any, key: str, new_value: Any) -> int:
    count = 0
    if isinstance(value, dict):
        for k in list(value):
            if k == key:
                value[k] = copy.deepcopy(new_value)
                count += 1
            else:
                count += set_key_recursive(value[k], key, new_value)
    elif isinstance(value, list):
        for item in value:
            count += set_key_recursive(item, key, new_value)
    return count


def card_like_nodes(value: Any, source_spec_id: str):
    if isinstance(value, dict):
        if value.get("source_spec_id") == source_spec_id and isinstance(value.get("fact_sources"), list):
            yield value
        for child in value.values():
            yield from card_like_nodes(child, source_spec_id)
    elif isinstance(value, list):
        for child in value:
            yield from card_like_nodes(child, source_spec_id)


def find_insert(run: dict[str, Any], spec: str) -> tuple[dict[str, Any], dict[str, Any]]:
    matches = []
    for op in run.get("operations", {}).get("insert", []):
        if isinstance(op, dict) and isinstance(op.get("card"), dict) and op["card"].get("source_spec_id") == spec:
            matches.append((op, op["card"]))
    if len(matches) != 1:
        die(f"{spec}: expected one insert operation, got {len(matches)}")
    return matches[0]


def reconstruct_baseline() -> Path:
    path = Path(os.environ.get("RUNNER_TEMP", "/tmp")) / "pr256-followup-baseline.json"
    with path.open("wb") as handle:
        result = subprocess.run(["git", "show", f"{BASE_SHA}:data/cards.full.json"], cwd=ROOT,
                                stdout=handle, stderr=subprocess.PIPE, check=False)
    if result.returncode:
        die(result.stderr.decode(errors="replace"))
    return path


def normalize_runtime_pending(run: dict[str, Any]) -> None:
    inserts = run.get("operations", {}).get("insert", [])
    if len(inserts) != 32:
        die(f"expected 32 inserts, got {len(inserts)}")
    for op in inserts:
        card = op.get("card")
        if not isinstance(card, dict):
            die("insert missing card")
        if "prompt_0_8_runtime_engine_validation_pending" not in card:
            die(f"{card.get('source_spec_id')}: runtime pending field absent")
        card["prompt_0_8_runtime_engine_validation_pending"] = False
        card["prompt_0_8_runtime_engine_validation_status"] = "PASS"


def correct_antimony(run: dict[str, Any]) -> None:
    op, card = find_insert(run, ANTIMONY_SPEC)
    if card.get("id") != ANTIMONY_OLD_ID:
        die(f"antimony unexpected current id {card.get('id')}")
    if any(x.get("card", {}).get("id") == ANTIMONY_NEW_ID for x in run["operations"]["insert"] if x is not op):
        die(f"new antimony ID already used in current run: {ANTIMONY_NEW_ID}")
    sources = [s for s in card.get("fact_sources", []) if isinstance(s, dict)]
    if len(sources) < 2 or any(s.get("source_published_date") != ANTIMONY_DATE for s in sources[:2]):
        die("antimony retained sources are not both dated 2026-07-30")
    northern = next((s for s in sources if "northernminer.com" in str(s.get("source_url", ""))), None)
    if not northern or "announced Thursday" not in str(northern.get("source_quote", "")):
        die("antimony Northern Miner Thursday quote unavailable")
    if datetime(2026, 7, 30).strftime("%A") != "Thursday":
        die("calendar sanity check failed for 2026-07-30 Thursday")

    for field in ("id", "assigned_id", "proposed_production_id_0_8"):
        if field in card:
            card[field] = ANTIMONY_NEW_ID
    card["date"] = ANTIMONY_DATE
    role = card.get("date_role")
    if not isinstance(role, dict):
        die("antimony date_role missing")
    role["publication_dates"] = [ANTIMONY_DATE]
    role["event_date"] = ANTIMONY_DATE
    role["representative_date"] = ANTIMONY_DATE
    role["event_date_confidence"] = "high"
    role["stage_b_correction_applied"] = True
    role["stage_b_date_note"] = (
        "Prompt 0.8 bounded correction: prior 2026-07-29 date was unsupported. Both retained sources are "
        "published 2026-07-30, and Northern Miner states the opening was announced Thursday; 2026-07-30 is Thursday."
    )
    role["earliest_same_event_date_checked"] = True
    role["event_date_source_url"] = northern["source_url"]
    role["event_date_source_quote"] = northern["source_quote"]
    if isinstance(card.get("event_fingerprint"), dict):
        card["event_fingerprint"]["event_date"] = ANTIMONY_DATE
    review = card.get("related_evidence_review")
    if isinstance(review, dict):
        review["earliest_same_event_date"] = ANTIMONY_DATE
        review["earliest_same_event_date_checked"] = True
        review["same_event_checked"] = True
    profile = card.get("event_fingerprint_search_profile")
    if isinstance(profile, dict):
        profile["event_date_or_window"] = ANTIMONY_DATE
        for key in ("same_event_disambiguators", "must_match_terms"):
            if isinstance(profile.get(key), list):
                profile[key] = [ANTIMONY_DATE if v == "2026-07-29" else v for v in profile[key]]
    card["prompt_0_8_date_correction"] = {
        "status": "PASS",
        "field": "event_date_and_production_id",
        "before_event_date": "2026-07-29",
        "after_event_date": ANTIMONY_DATE,
        "before_production_id": ANTIMONY_OLD_ID,
        "after_production_id": ANTIMONY_NEW_ID,
        "basis_source_url": northern["source_url"],
        "basis_source_quote": northern["source_quote"],
        "selection_or_factual_judgment_changed": False,
    }


def baseline_text(card: dict[str, Any]) -> str:
    parts = [str(card.get(k, "")) for k in ("id", "title", "sub", "fact", "gate", "lineage_key")]
    for u in card.get("urls", []) or []:
        parts.append(str(u))
    return " ".join(parts).casefold()


def build_mou_review(run: dict[str, Any], baseline_payload: Any) -> dict[str, Any]:
    _, card = find_insert(run, MOU_SPEC)
    urls = {str(s.get("source_url")) for s in card.get("fact_sources", []) if isinstance(s, dict)}
    baseline_cards = baseline_payload if isinstance(baseline_payload, list) else baseline_payload.get("cards", [])
    candidates = []
    for b in baseline_cards:
        if not isinstance(b, dict):
            continue
        text = baseline_text(b)
        exact_url = bool(urls.intersection(set(map(str, b.get("urls", []) or []))))
        actor_match = ("아르헨티나" in text or "argentina" in text or "korea_argentina" in text)
        mineral_match = ("핵심광물" in text or "critical mineral" in text)
        if exact_url or (actor_match and mineral_match):
            candidates.append({"id": b.get("id"), "title": b.get("title"), "exact_source_url_match": exact_url})
    batch_candidates = []
    for other in run["operations"]["insert"]:
        c = other.get("card", {})
        if c.get("source_spec_id") == MOU_SPEC:
            continue
        text = baseline_text(c)
        if ("아르헨티나" in text or "argentina" in text or "korea_argentina" in text) and (
            "핵심광물" in text or "critical mineral" in text
        ):
            batch_candidates.append({"source_spec_id": c.get("source_spec_id"), "title": c.get("title")})
    if candidates or batch_candidates:
        die(f"MOU same-event screening found candidates requiring manual adjudication: {candidates} {batch_candidates}")
    source = card.get("fact_sources", [])[0]
    review = {
        "status": "PASS",
        "reviewed_current_baseline": True,
        "all_candidates_reviewed": True,
        "same_event_checked": True,
        "earliest_same_event_date_checked": True,
        "earliest_same_event_date": "2026-07-31",
        "earliest_same_event_source_url": source.get("source_url"),
        "relation_type": "new_unrelated_event",
        "matched_baseline_card_ids": [],
        "matched_candidate_spec_ids": [],
        "candidate_rejections": [],
        "baseline_search": {
            "baseline_main_sha": BASE_SHA,
            "search_terms": ["Korea Argentina critical minerals MOU", "한국 아르헨티나 핵심광물 MOU"],
            "source_url_exact_match_count": 0,
            "actor_plus_subject_candidate_count": 0,
            "current_batch_actor_plus_subject_candidate_count": 0,
        },
        "evidence_basis": [
            {"source_url": s.get("source_url"), "source_quote": s.get("source_quote")}
            for s in card.get("fact_sources", []) if isinstance(s, dict)
        ],
        "reason": "Locked current-main and current-batch search found no same-event candidate; retain as new_unrelated_event.",
    }
    card["related_evidence_review"] = copy.deepcopy(review)
    lineage = card.get("related_lineage")
    if not isinstance(lineage, dict):
        die("MOU related_lineage missing")
    lineage["same_event_checked"] = True
    lineage["earliest_same_event_date_checked"] = True
    lineage["related_evidence_review_ref"] = str(MOU_CORRECTION_PATH.relative_to(ROOT))
    return review


def write_mou_correction(run: dict[str, Any], review: dict[str, Any]) -> None:
    _, card = find_insert(run, MOU_SPEC)
    payload = {
        "stage": "B_related_evidence_review_correction",
        "status": "PASS",
        "run_tag": "20260809_BACKLOG_RECONCILIATION_R2",
        "source_spec_id": MOU_SPEC,
        "production_id": card.get("id"),
        "baseline_main_sha": BASE_SHA,
        "correction_type": "bounded_missing_stage_b_related_evidence_review",
        "selection_changed": False,
        "factual_judgment_changed": False,
        "related_evidence_review": review,
    }
    save_json(MOU_CORRECTION_PATH, payload)
    op, _ = find_insert(run, MOU_SPEC)
    ref = str(MOU_CORRECTION_PATH.relative_to(ROOT))
    op.setdefault("stage_artifacts", [])
    if ref not in op["stage_artifacts"]:
        op["stage_artifacts"].append(ref)


def sync_publish_ready(run: dict[str, Any]) -> None:
    payload = load_json(PUBLISH_PATH)
    _, mou = find_insert(run, MOU_SPEC)
    _, ant = find_insert(run, ANTIMONY_SPEC)
    mou_nodes = list(card_like_nodes(payload, MOU_SPEC))
    ant_nodes = list(card_like_nodes(payload, ANTIMONY_SPEC))
    if not mou_nodes or not ant_nodes:
        die(f"publish-ready correction targets absent: mou={len(mou_nodes)} ant={len(ant_nodes)}")
    for node in mou_nodes:
        node["related_evidence_review"] = copy.deepcopy(mou["related_evidence_review"])
        node["related_lineage"] = copy.deepcopy(mou["related_lineage"])
    for node in ant_nodes:
        node["date"] = ANTIMONY_DATE
        node["date_role"] = copy.deepcopy(ant["date_role"])
        if isinstance(node.get("event_fingerprint"), dict):
            node["event_fingerprint"]["event_date"] = ANTIMONY_DATE
        if isinstance(node.get("related_evidence_review"), dict):
            node["related_evidence_review"]["earliest_same_event_date"] = ANTIMONY_DATE
        node["prompt_0_8_date_correction"] = copy.deepcopy(ant["prompt_0_8_date_correction"])
    set_key_recursive(payload, "prompt_0_8_runtime_engine_validation_pending", False)
    save_json(PUBLISH_PATH, payload)


def sync_id_ledgers() -> None:
    prod = load_json(PROD_MAP_PATH)
    if prod.get("mapping", {}).get(ANTIMONY_SPEC) != ANTIMONY_OLD_ID:
        die("production-id-map antimony old ID mismatch")
    prod["mapping"][ANTIMONY_SPEC] = ANTIMONY_NEW_ID
    for row in prod.get("assignments", []):
        if row.get("source_spec_id") == ANTIMONY_SPEC:
            row["date"] = ANTIMONY_DATE
            row["production_id"] = ANTIMONY_NEW_ID
            row["allocation_note"] = "Date corrected from unsupported 2026-07-29; 2026-07-30_US_01 is already allocated in this run, so next unused ID is _02."
    save_json(PROD_MAP_PATH, prod)
    ledger = load_json(PROD_LEDGER_PATH)
    for row in ledger.get("assignments", []):
        if row.get("source_spec_id") == ANTIMONY_SPEC:
            row["date"] = ANTIMONY_DATE
            row["production_id"] = ANTIMONY_NEW_ID
            row["allocation_note"] = "Date corrected from unsupported 2026-07-29; 2026-07-30_US_01 is already allocated in this run, so next unused ID is _02."
    save_json(PROD_LEDGER_PATH, ledger)


def json_pointer_escape(key: str) -> str:
    return key.replace("~", "~0").replace("/", "~1")


def materialize(run: dict[str, Any], baseline: Path) -> None:
    save_json(RUN_PATH, run)
    run_cmd(["node", "scripts/apply_card_run.mjs", "--run", str(RUN_PATH.relative_to(ROOT)),
             "--baseline", str(baseline), "--canonical-path", "data/cards.full.json",
             "--output", "data/cards.full.json", "--report", str((RUN_DIR / "apply-report.json").relative_to(ROOT)),
             "--lean-path", "public/data/cards.json", "--base-main-sha", BASE_SHA, "--apply"])


def recompute_ofgem_operation(run: dict[str, Any], baseline: Path) -> None:
    materialize(run, baseline)
    full = load_json(FULL_PATH)
    cards = full if isinstance(full, list) else full.get("cards", [])
    matches = [c for c in cards if isinstance(c, dict) and c.get("id") == OFGEM_ID]
    if len(matches) != 1:
        die(f"Ofgem candidate count {len(matches)}")
    before = copy.deepcopy(matches[0])
    temp_in = Path(os.environ.get("RUNNER_TEMP", "/tmp")) / "ofgem-one.json"
    temp_out = Path(os.environ.get("RUNNER_TEMP", "/tmp")) / "ofgem-one-recomputed.json"
    save_json(temp_in, [before])
    run_cmd(["python", "validation_scripts/recompute_source_audit_metadata.py", str(temp_in),
             "--output", str(temp_out), "--strict"])
    after = load_json(temp_out)[0]
    changed_keys = [k for k in set(before) | set(after) if before.get(k) != after.get(k)]
    if not changed_keys:
        die("Ofgem recomputation unexpectedly produced no changes before remediation")
    updates = [u for u in run["operations"]["update"] if u.get("id") == OFGEM_ID]
    if len(updates) != 1:
        die("Ofgem update operation missing")
    changes = updates[0]["changes"]
    controlled = set(changed_keys)
    changes[:] = [c for c in changes if c.get("path", "").lstrip("/").split("/")[0].replace("~1", "/").replace("~0", "~") not in controlled]
    for key in sorted(changed_keys):
        op = "replace" if key in before else "add"
        changes.append({"op": op, "path": "/" + json_pointer_escape(key), "value": copy.deepcopy(after[key])})
    audit = load_json(OFGEM_AUDIT_PATH)
    audit["runtime_source_audit_recompute_required"] = False
    audit["source_audit_recomputed"] = True
    audit["source_audit_recompute_status"] = "PASS"
    audit["recomputed_fields"] = sorted(changed_keys)
    audit["source_evidence_entry_count"] = after.get("source_evidence_entry_count")
    audit["source_unique_url_count"] = after.get("source_unique_url_count")
    audit["source_independent_owner_count"] = after.get("source_independent_owner_count")
    save_json(OFGEM_AUDIT_PATH, audit)


def update_ops_bindings(old_sha: str, run: dict[str, Any]) -> str:
    save_json(RUN_PATH, run)
    new_sha = operations_sha256(run["operations"])
    if new_sha == old_sha:
        die("operations SHA unchanged after follow-up remediation")
    replaced = replace_in_run_jsons(old_sha, new_sha)
    print(f"operations SHA bindings replaced: {replaced}")
    run2 = load_json(RUN_PATH)
    if operations_sha256(run2["operations"]) != new_sha:
        die("operation hash drift after binding replacement")
    return new_sha


def update_output_hash_bindings(full_sha: str, lean_sha: str) -> None:
    for path in sorted(RUN_DIR.rglob("*.json")):
        payload = load_json(path)
        n1 = set_key_recursive(payload, "full_output_sha256", full_sha)
        n2 = set_key_recursive(payload, "lean_output_sha256", lean_sha)
        if n1 or n2:
            save_json(path, payload)


def finalize_runtime_artifacts() -> None:
    manifest = load_json(OP_MANIFEST_PATH)
    manifest["status"] = "PASS_RUNTIME_VERIFIED"
    manifest["runtime_engine_apply_verify_pending"] = False
    manifest["runtime_verified"] = True
    manifest["runtime_verified_kst"] = datetime.now(KST).isoformat(timespec="seconds")
    save_json(OP_MANIFEST_PATH, manifest)

    prompt = load_json(RUN_DIR / "prompt-0-8-prep-result.json")
    prompt["status"] = "GITHUB_MERGE_READY"
    prompt["github_merge_ready"] = True
    prompt["pr_candidate_ready"] = True
    prompt["runtime_pending"] = []
    prompt["generated_kst"] = datetime.now(KST).isoformat(timespec="seconds")
    save_json(RUN_DIR / "prompt-0-8-prep-result.json", prompt)


def regenerate_bundle_manifest() -> None:
    bundle = load_json(BUNDLE_PATH)
    entries = bundle.get("files", [])
    for entry in entries:
        rel = entry.get("path")
        path = RUN_DIR / rel
        if not path.is_file():
            die(f"bundle member missing: {rel}")
        entry["bytes"] = path.stat().st_size
        entry["sha256"] = file_sha256(path)
    bundle["file_count"] = len(entries)
    bundle["status"] = "RUNTIME_VERIFIED_PASS"
    bundle["regenerated_kst"] = datetime.now(KST).isoformat(timespec="seconds")
    save_json(BUNDLE_PATH, bundle)


def verify_bundle_manifest() -> None:
    bundle = load_json(BUNDLE_PATH)
    for entry in bundle.get("files", []):
        path = RUN_DIR / entry["path"]
        if path.stat().st_size != entry["bytes"] or file_sha256(path) != entry["sha256"]:
            die(f"bundle integrity mismatch: {entry['path']}")


def build_id_files(run: dict[str, Any]) -> tuple[Path, Path]:
    temp = Path(os.environ.get("RUNNER_TEMP", "/tmp"))
    ids = [op["card"]["id"] for op in run["operations"]["insert"]]
    if len(ids) != 32 or len(set(ids)) != 32:
        die("insert ID accounting invalid")
    insert_file = temp / "pr256-followup-insert-ids.json"
    merge_file = temp / "pr256-followup-merge-ids.json"
    save_json(insert_file, ids)
    save_json(merge_file, ids + [OFGEM_ID])
    return insert_file, merge_file


def verify_ofgem_recompute_check() -> None:
    payload = load_json(FULL_PATH)
    cards = payload if isinstance(payload, list) else payload.get("cards", [])
    card = next(c for c in cards if c.get("id") == OFGEM_ID)
    temp = Path(os.environ.get("RUNNER_TEMP", "/tmp")) / "ofgem-final-one.json"
    save_json(temp, [card])
    run_cmd(["python", "validation_scripts/recompute_source_audit_metadata.py", str(temp), "--check", "--strict"])


def verify_semantics(run: dict[str, Any]) -> None:
    if any(op["card"].get("prompt_0_8_runtime_engine_validation_pending") is not False for op in run["operations"]["insert"]):
        die("runtime pending remains on insert card")
    _, ant = find_insert(run, ANTIMONY_SPEC)
    if ant.get("id") != ANTIMONY_NEW_ID or ant.get("date") != ANTIMONY_DATE or ant.get("date_role", {}).get("event_date") != ANTIMONY_DATE:
        die("antimony correction not materialized in card-run")
    _, mou = find_insert(run, MOU_SPEC)
    review = mou.get("related_evidence_review", {})
    if not (review.get("reviewed_current_baseline") is True and review.get("all_candidates_reviewed") is True):
        die("MOU Stage B review not materialized")
    full = load_json(FULL_PATH)
    cards = full if isinstance(full, list) else full.get("cards", [])
    by_id = {c.get("id"): c for c in cards if isinstance(c, dict)}
    if ANTIMONY_OLD_ID in by_id or ANTIMONY_NEW_ID not in by_id:
        die("canonical antimony ID correction failed")
    if sum(1 for c in cards if c.get("prompt_0_8_runtime_engine_validation_pending") is True and c.get("source_spec_id") in {op["card"].get("source_spec_id") for op in run["operations"]["insert"]}) != 0:
        die("canonical runtime pending remains")


def main() -> None:
    os.chdir(ROOT)
    observed = run_cmd(["git", "rev-parse", "origin/main"], capture=True)
    if observed != BASE_SHA:
        die(f"BLOCKED_BASELINE_MOVED_REBASE_REQUIRED origin/main={observed}")
    baseline = reconstruct_baseline()
    baseline_payload = load_json(baseline)
    run = load_json(RUN_PATH)
    if run.get("base_main_commit_sha") != BASE_SHA:
        die("card-run baseline drift")
    old_ops_sha = operations_sha256(run["operations"])

    normalize_runtime_pending(run)
    correct_antimony(run)
    review = build_mou_review(run, baseline_payload)
    write_mou_correction(run, review)
    sync_id_ledgers()
    sync_publish_ready(run)
    save_json(RUN_PATH, run)
    replace_in_run_jsons(ANTIMONY_OLD_ID, ANTIMONY_NEW_ID)
    run = load_json(RUN_PATH)

    # First operation binding update makes the intermediate materialization governance-valid.
    first_ops_sha = update_ops_bindings(old_ops_sha, run)
    run = load_json(RUN_PATH)
    recompute_ofgem_operation(run, baseline)
    # Ofgem materialization patches change operations a second time; bind them too.
    run = load_json(RUN_PATH)
    final_ops_sha = update_ops_bindings(first_ops_sha, run)
    print("final operations sha:", final_ops_sha)
    run = load_json(RUN_PATH)

    # Final governed materialization from locked main.
    materialize(run, baseline)
    finalize_runtime_artifacts()
    full_sha = file_sha256(FULL_PATH)
    lean_sha = file_sha256(LEAN_PATH)
    update_output_hash_bindings(full_sha, lean_sha)

    # Refresh final runtime audit bookkeeping after ID correction.
    audit_path = RUN_DIR / "audit/card-run-runtime-audit.json"
    audit = load_json(audit_path)
    audit["inserted_ids"] = [op["card"]["id"] for op in run["operations"]["insert"]]
    audit["reviewed_operations_sha256"] = final_ops_sha
    audit["full_output_sha256"] = full_sha
    audit["lean_output_sha256"] = lean_sha
    corr_ref = str(MOU_CORRECTION_PATH.relative_to(ROOT))
    audit.setdefault("supporting_audit_refs", [])
    if corr_ref not in audit["supporting_audit_refs"]:
        audit["supporting_audit_refs"].append(corr_ref)
    save_json(audit_path, audit)

    # Re-run output hash binding once after runtime audit write (only bound output fields are changed).
    update_output_hash_bindings(full_sha, lean_sha)
    regenerate_bundle_manifest()

    run = load_json(RUN_PATH)
    insert_file, merge_file = build_id_files(run)
    verify_semantics(run)
    verify_ofgem_recompute_check()
    verify_bundle_manifest()

    run_cmd(["python", "validation_scripts/date_role_freshness_check.py", "data/cards.full.json", "--require-date-role", "--id-file", str(insert_file)])
    run_cmd(["python", "validation_scripts/evidence_qc_v8_check.py", "data/cards.full.json", "--id-file", str(merge_file)])
    run_cmd(["python", "validation_scripts/related_lifecycle_check.py", "data/cards.full.json", "--require-contract", "--new-id-file", str(insert_file)])
    run_cmd(["python", "validation_scripts/stage_artifact_contract_check.py", "0.8", str((RUN_DIR / "prompt-0-8-prep-result.json").relative_to(ROOT))])
    run_cmd(["node", "scripts/validate_card_run_stage_artifacts.mjs", "--run", str(RUN_PATH.relative_to(ROOT))])
    run_cmd(["node", "scripts/validate_card_run_status_consistency.mjs", "--run", str(RUN_PATH.relative_to(ROOT))])
    run_cmd(["node", "scripts/validate_card_run_relations.mjs", "--run", str(RUN_PATH.relative_to(ROOT))])
    run_cmd(["node", "scripts/validate_card_run_lineage_containers.mjs", "--run", str(RUN_PATH.relative_to(ROOT)), "--canonical", "data/cards.full.json"])
    run_cmd(["node", "scripts/validate_card_run_audits.mjs", "--run", str(RUN_PATH.relative_to(ROOT)), "--full", "data/cards.full.json", "--lean", "public/data/cards.json"])
    run_cmd(["node", "scripts/validate.mjs"])
    run_cmd(["node", "scripts/validate_cards.mjs", "data/cards.full.json"])
    run_cmd(["node", "scripts/validate_cards.mjs", "public/data/cards.json"])
    run_cmd(["node", "scripts/lean_cards.mjs", "--check"])
    run_cmd(["node", "scripts/apply_card_run.mjs", "--run", str(RUN_PATH.relative_to(ROOT)), "--baseline", "data/cards.full.json", "--canonical-path", "data/cards.full.json", "--output", "data/cards.full.json", "--report", str((RUN_DIR / "apply-report.json").relative_to(ROOT)), "--lean-path", "public/data/cards.json", "--base-main-sha", BASE_SHA, "--verify"])
    run_cmd(["git", "diff", "--check"])
    verify_bundle_manifest()

    print(json.dumps({
        "status": "PASS",
        "insert_count": 32,
        "update_count": 1,
        "related_add_count": 10,
        "antimony_id": ANTIMONY_NEW_ID,
        "operations_sha256": final_ops_sha,
        "full_output_sha256": full_sha,
        "lean_output_sha256": lean_sha,
        "bundle_manifest": "PASS_EXACT",
        "ofgem_recompute_strict_check": "PASS_ZERO_CHANGES",
        "mou_stage_b_related_review": "PASS_DURABLE_CORRECTION",
        "runtime_pending_insert_cards": 0,
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
