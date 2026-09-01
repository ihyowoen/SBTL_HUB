#!/usr/bin/env node
// coverage 쿼리 선행성 판정 — 같은 셀에서 queries 추가와 lastSwept 전진이 한 PR 에 함께 일어나면 실패.
//
// 왜 CI 층위인가: 검사 #13은 "셀의 사전 정의 queries 에 있는 쿼리"만 스윕 근거로 인정하는데,
// queries 는 작성자 소유라 스탬프와 같은 PR 에서 끼워 넣으면 자기인증이 된다(실측: 철회한 19셀이
// 그대로 복귀). validator 는 git 이력을 볼 수 없으므로 선행성은 여기서만 강제할 수 있다.
//
// 왜 diff 라인이 아니라 셀 단위 비교인가: `^\+\s+"..."` 같은 라인 휴리스틱은 itemVerifyQueries·
// cells 등 다른 문자열 배열의 원소 추가까지 세어 오탐을 낸다(실측 27행). 두 스냅샷을 파싱해
// 셀별로 대조하면 정확하다.
//
// 사용: node ops/check_query_precedence.mjs <base.json> <head.json>
import { readFileSync } from 'fs';

const load = (p) => {
  const cells = new Map();
  for (const c of (JSON.parse(readFileSync(p, 'utf8')).cells ?? []))
    cells.set(`${c.region}/${c.axis}`, { q: new Set(c.queries ?? []), sw: c.lastSwept ?? null });
  return cells;
};
const [basePath, headPath] = process.argv.slice(2);
if (!basePath || !headPath) { console.error('usage: check_query_precedence.mjs <base.json> <head.json>'); process.exit(2); }

const base = load(basePath), head = load(headPath);
const bad = [];
for (const [k, h] of head) {
  const b = base.get(k) ?? { q: new Set(), sw: null };
  const added = [...h.q].filter(x => !b.q.has(x));
  const advanced = h.sw && h.sw !== b.sw;
  if (added.length && advanced) bad.push({ k, added, from: b.sw ?? '없음', to: h.sw });
}
if (bad.length) {
  console.error('FAIL: 같은 셀에서 queries 추가와 lastSwept 전진이 한 PR 에 함께 일어났다.');
  console.error('      검사 #13의 근거 규칙이 자기인증된다 — 사전 정의 쿼리는 스윕보다 앞선 PR 에서 채울 것.');
  for (const x of bad)
    console.error(`      ${x.k}: lastSwept ${x.from} → ${x.to} · 신규 queries ${x.added.length}개 [${x.added.map(s => s.slice(0, 40)).join(' | ')}]`);
  process.exit(1);
}
console.log(`선행성 확인 — 스윕 전진 셀 ${[...head].filter(([k, h]) => h.sw && h.sw !== (base.get(k)?.sw ?? null)).length}개, 그중 동일 PR 쿼리 추가 0개`);
