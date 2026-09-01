#!/usr/bin/env node
// validator v2 신규 검사 (RUNBOOK G3) — 기존 validate.mjs에 추가 예정, 우선 독립 실행
// 사용: node ops/validate2.mjs public/data/tracker_data.json [ops/runs/RUN.json]
//       env: RP_PATH=public/data/region_policy.json  COV_PATH=ops/coverage.json
import { readFileSync, readdirSync } from 'fs';
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
// 5) watch 큐 due 경과 → ERROR (G2: run 종료 불가)
const today=new Date().toISOString().slice(0,10);
for (const i of items) if (Array.isArray(i.watch))
  for (const w of i.watch) if (w.status==='open' && w.due && w.due<today) err(`${i.id}.watch 기한 경과 — G2상 run 종료 불가: ${w.what} (due ${w.due})`);
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
    // v2 verify 사용 시 runId까지 대조 (동일 날짜 다른 원장으로 통과하는 구멍 차단)
    if (i.verify && lc===rd && meth!=='mechanical' && i.verify.runId !== run.runId)
      err(`${i.id}: verify.runId(${i.verify.runId ?? '없음'}) ≠ 원장 runId(${run.runId}) — 추적성 미확보`);
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
    // region_policy는 '현재 발행 상태'의 스냅샷이므로 부분 run에서도 갱신된다. 따라서 비교 대상은
    // meta.lastUpdated(마지막 전수 검증일)가 아니라 스냅샷 날짜 — dataSnapshotDate가 있으면 그것이 정본.
    const snapDate=(tj.meta?.dataSnapshotDate||'').slice(0,10);
    const tjDate=snapDate||(tj.meta?.lastUpdated||'').slice(0,10);
    if (rpDate && tjDate && rpDate!==tjDate)
      warn(`region_policy _meta.lastUpdated(${rpDate}) ≠ tracker ${snapDate?'meta.dataSnapshotDate':'meta.lastUpdated'}(${tjDate}) — RD-4 정합 위반`);
    for (const rg of ['NA','EU','CN','KR','JP','GL'])
      if (!rp[rg]) warn(`region_policy: ${rg} 권역 서술 누락`);
  } catch(e){ warn('region_policy 로드 실패: '+e.message); }
}

// 9) coverage.json ↔ tracker ID 동기 (RD-3 gap 은폐 방지)
{
  const covPath = process.env.COV_PATH ?? 'ops/coverage.json';
  try {
    const cov=JSON.parse(readFileSync(covPath,'utf8'));
    const bad=new Map();
    for (const c of cov.cells??[]) for (const x of c.items??[])
      if (!ids.has(x)) { const k=`${c.axis}/${c.region}`; bad.set(k,[...(bad.get(k)??[]),x]); }
    for (const [cell,list] of bad)
      err(`coverage ${cell}: tracker에 없는 ID 참조 ${list.join(', ')} — 셀이 covered로 잘못 표시되어 gap 은폐. 데이터 파일과 동시 착지 필요`);
    const mapped=new Set((cov.cells??[]).flatMap(c=>c.items??[]));
    const unmapped=[...ids].filter(x=>!mapped.has(x));
    if (unmapped.length) warn(`coverage 미매핑 항목 ${unmapped.length}개: ${unmapped.slice(0,8).join(', ')}${unmapped.length>8?' …':''}`);
  } catch(e){
    // COV_PATH 를 명시했다는 것은 그 파일을 검사하라는 요청이다 — 파싱 실패를 경고로 흘리면
    // 손상·삭제된 coverage.json 이 게이트를 통과한다(검사 #13은 원장 미전달 시 건너뛰므로 이중 사각).
    if (process.env.COV_PATH) err('coverage 로드 실패(COV_PATH 명시됨): '+e.message);
    else warn('coverage 로드 실패: '+e.message);
  }
}

// 10) meta.totalItems ↔ items.length 동기 (앱이 totalItems를 우선 표시)
if (tj.meta && tj.meta.totalItems != null && tj.meta.totalItems !== items.length)
  err(`meta.totalItems(${tj.meta.totalItems}) ≠ items.length(${items.length}) — 앱 헤더가 과소/과대 보고`);

