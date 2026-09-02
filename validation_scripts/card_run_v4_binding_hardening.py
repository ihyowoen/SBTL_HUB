#!/usr/bin/env python3
from __future__ import annotations
import argparse, json, os, subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "docs/llm_prompts/v1/GOVERNANCE_LIFECYCLE_REGISTRY.json"
COVERAGE_AXES_PATH = Path(os.environ.get(
    "WORKFLOW_V4_COVERAGE_AXES_PATH",
    str(ROOT / "schemas/workflow-v4-coverage-axes.json"),
)).resolve()
ALIASES = {"a":"A","stage_a":"A","0.1":"A","b":"B","stage_b":"B","0.2":"B","c":"C","stage_c":"C","0.3":"C","0.4":"0.4","0.5":"0.5","0.6":"0.6","0.7":"0.7"}
BUCKETS = {"A":["strict_passed_spec"],"B":["draft_cards","draft_card"],"C":["accepted_fact_safe"],"0.4":["addable_merge_safe"],"0.5":["evidence_complete_and_source_claim_covered"],"0.6":["content_enriched_and_language_polished"],"0.7":["publish_ready"]}
STAGES = tuple(BUCKETS)
ALLOWED_RELATED_ADD_TYPES = {"distinct_follow_up", "program_lineage"}
IDENTITY_ROOT = "source_spec_id"

class Blocked(Exception): pass

def load(path: Path): return json.loads(path.read_text(encoding="utf-8-sig"))
def repo_json(ref: str) -> Path:
    if not isinstance(ref,str) or not ref or not ref.endswith(".json") or ref.startswith("/") or ".." in Path(ref).parts: raise Blocked(f"invalid repository JSON ref: {ref}")
    p=(ROOT/ref).resolve()
    if not p.is_file() or ROOT not in p.parents: raise Blocked(f"missing repository JSON ref: {ref}")
    return p

def strings(v,label,allow_empty=False):
    if not isinstance(v,list): raise Blocked(f"{label} must be string array")
    if not v and not allow_empty: raise Blocked(f"{label} must be non-empty string array")
    if any(not isinstance(x,str) or not x.strip() for x in v): raise Blocked(f"{label} must contain only non-empty strings")
    out=[x.strip() for x in v]
    if len(out)!=len(set(out)): raise Blocked(f"{label} contains duplicates")
    return set(out)

def coverage_axes():
    try:
        payload=json.loads(COVERAGE_AXES_PATH.read_text(encoding="utf-8-sig"))
    except Exception as exc:
        raise Blocked(f"workflow-v4 coverage axes contract is unreadable: {exc}") from exc
    if not isinstance(payload,dict) or payload.get("schema")!="workflow_v4_coverage_axes_v1":
        raise Blocked("workflow-v4 coverage axes contract has unexpected schema id")
    regions=strings(payload.get("regions"),"workflow-v4 coverage axes regions")
    topics=strings(payload.get("topics"),"workflow-v4 coverage axes topics")
    return regions,topics

def validate_preflight(run):
    a=load(repo_json(run["document_universe_manifest_ref"])); r=load(REGISTRY)
    expected_c=set(r.get("active_canonical",[]))|set(r.get("active_named_prompts",[]))
    expected_v=set(r.get("active_validator_contracts",[]))
    expected_m=set(r.get("open_remediations",[]))|set(r.get("activation_required_migrations",[]))
    if strings(a.get("active_canonical_paths"),"0.0D.active_canonical_paths")!=expected_c: raise Blocked("0.0D active_canonical_paths != current registry active set")
    if strings(a.get("active_validator_contract_paths"),"0.0D.active_validator_contract_paths")!=expected_v: raise Blocked("0.0D active_validator_contract_paths != current registry validator set")
    if strings(a.get("applicable_remediation_or_migration"),"0.0D.applicable_remediation_or_migration",allow_empty=True)!=expected_m: raise Blocked("0.0D applicable remediation/migration != current registry set")
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
    regions,topics=coverage_axes()
    a=load(repo_json(run["coverage_discovery_ref"])); axis_matrix(a.get("regional_coverage_matrix"),regions,"0.0C.regional_coverage_matrix"); axis_matrix(a.get("topic_coverage_matrix"),topics,"0.0C.topic_coverage_matrix")

