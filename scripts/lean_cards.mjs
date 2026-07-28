#!/usr/bin/env node
// cards.json lean export — 앱이 읽는 필드만 남겨 발행본을 가볍게 한다.
//
// 왜: 파이프라인이 단계마다 남기는 QC 메타데이터(publish_ready·github_main_sync_passed·
// prompt_0_5R_before_hash·related_lineage·date_role 등 700종 가까이)가 발행본에 그대로
// 실려 파일의 절반을 차지한다. 앱은 하나도 읽지 않는데 모든 사용자가 매번 내려받는다.
//
// 원본은 버리지 않는다 — data/cards.full.json에 통째로 보존한다(빌드에 포함되지 않는
// 저장소 경로라 배포 용량과 무관). 계약 검증·감사·리뷰는 그 파일을 본다.
//
// KEEP 15: 전수 대조(703필드 × src/api/lib 32파일)로 확정. source_tier는
// buildCardConsultContext가 읽으므로 발행 14필드에 더한다.
//
// Usage:
//   node scripts/lean_cards.mjs           # 변환 적용(원본 → data/cards.full.json)
//   node scripts/lean_cards.mjs --check   # 위반만 보고(쓰지 않음, 위반 시 exit 1)
//   node scripts/lean_cards.mjs --dry     # 미리보기
import { readFileSync, writeFileSync, mkdirSync, existsSync } from "node:fs";
import { dirname } from "node:path";

const KEEP = [
  "id", "region", "date", "cat", "sub_cat", "signal", "title", "sub",
  "gate", "fact", "implication", "urls", "related", "fact_sources", "source_tier",
];
const LEAN_PATH = "public/data/cards.json";
const FULL_PATH = "data/cards.full.json";

const args = process.argv.slice(2);
const CHECK = args.includes("--check");
const DRY = args.includes("--dry");

if (!existsSync(LEAN_PATH)) { console.error(`FAIL: ${LEAN_PATH} 없음`); process.exit(1); }
const raw = readFileSync(LEAN_PATH, "utf8");
let doc;
try { doc = JSON.parse(raw); } catch (e) { console.error(`FAIL: JSON 파싱 — ${e.message}`); process.exit(1); }
const cards = Array.isArray(doc.cards) ? doc.cards : null;
if (!cards) { console.error("FAIL: cards 배열 없음"); process.exit(1); }

const keepSet = new Set(KEEP);
const extraFields = new Set();
let dirty = 0;
for (const c of cards) {
  const extras = Object.keys(c).filter((k) => !keepSet.has(k));
  if (extras.length) { dirty++; extras.forEach((k) => extraFields.add(k)); }
}

const before = Buffer.byteLength(raw);
const leanCards = cards.map((c) => {
  const o = {};
  for (const k of KEEP) if (c[k] !== undefined) o[k] = c[k];
  return o;
});
const leanDoc = { ...doc, cards: leanCards };
const out = JSON.stringify(leanDoc);
const after = Buffer.byteLength(out);

console.log(`카드 ${cards.length}장 · 발행 외 필드를 가진 카드 ${dirty}장 · 제거 대상 필드 ${extraFields.size}종`);
console.log(`크기 ${(before / 1048576).toFixed(2)}MB → ${(after / 1048576).toFixed(2)}MB (${Math.round((1 - after / before) * 100)}% 감소)`);

if (CHECK) {
  if (dirty) {
    console.error(`\nFAIL: 발행본에 파이프라인 메타데이터가 남아 있다 — 'node scripts/lean_cards.mjs'로 정리할 것`);
    console.error(`예: ${[...extraFields].slice(0, 8).join(", ")}${extraFields.size > 8 ? " 외" : ""}`);
    process.exit(1);
  }
  console.log("\nPASS: 발행본이 KEEP 15로 정리돼 있다");
  process.exit(0);
}

if (!dirty) { console.log("\n이미 정리돼 있음 — 변경 없음"); process.exit(0); }
if (DRY) { console.log("\n(--dry: 쓰지 않음)"); process.exit(0); }

// 원본 보존이 먼저 — 이 순서가 뒤집히면 되돌릴 수 없다
mkdirSync(dirname(FULL_PATH), { recursive: true });
writeFileSync(FULL_PATH, raw);
const verify = JSON.parse(readFileSync(FULL_PATH, "utf8"));
if (!Array.isArray(verify.cards) || verify.cards.length !== cards.length) {
  console.error(`FAIL: 원본 보존 검증 실패 — ${FULL_PATH}를 확인할 것. 발행본은 건드리지 않았다`);
  process.exit(1);
}
writeFileSync(LEAN_PATH, out);
console.log(`\n완료: 원본 → ${FULL_PATH} (${cards.length}장) · 발행본 → ${LEAN_PATH} (KEEP ${KEEP.length})`);
