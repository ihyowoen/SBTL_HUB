#!/usr/bin/env python3
from pathlib import Path

p = Path('scripts/stage_c_r6_accepted7.py')
s = p.read_text(encoding='utf-8')

old_defs = 'qna_spec = "STD26_R6_B01_009"\ntax_spec = "STD26_R6_B01_010"\nqna_id = pkg_by_spec[qna_spec]["draft"]["id"]'
new_defs = 'qna_spec = "STD26_R6_B01_009"\ntax_spec = "STD26_R6_B01_010"\neu_passport_spec = "STD26_R6_B01_008"\nqna_id = pkg_by_spec[qna_spec]["draft"]["id"]'
if old_defs in s:
    s = s.replace(old_defs, new_defs, 1)
assert new_defs in s

old_else = '''    else:\n        lineage = {\n            "status": "PASS",\n            "relation_type": "new_unrelated_event",\n            "related_ids": [],\n            "provisional_current_batch_candidate_ids": [],\n            "reason": "R6 baseline/current-batch evidence did not identify a direct auditable predecessor or same-event representative card for this event.",\n            "fresh_follow_up_anchor_class": None,\n            "fresh_follow_up_anchor": None,\n            "incremental_fact": None,\n            "changed_judgment": None,\n            "same_event_check": "PASS",\n            "earliest_date_check": "PASS",\n            "rejected_relation_candidates": [],\n            "chronology_exception": None,\n        }\n'''
new_else = '''    elif pkg["spec_id"] == eu_passport_spec:\n        lineage = {\n            "status": "PASS",\n            "relation_type": "distinct_follow_up",\n            "related_ids": ["2026-07-20_EU_06"],\n            "provisional_current_batch_candidate_ids": [],\n            "reason": "R6 canonical-relation closure independently re-anchors the 2026-08-21 European Commission Battery Passport guidance to canonical predecessor 2026-07-20_EU_06. The later guidance is not a republication: it adds a current policy-preparation anchor by enumerating the 71 passport data points and their mandatory, optional or conditional applicability.",\n            "fresh_follow_up_anchor_class": "policy_regulatory_anchor",\n            "fresh_follow_up_anchor": "On 2026-08-21 the European Commission published updated Digital Batteries Passport preparation guidance that operationalizes the compliance-preparation layer around 71 data points ahead of the 2027-02-18 passport obligation.",\n            "incremental_fact": "The Commission guidance moves the July-level Battery Passport framework into field-level preparation detail by identifying 71 data points and their applicability/legal basis for covered battery categories.",\n            "changed_judgment": "Battery Passport readiness can now be assessed against a materially more specific Commission data-field checklist rather than only the earlier framework-level obligation.",\n            "same_event_check": "PASS_DISTINCT_STAGE",\n            "earliest_date_check": "PASS",\n            "rejected_relation_candidates": [],\n            "chronology_exception": None,\n        }\n    else:\n        lineage = {\n            "status": "PASS",\n            "relation_type": "new_unrelated_event",\n            "related_ids": [],\n            "provisional_current_batch_candidate_ids": [],\n            "reason": "R6 baseline/current-batch evidence did not identify a direct auditable predecessor or same-event representative card for this event.",\n            "fresh_follow_up_anchor_class": None,\n            "fresh_follow_up_anchor": None,\n            "incremental_fact": None,\n            "changed_judgment": None,\n            "same_event_check": "PASS",\n            "earliest_date_check": "PASS",\n            "rejected_relation_candidates": [],\n            "chronology_exception": None,\n        }\n'''
if new_else not in s:
    assert s.count(old_else) == 1, s.count(old_else)
    s = s.replace(old_else, new_else, 1)

p.write_text(s, encoding='utf-8')
print('PASS_PATCH_STAGE_C_R6_EU_LINEAGE')
