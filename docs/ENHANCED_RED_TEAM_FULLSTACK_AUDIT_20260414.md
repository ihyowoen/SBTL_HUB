# SBTL_HUB 풀스택 Red Team Audit (Line-by-Line)

**Date:** 2026-04-14
**Scope:** App.jsx, lib/chat/* (8 modules), api/* (4 endpoints), public/data/* (cards.json, faq.json, tracker_data.json), docs/* (7 files), merge_cards.py, vercel.json, package.json, env.example
**Method:** Line-by-line read of every file except public/webtoon/*.html (4 files) and full cards.json content (sampled ~50 cards from 337)

---

## Executive Summary

25 distinct bugs/issues found, grouped by severity. 3 of them are P0 operational emergencies (data is 9+ days stale, potential chatbot infrastructure failure). The architecture documents (`AI_CHATBOT_REFACTOR_PLAN.md`, `AI_CHATBOT_IMPLEMENTATION_CHECKLIST.md`) are excellent — the chatbot audit here confirms the docs' own diagnosis and pinpoints which of the listed P0/P1 items are still unfinished.

The single biggest finding is **BUG #3 (lib/chat/common.js uses `process.cwd()`)** — if this breaks in Vercel's serverless environment, the chatbot silently returns empty results for every query, which matches the user-reported "stupid chatbot" symptom better than any other single cause.

---

## P0 — Operational Emergencies

### BUG #1: cards.json 9 days stale
- `updated: "2026.04.13"` in cards.json; today is 2026.04.14. No cards dated 2026.04.14.
- The 11-day gap between today and the latest card breaks the app's "live feed" value proposition.
- Fix: run W6 merge pipeline. Verify merge_cards.py output.

### BUG #2: tracker_data.json 9 days stale
- `lastUpdated: "2026-04-05T15:00:00+09:00"`; all 50 items have `lastChecked: "2026-04-05"`.
- App.jsx Tracker shows "LAST CHECKED 2026.04.05" in the header — users see an 8-day-old policy tracker and may act on stale data.
- Fix: daily 2A+2B protocol on tracker_data.json per SKILL.md.

### BUG #3: lib/chat/common.js uses `process.cwd()` in serverless
```js
function projectRoot() { return process.cwd(); }
```
- In Vercel serverless functions, `cwd()` is typically `/var/task` or `/var/runtime`.
- `public/` is static-hosted; NOT automatically bundled into function output.
- If chat API cannot read cards.json/faq.json/tracker_data.json, `loadKnowledge()` returns empty arrays → ret