// 11) dt의 D-day ↔ 선행 앵커 날짜 정합 (롤오버 누락 검출; 1~2자리 월/일 허용, dt 전용)
{
  const DATE=/(\d{4})\.(\d{1,2})\.(\d{1,2})/g, MK=/D-{1,2}\d+|D\+\d+/g;
  const today=new Date(); const t0=Date.UTC(today.getUTCFullYear(),today.getUTCMonth(),today.getUTCDate());
  // dt 전용: 산문(t/d/detail/tip)은 앵커가 모호해 오탐 → 검사 #1이 산문 D-day 자체를 금지
  for (const i of items) for (const k of ['dt']) {
    const v=i[k]; if (typeof v!=='string') continue;
    for (const m of v.matchAll(MK)) {
      const pre=v.slice(0,m.index); const ds=[...pre.matchAll(DATE)];
      if (!ds.length) continue;
      const [,y,mo,d]=ds[ds.length-1];
      const anc=Date.UTC(+y,+mo-1,+d); if (Number.isNaN(anc)) continue;
      const delta=Math.round((anc-t0)/86400000);
      const good = delta>=0 ? `D-${delta}` : `D+${-delta}`;
      if (m[0]!==good) err(`${i.id}.${k}: D-day 스테일 ${m[0]} → ${good} (앵커 ${y}.${mo}.${d}) — RD-0 롤오버 누락`);
    }
  }
}

// 12) region_policy ↔ App.jsx 로더 스키마 (useTrackerData는 policies+watchpoints 배열 요구)
if (process.env.RP_PATH) {
  try {
    const rp=JSON.parse(readFileSync(process.env.RP_PATH,'utf8'));
    for (const rg of ['NA','EU','CN','KR','JP','GL']) {
      const e=rp[rg]; if (!e) continue;
      if (!Array.isArray(e.policies) || !Array.isArray(e.watchpoints))
        err(`region_policy ${rg}: policies/watchpoints 배열 누락 — App.jsx useTrackerData가 병합을 거부하고 하드코드 REGION_POLICY로 폴백(갱신 미반영)`);
      const nonStr=(e.watchpoints||[]).filter(w=>typeof w!=='string').length;
      if (nonStr) err(`region_policy ${rg}: watchpoints에 비문자열 ${nonStr}건 — 렌더러가 {wp}를 직접 출력하므로 React 렌더 오류`);
      for (const p of e.policies||[]) if (!p || typeof p.name!=='string' || typeof p.desc!=='string')
        err(`region_policy ${rg}: policies 항목에 name/desc 문자열 누락`);
      if (typeof e.why!=='string') warn(`region_policy ${rg}: why 문자열 없음 — '왜 중요한지' 블록이 빈칸으로 렌더`);
      if (typeof e.title!=='string') warn(`region_policy ${rg}: title 없음 — 카드 헤더 빈칸`);
    }
  } catch(e){ warn('region_policy 스키마 검사 실패: '+e.message); }
}

