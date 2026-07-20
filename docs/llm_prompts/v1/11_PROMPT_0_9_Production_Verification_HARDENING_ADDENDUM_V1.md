# Prompt 0.9 Production Verification Hardening Addendum V1

Base prompt blob: `c833acbb451499ac000f7b72023eeef595c71ea2`
Integrity override SHA-256: `6d3cd9e6dcf7ad47801ef587f25633ec849a2108a9b9f6aa8b775076206ec05d`

Recompute from merged GitHub main and production data:

- card count and merge accounting;
- active-ID uniqueness;
- ID prefix versus event date and region;
- latest-first order;
- atomic claim-map hashes for newly merged cards;
- source publication and visible quote dates, including real ISO calendar-date validation;
- story-ID collision flags;
- related target existence, self-link, duplicate-link, and confirmed-remap history, compared with the prior production/main card baseline;
- state-ladder monotonicity.

Required related-lineage command:

```bash
python validation_scripts/related_lineage_check.py \
  MERGED_PRODUCTION_CARDS_JSON \
  --previous-cards-json PRIOR_PRODUCTION_CARDS_JSON
```

Do not accept upstream PASS flags as proof. Do not classify a dangling related target as historical without the previous baseline comparison.
Production verified requires successful recomputation.
