#!/usr/bin/env node
/**
 * PR #386 review-only R24 URL normalisation replay.
 * Replays a tracked byte-identical original R12 fixture (not today's
 * changing production main) and verifies the corrected R12 + all 1,157
 * rows of the checked-in manifest. Does NOT assert unique economic events.
 *
 *   node runs/2026-10-08/ops-recovery-intake-v1/R24_REPLAY_ARTICLE_URLS_V2.mjs
 * 
 * No network access, no side effects, Node core only.
 */
import { readFileSync } from "node:fs";
import { execFileSync } from "node:child_process";
import assert from "node:assert/strict";

const dir = "runs/2026-10-08/ops-recovery-intake-v1/";
const originalSourceRef = "4bce4b1f3e7bd454538e718df7666f03c5310aa0"; // provenance only
const originalBlob = "63b092bb1e6938c8fdbd0a31e98142c198e1e368";
const correctedBlob = "b418ba95a17505e3344afabfc255f67be128243d";
const manifestBlob = "61de9d5a104821040504124014fa3f7116285dd1";
const originalPath = dir+"R24_ORIGINAL_R12_INPUT_1157.csv";
const oldPath = dir+"R12_FULL_CANONICAL_URL_CROSSWALK_1157.csv";
const manifestPath = dir+"R24_NORMALIZED_URL_REPLAY_MANIFEST_1157.csv";
const normVersion = "PR386_R24_ARTICLE_URL_NORM_V2_20261015";

function parse(row) {
  assert(row.startsWith('"') && row.endsWith('"'));
  return row.slice(1,-1).split('","').map(x=>x.replaceAll('""','"'));
}
function serialize(cells) {
  return '"'+cells.map(x=>String(x).replaceAll('"','""')).join('","')+'"';
}
function normalize(url) {
  const idx=url.indexOf("?");
  if(idx<0)return {url,removed:[]};
  const prefix=url.slice(0,idx), kept=[],removed=[];
  for(const pair of url.slice(idx+1).split("&")) {
    const sep=pair.indexOf("="),key=sep<0?pair:pair.slice(0,sep),value=sep<0?"":pair.slice(sep+1);
    const k=decodeURIComponent(key).toLowerCase(),v=decodeURIComponent(value).toLowerCase();
    const track=k.startsWith("utm_")||["fbclid","gclid","yclid","mc_cid","mc_eid"].includes(k)
      ||(k==="sourcetype"&&v==="rss")||(k===".tsrc"&&v==="rss")||(k==="sc"&&v==="rssn");
    if(track)removed.push(key); else kept.push(pair);
  }
  return {url:prefix+(kept.length?"?"+kept.join("&"):""),removed};
}
function blob(text) {
  return execFileSync("git",["hash-object","--stdin"],{input:text,encoding:"utf8"}).trim();
}
assert.equal(normalize("https://example.org/entry?no=5&sourceType=rss").url,"https://example.org/entry?no=5");
assert.equal(normalize("https://example.org/entry?sc=article&idxno=3").url,"https://example.org/entry?sc=article&idxno=3");
assert.equal(normalize("https://example.org/entry?utm_source=abc&newsId=x").url,"https://example.org/entry?newsId=x");

const old=readFileSync(originalPath,"utf8");
assert.equal(blob(old),originalBlob,"historical fixture differs from "+originalSourceRef);
const lines=old.trimEnd().split(/\r?\n/);
assert.equal(lines.length,1158,"1 header + 1,157 observations required");
const h=parse(lines[0]);
assert.deepEqual(h,["source_row_uid","candidate_id","original_input_triage",
"source_normalized_primary_url","url_reobservation_group_size","exact_url_card_ids",
"exact_url_source_scope","url_match_status","event_semantic_disposition",
"canonical_related_disposition","stage_0_0c_terminal_disposition"]);

const groups=new Map(), seen=new Set(), intermediate=[], triage=new Map();
for(const line of lines.slice(1)) {
  const cols=parse(line),uid=cols[0],n=normalize(cols[3]);
  assert(!seen.has(uid),"duplicate source row UID");
  seen.add(uid);
  assert.equal(cols[10],"UNASSIGNED","never fabricate formal terminal status");
  triage.set(cols[2],(triage.get(cols[2])||0)+1);
  groups.set(n.url,(groups.get(n.url)||0)+1);
  intermediate.push({cols,n});
}
assert.equal(groups.size,1045);
assert.equal([...groups.values()].filter(v=>v>1).length,110);
assert.equal([...groups.values()].filter(v=>v>1).reduce((a,b)=>a+b,0),222);
assert.equal(triage.get("KEEP"),919);
assert.equal(triage.get("TRIAGE_FILTERED"),234);
assert.equal(triage.get("REVIEW"),4);

const colnames=["source_row_uid","candidate_id","original_input_triage",
"original_normalized_primary_url","norm_v2_primary_url","norm_v2_reobserved_group_size",
"stripped_tracking_keys","normalization_version"];
const previewCross=[lines[0]];
const previewManifest=[serialize(colnames)];
let stripped=0;
for(const {cols,n} of intermediate) {
  assert.equal(Number(cols[4]),groups.get(n.url),"repeat grouping must remain unchanged");
  if(n.removed.length)stripped++;
  const corrected=[...cols];corrected[3]=n.url;
  previewCross.push(serialize(corrected));
  previewManifest.push(serialize([cols[0],cols[1],cols[2],cols[3],n.url,
    String(groups.get(n.url)),n.removed.join(";"),normVersion]));
}
assert.equal(stripped,3,"exact three RSS acquisition marker rows expected");
const corrected=previewCross.join("\n")+"\n";
const manifest=previewManifest.join("\n")+"\n";
assert.equal(blob(corrected),correctedBlob,"corrected CSV mismatched audited blob");
assert.equal(blob(manifest),manifestBlob,"manifest mismatched audited blob");
assert.equal(readFileSync(oldPath,"utf8"),corrected,"checked-in corrected R12 changed");
assert.equal(readFileSync(manifestPath,"utf8"),manifest,"checked-in URL manifest changed");

console.log("R24 PASS: 1,157 source UIDs, 1,045 unique URLs, 110 repeat groups, 3 acquisition-only corrections; 0 governed event terminals.");
console.log("R24 SHA: corrected="+correctedBlob+", manifest="+manifestBlob);