def validate_completeness(run):
    a=load(repo_json(run["independent_completeness_ref"]))
    if a.get("stage")!="0.7C": raise Blocked("0.7C stage must be explicit")
    if a.get("status")!="PASS_WITH_DECLARED_RESIDUAL_RISK" or a.get("completeness_status")!=a.get("status"): raise Blocked("0.7C status/completeness_status must both be PASS_WITH_DECLARED_RESIDUAL_RISK")
    risks=a.get("residual_risks")
    if not isinstance(risks,list) or not risks or any(not isinstance(x,str) or not x.strip() for x in risks): raise Blocked("0.7C PASS_WITH_DECLARED_RESIDUAL_RISK requires non-empty residual_risks strings")
    for field in ("run_id","base_main_commit_sha","base_full_blob_sha"):
        if a.get(field)!=run.get(field): raise Blocked(f"0.7C {field} must match card run")
    if a.get("document_universe_manifest_ref")!=run.get("document_universe_manifest_ref"): raise Blocked("0.7C document_universe_manifest_ref must match card run")
    if a.get("coverage_discovery_ref")!=run.get("coverage_discovery_ref"): raise Blocked("0.7C coverage_discovery_ref must match card run")

def stage(payload,label):
    raw=payload.get("stage")
    if not isinstance(raw,str) or not raw.strip(): raise Blocked(f"{label}.stage required")
    s=ALIASES.get(raw.strip().lower())
    if not s: raise Blocked(f"{label}.stage={raw} is not an ordinary stage; 0.2R/0.3R cannot substitute")
    return s

def validate_stage_binding(payload,run,label):
    for field in ("run_id","base_main_commit_sha","base_full_blob_sha"):
        value=payload.get(field)
        if not isinstance(value,str) or not value.strip(): raise Blocked(f"{label}.{field} required")
        if value!=run.get(field): raise Blocked(f"{label}.{field} stale or mismatched")

def stage_rows(payload,s):
    rows=[]
    for bucket in BUCKETS[s]:
        v=payload.get(bucket)
        if isinstance(v,list): rows.extend(row for row in v if isinstance(row,dict))
        elif isinstance(v,dict): rows.append(v)
    return rows

def row_spec_id(row,s):
    x=row.get("spec_id") if s=="A" else row.get("source_spec_id")
    return x.strip() if isinstance(x,str) and x.strip() else None

def matching_rows(payload,s,expected): return [row for row in stage_rows(payload,s) if row_spec_id(row,s)==expected]
def spec_ids(payload,s): return {x for row in stage_rows(payload,s) if (x:=row_spec_id(row,s))}

def _git(args):
    proc=subprocess.run(["git","-C",str(ROOT),*args],text=True,capture_output=True)
    if proc.returncode!=0: raise Blocked(f"git {' '.join(args)} failed: {(proc.stderr or proc.stdout).strip()}")
    return proc.stdout

def baseline_canonical(run):
    sha=run.get("base_main_commit_sha"); blob=run.get("base_full_blob_sha")
    if not isinstance(sha,str) or len(sha)!=40 or not isinstance(blob,str) or len(blob)!=40: raise Blocked("declared baseline SHA/blob required")
    actual=_git(["rev-parse",f"{sha}:data/cards.full.json"]).strip()
    if actual!=blob: raise Blocked(f"declared baseline blob mismatch: {actual} != {blob}")
    try: data=json.loads(_git(["show",f"{sha}:data/cards.full.json"]))
    except Exception as exc: raise Blocked(f"declared baseline canonical JSON unreadable: {exc}") from exc
    if not isinstance(data,dict) or not isinstance(data.get("cards"),list): raise Blocked("declared baseline canonical cards array required")
    return data

def canonical_map_from_data(data):
    return {c["id"].strip():c["source_spec_id"].strip() for c in data.get("cards",[]) if isinstance(c,dict) and isinstance(c.get("id"),str) and c["id"].strip() and isinstance(c.get("source_spec_id"),str) and c["source_spec_id"].strip()}

def validate_no_identity_mutation(op,label):
    for i,change in enumerate(op.get("changes",[]) if isinstance(op,dict) else []):
        if not isinstance(change,dict): continue
        path=change.get("path")
        if isinstance(path,str) and (path==f"/{IDENTITY_ROOT}" or path.startswith(f"/{IDENTITY_ROOT}/")):
            raise Blocked(f"{label}.changes[{i}] cannot mutate {IDENTITY_ROOT}; operation.source_spec_id is binding metadata only")

def validate_insert_identities(insert_ops,known):
    baseline_specs=set(known.values()); seen=set()
    for i,op in enumerate(insert_ops):
        card=op.get("card") if isinstance(op,dict) else None
        spec=card.get("source_spec_id") if isinstance(card,dict) else None
        if not isinstance(spec,str) or not spec.strip(): raise Blocked(f"insert[{i}].card.source_spec_id required")
        spec=spec.strip()
        if spec in seen: raise Blocked(f"insert[{i}] reuses source_spec_id={spec} within the same run")
        if spec in baseline_specs: raise Blocked(f"insert[{i}] reuses baseline source_spec_id={spec}")
        seen.add(spec)

