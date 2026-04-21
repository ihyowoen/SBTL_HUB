// scripts/classify_dist.js
// ============================================================================
// classifyCard() 분포 측정 — 273개 카드 카테고리 쏠림·default fallback 확인
// ============================================================================
// opener pool 품질의 선행 지표. default 비율이 10% 넘으면 rule 보강 검토.
//
// 실행: node scripts/classify_dist.js
// ============================================================================

import { classifyCard } from '../src/story/cardOpenerPool.js';
import { readFileSync } from 'fs';
import { fileURLToPath } from 'url';
import { dirname, join } from 'path';

const __dirname = dirname(fileURLToPath(import.meta.url));
const cardsPath = join(__dirname, '..', 'public', 'data', 'cards.json');

const raw = JSON.parse(readFileSync(cardsPath, 'utf-8'));
const cards = Array.isArray(raw.cards) ? raw.cards : (Array.isArray(raw) ? raw : []);

const dist = {};
const examples = {};

cards.forEach(c => {
  const cat = classifyCard(c);
  dist[cat] = (dist[cat] || 0) + 1;
  if (!examples[cat]) examples[cat] = [];
  if (examples[cat].length < 3) {
    examples[cat].push(c.T || c.title || '(no title)');
  }
});

console.log(`\n📊 classifyCard distribution (total ${cards.length} cards)\n`);
Object.entries(dist)
  .sort((a, b) => b[1] - a[1])
  .forEach(([cat, n]) => {
    const pct = (n / cards.length * 100).toFixed(1);
    console.log(`  ${cat.padEnd(14)} ${String(n).padStart(4)} (${pct}%)`);
    examples[cat].forEach(t => {
      const trimmed = String(t).slice(0, 70);
      console.log(`    · ${trimmed}${String(t).length > 70 ? '…' : ''}`);
    });
    console.log('');
  });

const defaultPct = ((dist.default || 0) / cards.length * 100).toFixed(1);
const signal = parseFloat(defaultPct) > 10 ? '⚠️ rule 보강 검토' : '✓ acceptable';
console.log(`Default fallback: ${defaultPct}% ${signal}`);

// implication 필드 품질도 같이 봐 — opener coverage 핵심 input
const withImp = cards.filter(c => Array.isArray(c.implication) && c.implication.length > 0).length;
const withMultiImp = cards.filter(c => Array.isArray(c.implication) && c.implication.length >= 2).length;
const impPct = (withImp / cards.length * 100).toFixed(1);
const multiImpPct = (withMultiImp / cards.length * 100).toFixed(1);
console.log(`\nimplication 보유: ${withImp}/${cards.length} (${impPct}%)`);
console.log(`implication 2개 이상: ${withMultiImp}/${cards.length} (${multiImpPct}%)`);
console.log(`※ implication 얇으면 coverage contract opener가 부실해질 위험`);
