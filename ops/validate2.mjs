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
//     **근거 인정 경로(2026-09-01 개정, 단일)** — searches[] 중 region·axis 가 그 셀이고 **query 가 그 셀의
//     사전 정의 queries 에 있는 것**만 근거다. 종전의 두 경로(axis 선언만으로 인정 / itemsCovered 파생)는
//     폐지했다. 그 경로들은 특정 항목을 지목한 재검증 쿼리로도 lastSwept 를 전진시켰고(2026-09-01 실측 19셀),
//     훑지 않은 셀이 최신으로 찍히면 RD-3 로테이션(오래된 순 + gap 우선)에서 뒤로 밀려 공백이 굳는다.
//     따라서 **사전 정의 queries 가 없는 셀은 스윕될 수 없다** — 별도 집계 경고로 표면화한다.
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
    // i2c(항목→셀)는 **구 규칙 분기에서만** 쓴다. strict(2026-09-01 이후) 원장에서는 만들고 버리게 된다.
    let i2c = null;
    const buildI2c = () => {
      if (i2c) return i2c;
      i2c = new Map();
      for (const c of cov2.cells ?? []) for (const x of c.items ?? []) {
        if (!i2c.has(x)) i2c.set(x, []);
        i2c.get(x).push(`${c.region}/${c.axis}`);
      }
      return i2c;
    };
    // 스윕 근거는 **셀의 사전 정의 queries 를 실제로 돌린 검색**만 인정한다(RUNBOOK §셀 운영 — 쿼리는
    // 현 항목과 무관하게 셀에 사전 정의). 종전에는 region+axis 를 선언하기만 하면 근거가 됐고
    // itemsCovered 로도 파생시켜서, 특정 항목을 지목한 재검증 쿼리로 lastSwept 가 전진했다
    // (2026-09-01 실측 19셀). 훑지 않은 셀이 최신으로 찍히면 RD-3 로테이션에서 뒤로 밀려 공백이 굳는다.
    // **도입일 경계** — 이 근거 규칙은 2026-09-01 부터다. 그 이전 원장은 구 규칙(axis 선언 / itemsCovered
    // 파생)으로 작성됐으므로 소급 적용하면 과거 원장이 전부 FAIL 한다(실측: 2026-08-31 원장 33셀).
    // CI 는 변경된 원장 전부를 검증하므로, 소급 적용은 과거 원장을 건드리는 모든 PR 을 막아버린다.
    const EVIDENCE_RULE_FROM = '2026-09-01';
    const strict = rd2 >= EVIDENCE_RULE_FROM;
    const predef = new Map();
    for (const c of cov2.cells ?? []) predef.set(`${c.region}/${c.axis}`, new Set(c.queries ?? []));
    const ev = new Set();
    for (const s of run2.searches ?? []) {
      if (s.region && s.axis) {
        const key = `${s.region}/${s.axis}`;
        // 신규 규칙: 셀의 사전 정의 queries 를 실제로 돌린 검색만 근거.
        if (!strict || (predef.get(key) ?? new Set()).has(s.query)) ev.add(key);
        // **축을 선언한 검색은 그 셀만 근거다.** 구 규칙에서도 그랬다 — 여기서 continue 하지 않으면
        // 아래 itemsCovered 파생으로 흘러가 다중 셀 소속 항목이 다른 축까지 근거를 만든다
        // (실측: 2026-08-31 원장 33셀 → 35셀, CN/upstream·EU/recycle 추가). 재작성 때 잃은 continue 다.
        continue;
      }
      if (strict) continue;
      // 구 규칙(2026-09-01 이전 원장 한정): itemsCovered 파생도 근거로 인정했다.
      for (const x of s.itemsCovered ?? []) for (const k of buildI2c().get(x) ?? []) ev.add(k);
    }
    if (!strict) {
      for (const p of run2.primaryDocs ?? [])
        for (const x of p.itemsCovered ?? []) for (const k of buildI2c().get(x) ?? []) ev.add(k);
      warn(`스윕 근거 규칙 — 원장 날짜(${rd2})가 신규 규칙 도입일(${EVIDENCE_RULE_FROM}) 이전이라 구 규칙(axis 선언·itemsCovered 파생)으로 대조했다`);
    }
    let stamped = 0, missing = 0;
    for (const c of cov2.cells ?? []) {
      if (c.lastSwept !== rd2) continue;
      stamped++;
      const k = `${c.region}/${c.axis}`;
      // 사전 정의 쿼리가 RUNBOOK 최소치(3개) 미만인 셀은 스탬프 자체를 인정하지 않는다.
      // #13의 근거 규칙은 "셀의 queries 에 있는 쿼리"인데 queries 는 같은 커밋에서 덧붙일 수 있어
      // 자기인증이 가능하다(리뷰 실측: 재검증 쿼리 30개를 셀에 밀어넣으면 철회했던 19셀이 초록불 복귀).
      // 최소 3개를 요구하면 스탬프를 세우려면 셀 단위 쿼리 세트를 실제로 설계해야 한다.
      if (strict && (predef.get(k) ?? new Set()).size < 3) {
        missing++;
        err(`coverage ${k}: lastSwept=${rd2} 인데 사전 정의 queries 가 ${(predef.get(k) ?? new Set()).size}개 — RUNBOOK 은 셀당 3~6개를 요구한다(쿼리를 스탬프와 같은 커밋에 끼워 넣는 자기인증 차단)`);
        continue;
      }
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
    } else if (!known.size) {
      // 파일은 있는데 전부 깨졌거나 runId 가 없는 경우. scanned>0 만 보면 baseUsable 이 true 로 남아
      // 전 항목이 고아로 걸린다(실측 187줄). 기준 집합이 비었다는 것 자체가 '못 만든 것'이다.
      baseUsable = false;
      err(`${dir}: 유효한 runId 를 하나도 수집하지 못함 — 기준 집합이 비어 항목별 대조가 전부 오탐이 된다`);
    }
  } catch(e) {
    baseUsable = false;
    err(`${dir} 스캔 실패(${e.message}) — runId 실재 대조를 수행할 수 없다. 저장소 루트에서 실행할 것`);
  }
  // 기준 집합이 부분적으로 깨진 경우(파싱 실패 일부)에는 대조를 계속한다 — 위에서 이미 ERROR 를 올렸다.
  // 기준 집합이 통째로 없는 경우에는 전 항목 오탐이 되므로 대조를 건너뛴다(이미 ERROR 로 끊긴 상태).
  if (baseUsable) for (const i of items) {
    if (!i.verify) continue;                     // verify 자체가 없는 항목은 다른 검사 관할
    const rid = i.verify.runId;
    // **runId 가 비면 건너뛰지 않는다.** 현 188건 전부 runId 를 갖고 있어 하위호환 사유가 없고,
    // 건너뛰면 필드를 지우는 것만으로 #15·#20 을 동시에 우회할 수 있다(6차 리뷰 지적).
    if (!rid) { err(`${i.id}: verify 에 runId 없음 — 근거 추적 불가(필드 제거로 #15·#20 을 동시에 우회할 수 있다)`); continue; }
    if (!known.has(rid))
      err(`${i.id}: verify.runId(${rid}) 에 해당하는 원장이 ops/runs 에 없음 — 근거 추적 불가(검사 #6이 날짜 불일치로 건너뛰는 사각)`);
  }
}


