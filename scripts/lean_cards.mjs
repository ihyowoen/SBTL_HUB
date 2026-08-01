#!/usr/bin/env node
// Canonical full → lean public projection.
//
// Long-term data ownership:
//   data/cards.full.json   = sole canonical card inventory and metadata source.
//   public/data/cards.json = generated application projection only.
//
// This exporter never ingests the public projection back into the canonical full and never writes
// data/cards.full.json. Canonical changes must be produced by the governed incremental operation
// path (insert/update/related_add), validated, and committed before this exporter runs.
//
// Usage:
//   node scripts/lean_cards.mjs           # generate public projection from canonical full
//   node scripts/lean_cards.mjs --check   # verify public projection exactly matches canonical full
//   node scripts/lean_cards.mjs --dry     # preview generation without writing
import { readFileSync, writeFileSync, mkdirSync, existsSync } from "node:fs";
import { dirname } from "node:path";

const KEEP = [
  "id", "region", "date", "cat", "sub_cat", "signal", "title", "sub",
  "gate", "fact", "implication", "urls", "related", "fact_sources", "source_tier",
  "related_lineage",
];

const FULL_PATH = process.env.CARDS_FULL_PATH || "data/cards.full.json";
const LEAN_PATH = process.env.CARDS_PUBLIC_PATH || "public/data/cards.json";
const keepSet = new Set(KEEP);
const args = process.argv.slice(2);
const CHECK = args.includes("--check");
const DRY = args.includes("--dry");
const unknown = args.filter((arg) => !["--check", "--dry"].includes(arg));

if (CHECK && DRY) {
  console.error("FAIL: --check와 --dry는 함께 사용할 수 없음");
  process.exit(2);
}
if (unknown.length) {
  console.error(`FAIL: 지원하지 않는 인자 ${unknown.join(", ")}`);
  process.exit(2);
}

const load = (path) => {
  const raw = readFileSync(path, "utf8");
  const doc = JSON.parse(raw);
  if (!doc || typeof doc !== "object" || Array.isArray(doc)) {
    throw new Error(`${path}: 최상위 JSON 객체 아님`);
  }
  if (!Array.isArray(doc.cards)) throw new Error(`${path}: cards 배열 없음`);
  return { raw, doc };
};

const projectCard = (card) => {
  const projected = {};
  for (const key of KEEP) {
    if (card[key] !== undefined) projected[key] = card[key];
  }
  return projected;
};

const projectDocument = (full) => ({
  ...Object.fromEntries(Object.entries(full).filter(([key]) => key !== "cards")),
  cards: full.cards.map(projectCard),
});

const sameKeep = (publicCard, fullCard) => KEEP.every((key) => {
  const publicHas = key in publicCard;
  const fullHas = key in fullCard;
  if (publicHas !== fullHas) return false;
  return !publicHas || JSON.stringify(publicCard[key]) === JSON.stringify(fullCard[key]);
});

if (!existsSync(FULL_PATH)) {
  console.error(`FAIL: canonical full 없음 — ${FULL_PATH}`);
  process.exit(1);
}

let fullLoaded;
try {
  fullLoaded = load(FULL_PATH);
} catch (error) {
  console.error(`FAIL: canonical full 파싱 — ${error.message}`);
  process.exit(1);
}

const full = fullLoaded.doc;
const projected = projectDocument(full);

const validateProjection = (publicDoc) => {
  const errors = [];
  const topKeys = new Set([
    ...Object.keys(publicDoc).filter((key) => key !== "cards"),
    ...Object.keys(full).filter((key) => key !== "cards"),
  ]);

  for (const key of topKeys) {
    const publicHas = key in publicDoc;
    const fullHas = key in full;
    if (publicHas !== fullHas) {
      errors.push(`최상위 ${key} 존재 불일치`);
      continue;
    }
    if (JSON.stringify(publicDoc[key]) !== JSON.stringify(full[key])) {
      errors.push(`최상위 ${key} 값 불일치`);
    }
  }

  if (publicDoc.cards.length !== full.cards.length) {
    errors.push(`카드 수 불일치 public ${publicDoc.cards.length} vs full ${full.cards.length}`);
  }

  const count = Math.min(publicDoc.cards.length, full.cards.length);
  for (let index = 0; index < count; index += 1) {
    const publicCard = publicDoc.cards[index];
    const fullCard = full.cards[index];
    if (publicCard.id !== fullCard.id) {
      errors.push(`순서 불일치 @${index}: public ${publicCard.id} vs full ${fullCard.id}`);
      break;
    }
    const extra = Object.keys(publicCard).filter((key) => !keepSet.has(key));
    if (extra.length) {
      errors.push(`${publicCard.id}: public에 KEEP 밖 필드 ${extra.join(",")}`);
      continue;
    }
    if (!sameKeep(publicCard, fullCard)) {
      errors.push(`${publicCard.id}: KEEP 값 불일치`);
    }
  }

  return errors;
};

if (CHECK) {
  if (!existsSync(LEAN_PATH)) {
    console.error(`FAIL: public projection 없음 — ${LEAN_PATH}`);
    process.exit(1);
  }
  let publicLoaded;
  try {
    publicLoaded = load(LEAN_PATH);
  } catch (error) {
    console.error(`FAIL: public projection 파싱 — ${error.message}`);
    process.exit(1);
  }
  const errors = validateProjection(publicLoaded.doc);
  if (errors.length) {
    errors.slice(0, 8).forEach((error) => console.error("FAIL:", error));
    if (errors.length > 8) console.error(`… 외 ${errors.length - 8}건`);
    console.error("\n'node scripts/lean_cards.mjs'로 canonical full에서 public projection을 재생성할 것");
    process.exit(1);
  }
  console.log(`PASS: public ${publicLoaded.doc.cards.length}장 ≡ canonical full 사영 (KEEP ${KEEP.length})`);
  process.exit(0);
}

let currentPublic = null;
let currentRaw = null;
if (existsSync(LEAN_PATH)) {
  try {
    const loaded = load(LEAN_PATH);
    currentPublic = loaded.doc;
    currentRaw = loaded.raw;
  } catch (error) {
    console.error(`FAIL: 기존 public projection 파싱 — ${error.message}`);
    process.exit(1);
  }
}

const output = JSON.stringify(projected);
const beforeBytes = currentRaw ? Buffer.byteLength(currentRaw) : 0;
const afterBytes = Buffer.byteLength(output);
const unchanged = currentPublic !== null && JSON.stringify(currentPublic) === JSON.stringify(projected);

console.log(`canonical full ${full.cards.length}장 → public projection KEEP ${KEEP.length}`);
console.log(`public 크기 ${(beforeBytes / 1048576).toFixed(2)}MB → ${(afterBytes / 1048576).toFixed(2)}MB`);

if (unchanged) {
  console.log("변경 없음 — public projection이 canonical full과 이미 정합");
  process.exit(0);
}
if (DRY) {
  console.log("--dry: 쓰지 않음");
  process.exit(0);
}

mkdirSync(dirname(LEAN_PATH), { recursive: true });
writeFileSync(LEAN_PATH, output);

const written = load(LEAN_PATH).doc;
const errors = validateProjection(written);
if (errors.length) {
  errors.slice(0, 8).forEach((error) => console.error("FAIL:", error));
  console.error("FAIL: 생성 후 projection 검증 실패");
  process.exit(1);
}

console.log(`완료: ${FULL_PATH}은 변경하지 않고 ${LEAN_PATH}만 재생성`);