def op_spec(kind,op,known,inserted,label):
    if kind=="insert":
        x=(op.get("card") or {}).get("source_spec_id")
        if not isinstance(x,str) or not x.strip(): raise Blocked(f"{label}.card.source_spec_id required")
        return x.strip()
    if kind=="update":
        validate_no_identity_mutation(op,label)
        cid=op.get("id"); old=known.get(cid); declared=op.get("source_spec_id")
        if isinstance(declared,str): declared=declared.strip() or None
        else: declared=None
        if old and declared and old!=declared: raise Blocked(f"{label}.source_spec_id conflicts with declared-baseline identity")
        if old: return old
        if not declared: raise Blocked(f"{label}.source_spec_id required for legacy card without baseline source_spec_id")
        return declared
    sid,tid=op.get("source_id"),op.get("target_id"); ss=inserted.get(sid) or known.get(sid); ts=inserted.get(tid) or known.get(tid); declared=op.get("source_spec_id"); ident=op.get("identity_card_id")
    declared=declared.strip() if isinstance(declared,str) and declared.strip() else None
    if isinstance(ident,str) and ident.strip() not in {sid,tid}: raise Blocked(f"{label}.identity_card_id must equal source_id or target_id")
    if ss or ts:
        if declared and declared not in {x for x in (ss,ts) if x}: raise Blocked(f"{label}.source_spec_id does not match a governed endpoint")
        return declared or ss or ts
    if not declared or not isinstance(ident,str) or not ident.strip(): raise Blocked(f"{label} requires source_spec_id + identity_card_id when both legacy endpoints lack source_spec_id")
    return declared

def relation_type(obj):
    if not isinstance(obj,dict): return None
    for key in ("relation_type","final_relation_type","proposed_relation_type","proposed_type"):
        value=obj.get(key)
        if isinstance(value,str) and value.strip(): return value.strip()
    return None

def identifier_tokens(obj):
    tokens=set()
    if not isinstance(obj,dict): return tokens
    for key,value in obj.items():
        lower=str(key).lower()
        identity_key=(lower.endswith("_id") or lower.endswith("_ids") or "candidate" in lower or "target" in lower or lower in {"related","related_ids"})
        if identity_key:
            if isinstance(value,str) and value.strip(): tokens.add(value.strip())
            elif isinstance(value,list): tokens.update(x.strip() for x in value if isinstance(x,str) and x.strip())
        if isinstance(value,dict): tokens.update(identifier_tokens(value))
        elif isinstance(value,list):
            for row in value:
                if isinstance(row,dict): tokens.update(identifier_tokens(row))
    return tokens

def relation_reason(obj):
    if not isinstance(obj,dict): return None
    for key in ("reason","relation_reason","lineage_reason"):
        value=obj.get(key)
        if isinstance(value,str) and value.strip(): return value.strip()
    return None

def endpoint_context(op,known,inserted,expected,label):
    sid,tid=op.get("source_id"),op.get("target_id")
    if not isinstance(sid,str) or not isinstance(tid,str) or not sid or not tid: raise Blocked(f"{label} source_id/target_id required")
    ss=inserted.get(sid) or known.get(sid); ts=inserted.get(tid) or known.get(tid)
    ident=op.get("identity_card_id")
    if isinstance(ident,str) and ident.strip(): governed=ident.strip()
    else:
        matches=[cid for cid,spec in ((sid,ss),(tid,ts)) if spec==expected]
        if len(matches)!=1: raise Blocked(f"{label} cannot unambiguously bind source_spec_id={expected} to one Related endpoint; identity_card_id required")
        governed=matches[0]
    other=tid if governed==sid else sid
    other_spec=ts if governed==sid else ss
    target_tokens={other}
    if isinstance(other_spec,str) and other_spec: target_tokens.add(other_spec)
    return governed,target_tokens