// 16) effectiveDate ↔ dt 등장 대조 (WARN)
//     dt 를 통째로 재작성하면서 원래 시행일을 지우는 사고가 있다. 2026-09-01 도입 계기: KR-022 의
//     연혁을 보강하다 dt 를 새로 써서 `2020.04.01 시행`(effectiveDate 와 짝) 과 기본계획 항목을 지웠고,
//     게이트 4종이 전부 통과시켰다. **보강은 덧붙이는 것이지 덮어쓰는 것이 아니다.**
//     dt 는 자유 서술이라 표기가 갈릴 수 있어 ERROR 가 아니라 WARN 으로 둔다.
for (const i of items) {
  const eff = i.effectiveDate, dt = i.dt;
  if (typeof eff !== 'string' || eff.length !== 10 || typeof dt !== 'string' || !dt) continue;
  const [y,m,d] = eff.split('-');
  const forms = [eff, `${y}.${m}.${d}`, `${y}.${+m}.${+d}`, `${y}년 ${+m}월 ${+d}일`];
  if (!forms.some(f => dt.includes(f)))
    warn(`${i.id}: effectiveDate(${eff})가 dt 에 없음 — dt 재작성 중 시행일이 지워졌을 수 있다`);
}

// 17) checkNote 같은 run 단락 중복 부착 (ERROR)
//     한 run 안에서 항목을 두 번 손대면 `**YYYY-MM-DD RD**` 단락이 겹쳐 붙어 감사 이력이 중복된다.
for (const i of items) {
  const cn = i.checkNote;
  if (typeof cn !== 'string') continue;
  const seen = new Map();
  // **날짜가 아니라 헤더 문자열로 센다.** 종전 패턴(`**YYYY-MM-DD RD**` 정확형)은 실제 표기의
  // 6.8%(29/428)만 덮었다. 그렇다고 날짜 단위로 넓히면 안 된다 — 하루에 여러 단락이 붙는 것은
  // 정상 이력이다(`**2026-08-29 재개 run:**` `**2026-08-29 정정 1차:**` `**2026-08-29 Claire 승인:**`).
  // 날짜로 넓힌 시안은 실측 59건이 전부 오탐이었다. 중복의 신호는 같은 헤더가 두 번 나오는 것이다.
  for (const m of cn.matchAll(/\*\*\s*(\d{4}-\d{2}-\d{2}[^*]{0,60}?)\s*\*\*/g)) {
    const key = m[1].trim().replace(/[:\uFF1A\-\u2014\s]+$/, '');
    seen.set(key, (seen.get(key) ?? 0) + 1);
  }
  for (const [hdr, n] of seen)
    if (n > 1) err(`${i.id}.checkNote: 단락 헤더 "${hdr}" 가 ${n}번 붙음 — 같은 run 에서 중복 부착됐다`);
}

