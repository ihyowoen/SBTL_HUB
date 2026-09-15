#!/usr/bin/env python3
from __future__ import annotations

import copy, hashlib, importlib.util, json, sys
from collections import Counter
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
RUN=ROOT/'runs/2026-09-03'
INPUT=RUN/'prompt_0_1p_r6_candidates16_input_20260903_R1.json'
DECISIONS=RUN/'prompt_0_1p_r6_candidates16_research_decisions_20260903_R1.json'
TEMPLATE=RUN/'stage_a_formal_r6_batch01_20260903_R1.json'
FORMAL_PATH=ROOT/'scripts/formal_stage_a_r6_remaining.py'
OUT=RUN/'stage_a_prompt_0_1p_r6_promotion16_20260903_R1.json'
REPORT=RUN/'stage_a_prompt_0_1p_r6_promotion16_validation_20260903_R1.json'
MAIN='df6fcccf3a69464ff0a43a8ba5897d71b6a4d9c4'
BLOB='53219907cdb435c3822c41d097b23e475662aa8a'
CAND_SHA='3594d79cf12f04e68f3ba7e3d683690cdabc7a73d505e857851e46bc871e8bf6'
PROMOTED={'R6_B01_REVIEW_006','R6_B01_REVIEW_024'}

spec=importlib.util.spec_from_file_location('formal_stage_a_r6_remaining',FORMAL_PATH)
formal=importlib.util.module_from_spec(spec); spec.loader.exec_module(formal)

