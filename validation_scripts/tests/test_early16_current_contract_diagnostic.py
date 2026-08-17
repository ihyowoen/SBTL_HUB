import base64
import gzip
import io
import json
import unittest
from collections import Counter
from contextlib import redirect_stdout
from copy import deepcopy
from pathlib import Path

from validation_scripts.stage_lineage_contract_check import check_stage_a_full

PAYLOAD = ''.join(Path(f'.diagnostics/early16_payload_{i}.txt').read_text().strip() for i in range(8))

REPAIRS = {
 'STD26_A_001': {'next_confirmation_points':[{'measurable_event_or_metric':'Section 232 polysilicon proclamation effective date and final covered-HTS tariff schedule publication','interpretation_effect':'The published schedule would confirm or invalidate the U.S. polysilicon market-access and supply-chain impact thesis.'}]},
 'STD26_A_009': {'next_confirmation_points':[{'measurable_event_or_metric':'GM-Samsung SDI Indiana JV transaction closing date and transferred 49.99% ownership status','interpretation_effect':'Transaction closing would confirm or invalidate the GM-Samsung SDI strategic-control and Indiana asset-use thesis.'}]},
 'STD26_A_010': {'evidence_needed_for_stage_b':[{'source_or_document_class':'official EIA dataset','exact_claim_or_metric':'EIA 2026 U.S. electricity-consumption volume in billion kWh, EIA 2027 consumption volume in billion kWh, and AI/data-center load volume in billion kWh'}],'next_confirmation_points':[{'measurable_event_or_metric':'EIA next STEO U.S. electricity-consumption volume in billion kWh and data-center load volume in billion kWh','interpretation_effect':'This would weaken the EIA demand thesis.'}]},
 'STD26_A_013': {'evidence_needed_for_stage_b':[{'source_or_document_class':'official SNE Research statistics dataset','exact_claim_or_metric':'SNE H1 2026 non-China EV battery volume of 269.0 GWh, 26.3% year-on-year volume growth, and Korean-three supplier-share percentage'}],'next_confirmation_points':[{'measurable_event_or_metric':'SNE H2 2026 non-China EV battery volume in GWh and Korean-three supplier-share percentage change','interpretation_effect':'This would weaken the SNE market thesis.'}]},
 'STD26_A_016': {'next_confirmation_points':[{'measurable_event_or_metric':'Salares Altoandinos antitrust approval or project milestone date change','interpretation_effect':'This would weaken the Altoandinos timing thesis.'}]},
 'STD26_A_017': {'evidence_needed_for_stage_b':[{'source_or_document_class':'official government demonstration-program notice or project document','exact_claim_or_metric':'KREST-Lobos 2026 humanoid hot-swap demonstration award status, field-test start date, test duration, robot count, and battery-swap cycle target'}]},
 'STD26_A_018': {'next_confirmation_points':[{'measurable_event_or_metric':'Bikaner phase-2 800 MWh commissioning completion date or utilization rate','interpretation_effect':'This would weaken the Bikaner scale-up thesis.'}]},
 'STD26_A_021': {'next_confirmation_points':[{'measurable_event_or_metric':'DR Congo export-ban enforcement launch date, exemption approval status, or monthly concentrate export volume','interpretation_effect':'This would weaken the DRC trade thesis.'}]},
 'STD26_A_022': {'next_confirmation_points':[{'measurable_event_or_metric':'Korea Zinc next-quarter segment-margin percentage, sales volume, and operating-profit bridge','interpretation_effect':'The filing would confirm or invalidate the Korea Zinc profitability-persistence thesis.'}]},
 'STD26_A_023': {'next_confirmation_points':[{'measurable_event_or_metric':'Albemarle next-quarter realized lithium price, sales volume, and Energy Storage EBITDA-margin percentage','interpretation_effect':'The earnings update would confirm or invalidate the Albemarle lithium-recovery and earnings-persistence thesis.'}]},
}

