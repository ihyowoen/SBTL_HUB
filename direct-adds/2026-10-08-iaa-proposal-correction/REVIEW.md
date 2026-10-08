# IAA governed correction — approval pending

**Prerequisite Draft #388 targets main and lands evidence plus corrected briefs first; canonical Draft #387 is stacked on it and changes only the three governed files.** After approval and landing of #388, retarget #387 to main, relock its active manifest to actual main, and rerun before separate approval. Neither PR may merge or deploy without owner approval. The canonical exporter and production gate are unchanged.

This branch corrects `2026-05-13_EU_01` against official EU evidence checked on 2026-10-08. It is a bounded `manual_direct_add_v2` correction, not a completed Stage A/B/C run, new event, or production approval. No merge, production deployment, auto-merge, or change to PR #386 / Revolution branches is authorized by this packet.

## Baseline and identity

- Main commit: `c09c1bc5112216a617903a2d572662342bcd857c`
- Canonical blob: `d847e2d53bfe27a2b61bac023a82d2009c313356`
- Inventory: 1,674 → 1,674; only one card updated; no add, deletion, ID migration, or Related change.
- Preserve ID, 2026-05-13 representative/news date, region, original assignment and lineage. March 4 is the proposal publication date, not a re-dating of the May media event. October 8 is the correction/status check date.
- Preserve original OFweek URL as a historical event anchor, while primary official sources now support current claims. The complete previous card and exact before/after brief items are retained in `correction.json`.

## Official source review

