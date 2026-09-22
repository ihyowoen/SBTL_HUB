#!/usr/bin/env python3
"""Build/test scoped candidates; never update PR/main or conceal known defects."""
from pathlib import Path
import hashlib, json, os, re, shutil, subprocess, sys, time, traceback

ROOT=Path.cwd()
STAGING=ROOT/'docs/audits/pr385/phase3_build'
PROOF=Path(os.environ['RUNNER_TEMP'])/'pr385-phase3-proof'
BASE='d9e4d7c22fad275e8d2b058e6c69d8a4dcffe12a'
TEMP_WORKFLOW='.github/workflows/pr385-phase3-checkpoint.yml'
ALLOWED={
    'validation_scripts/content_enrichment_core.py',
    'validation_scripts/card_run_v4_binding_hardening.py',
    'validation_scripts/stage_artifact_contract_check.py',
    'validation_scripts/tests/test_content_enrichment_core.py',
    'docs/audits/pr385/PHASE3_IMPLEMENTATION.md',
}
PROOF.mkdir(parents=True,exist_ok=True)
RECEIPT={'schema':'pr385.phase3.checkpoint.v1','release_ready':False,
         'scope':'Shared-policy refactor and two mode-policy corrections, not full semantic remediation',
         'not_executed':['full-run CLI','production materializer','real KR/EN artifact replay'],
         'runs':{}}


def git(*args):
    return subprocess.check_output(['git',*args],cwd=ROOT,text=True).strip()

def execute(label,command,expected=0):
    start=time.monotonic()
    with (PROOF/(label+'.log')).open('w') as f:
        proc=subprocess.run(command,cwd=ROOT,stdout=f,stderr=subprocess.STDOUT,timeout=600)
    RECEIPT['runs'][label]={'returncode':proc.returncode,'seconds':round(time.monotonic()-start,3),'log':label+'.log'}
    print(label,proc.returncode,flush=True)
    if proc.returncode!=expected:
        print((PROOF/(label+'.log')).read_text()[-12000:],flush=True)
        raise RuntimeError(f'{label}: expected exit {expected}, got {proc.returncode}')


def suite(label,count):
    execute(label,[sys.executable,'validation_scripts/run_active_workflow_tests.py'])
    text=(PROOF/(label+'.log')).read_text()
    if f'Ran {count} tests' not in text or 'PASS_ACTIVE_WORKFLOW_TESTS_V4' not in text:
        raise RuntimeError(f'{label}: exact test count/success marker missing')
    RECEIPT['runs'][label]['test_count']=count


def reproduce(label):
    execute(label,[sys.executable,'docs/audits/pr385/reproduce.py','--repo',str(ROOT),
                   '--expect-head',git('rev-parse','HEAD'),'--output',str(PROOF/(label+'.json'))],expected=1)
    report=json.loads((PROOF/(label+'.json')).read_text())
    if report.get('setup_error') or report['summary']['runtime_errors'] or report['summary']['total']!=32:
        raise RuntimeError('Characterization setup/count failure')
    return report


def commit(message):
    subprocess.run(['git','add','-A'],check=True,cwd=ROOT)
    subprocess.run(['git','-c','user.name=github-actions[bot]',
                    '-c','user.email=41898282+github-actions[bot]@users.noreply.github.com',
                    'commit','-m',message],check=True,cwd=ROOT)
    return git('rev-parse','HEAD')


