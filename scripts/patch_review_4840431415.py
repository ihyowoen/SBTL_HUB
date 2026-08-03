#!/usr/bin/env python3
from pathlib import Path


def replace_once(path: str, old: str, new: str, label: str) -> None:
    p = Path(path)
    text = p.read_text(encoding="utf-8")
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected exactly one match, found {count}")
    p.write_text(text.replace(old, new, 1), encoding="utf-8")


validator = "validation_scripts/related_lifecycle_check.py"

replace_once(
    validator,
    '''def relation_object(card: dict[str, Any]) -> dict[str, Any] | None:\n''',
    '''def build_provisional_target_index(\n    cards: list[dict[str, Any]],\n) -> tuple[dict[str, dict[str, Any]], set[str]]:\n    """Resolve provisional candidate IDs only within the current-run scope."""\n    index: dict[str, dict[str, Any]] = {}\n    ambiguous: set[str] = set()\n    for card in cards:\n        for identifier in provisional_card_identifiers(card):\n            existing = index.get(identifier)\n            if existing is not None and existing is not card:\n                ambiguous.add(identifier)\n            else:\n                index[identifier] = card\n    for identifier in ambiguous:\n        index.pop(identifier, None)\n    return index, ambiguous\n\n\ndef relation_object(card: dict[str, Any]) -> dict[str, Any] | None:\n''',
    "insert provisional target index",
)

replace_once(
    validator,
    '''def check_card(card: dict[str, Any], by_id: dict[str, dict[str, Any]], require_contract: bool):\n''',
    '''def check_card(\n    card: dict[str, Any],\n    by_id: dict[str, dict[str, Any]],\n    require_contract: bool,\n    allow_provisional_related: bool = False,\n    provisional_by_id: dict[str, dict[str, Any]] | None = None,\n    ambiguous_provisional_ids: set[str] | None = None,\n):\n''',
    "expand check_card signature",
)

replace_once(
    validator,
    '''    related = card.get("related") or []\n    errors = []\n    warnings = []\n''',
    '''    related = card.get("related") or []\n    provisional_by_id = provisional_by_id or {}\n    ambiguous_provisional_ids = ambiguous_provisional_ids or set()\n    errors = []\n    warnings = []\n''',
    "initialize provisional maps",
)

replace_once(
    validator,
    '''    declared = lineage.get("related_ids")\n    if isinstance(declared, list) and set(declared) != set(related):\n        errors.append("related_lineage.related_ids does not match related[]")\n\n    if relation_type == "new_unrelated_event" and related:\n        errors.append("new_unrelated_event must have empty related[]")\n    if relation_type in {"distinct_follow_up", "program_lineage"} and not related:\n        errors.append(f"{relation_type} requires at least one related ID")\n''',
    '''    declared = lineage.get("related_ids")\n    if isinstance(declared, list) and set(declared) != set(related):\n        errors.append("related_lineage.related_ids does not match related[]")\n\n    provisional = (\n        lineage.get("related_candidate_spec_ids")\n        or card.get("related_candidate_spec_ids")\n        or []\n    )\n    valid_provisional_edge = False\n    if allow_provisional_related and provisional:\n        if not isinstance(provisional, list):\n            errors.append("related_candidate_spec_ids must be a list")\n        else:\n            normalized_provisional = []\n            for value in provisional:\n                if not isinstance(value, str) or not value.strip():\n                    errors.append("related_candidate_spec_ids must contain non-empty strings")\n                    continue\n                normalized_provisional.append(value.strip())\n            if normalized_provisional != dedupe(normalized_provisional):\n                errors.append("related_candidate_spec_ids contains duplicate IDs")\n            for target in normalized_provisional:\n                if target in ambiguous_provisional_ids:\n                    errors.append(f"ambiguous provisional related ID: {target}")\n                    continue\n                resolved_target = provisional_by_id.get(target)\n                if resolved_target is card:\n                    errors.append("related_candidate_spec_ids contains self-reference")\n                elif resolved_target is None:\n                    errors.append(f"dangling provisional related ID: {target}")\n            valid_provisional_edge = bool(normalized_provisional) and not any(\n                message.startswith((\n                    "related_candidate_spec_ids",\n                    "ambiguous provisional related ID",\n                    "dangling provisional related ID",\n                ))\n                for message in errors\n            )\n\n    if relation_type == "new_unrelated_event" and (related or (allow_provisional_related and provisional)):\n        errors.append("new_unrelated_event must have no final or provisional related edges")\n    if (\n        relation_type in {"distinct_follow_up", "program_lineage"}\n        and not related\n        and not valid_provisional_edge\n    ):\n        errors.append(f"{relation_type} requires at least one final or allowed provisional related ID")\n''',
    "allow provisional candidate edges",
)

