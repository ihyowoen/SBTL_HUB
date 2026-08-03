from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def replace_once(path, old, new, label):
    p = ROOT / path
    text = p.read_text(encoding='utf-8')
    count = text.count(old)
    if count != 1:
        raise SystemExit(f'{label}: expected one match, found {count}')
    p.write_text(text.replace(old, new, 1), encoding='utf-8')

old_gate = '- execution_anchor_type / execution_anchor_strength is present for every format-risk candidate'
new_gate = '''- every format-risk candidate preserves a passing `anchor_path_validation` and selects exactly one source-backed path:
  - `selected_anchor_path: execution` with non-empty `execution_anchor_type` and adequate/strong `execution_anchor_strength`; or
  - `selected_anchor_path: v3_non_execution` with `structural_value_override_applied: true`, complete canonical V3 override metadata, and the execution route explicitly `not_applicable` with a specific reason.
- conventional execution-anchor fields are not mandatory for a valid `v3_non_execution` path; missing, dual-claimed, contradictory, or unsupported route metadata is invalid upstream lineage'''

for path in [
    'docs/llm_prompts/v1/07_PROMPT_0_5_Evidence_QC.md',
    'docs/llm_prompts/v1/08_PROMPT_0_6_Content_Polish.md',
    'docs/llm_prompts/v1/11_PROMPT_0_9_Production_Verification.md',
    'docs/llm_prompts/v1/12_PROMPT_1_0_Remediation.md',
]:
    replace_once(path, old_gate, new_gate, f'two-path upstream lineage gate in {path}')

old_overlay = '''- Build `CURRENT_RUN_ID_FILE` containing only the production IDs / candidate IDs introduced or materially updated by the current run.
- Run `evidence_qc_v8_check.py`,
  `related_lifecycle_check.py --require-contract --new-id-file <CURRENT_RUN_ID_FILE>` against the merged baseline/candidate validation artifact,'''
new_overlay = '''- Build `CURRENT_RUN_SCOPE_FILE` containing only identifiers introduced or materially updated by the current run. Use final `id` / `card_id` when assigned; before Prompt 0.8 production-ID resolution, use the exact carried `draft_id` or `source_spec_id` present on the merged candidate artifact.
- The Related lifecycle validator must match scope entries against `id`, `card_id`, `draft_id`, or `source_spec_id`; unmatched or zero-match scope remains a hard failure.
- Run `evidence_qc_v8_check.py`,
  `related_lifecycle_check.py --require-contract --new-id-file <CURRENT_RUN_SCOPE_FILE>` against the merged baseline/candidate validation artifact,'''
for path in [
    'docs/llm_prompts/v1/09_PROMPT_0_7_Final_QC.md',
    'validation_scripts/apply_prompt_contract_overlays.py',
]:
    replace_once(path, old_overlay, new_overlay, f'pre-merge scope contract in {path}')

validator = ROOT / 'validation_scripts/related_lifecycle_check.py'
text = validator.read_text(encoding='utf-8')
text = text.replace('''    parse_date,\n    select_scoped_cards,\n)''', '''    parse_date,\n)''')
text = text.replace('''            value = row.get("assigned_id") or row.get("id") or row.get("card_id")''', '''            value = (\n                row.get("assigned_id")\n                or row.get("id")\n                or row.get("card_id")\n                or row.get("draft_id")\n                or row.get("source_spec_id")\n            )''')
needle = '''def relation_object(card: dict[str, Any]) -> dict[str, Any] | None:\n'''
helper = '''def card_identifiers(card: dict[str, Any]) -> set[str]:\n    return {\n        str(card.get(key)).strip()\n        for key in ("id", "card_id", "draft_id", "source_spec_id")\n        if card.get(key) is not None and str(card.get(key)).strip()\n    }\n\n\ndef primary_card_identifier(card: dict[str, Any]) -> str:\n    for key in ("id", "card_id", "draft_id", "source_spec_id"):\n        value = card.get(key)\n        if value is not None and str(value).strip():\n            return str(value).strip()\n    return ""\n\n\ndef select_related_scope(\n    cards: list[dict[str, Any]], selected: set[str] | None\n) -> tuple[list[dict[str, Any]], dict[str, Any]]:\n    if selected is None:\n        return cards, {"errors": [], "matched_ids": [], "unmatched_ids": []}\n    rows = [card for card in cards if card_identifiers(card) & selected]\n    matched = set().union(*(card_identifiers(card) & selected for card in rows)) if rows else set()\n    unmatched = sorted(selected - matched)\n    errors = []\n    if unmatched:\n        errors.append(f"unmatched scope identifiers: {', '.join(unmatched)}")\n    if selected and not rows:\n        errors.append("scope matched zero cards")\n    return rows, {\n        "errors": errors,\n        "matched_ids": sorted(matched),\n        "unmatched_ids": unmatched,\n    }\n\n\n'''
if needle not in text:
    raise SystemExit('validator helper insertion point missing')
text = text.replace(needle, helper + needle, 1)
text = text.replace('''    cid = str(card.get("id", ""))''', '''    cid = primary_card_identifier(card)''')
old_main = '''    by_id = {str(card.get("id")): card for card in cards if card.get("id")}\n    selected = load_ids(args.new_id_file)\n    rows, scope = select_scoped_cards(cards, selected)'''
new_main = '''    by_id: dict[str, dict[str, Any]] = {}\n    for card in cards:\n        for identifier in card_identifiers(card):\n            existing = by_id.get(identifier)\n            if existing is not None and existing is not card:\n                raise ValueError(f"duplicate card identifier alias: {identifier}")\n            by_id[identifier] = card\n    selected = load_ids(args.new_id_file)\n    rows, scope = select_related_scope(cards, selected)'''
if old_main not in text:
    raise SystemExit('validator main scope block missing')
text = text.replace(old_main, new_main, 1)
validator.write_text(text, encoding='utf-8')

# Validation log
log = ROOT / 'docs/validation/STRUCTURAL_NEWS_VALUE_V3_VALIDATION_20260802.md'
with log.open('a', encoding='utf-8') as f:
    f.write('''\n\n## Review 4840119588\n\n- Related lifecycle scope now recognizes final `id` / `card_id` and pre-merge `draft_id` / `source_spec_id` aliases in the merged artifact.\n- Final QC uses a current-run scope file compatible with identifiers available before Prompt 0.8 production-ID assignment.\n- Evidence QC, Content Polish, Production Verification, and Remediation upstream lineage gates now require exactly one supported execution or V3 non-execution path rather than execution-only fields.\n- Focused regression coverage verifies pre-merge scoping, unmatched-scope failure, and removal of residual execution-only lineage requirements.\n''')

# Remove patch machinery before committing.
(ROOT / 'scripts/patch_review_4840119588.py').unlink()
(ROOT / '.github/workflows/patch-review-4840119588.yml').unlink()
