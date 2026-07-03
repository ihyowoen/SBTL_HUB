# tracker validation

`scripts/validate.mjs` — zero-dependency Node validator (node: built-ins only). Runs locally and as a
PR merge gate via `.github/workflows/validate-tracker.yml`. No install step.

## run locally
```bash
node scripts/validate.mjs                                   # defaults to public/data/*
node scripts/validate.mjs public/data/tracker_data.json public/data/region_policy.json
```
Exit `0` = PASS, `1` = FAIL (≥1 error). Prints item count + region/status distribution every run.

## ERRORS (block merge)
- broken JSON
- duplicate item id / id not matching `XX-NNN`
- region not in `NA/EU/CN/KR/JP/GL`
- status not in `ACTIVE/UPCOMING/WATCH/DONE`
- banned emoji anywhere in an item, meta, or region_policy
- `canonicalId` / `supersededBy` pointing to a non-existent id (or to itself)
- `effectiveDate` / `lastChecked` present but not ISO `YYYY-MM-DD`
- `instrumentType` present but not in `law/decree/notification/standard`
- region_policy segment missing `name/headline/summary/watchpoints`

## WARNINGS (non-blocking — migration nudges)
- `no effectiveDate` — D-day should derive from an ISO date at render time, not be baked into `dt`
- `dt contains baked 'D-…'` — staleness smell
- `no instrumentType` — scope enum not yet enforced as a field
- `src[i] no accessedDate` — no link-rot trail

Once the migration fields are present, the validator upgrades these from WARN to enforced ERROR-on-malformed.