replace_once(
    validator,
    '''    parser.add_argument("--require-contract", action="store_true")\n    parser.add_argument("--report")\n    args = parser.parse_args()\n\n    _, cards = load_cards(args.input)\n''',
    '''    parser.add_argument("--require-contract", action="store_true")\n    parser.add_argument("--allow-provisional-related", action="store_true")\n    parser.add_argument("--report")\n    args = parser.parse_args()\n\n    if args.allow_provisional_related and not args.require_contract:\n        parser.error("--allow-provisional-related requires --require-contract")\n    if args.allow_provisional_related and not args.new_id_file:\n        parser.error("--allow-provisional-related requires --new-id-file current-run scope")\n\n    _, cards = load_cards(args.input)\n''',
    "add provisional CLI flag",
)

replace_once(
    validator,
    '''    selected = load_ids(args.new_id_file)\n    rows, scope = select_related_scope(cards, selected)\n\n    findings = []\n''',
    '''    selected = load_ids(args.new_id_file)\n    rows, scope = select_related_scope(cards, selected)\n    if args.allow_provisional_related:\n        provisional_by_id, ambiguous_provisional_ids = build_provisional_target_index(rows)\n    else:\n        provisional_by_id, ambiguous_provisional_ids = {}, set()\n\n    findings = []\n''',
    "build current-run provisional map",
)

replace_once(
    validator,
    '''        errors, warnings = check_card(card, by_id, args.require_contract)\n''',
    '''        errors, warnings = check_card(\n            card,\n            by_id,\n            args.require_contract,\n            allow_provisional_related=args.allow_provisional_related,\n            provisional_by_id=provisional_by_id,\n            ambiguous_provisional_ids=ambiguous_provisional_ids,\n        )\n''',
    "pass provisional validation context",
)

# Final QC prompt and overlay generator: provisional edges are allowed only before Prompt 0.8.
for path in [
    "docs/llm_prompts/v1/09_PROMPT_0_7_Final_QC.md",
    "validation_scripts/apply_prompt_contract_overlays.py",
]:
    replace_once(
        path,
        '''- The Related lifecycle validator must match scope entries against `id`, `card_id`, `draft_id`, or `source_spec_id`; unmatched, empty, partial, or zero-match scope remains a hard failure.\n- Run `evidence_qc_v8_check.py`,\n  `related_lifecycle_check.py --require-contract --new-id-file <CURRENT_RUN_ID_FILE>` against the merged baseline/candidate validation artifact,\n''',
        '''- The Related lifecycle validator must match scope entries against `id`, `card_id`, `draft_id`, or `source_spec_id`; unmatched, empty, partial, ambiguous, or zero-match scope remains a hard failure.\n- Before Prompt 0.8 assigns production IDs, a current-run `distinct_follow_up` or `program_lineage` may carry candidate-to-candidate edges in `related_candidate_spec_ids` while `related[]` remains empty. Every provisional target must resolve uniquely within the current-run scope; dangling, ambiguous, duplicate, or self-referential provisional edges are hard failures.\n- Run `evidence_qc_v8_check.py`,\n  `related_lifecycle_check.py --require-contract --allow-provisional-related --new-id-file <CURRENT_RUN_ID_FILE>` against the merged baseline/candidate validation artifact,\n''',
        f"enable provisional Final QC in {path}",
    )

