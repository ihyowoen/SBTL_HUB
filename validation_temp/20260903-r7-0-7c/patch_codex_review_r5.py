#!/usr/bin/env python3
import copy, hashlib, json
from pathlib import Path

ROOT=Path('runs/2026-09-06/r7-20260903-production-r1')
RUN=ROOT/'card-run.json'
C07=ROOT/'stage-0-7c.json'
OLD_SHA='203f788ac48796fe9e790a70a30afa7bfcc8dd7143e56011548f00150d2e80a7'
NEW_SHA='a1957c8cac140083029bbcff41e96980c740a03ab8d47bfefae55a8e91fc240c'
OCI_SID='STD26_R7_009'
KR_SID='STD26_R7_011'
WAG_SID='STD26_R7_043'
WAG_TARGET='2026-07-14_GL_02'
WAG_SOURCE='2026-08-31_GL_04'
OCI_GENERIC='https://www.oci-holdings.co.kr/en/media/newsroom'
OCI_ITEM='https://www.koreatimes.co.kr/amp/business/companies/20260903/oci-holdings-breaks-ground-on-texas-solar-project-amid-ai-power-boom'
OCI_DATE_QUOTE='broke ground Tuesday (local time) on the 260-megawatt SunRoper solar project'
KR_DATE_QUOTE="9월 4일자로 '송·배전용 전기설비 이용규정'을 개정하여"
WAG_REASON=('The Aug. 31 U.S. Department of War $174 million equity-financing milestone is a distinct follow-up '
            'to the July 14 canonical Wagerup gallium FID, adding follow-on project financing for the same '
            '100-ton-per-year facility rather than a separate project.')
WAG_STAGE_REL='fid_to_follow_on_equity_financing'
WAG_FRESH=('On 2026-08-31 the U.S. Department of War announced an estimated $174 million equity financing investment '
           'for the same Wagerup 100-ton-per-year gallium facility whose FID was announced on 2026-07-14.')
WAG_INCREMENT=('Relative to canonical predecessor 2026-07-14_GL_02, the current event adds an estimated $174 million '
               'U.S. Department of War equity financing commitment for the same Wagerup 100-ton-per-year gallium project after FID.')
WAG_CHANGED=('The Wagerup gallium lineage advances from the 2026-07-14 FID to a follow-on U.S. equity-financing commitment, '
             'strengthening project execution and funding visibility without treating the financing disclosure as a separate project.')
STAGE_REFS=[
 'runs/2026-09-06/r7-20260903-production-r1/stages/stage-a.json',
 'runs/2026-09-06/r7-20260903-production-r1/stages/stage-b.json',
 'runs/2026-09-06/r7-20260903-production-r1/stages/stage-c.json',
 'runs/2026-09-06/r7-20260903-production-r1/stages/stage-0-4.json',
 'runs/2026-09-06/r7-20260903-production-r1/stages/stage-0-5.json',
 'runs/2026-09-06/r7-20260903-production-r1/stages/stage-0-6.json',
 'runs/2026-09-06/r7-20260903-production-r1/stages/stage-0-7.json',
]

def load(path): return json.loads(Path(path).read_text(encoding='utf-8-sig'))
def dump(path,obj): Path(path).write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def stable(v):
    if isinstance(v,list): return [stable(x) for x in v]
    if isinstance(v,dict): return {k:stable(v[k]) for k in sorted(v)}
    return v
def digest(ops):
    return hashlib.sha256(json.dumps(stable(ops),ensure_ascii=False,separators=(',',':')).encode('utf-8')).hexdigest()

