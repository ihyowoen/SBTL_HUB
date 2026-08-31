#!/usr/bin/env node
import { readFileSync } from "node:fs";

class ValidationError extends Error { constructor(code, message) { super(message); this.code = code; } }
const fail = (code, message) => { throw new ValidationError(code, message); };
const readJson = (path, label) => { try { return JSON.parse(readFileSync(path, "utf8").replace(/^\uFEFF/, "")); } catch (e) { fail("BLOCKED_MANUAL_DIRECT_ADD_INVALID", `${label}: ${e.message}`); } };
const same = (a,b) => JSON.stringify(a) === JSON.stringify(b);
const uniq = (x) => new Set(x).size === x.length;
const RFC3339 = /^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:\d{2})$/;
const ANCHORS = new Set(["execution_event_anchor","policy_regulatory_anchor","data_financial_anchor","strategic_behavior_anchor","technology_commercialization_anchor","follow_up_probability_anchor"]);
const NON_EXECUTION_ANCHORS = new Set(["policy_regulatory_anchor","data_financial_anchor","strategic_behavior_anchor","technology_commercialization_anchor","follow_up_probability_anchor"]);
const CLASSES = [
  [85,"critical_structural"],[70,"high_decision_value"],[55,"material_industry_signal"],[40,"standard_monitoring"],[25,"context_or_reinforcement"],[0,"low_independent_value"]
];
const MANIFEST_KEYS=["schema","status","direct_add_id","review_mode","formal_full_run_claimed","base_main_commit_sha","base_full_blob_sha","expected_before","expected_after","output_updated","operations","editorial_attestation"];
const OPERATION_KEYS=["add","update","id_migration"];
const MIGRATION_KEYS=["old_id","new_id","reason"];
const EDITORIAL_KEYS=["policy_version","additions","updates"];
const ADDITION_KEYS=["id","execution_credibility_gate","independent_cardability_gate","anchor_classes","selection_route","decision_news_value_score","decision_value_classification","publication_urgency","prior_state","new_verified_fact","changed_judgment","evidence_review_summary","next_confirmation_points","inclusion_decision","owner_override_reason","structural_non_execution_reason","why_execution_event_not_required"];
const UPDATE_KEYS=["id","change_type","reason","evidence_review_summary"];

