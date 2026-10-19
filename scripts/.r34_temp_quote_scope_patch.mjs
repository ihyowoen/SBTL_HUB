#!/usr/bin/env node
// R34 temporary quote-coverage repair. Workflow self-deletes this file before final review.
import {readFileSync,writeFileSync} from "node:fs";
import {execFileSync} from "node:child_process";
const F="data/cards.full.json",M="direct-adds/2026-10-17-r28-signed-lfp-source-verified/direct-add.json";
const f=JSON.parse(readFileSync(F,"utf8")),m=JSON.parse(readFileSync(M,"utf8"));
const assert=(x,msg)=>{if(!x)throw Error(msg);};
const stamp=new Date().toISOString().replace(/\.\d{3}Z$/,"Z");
assert(f.updated==="2026-10-19T07:44:48Z"&&f.total===1676&&f.cards.length===1676,"R33 frozen Full mismatch");
assert(m.output_updated===f.updated&&m.base_main_commit_sha==="6851fdbe4a25b30b7204d07708a1238123c14910"&&m.base_full_blob_sha==="1af792e2e80516e1ec1d7d9660c150b312168b21"&&m.expected_before===1674&&m.expected_after===1676&&m.formal_full_run_claimed===false,"Manifest baseline/contract mismatch");
const before=f.cards.map(c=>JSON.stringify(c));
const d=f.cards.find(c=>c.id==="2026-10-06_KR_01"),s=f.cards.find(c=>c.id==="2026-09-22_KR_01");
assert(d?.fact_sources?.length===10&&s?.fact_sources?.length===6,"R33 evidence count mismatch");
d.fact_sources[0].claim="2026년 10월 6일 삼성SDI와 LFP 포함 소재 장기 공급계약 실제 체결; 6조원 계약액은 별도 발행사·언론사 금액 인용행으로 검증";
d.fact_sources[0].source_quote="포스코퓨처엠은 6일 삼성SDI와 LFP 양극재를 포함한 이차전지소재 '일괄공급'을 위한 배터리용 소재 장기 공급계약을 체결했다.";
d.fact_sources[1].claim="2026년 8월 삼성SDI와 LFP 19만톤(2027~2032) 공급 합의 물량을 2배 이상 늘려 10월 본계약 체결";
d.fact_sources[1].source_quote="지난 8월 삼성SDI와 합의한 2027년부터 2032년까지 19만톤 규모의 LFP 양극재 대규모 장기 공급 합의 물량을 2배 이상 대폭 늘려 본 계약을 맺은 것이다.";
d.fact_sources[6].claim="2023년 삼성SDI NCA 공급계약 개정으로 LFP 품목을 추가함. LMO·인조흑연 미래 협력은 다른 증빙행에 분리.";
d.fact_sources[8].claim="발행사 발표 기준 전체 예상 공급물량은 기존 대비 약 45% 증가; 8월의 LFP 19만톤 대비 2배 이상 증량과 분모가 다름.";
s.fact_sources[2].claim="지난달 익명 국내 배터리사 LFP 19만톤 장기 공급 합의에 이어 SK온 별도 본계약 체결; 국내 3사 고객 확보는 별도 공식 인용행에서 입증";
for(const c of [d,s]){
  for(const evidence of c.fact_sources)evidence.checked_at=stamp;
  for(const ledger of c.source_discovery_ledger){
    const matched=c.fact_sources.filter(v=>v.source_url===ledger.source_url);
    assert(matched.length>0,"Missing ledger source for "+c.id);
    const actual=[...new Set(matched.flatMap(v=>v.supports))].sort();
    const declared=[...ledger.visible_fields_supported].sort();
    assert(JSON.stringify(actual)===JSON.stringify(declared),"Source support drift "+c.id);
    ledger.checked_at=stamp;
  }
  assert(c.source_evidence_entry_count===c.fact_sources.length&&c.source_independent_owner_count===2,"Evidence counter drift");
}
const edits=f.cards.filter((c,i)=>JSON.stringify(c)!==before[i]).map(c=>c.id);
assert(edits.join(",")==="2026-10-06_KR_01,2026-09-22_KR_01","Out of scope edited cards: "+edits);
const notes={
"2026-10-06_KR_01":"R34: expanded exact issuer Oct 6 signed-framework and August 190kt more-than-double contract excerpts; narrowed out-of-range quote claim descriptions for 2023 NCA and the distinct +45% aggregate denominator. Source checks refreshed. No shipment, revenue or statutory Non-PFE certification inferred. Manual six-dimension source readback only; formal Prompt 0.6 V5 NOT RUN.",
"2026-09-22_KR_01":"R34: narrowed Yonhap prior 190kt deal claim to retained literal; separate issuer row verifies three domestic customers. Refreshed quote and ledger check timestamps. No changed signed contract score, stage or publication decision. Formal Prompt 0.6 V5 NOT RUN."
};
for(const entry of m.editorial_attestation.additions){assert(notes[entry.id],"Unknown attestation");entry.evidence_review_summary+=" | "+stamp+" "+notes[entry.id];}
f.updated=stamp;m.output_updated=stamp;
writeFileSync(F,JSON.stringify(f,null,2)+"\n");
writeFileSync(M,JSON.stringify(m,null,2)+"\n");
execFileSync(process.execPath,["scripts/lean_cards.mjs"],{stdio:"inherit"});
const lean=JSON.parse(readFileSync("public/data/cards.json","utf8"));
assert(lean.updated===stamp&&lean.total===1676&&lean.cards.length===1676,"Projection mismatch");
console.log(JSON.stringify({status:"R34_DATA_BUILT",timestamp:stamp,edited_cards:edits,evidence_count:[d.fact_sources.length,s.fact_sources.length],formal_prompt_06:"NOT_RUN"}));