def patch_oci_kr_card(card):
    sid=card.get('source_spec_id') or card.get('spec_id')
    if sid==OCI_SID:
        urls=card.get('urls')
        if isinstance(urls,list): card['urls']=[OCI_ITEM]+[u for u in urls if u!=OCI_ITEM]
        fs=card.get('fact_sources')
        if isinstance(fs,list) and not any(isinstance(x,dict) and x.get('url')==OCI_ITEM for x in fs):
            fs.append({
                'id':'STD26_R7_009-S2','owner':'The Korea Times','role':'independent_confirmation','url':OCI_ITEM,
                'published':'2026-09-03',
                'summary':'Item-specific independent report verifies the Sep. 1 SunRoper groundbreaking, 260MW scale, Wharton County location and 2027 operation target.',
                'fetch_status':'fetched_body_or_authoritative_page','headline_only':False,'rss_or_snippet_only':False,
                'claim_use':'paraphrase_only_no_source_quote','domain':'www.koreatimes.co.kr','source_url':OCI_ITEM,
                'source_id':'STD26_R7_009-S2','source_owner_id':'The Korea Times','source_owner_id_normalized':'The Korea Times',
                'source_role':'independent_confirmation','source_type':'independent body-level article','evidence_role':'secondary_event_evidence',
                'supports':['title','sub','gate','fact','implication'],'checked_at':'2026-09-07','fetched':True,
                'source_quote':OCI_DATE_QUOTE,'source_quote_status':'independent_material_quote_verified',
            })
        dr=card.get('date_role')
        if isinstance(dr,dict):
            dr['event_date_source_url']=OCI_ITEM
            dr['event_date_source_quote']=OCI_DATE_QUOTE
        sdl=card.get('source_discovery_ledger')
        if isinstance(sdl,list) and not any(isinstance(x,dict) and x.get('query_or_target')==OCI_ITEM for x in sdl):
            sdl.append({'source_spec_id':OCI_SID,'source_event_id':'E0067','query_or_target':OCI_ITEM,
                        'owner':'The Korea Times','result':'body_or_document_verified','checked_at':'2026-09-07'})
        if 'source_diversity_status' in card:
            card['source_diversity_status']='PASS_MULTI_SOURCE'
            card['source_diversity_measure']={'unique_urls':2,'unique_domains':2,'independent_owner_count':2}
            card['source_diversity_roles']={'official_company_newsroom':1,'independent_confirmation':1}
            card['single_source_exception']={'allowed':False,'reason':'not applicable: independent item-specific corroboration added in R5'}
        if isinstance(card.get('source_synthesis_audit'),dict): card['source_synthesis_audit']['independent_confirmation_used']=True
        for cm in card.get('claim_map',[]) if isinstance(card.get('claim_map'),list) else []:
            ids=cm.get('supported_by_source_ids')
            if isinstance(ids,list) and 'STD26_R7_009-S1' in ids and 'STD26_R7_009-S2' not in ids: ids.append('STD26_R7_009-S2')
    elif sid==KR_SID:
        fs=card.get('fact_sources')
        if isinstance(fs,list):
            for s in fs:
                if isinstance(s,dict) and s.get('id')=='STD26_R7_011-S1': s['source_quote']=KR_DATE_QUOTE
        dr=card.get('date_role')
        if isinstance(dr,dict): dr['event_date_source_quote']=KR_DATE_QUOTE

def patch_nested_oci_kr(obj):
    if isinstance(obj,dict):
        sid=obj.get('source_spec_id') or obj.get('spec_id')
        if sid in {OCI_SID,KR_SID} and any(k in obj for k in ('urls','fact_sources','date_role','source_discovery_ledger','claim_map')):
            patch_oci_kr_card(obj)
        for value in obj.values(): patch_nested_oci_kr(value)
    elif isinstance(obj,list):
        for value in obj: patch_nested_oci_kr(value)