function str(v,l){ if(typeof v!=="string"||!v.trim()) fail("BLOCKED_MANUAL_DIRECT_ADD_INVALID",`${l} must be a non-empty string`); return v.trim(); }
function strArr(v,l,{nonempty=false}={}){ if(!Array.isArray(v)||v.some(x=>typeof x!=="string"||!x.trim())||(nonempty&&v.length===0)) fail("BLOCKED_MANUAL_DIRECT_ADD_INVALID",`${l} must be ${nonempty?"a non-empty ":"an "}array of non-empty strings`); if(!uniq(v)) fail("BLOCKED_MANUAL_DIRECT_ADD_INVALID",`${l} contains duplicates`); return v; }
function exactKeys(v,l,required){
 if(!v||typeof v!=="object"||Array.isArray(v)) fail("BLOCKED_MANUAL_DIRECT_ADD_INVALID",`${l} must be an object`);
 const keys=Object.keys(v), allowed=new Set(required);
 const missing=required.filter(k=>!Object.prototype.hasOwnProperty.call(v,k));
 const extra=keys.filter(k=>!allowed.has(k));
 if(missing.length||extra.length) fail("BLOCKED_MANUAL_DIRECT_ADD_INVALID",`${l} schema mismatch; missing=[${missing.join(",")}] extra=[${extra.join(",")}]`);
 return v;
}
function timestamp(v){ str(v,"output_updated"); if(!RFC3339.test(v)||Number.isNaN(Date.parse(v))) fail("BLOCKED_MANUAL_DIRECT_ADD_INVALID",`output_updated must be RFC3339 — ${v}`); }
function cardMap(cards,label){ if(!Array.isArray(cards)) fail("BLOCKED_MANUAL_DIRECT_ADD_INVALID",`${label}.cards must be an array`); const m=new Map(); for(const c of cards){const id=str(c?.id,`${label} card id`); if(m.has(id)) fail("BLOCKED_MANUAL_DIRECT_ADD_DUPLICATE_ID",`${label} duplicate id ${id}`); m.set(id,c);} return m; }
function topStable(d){ const c={...d}; delete c.cards; delete c.updated; delete c.total; return c; }
function identityTokens(card){ const s=new Set(); for(const k of ["source_spec_id","origin_source_spec_id","original_source_spec_id"]){ if(typeof card?.[k]==="string"&&card[k].trim()) s.add(`spec:${card[k].trim()}`); if(typeof card?.provenance?.[k]==="string"&&card.provenance[k].trim()) s.add(`spec:${card.provenance[k].trim()}`); } for(const u of Array.isArray(card?.urls)?card.urls:[]) if(typeof u==="string"&&u.trim()) s.add(`url:${u.trim()}`); for(const x of Array.isArray(card?.fact_sources)?card.fact_sources:[]) if(typeof x?.source_url==="string"&&x.source_url.trim()) s.add(`url:${x.source_url.trim()}`); if(typeof card?.title==="string"&&card.title.trim()) s.add(`title:${card.title.trim()}`); return s; }
function stableIdentity(a,b){ const l=identityTokens(a),r=identityTokens(b); for(const t of l) if(r.has(t)) return true; return false; }
function brokenPairs(doc,migrate=new Map()){ const ids=new Set(doc.cards.map(c=>c.id)), out=new Set(); for(const c of doc.cards){for(const t of Array.isArray(c.related)?c.related:[]){if(!ids.has(t)){out.add(`${migrate.get(c.id)||c.id}→${migrate.get(t)||t}`);}}} return out; }
function scoreClass(score){ for(const [min,c] of CLASSES) if(score>=min) return c; }

function parseOps(manifest){
 const o=exactKeys(manifest.operations,"operations",OPERATION_KEYS);
 const adds=strArr(o.add,"operations.add"), updates=strArr(o.update,"operations.update");
 if(!Array.isArray(o.id_migration)) fail("BLOCKED_MANUAL_DIRECT_ADD_INVALID","operations.id_migration must be an array");
 const migrations=o.id_migration, oldIds=[],newIds=[],map=new Map();
 for(const [i,x] of migrations.entries()){
   exactKeys(x,`id_migration[${i}]`,MIGRATION_KEYS);
   const oldId=str(x.old_id,`id_migration[${i}].old_id`), newId=str(x.new_id,`id_migration[${i}].new_id`); str(x.reason,`id_migration[${i}].reason`);
   if(oldId===newId||map.has(oldId)) fail("BLOCKED_MANUAL_DIRECT_ADD_INVALID",`invalid/duplicate migration ${oldId}`); map.set(oldId,newId); oldIds.push(oldId);newIds.push(newId);
 }
 if(!uniq(newIds)) fail("BLOCKED_MANUAL_DIRECT_ADD_INVALID","duplicate migration new_id");
 const sets=[adds,updates,oldIds,newIds]; for(let i=0;i<sets.length;i++) for(let j=i+1;j<sets.length;j++){const b=new Set(sets[j]); if(sets[i].some(x=>b.has(x))) fail("BLOCKED_MANUAL_DIRECT_ADD_INVALID","add/update/id_migration identities must be disjoint");}
 return {adds,updates,migrations,oldIds,newIds,migrationMap:map};
}