HEADLINES = {
 '20260807_160552::US_2026-08-06_C09':'Fact Sheet: President Donald J. Trump Bolsters National Security and Strengthens U.S. Supply Chains by Imposing Tariffs on Polysilicon and its Derivatives',
 '20260807_160552::KR_2026-08-07_C85':'산업부·기후부, 사용후배터리 산업 육성 맞손…거래·이력 플랫폼 조성',
 '20260807_160552::KR_2026-08-07_C60':'기후부·산업부 칸막이 허문다…사용후배터리 통합관리로 핵심광물 공급망 강화',
 '20260807_160552::KR_2026-08-07_C81':'사용후배터리 관리 체계 일원화…산업부·기후부 칸막이 허문다',
 '20260807_160552::KR_2026-08-07_C126':'포스코퓨처엠, LFP 양극재 장기 공급 합의',
 '20260807_160552::KR_2026-08-07_C127':'포스코퓨처엠, 국내 배터리 업체와 LFP 양극재 공급 합의',
 '20260807_160552::US_2026-08-06_C22':'Tesla starts Megapack 3 production with 28% more energy per unit',
 '0.0C_DISCOVERY::REUTERS_2026-08-11_SAMSUNG_SDI_GM':'GM plans to sell its half of Indiana battery venture to Samsung SDI, Bloomberg News reports',
 '0.0C_DISCOVERY::REUTERS_2026-08-11_EIA_POWER':'US power use to beat record highs in 2026, 2027 as AI use surges, EIA says',
 '20260807_160552::TF_0071':'2026년 1~6월 非중국 글로벌 전기차용 배터리 사용량 269.0GWh, 전년 동기 대비 26.3% 성장 2026.08.07',
 '20260809_221256::TF_0002':'2026년 1~6월 非중국 글로벌 전기차용 배터리 사용량 269.0GWh, 전년 동기 대비 26.3% 성장 2026.08.07',
 '20260807_160552::TF_0036':'Hades licence win puts Germany on rare earth map - Mining.com',
 '20260807_160552::GL_2026-08-07_C05':"CATL's Jianxiawo lithium mine remains closed pending environmental approval, state media reports - Mining Weekly",
 '20260807_160552::GL_2026-08-06_C18':'ENAMI says China antitrust review of Rio Tinto lithium project delayed - Mining.com',
 '20260807_160552::GL_2026-08-07_C07':"Chile's ENAMI says China antitrust review of Rio Tinto lithium project delayed - Mining Weekly",
 '20260807_160552::KR_2026-08-07_C120':'크레스트, 휴머노이드 배터리 실증사업 선정…핫스왑 기술 상용화 나선다',
 '20260807_160552::KR_2026-08-07_C119':'크레스트, 로브로스와 ‘무정전 핫스왑 배터리시스템’ 개발 본격화',
 '20260807_160552::GL_2026-08-06_C45':'Serentica commissions first phase of 1GWh Bikaner BESS in India',
 '20260807_160552::EU_2026-08-06_C14':'Serentica Renewables commissions first phase of 1 GWh Bikaner battery project',
 '20260807_160552::GL_2026-08-05_C16':'Japan: Tokyo Gas enters offtake for 200MWh Fukushima BESS, Eku Energy nears completion of first project',
 '20260807_160552::GL_2026-08-06_C11':'Congo bans exports of copper, cobalt concentrates, official order says - Mining.com',
 '20260807_160552::GL_2026-08-06_C13':'Congo bans exports of copper, cobalt concentrates, official order says - The Straits Times',
 '20260807_160552::GL_2026-08-07_C09':'Congo bans exports of copper, cobalt concentrates, official order says - Mining Weekly',
 '20260807_160552::TF_0057':'고려아연 상반기 매출 12조·영업이익 1조3천억 돌파 ‘사상 최대’ 2분기 매출 6조3,730억·영업이익 5,870억…106분기 연속 흑자 달성 2분기 배당 주당 5천원 결의…”예측 가능한 주주환원 기조 지속”',
 '20260807_160552::GL_2026-08-05_C02':'Albemarle quarterly profit surges on rising lithium prices - Mining.com',
}


def repair(data):
    repaired=deepcopy(data)
    strict_by_story={}
    cluster_by_story={}
    representative_by_spec={}
    for item in repaired['strict_passed_spec']:
        for field,value in REPAIRS.get(item.get('spec_id'),{}).items():
            item[field]=deepcopy(value)
        representative_by_spec[item['spec_id']]=item.get('representative_story_id')
        for c in item.get('same_event_source_cluster',[]):
            if isinstance(c,dict) and c.get('story_id'):
                cluster_by_story[c['story_id']]=c
        for story_id in item.get('source_story_ids',[]):
            strict_by_story[story_id]=item

    for row in repaired['decision_ledger']:
        story_id=row.get('story_id')
        spec=strict_by_story.get(story_id)
        if not spec:
            continue
        cluster=cluster_by_story[story_id]
        row['evidence_needed_for_stage_b']=deepcopy(spec.get('evidence_needed_for_stage_b'))
        row['next_confirmation_points']=deepcopy(spec.get('next_confirmation_points'))
        row['upstream_drop_reason']=None
        row['headline']=HEADLINES[story_id]
        row['site']=cluster.get('site')
        row['url']=cluster.get('url')
        row['integrity_group_id']=None
        row['integrity_is_best']=None
        row['merged_into_spec_id']=(None if story_id==representative_by_spec[spec['spec_id']] else spec['spec_id'])
        row['baseline_match']=spec.get('baseline_match')
        row['baseline_relation']=spec.get('baseline_relation')
        row['duplicate_risk']=spec.get('duplicate_risk')
        row['staleness_decision']=spec.get('staleness_decision')
        row['treasure_hunt_sampled']=row.get('upstream_status')=='TRIAGE_FILTERED'
        if story_id.startswith('0.0C_DISCOVERY::'):
            row['notes']='0.0C discovery observation provenance restored from its normalized discovery headline/site/URL; editorial disposition unchanged.'
        elif story_id.endswith('::KR_2026-08-07_C119'):
            row['notes']='Raw headline field contained article-body spillover; ledger uses the source-title prefix while preserving the exact composite story ID and URL.'
        else:
            row['notes']='Raw observation provenance restored from the exact composite run/story ID; editorial disposition unchanged.'

    repaired['original_status_counts']=dict(Counter(r.get('upstream_status') for r in repaired['decision_ledger']))
    return repaired


class Early16CurrentContractDiagnostic(unittest.TestCase):
    def test_early16_current_contract(self):
        original=json.loads(gzip.decompress(base64.b64decode(PAYLOAD)))
        data=repair(original)
        out=io.StringIO()
        with redirect_stdout(out):
            rc=check_stage_a_full(data)
        self.assertEqual(rc,0,out.getvalue())
        self.assertEqual(len(data['strict_passed_spec']),16)
        self.assertEqual(len(data['decision_ledger']),25)
        self.assertEqual(data['original_status_counts'],{'KEEP':19,'DISCOVERY':2,'TRIAGE_FILTERED':4})
        self.assertEqual(sum(1 for r in data['decision_ledger'] if r['treasure_hunt_sampled']),4)
        self.assertTrue(all(k in HEADLINES for k in (r['story_id'] for r in data['decision_ledger'])))
        Path('early16_repaired_current_main.json').write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8')
        print('RESULT: PASS_EARLY16_CURRENT_MAIN_REPAIRED')

if __name__=='__main__': unittest.main()
