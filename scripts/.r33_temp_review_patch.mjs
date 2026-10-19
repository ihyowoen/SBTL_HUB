#!/usr/bin/env node
// R33 temporary, bounded reviewer remediation. REMOVE before PR review.
import {readFileSync,writeFileSync} from "node:fs";
import {execFileSync} from "node:child_process";
const FULL="data/cards.full.json",MAN="direct-adds/2026-10-17-r28-signed-lfp-source-verified/direct-add.json";
const f=JSON.parse(readFileSync(FULL,"utf8")),m=JSON.parse(readFileSync(MAN,"utf8"));
const before=JSON.stringify(f.cards), now=new Date().toISOString().replace(/\.\d{3}Z$/,"Z");
const assert=(x,msg)=>{if(!x)throw Error(msg)};
assert(f.total===1676&&f.cards.length===1676&&f.updated==="2026-10-17T12:20:29Z","Frozen Full state mismatch");
assert(m.base_main_commit_sha==="6851fdbe4a25b30b7204d07708a1238123c14910"&&m.expected_before===1674&&m.expected_after===1676&&m.formal_full_run_claimed===false,"Governed manifest mismatch");
const S=f.cards.find(x=>x.id==="2026-09-22_KR_01"),D=f.cards.find(x=>x.id==="2026-10-06_KR_01");
assert(S&&D&&S.fact_sources.length===5&&D.fact_sources.length===7,"Unexpected original evidence");
const row=(src,url,claim,quote,supports,date)=>({source_name:src,source_url:url,source_owner:src,claim,source_quote:quote,source_quote_status:src==="포스코퓨처엠"?"official_material_quote_verified":"body_quote_verified",evidence_role:src==="포스코퓨처엠"?"primary_event_evidence":"secondary_event_evidence",supports,source_published_date:date,visible_quote_date:date,source_origin_type:src==="포스코퓨처엠"?"official_or_source_owner_material":"independently_published_reporting",fetch_method:"web_article_body_readback",source_url_canonical_complete:true,resolved_article_matches_quote:true,checked_at:now});
S.fact_sources[1].supports=["fact","implication"];
S.fact_sources[2].supports=["sub"];
S.fact_sources[3].supports=["title","sub","fact","implication"];
S.fact_sources[4].supports=["fact","implication"];
for(const i of [3,4]){S.fact_sources[i].fetch_method="web_article_body_readback";S.fact_sources[i].checked_at=now;}
S.fact_sources.push(row("연합뉴스","https://www.yna.co.kr/amp/view/AKR20260922178700003","9월 22일 SK온 1조1천억원 LFP 양극재 계약 독립 보도","포스코퓨처엠이 SK온과 1조1천억원 규모 리튬인산철(LFP) 양극재 대규모 공급계약을 체결했다고 22일 밝혔다.",["title","sub","gate","fact"],"2026-09-22"));
const sdiMaps=[["sub","fact"],["sub","fact"],["gate","fact"],["title","sub","fact"],["title","gate","fact"],["implication"],["gate","fact"]];
sdiMaps.forEach((fields,i)=>D.fact_sources[i].supports=fields);
D.gate="포스코퓨처엠이 발표한 장기 LFP 양극재 계약액은 약 6조원이다. 양사는 2023년 NCA 공급계약을 개정해 LFP를 추가하고 기존 주요 품목별 계약을 묶는 포괄적 공급 협약도 체결했다. 그러나 LMO·인조흑연 확대는 향후 협력 방향이며, 품목별 확정 발주·실제 납품 및 실현매출과 구분해야 한다.";
D.fact="포스코퓨처엠과 삼성SDI는 10월 6일 배터리 소재 장기 공급 본계약을 체결했다고 발표했다(포스코퓨처엠 홈페이지 게시 10월 7일). 8월 익명 국내 고객사에 대해 합의한 2027~2032년 LFP 양극재 19만t은 삼성SDI 건으로 확인됐고 이번 본계약에서 물량이 2배 이상 확대됐다. 약 6조원은 LFP 장기 공급 계약액이지 연도별 확정 출하·실현매출이 아니다. 기존 2023년 NCA 계약은 LFP까지 확대되고 주요 제품의 개별 계약은 포괄적 공급 협약으로 묶였지만, LMO·인조흑연은 향후 협력 대상으로 남는다. 회사가 발표한 '예상 공급물량 기존 대비 약 45% 증가'와 8월 LFP 합의물량의 '2배 이상 증량'은 서로 다른 비교 기준이다.";
const uD="https://www.poscofuturem.com/pr/view.do?num=1051";
D.fact_sources.push(row("포스코퓨처엠",uD,"삼성SDI 계약은 주요 개별 제품계약을 묶는 포괄적 협약이라는 발행사 원문","이날 삼성SDI와 체결한 계약은 포스코퓨처엠이 공급하는 주요 제품의 개별 계약을 하나로 묶은 포괄적 협약으로",["gate","fact"],"2026-10-07"));
D.fact_sources.push(row("포스코퓨처엠",uD,"발행사 예상 공급물량 약45%와 LFP 19만t 기존 합의 대비 2배는 다른 모집단","예상 공급물량이 기존 대비 약 45% 증가하며",["fact"],"2026-10-07"));
D.fact_sources.push(row("연합뉴스","https://www.yna.co.kr/view/AKR20261006171200003","연합뉴스 당일 보도에서 LFP 6조원 계약액 확인","포스코퓨처엠이 삼성SDI에 6조원 규모의 리튬·인산·철(LFP) 양극재를 장기 공급한다.",["title","gate","fact"],"2026-10-06"));
const contribS={"포스코퓨처엠":"1.1조원 계약·2027~29 기간·상호합의 연장, 기존 SK온 음극재→첫 양극재 거래, 3사 고객 및 포항 전환/생산 예정 원출처","연합뉴스":"당일 독립 기사로 SK온 LFP 1.1조원 계약 확인; 8월 19만t 타 고객사 합의와 별건임을 설명"};
const contribD={"포스코퓨처엠":"6조원 LFP 계약액·19만t 8월 합의 대비 2배 이상, NCA 계약 개정·포괄 협약, 예상공급량 +45%, Non-PFE 기대 및 LMO/흑연 협력 단계 구분","연합뉴스":"당일 6조원 LFP 계약 및 8월 합의 물량 증량 독립보도; 향후 LMO·인조흑연 구분"};
for(const [c,cc] of [[S,contribS],[D,contribD]]){
 for(const e of c.source_discovery_ledger){const rows=c.fact_sources.filter(x=>x.source_url===e.source_url);assert(rows.length>0,"Ledger URL lacks evidence");e.source_domain=e.source_url.split("/")[2].replace(/^www\./,"");e.source_origin_type=rows[0].source_origin_type;e.visible_fields_supported=[...new Set(rows.flatMap(x=>x.supports))].sort();e.checked_at=now;e.unique_contribution=cc[e.source_owner];}
 c.source_evidence_entry_count=c.fact_sources.length;c.source_diversity_measure.source_evidence_entry_count=c.fact_sources.length;
 assert(c.fact_sources.length===c.source_evidence_entry_count,"Counter mismatch");
}
const aS=m.editorial_attestation.additions.find(x=>x.id===S.id),aD=m.editorial_attestation.additions.find(x=>x.id===D.id);
assert(aS&&aD,"Missing editorial attestations");
aD.new_verified_fact += "; 2023년 NCA 공급계약 개정 및 기존 개별 계약을 묶는 포괄 협약; 예상 공급량 +45%는 과거 LFP 19만t 합의 대비 2배 이상과 구별";
aS.evidence_review_summary += " | R33 "+now+": Full official and Yonhap article readbacks confirm SK On 1.1tn 2027-29, mutual-only two-year option, anode-to-cathode first contract, 3 buyers and Pohang conversion (year-end production is future). Added independent amount quote; removed overstated supports and reconciled ledger. Manual six-dimension QC only; formal Prompt 0.6 V5 NOT RUN.";
aD.evidence_review_summary += " | R33 "+now+": Official issuer article confirms 6tn LFP supply and umbrella of existing individual agreements with 2023 NCA-to-LFP amendment; LMO/graphite are prospective, Non-PFE is issuer expectation, and aggregate expected supply volume +45% uses different denominator than 2x August LFP agreement. Added exact primary and independent excerpts; remapped source supports, checked ledger. Manual six Deep Summary dimensions verified; formal Prompt 0.6 V5 NOT RUN.";
f.updated=now;m.output_updated=now;
const old=JSON.parse(before),touched=f.cards.filter((x,i)=>JSON.stringify(x)!==JSON.stringify(old[i])).map(x=>x.id);
assert(touched.join(",")==="2026-10-06_KR_01,2026-09-22_KR_01","Unintended card changes: "+touched);
writeFileSync(FULL,JSON.stringify(f,null,2)+"\n");
writeFileSync(MAN,JSON.stringify(m,null,2)+"\n");
execFileSync("node",["scripts/lean_cards.mjs"],{stdio:"inherit"});
const lean=JSON.parse(readFileSync("public/data/cards.json","utf8"));
assert(lean.updated===m.output_updated&&lean.total===1676&&lean.cards.length===1676,"Projection failed");
console.log("R33 bounded edit generated: 2 cards only, issuer quote mapping, Full/Lean/manifest timestamps synchronized "+now);
