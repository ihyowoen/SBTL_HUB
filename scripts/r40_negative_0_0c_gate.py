#!/usr/bin/env python3
"""R40 isolated, fail-closed native 0.0C *negative* acceptance test.

This probes the actual tracked V4 validator with an intentionally BLOCKED,
aggregate-only stage artifact. It does not assert that the complete confidential
1,319-item ledger was submitted, and cannot certify 0.0C or Stage A.
"""
import hashlib
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / 'runs/2026-10-24/r40-native-negative-evidence'
R37 = ROOT / 'runs/2026-10-24/r37-native-0-0d-evidence/R37_0_0D_V4_STAGE_20261024.json'
MAIN = '805c2718d6daf40a219ae94242d9687e33ac3e88'
FULL = '07a91714e56be2a8bfad10ab63822f0c5cb3f06e'
LEAN = '8ebad37e98639ad97a30e52063d7325da77be650'
R39_OVERLAY_SHA = '1bce50ee1406168340a8f26af971fd50c2c228cae545d109f50c4777996e6d39'
R39_STAGE_SHA = '95f00294870dd4de78b937635137d00b9a539f80226e3c4b91606a361886b296'
AXES = ROOT / 'schemas/workflow-v4-coverage-axes.json'

def git(*argv):
    p = subprocess.run(['git',*argv],cwd=ROOT, text=True, capture_output=True, timeout=30)
    if p.returncode: raise RuntimeError(f"git {' '.join(argv)} => {p.stderr.strip()[:400]}")
    return p.stdout.strip()

def write(name, value):
    dst=OUT/name
    dst.write_text(json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2)+'\n',encoding='utf-8')
    return dst

def main():
    OUT.mkdir(parents=True,exist_ok=True)
    base = git('rev-parse','refs/remotes/origin/main')
    actual_full=git('rev-parse',f'{MAIN}:data/cards.full.json')
    actual_lean=git('rev-parse',f'{MAIN}:public/data/cards.json')
    assert (base,actual_full,actual_lean)==(MAIN,FULL,LEAN), 'main or canonical baseline changed; fail closed'
    stage0d=json.loads(R37.read_text(encoding='utf-8'))
    assert stage0d['stage']=='0.0D' and stage0d['status']=='PASS'
    assert stage0d['repository_head_sha']==MAIN and stage0d['canonical_full_blob_sha']==FULL
    assert (stage0d['docs_inventory_count'],stage0d['active_full_read_count'])==(96,43)
    axes=json.loads(AXES.read_text(encoding='utf-8'))
    assert len(axes['regions'])==6 and len(axes['topics'])==14
    # Intentionally blocked and no fake article dispositions or claimed search completeness.
    blocked_reason='R39 previous universe 1313 original + 6 discovery = 1319; 0 governed terminal dispositions; time-scoped discovery and contrary-source/related checks incomplete'
    docref=R37.relative_to(ROOT).as_posix()
    c={
      'stage':'0.0C','status':'BLOCKED_COVERAGE_DISCOVERY_INCOMPLETE',
      'document_universe_manifest_ref':docref,'base_full_blob_sha':FULL,
      'original_input_accounted':False,'stage_a_authorized':False,
      'original_input_observation_count':1313,
      'retained_prior_discovery_observations_count':6,
      'expanded_source_candidate_count':1319,
      'governed_terminal_dispositions':0,
      'source_boundary':'R39 original source review not a count of independent economic events',
      'confidential_original_ledger_included':False,
      'regional_coverage_matrix':{x:{'status':'blocked','reason':blocked_reason} for x in axes['regions']},
      'topic_coverage_matrix':{x:{'status':'blocked','reason':blocked_reason} for x in axes['topics']},
      'separate_editorial_12':{'all_complete':False,'status':'BLOCKED'},
      'independent_weekly_26':{'formally_complete_count':0,'status':'BLOCKED'},
      'prior_source_proofs':{'R39_original_overlay_sha256':R39_OVERLAY_SHA, 'R39_stage_sha256':R39_STAGE_SHA},
    }
    cp=write('R40_0_0C_BLOCKED_AGGREGATE_PROBE.json',c)
    run={
       'schema':'card_run_v1','run_id':'R40_NATIVE_REJECTION_PROBE_ONLY',
       'base_main_commit_sha':MAIN,'base_full_blob_sha':FULL,'expected_before':1676,
       'output_updated':datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'),
       'operations':{'insert':[],'update':[],'related_add':[]},
       'expected_after':1676,'audit_refs':{},
       'document_universe_manifest_ref':docref,
       'coverage_discovery_ref':cp.relative_to(ROOT).as_posix(),
       'independent_completeness_ref':'runs/2026-10-24/r40-native-negative-evidence/NOT_PRODUCED_0_7C.json'
    }
    rp=write('R40_ZERO_OPERATION_CARD_RUN_REJECTION_PROBE.json',run)
    cmd=['node','scripts/validate_card_run_v4_hardening.mjs','--run',rp.relative_to(ROOT).as_posix()]
    p=subprocess.run(cmd,cwd=ROOT, capture_output=True,text=True,timeout=120)
    expected='BLOCKED_COVERAGE_ENVELOPE'
    gate_ok = p.returncode==1 and expected in (p.stderr+p.stdout)
    receipt={
        'schema':'R40_NATIVE_V4_0_0C_NEGATIVE_ACCEPTANCE_V1',
        'checked_at_utc':datetime.now(timezone.utc).isoformat(),
        'locked_main_sha':MAIN,'locked_full_blob_sha':FULL,'locked_lean_blob_sha':LEAN,
        'r37_native_0_0d_status':stage0d['status'],
        'r40_native_0_0c_status':'BLOCKED_COVERAGE_DISCOVERY_INCOMPLETE',
        'native_command':cmd,'native_validator_exit_code':p.returncode,
        'expected_code':expected,'expected_negative_gate_passed':gate_ok,
        'native_stdout_tail':p.stdout[-1400:], 'native_stderr_tail':p.stderr[-1600:],
        'reported_stage_a_authorized':False,
        'user_approval_to_merge':False,
        'card_operations':0,'main_or_canonical_mutated':False,
        'privacy':'R39 detailed source-capture ledger not pushed to GitHub; only aggregate gate probe',
        'scope_limit':'0.0C native fail-closed acceptance negative test; NOT an R39 full-ledger run nor Stage A PASS',
    }
    write('R40_NATIVE_NEGATIVE_GATE_RECEIPT.json',receipt)
    manifest={n.name:hashlib.sha256(n.read_bytes()).hexdigest() for n in sorted(OUT.iterdir()) if n.is_file()}
    write('R40_SHA256_MANIFEST.json',manifest)
    print(json.dumps({'status':'PASS_NEGATIVE_GATE_ONLY' if gate_ok else 'FAIL_UNEXPECTED_GATE_RESULT',
                      'native_exit':p.returncode,'stderr':p.stderr[-300:],
                      'baseline_locked':True,'r37_stage0d':'PASS','r40_stage0c':'BLOCKED',
                      'stage_a_authorized':False},indent=2))
    if not gate_ok: raise RuntimeError('Native JS gate did not reject the blocked 0.0C artifact with the expected code')

if __name__=='__main__': main()