def require_target_and_type(review,op,target_tokens,label,require_reason=False):
    if not isinstance(review,dict): raise Blocked(f"{label} relation review object required")
    if review.get("status") not in (None,"PASS"): raise Blocked(f"{label}.status must be PASS when present")
    actual_type=relation_type(review)
    if actual_type!=op.get("relation_type"): raise Blocked(f"{label} relation_type={actual_type} != operation {op.get('relation_type')}")
    if not (identifier_tokens(review)&target_tokens): raise Blocked(f"{label} does not identify the declared Related counterpart {sorted(target_tokens)}")
    if require_reason:
        reason=relation_reason(review)
        if reason!=op.get("lineage_reason"): raise Blocked(f"{label} lineage reason does not match operation.lineage_reason")
    direction=review.get("direction")
    if direction is not None and direction!=op.get("direction"): raise Blocked(f"{label}.direction does not match operation.direction")
    event_stage=review.get("event_stage_relationship")
    if event_stage is not None and event_stage!=op.get("event_stage_relationship"): raise Blocked(f"{label}.event_stage_relationship does not match operation")

def validate_related_semantics(op,expected,rows_by_stage,known,inserted,label):
    if op.get("relation_type") not in ALLOWED_RELATED_ADD_TYPES: raise Blocked(f"{label}.relation_type must be distinct_follow_up or program_lineage for related_add")
    _,target_tokens=endpoint_context(op,known,inserted,expected,label)

    arows=rows_by_stage.get("A",[])
    a_ok=False
    for row in arows:
        pre=row.get("related_prepass")
        if not isinstance(pre,dict) or pre.get("status")!="PASS": continue
        candidates=pre.get("relation_candidates")
        if not isinstance(candidates,list): continue
        for candidate in candidates:
            if isinstance(candidate,dict) and relation_type(candidate)==op.get("relation_type") and (identifier_tokens(candidate)&target_tokens): a_ok=True; break
        if a_ok: break
    if not a_ok: raise Blocked(f"{label} Stage A related_prepass does not review the declared counterpart/type")

    brows=rows_by_stage.get("B",[])
    if not any(isinstance(row.get("related_evidence_review"),dict) and _relation_review_matches(row["related_evidence_review"],op,target_tokens,False) for row in brows):
        raise Blocked(f"{label} Stage B related_evidence_review does not resolve the declared counterpart/type")

    for s in ("C","0.4","0.5","0.6","0.7"):
        rows=rows_by_stage.get(s,[])
        if not any(isinstance(row.get("related_lineage"),dict) and _relation_review_matches(row["related_lineage"],op,target_tokens,True) for row in rows):
            raise Blocked(f"{label} stage {s} related_lineage does not preserve the declared counterpart/type/reason")

def _relation_review_matches(review,op,target_tokens,require_reason):
    try:
        require_target_and_type(review,op,target_tokens,"relation review",require_reason=require_reason)
        return True
    except Blocked:
        return False

def validate_operations(run):
    base=baseline_canonical(run); known=canonical_map_from_data(base)
    insert_ops=run.get("operations",{}).get("insert",[])
    if not isinstance(insert_ops,list): raise Blocked("operations.insert must be array")
    validate_insert_identities(insert_ops,known)
    inserted={op.get("card",{}).get("id"):op.get("card",{}).get("source_spec_id") for op in insert_ops if isinstance(op,dict) and isinstance(op.get("card"),dict)}
    for kind in ("insert","update","related_add"):
        ops=run.get("operations",{}).get(kind)
        if not isinstance(ops,list): raise Blocked(f"operations.{kind} must be array")
        for i,op in enumerate(ops):
            if not isinstance(op,dict): raise Blocked(f"{kind}[{i}] must be object")
            label=f"{kind}[{i}]"; expected=op_spec(kind,op,known,inserted,label); matched=set(); rows_by_stage={}
            refs=op.get("stage_artifacts")
            if not isinstance(refs,list) or not refs: raise Blocked(f"{label}.stage_artifacts required")
            for j,ref in enumerate(refs):
                p=load(repo_json(ref)); artifact_label=f"{label}.stage_artifacts[{j}]"; s=stage(p,artifact_label)
                validate_stage_binding(p,run,artifact_label)
                rows=matching_rows(p,s,expected)
                if rows:
                    matched.add(s); rows_by_stage.setdefault(s,[]).extend(rows)
            missing=[s for s in STAGES if s not in matched]
            if missing: raise Blocked(f"{label} missing current-run candidate binding at stages {missing}")
            if kind=="related_add": validate_related_semantics(op,expected,rows_by_stage,known,inserted,label)