# Stage B revise: preserve the complete canonical V3 package.
path = "docs/llm_prompts/v1/04_PROMPT_0_2R_Stage_B_Revise.md"
replace_once(
    path,
    '''- If the selected route was already settled and only visible wording requires revision, preserve `anchor_path_validation` byte-for-byte.\n- If Stage C emitted `selected_anchor_path: unresolved`, this pass may resolve the route only from already-authorized, source-backed evidence in the current run. It must select exactly one of `execution` or `v3_non_execution`, set `anchor_path_qc_passed: true`, set exactly one route status to `pass`, set the other to `not_applicable`, and provide a specific `non_applicable_anchor_path_reason`.\n''',
    '''- If the selected route was already settled and only visible wording requires revision, preserve `anchor_path_validation` byte-for-byte.\n- If the settled route is `v3_non_execution`, also preserve the complete canonical Structural Value Override package byte-for-byte: `structural_value_override_applied`, `structural_value_override_reason`, `anchor_classes[]`, `evidence_needed_for_stage_b[]`, `why_execution_event_not_required`, `prior_state`, `new_verified_fact`, `changed_judgment`, `uncertainty_resolved`, `remaining_uncertainty`, `incremental_information`, `baseline_expectation_changed`, `decision_relevance`, and `next_confirmation_points[]`. A wording-only revision must not summarize, rename, drop, or regenerate these fields.\n- If Stage C emitted `selected_anchor_path: unresolved`, this pass may resolve the route only from already-authorized, source-backed evidence in the current run. It must select exactly one of `execution` or `v3_non_execution`, set `anchor_path_qc_passed: true`, set exactly one route status to `pass`, set the other to `not_applicable`, and provide a specific `non_applicable_anchor_path_reason`. When resolving to `v3_non_execution`, the complete canonical package above must be present and source-backed; existing non-null package fields must remain byte-for-byte stable unless the resolution change is explicitly recorded in `revision_change_log[]`.\n''',
    "preserve V3 package in Stage B revise rule",
)
replace_once(
    path,
    '''- `anchor_path_validation` for every format-risk item\n- `anchor_path_resolution_action: preserved|resolved_from_unresolved`\n''',
    '''- `anchor_path_validation` for every format-risk item\n- when `anchor_path_validation.selected_anchor_path = v3_non_execution`, the complete byte-for-byte canonical package: `structural_value_override_applied`, `structural_value_override_reason`, `anchor_classes[]`, `evidence_needed_for_stage_b[]`, `why_execution_event_not_required`, `prior_state`, `new_verified_fact`, `changed_judgment`, `uncertainty_resolved`, `remaining_uncertainty`, `incremental_information`, `baseline_expectation_changed`, `decision_relevance`, and `next_confirmation_points[]`\n- `anchor_path_resolution_action: preserved|resolved_from_unresolved`\n''',
    "add V3 package to revised_draft_cards schema",
)

# Stage C revise: consume and preserve the package in accepted and unresolved outputs.
path = "docs/llm_prompts/v1/05_PROMPT_0_3R_Stage_C_Revise.md"
replace_once(
    path,
    '''- for every format-risk item, consume the Stage B revise `anchor_path_validation` and validate exactly one source-backed route\n- accept a format-risk item only when `selected_anchor_path` is `execution` or `v3_non_execution`, `anchor_path_qc_passed: true`, exactly one route status is `pass`, and the other is `not_applicable` with a specific reason\n''',
    '''- for every format-risk item, consume the Stage B revise `anchor_path_validation` and validate exactly one source-backed route\n- when the selected route is `v3_non_execution`, consume and preserve byte-for-byte the complete canonical Structural Value Override package: `structural_value_override_applied`, `structural_value_override_reason`, `anchor_classes[]`, `evidence_needed_for_stage_b[]`, `why_execution_event_not_required`, `prior_state`, `new_verified_fact`, `changed_judgment`, `uncertainty_resolved`, `remaining_uncertainty`, `incremental_information`, `baseline_expectation_changed`, `decision_relevance`, and `next_confirmation_points[]`; missing, renamed, summarized, or mutated package fields prevent acceptance\n- accept a format-risk item only when `selected_anchor_path` is `execution` or `v3_non_execution`, `anchor_path_qc_passed: true`, exactly one route status is `pass`, and the other is `not_applicable` with a specific reason\n''',
    "validate V3 package in Stage C revise",
)
replace_once(
    path,
    '''- `anchor_path_validation` for every format-risk item, with a passing two-path schema\n- stage_c_revise_only: true\n''',
    '''- `anchor_path_validation` for every format-risk item, with a passing two-path schema\n- when `anchor_path_validation.selected_anchor_path = v3_non_execution`, the complete byte-for-byte canonical package: `structural_value_override_applied`, `structural_value_override_reason`, `anchor_classes[]`, `evidence_needed_for_stage_b[]`, `why_execution_event_not_required`, `prior_state`, `new_verified_fact`, `changed_judgment`, `uncertainty_resolved`, `remaining_uncertainty`, `incremental_information`, `baseline_expectation_changed`, `decision_relevance`, and `next_confirmation_points[]`\n- stage_c_revise_only: true\n''',
    "add V3 package to Stage C accepted schema",
)
replace_once(
    path,
    '''- `anchor_path_validation` when the item is format-risk, preserving the honest unresolved or failed state\n- remaining_issue_type\n''',
    '''- `anchor_path_validation` when the item is format-risk, preserving the honest unresolved or failed state\n- when any V3 override package fields entered the revise pass, preserve them byte-for-byte in `revise_required_again[]`; a later pass may complete missing fields only from already-authorized evidence and must record the resolution change\n- remaining_issue_type\n''',
    "preserve V3 package in revise_required_again",
)

