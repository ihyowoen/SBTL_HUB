#!/usr/bin/env python3
"""Build and verify one bounded candidate; never update main or the PR ref."""
from pathlib import Path
import base64
import gzip
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import time
import traceback

ROOT = Path(__file__).resolve().parents[4]
STAGE = ROOT / 'docs/audits/pr385/phase4a_stage'
WORKFLOW = '.github/workflows/pr385-phase4a-checkpoint.yml'
BASE = 'ee023a13eb141c594a4e595fbbc4bb1ec134e604'
PROOF = ROOT / '.pr385_phase4a_proof'
PROOF.mkdir(exist_ok=True)
receipt = {'schema':'pr385.phase4a.checkpoint.v1','checkpoint_verified':False,
           'release_ready':False,'runs':{},'base_head':BASE,
           'not_executed':['full-run production CLI','production materializer',
                           'real KR/EN artifact replay','final-main compatibility']}

def require(condition, message):
    if not condition:
        raise RuntimeError(message)

def git(*args):
    return subprocess.check_output(['git',*args],cwd=ROOT,text=True).strip()

def run(name, args, allowed=(0,)):
    start=time.monotonic()
    with (PROOF/(name+'.log')).open('w',encoding='utf-8') as log:
        proc=subprocess.run(args,cwd=ROOT,text=True,stdout=log,stderr=subprocess.STDOUT,timeout=360)
    receipt['runs'][name]={'returncode':proc.returncode,'seconds':round(time.monotonic()-start,3),'log':name+'.log'}
    require(proc.returncode in allowed, f'{name}: unexpected exit {proc.returncode}')
    return proc.returncode

