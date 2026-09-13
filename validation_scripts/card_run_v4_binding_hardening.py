#!/usr/bin/env python3
from __future__ import annotations
import argparse, hashlib, json, os, subprocess, sys
from collections import Counter
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
ALLOWED_STAGE_A_TERMINAL_DISPOSITIONS = {
    "legacy_keep",
    "strict_passed_spec",
    "candidate_review_pool",
    "watchlist_context_pool",
    "watchlist_or_support_context",
    "reject_or_support_only_pool",
    "rejected",
    "existing_reinforcement",
    "existing_reinforcement_or_same_event",
    "reinforcement",
    "support_source_only",
    "split_parent_decomposed",
}
STAGE_A_GOVERNED_POOLS = (
    "legacy_keep",
    "strict_passed_spec",
    "candidate_review_pool",
    "watchlist_context_pool",
    "reject_or_support_only_pool",
    "rejected",
    "existing_reinforcement",
    "support_source_only",
)
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
    if strings(a.get("applicable_remediation_or_migration"),"0.0D.applicable remediation/migration",allow_empty=True)!=expected_m: raise Blocked("0.0D applicable remediation/migration != current registry set")
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

def _nonempty_text(value):
    return isinstance(value,str) and bool(value.strip())

def _stage_a_story_ids(item,pool):
    if not isinstance(item,dict): return []
    out=[]
    if pool=="strict_passed_spec":
        values=item.get("source_story_ids")
        if isinstance(values,list): out.extend(x.strip() for x in values if _nonempty_text(x))
    else:
        if _nonempty_text(item.get("story_id")): out.append(item["story_id"].strip())
        grouped=item.get("grouped_story_ids")
        if isinstance(grouped,list): out.extend(x.strip() for x in grouped if _nonempty_text(x))
        source_ids=item.get("source_story_ids")
        if isinstance(source_ids,list): out.extend(x.strip() for x in source_ids if _nonempty_text(x))
    return list(dict.fromkeys(out))

def checker_validated_stage_a_decisions(source):
    review_pool=source.get("review_pool")
    if not isinstance(review_pool,list):
        raise Blocked("checker-validated Stage A review_pool must be an array")
    if review_pool:
        raise Blocked("checker-validated Stage A review_pool must be empty before terminal authority; use canonical review partitions")

    governed={}
    for pool in STAGE_A_GOVERNED_POOLS:
        values=source.get(pool)
        if not isinstance(values,list):
            raise Blocked(f"checker-validated Stage A output pool {pool} must be an array")
        for index,item in enumerate(values):
            if not isinstance(item,dict):
                raise Blocked(f"checker-validated Stage A {pool}[{index}] must be an object")
            spec_id=item.get("spec_id") if _nonempty_text(item.get("spec_id")) else None
            identities=_stage_a_story_ids(item,pool)
            if not identities:
                raise Blocked(f"checker-validated Stage A {pool}[{index}] has no governed story identity")
            for identity in identities:
                if identity in governed:
                    raise Blocked(f"checker-validated Stage A identity {identity} appears in multiple output dispositions")
                basis=f"stage_a_checker:{pool}:{spec_id or identity}"
                governed[identity]=(pool,basis)
    return governed

def governed_stage_a_decisions(run,ledger):
    ref=ledger.get("governed_stage_a_ledger_ref") or ledger.get("prior_partial_ledger_ref")
    if not _nonempty_text(ref):
        raise Blocked("Stage A terminal identity ledger must reference its governed Stage A decision ledger")
    source_path=repo_json(ref.strip())
    source=load(source_path)
    raw_stage=source.get("stage")
    if not _nonempty_text(raw_stage) or ALIASES.get(raw_stage.strip().lower())!="A" or source.get("run_id")!=run.get("run_id"):
        raise Blocked("governed Stage A decision ledger stage/run_id mismatch")
    authority=source.get("authority") if isinstance(source.get("authority"),dict) else source
    for field in ("base_main_commit_sha","base_full_blob_sha"):
        if authority.get(field)!=run.get(field):
            raise Blocked(f"governed Stage A decision ledger {field} mismatch")
    if ledger.get("status")!="PASS":
        raise Blocked("terminal decision binding requires a PASS terminal identity ledger")
    checker=ROOT / "validation_scripts/stage_lineage_contract_check.py"
    proc=subprocess.run(
        [sys.executable,str(checker),"stage_a",str(source_path)],
        text=True,capture_output=True,
    )
    if proc.returncode!=0:
        detail=(proc.stderr or proc.stdout or "Stage A checker failed").strip().replace("\n"," ")
        raise Blocked(
            "passing terminal ledger requires governed Stage A decision ledger to pass the full Stage A checker: "
            + detail[:600]
        )
    return checker_validated_stage_a_decisions(source)