function validateV2Editorial(m,ops){
 if(m.review_mode!=="already_reviewed_bounded_direct_add"||m.formal_full_run_claimed!==false) fail("BLOCKED_MANUAL_DIRECT_ADD_EDITORIAL","V2 must declare bounded review mode and formal_full_run_claimed=false");
 const e=exactKeys(m.editorial_attestation,"editorial_attestation",EDITORIAL_KEYS); if(e.policy_version!=="EMBEDDED_NEWS_VALUE_SELECTION_V4") fail("BLOCKED_MANUAL_DIRECT_ADD_EDITORIAL","V2 editorial policy attestation missing/invalid");
 const adds=Array.isArray(e.additions)?e.additions:fail("BLOCKED_MANUAL_DIRECT_ADD_EDITORIAL","editorial_attestation.additions required");
 const ups=Array.isArray(e.updates)?e.updates:fail("BLOCKED_MANUAL_DIRECT_ADD_EDITORIAL","editorial_attestation.updates required");
 const addMap=new Map(),upMap=new Map();
 for(const [i,a] of adds.entries()){
   exactKeys(a,`addition[${i}]`,ADDITION_KEYS); const id=str(a.id,`addition[${i}].id`); if(addMap.has(id)) fail("BLOCKED_MANUAL_DIRECT_ADD_EDITORIAL",`duplicate addition attestation ${id}`); addMap.set(id,a);
   if(a.execution_credibility_gate!=="PASS"||a.independent_cardability_gate!=="PASS") fail("BLOCKED_MANUAL_DIRECT_ADD_EDITORIAL",`${id}: credibility/cardability must PASS`);
   const anchors=strArr(a.anchor_classes,`${id}.anchor_classes`,{nonempty:true}); if(anchors.some(x=>!ANCHORS.has(x))) fail("BLOCKED_MANUAL_DIRECT_ADD_EDITORIAL",`${id}: invalid anchor class`);
   if(!["execution_anchor_route","structural_non_execution_route"].includes(a.selection_route)) fail("BLOCKED_MANUAL_DIRECT_ADD_EDITORIAL",`${id}: invalid selection route`);
   if(a.selection_route==="execution_anchor_route"&&!anchors.includes("execution_event_anchor")) fail("BLOCKED_MANUAL_DIRECT_ADD_EDITORIAL",`${id}: execution_anchor_route requires execution_event_anchor`);
   if(a.selection_route==="structural_non_execution_route"){
     if(anchors.includes("execution_event_anchor")) fail("BLOCKED_MANUAL_DIRECT_ADD_EDITORIAL",`${id}: structural_non_execution_route cannot attest execution_event_anchor`);
     if(!anchors.some(x=>NON_EXECUTION_ANCHORS.has(x))) fail("BLOCKED_MANUAL_DIRECT_ADD_EDITORIAL",`${id}: structural_non_execution_route requires a non-execution anchor class`);
   }
   if(!Number.isInteger(a.decision_news_value_score)||a.decision_news_value_score<0||a.decision_news_value_score>100) fail("BLOCKED_MANUAL_DIRECT_ADD_EDITORIAL",`${id}: score must be integer 0..100`);
   const expected=scoreClass(a.decision_news_value_score); if(a.decision_value_classification!==expected) fail("BLOCKED_MANUAL_DIRECT_ADD_EDITORIAL",`${id}: classification ${a.decision_value_classification} != ${expected}`);
   if(!["immediate","near_term","monitor"].includes(a.publication_urgency)) fail("BLOCKED_MANUAL_DIRECT_ADD_EDITORIAL",`${id}: invalid urgency`);
   for(const k of ["prior_state","new_verified_fact","changed_judgment","evidence_review_summary"]) str(a[k],`${id}.${k}`); strArr(a.next_confirmation_points,`${id}.next_confirmation_points`,{nonempty:true});
   if(a.selection_route==="structural_non_execution_route"){str(a.structural_non_execution_reason,`${id}.structural_non_execution_reason`);str(a.why_execution_event_not_required,`${id}.why_execution_event_not_required`);}
   if(a.inclusion_decision==="standard_include"){if(a.decision_news_value_score<55) fail("BLOCKED_MANUAL_DIRECT_ADD_EDITORIAL",`${id}: standard_include requires score >=55`);} else if(a.inclusion_decision==="owner_override_include"){str(a.owner_override_reason,`${id}.owner_override_reason`);} else fail("BLOCKED_MANUAL_DIRECT_ADD_EDITORIAL",`${id}: invalid inclusion_decision`);
 }
 for(const [i,u] of ups.entries()){
   exactKeys(u,`update[${i}]`,UPDATE_KEYS); const id=str(u.id,`update[${i}].id`); if(upMap.has(id)) fail("BLOCKED_MANUAL_DIRECT_ADD_EDITORIAL",`duplicate update attestation ${id}`); upMap.set(id,u); if(!["reinforcement","correction","evidence_update","content_correction"].includes(u.change_type)) fail("BLOCKED_MANUAL_DIRECT_ADD_EDITORIAL",`${id}: invalid change_type`); str(u.reason,`${id}.reason`);str(u.evidence_review_summary,`${id}.evidence_review_summary`);
 }
 if(!same([...addMap.keys()].sort(),[...ops.adds].sort())) fail("BLOCKED_MANUAL_DIRECT_ADD_EDITORIAL","addition attestations must exactly match operations.add");
 if(!same([...upMap.keys()].sort(),[...ops.updates].sort())) fail("BLOCKED_MANUAL_DIRECT_ADD_EDITORIAL","update attestations must exactly match operations.update");
}

