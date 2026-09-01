#!/usr/bin/env python3
from __future__ import annotations
import argparse, json, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "docs/llm_prompts/v1/GOVERNANCE_LIFECYCLE_REGISTRY.json"
REGIONS = {"korea","north_america","china","japan","europe","material_global_markets"}
TOPICS = {"cells_chemistries","materials_components","pouch_pouch_film_demand","ess_bess","ev_charging","manufacturing_capacity_utilisation","grid_ai_data_centre_power","critical_minerals_refining","recycling","policy_trade_sanctions_subsidies_localisation","competitors_customers","prices_costs_margins","financing","safety_recall_commissioning_operation"}
ALIASES = {"a":"A","stage_a":"A","0.1":"A","b":"B","stage_b":"B","0.2":"B","c":"C","stage_c":"C","0.3":"C","0.4":"0.4","0.5":"0.5","0.6":"0.6","0.7":"0.7"}
BUCKETS = {"A":["strict_passed_spec"],"B":["draft_cards","draft_card"],"C":["accepted_fact_safe"],"0.4":["addable_merge_safe"],"0.5":["evidence_complete_and_source_claim_covered"],"0.6":["content_enriched_and_language_polished"],"0.7":["publish_ready"]}
STAGES = tuple(BUCKETS)

class Blocked(Exception): pass

def load(path: Path): return json.loads(path.read_text(encoding="utf-8-sig"))
def repo_json(ref: str) -> Path:
    if not isinstance(ref,str) or not ref or not ref.endswith(".json") or ref.startswith("/") or ".." in Path(ref).parts: raise Blocked(f"invalid repository JSON ref: {ref}")
    p=(ROOT/ref).resolve()
    if not p.is_file() or ROOT not in p.parents: raise Blocked(f"missing repository JSON ref: {ref}")
    return p

def strings(v,label):
    if not isinstance(v,list) or any(not isinstance(x,str) or not x.strip() for x in v): raise Blocked(f"{label} must be non-empty string array")
    out=[x.strip() for x in v]
    if len(out)!=len(set(out)): raise Blocked(f"{label} contains duplicates")
    return set(out)

def validate_preflight(run):
    a=load(repo_json(run["document_universe_manifest_ref"])); r=load(REGISTRY)
    expected_c=set(r.get("active_canonical",[]))|set(r.get("active_named_prompts",[]))
    expected_v=set(r.get("active_validator_contracts",[]))
    expected_m=set(r.get("open_remediations",[]))|set(r.get("activation_required_migrations",[]))
    if strings(a.get("active_canonical_paths"),"0.0D.active_canonical_paths")!=expected_c: raise Blocked("0.0D active_canonical_paths != current registry active set")
    if strings(a.get("active_validator_contract_paths"),"0.0D.active_validator_contract_paths")!=expected_v: raise Blocked("0.0D active_validator_contract_paths != current registry validator set")
    if strings(a.get("applicable_remediation_or_migration"),"0.0D.applicable_remediation_or_migration")!=expected_m: raise Blocked("0.0D applicable remediation/migration != current registry set")
    required=len(expected_c|expected_v|expected_m)
    if a.get("active_full_read_count")!=required: raise Blocked(f"0.0D active_full_read_count must equal exact active/dependency closure ({required})")

def axis_matrix(v,required,label):
    if not isinstance(v,dict): raise Blocked(f"{label} must be object")
    missing=sorted(required-set(v))
    if missing: raise Blocked(f"{label} missing axes: {missing}")
    for key in required:
        row=v[key]
        if not isinstance(row,dict) or row.get("status") not in {"searched","blocked"}: raise Blocked(f"{label}.{key}.status must be searched|blocked")
        if row["status"]=="blocked" and (not isinstance(row.get("reason"),str) or not row["reason"].strip()): raise Blocked(f"{label}.{key}.reason required when blocked")

def validate_coverage(run):
    a=load(repo_json(run["coverage_discovery_ref"])); axis_matrix(a.get("regional_coverage_matrix"),REGIONS,"0.0C.regional_coverage_matrix"); axis_matrix(a.get("topic_coverage_matrix"),TOPICS,"0.0C.topic_coverage_matrix")

def stage(payload,label):
    raw=payload.get("stage")
    if not isinstance(raw,str) or not raw.strip(): raise Blocked(f"{label}.stage required")
    s=ALIASES.get(raw.strip().lower())
    if not s: raise Blocked(f"{label}.stage={raw} is not an ordinary stage; 0.2R/0.3R cannot substitute")
    return s