// 18) 원장 승인 큐 ↔ 실제 status 정합 (ERROR, 원장 있을 때만)
//     `[status] XX-000 A → B` 형태의 큐 항목은 데이터가 아직 A 여야 한다. 이미 B 로 바꿔놓고 큐에만
//     남겨두면 승인 없이 반영된 것을 큐가 가려준다(승인 게이트 우회).
if (runPath) {
  try {
    const r3 = JSON.parse(readFileSync(runPath,'utf8'));
    // **현 스냅샷을 서술하는 원장만 대조한다.** 과거 원장의 승인 큐는 이력이다 — 그때 대기였던 항목이
    // 이후 run 에서 승인·반영됐으면 현재 status 와 어긋나는 것이 정상이고, 소급 대조하면 오탐이 된다
    // (실측: 2026-08-31 원장의 CN-011 대기 항목).
    const snap3 = (tj.meta?.dataSnapshotDate ?? '').slice(0,10);
    if (!snap3 || r3.date !== snap3) throw { skip: true };
    const byId = new Map(items.map(i => [i.id, i]));
    for (const a of r3.approvalQueueCandidates ?? []) {
      // **완료·대기를 모두 파싱한다.** 종전에는 완료 항목을 파싱 전에 건너뛰어, 승인된 목표값에서
      // status 를 다시 바꿔도 통과했다(5차 리뷰 지적). 완료는 to, 대기는 from 이 현재 status 여야 한다.
      // **표시명이 아니라 필드를 본다.** 종전에는 [status] 접두를 파싱해서, KR-020 처럼 [정책판단] 으로
      // 적히고도 실제로는 WATCH → ACTIVE 를 수행하는 항목이 검사에서 통째로 빠졌다(6차 리뷰 지적).
      let id, from, to;
      const sc = a.statusChange;
      if (sc?.id && sc?.from && sc?.to) { id = sc.id; from = sc.from; to = sc.to; }
      else {
        const m = /\[[^\]]*\]\s*([A-Z]{2}-\d{3})\s+(\w+)\s*(?:→|->)\s*(\w+)/.exec(a.name ?? '');
        if (!m) continue;
        [, id, from, to] = m;
      }
      const it = byId.get(id);
      if (!it) { err(`원장 승인 큐: ${id} 가 tracker 에 없음`); continue; }
      // **판별 축을 구조화한다.** 종전에는 자유 서술 decision 에 대한 정규식이라,
      // "승인 완료" 나 "반영함" 으로 적거나 필드를 빼면 완료 건이 대기 분기로 떨어져 오탐을 냈다.
      if (a.applied !== undefined && typeof a.applied !== 'boolean')
        err(`원장 승인 큐 ${id}: applied 는 boolean 이어야 한다(현재 ${typeof a.applied})`);
      const done = typeof a.applied === 'boolean'
        ? a.applied
        : /반영\s*완료|적용\s*완료|승인\s*완료|applied/i.test(a.decision ?? '');
      if (done) {
        if (it.s !== to)
          err(`원장 승인 큐: ${id} 는 ${to} 로 승인·반영 완료로 기록됐는데 현재 status 가 ${it.s} — 승인 결과가 되돌려졌다`);
      } else if (it.s === to) {
        err(`원장 승인 큐: ${id} 가 이미 ${to} 인데 큐에 ${from} → ${to} 대기로 남아 있음 — 승인 없이 반영됐거나 큐가 낡았다`);
      } else if (it.s !== from) {
        err(`원장 승인 큐: ${id} 현재 status(${it.s})가 큐 기재(${from} → ${to})와 불일치`);
      }
    }
  } catch(e){ if (!e?.skip) err('승인 큐 정합 대조 실패: '+e.message); }
}