function validate(manifest,base,full){
 if(manifest?.schema!=="manual_direct_add_v2") fail("BLOCKED_MANUAL_DIRECT_ADD_V1_RETIRED","active manual direct-add validation accepts manual_direct_add_v2 only; V1 is historical/audit-only");
 exactKeys(manifest,"manifest",MANIFEST_KEYS);
 if(manifest.status!=="PASS") fail("BLOCKED_MANUAL_DIRECT_ADD_INVALID","manifest status must be PASS");
 str(manifest.direct_add_id,"direct_add_id");str(manifest.base_main_commit_sha,"base_main_commit_sha");str(manifest.base_full_blob_sha,"base_full_blob_sha");timestamp(manifest.output_updated);
 if(!Number.isInteger(manifest.expected_before)||!Number.isInteger(manifest.expected_after)) fail("BLOCKED_MANUAL_DIRECT_ADD_INVALID","expected counts must be integers");
 const ops=parseOps(manifest); validateV2Editorial(manifest,ops);
 const bm=cardMap(base?.cards,"base"),fm=cardMap(full?.cards,"full");
 if(base.cards.length!==manifest.expected_before||full.cards.length!==manifest.expected_after) fail("BLOCKED_MANUAL_DIRECT_ADD_COUNT",`card count mismatch base=${base.cards.length}/${manifest.expected_before} full=${full.cards.length}/${manifest.expected_after}`);
 if(manifest.expected_after!==manifest.expected_before+ops.adds.length) fail("BLOCKED_MANUAL_DIRECT_ADD_COUNT","expected_after must equal expected_before + adds; migrations are count-neutral");
 if(full.total!==full.cards.length||base.total!==base.cards.length) fail("BLOCKED_MANUAL_DIRECT_ADD_COUNT","total must equal cards.length");
 if(full.updated!==manifest.output_updated) fail("BLOCKED_MANUAL_DIRECT_ADD_INVALID","full.updated must equal manifest.output_updated");
 if(!same(topStable(base),topStable(full))) fail("BLOCKED_MANUAL_DIRECT_ADD_UNDECLARED_CHANGE","top-level fields other than total/updated/cards changed");
 const lost=[...bm.keys()].filter(x=>!fm.has(x)).sort(), introduced=[...fm.keys()].filter(x=>!bm.has(x)).sort();
 if(!same(lost,[...ops.oldIds].sort())) fail("BLOCKED_MANUAL_DIRECT_ADD_SCOPE",`lost IDs mismatch migration old_ids`);
 if(!same(introduced,[...ops.adds,...ops.newIds].sort())) fail("BLOCKED_MANUAL_DIRECT_ADD_SCOPE",`introduced IDs mismatch add + migration new_ids`);
 for(const id of ops.adds) if(bm.has(id)||!fm.has(id)) fail("BLOCKED_MANUAL_DIRECT_ADD_SCOPE",`declared add invalid ${id}`);
 for(const id of ops.updates){if(!bm.has(id)||!fm.has(id)||same(bm.get(id),fm.get(id))) fail("BLOCKED_MANUAL_DIRECT_ADD_SCOPE",`declared update invalid/unchanged ${id}`);}
 for(const x of ops.migrations){const before=bm.get(x.old_id),after=fm.get(x.new_id);if(!before||!after||fm.has(x.old_id)||bm.has(x.new_id)||!stableIdentity(before,after)) fail("BLOCKED_MANUAL_DIRECT_ADD_IDENTITY",`invalid/stable identity missing ${x.old_id} → ${x.new_id}`);}
 const mutable=new Set(ops.updates); for(const [id,before] of bm.entries()){if(ops.migrationMap.has(id)) continue; const after=fm.get(id);if(after&&!mutable.has(id)&&!same(before,after)) fail("BLOCKED_MANUAL_DIRECT_ADD_UNDECLARED_CHANGE",`${id}: undeclared card change`);}
 const baseBroken=brokenPairs(base,ops.migrationMap),fullBroken=brokenPairs(full),newBroken=[...fullBroken].filter(x=>!baseBroken.has(x));if(newBroken.length) fail("BLOCKED_MANUAL_DIRECT_ADD_RELATED",`new dangling related: ${newBroken.slice(0,5).join(", ")}`);
 return {schema:manifest.schema,before:base.cards.length,after:full.cards.length,added_ids:ops.adds,updated_ids:ops.updates,id_migrations:ops.migrations,new_dangling_related:0};
}