def spec_ids(payload,s):
    ids=set()
    for bucket in BUCKETS[s]:
        v=payload.get(bucket); rows=v if isinstance(v,list) else [v] if isinstance(v,dict) else []
        for row in rows:
            if isinstance(row,dict):
                x=row.get("spec_id") if s=="A" else row.get("source_spec_id")
                if isinstance(x,str) and x.strip(): ids.add(x.strip())
    return ids

def canonical_map():
    data=load(ROOT/"data/cards.full.json"); return {c["id"]:c["source_spec_id"] for c in data.get("cards",[]) if isinstance(c,dict) and isinstance(c.get("id"),str) and isinstance(c.get("source_spec_id"),str) and c["source_spec_id"].strip()}

def op_spec(kind,op,known,inserted,label):
    if kind=="insert":
        x=(op.get("card") or {}).get("source_spec_id");
        if not isinstance(x,str) or not x.strip(): raise Blocked(f"{label}.card.source_spec_id required")
        return x.strip()
    if kind=="update":
        cid=op.get("id"); old=inserted.get(cid) or known.get(cid); declared=op.get("source_spec_id")
        if isinstance(declared,str): declared=declared.strip() or None
        else: declared=None
        if old and declared and old!=declared: raise Blocked(f"{label}.source_spec_id conflicts with canonical identity")
        if old: return old
        if not declared: raise Blocked(f"{label}.source_spec_id required for legacy card without canonical source_spec_id")
        return declared
    sid,tid=op.get("source_id"),op.get("target_id"); ss=inserted.get(sid) or known.get(sid); ts=inserted.get(tid) or known.get(tid); declared=op.get("source_spec_id"); ident=op.get("identity_card_id")
    declared=declared.strip() if isinstance(declared,str) and declared.strip() else None
    if isinstance(ident,str) and ident.strip() not in {sid,tid}: raise Blocked(f"{label}.identity_card_id must equal source_id or target_id")
    if ss or ts:
        if declared and declared not in {x for x in (ss,ts) if x}: raise Blocked(f"{label}.source_spec_id does not match a governed endpoint")
        return declared or ss or ts
    if not declared or not isinstance(ident,str) or not ident.strip(): raise Blocked(f"{label} requires source_spec_id + identity_card_id when both legacy endpoints lack source_spec_id")
    return declared

def validate_operations(run):
    known=canonical_map(); inserted={op.get("card",{}).get("id"):op.get("card",{}).get("source_spec_id") for op in run.get("operations",{}).get("insert",[]) if isinstance(op,dict)}
    for kind in ("insert","update","related_add"):
        ops=run.get("operations",{}).get(kind)
        if not isinstance(ops,list): raise Blocked(f"operations.{kind} must be array")
        for i,op in enumerate(ops):
            label=f"{kind}[{i}]"; expected=op_spec(kind,op,known,inserted,label); matched=set()
            refs=op.get("stage_artifacts")
            if not isinstance(refs,list) or not refs: raise Blocked(f"{label}.stage_artifacts required")
            for j,ref in enumerate(refs):
                p=load(repo_json(ref)); s=stage(p,f"{label}.stage_artifacts[{j}]")
                if p.get("run_id")!=run.get("run_id") or p.get("base_main_commit_sha")!=run.get("base_main_commit_sha") or p.get("base_full_blob_sha")!=run.get("base_full_blob_sha"): raise Blocked(f"{label}.stage_artifacts[{j}] stale run/baseline binding")
                if expected in spec_ids(p,s): matched.add(s)
            missing=[s for s in STAGES if s not in matched]
            if missing: raise Blocked(f"{label} missing current-run candidate binding at stages {missing}")

def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--run"); ap.add_argument("--self-test",action="store_true"); args=ap.parse_args()
    if args.self_test:
        try: stage({"stage":"0.2R"},"x")
        except Blocked: pass
        else: raise RuntimeError("revise stage substitution not blocked")
        axis_matrix({k:{"status":"searched"} for k in REGIONS},REGIONS,"regions")
        print("PASS: V4 binding hardening self-test"); return 0
    run=load(repo_json(args.run)); validate_preflight(run); validate_coverage(run); validate_operations(run); print(json.dumps({"status":"PASS","registry_binding":"PASS","coverage_axes":"PASS","stage_baseline_binding":"PASS"})); return 0

if __name__=="__main__":
    try: raise SystemExit(main())
    except Blocked as e: print(f"FAIL [BLOCKED_V4_BINDING]: {e}",file=sys.stderr); raise SystemExit(1)