# Focused regression coverage.
Path("validation_scripts/tests/test_review_4840431415_contracts.py").write_text(
    '''from __future__ import annotations\n\nimport json\nimport subprocess\nimport sys\nimport tempfile\nimport unittest\nfrom pathlib import Path\n\nROOT = Path(__file__).resolve().parents[2]\nVALIDATOR = ROOT / "validation_scripts/related_lifecycle_check.py"\n\n\ndef lifecycle(relation_type: str, related_candidate_spec_ids=None):\n    return {\n        "status": "PASS",\n        "same_event_checked": True,\n        "earliest_same_event_date_checked": True,\n        "relation_type": relation_type,\n        "related_ids": [],\n        "related_candidate_spec_ids": related_candidate_spec_ids or [],\n        "fresh_follow_up_anchor": "new verified timing change" if relation_type == "distinct_follow_up" else None,\n        "fresh_follow_up_anchor_class": "follow_up_probability_anchor" if relation_type == "distinct_follow_up" else None,\n        "incremental_fact_vs_predecessor": "schedule moved" if relation_type == "distinct_follow_up" else None,\n        "changed_judgment_vs_predecessor": "probability reduced" if relation_type == "distinct_follow_up" else None,\n        "reason": "current-run candidate relation",\n    }\n\n\nclass TestReview4840431415Contracts(unittest.TestCase):\n    def run_validator(self, allow_provisional: bool):\n        parent = {\n            "source_spec_id": "SPEC_PARENT",\n            "date": "2026-08-01",\n            "related": [],\n            "related_lineage": lifecycle("new_unrelated_event"),\n        }\n        child = {\n            "source_spec_id": "SPEC_CHILD",\n            "date": "2026-08-02",\n            "related": [],\n            "related_candidate_spec_ids": ["SPEC_PARENT"],\n            "related_lineage": lifecycle("distinct_follow_up", ["SPEC_PARENT"]),\n        }\n        with tempfile.TemporaryDirectory() as tmp:\n            tmp_path = Path(tmp)\n            cards = tmp_path / "cards.json"\n            ids = tmp_path / "ids.json"\n            cards.write_text(json.dumps({"cards": [parent, child]}), encoding="utf-8")\n            ids.write_text(json.dumps(["SPEC_PARENT", "SPEC_CHILD"]), encoding="utf-8")\n            cmd = [\n                sys.executable, str(VALIDATOR), str(cards),\n                "--require-contract", "--new-id-file", str(ids),\n            ]\n            if allow_provisional:\n                cmd.append("--allow-provisional-related")\n            return subprocess.run(cmd, cwd=ROOT, text=True, capture_output=True)\n\n    def test_final_qc_allows_uniquely_resolved_current_run_provisional_edge(self):\n        result = self.run_validator(True)\n        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)\n        self.assertEqual(json.loads(result.stdout)["status"], "PASS")\n\n    def test_final_id_gate_still_rejects_unresolved_provisional_only_edge(self):\n        result = self.run_validator(False)\n        self.assertNotEqual(result.returncode, 0)\n        self.assertIn("requires at least one final or allowed provisional related ID", result.stdout)\n\n    def test_final_qc_prompt_and_generator_use_provisional_flag(self):\n        needle = "--require-contract --allow-provisional-related --new-id-file <CURRENT_RUN_ID_FILE>"\n        for rel in [\n            "docs/llm_prompts/v1/09_PROMPT_0_7_Final_QC.md",\n            "validation_scripts/apply_prompt_contract_overlays.py",\n        ]:\n            self.assertIn(needle, (ROOT / rel).read_text(encoding="utf-8"))\n\n    def test_revise_outputs_preserve_complete_v3_package(self):\n        required = [\n            "structural_value_override_reason", "anchor_classes[]",\n            "evidence_needed_for_stage_b[]", "why_execution_event_not_required",\n            "prior_state", "new_verified_fact", "changed_judgment",\n            "uncertainty_resolved", "remaining_uncertainty",\n            "incremental_information", "baseline_expectation_changed",\n            "decision_relevance", "next_confirmation_points[]",\n        ]\n        for rel in [\n            "docs/llm_prompts/v1/04_PROMPT_0_2R_Stage_B_Revise.md",\n            "docs/llm_prompts/v1/05_PROMPT_0_3R_Stage_C_Revise.md",\n        ]:\n            text = (ROOT / rel).read_text(encoding="utf-8")\n            self.assertIn("complete byte-for-byte canonical package", text)\n            for field in required:\n                self.assertIn(field, text)\n\n\nif __name__ == "__main__":\n    unittest.main()\n''',
    encoding="utf-8",
)