for name in ('stage-a.json','stage-b.json'):
    path=ROOT/'stages'/name; obj=load(path)
    rows=[x for x in obj.get('strict_passed_spec',[]) if (x.get('spec_id') or x.get('source_spec_id'))==WAG_SID]
    assert len(rows)==1,(name,len(rows)); row=rows[0]
    row['baseline_relation']='distinct_follow_up'; row['baseline_match']=[WAG_TARGET]; row['baseline_follow_up_relation']='distinct_follow_up'
    row['baseline_expectation_changed']='Current baseline treatment for NR_20260903_E0410 now follows R5 review correction relation=distinct_follow_up to 2026-07-14_GL_02.'
    pre=row.setdefault('related_prepass',{})
    pre.update({'status':'PASS','same_event_checked':True,'matched_baseline_candidate_ids':[WAG_TARGET],
                'matched_current_batch_candidate_ids':[],'relation_candidates':[{
                    'target_candidate_id':WAG_TARGET,'proposed_relation_type':'distinct_follow_up','confidence':'high',
                    'reason':'R5 review confirms the Aug. 31 financing is a distinct follow-up to the same Wagerup gallium project FID.',
                    'anchor_class_to_verify':'execution_event_anchor',
                    'incremental_anchor_question':'Confirm the Aug. 31 U.S. equity financing is incremental to the July 14 Wagerup FID.'}],
                'duplicate_disposition':'no_duplicate_found','earliest_same_event_check_status':'PASS'})
    if name=='stage-b.json':
        brows=[x for x in obj.get('draft_cards',[]) if (x.get('source_spec_id') or x.get('spec_id'))==WAG_SID]
        assert len(brows)==1,len(brows)
        brows[0]['related_evidence_review']={
            'status':'PASS','same_event_check':'PASS','earliest_event_date_check':'PASS','relation_type':'distinct_follow_up',
            'matched_baseline_candidate_ids':[WAG_TARGET],'production_related_ids':[],
            'note':'R5 Codex review correction: same Wagerup project FID predecessor confirmed; production Related ID remains deferred to governed related_add.'}
        patch_nested_oci_kr(obj)
    dump(path,obj)

buckets={
 'stage-c.json':'accepted_fact_safe','stage-0-4.json':'addable_merge_safe',
 'stage-0-5.json':'evidence_complete_and_source_claim_covered','stage-0-6.json':'content_enriched_and_language_polished',
 'stage-0-7.json':'publish_ready',
}
for name,bucket in buckets.items():
    path=ROOT/'stages'/name; obj=load(path)
    rows=[x for x in obj.get(bucket,[]) if x.get('source_spec_id')==WAG_SID]
    assert len(rows)==1,(name,len(rows))
    targets=list(rows)
    if isinstance(obj.get('cards'),list): targets += [x for x in obj['cards'] if x.get('source_spec_id')==WAG_SID]
    for row in targets:
        rl=row.setdefault('related_lineage',{})
        rl.update({'status':'PASS','relation_type':'distinct_follow_up','related_ids':[WAG_TARGET],
                   'note':'R5 Codex review correction: direct Wagerup FID predecessor restored through governed lineage.',
                   'reason':WAG_REASON,'event_stage_relationship':WAG_STAGE_REL,'direction':'directional'})
        if name not in {'stage-c.json','stage-0-4.json'}:
            rl.update({'same_event_checked':True,'earliest_same_event_date_checked':True,'related_candidate_spec_ids':[],
                       'fresh_follow_up_anchor_class':'execution_event_anchor','fresh_follow_up_anchor':WAG_FRESH,
                       'incremental_fact_vs_predecessor':WAG_INCREMENT,'changed_judgment_vs_predecessor':WAG_CHANGED})
            row['related']=[WAG_TARGET]
    patch_nested_oci_kr(obj)
    dump(path,obj)

run=load(RUN)
assert digest(run['operations'])==OLD_SHA
insert_by_sid={op['card']['source_spec_id']:op for op in run['operations']['insert']}
assert {OCI_SID,KR_SID,WAG_SID} <= set(insert_by_sid)
patch_oci_kr_card(insert_by_sid[OCI_SID]['card'])
insert_by_sid[OCI_SID]['evidence_refs']=[OCI_ITEM,OCI_GENERIC]
patch_oci_kr_card(insert_by_sid[KR_SID]['card'])
wc=insert_by_sid[WAG_SID]['card']; wrl=wc['related_lineage']
assert wc['related']==[] and wrl['relation_type']=='new_unrelated_event' and wrl['related_ids']==[]
wrl.update({'fresh_follow_up_anchor_class':'execution_event_anchor','fresh_follow_up_anchor':WAG_FRESH,
            'incremental_fact_vs_predecessor':WAG_INCREMENT,'changed_judgment_vs_predecessor':WAG_CHANGED})
