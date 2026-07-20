# Prompt 0.8 Merge Prep Hardening Addendum V1

Base prompt blob: `d9a86bdc915ebf77c31aad12bcc710b9f6afdbf3`
Integrity override SHA-256: `6d3cd9e6dcf7ad47801ef587f25633ec849a2108a9b9f6aa8b775076206ec05d`

Order of operations:

1. lock final `event_date`;
2. derive and assign production ID from that locked date and resolved region;
3. enumerate all current and historical IDs;
4. retire superseded IDs in audit metadata;
5. update only confirmed related-ID replacements;
6. validate related targets, self-links, duplicates, and forward-date anomalies against the merge-base card baseline;
7. preserve only unresolved related IDs that were already dangling in that previous baseline; block every newly missing target;
8. re-sort latest-first;
9. rerun ID/date/region integrity.

Required related-lineage command:

```bash
python validation_scripts/related_lineage_check.py \
  CURRENT_CARDS_JSON \
  --previous-cards-json MERGE_BASE_CARDS_JSON
```

Hard fail: `BLOCKED_ID_EVENT_DATE_MISMATCH`, `NEW_MISSING_RELATED_TARGET`, or `BLOCKED_RELATED_HISTORY_UNCLASSIFIED`.
