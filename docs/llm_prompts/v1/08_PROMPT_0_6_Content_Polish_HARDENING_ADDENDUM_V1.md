# Prompt 0.6 Content Polish Hardening Addendum V1

Base prompt blob: `224e6d67101d983a285bf793a339246e7cba43cf`
Integrity override SHA-256: `6d3cd9e6dcf7ad47801ef587f25633ec849a2108a9b9f6aa8b775076206ec05d`

Before visible-field rewriting, store the incoming coverage hash.
After any title/sub/gate/fact/implication edit:

- invalidate the incoming coverage hash;
- rebuild atomic claims;
- rebuild the claim-to-quote map;
- rerun numeric/date/entity coverage;
- preserve event-date and source-date roles;
- prohibit content pass when the rebuilt map does not PASS.

A wording-only assertion is not accepted when the factual atom changed.
