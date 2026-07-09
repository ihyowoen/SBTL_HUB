#!/usr/bin/env python3
"""
R3C_P06 - Content audit gate (0.6 / 0.7).
run 20260516_012728 retrospective patch.

Checks that 0.6 Content Polish produced:
  1. card_claim_diversity_audit[]  (CARD_CLAIM_DIVERSITY_AUDIT_RULE v7)
  2. related_coverage_audit[]      (per-card: was a genuine same-event /
     same-cluster link CONSIDERED against batch + recent baseline?)

0.7 Final QC uses this as a hard gate: publish_ready is BLOCKED if either audit
is missing/empty, or if any card lacks a related_coverage_audit entry.

The related audit verifies that a link was CONSIDERED for each card - it does
NOT require that a link was forced. related[] must hold only genuine links.

Usage:
    python3 content_audit_check.py <content_output.json>

Exit codes: 0 = PASS, 1 = BLOCKED, 2 = usage error.
"""
import json
import sys


def load_cards(data):
    if isinstance(data, list):
        return data
    if isinstance(data, dict):
        for k in ('cards', 'draft_cards', 'payload', 'accepted'):
            v = data.get(k)
            if isinstance(v, list):
                return v
    return []


def main():
    if len(sys.argv) < 2:
        print("usage: content_audit_check.py <content_output.json>")
        return 2
    with open(sys.argv[1], encoding='utf-8') as f:
        data = json.load(f)

    cards = load_cards(data)
    cdv = data.get('card_claim_diversity_audit') if isinstance(data, dict) else None
    rca = data.get('related_coverage_audit') if isinstance(data, dict) else None

    problems = []
    if not isinstance(cdv, list) or len(cdv) == 0:
        problems.append("card_claim_diversity_audit[] missing or empty "
                         "(V7 required)")
    if not isinstance(rca, list) or len(rca) == 0:
        problems.append("related_coverage_audit[] missing or empty")

    audited_ids = set()
    if isinstance(rca, list):
        for r in rca:
            if isinstance(r, dict):
                cid = r.get('card_id') or r.get('id')
                if cid:
                    audited_ids.add(cid)

    card_ids = [c.get('id') for c in cards
                if isinstance(c, dict) and c.get('id')]
    not_audited = [cid for cid in card_ids if cid not in audited_ids]

    print("=== R3C_P06 content audit gate ===")
    print(f"cards                          : {len(cards)}")
    print("card_claim_diversity_audit     : "
          f"{len(cdv) if isinstance(cdv, list) else 'MISSING'}")
    print("related_coverage_audit         : "
          f"{len(rca) if isinstance(rca, list) else 'MISSING'}")

    if card_ids and not_audited:
        print(f"cards w/o related audit entry  : {len(not_audited)}")
        for cid in not_audited[:30]:
            print(f"    - {cid}")
        if len(not_audited) > 30:
            print(f"    ... (+{len(not_audited) - 30} more)")
        problems.append(f"{len(not_audited)} card(s) absent from "
                        f"related_coverage_audit[]")
    print()

    if problems:
        print("RESULT: BLOCKED - 0.7 must not grant publish_ready.")
        for p in problems:
            print(f"    - {p}")
        return 1
    print("RESULT: PASS - both audits present and all cards covered.")
    return 0


if __name__ == '__main__':
    sys.exit(main())