function fixture(){return {total:2,updated:"2026-01-01T00:00:00Z",cards:[{id:"2026-01-02_KR_01",date:"2026-01-02",title:"A",urls:["https://a.example"],related:[]},{id:"2026-01-01_KR_01",date:"2026-01-01",title:"B",urls:["https://b.example"],related:[]}]};}
function selfTest(){
 const base=fixture(),full=structuredClone(base);full.updated="2026-08-29T22:30:00+09:00";full.total=3;full.cards[0].title="A updated";full.cards[1].id="2025-12-31_KR_01";full.cards[1].date="2025-12-31";full.cards.push({id:"2026-01-03_KR_01",date:"2026-01-03",title:"C",urls:["https://c.example"],related:[]});
 const operations={add:["2026-01-03_KR_01"],update:["2026-01-02_KR_01"],id_migration:[{old_id:"2026-01-01_KR_01",new_id:"2025-12-31_KR_01",reason:"event date correction"}]};
 const common={status:"PASS",direct_add_id:"TEST",base_main_commit_sha:"a",base_full_blob_sha:"b",expected_before:2,expected_after:3,output_updated:full.updated,operations};
 let v1Blocked=false;try{validate({schema:"manual_direct_add_v1",...common},base,full);}catch(e){v1Blocked=e instanceof ValidationError&&e.code==="BLOCKED_MANUAL_DIRECT_ADD_V1_RETIRED";}if(!v1Blocked) throw new Error("self-test failed to reject retired V1");
 const v2={schema:"manual_direct_add_v2",...common,review_mode:"already_reviewed_bounded_direct_add",formal_full_run_claimed:false,editorial_attestation:{policy_version:"EMBEDDED_NEWS_VALUE_SELECTION_V4",additions:[{id:"2026-01-03_KR_01",execution_credibility_gate:"PASS",independent_cardability_gate:"PASS",anchor_classes:["data_financial_anchor"],selection_route:"structural_non_execution_route",decision_news_value_score:60,decision_value_classification:"material_industry_signal",publication_urgency:"near_term",prior_state:"old",new_verified_fact:"new",changed_judgment:"changed",evidence_review_summary:"official evidence reviewed",next_confirmation_points:["next metric"],inclusion_decision:"standard_include",owner_override_reason:null,structural_non_execution_reason:"material data change",why_execution_event_not_required:"decision-useful without transaction"}],updates:[{id:"2026-01-02_KR_01",change_type:"evidence_update",reason:"better source",evidence_review_summary:"verified"}]}};validate(v2,base,full);
 const missingMigration=structuredClone(v2);delete missingMigration.operations.id_migration;let missingMigrationBlocked=false;try{validate(missingMigration,base,full);}catch(e){missingMigrationBlocked=e instanceof ValidationError&&/id_migration/.test(e.message);}if(!missingMigrationBlocked) throw new Error("self-test failed to reject missing required operations.id_migration");
 const extraField=structuredClone(v2);extraField.operations.unexpected=true;let extraFieldBlocked=false;try{validate(extraField,base,full);}catch(e){extraFieldBlocked=e instanceof ValidationError&&/extra=\[unexpected\]/.test(e.message);}if(!extraFieldBlocked) throw new Error("self-test failed to reject additional operation property");
 const low=structuredClone(v2);low.editorial_attestation.additions[0].decision_news_value_score=40;low.editorial_attestation.additions[0].decision_value_classification="standard_monitoring";let blocked=false;try{validate(low,base,full);}catch(e){blocked=e instanceof ValidationError;}if(!blocked) throw new Error("self-test failed to block low standard inclusion");
 low.editorial_attestation.additions[0].inclusion_decision="owner_override_include";low.editorial_attestation.additions[0].owner_override_reason="intentional strategic watch card";validate(low,base,full);
 const badExecution=structuredClone(v2);badExecution.editorial_attestation.additions[0].selection_route="execution_anchor_route";let badExecutionBlocked=false;try{validate(badExecution,base,full);}catch(e){badExecutionBlocked=e instanceof ValidationError&&/execution_event_anchor/.test(e.message);}if(!badExecutionBlocked) throw new Error("self-test failed to block execution route without execution_event_anchor");
 const badStructural=structuredClone(v2);badStructural.editorial_attestation.additions[0].anchor_classes=["execution_event_anchor"];let badStructuralBlocked=false;try{validate(badStructural,base,full);}catch(e){badStructuralBlocked=e instanceof ValidationError&&/structural_non_execution_route/.test(e.message);}if(!badStructuralBlocked) throw new Error("self-test failed to block structural route with execution_event_anchor");
 console.log("PASS: validate_manual_direct_add V2-only schema/editorial/route-anchor self-test");
}

const args=process.argv.slice(2);if(args.includes("--self-test")){selfTest();process.exit(0);}const get=f=>{const i=args.indexOf(f);return i>=0?args[i+1]:null;};
try{const manifestPath=get("--manifest"),basePath=get("--base"),fullPath=get("--full");if(!manifestPath||!basePath||!fullPath) fail("INVALID_ARGUMENT","--manifest --base --full required");const r=validate(readJson(manifestPath,"manifest"),readJson(basePath,"base"),readJson(fullPath,"full"));console.log(JSON.stringify({status:"PASS",...r},null,2));console.log(`PASS: ${r.schema} ${r.before} → ${r.after}; add ${r.added_ids.length}; update ${r.updated_ids.length}; migration ${r.id_migrations.length}`);}catch(e){if(e instanceof ValidationError){console.error(`FAIL [${e.code}]: ${e.message}`);process.exit(1);}throw e;}