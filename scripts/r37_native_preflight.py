#!/usr/bin/env python3
"""Stage-only native 0.0D V4 probe, fail closed, no canonical file mutations.
Exact main commit, Git object docs read, validator execution and evidentiary receipts.
"""
import hashlib
import json
import os
import re
import subprocess
import sys
import traceback
from pathlib import Path
from datetime import datetime, timezone

MAIN = "805c2718d6daf40a219ae94242d9687e33ac3e88"
FULL = "07a91714e56be2a8bfad10ab63822f0c5cb3f06e"
LEAN = "8ebad37e98639ad97a30e52063d7325da77be650"
PR386 = "c5cb244b83f1668c402146bce31743d23509442b"
ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "runs" / "2026-10-24" / "r37-native-0-0d-evidence"
REGPATH = "docs/llm_prompts/v1/GOVERNANCE_LIFECYCLE_REGISTRY.json"
STAGEPATH = (OUT / "R37_0_0D_V4_STAGE_20261024.json").relative_to(ROOT).as_posix()


def sha(data):
    return hashlib.sha256(data).hexdigest()


def git(*args):
    p = subprocess.run(["git", *args], cwd=ROOT, capture_output=True, timeout=45)
    if p.returncode != 0:
        raise RuntimeError(f"git {' '.join(args)}: {p.stderr.decode(errors='replace')[:300]}")
    return p.stdout


def gitstr(*args):
    return git(*args).decode().strip()


def read_locked(path):
    return git("show", f"{MAIN}:{path}")


def dump(name, value):
    p = OUT / name
    p.write_text(json.dumps(value, indent=2, ensure_ascii=False, sort_keys=True) + "\n", encoding="utf-8")
    return p


def native(cmd):
    p = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True, timeout=180)
    return {"command": cmd, "exit_code": p.returncode, "stdout": p.stdout[-7000:], "stderr": p.stderr[-7000:]}