def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--run"); ap.add_argument("--self-test",action="store_true"); args=ap.parse_args()
    if args.self_test:
        try: stage({"stage":"0.2R"},"x")
        except Blocked: pass
        else: raise RuntimeError("revise stage substitution not blocked")
        try: stage({},"x")
        except Blocked: pass
        else: raise RuntimeError("missing declared stage not blocked")
        sample_run={"run_id":"r","base_main_commit_sha":"a"*40,"base_full_blob_sha":"b"*40}
        validate_stage_binding({"run_id":"r","base_main_commit_sha":"a"*40,"base_full_blob_sha":"b"*40},sample_run,"artifact")
        try: validate_stage_binding({"base_main_commit_sha":"a"*40,"base_full_blob_sha":"b"*40},sample_run,"artifact")
        except Blocked: pass
        else: raise RuntimeError("missing stage run_id binding not blocked")
        regions,_=coverage_axes(); axis_matrix({k:{"status":"searched"} for k in regions},regions,"regions")
        if strings([],"empty remediation",allow_empty=True)!=set(): raise RuntimeError("empty remediation set not accepted")
        try: strings([],"coverage axes")
        except Blocked: pass
        else: raise RuntimeError("coverage-axis empty list unexpectedly accepted")
        known={"OLD":"SPEC_BASE"}
        validate_insert_identities([{"card":{"id":"NEW","source_spec_id":"SPEC_NEW"}}],known)
        for bad in ([{"card":{"id":"A","source_spec_id":"SPEC_NEW"}},{"card":{"id":"B","source_spec_id":"SPEC_NEW"}}],[{"card":{"id":"A","source_spec_id":"SPEC_BASE"}}]):
            try: validate_insert_identities(bad,known)
            except Blocked: pass
            else: raise RuntimeError("insert source identity reuse not blocked")
        try: validate_no_identity_mutation({"changes":[{"op":"replace","path":"/source_spec_id","value":"OTHER"}]},"update[0]")
        except Blocked: pass
        else: raise RuntimeError("source_spec_id mutation not blocked")
        op={"source_id":"NEW","target_id":"OLD","source_spec_id":"SPEC_NEW","identity_card_id":"NEW","relation_type":"distinct_follow_up","lineage_reason":"verified follow-up","event_stage_relationship":"successor","direction":"directional"}
        arow={"spec_id":"SPEC_NEW","related_prepass":{"status":"PASS","relation_candidates":[{"target_id":"OLD","proposed_relation_type":"distinct_follow_up"}]}}
        brow={"source_spec_id":"SPEC_NEW","related_evidence_review":{"status":"PASS","target_id":"OLD","final_relation_type":"distinct_follow_up"}}
        lineage={"status":"PASS","relation_type":"distinct_follow_up","related_ids":["OLD"],"reason":"verified follow-up","event_stage_relationship":"successor","direction":"directional"}
        downstream={s:[{"source_spec_id":"SPEC_NEW","related_lineage":dict(lineage)}] for s in ("C","0.4","0.5","0.6","0.7")}
        rows={"A":[arow],"B":[brow],**downstream}
        validate_related_semantics(op,"SPEC_NEW",rows,known,{"NEW":"SPEC_NEW"},"related_add[0]")
        bad_rows={**rows,"C":[{"source_spec_id":"SPEC_NEW","related_lineage":{**lineage,"related_ids":["OTHER"]}}]}
        try: validate_related_semantics(op,"SPEC_NEW",bad_rows,known,{"NEW":"SPEC_NEW"},"related_add[0]")
        except Blocked: pass
        else: raise RuntimeError("Related target mismatch not blocked")
        bad_status={**rows,"B":[{"source_spec_id":"SPEC_NEW","related_evidence_review":{"status":"PASS_WITH_NOTES","target_id":"OLD","final_relation_type":"distinct_follow_up"}}]}
        try: validate_related_semantics(op,"SPEC_NEW",bad_status,known,{"NEW":"SPEC_NEW"},"related_add[0]")
        except Blocked: pass
        else: raise RuntimeError("non-canonical Stage B Related review status not blocked")
        print("PASS: V4 binding hardening self-test; empty remediation allowed, baseline identities immutable, insert identities unique, Related semantics/status bound, and coverage contract override supported"); return 0
    if not args.run: raise Blocked("--run PATH required")
    run=load(repo_json(args.run)); validate_preflight(run); validate_coverage(run); validate_completeness(run); validate_operations(run); print(json.dumps({"status":"PASS","registry_binding":"PASS","coverage_axes":"PASS","completeness_residual_risk":"PASS","stage_baseline_binding":"PASS","identity_binding":"PASS","related_semantics":"PASS"})); return 0

if __name__=="__main__":
    try: raise SystemExit(main())
    except Blocked as e: print(f"FAIL [BLOCKED_V4_BINDING]: {e}",file=sys.stderr); raise SystemExit(1)
    except Exception as e: print(f"FAIL [BLOCKED_V4_BINDING_INTERNAL]: {e}",file=sys.stderr); raise SystemExit(1)
