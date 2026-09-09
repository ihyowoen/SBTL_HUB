from pathlib import Path
import copy, datetime, json

BASE_SHA='d348296e65fe41423e6419058c58b1d7fedd89ee'
BASE_BLOB='83a996cd788e7195863318a348effa6310559583'
CID='2026-09-06_CN_02'
CLS='https://www.cls.cn/detail/2475109'
JIEMIAN='https://www.jiemian.com/article/15067758.html'
REUTERS='https://www.reuters.com/business/energy/china-pauses-approvals-battery-storage-manufacturing-projects-cailianshe-reports-2026-09-07/'
FACT='财联社는 9월 6일 복수 산업체인 관계자를 인용해 관련 당국이 기존·계획 중인 에너지저장 생산능력을 전면 점검하고, 저장용 전지셀을 중점 대상으로 삼아 아직 계획 단계이거나 착공하지 않은 신규 프로젝트의 승인·추진을 잠정 보류하고 있다고 보도했다. 이미 신고·등록되어 건설 중인 프로젝트는 영향받지 않으며, 전면 중단이 아니라 시장 수요에 따라 조정될 수 있다고 전했다. Reuters는 9월 7일 이를 재보도했고, 界面新闻은 9월 8일 복수 배터리 기업에 별도 확인해 관련 상황이 존재한다고 보도했다. 공식 부처 규정·공고의 발효일은 확인되지 않았다.'

p=Path('data/cards.full.json')
doc=json.loads(p.read_text(encoding='utf-8'))
before_doc=copy.deepcopy(doc)
cards=doc['cards']
card=next(c for c in cards if c['id']==CID)
before=copy.deepcopy(card)

# Keep durable Reuters anchor while adding the original report and independent confirmation.
for u in (CLS, JIEMIAN):
    if u not in card['urls']:
        card['urls'].append(u)

# Normalize Reuters as relay/context rather than independent same-event confirmation.
s1=next(s for s in card['fact_sources'] if s.get('id')=='STD26_0907_A_027-S1')
s1.update({
    'owner':'Reuters',
    'role':'international_wire_relay',
    'summary':'Reuters Sep 7 international relay of the Cailianshe report, preserving the distinction between planned/not-started projects and projects already under construction and noting the absence of a published final rule.',
    'source_owner_id':'Reuters',
    'source_owner_id_normalized':'Reuters',
    'source_role':'international_wire_relay',
    'source_type':'international wire reporting citing Cailianshe',
    'evidence_role':'policy_market_context',
    'checked_at':'2026-09-09',
    'source_quote':'Reuters relays Cailianshe’s report that planned or not-yet-started projects are paused while projects already under construction are unaffected.',
    'source_quote_status':'body_level_evidence_verified',
})

existing_ids={s.get('id') for s in card['fact_sources']}
if 'STD26_0907_A_027-S2' not in existing_ids:
    card['fact_sources'].append({
        'id':'STD26_0907_A_027-S2',
        'owner':'财联社',
        'role':'original_domestic_reporting',
        'url':CLS,
        'published':'2026-09-06',
        'summary':'Original Cailianshe report at 14:54 on Sep 6, based on multiple supply-chain sources, that authorities are surveying existing/planned storage capacity and temporarily pausing approval/progress of planned or not-yet-started projects while filed projects already under construction are unaffected; the tightening is not a blanket halt.',
        'fetch_status':'fetched_body_or_authoritative_page',
        'headline_only':False,
        'rss_or_snippet_only':False,
        'claim_use':'paraphrase_only_no_visible_quote',
        'domain':'cls.cn',
        'source_url':CLS,
        'source_id':'STD26_0907_A_027-S2',
        'source_owner_id':'Cailianshe',
        'source_owner_id_normalized':'Cailianshe',
        'source_role':'original_domestic_reporting',
        'source_type':'original domestic reporting primary_event_evidence',
        'evidence_role':'primary_event_evidence',
        'supports':['title','sub','gate','fact','implication'],
        'checked_at':'2026-09-09',
        'fetched':True,
        'source_quote':'Cailianshe reports that authorities are surveying existing and planned storage capacity; planned/not-started projects are temporarily paused, while filed projects already under construction are unaffected and the tightening is not a blanket halt.',
        'source_quote_status':'body_level_evidence_verified',
    })