def preflight():
    now = datetime.now(timezone.utc).isoformat()
    status = "BLOCKED"
    errors = []
    evidence = {"timestamp_utc": now, "required_docs": [], "classifications": [], "runtime_tests": []}
    stage = {"stage": "0.0D", "status": status,
        "repository_head_sha": MAIN, "canonical_full_blob_sha": FULL,
        "docs_inventory_count": 0, "classified_count": 0, "active_full_read_count": 0,
        "active_canonical_paths": [], "active_validator_contract_paths": [],
        "applicable_remediation_or_migration": [], "superseded_or_reference_paths": [],
        "unclassified_paths": [], "unread_active_paths": [], "unresolved_dependencies": [],
        "unresolved_conflicts": [], "unregistered_active_looking_paths": [],
        "active_override_or_addendum_count": 0,
        "stage_a_embedded_news_value_verified": False,
        "all_docs_files_read_or_parsed": False, "unresolved_rule_conflicts": [],
        "incomplete_universe_defects": [], "stage_0_0c_authorized": False,
        "execution_evidence": {"run_type": "R37_LOCKED_MAIN_NATIVE_STAGE_ONLY", "commit_sha": MAIN,
                               "lean_blob_sha": LEAN, "pr_386_unchanged_head": PR386}}
    try:
        observed_main = gitstr("rev-parse", "refs/remotes/origin/main")
        evidence["observed_origin_main"] = observed_main
        if observed_main != MAIN:
            errors.append(f"BASE_MAIN_MOVED: {observed_main} != {MAIN}")
        for p, expected in (("data/cards.full.json", FULL), ("public/data/cards.json", LEAN)):
            actual = gitstr("rev-parse", f"{MAIN}:{p}")
            evidence[p + "_blob"] = actual
            if actual != expected: errors.append(f"BASE_BLOB_CHANGED {p} {actual}")
        docs = sorted(x for x in gitstr("ls-tree", "-r", "--name-only", MAIN, "docs").splitlines() if x)
        registry = json.loads(read_locked(REGPATH))
        fields = {"active_canonical":"ACTIVE_CANONICAL", "active_named_prompts":"ACTIVE_CANONICAL",
                  "active_validator_contracts":"ACTIVE_VALIDATOR_CONTRACT", "open_remediations":"OPEN_REMEDIATION",
                  "activation_required_migrations":"ACTIVE_MIGRATION", "superseded":"SUPERSEDED", "reference_only":"REFERENCE_ONLY"}
        classifications = {}
        for f, label in fields.items():
            items = registry.get(f)
            if not isinstance(items, list):
                errors.append(f"INVALID_REGISTRY_FIELD {f}")
                continue
            for item in items:
                if item in classifications: errors.append(f"MULTIPLE_LIFECYCLE_CLASS {item}")
                classifications[item] = label
        stage["docs_inventory_count"] = len(docs)
        stage["classified_count"] = len(set(docs) & set(classifications))
        stage["unclassified_paths"] = sorted(set(docs) - set(classifications))
        stale = sorted(set(classifications) - set(docs))
        if stale: errors.append("REGISTRY_STALE " + ",".join(stale))
        stage["active_canonical_paths"] = sorted(set(registry.get("active_canonical", []) + registry.get("active_named_prompts", [])))
        stage["active_validator_contract_paths"] = sorted(set(registry.get("active_validator_contracts", [])))
        stage["applicable_remediation_or_migration"] = sorted(set(registry.get("open_remediations", []) + registry.get("activation_required_migrations", [])))
        stage["superseded_or_reference_paths"] = sorted(set(registry.get("superseded", []) + registry.get("reference_only", [])))
        required = sorted(set(stage["active_canonical_paths"] + stage["active_validator_contract_paths"] + stage["applicable_remediation_or_migration"]))
        if registry.get("status") != "ACTIVE_VALIDATOR_CONTRACT": errors.append("REGISTRY_NOT_ACTIVE")
        if registry.get("active_override_or_addendum_count") != 0: errors.append("UNRESOLVED_ACTIVE_OVERRIDE")
        stage["active_override_or_addendum_count"] = registry.get("active_override_or_addendum_count", -1)
        if len(required) != 43: errors.append(f"UNEXPECTED_REQUIRED_CLOSURE_LENGTH {len(required)} (review no hardcoded reclassification)")
        for p in docs:
            # The registry classifies every file; historical docs do not become rules just by being inspected.
            evidence["classifications"].append({"path": p, "lifecycle_class": classifications.get(p, "UNCLASSIFIED")})
        for path in required:
            try:
                buf = read_locked(path)
                if not buf.strip(): raise RuntimeError("zero-byte or blank required source")
                hdr = buf[:4096].decode("utf-8-sig",errors="replace")
                found = re.search(r"(?im)^\s*(?:\*\*)?Status(?:\*\*)?\s*:\s*`?([A-Z_]+)", hdr)
                marker = found.group(1) if found else "UNDECLARED"
                if marker in ("SUPERSEDED", "REFERENCE_ONLY", "ARCHIVED") and classifications[path] in ("ACTIVE_CANONICAL", "ACTIVE_VALIDATOR_CONTRACT"):
                    errors.append("CONFLICTING_ACTIVE_HEADER " + path + "=" + marker)
                if path.endswith(".json"): json.loads(buf)
                evidence["required_docs"].append({"path": path, "sha256": sha(buf),
                    "git_blob_sha": gitstr("rev-parse",f"{MAIN}:{path}"),
                    "bytes": len(buf), "declared_header_status":marker})
            except Exception as exc:
                stage["unread_active_paths"].append(path)
                errors.append("UNREADABLE_REQUIRED " + path + ": " + str(exc))
        stage["active_full_read_count"] = len(evidence["required_docs"])
        # Check named prompts are real, standalone bodies and Stage A's embedded selection/Related prepass.
        for path in registry.get("active_named_prompts", []):
            b = read_locked(path)
            if not b.lstrip().startswith(b"# ") or len(b) < 150:
                errors.append("INCOMPLETE_NAMED_PROMPT " + path)
        stage_a = read_locked("docs/llm_prompts/v1/01_PROMPT_0_1_Stage_A.md").decode("utf-8-sig")
        stage["stage_a_embedded_news_value_verified"] = all(x in stage_a for x in (
            "EMBEDDED_NEWS_VALUE_SELECTION_V4", "Related pre-pass", "related_prepass", "decision_news_value_score"))
        if not stage["stage_a_embedded_news_value_verified"]: errors.append("STAGE_A_NEWS_VALUE_OR_RELATED_INCOMPLETE")
        needed = ["docs/WORKFLOW.md", "docs/OPERATIONS.md", "docs/DOCUMENT_UNIVERSE_POLICY.md",
                  "docs/RUN_GOVERNANCE_INDEX.md", "docs/llm_prompts/v1/PROMPT_MANIFEST.md",
                  "docs/llm_prompts/v1/LLM_PROMPT_GITHUB_CANONICAL_V1_MANIFEST.json",
                  "docs/llm_prompts/v1/UPLOAD_MANIFEST.json", "docs/RELATED_LIFECYCLE_CONTRACT.md"]
        for path in needed:
            if path not in required: stage["unresolved_dependencies"].append(path)
        if stage["unclassified_paths"]: errors.append("UNCLASSIFIED_DOCS")
        if stage["unresolved_dependencies"]: errors.append("MISSING_REQUIRED_DEPENDENCIES")
        stage["all_docs_files_read_or_parsed"] = not errors and stage["classified_count"] == len(docs) and len(evidence["required_docs"]) == len(required)
        stage["stage_0_0c_authorized"] = stage["all_docs_files_read_or_parsed"]
        stage["status"] = "PASS" if stage["all_docs_files_read_or_parsed"] else "BLOCKED"
        stage["incomplete_universe_defects"] = errors.copy()
        dump(Path(STAGEPATH).name, stage)
        if not errors:
            js = ROOT / "scripts" / ".r37-native-stage-only-probe.mjs"
            original = (ROOT / "scripts" / "validate_card_run_v4_hardening.mjs").read_text()
            assert "const args = process.argv.slice(2);" in original
            prefix = original.split("const args = process.argv.slice(2);")[0]
            snippet = "\nconst probeRun = " + json.dumps({"document_universe_manifest_ref":STAGEPATH,
                "base_main_commit_sha":MAIN,"base_full_blob_sha":FULL}) + ";\n" \
                + "validateDocumentUniverse(probeRun, '.'); console.log('R37_NATIVE_JS_STAGE_ONLY_PASS');\n"
            try:
                js.write_text(prefix + snippet)
                checks = [native(["node", str(js.relative_to(ROOT))]),
                          native(["python3", "-c", "import sys;sys.path.insert(0,'.');from validation_scripts import card_run_v4_binding_hardening as c;c.validate_preflight(" + repr({"document_universe_manifest_ref":STAGEPATH,"base_main_commit_sha":MAIN}) + ");print('R37_NATIVE_PY_STAGE_ONLY_PASS')"]),
                          native(["node", "scripts/validate_card_run_v4_hardening.mjs", "--self-test"]),
                          native(["python3", "validation_scripts/card_run_v4_binding_hardening.py", "--self-test"])]
            finally:
                js.unlink(missing_ok=True)
            evidence["runtime_tests"] = checks
            for check in checks:
                if check["exit_code"] != 0: errors.append("NATIVE_VALIDATOR_FAILURE: " + " ".join(check["command"]) + " : " + check["stderr"][-450:])
            if errors:
                stage["status"] = "BLOCKED"
                stage["stage_0_0c_authorized"] = False
                stage["all_docs_files_read_or_parsed"] = False
                stage["incomplete_universe_defects"] = errors.copy()
                dump(Path(STAGEPATH).name, stage)
    except Exception as exc:
        errors.append("STAGE_RUNTIME_ERROR: " + repr(exc))
        evidence["exception_trace"] = traceback.format_exc()[-5000:]
        stage["status"]="BLOCKED"
        stage["stage_0_0c_authorized"] = False
        stage["incomplete_universe_defects"] = errors.copy()
        dump(Path(STAGEPATH).name, stage)
    dump("R37_96_DOCS_CLASSIFICATION.json", evidence["classifications"])
    dump("R37_43_ACTIVE_DEEP_READ_RECEIPT.json", evidence["required_docs"])
    dump("R37_NATIVE_VALIDATOR_QC.json", {"status": stage["status"], "main_sha": MAIN,
        "full_blob_sha":FULL, "runtime_tests": evidence["runtime_tests"], "defects":errors,
        "note":"STAGE_ONLY: integrated card run / 0.0C / Stage A not executed; no production update"})
    dump("R37_0_0C_GATE_HOLD.json", {"stage":"0.0C","status":"BLOCKED","reason":"1313 observations remain formally UNASSIGNED; HUB 6+14, Editorial 12 and Weekly 26 full coverage not complete; do not fabricate PASS", "stage_a_authorized":False})
    manifest={f.name:sha(f.read_bytes()) for f in sorted(OUT.glob("*")) if f.is_file()}
    dump("R37_SHA256_MANIFEST.json",{"entries_sha256":manifest,"locked_main_sha":MAIN,"canonical_full_blob_sha":FULL,"stage_0_0d":stage["status"]})
    print(json.dumps({"status":stage["status"],"classified":stage["classified_count"],
        "inventory":stage["docs_inventory_count"], "deep_read":stage["active_full_read_count"],
        "native_checks":[x["exit_code"] for x in evidence["runtime_tests"]],"defects":errors}, indent=2))
    return 0 if stage["status"] == "PASS" else 1


if __name__ == "__main__":
    OUT.mkdir(parents=True,exist_ok=True)
    sys.exit(preflight())
