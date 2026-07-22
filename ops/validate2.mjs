#!/usr/bin/env node
// validator v2 신규 검사 (RUNBOOK G3) — 기존 validate.mjs에 추가 예정, 우선 독립 실행
// 사용: node ops/validate2.mjs tracker_data.json [ops/runs/RUN.json]
import { readFileSync } from 'fs';
const tj = JSON.parse(readFileSync(process.argv[2] ?? 'tracker_data.json','utf8'));
const runPath = process.argv[3];
const items = tj.items; const ids = new Set(items.map(i=>i.id));
let E=0,W=0; const err=m=>{console.log('ERROR:',m);E++}, warn=m=>{console.log('WARN :',m);W++};

// 1) 산문 D-day 금지 (이행기 WARN → ERROR 승격 예정)
const PROSE=['t','d','detail','tip'];
for (const i of items) for (const k of PROSE) {
  const v=i[k]; if (typeof v!=='string') continue;
  const m=v.match(/\(?D[-+]{1,2}\d+/g);
  if (m) warn(`${i.id}.${k}: 산문 내 D-day ${m.length}건 [${m.slice(0,3).join(', ')}] — milestones로 이관`);
}
// 2) refs 정합 (필드 있으면 dangling 검사, 산문 ID 언급 ↔ refs 대조)
const IDRE=/\b(NA|EU|CN|KR|JP|GL)-\d{3}\b/g;
for (const i of items) {
  if (Array.isArray(i.refs)) for (const r of i.refs) if(!ids.has(r)) err(`${i.id}.refs dangling: ${r}`);
  const mentioned=new Set();
  for (const k of [...PROSE,'dt','checkNote']) {
    const v=i[k]; if (typeof v!=='string') continue;
    for (const m of v.matchAll(IDRE)) if (m[0]!==i.id) mentioned.add(m[0]);
  }
  for (const m of mentioned) {
    if (!ids.has(m)) err(`${i.id}: 산문이 미존재 항목 참조 ${m}`);
    else if (Array.isArray(i.refs) && !i.refs.includes(m)) warn(`${i.id}: 산문 참조 ${m} 가 refs 미등재`);
  }
}
// 3) 동일 법령·규정 번호 중복 후보 (F10 CN-022 재발 방지)
const PAT=[/令第?\s?(\d+)\s?号/g, /GB\/?T?\s?(\d{4,5})/g, /Regulation\s?\(?EU\)?\s?(20\d{2}\/\d+)/gi, /Pub\.?\s?L\.?\s?(\d+[–-]\d+)/g, /(\d{4}\/\d+\/E[CU])/g];
const seen={};
for (const i of items) {
  if (i.canonicalId||i.supersededBy) continue;  // dedup된 항목 제외
  const blob=[i.t,i.d].join(' ');
  for (const p of PAT) for (const m of blob.matchAll(p)) {
    const key=m[0].replace(/\s/g,'');
    (seen[key] ??= []).push(i.id);
  }
}
for (const [k,v] of Object.entries(seen)) if (new Set(v).size>1) warn(`중복 후보 — '${k}' 를 복수 정본이 언급: ${[...new Set(v)].join(', ')}`);
// 4) 제안 키워드 + ACTIVE/DONE 조합 (F10)
const PROP=/미제정|제안 단계|입법 진행|초안|삼자협의|협의 중|COD\)|pending|채택 미완/;
for (const i of items) if ((i.s==='ACTIVE'||i.s==='DONE') && PROP.test([i.t,i.d].join(' ')))
  warn(`${i.id} [${i.s}]: 제안·미제정 키워드 감지 — status 재검토 (t: ${i.t.slice(0,40)})`);
// 5) watch 큐 due 경과 (필드 도입 후)
const today=new Date().toISOString().slice(0,10);
for (const i of items) if (Array.isArray(i.watch))
  for (const w of i.watch) if (w.status==='open' && w.due && w.due<today) warn(`${i.id}.watch 기한 경과: ${w.what} (due ${w.due})`);
// 6) verify ↔ 원장 대조 (원장 전달 시)
if (runPath) {
  const run=JSON.parse(readFileSync(runPath,'utf8'));
  const covered=new Set();
  for (const s of run.searches??[]) for (const x of s.itemsCovered??[]) covered.add(x);
  for (const p of run.primaryDocs??[]) for (const x of p.itemsCovered??[]) covered.add(x);
  const rd=run.date;
  for (const i of items) {
    const lc=i.verify?.date ?? i.lastChecked;
    const meth=i.verify?.method;
    if (lc===rd && meth!=='mechanical' && !covered.has(i.id))
      err(`${i.id}: verify=${rd} 인데 원장(${run.runId})에 근거 없음 — 부분검증 금지 위반`);
  }
}
// 7) checkNote 내 미이관 pending 신호 (watch 필드 부재 항목)
const PEND=/대기|모니터링 지속|확인 요망|flag/;
let pendCnt=0;
for (const i of items) if (!Array.isArray(i.watch) && typeof i.checkNote==='string' && PEND.test(i.checkNote)) pendCnt++;
if (pendCnt) warn(`watch 미이관 pending 신호 보유 항목 ${pendCnt}개 — M3에서 watch[]로 이관 필요`);


// 8) region_policy ↔ tracker lastUpdated 동기 (RD-4 정합, 별도 인자)
if (process.env.RP_PATH) {
  try {
    const rp=JSON.parse(readFileSync(process.env.RP_PATH,'utf8'));
    const rpDate=(rp._meta?.lastUpdated||'').slice(0,10);
    const tjDate=(tj.meta?.lastUpdated||'').slice(0,10);
    if (rpDate && tjDate && rpDate!==tjDate)
      warn(`region_policy _meta.lastUpdated(${rpDate}) ≠ tracker meta.lastUpdated(${tjDate}) — RD-4 정합 위반`);
    for (const rg of ['NA','EU','CN','KR','JP','GL'])
      if (!rp[rg]) warn(`region_policy: ${rg} 권역 서술 누락`);
  } catch(e){ warn('region_policy 로드 실패: '+e.message); }
}

console.log(`\nRESULT: ${E?'FAIL':'PASS'} (errors ${E}, warnings ${W})`);
process.exit(E?1:0);