// 13) coverage.lastSwept ↔ 원장 스윕 근거 대조 (스윕 위장 차단)
//     lastSwept 를 run 날짜로 찍었는데 그 run 원장에 해당 (region, axis) 근거가 없으면 ERROR.
//     근거 인정 경로 — ① searches[].axis + region 일치  ② searches[]/primaryDocs[].itemsCovered 가 그 셀 items 에 포함.
//     gap/na 셀은 items 가 비어 있어 ②로는 근거를 댈 수 없다: 무산출 스윕은 searches[].axis 를 반드시 적어야 한다.
//     도입 계기(2026-08-31) — RD-3 에서 subsidy 6셀 전부에 lastSwept 를 찍었으나 실검색은 1권역뿐이었고,
//     원장 searches 와 coverage.lastSwept 가 서로 대조되지 않아 기존 게이트를 전부 통과했다.
if (runPath) {
  try {
    const run2 = JSON.parse(readFileSync(runPath,'utf8'));
    const cov2 = JSON.parse(readFileSync(process.env.COV_PATH ?? 'ops/coverage.json','utf8'));
    const rd2 = run2.date;
    // 도입 시점 임계 — 이전 원장은 searches[].axis 스키마가 없어 gap/na 셀 근거를 남길 방법이 없었다.
    // 소급 적용하면 고칠 수 없는 과거 데이터로 ERROR가 나고 그 원장을 손대는 PR이 전부 막힌다.
    // 임계는 날짜이므로 앞으로만 움직이고 우회되지 않는다.
    const SWEEP_FROM = '2026-08-31';
    if (!rd2 || rd2 < SWEEP_FROM) {
      warn(`스윕 근거 대조 건너뜀 — 원장 날짜(${rd2 ?? '없음'})가 검사 도입일(${SWEEP_FROM}) 이전. searches[].axis 스키마 부재로 소급 검증 불가`);
    } else {
    const i2c = new Map();
    for (const c of cov2.cells ?? []) for (const x of c.items ?? []) {
      if (!i2c.has(x)) i2c.set(x, []);
      i2c.get(x).push(`${c.region}/${c.axis}`);
    }
    const ev = new Set();
    for (const s of run2.searches ?? []) {
      // 축을 명시한 검색은 **그 (region, axis) 만** 근거가 된다.
      // itemsCovered 로 파생시키면 다중 셀 소속 항목이 다른 축까지 근거를 만들어(예: NA-027 은
      // NA/trade·NA/subsidy 양쪽 소속) 무근거 lastSwept 전진을 다시 허용한다 — 이 검사가 막으려던 바로 그것.
      if (s.region && s.axis) { ev.add(`${s.region}/${s.axis}`); continue; }
      for (const x of s.itemsCovered ?? []) for (const k of i2c.get(x) ?? []) ev.add(k);
    }
    for (const p of run2.primaryDocs ?? [])
      for (const x of p.itemsCovered ?? []) for (const k of i2c.get(x) ?? []) ev.add(k);
    let stamped = 0, missing = 0;
    for (const c of cov2.cells ?? []) {
      if (c.lastSwept !== rd2) continue;
      stamped++;
      const k = `${c.region}/${c.axis}`;
      if (!ev.has(k)) {
        missing++;
        err(`coverage ${k}: lastSwept=${rd2} 인데 원장(${run2.runId})에 스윕 근거 없음 — 검색을 돌리지 않고 스윕 표기만 전진했거나, 무산출 스윕에 searches[].axis 가 없다`);
      }
    }
    if (stamped && !missing) console.log(`INFO : 스윕 근거 대조 — lastSwept=${rd2} 셀 ${stamped}개 전부 원장 근거 확인`);
    }
  } catch(e){ warn('스윕 근거 대조 실패: '+e.message); }
}


// 14) 노출 필드 마크다운 파손 (ERROR)
//     d·tip·detail 은 App.jsx 가 사용자에게 직접 렌더한다. 볼드 마커가 홀수 개면 강조가 문장 끝까지
//     번지고, 별표 3개 이상은 그대로 출력되며, 내부 필드명 잔재(…ckNote)는 편집 사고의 흔적이다.
//     도입 계기(2026-08-31): 감사화법을 정규식 substring 삭제로 지우다 4개 항목의 tip 문장이 깨졌고
//     Codex 리뷰가 지적할 때까지 사용자 화면에 렌더되고 있었다.
for (const i of items) for (const f of ['d','tip','detail']) {
  const v = i[f]; if (typeof v !== 'string' || !v) continue;
  const stars = v.match(/[*]{3,}/g);
  if (stars) err(`${i.id}.${f}: 별표 3개 이상 ${stars.length}건 — 마크다운 파손이 사용자 화면에 렌더됨`);
  const bolds = v.match(/[*][*]/g);
  if (bolds && bolds.length % 2) err(`${i.id}.${f}: 볼드 마커 홀수 개(${bolds.length}) — 강조가 문장 끝까지 번짐`);
  if (/[가-힣]ckNote/.test(v)) err(`${i.id}.${f}: 내부 필드명 잔재(…ckNote) — 편집 사고 흔적`);
  // 의미 파편 — 마커 짝은 맞아도 문장 앞이 잘리면 조사·어미로 시작한다.
  // 마커 기반 검사로는 잡히지 않아 Codex 6차에서 JP-004 tip 이 이 형태로 남아 있었다.
  const head = v.replace(/^[*\s]+/, '');
  if (/^(짜리|이며|하고|으로써|에서는|에게는|보다는|까지는|부터는|라는|이라는|되며|되고|인데|지만|면서)/.test(head))
    err(`${i.id}.${f}: 조사·어미로 시작 — 문장 앞이 잘린 의미 파편("${head.slice(0,24)}…")`);
}


