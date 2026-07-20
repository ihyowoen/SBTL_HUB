# Prompt 0.7 Final QC Hardening Addendum V1

Base prompt blob: `617f3c8bf4f02dd585954ac10134c07062e5b13c`
Integrity override SHA-256: `6d3cd9e6dcf7ad47801ef587f25633ec849a2108a9b9f6aa8b775076206ec05d`

Final QC must independently replay, not trust:

- atomic claim-to-quote coverage;
- every visible number/date/entity;
- event-date versus source-publication-date separation;
- event-fingerprint date;
- legal/technology execution stage;
- story-ID collision audit;
- related-candidate lineage.

Hard fail: `FINAL_QC_EVENT_SOURCE_DATE_CONTRADICTION`.
No `publish_ready` assignment when visible fields changed after the last
coverage-map hash.
