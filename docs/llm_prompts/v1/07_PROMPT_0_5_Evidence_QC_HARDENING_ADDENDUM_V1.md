# Prompt 0.5 Evidence QC Hardening Addendum V1

Base prompt blob: `eb1fae6fe23072672209af92665b44b289580d4d`
Integrity override SHA-256: `6d3cd9e6dcf7ad47801ef587f25633ec849a2108a9b9f6aa8b775076206ec05d`

For every card:

1. split every visible field into atomic factual claims;
2. map every number, date, named entity, project, technology stage, legal
   stage, comparison, and causal dependency to an exact source quote;
3. create `claim_quote_coverage_map` with stable atomic IDs;
4. create `date_alignment_audit` covering card event date, source publication
   dates, visible quote dates, discovery dates, and event-fingerprint date;
5. hard fail on unsupported visible claims or ambiguous date roles.

Hard-fail status: `BLOCKED_DATE_ROLE_AMBIGUITY`.
Story IDs cannot satisfy evidence or duplicate identity.