assert not any(x.get('source_spec_id')==WAG_SID for x in run['operations']['related_add'])
run['operations']['related_add'].append({
    'source_id':WAG_SOURCE,'target_id':WAG_TARGET,'source_spec_id':WAG_SID,'identity_card_id':WAG_SOURCE,
    'relation_type':'distinct_follow_up','lineage_reason':WAG_REASON,'event_stage_relationship':WAG_STAGE_REL,'direction':'directional',
    'stage_artifacts':copy.deepcopy(STAGE_REFS),'evidence_refs':copy.deepcopy(insert_by_sid[WAG_SID]['evidence_refs']),
    'patches':[
        {'card_id':WAG_SOURCE,'op':'add','path':'/related/-','value':WAG_TARGET},
        {'card_id':WAG_SOURCE,'op':'add','path':'/related_lineage/related_ids/-','value':WAG_TARGET},
        {'card_id':WAG_SOURCE,'op':'replace','path':'/related_lineage/relation_type','value':'distinct_follow_up'},
        {'card_id':WAG_SOURCE,'op':'replace','path':'/related_lineage/reason','value':WAG_REASON},
        {'card_id':WAG_SOURCE,'op':'add','path':'/related_lineage/event_stage_relationship','value':WAG_STAGE_REL},
        {'card_id':WAG_SOURCE,'op':'add','path':'/related_lineage/direction','value':'directional'},
    ],
})
assert {k:len(run['operations'][k]) for k in ('insert','update','related_add')}=={'insert':33,'update':0,'related_add':4}
assert digest(run['operations'])==NEW_SHA,(digest(run['operations']),NEW_SHA)
dump(RUN,run)

c=load(C07); assert c['reviewed_operations_sha256']==OLD_SHA and c['operation_freeze']['operations_sha256']==OLD_SHA
c['reviewed_operations_sha256']=NEW_SHA; c['operation_freeze']['operations_sha256']=NEW_SHA; c['operation_freeze']['related_add']=4
rd=c['six_round_review']['round_2_baseline_duplicate_reinforcement_followup']['relation_distribution']
assert rd.get('no_duplicate_found')==332 and rd.get('distinct_development_existing_lineage')==4
rd['no_duplicate_found']=331; rd['distinct_development_existing_lineage']=5
c['six_round_review']['round_2_baseline_duplicate_reinforcement_followup']['final_operations']['related_add']=4
c['six_round_review']['round_3_event_stage_lineage']['distinct_follow_up_cards']=3
c['six_round_review']['round_3_event_stage_lineage']['resolved_related_targets']=4
c['review_corrections_r5']={
 'status':'PASS','source':'Codex review issuecomment-5565195871','adjudication':[
   {'finding':'KR event date','disposition':'REJECTED_AFTER_OFFICIAL_SOURCE_RECHECK',
    'basis':'Official ministry body states the regulation was amended by action dated Sep. 4; Sep. 3 is the publication date.',
    'action':'Retain 2026-09-04 event date and strengthen date-bearing event_date_source_quote.'},
   {'finding':'Wagerup lineage','disposition':'ACCEPTED_FIXED',
    'basis':'2026-07-14_GL_02 is the same Wagerup 100 t/y gallium project FID predecessor.',
    'action':'Add governed distinct_follow_up related_add to 2026-07-14_GL_02.'},
   {'finding':'OCI newsroom index','disposition':'ACCEPTED_FIXED',
    'basis':'Generic official newsroom is not durable item-specific evidence.',
    'action':'Add item-specific Korea Times corroboration through urls, fact_sources, date-role source, discovery ledger and evidence_refs.'},
 ]}
dump(C07,c)
print('RESULT: PATCHED_CODEX_REVIEW_R5',{'operations_sha256':NEW_SHA,'insert':33,'update':0,'related_add':4})