def validate_terminal_decision_binding(entries,governed):
    if not isinstance(entries,list):
        raise Blocked("Stage A terminal identity ledger terminal_decisions must be an array")
    terminal_ids=[]; dispositions=[]
    for index,row in enumerate(entries):
        identity=row.get("identity") if isinstance(row,dict) else None
        disposition=row.get("disposition") if isinstance(row,dict) else None
        basis=row.get("basis") if isinstance(row,dict) else None
        if not _nonempty_text(identity): raise Blocked(f"Stage A terminal_decisions[{index}].identity required")
        if disposition not in ALLOWED_STAGE_A_TERMINAL_DISPOSITIONS: raise Blocked(f"Stage A terminal_decisions[{index}].disposition is not an allowed terminal disposition")
        if not _nonempty_text(basis): raise Blocked(f"Stage A terminal_decisions[{index}].basis required")
        if row.get("terminal") is not True: raise Blocked(f"Stage A terminal_decisions[{index}] must declare terminal=true")
        identity=identity.strip(); basis=basis.strip()
        expected=governed.get(identity)
        if expected is None: raise Blocked(f"Stage A terminal_decisions[{index}] identity={identity} has no governed Stage A decision")
        if expected!=(disposition,basis): raise Blocked(f"Stage A terminal_decisions[{index}] disposition/basis does not match checker-validated Stage A output")
        terminal_ids.append(identity); dispositions.append(disposition)
    if len(terminal_ids)!=len(set(terminal_ids)):
        raise Blocked("Stage A terminal identity ledger contains duplicate identities")
    return terminal_ids,dispositions

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

    ledger_ref=a.get("terminal_identity_ledger_ref")
    if not isinstance(ledger_ref,str) or not ledger_ref.strip():
        raise Blocked("0.7C terminal_identity_ledger_ref is required")
    ledger_path=repo_json(ledger_ref)
    recorded_sha=a.get("terminal_identity_ledger_sha256")
    actual_sha=hashlib.sha256(ledger_path.read_bytes()).hexdigest()
    if recorded_sha!=actual_sha:
        raise Blocked("0.7C terminal_identity_ledger_sha256 does not match referenced bytes")
    ledger=load(ledger_path)
    if ledger.get("status")!="PASS" or ledger.get("stage")!="A":
        raise Blocked("0.7C terminal identity ledger must be a passing Stage A ledger")
    if ledger.get("run_id")!=run.get("run_id"):
        raise Blocked("0.7C terminal identity ledger run_id mismatch")
    governed=governed_stage_a_decisions(run,ledger)

    coverage=load(repo_json(run["coverage_discovery_ref"]))
    coverage_rows=coverage.get("source_universe_expansion_ledger")
    if not isinstance(coverage_rows,list):
        raise Blocked("0.0C source_universe_expansion_ledger must be an array")
    coverage_ids=[]
    for index,row in enumerate(coverage_rows):
        candidate_id=row.get("candidate_id") if isinstance(row,dict) else None
        if not isinstance(candidate_id,str) or not candidate_id.strip():
            raise Blocked(f"0.0C source_universe_expansion_ledger[{index}].candidate_id required")
        coverage_ids.append(candidate_id.strip())
    if len(coverage_ids)!=len(set(coverage_ids)):
        raise Blocked("0.0C source_universe_expansion_ledger contains duplicate identities")

    entries=ledger.get("terminal_decisions")
    terminal_ids,dispositions=validate_terminal_decision_binding(entries,governed)
    if set(terminal_ids)!=set(coverage_ids):
        missing=sorted(set(coverage_ids)-set(terminal_ids))
        unknown=sorted(set(terminal_ids)-set(coverage_ids))
        raise Blocked(f"Stage A terminal identity ledger does not exactly reconcile 0.0C; missing={missing[:5]} unknown={unknown[:5]}")
    if set(governed)!=set(coverage_ids):
        missing=sorted(set(coverage_ids)-set(governed))
        unknown=sorted(set(governed)-set(coverage_ids))
        raise Blocked(f"checker-validated Stage A outputs do not exactly reconcile 0.0C; missing={missing[:5]} unknown={unknown[:5]}")

    universe=a.get("universe_accounting")
    if not isinstance(universe,dict): raise Blocked("0.7C universe_accounting must be an object")
    total=len(coverage_ids)
    if universe.get("terminal_identity_total")!=total or universe.get("terminal_identity_accounted")!=total: raise Blocked("0.7C terminal identity totals must equal the exact identity ledger cardinality")
    if universe.get("duplicate_identity_count")!=0 or universe.get("missing_identity_count")!=0: raise Blocked("0.7C duplicate/missing identity counts must both be zero")
    if ledger.get("terminal_identity_total")!=total or ledger.get("terminal_identity_accounted")!=total: raise Blocked("Stage A terminal identity ledger cardinality fields are inconsistent")
    if ledger.get("open_identity_count")!=0: raise Blocked("Stage A terminal identity ledger open_identity_count must be zero")

    actual_counts=dict(sorted(Counter(dispositions).items()))
    if ledger.get("disposition_counts")!=actual_counts: raise Blocked("Stage A terminal identity ledger disposition_counts do not match identity rows")
    revalidation=a.get("stage_a_revalidation")
    if not isinstance(revalidation,dict) or revalidation.get("disposition_counts")!=actual_counts: raise Blocked("0.7C stage_a_revalidation.disposition_counts must match the identity ledger")
    return governed

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

