from pathlib import Path

path = Path("docs/llm_prompts/v1/07_PROMPT_0_5_Evidence_QC.md")
text = path.read_text(encoding="utf-8")
old = '''For every candidate with `format_risk_tags` such as product/demo/PoC/component/interview/roundup/commentary/speech/personnel/partnership, require:

- `execution_anchor_type` is not null;
- `execution_anchor_strength` is `adequate` or `strong`; and
- Stage C did not leave unresolved `execution_anchor_gap`, `selection_defect`, or `source_direction_reversal` findings.
'''
new = '''For every candidate with `format_risk_tags` such as product/demo/PoC/component/interview/roundup/commentary/speech/personnel/partnership, require the preserved `anchor_path_validation` to prove exactly one source-backed route:

1. execution route
   - `selected_anchor_path = execution`
   - `anchor_path_qc_passed = true`
   - `execution_anchor_qc_status = pass`
   - `structural_value_override_qc_status = not_applicable`
   - `execution_anchor_type` is not null
   - `execution_anchor_strength` is `adequate` or `strong`

2. V3 non-execution route
   - `selected_anchor_path = v3_non_execution`
   - `anchor_path_qc_passed = true`
   - `structural_value_override_qc_status = pass`
   - `execution_anchor_qc_status = not_applicable`
   - the complete source-backed Structural Value Override package remains intact, including valid `anchor_classes[]`, item-specific `evidence_needed_for_stage_b[]`, specific `why_execution_event_not_required`, before-after change, changed judgment, and current-run source lineage

For either route, the non-selected route must be `not_applicable` with a specific `non_applicable_anchor_path_reason`, and Stage C must not have left unresolved `anchor_path_issue`, `selection_defect`, `source_direction_reversal`, or route-lineage conflict findings. Do not require a conventional execution anchor when the complete V3 non-execution route is the single validated path.
'''
if text.count(old) != 1:
    raise SystemExit(f"expected exactly one residual guard, found {text.count(old)}")
text = text.replace(old, new)
text = text.replace(
    "If only individual candidates have lineage or execution-anchor gaps while the overall lineage is valid, exclude those candidates from evidence QC and record them as:",
    "If only individual candidates have lineage or anchor-path gaps while the overall lineage is valid, exclude those candidates from evidence QC and record them as:",
)
text = text.replace(
    "- `addable_hold_execution_anchor_gap`",
    "- `addable_hold_anchor_path_gap`",
)
path.write_text(text, encoding="utf-8")