// 19) 검색 선언 축 ↔ coverage 항목 매핑 정합 (ERROR, 원장 있을 때만)
//     검사 #13은 검색이 선언한 (region, axis) 를 그대로 믿는다. 그래서 축을 잘못 적으면 훑지 않은 셀이
//     스윕된 것으로 올라간다. 2026-09-01 도입 계기: 항목 재검증 30건 중 10건의 축이 그 항목이 실제로
//     속한 셀과 달랐고, KR/next_tech·EU/next_tech 같은 gap 셀이 허위로 전진했다.
if (runPath) {
  try {
    const r4 = JSON.parse(readFileSync(runPath,'utf8'));
    const cv4 = JSON.parse(readFileSync(process.env.COV_PATH ?? 'ops/coverage.json','utf8'));
    const home = new Map();
    for (const c of cv4.cells ?? []) for (const it of c.items ?? []) {
      if (!home.has(it)) home.set(it, []);
      home.get(it).push(`${c.region}/${c.axis}`);
    }
    for (const s of r4.searches ?? []) {
      if (!s.region || !s.axis) continue;
      const its = s.itemsCovered ?? [];
      if (!its.length) continue;                       // 순수 발굴 검색은 대상 아님
      // **항목별로** 대조한다. 합집합으로 보면 여러 항목을 덮는 검색에서 한 항목만 맞아도 통과해
      // 나머지 항목의 축 오류가 묻힌다(4차 리뷰 지적).
      const decl = `${s.region}/${s.axis}`;
      const mapped = its.filter(x => (home.get(x) ?? []).length);
      if (!mapped.length) continue;
      const hit = mapped.filter(x => home.get(x).includes(decl));
      const missIt = mapped.filter(x => !home.get(x).includes(decl));
      if (!hit.length)
        err(`원장 검색 축 불일치: ${mapped.join(',')} 는 ${[...new Set(mapped.flatMap(x=>home.get(x)))].join(' | ')} 에 속하는데 검색은 ${decl} 로 선언 — 훑지 않은 셀이 스윕으로 올라간다`);
      else if (missIt.length)
        // RUNBOOK 이 다항목 검색을 허용하므로 축이 갈리는 것 자체는 오류가 아니다. 다만 선언 축 밖의
        // 항목은 그 항목의 셀에 대한 근거가 아니라는 점을 남긴다.
        warn(`원장 검색 축 부분 불일치: ${missIt.join(',')} 는 ${decl} 밖(${[...new Set(missIt.flatMap(x=>home.get(x)))].join(' | ')}) — 해당 셀의 스윕 근거로는 쓰이지 않는다`);
    }
  } catch(e){ err('검색 축 정합 대조 실패: '+e.message); }
}

