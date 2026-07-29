#!/usr/bin/env node
// cards.json lean export — 정본은 아카이브, 발행본은 사영(projection).
//
// 왜: 파이프라인이 단계마다 남기는 QC 메타데이터(700종 가까이)가 발행본에 실려
// 파일의 절반을 차지한다. 앱은 KEEP 16만 읽는데 모든 사용자가 매번 내려받는다.
//
// 구조(Codex #221 P1 반영 — 발행본을 원천으로 삼으면 다음 배치가 아카이브를
// 혼합본으로 덮어써 기존 카드의 메타데이터가 영구 소실된다):
//   data/cards.full.json   = 정본 아카이브(전체 필드). 계약 검증·감사·리뷰의 원천.
//   public/data/cards.json = 배치 유입함이자 발행본. 봇의 replace-all이 여기 착지하고,
//                            apply가 id 단위로 아카이브에 병합한 뒤 사영으로 재생성한다.
//
// 병합 규약(id 단위):
//   - 유입 카드에 KEEP 밖 필드가 하나라도 있으면 = 봇의 완전판 → 아카이브 항목을 교체
//   - KEEP만 있으면 = lean 편집 → 아카이브의 비KEEP 필드는 보존하고 KEEP 값만 갱신
//   - 유입에 없는 아카이브 id = 상류에서 삭제된 카드 → 아카이브도 제거(경고, 게이트가
//     삭제 자체를 별도 차단하므로 여기선 거울만 맞춘다)
//
// Usage:
//   node scripts/lean_cards.mjs           # 병합 + 사영 재생성
//   node scripts/lean_cards.mjs --check   # 발행본 ≡ 사영(아카이브) 검증(쓰지 않음)
//   node scripts/lean_cards.mjs --dry     # 미리보기
import { readFileSync, writeFileSync, mkdirSync, existsSync } from "node:fs";
import { dirname } from "node:path";

const KEEP = [
  "id", "region", "date", "cat", "sub_cat", "signal", "title", "sub",
  "gate", "fact", "implication", "urls", "related", "fact_sources", "source_tier",
  "related_lineage",
];
const LEAN_PATH = "public/data/cards.json";
const FULL_PATH = "data/cards.full.json";
const keepSet = new Set(KEEP);

const args = process.argv.slice(2);
const CHECK = args.includes("--check");
const DRY = args.includes("--dry");

const load = (p) => {
  const raw = readFileSync(p, "utf8");
  const doc = JSON.parse(raw);
  if (!Array.isArray(doc.cards)) throw new Error(`${p}: cards 배열 없음`);
  return doc;
};
const isFullRecord = (c) => Object.keys(c).some((k) => !keepSet.has(k));
const project = (c) => { const o = {}; for (const k of KEEP) if (c[k] !== undefined) o[k] = c[k]; return o; };
// 존재 여부까지 비교 — ?? 병합은 'null 값 보유'와 '필드 부재'를 동일시해 실데이터
// source_tier:null(37장)에서 발행본의 필드 삭제가 사영 정합으로 오판된다(Codex #221 R8)
const sameKeep = (a, b) => KEEP.every((k) => {
  const ha = k in a, hb = k in b;
  if (ha !== hb) return false;
  return !ha || JSON.stringify(a[k]) === JSON.stringify(b[k]);
});

if (!existsSync(LEAN_PATH)) { console.error(`FAIL: ${LEAN_PATH} 없음`); process.exit(1); }
let pub;
try { pub = load(LEAN_PATH); } catch (e) { console.error(`FAIL: ${e.message}`); process.exit(1); }

let archive = null;
if (existsSync(FULL_PATH)) {
  try { archive = load(FULL_PATH); } catch (e) { console.error(`FAIL: 아카이브 파싱 — ${e.message}`); process.exit(1); }
}

// ---- --check: 발행본이 아카이브의 KEEP 사영과 정확히 일치하는가 ----
// (발행본에 여분 필드 / 값 불일치 / id 집합 불일치 전부 실패 — 발행·감사본의 조용한
//  괴리를 잡는다. Codex #221 P2)
if (CHECK) {
  if (!archive) { console.error(`FAIL: ${FULL_PATH} 없음 — 아카이브가 정본이다. 'node scripts/lean_cards.mjs'로 생성할 것`); process.exit(1); }
  const errs = [];
  // 최상위 메타(total·updated·schema·sort 등 cards 밖 전부) — 한쪽만 고치면 실패
  const topKeys = new Set([...Object.keys(pub), ...Object.keys(archive)].filter((k) => k !== "cards"));
  for (const k of topKeys) {
    if (JSON.stringify(pub[k] ?? null) !== JSON.stringify(archive[k] ?? null)) errs.push(`최상위 ${k} 불일치 — 발행 ${JSON.stringify(pub[k]).slice(0, 40)} vs 아카이브 ${JSON.stringify(archive[k]).slice(0, 40)}`);
  }
  // 카드는 순서까지 동일해야 한다 — 앱이 kb.cards.slice(0,400)처럼 순서를 소비하므로
  // 집합 비교로는 재정렬된 발행본이 통과한다(Codex #221 R3)
  if (pub.cards.length !== archive.cards.length) errs.push(`카드 수 불일치 발행 ${pub.cards.length} vs 아카이브 ${archive.cards.length}`);
  const n = Math.min(pub.cards.length, archive.cards.length);
  for (let i = 0; i < n; i++) {
    const c = pub.cards[i], a = archive.cards[i];
    if (c.id !== a.id) { errs.push(`순서 불일치 @${i}: 발행 ${c.id} vs 아카이브 ${a.id}`); break; }
    const extra = Object.keys(c).filter((k) => !keepSet.has(k));
    if (extra.length) { errs.push(`${c.id}: 발행본에 KEEP 밖 필드 ${extra.length}개(${extra.slice(0, 3).join(",")}…) — 병합·재사영 필요`); continue; }
    if (!sameKeep(c, a)) errs.push(`${c.id}: KEEP 값이 아카이브와 다름 — 한쪽만 고쳐졌다`);
  }
  if (errs.length) {
    errs.slice(0, 6).forEach((e) => console.error("FAIL:", e));
    if (errs.length > 6) console.error(`… 외 ${errs.length - 6}건`);
    console.error(`\n'node scripts/lean_cards.mjs'로 병합·재사영할 것`);
    process.exit(1);
  }
  console.log(`PASS: 발행본 ${pub.cards.length}장 ≡ 아카이브 사영 (KEEP ${KEEP.length})`);
  process.exit(0);
}