try:
    require(os.environ.get('GITHUB_REPOSITORY')=='ihyowoen/SBTL_HUB','wrong repository')
    run_id=os.environ.get('GITHUB_RUN_ID','')
    require(bool(re.fullmatch(r'[0-9]+',run_id)),'invalid run identity')
    head=git('rev-parse','HEAD')
    require(head==os.environ.get('REQUESTED_HEAD'),'checkout is not requested exact head')
    require(git('rev-parse','HEAD^')==BASE,'unexpected preparation parent')
    receipt['preparation_head']=head
    expected=json.loads((STAGE/'expected.json').read_text())
    for path,sha in expected['before'].items():
        require(git('hash-object',path)==sha,f'input blob drift: {path}')
    for path in set(expected['after'])-set(expected['before']):
        require(not (ROOT/path).exists(),f'new candidate path already exists: {path}')
    parts=expected['transport_parts']
    require(len(parts)==12, 'unexpected transport part count')
    encoded=[]
    for part in parts:
        name=part['path']
        require(bool(re.fullmatch(r'part[0-9]{2,3}\.b64',name)), 'invalid transport path')
        data=(STAGE/name).read_bytes()
        require(len(data)==part['size'],'transport part length mismatch')
        blob=hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()
        require(blob==part['git_blob'], 'transport part checksum mismatch: '+name)
        encoded.append(data)
    patch=gzip.decompress(base64.b64decode(b''.join(encoded),validate=True))
    require(hashlib.sha256(patch).hexdigest()==expected['patch_sha256'],'patch checksum mismatch')
    patch_path=PROOF/'candidate.patch'
    patch_path.write_bytes(patch)
    (PROOF/'expected.json').write_text(json.dumps(expected,indent=2)+'\n')
    run('baseline-characterization',[sys.executable,'docs/audits/pr385/reproduce.py',
         '--repo',str(ROOT),'--expect-head',head,'--output',str(PROOF/'baseline-characterization.json')],(1,))
    baseline=json.loads((PROOF/'baseline-characterization.json').read_text())
    require(baseline['summary']['total']==32 and baseline['summary']['violations']==17
            and baseline['summary']['runtime_errors']==0,'baseline characterization drift')
    run('apply-check',['git','apply','--check',str(patch_path)])
    run('apply-candidate',['git','apply',str(patch_path)])
    for path,sha in expected['after'].items():
        require(git('hash-object',path)==sha,f'candidate bytes differ from tested local file: {path}')
    # Remove this transport harness from the candidate tree; keep it in history.
    git('rm','-r','--','docs/audits/pr385/phase4a_stage',WORKFLOW)
    git('add','--',*expected['after'].keys())
    git('config','user.name','github-actions[bot]')
    git('config','user.email','41898282+github-actions[bot]@users.noreply.github.com')
    git('commit','-m','fix(0.6): preserve numeric polarity and Korean scale; classify non-realized state scope')
    candidate=git('rev-parse','HEAD')
    receipt['candidate_head']=candidate
    receipt['candidate_tree']=git('rev-parse','HEAD^{tree}')
    changed=set(git('diff','--name-only',BASE,'HEAD').splitlines())
    require(changed==set(expected['after']),'candidate changes outside bounded file set')
    run('compile',[sys.executable,'-m','compileall','-q','validation_scripts'])
    run('active-tests',[sys.executable,'validation_scripts/run_active_workflow_tests.py'])
    tests_log=(PROOF/'active-tests.log').read_text()
    totals=re.findall(r'Ran (\d+) tests?',tests_log)
    require(totals and int(totals[-1])==984,'unexpected active test count')
    receipt['active_test_count']=984
    run('self-test',[sys.executable,'validation_scripts/card_run_v4_binding_hardening.py','--self-test'])
    run('architecture',[sys.executable,'validation_scripts/workflow_v4_architecture_check.py'])
    run('candidate-characterization',[sys.executable,'docs/audits/pr385/reproduce.py',
         '--repo',str(ROOT),'--expect-head',candidate,'--output',str(PROOF/'candidate-characterization.json')],(1,))
    result=json.loads((PROOF/'candidate-characterization.json').read_text())
    require(result['summary']['total']==32 and result['summary']['violations']==9
            and result['summary']['runtime_errors']==0,'candidate characterization mismatch')
    before={row['id']:row for row in baseline['results']}
    after={row['id']:row for row in result['results']}
    expected_changes={'A01','A02','A03','A04','R01_unicode_sign','R02_korean_scale',
                      'R03_korean_negated_zero','R04_conditional_zero'}
    require(set(before)==set(after),'probe universe changed')
    observed_changes={key for key in before if before[key]['observed']!=after[key]['observed']}
    require(observed_changes==expected_changes,'unexpected decision changes')
    require(all(after[key]['matches_expected'] for key in expected_changes),'target case still fails')
    require(not result['summary']['positive_control_blocks'],'positive control blocked')
    require(not git('diff','HEAD','--name-only'),'tests modified tracked candidate files')
    receipt['intentional_decision_changes']=sorted(observed_changes)
    receipt['remaining_characterization']=result['summary']
    receipt['files']={}
    for path,sha in expected['after'].items():
        require(git('hash-object',path)==sha,f'tested file mutated: {path}')
        require(git('rev-parse',f'HEAD:{path}')==sha,f'commit/file mismatch: {path}')
        receipt['files'][path]={'git_blob':sha,'sha256':hashlib.sha256((ROOT/path).read_bytes()).hexdigest()}
        target=PROOF/'candidate-files'/path
        target.parent.mkdir(parents=True,exist_ok=True)
        shutil.copyfile(ROOT/path,target)
    branch='audit/pr385-phase4a-proof-'+run_id
    require(not git('ls-remote','--heads','origin',branch),'proof branch already exists')
    run('publish-proof',['git','push','origin',f'HEAD:refs/heads/{branch}'])
    receipt['proof_branch']=branch
    receipt['checkpoint_verified']=True
except Exception as exc:
    receipt['error']={'type':type(exc).__name__,'message':str(exc),'traceback':traceback.format_exc()}
finally:
    (PROOF/'receipt.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(receipt,ensure_ascii=False,indent=2))
if not receipt['checkpoint_verified']:
    raise SystemExit(2)