// 20) verify.runId 의 원장 날짜 ↔ verify.date 일치 (ERROR)
//     #15는 runId 가 실재하는지만 본다. 실재하는 다른 날짜의 원장을 가리켜도 통과하므로,
//     검사 #6이 건너뛰는 날짜 불일치 경로에서 여전히 근거 없는 스탬프가 살아남는다.
{
  const dir = 'ops/runs';
  const dateOf = new Map();
  try {
    for (const f of readdirSync(dir)) {
      if (!f.endsWith('.json')) continue;
      try {
        const j = JSON.parse(readFileSync(`${dir}/${f}`,'utf8'));
        if (!j.runId) continue;
        // date 가 없으면 맵에 넣지 않는다. 넣으면 undefined 가 되어 이 runId 를 가리키는 스탬프가
        // if (d0 && ...) 에서 조용히 통과하고, #15는 runId 를 known 으로 보아 존재 검사까지 빠져나간다.
        if (!j.date) { err(`ops/runs/${f}: date 필드 없음 — 이 원장을 가리키는 스탬프가 날짜 대조를 통째로 빠져나간다`); continue; }
        if (dateOf.has(j.runId)) err(`ops/runs: runId ${j.runId} 가 파일 여럿에 중복 — 날짜 대조가 모호해진다`);
        dateOf.set(j.runId, j.date);
      } catch(e) { /* #15가 이미 ERROR 로 보고한다 */ }
    }
  } catch(e) { /* #15가 이미 ERROR 로 보고한다 */ }
  if (dateOf.size) for (const i of items) {
    const v = i.verify; if (!v?.runId) continue;  // runId 부재는 #15가 ERROR 로 보고한다
    // **date 가 없으면 건너뛰지 않는다.** #6은 lastChecked 로 폴백하므로 date 를 지우면 이 대조만 빠져나간다.
    if (!v.date) { err(`${i.id}: verify 에 date 없음 — 원장 날짜 대조를 빠져나간다(#6은 lastChecked 로 폴백)`); continue; }
    const d0 = dateOf.get(v.runId);
    if (d0 && d0 !== v.date)
      err(`${i.id}: verify.date(${v.date}) ≠ 원장 ${v.runId} 의 date(${d0}) — 실재하지만 무관한 원장을 가리킨다`);
  }
}


// 21) 원장 파생값 ↔ tracker 실측 정합 (ERROR, 스냅샷 날짜가 일치하는 원장에 한해)
//     verifyCounts·statusDistribution 은 데이터에서 파생되는 값인데 손으로 적히면 반드시 낡는다.
//     2026-09-01 도입 계기: 승인 5건을 반영하고 파생값을 재생성하지 않아 187/28/구 status 분포가 남았고,
//     같은 run 안에서 이 유형이 두 번 났다. 과거 원장은 그때의 상태를 담으므로 대조 대상이 아니다 —
//     tracker 의 dataSnapshotDate 와 run.date 가 같은, 즉 **현 스냅샷을 서술하는 원장**만 검사한다.
if (runPath) {
  try {
    const r5 = JSON.parse(readFileSync(runPath,'utf8'));
    const snap = (tj.meta?.dataSnapshotDate ?? '').slice(0,10);
    if (snap && r5.date === snap) {
      const realTotal = items.length;
      const realStatus = {};
      for (const i of items) realStatus[i.s] = (realStatus[i.s] ?? 0) + 1;
      const realRun = {};
      for (const i of items) {
        const rid = i.verify?.runId, mth = i.verify?.method;
        if (rid === r5.runId && mth) realRun[mth] = (realRun[mth] ?? 0) + 1;
      }
      const vcTotal = Object.values(realRun).reduce((a,b)=>a+b,0);
      // **필드 부재를 통과로 두지 않는다.** 조건부 비교만 하면 현 스냅샷 원장이 필드를 지우는 것만으로
      // 이 게이트를 통째로 우회한다(6차 리뷰 지적).
      const vc = r5.verifyCounts ?? {};
      if (vc.totalItems === undefined) err('원장 verifyCounts.totalItems 없음 — 파생값 정합 대조를 우회한다');
      else if (vc.totalItems !== realTotal)
        err(`원장 verifyCounts.totalItems(${vc.totalItems}) ≠ tracker 실측(${realTotal}) — 파생값이 낡았다`);
      if (vc.thisRunTotal === undefined) err('원장 verifyCounts.thisRunTotal 없음 — 파생값 정합 대조를 우회한다');
      else if (vc.thisRunTotal !== vcTotal)
        err(`원장 verifyCounts.thisRunTotal(${vc.thisRunTotal}) ≠ tracker 실측(${vcTotal}) — 파생값이 낡았다`);
      // **축별 집계와 carriedOver 도 대조한다.** 종전에는 합만 봐서 thisRun 의 method 분포를
      // {secondary:29} 로 바꿔도, carriedOver 를 아무 값으로 적어도 통과했다.
      const tr = vc.thisRun;
      if (!tr) err('원장 verifyCounts.thisRun 없음 — 축별 집계 대조를 우회한다');
      else {
        for (const m of new Set([...Object.keys(tr), ...Object.keys(realRun)]))
          if ((tr[m] ?? 0) !== (realRun[m] ?? 0))
            err(`원장 verifyCounts.thisRun.${m}(${tr[m] ?? 0}) ≠ tracker 실측(${realRun[m] ?? 0}) — 파생값이 낡았다`);
      }
      if (vc.carriedOver === undefined) err('원장 verifyCounts.carriedOver 없음 — 파생값 정합 대조를 우회한다');
      else if (vc.carriedOver !== realTotal - vcTotal)
        err(`원장 verifyCounts.carriedOver(${vc.carriedOver}) ≠ 실측(${realTotal - vcTotal}) — 파생값이 낡았다`);
      const sd = r5.statusDistribution;
      if (!sd) err('원장 statusDistribution 없음 — 파생값 정합 대조를 우회한다');
      if (sd) {
        const keys = new Set([...Object.keys(sd), ...Object.keys(realStatus)]);
        for (const k of keys) if ((sd[k] ?? 0) !== (realStatus[k] ?? 0))
          err(`원장 statusDistribution.${k}(${sd[k] ?? 0}) ≠ tracker 실측(${realStatus[k] ?? 0}) — 파생값이 낡았다`);
      }
      const cs = r5.coverageStamped?.count;
      if (cs === undefined) err('원장 coverageStamped.count 없음 — 스윕 셀 수 대조를 우회한다');
      if (cs !== undefined) {
        const realStamp = (JSON.parse(readFileSync(process.env.COV_PATH ?? 'ops/coverage.json','utf8')).cells ?? [])
          .filter(c => c.lastSwept === r5.date).length;
        if (cs !== realStamp)
          err(`원장 coverageStamped.count(${cs}) ≠ coverage 실측(${realStamp}) — 스윕 셀 수가 낡았다`);
      }
    }
  } catch(e){ err('원장 파생값 정합 대조 실패: '+e.message); }
}


