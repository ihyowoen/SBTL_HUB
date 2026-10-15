# R23 — verified existing-card factual repair (two IDs only)

**This is a production-content PATCH PROPOSAL on an isolated draft PR, not a 0.0C/Stage A release.** Source of truth is `data/cards.full.json`, mirrored by exact projection to `public/data/cards.json`.

## Scope & verification target
- Locked input main `b7847ca9885f6f27ae0566455b0a476ef1059d24`, Full blob `d0b472e4173e565284616bb7eec0e4b28e1a42b9`, Lean blob `c39eac64afde20ff0ccacd920e12abbdab1b3d02`. Exactly **1,674** cards.
- Proposed change **only** `R3_07` and `2026-08-24_GL_03`, preserving IDs, other 1,672 card objects, root inventory and related edges. Original historic Stage B/C traces are not rewritten or treated as re-validated.
- `R3_07` **Nth Cycle–Trafigura:** issuer March 16 release calls this a binding 10-year ~$1.1bn offtake; subsequent Nth Cycle SEC S-4 risk disclosure calls it a **binding term sheet** subject to final purchase agreement, project development and conditions precedent, **not** $1.1bn booked sales or completed refining commercialisation.
  - Issuer: https://nthcycle.com/newsroom/nth-cycle-announces-landmark-1-1-billion-offtake-agreement-with-trafigura-expands-operations-in-us-and-europe
  - SEC: https://www.sec.gov/Archives/edgar/data/2102713/000119312526394814/kcac-20260918.htm
- `2026-08-24_GL_03` **Lithium Argentina–Ganfeng:** issuer August 24 release states **$180m 6-year unsecured convertible note, 4% coupon, $12.50/share conversion price**, and separate 67:33 PPG JV definitive agreements. Existing card's **$130m equity + $50m JV** construction is incorrect. **$180m financing closed Sep 15**, PPG JV completion and commercial lithium output remain distinct stages.
  - Aug24 issuer: https://investors.lithium-argentina.com/news-releases/news-release-details/lithium-argentina-finalizes-ppg-joint-venture-announces-180m
  - Sep15 issuer: https://investors.lithium-argentina.com/news-releases/news-release-details/lithium-argentina-announces-closing-180m-strategic-investment

## Governed correction path (CI verified)
- Bounded existing-card `manual_direct_add_v2` manifest: `direct-adds/2026-10-15-r23-existing-claims/direct-add.json`, **operations.update=2, add=0, ID migration=0**.
- Both unchanged event identities are guaranteed: no `id`, `date`, `region`, `related` edits; the PPG `event_fingerprint` is preserved exactly to retain the prior economic-event anchor.
- Actual native `validate_manual_direct_add.mjs` and `validate_manual_direct_add_v4_hardening.mjs` **PASS**, with no new dangling Related. The GitHub branch-only action committed the verified Full blob `1af792e2e80516e1ec1d7d9660c150b312168b21`, and exact Lean blob `41b51ca4fa4e4f40a92c18577ea0655483295be1`. These are proposed PR changes; main remains unchanged.
- Broad HUB 0.0C remains blocked, but this update uses a **separate, explicitly governed factual-correction path**. Do not weaken the 0.0C/new-card publication gate.

## Programmatic execution and safety
- The added Python script `scripts/remediation/r23_two_card_factual_correction.py` **never writes either live file**. It hard-checks the original SHA256 of both files and produces two preview outputs in `/tmp/r23_hotfix_preview/`; requires identical fixed output hashes.
- The isolated GitHub Actions workflow only runs on this PR's exact branch (same repository) and generates a **proposed pair of Full/Lean changes into this draft branch only**. It checks unchanged main, exactly two card IDs, native `validate_cards.mjs` against main, and `lean_cards.mjs --check`, then commits **only** those two files back to this PR. If action token cannot write to PR, the branch remains a nonproduction proposal and the failure must be reported.
- Preview computed SHA256 (git hash-object): Full `855566c8bb724a8c88a6759e5318d952892493ecdef8db1c4870319288164ea6` (`1af792e2e80516e1ec1d7d9660c150b312168b21`); Lean `df7b0c056554958fe4f75b96352d596b99d5b3b0ac52099c00a34e89044ea6ac` (`41b51ca4fa4e4f40a92c18577ea0655483295be1`).
- Native check run in isolated read-only sandbox: **1,674/1,674 IDs**, exact two-card Full/Lean projection, `validate_cards.mjs` PASS; `lean_cards.mjs --check` PASS. Baseline's 14 legacy broken Related refs and 3 legacy ID/date anomalies are unchanged.
- **Do not merge before reviewing the branch's generated two-card diff, CI and relevant release/security gates.** Broad 0.0C stays **BLOCKED**; this narrow repair is explicitly proposed as a separate emergency accuracy correction and must not be mislabeled a new-news catch-up release.