def governed_strict_spec_identities(governed):
    prefix="stage_a_checker:strict_passed_spec:"
    result={}
    for identity,(disposition,basis) in governed.items():
        if disposition!="strict_passed_spec": continue
        if not isinstance(basis,str) or not basis.startswith(prefix) or not basis[len(prefix):]: raise Blocked(f"checker-validated strict Stage A identity {identity} has malformed derived basis")
        result.setdefault(basis[len(prefix):],set()).add(identity)
    return result

def validate_governed_stage_a_operation(rows_by_stage,expected,strict_specs,label):
    governed_ids=strict_specs.get(expected)
    if not governed_ids: raise Blocked(f"{label} source_spec_id={expected} is not a checker-validated strict Stage A outcome")
    actual_ids=set()
    for row in rows_by_stage.get("A",[]): actual_ids.update(_stage_a_story_ids(row,"strict_passed_spec"))
    if actual_ids!=governed_ids: raise Blocked(f"{label} Stage A operation binding disagrees with terminal authority for {expected}; governed={sorted(governed_ids)} actual={sorted(actual_ids)}")

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
        if isinstance(path,str) and (path==f"/{IDENTITY_ROOT}" or path.startswith(f"/{IDENTITY_ROOT}/")): raise Blocked(f"{label}.changes[{i}] cannot mutate {IDENTITY_ROOT}; operation.source_spec_id is binding metadata only")

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
        declared=declared.strip() if isinstance(declared,str) and declared.strip() else None
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
    arows=rows_by_stage.get("A",[]); a_ok=False
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
    if not any(isinstance(row.get("related_evidence_review"),dict) and _relation_review_matches(row["related_evidence_review"],op,target_tokens,False) for row in brows): raise Blocked(f"{label} Stage B related_evidence_review does not resolve the declared counterpart/type")
    for s in ("C","0.4","0.5","0.6","0.7"):
        rows=rows_by_stage.get(s,[])
        if not any(isinstance(row.get("related_lineage"),dict) and _relation_review_matches(row["related_lineage"],op,target_tokens,True) for row in rows): raise Blocked(f"{label} stage {s} related_lineage does not preserve the declared counterpart/type/reason")