// ---- apply: 유입(발행 경로) → 아카이브 병합 → 사영 재생성 ----
const stats = { fullMerged: 0, leanMerged: 0, inserted: 0, dropped: 0, leanNew: 0 };
let mergedCards;
if (!archive) {
  // 최초 실행 — 현재 발행 파일이 그대로 초대 아카이브가 된다
  mergedCards = pub.cards;
  stats.inserted = pub.cards.length;
} else {
  const am = new Map(archive.cards.map((c) => [c.id, c]));
  const pubIds = new Set(pub.cards.map((c) => c.id));
  mergedCards = pub.cards.map((c) => {
    const prev = am.get(c.id);
    if (!prev) { stats[isFullRecord(c) ? "inserted" : "leanNew"]++; return c; }
    // 기존 카드는 통째 교체 금지 — '비KEEP 필드가 있으면 완전판'이라는 판별은 잡키
    // 하나로 아카이브 감사 기록 전체를 날린다(Codex #221 R7 P1). 대신 키 단위 합집합:
    //   비KEEP: 유입이 가진 키는 유입 값, prev에만 있는 키는 보존(손실 원천 불가.
    //           봇이 의도적으로 지운 낡은 감사 필드가 남는 편향은 감수 — 아카이브는
    //           감사 원천이라 '손실 < 잔존'이다)
    //   KEEP:   유입본으로 정확히 교체 — 발행면이 KEEP의 표면이므로 삭제도 편집(R6)
    // prev 키 순서 보존 = 무변경 병합이 바이트 동일 = apply 멱등.
    const incomingNonKeep = Object.keys(c).filter((k) => !keepSet.has(k));
    if (incomingNonKeep.length) {
      stats.fullMerged++;
      // 풍부한 아카이브에 쥐꼬리 비KEEP만 유입 = 잡키 의심 — 막지 않고 드러낸다
      const prevNonKeep = Object.keys(prev).filter((k) => !keepSet.has(k)).length;
      if (incomingNonKeep.length <= 2 && prevNonKeep >= 10) console.log(`경고: ${c.id} 비KEEP 유입 ${incomingNonKeep.length}개(${incomingNonKeep.join(",")}) vs 아카이브 ${prevNonKeep}개 — 잡키 의심, 합집합 병합으로 기존 기록은 보존됨`);
    } else if (!sameKeep(c, prev)) stats.leanMerged++;
    const rest = { ...c };
    const merged = {};
    for (const [k, v] of Object.entries(prev)) {
      if (k in rest) { merged[k] = rest[k]; delete rest[k]; }
      else if (!keepSet.has(k)) merged[k] = v; // prev에만 있는 비KEEP은 보존
      // prev에만 있는 KEEP 키는 건너뜀 — 유입이 지운 것(삭제도 편집)
    }
    return Object.assign(merged, rest); // 유입이 새로 추가한 키
  });
  for (const c of archive.cards) if (!pubIds.has(c.id)) stats.dropped++;
}
const mergedArchive = { ...pub, cards: mergedCards };
const leanDoc = { ...pub, cards: mergedCards.map(project) };

const before = Buffer.byteLength(JSON.stringify(pub));
const after = Buffer.byteLength(JSON.stringify(leanDoc));
console.log(`유입 ${pub.cards.length}장 → 아카이브: 완전판 병합 ${stats.fullMerged} · 신규 ${stats.inserted} · lean 병합 ${stats.leanMerged} · 제거 ${stats.dropped}`);
if (stats.leanNew) console.log(`경고: 완전판 없이 lean으로만 들어온 신규 카드 ${stats.leanNew}장 — 아카이브에 감사 기록이 없다`);
console.log(`발행본 ${(before / 1048576).toFixed(2)}MB → ${(after / 1048576).toFixed(2)}MB`);

const changedArchive = !archive || JSON.stringify(mergedArchive) !== JSON.stringify(archive);
const changedLean = JSON.stringify(leanDoc) !== JSON.stringify(pub);
if (!changedArchive && !changedLean) { console.log("변경 없음 — 발행본·아카이브 이미 정합"); process.exit(0); }
if (DRY) { console.log("(--dry: 쓰지 않음)"); process.exit(0); }

// 아카이브가 먼저 — 사영을 먼저 쓰면 실패 시 원본이 남지 않는다
mkdirSync(dirname(FULL_PATH), { recursive: true });
writeFileSync(FULL_PATH, JSON.stringify(mergedArchive));
const verify = load(FULL_PATH);
if (verify.cards.length !== mergedCards.length) { console.error(`FAIL: 아카이브 검증 실패 — 발행본은 건드리지 않았다`); process.exit(1); }
writeFileSync(LEAN_PATH, JSON.stringify(leanDoc));
console.log(`완료: 아카이브 ${FULL_PATH} (${mergedCards.length}장, 전체 필드) · 발행본 ${LEAN_PATH} (KEEP ${KEEP.length})`);