// 22) meta.dataSnapshotDate 필수 + coverage 사전 정의 쿼리 분포 (ERROR / WARN)
//     #18·#21 은 tj.meta.dataSnapshotDate === run.date 를 자기 실행 조건으로 삼는데, 그 필드의
//     존재를 요구하는 게이트가 어디에도 없었다. 필드 한 줄을 지우면 두 검사가 통째로 꺼진다
//     (리뷰 실측: 승인 결과를 되돌린 상태에서 FAIL 3 → 필드 삭제 시 PASS 0).
//     #21 이 스스로 세운 원칙(필드 부재를 통과로 두지 않는다)을 tracker 쪽에도 적용한다.
{
  const snap = tj.meta?.dataSnapshotDate;
  if (!snap) err('meta.dataSnapshotDate 없음 — 이 필드가 없으면 검사 #18·#21 이 조용히 꺼진다');
  else if (!/^\d{4}-\d{2}-\d{2}$/.test(String(snap)))
    err(`meta.dataSnapshotDate(${snap}) 형식 불량 — YYYY-MM-DD 여야 #18·#21 이 작동한다`);
}
//     coverage 쿼리 분포 — RUNBOOK 은 셀당 3~6개를 요구한다. 종전 경고는 0개 셀만 세어
//     실제 미달 규모를 축소 보고했고(27 vs 84), 원장이 있을 때만 나왔다.
try {
  const cv6 = JSON.parse(readFileSync(process.env.COV_PATH ?? 'ops/coverage.json','utf8'));
  const cells = cv6.cells ?? [];
  const dist = new Map();
  for (const c of cells) { const n = (c.queries ?? []).length; dist.set(n, (dist.get(n) ?? 0) + 1); }
  const under = cells.filter(c => (c.queries ?? []).length < 3).length;
  const zero  = cells.filter(c => !(c.queries ?? []).length).length;
  if (under) warn(`coverage 사전 정의 쿼리 미달 ${under}/${cells.length}셀 (0개 ${zero}셀 포함) — RUNBOOK 은 셀당 3~6개를 요구하며, 미달 셀은 검사 #13이 스탬프를 거부한다. 분포 ${[...dist].sort((a,b)=>a[0]-b[0]).map(([k,v])=>`${k}개:${v}셀`).join(' ')}`);
  // _meta 에 손으로 적힌 집계가 있으면 실측과 대조한다(이 PR 이 금지한 하드코딩 파생값).
  const hard = cv6._meta?.cellsWithoutPredefinedQueries?.count;
  if (hard !== undefined && hard !== zero)
    err(`coverage _meta.cellsWithoutPredefinedQueries.count(${hard}) ≠ 실측(${zero}) — 손으로 적힌 파생값이 낡았다`);
} catch(e){ err('coverage 쿼리 분포 대조 실패: '+e.message); }

console.log(`\nRESULT: ${E?'FAIL':'PASS'} (errors ${E}, warnings ${W})`);
process.exit(E?1:0);