def main():
    start=git('rev-parse','HEAD');RECEIPT['preparation_head']=start
    if start!=os.environ['EXPECTED_HEAD'] or git('rev-parse','HEAD^')!=BASE:
        raise RuntimeError('Preparation parent/head changed; refusing stale migration')
    migration=(STAGING/'apply_phase3.py').read_text()
    core=(STAGING/'content_enrichment_core.py').read_bytes()
    tests=(STAGING/'test_content_enrichment_core.py').read_bytes()
    document=(STAGING/'PHASE3_IMPLEMENTATION.md').read_bytes()
    migration_path=PROOF/'apply_phase3.py';migration_path.write_text(migration)
    original=reproduce('baseline-characterization')
    if original['summary']['violations']!=19:
        raise RuntimeError('Historical diagnostic shape changed')
    (ROOT/'validation_scripts/content_enrichment_core.py').write_bytes(core)
    execute('apply-refactor',[sys.executable,str(migration_path),'a',str(ROOT)])
    a=commit('refactor(0.6): share evidence snapshots and density/grounding policy core')
    RECEIPT['refactor_head']=a
    suite('refactor-active-tests',924)
    execute('refactor-self-test',[sys.executable,'validation_scripts/card_run_v4_binding_hardening.py','--self-test'])
    after_a=reproduce('refactor-characterization')
    observations=lambda report:{r['id']:r['observed'] for r in report['results']}
    if observations(original)!=observations(after_a):
        raise RuntimeError('Behavior-preserving refactor changed a probe decision')
    RECEIPT['refactor_probe_decision_changes']=0
    execute('apply-policy-fix',[sys.executable,str(migration_path),'b',str(ROOT)])
    (ROOT/'validation_scripts/tests/test_content_enrichment_core.py').write_bytes(tests)
    (ROOT/'docs/audits/pr385/PHASE3_IMPLEMENTATION.md').write_bytes(document)
    shutil.rmtree(STAGING)
    (ROOT/TEMP_WORKFLOW).unlink()
    b=commit('fix(0.6): restrict realized-state minimum to no-change and align standalone policy')
    RECEIPT['candidate_head']=b
    changed=set(git('diff','--name-only',BASE,b).splitlines())
    if changed!=ALLOWED:
        raise RuntimeError(f'Unexpected final change scope: {sorted(changed)}')
    execute('compile',[sys.executable,'-m','compileall','-q','validation_scripts'])
    suite('candidate-active-tests',946)
    execute('candidate-self-test',[sys.executable,'validation_scripts/card_run_v4_binding_hardening.py','--self-test'])
    execute('candidate-architecture',[sys.executable,'validation_scripts/workflow_v4_architecture_check.py'])
    after_b=reproduce('candidate-characterization')
    before,after=observations(original),observations(after_b)
    delta={key:{'before':before[key],'after':after[key]} for key in before if before[key]!=after[key]}
    expected={'R13_tentative_standalone':{'before':'ACCEPTED','after':'BLOCKED'},
              'P04_tentative_changed':{'before':'BLOCKED','after':'ACCEPTED'}}
    if delta!=expected or after_b['summary']['violations']!=17:
        raise RuntimeError(f'Unexpected policy decision changes: {delta}')
    RECEIPT['intentional_decision_changes']=delta
    RECEIPT['remaining_characterization']=after_b['summary']
    RECEIPT['candidate_tree']=git('rev-parse',b+'^{tree}')
    RECEIPT['files']={}
    for name in sorted(ALLOWED):
        path=ROOT/name;blob=git('hash-object',str(path))
        if blob!=git('rev-parse',b+':'+name): raise RuntimeError('Working source differs from tested commit')
        RECEIPT['files'][name]={'git_blob':blob,'sha256':hashlib.sha256(path.read_bytes()).hexdigest()}
        destination=PROOF/'candidate-files'/name;destination.parent.mkdir(parents=True,exist_ok=True)
        shutil.copyfile(path,destination)
    if git('status','--porcelain'): raise RuntimeError('Test mutated tracked/unignored working tree')
    run=os.environ['GITHUB_RUN_ID']
    if not re.fullmatch(r'[0-9]+',run): raise RuntimeError('Invalid run ID')
    branch='audit/pr385-phase3-proof-'+run
    # A fresh proof ref only. PR/main promotion is deliberately not done here.
    if git('ls-remote','--heads','origin','refs/heads/'+branch): raise RuntimeError('Proof branch already exists')
    subprocess.run(['git','push','origin',b+':refs/heads/'+branch],cwd=ROOT,check=True)
    RECEIPT['proof_branch']=branch;RECEIPT['checkpoint_verified']=True


if __name__=='__main__':
    code=0
    try: main()
    except Exception as exc:
        code=1; RECEIPT['error']={'type':type(exc).__name__,'message':str(exc),'traceback':traceback.format_exc()}
        traceback.print_exc()
    finally:
        (PROOF/'receipt.json').write_text(json.dumps(RECEIPT,ensure_ascii=False,indent=2)+'\n')
    raise SystemExit(code)