def _relation_review_matches(review,op,target_tokens,require_reason):
    try:
        require_target_and_type(review,op,target_tokens,"relation review",require_reason=require_reason)
        return True
    except Blocked: return False

def validate_source_diversity_chain(rows_by_stage,label):
    observed={}
    for s in ("B","C","0.5","0.6","0.7"):
        rows=rows_by_stage.get(s,[])
        if not rows: raise Blocked(f"{label} stage {s} requires a bound row with source_diversity_status")
        values=set()
        for index,row in enumerate(rows):
            value=row.get("source_diversity_status") if isinstance(row,dict) else None
            if not _nonempty_text(value): raise Blocked(f"{label} stage {s} row {index} requires non-empty source_diversity_status")
            values.add(value.strip())
        if len(values)!=1: raise Blocked(f"{label} stage {s} has contradictory source_diversity_status values {sorted(values)}")
        observed[s]=next(iter(values))
    statuses=set(observed.values())
    if len(statuses)>1:
        detail=", ".join(f"{stage}={status}" for stage,status in observed.items())
        raise Blocked(f"{label} source_diversity_status drifts across the bound stage chain: {detail}")

def validate_operations(run,governed):
    strict_specs=governed_strict_spec_identities(governed)
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
            validate_governed_stage_a_operation(rows_by_stage,expected,strict_specs,label)
            validate_source_diversity_chain(rows_by_stage,label)
            if kind=="related_add": validate_related_semantics(op,expected,rows_by_stage,known,inserted,label)

def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--run"); ap.add_argument("--self-test",action="store_true"); args=ap.parse_args()
    if args.self_test:
        source={"review_pool":[],"legacy_keep":[{"story_id":"C1","grouped_story_ids":["C1"]}],"strict_passed_spec":[],"candidate_review_pool":[],"watchlist_context_pool":[],"reject_or_support_only_pool":[],"rejected":[],"existing_reinforcement":[],"support_source_only":[]}
        if checker_validated_stage_a_decisions(source)!={"C1":("legacy_keep","stage_a_checker:legacy_keep:C1")}: raise RuntimeError("legacy_keep/dedup contract failed")
        strict={"CAND_1":("strict_passed_spec","stage_a_checker:strict_passed_spec:SPEC_NEW")}
        validate_governed_stage_a_operation({"A":[{"spec_id":"SPEC_NEW","source_story_ids":["CAND_1"]}]},"SPEC_NEW",governed_strict_spec_identities(strict),"insert[0]")
        print("PASS: V4 binding hardening self-test; checker-valid legacy_keep and duplicate-in-row identities are supported, unchecked Stage A status aliases are ignored, operations bind to terminal-governed strict outcomes, and existing fail-closed gates remain active"); return 0
    if not args.run: raise Blocked("--run PATH required")
    run=load(repo_json(args.run)); validate_preflight(run); validate_coverage(run); governed=validate_completeness(run); validate_operations(run,governed); print(json.dumps({"status":"PASS","registry_binding":"PASS","coverage_axes":"PASS","completeness_residual_risk":"PASS","stage_baseline_binding":"PASS","identity_binding":"PASS","terminal_decision_binding":"PASS","operation_stage_a_binding":"PASS","source_diversity_chain":"PASS","related_semantics":"PASS"})); return 0

if __name__=="__main__":
    try: raise SystemExit(main())
    except Blocked as e: print(f"FAIL [BLOCKED_V4_BINDING]: {e}",file=sys.stderr); raise SystemExit(1)
    except Exception as e: print(f"FAIL [BLOCKED_V4_BINDING_INTERNAL]: {e}",file=sys.stderr); raise SystemExit(1)