if 'STD26_0907_A_027-S3' not in existing_ids:
    card['fact_sources'].append({
        'id':'STD26_0907_A_027-S3',
        'owner':'界面新闻',
        'role':'independent_event_confirmation',
        'url':JIEMIAN,
        'published':'2026-09-08',
        'summary':'Independent Jiemian reporting says multiple battery companies separately confirmed the situation; one battery executive said current controls primarily target battery capacity and approvals for added capacity had effectively stopped.',
        'fetch_status':'fetched_body_or_authoritative_page',
        'headline_only':False,
        'rss_or_snippet_only':False,
        'claim_use':'paraphrase_only_no_visible_quote',
        'domain':'jiemian.com',
        'source_url':JIEMIAN,
        'source_id':'STD26_0907_A_027-S3',
        'source_owner_id':'Jiemian News',
        'source_owner_id_normalized':'Jiemian News',
        'source_role':'independent_event_confirmation',
        'source_type':'independent original_reporting same_event_confirmation',
        'evidence_role':'independent_event_confirmation',
        'supports':['sub','fact','gate','implication'],
        'checked_at':'2026-09-09',
        'fetched':True,
        'source_quote':'Jiemian says multiple battery companies independently confirmed the situation and reports that new battery capacity is currently being restricted.',
        'source_quote_status':'body_level_evidence_verified',
    })

card['fact']=FACT
card['new_verified_fact']=FACT

# Date provenance now points to the original report while preserving later publication dates.
dr=card['date_role']
dr['source_publication_dates']=sorted(set(dr.get('source_publication_dates',[])+['2026-09-06','2026-09-07','2026-09-08']))
dr['publication_dates']=sorted(set(dr.get('publication_dates',[])+['2026-09-06','2026-09-07','2026-09-08']))
dr['event_date_source_url']=CLS
dr['event_date_source_quote']='Cailianshe original report was published at 14:54 on 2026-09-06 and describes the same temporary approval/progress pause for planned or not-yet-started projects.'

card['source_diversity_status']='PASS_MULTI_SOURCE'
card['source_diversity_measure']={'unique_urls':3,'unique_domains':3,'independent_owner_count':2}
card['source_diversity_roles']={
    'original_domestic_reporting':1,
    'international_wire_relay':1,
    'independent_event_confirmation':1,
}
card['source_synthesis_applied']=True
card['source_synthesis_fields']=sorted(set(card.get('source_synthesis_fields',[])+['fact']))
card['source_synthesis_audit']={
    'status':'PASS',
    'primary_or_official_controls_operative_facts':True,
    'independent_confirmation_used':True,
    'conflicts_explicitly_resolved':True,
}
card['single_source_exception']={
    'allowed':False,
    'reason':'Original Cailianshe reporting plus independent Jiemian same-event confirmation are now available; Reuters is retained as an international relay/context source rather than counted as independent confirmation.',
    'mitigation':'Evidence roles explicitly separate original event reporting, dependent international relay/context, and independent company-level confirmation.',
    'scope_limits':['paraphrase only','no claim that a formal ministry rule has been published'],
}
card['source_published_date']='2026-09-06'

# Claim map follows the corrected visible fact and all three source roles.
for claim in card.get('claim_map',[]):
    if claim.get('claim_id')=='STD26_0907_A_027-C1':
        claim['claim']=FACT
        claim['supported_by_source_ids']=['STD26_0907_A_027-S1','STD26_0907_A_027-S2','STD26_0907_A_027-S3']
        claim['status']='SUPPORTED'

# Event fingerprint remains same event but its durable source cluster and factual anchor now match the corrected evidence synthesis.
efp=card['event_fingerprint']
efp['source_url_cluster']=[REUTERS,CLS,JIEMIAN]
efp['factual_anchor']=FACT