def sha_obj(x):
    return hashlib.sha256(json.dumps(x,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()).hexdigest()

def load_event(batch:int, ordinal:int):
    p=RUN/'stage_a_review_packets_395_r6'/f'batch_{batch:02d}.json'
    data=json.loads(p.read_text(encoding='utf-8'))
    return next(e for e in data['events'] if e['ordinal']==ordinal)

def main():
    locked=json.loads(INPUT.read_text(encoding='utf-8'))
    research=json.loads(DECISIONS.read_text(encoding='utf-8'))
    template=json.loads(TEMPLATE.read_text(encoding='utf-8'))
    assert locked['status']=='PASS_INPUT_LOCK' and locked['candidate_count']==16
    assert locked['candidate_set_sha256']==CAND_SHA
    assert locked['main_sha']==MAIN and locked['canonical_blob_sha']==BLOB
    assert sha_obj(locked['items'])==CAND_SHA
    assert research['candidate_set_sha256']==CAND_SHA
    dmap={d['id']:d for d in research['decisions']}
    assert len(dmap)==16 and set(dmap)==set(locked['candidate_ids'])
    assert {k for k,v in dmap.items() if v['disposition']=='PROMOTE_TO_STRICT'}==PROMOTED
    assert sum(v['disposition']=='RETAIN_CANDIDATE' for v in dmap.values())==14

    # Source artifacts are authoritative for original candidate rows and their ledgers.
    source_artifacts={}
    for b in sorted({int(x['_formal_batch']) for x in locked['items']}):
        p=RUN/f'stage_a_formal_r6_batch{b:02d}_20260903_R1.json'
        source_artifacts[b]=json.loads(p.read_text(encoding='utf-8'))
        assert source_artifacts[b]['status']=='PASS'

    strict=[]; retained=[]; ledger=[]; resolutions=[]; promo_ledger=[]
    all_source_ids=set()
    for original in locked['items']:
        rid=original['review_pool_item_id']; dec=dmap[rid]; b=int(original['_formal_batch'])
        ordinal=int(rid.rsplit('_',1)[1])
        event=load_event(b,ordinal)
        assert set(original['source_story_ids'])=={o['observation_key'] for o in event['observations']}
        src=source_artifacts[b]
        src_rows=[copy.deepcopy(x) for x in src['decision_ledger'] if x.get('review_pool_item_id')==rid]
        assert {x['story_id'] for x in src_rows}==set(original['source_story_ids'])
        assert not (all_source_ids & set(original['source_story_ids']))
        all_source_ids.update(original['source_story_ids'])

        if rid in PROMOTED:
            j=formal.decide(event)
            # Promotion resolves the recorded evidence/stage question; it does not manufacture a larger score.
            j['pool']='strict_passed_spec'
            j['score']=int(original['decision_news_value_score'])
            j['breakdown']=copy.deepcopy(original['decision_value_breakdown'])
            j['route']=original['selection_route']
            j['anchors']=copy.deepcopy(original['anchor_classes'])
            j['exec']='PASS'; j['card']='PASS'; j['urgency']='near_term'
            j['gap']='Stage B must independently verify the bounded-research facts and source-owner diversity used for Prompt 0.1P promotion before drafting.'
            # preserve stage-specific metadata from the original review item
            if original.get('legal_policy_stage'):
                j['legal_stage']=original.get('legal_policy_stage')
            j['tech_stage']=original.get('technology_validation_stage',j.get('tech_stage'))
            item=formal.strict_item(event,j,b)
            # Preserve original Stage A judgment surfaces where research did not change them.
            for k in ('decision_value_breakdown','decision_news_value_score','decision_value_classification','related_prepass','baseline_relation','baseline_follow_up_relation','duplicate_risk','staleness_decision','structural_value_lenses','portfolio_coverage_contribution'):
                if k in original:
                    item[k]=copy.deepcopy(original[k])
            item['spec_id']=f"STD26_R6_P01P_{ordinal:03d}"
            item['source_spec_id']=item['spec_id']
            item['promotion_provenance']={
                'prompt_version':'PROMPT_0_1P_V4_20260829',
                'source_review_pool_item_id':rid,
                'candidate_set_sha256':CAND_SHA,
                'bounded_research_disposition':'PROMOTE_TO_STRICT',
                'original_score_preserved':original['decision_news_value_score'],
                'research_reason':dec['reason'],
                'research_evidence_urls':dec.get('evidence',[]),
            }
            item['new_verified_fact']=dec['reason']
            item['uncertainty_resolved']='The recorded Prompt 0.1P promotion question was resolved by bounded research without changing the original decision-value score.'
            item['remaining_uncertainty']='Stage B must verify claim-level evidence, source ownership and precise operative terms before drafting.'
            item['evidence_needed_for_stage_b']=[f"Verify the primary/official and independent sources supporting this promotion: {', '.join(dec.get('evidence',[]))}"]
            item['next_confirmation_points']=["Confirm the promoted fact package against primary/issuer documents and an independent second-owner source, and invalidate the promotion if the operative stage or quantified terms differ."]
            strict.append(item)
            for row in src_rows:
                row['ledger_decision']='passed'; row['editorial_bucket']='strict_passed_spec'
                row['spec_id']=item['spec_id']; row['review_pool_item_id']=None
                row['merged_into_spec_id']=item['spec_id'] if len(src_rows)>1 else None
                row['reason']=f"Prompt 0.1P promotion PASS for {rid}: {dec['reason']}"
                ledger.append(row)
        else:
            item=copy.deepcopy(original)
            item.pop('_formal_batch',None); item.pop('_source_artifact',None)
            item['promotion_review']={
                'prompt_version':'PROMPT_0_1P_V4_20260829','candidate_set_sha256':CAND_SHA,
                'disposition':'RETAIN_CANDIDATE','reason':dec['reason'],'research_evidence_urls':dec.get('evidence',[])
            }
            item['reason_for_review']=dec['reason']
            item['review_reason']=dec['reason']
            retained.append(item)
            ledger.extend(src_rows)
            oldres=next((copy.deepcopy(x) for x in src.get('review_pool_resolution_ledger',[]) if x.get('review_pool_item_id')==rid),None)
            if oldres:
                oldres['disposition_basis']=f"Prompt 0.1P bounded research completed; RETAIN_CANDIDATE: {dec['reason']}"
                oldres['reviewed_by_stage_or_pass']='Prompt 0.1P V4 R6 promotion review'
                oldres['review_artifact_id']='stage_a_prompt_0_1p_r6_promotion16_20260903_R1'
                resolutions.append(oldres)
        promo_ledger.append({'review_pool_item_id':rid,'formal_batch':b,'ordinal':ordinal,'original_score':original['decision_news_value_score'],'disposition':dec['disposition'],'reason':dec['reason'],'evidence':dec.get('evidence',[])})

    assert len(strict)==2 and len(retained)==14 and len(promo_ledger)==16
    assert len({x['story_id'] for x in ledger})==len(ledger)==len(all_source_ids)
    all_items=strict+retained
    anchors=Counter(a for x in all_items for a in x.get('anchor_classes',[]))
    lenses=Counter(a for x in all_items for a in x.get('structural_value_lenses',[]))
    classes=Counter(x.get('decision_value_classification') for x in all_items)

    art=copy.deepcopy(template)
    art.update({
        'stage':'stage_a','status':'PASS','run_tag':'20260903_R6_PROMPT_0_1P_PROMOTION16',
        'run_label':'Prompt 0.1P V4 authorized R6 candidate-16 promotion review',
        'input_file':str(INPUT.relative_to(ROOT)),
        'source_universe':'Exact 16-item candidate_review_pool promotion universe locked from the validated Formal Stage A R6 395-event run.',
        'story_count':len(ledger),'event_count':16,'original_status_counts':{'kept':len(ledger)},
        'recommended_for':['Stage B evidence package construction for newly promoted strict_passed_spec[] only','retained candidate-review terminal accounting before independent 0.7C completeness challenge'],
        'candidate_promotion_contract':{
            'prompt_file':'docs/llm_prompts/v1/14_PROMPT_0_1P_Review_Pool_Promotion.md','prompt_version':'PROMPT_0_1P_V4_20260829',
            'candidate_set_sha256':CAND_SHA,'candidate_count':16,'promoted_count':2,'retained_count':14,
            'score_inflation_for_source_recovery':False,'promotion_ledger':promo_ledger,
        },
        'strict_passed_spec':strict,'candidate_review_pool':retained,'watchlist_context_pool':[],'reject_or_support_only_pool':[],
        'review_pool':copy.deepcopy(retained),'review_pool_resolution_ledger':resolutions,'decision_ledger':ledger,
        'review_pool_partition_summary':{'candidate_review_pool':14,'watchlist_context_pool':0,'reject_or_support_only_pool':0,'total_review_items':14,'strict_passed_spec':2,'event_total':16},
        'next_call_recommendation':{
            'recommended_next_call':'Stage B r0','recommended_prompt_id':'Prompt 0.2','recommended_input_universe':'Prompt 0.1P validated strict_passed_spec[] only',
            'reason':'Two candidate-review items satisfy the ordinary Stage A strict contract after bounded Prompt 0.1P research; fourteen remain outside Stage B.',
            'pending_parallel_or_followup_call':'independent completeness challenge after downstream reintegration','pending_prompt_id':'Prompt 0.7C','pending_input_universe':'full R6 Stage A universe plus final publish-ready set','pending_reason':'Retained candidate/watch/support pools remain accounted and must be challenged before canonical promotion.','blocked_items_summary':[{'pool':'candidate_review_pool','count':14}]
        },
    })
    # Promotion uses external bounded research by design, unlike original Stage A selector.
    art['lane_sanity_rules_applied']=[x for x in art.get('lane_sanity_rules_applied',[]) if x not in {'selector_only_no_external_web_search','no_article_body_fetch'}] + ['authorized_prompt_0_1p_bounded_research_only','ordinary_stage_a_strict_contract_required_for_promotion']
    art['dropped_treasure_hunt']={'performed':False,'trigger_reason':'Prompt 0.1P is bounded to the exact 16 candidate-review items and does not open a new treasure-hunt universe.','sample_strategy':'not_applicable','sample_size':0,'sampled_story_ids':[],'rescued_count':0,'rescue_ids':[],'non_sampled_dropped_count':0,'non_sampled_ledger_policy':'All 16 candidate items receive an explicit promotion disposition.'}

    s=copy.deepcopy(template['summary'])
    s.update({
        'legacy_keep_count':0,'strict_passed_spec_count':2,'needs_review_count':14,'rejected_count':0,'existing_reinforcement_count':0,'support_source_only_count':0,
        'duplicate_or_reinforcement_count':0,'stale_discarded_count':0,'stale_warm_review_count':0,'total_ledger_count':len(ledger),'ledger_matches_story_count':True,
        'anchor_class_counts':dict(sorted(anchors.items())),'structural_lens_coverage_counts':dict(sorted(lenses.items())),'decision_value_classification_counts':dict(sorted(classes.items())),
        'critical_structural_candidate_ids':[x.get('spec_id') or x.get('review_pool_item_id') for x in all_items if x.get('decision_value_classification')=='critical_structural'],
        'high_decision_value_candidate_ids':[x.get('spec_id') or x.get('review_pool_item_id') for x in all_items if x.get('decision_value_classification')=='high_decision_value'],
        'high_value_review_pool_ids':[x['review_pool_item_id'] for x in retained if x.get('decision_news_value_score',0)>=70],
        'structural_signal_review_pool_ids':[x['review_pool_item_id'] for x in retained if x.get('review_pool_subtype')=='structural_signal_review'],
        'earnings_deep_dive_pool_ids':[x['review_pool_item_id'] for x in retained if x.get('review_pool_subtype')=='earnings_deep_dive'],
        'follow_up_candidate_ids':[x.get('spec_id') or x.get('review_pool_item_id') for x in all_items if x.get('baseline_follow_up_relation') not in {'new','new_unrelated_event','unrelated','not_applicable','none','',None}],
        'technology_validation_gap_ids':[x.get('spec_id') or x.get('review_pool_item_id') for x in all_items if 'technology_commercialization_anchor' in x.get('anchor_classes',[])],
        'legal_policy_stage_gap_ids':[],'decision_ledger_count':len(ledger),'selection_route_counts':dict(Counter(x['selection_route'] for x in all_items)),
        'formal_event_count':16,'source_bound_observation_count':len(ledger)
    })
    art['summary']=s
    art['formal_stage_a_batch']={
        'batch':17,'batch_count_total':17,'ordinal_start':min(x['ordinal'] for x in promo_ledger),'ordinal_end':max(x['ordinal'] for x in promo_ledger),
        'decision_batches_committed_before_this':16,'event_count':16,'strict_count':2,'candidate_review_count':14,'watchlist_count':0,'reject_or_support_only_count':0,
        'formal_stage_a_external_web_search_count':'bounded_prompt_0_1p_research_not_original_stage_a','formal_stage_a_article_body_fetch_count':'bounded_prompt_0_1p_research_not_original_stage_a',
        'adjudication_method':'PROMPT_0_1P_V4_20260829_bounded_research_then_ordinary_stage_a_strict_reemission'
    }

    from validation_scripts import stage_lineage_contract_check as lineage
    from validation_scripts.stage_a_v4_contract import validate_stage_a_v4_payload
    from validation_scripts.stage_a_v4_hardening import validate_stage_a_v4_hardening_payload
    from validation_scripts.stage_a_full_v3_completeness_review4945713246 import prevalidate_full_stage_a_artifact, validate_full_stage_a_artifact
    pre=prevalidate_full_stage_a_artifact(art); v4=validate_stage_a_v4_payload(art,require_contract=True); hard=validate_stage_a_v4_hardening_payload(art,require_contract=True); auth=lineage._validate_active_required_docs(art)
    compat=lineage._project_full_stage_a_for_v3_compat(art) if not auth else art
    full=validate_full_stage_a_artifact(compat,lineage._compat_module); rc=lineage.check_stage_a(art)
    report={'schema':'prompt_0_1p_r6_promotion_validation_v1','status':'PASS' if not(pre or v4 or hard or auth or full) and rc==0 else 'FAIL','candidate_count':16,'promoted_count':2,'retained_count':14,'candidate_set_sha256':CAND_SHA,'prevalidation_errors':pre,'v4_contract_errors':v4,'v4_hardening_errors':hard,'active_authority_errors':auth,'full_completeness_errors':full,'lineage_check_rc':rc}
    OUT.write_text(json.dumps(art,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    report['artifact_sha256']=hashlib.sha256(OUT.read_bytes()).hexdigest()
    REPORT.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(report,ensure_ascii=False,indent=2))
    return 0 if report['status']=='PASS' else 1

if __name__=='__main__': raise SystemExit(main())