// 15) verify.runId ↔ 원장 파일 실재 대조 (ERROR)
//     검사 #6은 verify.date === run.date 인 항목만 본다. 그래서 **원장이 존재하지 않는 날짜**의 스탬프는
//     어느 대조 대상에도 들어가지 않고 영영 검사되지 않는다. 2026-09-01 도입 계기: EU-038이
//     runId "2026-09-01-FIX"(실재하지 않는 원장)로 머지됐고 CI 가 통과시켰다.
//     **fail-open 금지** — 원장 디렉터리를 못 읽거나 원장 하나가 파싱되지 않으면 검사 전체가 건너뛰어진다.
//     그 경우 경고로 넘기면 이 검사가 막으려던 무검증 통과 경로가 그대로 되살아나므로 ERROR 로 끊는다.
//     다만 **기준 집합을 아예 만들지 못한 경우와 일부만 깨진 경우를 가른다** — 전자에서 항목별 대조까지
//     돌리면 전 항목이 오탐으로 걸려(실측 185줄) 진짜 원인이 묻힌다. 실패는 한 줄로, 종료코드는 그대로 1.
{
  const dir = 'ops/runs';
  const known = new Set();
  let scanned = 0, baseUsable = true;
  try {
    for (const f of readdirSync(dir)) {
      if (!f.endsWith('.json')) continue;
      scanned++;
      try {
        const id = JSON.parse(readFileSync(`${dir}/${f}`,'utf8')).runId;
        if (id) known.add(id);
        else err(`ops/runs/${f}: runId 필드 없음 — 이 원장을 가리키는 스탬프가 미검사로 통과한다`);
      } catch(e) {
        err(`ops/runs/${f}: 파싱 실패(${e.message}) — 원장 하나가 깨지면 그 원장을 가리키는 스탬프가 전부 미검사로 통과한다`);
      }
    }
    if (!scanned) {
      baseUsable = false;
      err(`${dir}: 원장 파일 0개 — runId 실재 대조를 수행할 수 없다(검사가 조용히 꺼진 상태)`);
    }
  } catch(e) {
    baseUsable = false;
    err(`${dir} 스캔 실패(${e.message}) — runId 실재 대조를 수행할 수 없다. 저장소 루트에서 실행할 것`);
  }
  // 기준 집합이 부분적으로 깨진 경우(파싱 실패 일부)에는 대조를 계속한다 — 위에서 이미 ERROR 를 올렸다.
  // 기준 집합이 통째로 없는 경우에는 전 항목 오탐이 되므로 대조를 건너뛴다(이미 ERROR 로 끊긴 상태).
  if (baseUsable) for (const i of items) {
    const rid = i.verify?.runId;
    if (rid && !known.has(rid))
      err(`${i.id}: verify.runId(${rid}) 에 해당하는 원장이 ops/runs 에 없음 — 근거 추적 불가(검사 #6이 날짜 불일치로 건너뛰는 사각)`);
  }
}

console.log(`\nRESULT: ${E?'FAIL':'PASS'} (errors ${E}, warnings ${W})`);
process.exit(E?1:0);