1. [OEIL 2026/0068(COD)](https://oeil.europarl.europa.eu/oeil/en/procedure-file?reference=2026%2F0068%28COD%29): committee decision pending. Proposal publication March 4; committee referral April 30. September 11 committee draft report is not enactment.
2. [Commission publication](https://single-market-economy.ec.europa.eu/publications/industrial-accelerator-act_en): COM(2026)100 is a March 4 proposal. `final` is the Commission document-version designation, not proof of adoption or entry into force.
3. [COM proposal](https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX%3A52026PC0100): Article 2 target; Articles 17–18 investment scope, exclusions, conditions; Article 36 future publication-based entry into force. Existing EU legislation is legally distinct from these proposed amendments.
4. Commission Annex III, printed pages 4–6: specific procurement, support and small-car routes; not a blanket restriction on all EV sales. Part I has a proposed 3-to-5-component transition measured from future entry into force. Part II has mismatched letter references in its transition sentence in the inspected March PDF; no silent drafting repair or settled application date is claimed. Download URL and SHA256 are in the evidence packet.

The investment scope is more than EUR 100m and more than 40% country-level global manufacturing capacity in listed sectors, subject to exclusions. At least four of six conditions are proposed for direct foreign investors from 12 months after future entry into force; the 50% EU workforce condition is separately mandatory. It is inaccurate to describe both JV and technology licensing as individually mandatory for every covered investor. Remove unsupported NCM preference/forced conversion and automatic Korean beneficiary claims.

## Mutation scope and derivative audit

- Canonical: title, sub, gate, fact, implication, URLs, fact sources, source tier and append-only correction history; exact field whitelist is in the manifest.
- Lean: regenerate with the unchanged canonical exporter; never edit public card independently.
- `public/data/briefs.json`: two May items (`lib_2026-05_all`, `lib_2026-05_region`), each with one narrative passage, one watch row and the target reference title/link. Preserve reference numbers, event dates and other news. Advance revision dates so existing library revision detection can adopt the correction.
- Public data containing the exact ID: canonical projection and those two refs. Other matches are historical run receipts (September 6 stage files and September 15 editorial audit); keep them immutable as evidence rather than rewriting past decisions.
- Scope extension beyond the three core direct-add files in `docs/MANUAL_DIRECT_ADD_V2.md` is explicitly authorized by the user's request for derived-data fixes, evidence preservation and regression tests. No production validator is relaxed.
- Browser localStorage archives and previously generated `/api/brief` responses are not repository artifacts. The static library's content/revision changes support normal application revision adoption; previously downloaded/exported copies cannot be changed here.

## Independent tracker findings — separate ledger required

`tracker_data.json` EU-002 and its hidden alias EU-005 already use WATCH/proposal framing; they are independently authored tracker records, not projections of this card. Their detail needs a separate tracker correction: EU-002 contains mismatched battery-EPR sources/tip and dates inconsistent with OEIL; EU-005 includes an incorrect 30% ownership limit and overbroad thresholds/mandatory conditions. `region_policy.json` EU-002 is an old procedural milestone. None is evidence of enacted IAA obligations. Do not mix unverified tracker stamps or an unaudited tracker ledger into this bounded card PR. These findings are retained for follow-up, not marked verified or silently fixed.

Other canonical keyword matches were 2026-05-28_KR_01, 2026-05-20_GL_08, 2026-05-11_CN_02 and 2026-04-24_KR_04. They are distinct records, not copies of this card. This packet makes no whole-IAA-universe accuracy claim.

## Reproduction and validation

Run from repository root (materialization writes the three reviewed data files locally):

```sh
python scripts/apply_iaa_correction.py
python scripts/test_iaa_correction.py
node scripts/lean_cards.mjs --check
git show c09c1bc5112216a617903a2d572662342bcd857c:data/cards.full.json > /tmp/iaa-base-full.json
node scripts/validate_json_schema_subset.mjs --schema schemas/manual-direct-add.v2.schema.json --instance direct-adds/2026-10-08-iaa-proposal-correction/direct-add.json
node scripts/validate_manual_direct_add.mjs --manifest direct-adds/2026-10-08-iaa-proposal-correction/direct-add.json --base /tmp/iaa-base-full.json --full data/cards.full.json
node scripts/validate_manual_direct_add_v4_hardening.mjs --manifest direct-adds/2026-10-08-iaa-proposal-correction/direct-add.json --base /tmp/iaa-base-full.json --full data/cards.full.json
node scripts/validate_cards.mjs
node scripts/validate_cards.mjs data/cards.full.json
node scripts/validate.mjs
```

Nine offline regression tests pass: pinned-base whole-inventory and brief replay; public projection alignment; negative controls for enacted headline, identity/lineage mutation, missing official evidence, stale brief narrative/watch/ref, and wrong threshold/mandatory workforce condition. Full replay rejects any undeclared unrelated mutation. It proves consistency with reviewed evidence, not future legal status; recheck official status before approval if time has elapsed.

Existing schema, bounded mutation, V4 hardening, lean, canonical/public card and tracker structural checks pass. Existing legacy warnings remain (14 dangling Related links, 3 ID/date mismatches, 7 composite regions; tracker 497 legacy warnings). Dedicated read-only CI is scoped to this branch to avoid pinning future legitimate corrections to this historical snapshot. Base/main drift requires relock and rerun before approval.

## Review remediation (2026-10-08)

The prior packet/data-shape finding is resolved by #387's exact three-file scope plus stacked #388. The apply tool now validates packet/manifest commit equality and the pinned full blob SHA before loading output candidates or writing. Two subprocess negative tests inject each bad lock and confirm failure plus byte-identical canonical, lean and brief sentinel outputs. Nine tests pass locally; read-only CI reruns them. No merge or production deployment.


## Revised landing order — review 5453167898

PR #388 targets main and contains the corrected public briefs, complete correction evidence, replay tooling, template manifest and tests. It must land first after approval. It changes no canonical cards. PR #387 is stacked on #388 and changes only canonical full/lean and the active manifest. Its baseline lock is the prerequisite commit, whose canonical blob is unchanged. After #388 lands, retarget #387 to main and relock its active manifest to the actual main commit (squash/rebase merge hashes may differ), then rerun all gates before separate approval. Never merge #387 first. This ordering makes correction.json available before the canonical provenance pointer and removes stale brief claims before the card correction. No merge or production deployment is authorized.

The original packet commit is the immutable replay base. A later governed manifest base is accepted only if it descends from that replay base and preserves the exact canonical blob, checked before writes. The inactive direct-add.template.json supports isolated prerequisite CI; it is not an active governed manifest.
