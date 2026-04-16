# App Story UI — Phase 1 Brief

## Goal

Phase 1 does **not** replace the current runtime data layer.
It keeps the current deploy app as the runtime base and only begins the story-UI migration safely.

## Locked Principles

- brand must remain `강차장의 배터리상담소`
- `kang.png` avatar must remain
- current `cards.json` / `tracker_data.json` fetch layer remains the source of truth
- current chatbot API flow remains the source of truth
- story UI should read normalized card fields, not hard-code legacy compact field names everywhere

## What Phase 1 Does

1. Add a normalization layer for cards
2. Use that layer when introducing story-style cards
3. Keep the current chatbot logic and only improve handoff later
4. Avoid mock reactions / consensus / audio in the first implementation step

## Normalized Story Mapping

- `title` -> story headline
- `sub` -> short support line
- `fact` -> `무슨 일이야?`
- `gate` -> `그래서 어떻게 돼?`
- `implicationText` -> `강차장 코멘트`
- `primaryUrl` -> source open action
- `id` -> storage / scrap / chatbot handoff key

## First Safe Integration Order

1. keep `src/App.jsx` as the base
2. import `src/story/normalizeCard.js`
3. introduce a story-style card shell in `Home` first
4. only after that expand the same shell to `NewsDesk`
5. keep `Tracker` and `ChatBot` runtime logic intact during phase 1

## Explicit Non-Goals for Phase 1

- no replacement of chatbot runtime with mock UI logic
- no fake `Industry Consensus`
- no reaction counters without trusted backing data
- no TTS/audio layer
- no full `cards.json` schema migration in the same step

## Why This Order

The uploaded redesign is visually stronger, but it still carries assumptions that can regress the current app if copied wholesale.
The safe path is:
- preserve current runtime
- add normalization
- migrate presentation gradually

That is the purpose of this phase.
