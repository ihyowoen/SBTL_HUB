#!/usr/bin/env node
/**
 * scripts/validate_faq.js v0.1
 * PHASE B1 — FAQ Schema v2.0 validator (data-only)
 *
 * Validates public/data/faq.json against schema:
 *   - top-level JSON array
 *   - each entry: { id, k, a, category }  (no other fields allowed)
 *   - id matches /^[a-z][a-z0-9_]*$/, globally unique
 *   - k: non-empty array of non-empty strings
 *   - a: non-empty trimmed string
 *   - category: one of us_policy, eu_policy, cn_policy, kr_policy,
 *               jp_policy, company, industry, tech, app
 *
 * Usage:
 *   node scripts/validate_faq.js          # human output
 *   node scripts/validate_faq.js --json   # JSON output
 *
 * Exit code: 0 = pass, 1 = fail
 */

import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const FAQ_PATH = path.join(__dirname, '..', 'public', 'data', 'faq.json');
const ALLOWED_CATEGORIES = new Set([
  'us_policy', 'eu_policy', 'cn_policy', 'kr_policy', 'jp_policy',
  'company', 'industry', 'tech', 'app',
]);
const ALLOWED_FIELDS = new Set(['id', 'k', 'a', 'category']);
const ID_RE = /^[a-z][a-z0-9_]*$/;

const jsonOut = process.argv.slice(2).includes('--json');
const errors = [];
let total = 0;

function emitAndExit() {
  if (jsonOut) {
    console.log(JSON.stringify({ ok: errors.length === 0, total, errors }, null, 2));
  } else if (errors.length === 0) {
    console.log(`✓ FAQ validation pass — ${total} entries`);
  } else {
    console.error(`✗ FAQ validation FAILED — ${errors.length} error(s)`);
    errors.forEach((e) => console.error(`  · ${e}`));
  }
  process.exit(errors.length === 0 ? 0 : 1);
}

let raw;
try {
  raw = fs.readFileSync(FAQ_PATH, 'utf8');
} catch (e) {
  errors.push(`cannot read ${FAQ_PATH}: ${e.message}`);
  emitAndExit();
}

let data;
try {
  data = JSON.parse(raw);
} catch (e) {
  errors.push(`invalid JSON: ${e.message}`);
  emitAndExit();
}

if (!Array.isArray(data)) {
  errors.push('top-level must be a JSON array');
  emitAndExit();
}

total = data.length;
const seenIds = new Map();

data.forEach((entry, i) => {
  const loc = `entry[${i}]`;

  if (entry === null || typeof entry !== 'object' || Array.isArray(entry)) {
    errors.push(`${loc}: must be a plain object`);
    return;
  }

  for (const key of Object.keys(entry)) {
    if (!ALLOWED_FIELDS.has(key)) {
      errors.push(`${loc}: unknown field "${key}" (allowed: id, k, a, category)`);
    }
  }

  if (typeof entry.id !== 'string' || entry.id.length === 0) {
    errors.push(`${loc}: id is required and must be a non-empty string`);
  } else if (!ID_RE.test(entry.id)) {
    errors.push(`${loc}: id "${entry.id}" does not match ${ID_RE}`);
  } else if (seenIds.has(entry.id)) {
    errors.push(`${loc}: duplicate id "${entry.id}" (also at entry[${seenIds.get(entry.id)}])`);
  } else {
    seenIds.set(entry.id, i);
  }

  if (!Array.isArray(entry.k) || entry.k.length === 0) {
    errors.push(`${loc}: k must be a non-empty array`);
  } else if (!entry.k.every((x) => typeof x === 'string' && x.length > 0)) {
    errors.push(`${loc}: k must contain only non-empty strings`);
  }

  if (typeof entry.a !== 'string' || entry.a.trim() === '') {
    errors.push(`${loc}: a must be a non-empty string`);
  }

  if (typeof entry.category !== 'string' || !ALLOWED_CATEGORIES.has(entry.category)) {
    errors.push(`${loc}: category "${entry.category}" not in allowed enum`);
  }
});

emitAndExit();
