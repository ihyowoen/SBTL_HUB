import fs from 'node:fs';

const src = JSON.parse(fs.readFileSync('data/cards.full.json','utf8'));
const cards = Array.isArray(src) ? src : (Array.isArray(src.cards) ? src.cards : []);
const idOf = (c) => String(c?.id || c?.news_id || c?.draft_id || c?.url || (Array.isArray(c?.urls) ? c.urls[0] : '') || '').trim();
const dateOf = (c) => String(c?.date || c?.d || '').slice(0,10);
const titleOf = (c) => String(c?.title || c?.T || '').trim();
const regionOf = (c) => String(c?.region || c?.r || '').trim();
const signalOf = (c) => String(c?.signal || c?.s || '').trim();
const sourceOf = (c) => String(c?.source || c?.src || '').trim();
const urlsOf = (c) => Array.isArray(c?.urls) ? c.urls.filter(Boolean).map(String) : (c?.url ? [String(c.url)] : []);
const arr = (v) => Array.isArray(v) ? v : [];
const relatedIdsOf = (c) => {
  const out = new Set();
  for (const v of arr(c?.related)) {
    if (typeof v === 'string') out.add(v);
    else if (v && typeof v === 'object') {
      for (const k of ['id','card_id','related_id','target_id']) if (v[k]) out.add(String(v[k]));
    }
  }
  for (const v of arr(c?.related_lineage?.related_ids)) out.add(String(v));
  for (const v of arr(c?.related_lineage)) if (typeof v === 'string') out.add(v);
  return [...out].filter(Boolean);
};
const compact = (c) => ({
  id: idOf(c), date: dateOf(c), title: titleOf(c), region: regionOf(c), signal: signalOf(c), source: sourceOf(c),
  fact: c?.fact ?? c?.summary ?? c?.sub ?? '',
  implication: c?.implication ?? c?.g ?? '',
  gate: c?.gate ?? '',
  tags: c?.tags ?? c?.themes ?? c?.theme ?? [],
  urls: urlsOf(c),
  related_ids: relatedIdsOf(c),
  value: c?.value ?? c?.news_value ?? c?.score ?? c?.importance ?? null,
  status: c?.status ?? c?.stage ?? null,
});
const august = cards.filter(c => dateOf(c).startsWith('2026-08-'));
const augIds = new Set(august.map(idOf));
const sep = cards.filter(c => dateOf(c) >= '2026-09-01' && dateOf(c) <= '2026-09-09');
const sepFollow = sep.filter(c => relatedIdsOf(c).some(id => augIds.has(id)) || [...augIds].some(id => relatedIdsOf(cards.find(x => idOf(x)===id) || {}).includes(idOf(c))));
const countBy = (xs, fn) => Object.fromEntries([...xs.reduce((m,x)=>{const k=fn(x)||'(blank)';m.set(k,(m.get(k)||0)+1);return m;},new Map())].sort((a,b)=>b[1]-a[1]||a[0].localeCompare(b[0])));
const keys = countBy(cards.slice(0,Math.min(cards.length,500)), c => Object.keys(c||{}).sort().join('|'));
const report = {
  schema:'monthly_brief_universe_extract_v1',
  baseline:{main_commit_sha:process.env.GITHUB_SHA || null, full_blob_sha:process.env.FULL_BLOB_SHA || null, total_cards:cards.length},
  month:'2026-08',
  counts:{august:august.length, sep_1_9:sep.length, sep_followups_to_august:sepFollow.length},
  august_distribution:{region:countBy(august,regionOf), signal:countBy(august,signalOf), source:countBy(august,sourceOf)},
  observed_key_shapes:Object.keys(keys).slice(0,20),
  august_cards:august.map(compact).sort((a,b)=>a.date.localeCompare(b.date)||a.id.localeCompare(b.id)),
  september_followups:sepFollow.map(compact).sort((a,b)=>a.date.localeCompare(b.date)||a.id.localeCompare(b.id)),
};
fs.mkdirSync('tmp',{recursive:true});
fs.writeFileSync('tmp/monthly_brief_2026-08_universe.json', JSON.stringify(report,null,2)+'\n');
console.log(JSON.stringify({august:august.length,sep:sep.length,sepFollow:sepFollow.length,total:cards.length},null,2));
