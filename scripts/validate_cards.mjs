#!/usr/bin/env node
// SBTL_HUB cards.json validator — zero dependency (node: built-ins only)
//
// 존재 이유: validate.mjs는 트래커 도메인만 지킨다. cards.json은 카드 PR이
// 무검사로 머지되는 위장 통과 상태였다(2026-07-16 사고: 1098장 파일이 6KB로
// 잘린 채 main에 22분 체류). 이 게이트는 그 계열 사고를 파싱·크기·수량·계약
// 검사로 차단한다.
//
// Usage:
//   node scripts/validate_cards.mjs                    # public/data/cards.json
//   node scripts/validate_cards.mjs path/to/cards.json
//   CARDS_BASE=path/to/base.json …                     # 기준본 명시(감소 검사)
// Exit code 1 if any ERROR (CI gate). WARNING은 막지 않는다.
//
// 레거시 동결 기준선: 과거 배치의 알려진 흠은 고치지 않고 '늘지 않음'만 지킨다.
// (id 불변 관행(R15d) 때문에 레거시 리데이팅 흔적 3건은 정상이고, 깨진 related
// 14건은 search-before-delete 정책상 의도 보존분이 섞여 있다 — 삭제 강제 금지)
import { readFileSync, statSync, existsSync } from "node:fs";
import { execSync } from "node:child_process";

const CARDS_PATH = process.argv[2] || "public/data/cards.json";
const MIN_BYTES = 2_000_000; // 현행 ~10MB — 절반 이하로 줄면 사고로 간주(6KB 사고 계열)
const MIN_CARDS = 1000;
const BROKEN_RELATED_MAX = 14; // 2026-04 레거시 동결분
const ID_DATE_MISMATCH_MAX = 3; // 레거시 리데이팅(ID 불변) 흔적 동결분
const SIGNALS = new Set(["top", "high", "mid", "info"]);
const ISO_RE = /^\d{4}-\d{2}-\d{2}$/;
const ID_DATE_RE = /^(\d{4}-\d{2}-\d{2})_/;

const errors = [];
const warns = [];
const E = (m) => errors.push(m);
const W = (m) => warns.push(m);

// 자리수만 맞는 가짜 날짜(2026-99-99)는 앱의 사전식 최신 비교(App.jsx latestFirst)에서
// 모든 정상 카드보다 새 것으로 취급돼 날짜 그룹을 오염시킨다 — 왕복 대조로 실재 확인
function isRealDate(s) {
  const v = String(s || "");
  if (!ISO_RE.test(v)) return false;
  const d = new Date(v + "T00:00:00Z");
  return !Number.isNaN(d.getTime()) && d.toISOString().slice(0, 10) === v;
}

// ---- 0) 파싱·크기 ----
if (!existsSync(CARDS_PATH)) { console.error(`FAIL: ${CARDS_PATH} 없음`); process.exit(1); }
const bytes = statSync(CARDS_PATH).size;
if (bytes < MIN_BYTES) E(`파일 ${(bytes / 1024).toFixed(0)}KB < 하한 ${(MIN_BYTES / 1048576).toFixed(0)}MB — 절단/파괴 의심`);
let doc;
try { doc = JSON.parse(readFileSync(CARDS_PATH, "utf8")); }
catch (e) { console.error(`FAIL: JSON 파싱 실패 — ${e.message}`); process.exit(1); }
const cards = Array.isArray(doc.cards) ? doc.cards : null;
if (!cards) { console.error("FAIL: cards 배열 없음"); process.exit(1); }
// total·updated는 merge-cards.yml이 d['total']·d['updated']로 직독한다 — 없으면 다음
// 페이로드 병합이 merge_cards.py 도달 전에 KeyError로 죽는다
if (!Number.isFinite(doc.total)) E(`total 필드 없음/비수치(${JSON.stringify(doc.total)})`);
else if (doc.total !== cards.length) E(`total(${doc.total}) ≠ cards.length(${cards.length})`);
if (typeof doc.updated !== "string" || !doc.updated.trim()) E(`updated 필드 없음/비문자열(${JSON.stringify(doc.updated)})`);
else if (Number.isNaN(Date.parse(doc.updated))) E(`updated 파싱 불가: "${doc.updated}"`);

// ---- 1) 기준본(있으면) — 수량 감소·신규 카드 판별 ----
// PR에선 origin/main의 파일이 기준본. push(main)에선 기준본==현재라 자동 무시.
let baseIds = null;
let baseBrokenPairs = null; // "카드id→대상id" 집합 — 숫자 상한이 아니라 '어느 엣지가' 예외인지를 동결
const baseSrc = process.env.CARDS_BASE;
try {
  const raw = baseSrc
    ? readFileSync(baseSrc, "utf8")
    : execSync("git show origin/main:public/data/cards.json", { maxBuffer: 64 * 1024 * 1024, stdio: ["ignore", "pipe", "ignore"] }).toString();
  const base = JSON.parse(raw);
  const bc = Array.isArray(base.cards) ? base.cards : [];
  baseIds = new Set(bc.map((c) => c.id));
  baseBrokenPairs = new Set();
  for (const c of bc) for (const r of (Array.isArray(c.related) ? c.related : [])) if (!baseIds.has(r)) baseBrokenPairs.add(`${c.id}→${r}`);
  if (cards.length < bc.length) E(`카드 수 감소 ${bc.length} → ${cards.length} — 의도한 삭제면 커밋 메시지에 명시하고 이 검사를 재검토할 것`);
} catch { W("기준본 없음(git origin/main 미접근) — 수량 감소·신규·엣지 동결 판별 생략, 절대 하한만 적용"); }
if (cards.length < MIN_CARDS) E(`카드 ${cards.length}장 < 절대 하한 ${MIN_CARDS}`);
const isNew = (c) => (baseIds ? !baseIds.has(c.id) : false);