# Discovery ledger: normalize Reuters dependency and add original + independent confirmation.
ledger=card.setdefault('source_discovery_ledger',[])
for row in ledger:
    if (row.get('canonical_url') or row.get('query_or_target'))==REUTERS:
        row.update({
            'name':'Reuters',
            'owner':'Reuters',
            'role':'international_wire_relay',
            'origin_type':'international wire reporting citing Cailianshe',
            'unique_contribution':'International relay/context of the Cailianshe report; preserves the not-started vs under-construction distinction and the lack of a published final rule.',
            'checked_at':'2026-09-09',
        })

def add_ledger(url,name,domain,owner,role,origin,contribution,fields):
    if any((r.get('canonical_url') or r.get('query_or_target'))==url for r in ledger):
        return
    ledger.append({
        'source_spec_id':'STD26_0907_A_027',
        'source_event_id':card.get('source_event_id'),
        'query_or_target':url,
        'canonical_url':url,
        'name':name,
        'domain':domain,
        'owner':owner,
        'role':role,
        'origin_type':origin,
        'outcome':'body_or_document_verified',
        'unique_contribution':contribution,
        'visible_fields_supported':fields,
        'checked_at':'2026-09-09',
    })
add_ledger(CLS,'财联社','cls.cn','Cailianshe','original_domestic_reporting','original domestic reporting primary_event_evidence','Original Sep 6 14:54 report establishes the representative event date and operative distinction between planned/not-started projects and filed projects already under construction.',['title','sub','gate','fact','implication'])
add_ledger(JIEMIAN,'界面新闻','jiemian.com','Jiemian News','independent_event_confirmation','independent original_reporting same_event_confirmation','Independent Sep 8 reporting separately confirms the situation with multiple battery companies and identifies current restrictions on additional battery capacity.',['sub','fact','gate','implication'])

card['alternative_source_search_audit']={
    'query':'中国 储能 新建产能 项目 审批 暂缓 财联社 独立确认',
    'channels':['bounded_web_search','source_owner_or_independent_check'],
    'candidate_results':[CLS,JIEMIAN],
    'conclusion':'Original Cailianshe report and independent Jiemian company-level confirmation found and incorporated; Reuters retained as relay/context. Single-source exception retired.',
    'checked_at':'2026-09-09',
    'bounded_search_complete':True,
    'search_result_accounting_complete':True,
}

# Keep publication state; direct correction is a bounded post-merge mutation, not a new formal-run state claim.
now=datetime.datetime.now(datetime.timezone.utc).replace(microsecond=0).isoformat().replace('+00:00','Z')
doc['updated']=now
doc['total']=len(cards)
p.write_text(json.dumps(doc,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

changed=sorted(k for k in set(before)|set(card) if before.get(k)!=card.get(k))
out=Path('direct-adds/2026-09-09-a027-source-correction')
out.mkdir(parents=True,exist_ok=True)
manifest={
  'schema':'manual_direct_add_v2',
  'status':'PASS',
  'direct_add_id':'A027_SOURCE_CORRECTION_20260909_R1',
  'review_mode':'already_reviewed_bounded_direct_add',
  'formal_full_run_claimed':False,
  'base_main_commit_sha':BASE_SHA,
  'base_full_blob_sha':BASE_BLOB,
  'expected_before':len(cards),
  'expected_after':len(cards),
  'output_updated':now,
  'operations':{'add':[],'update':[CID],'id_migration':[]},
  'editorial_attestation':{
    'policy_version':'EMBEDDED_NEWS_VALUE_SELECTION_V4',
    'additions':[],
    'updates':[{
      'id':CID,
      'change_type':'correction',
      'changed_fields':changed,
      'reason':'Post-merge source correction: replace Reuters-only/single-source framing with the Sep 6 original Cailianshe report, retain Reuters as dependent international relay/context, add independent Sep 8 Jiemian company-level confirmation, and source-lock the visible fact and event-date provenance without changing event identity.',
      'evidence_review_summary':'Cailianshe original report (Sep 6 14:54) establishes the event date and scope; Reuters (Sep 7) is a relay/context source citing Cailianshe; Jiemian (Sep 8) separately confirms the situation with multiple battery companies. No formal ministry rule text was found, so that uncertainty remains explicit.',
    }]
  }
}
(out/'direct-add.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'id':CID,'changed_fields':changed,'output_updated':now},ensure_ascii=False,indent=2))