// ---- 2) id·필수 필드 ----
const ids = new Set();
let dupIds = 0, missingReq = 0, badDate = 0, badSignalNew = 0, badType = 0;
const REQUIRED = ["id", "date", "title", "region", "signal", "gate", "fact", "urls", "implication"];
const ARRAY_FIELDS = new Set(["urls", "implication"]);
for (const c of cards) {
  if (ids.has(c.id)) { dupIds++; E(`중복 id: ${c.id}`); }
  ids.add(c.id);
  for (const k of REQUIRED) {
    const v = c[k];
    const empty = v === undefined || v === null || v === "" || (Array.isArray(v) && v.length === 0);
    if (empty) { missingReq++; if (missingReq <= 5) E(`${c.id || "(id없음)"}: 필수 필드 ${k} 비어있음`); continue; }
    // 존재만 보면 title이 객체여도 통과한다 — toCompatCard가 그대로 보존하고
    // JSX가 {card.title}로 렌더하면 "Objects are not valid as a React child"로 화면이 죽는다
    const wantArray = ARRAY_FIELDS.has(k);
    const ok = wantArray ? Array.isArray(v) : typeof v === "string";
    if (!ok) { badType++; if (badType <= 5) E(`${c.id || "(id없음)"}: ${k} 타입 위반 — ${wantArray ? "배열" : "문자열"} 필요, 실제 ${Array.isArray(v) ? "array" : typeof v}`); }
  }
  if (!isRealDate(c.date)) { badDate++; if (badDate <= 3) E(`${c.id}: date가 실제 달력 날짜가 아님 "${c.date}"`); }
  const sig = String(c.signal || "").toLowerCase();
  if (!SIGNALS.has(sig) && isNew(c)) { badSignalNew++; W(`${c.id}: 신규 카드 signal 미등록 값 "${c.signal}"`); }
}
if (missingReq > 5) E(`…필수 필드 누락 총 ${missingReq}건`);

// ---- 3) related 무결성 — 동결은 '숫자'가 아니라 '엣지 정체'로 ----
// 숫자 상한만 쓰면 레거시 카드가 깨진 대상을 다른 없는 id로 바꿔도, 하나를 고치고
// 다른 곳에 새로 만들어도 총계가 그대로라 통과한다(Codex #220 R3). 기준본의 (카드id→대상id)
// 쌍 집합에 없는 깨진 엣지는 전부 신규 결함으로 본다.
let broken = 0, brokenNew = 0, selfRef = 0;
for (const c of cards) {
  const rel = Array.isArray(c.related) ? c.related : [];
  for (const r of rel) {
    if (r === c.id) { selfRef++; E(`${c.id}: related가 자기 자신을 가리킴`); }
    else if (!ids.has(r)) {
      broken++;
      const pair = `${c.id}→${r}`;
      if (baseBrokenPairs) {
        if (!baseBrokenPairs.has(pair)) { brokenNew++; E(`새 깨진 related: ${pair}${isNew(c) ? " (신규 카드)" : " (기존 카드에 신규 유입)"}`); }
      } else if (isNew(c)) { brokenNew++; E(`신규 카드 깨진 related: ${pair}`); }
    }
  }
}
if (!baseBrokenPairs && broken > BROKEN_RELATED_MAX) E(`깨진 related ${broken}건 > 동결 기준선 ${BROKEN_RELATED_MAX} (기준본 없어 총계로만 판정)`);
else if (broken && !brokenNew) W(`깨진 related ${broken}건 — 전부 기준본 동결분(신규 0)`);

// ---- 4) id 날짜접두 ↔ date — 신규만 무관용(레거시 리데이팅은 ID 불변 관행) ----
let idDateMis = 0;
for (const c of cards) {
  const m = String(c.id || "").match(ID_DATE_RE);
  if (!m) {
    // 날짜 접두 자체가 없으면 접두 검사가 통째로 우회된다 — 신규는 표준 형식 강제,
    // 레거시(R##_##·W#·D_## 등 240장)는 허용
    if (isNew(c)) E(`신규 카드 id 형식 위반(YYYY-MM-DD_ 접두 없음): ${c.id}`);
    continue;
  }
  if (m[1] !== c.date) {
    idDateMis++;
    if (isNew(c)) E(`신규 카드 id 접두(${m[1]}) ≠ date(${c.date}): ${c.id} — 0.8은 날짜 잠금 후 id 부여가 규약`);
  }
}
if (idDateMis > ID_DATE_MISMATCH_MAX) E(`id접두≠date ${idDateMis}건 > 동결 기준선 ${ID_DATE_MISMATCH_MAX}`);

// ---- 5) 정보성 지표 (막지 않음) — lean export 전까지 관측만 ----
const fieldCounts = cards.map((c) => Object.keys(c).length);
const maxFields = Math.max(...fieldCounts);
const over20 = fieldCounts.filter((n) => n > 20).length;
console.log(`[info] 카드 ${cards.length}장 · ${(bytes / 1048576).toFixed(2)}MB · 필드 최대 ${maxFields} · 20필드 초과 ${over20}장(발행 파이프라인 메타 잔존 — lean export 도입 시 이 수치가 0이 목표)`);

// ---- 결과 ----
for (const w of warns) console.log("WARN:", w);
for (const e of errors) console.error("ERROR:", e);
console.log(`\nRESULT: ${errors.length ? "FAIL" : "PASS"} (errors ${errors.length}, warnings ${warns.length})`);
process.exit(errors.length ? 1 : 0);
