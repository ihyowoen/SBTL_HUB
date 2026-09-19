#!/usr/bin/env python3
"""Stage-exit schema contract checker for lineage, dates, source audit and Related."""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

# Direct execution (`python validation_scripts/stage_artifact_contract_check.py`)
# starts with validation_scripts/ rather than the repository root on sys.path.
# Add the root before absolute package imports so the documented 0.7/0.8 CLI
# works exactly like module/unittest execution.
_REPO_ROOT = str(Path(__file__).resolve().parent.parent)
if _REPO_ROOT not in sys.path:
    sys.path.insert(0, _REPO_ROOT)

from validation_scripts.stage_a_v4_contract import validate_stage_a_v4_spec
from validation_scripts.stage_a_v4_hardening import validate_stage_a_v4_hardening

STAGE_TOP_LEVEL = {
    "A": [
        "stage_a_validity_status", "artifact_consistency_status", "csv_schema_status",
        "review_pool_partition_status", "strict_pass_gate_metadata_status",
        "baseline_duplicate_screen_status",
    ],
    "B": [
        "lineage_integrity_status", "stage_a_validity_guard_applied",
        "strict_gate_metadata_preserved", "execution_anchor_metadata_preserved",
        "superseded_lineage_mixed", "manual_integrated_rule_mixed",
        "previous_run_output_mixed",
    ],
    "C": [
        "strict_gate_acceptance_guard_applied", "accepted_pool_lineage_status",
    ],
    "0.4": ["lineage_guard"],
    "0.5": ["lineage_integrity_status"],
    "0.6": ["upstream_lineage_integrity", "lineage_and_anchor_guard"],
    "0.7": ["lineage_and_anchor_guard"],
    "0.8": ["github_main_sync_gate", "lineage_merge_gate"],
}

# Presence is not enough for a production stage exit. These are the positive
# values required when an artifact is used to authorize a downstream formal
# operation. A batch carrying a blocked/false guard cannot be counted merely
# because its top-level `status` marker says PASS.
STAGE_TOP_LEVEL_EXPECTED = {
    "A": {
        "stage_a_validity_status": "PASS",
        "artifact_consistency_status": "PASS",
        "csv_schema_status": "PASS",
        "review_pool_partition_status": "PASS",
        "strict_pass_gate_metadata_status": "PASS",
        "baseline_duplicate_screen_status": "PASS",
    },
    "B": {
        "lineage_integrity_status": "PASS",
        "stage_a_validity_guard_applied": True,
        "strict_gate_metadata_preserved": True,
        "execution_anchor_metadata_preserved": True,
        "superseded_lineage_mixed": False,
        "manual_integrated_rule_mixed": False,
        "previous_run_output_mixed": False,
    },
    "C": {
        "strict_gate_acceptance_guard_applied": True,
        "accepted_pool_lineage_status": "PASS",
    },
    "0.4": {"lineage_guard": "PASS"},
    "0.5": {"lineage_integrity_status": "PASS"},
    "0.6": {
        "upstream_lineage_integrity": "PASS",
        "lineage_and_anchor_guard": "PASS",
    },
    "0.7": {"lineage_and_anchor_guard": "PASS"},
}

# A declared stage is authoritative. In particular, repair/revise artifacts such
# as 0.2R/0.3R may not masquerade as the re-established ordinary B/C exits just
# because they happen to carry a similarly named bucket.
DECLARED_STAGE_ALIASES = {
    "A": {"a", "stage_a", "0.1"},
    "B": {"b", "stage_b", "0.2"},
    "C": {"c", "stage_c", "0.3"},
    "0.4": {"0.4"},
    "0.5": {"0.5"},
    "0.6": {"0.6"},
    "0.7": {"0.7"},
    "0.8": {"0.8"},
}

BUCKETS = {
    "A": ["strict_passed_spec"],
    "B": ["draft_cards", "draft_card"],
    "C": ["accepted_fact_safe", "revise_required", "rejected"],
    "0.4": ["addable_merge_safe"],
    "0.5": ["evidence_complete_and_source_claim_covered"],
    "0.6": ["content_enriched_and_language_polished"],
    "0.7": ["publish_ready"],
    "0.8": ["github_merge_ready"],
}

PROMPT_04_ROUTE_PASS_BUCKETS = (
    "addable_merge_safe_new_unrelated",
    "addable_merge_safe_distinct_follow_up",
    "addable_merge_safe_program_lineage",
)
PROMPT_04_OUTCOMES = set(PROMPT_04_ROUTE_PASS_BUCKETS)
PASS_SOURCE_DIVERSITY = {
    "PASS_MULTI_SOURCE",
    "PASS_OFFICIAL_OR_PRIMARY_SINGLE_SOURCE_EXCEPTION",
}
PASS_RELATION_TYPES = {
    "new_unrelated_event",
    "distinct_follow_up",
    "program_lineage",
}

ITEM_REQUIRED = {
    "A": [
        "spec_id", "strict_pass_gate", "execution_anchor_type", "baseline_relation",
        "related_prepass", "date_role", "selection_policy_version", "selection_route",
        "execution_credibility_gate", "independent_cardability_gate", "anchor_classes",
        "decision_news_value_score", "decision_value_breakdown",
        "decision_value_classification", "publication_urgency",
        "systemic_scale_denominator", "denominator_gap", "prior_state",
        "new_verified_fact", "changed_judgment", "uncertainty_resolved",
        "remaining_uncertainty", "incremental_information",
        "baseline_expectation_changed", "decision_relevance",
        "evidence_needed_for_stage_b", "next_confirmation_points",
        "structural_non_execution_reason", "why_execution_event_not_required",
        "technology_evidence_level", "policy_stage", "novelty_cap_basis",
    ],
    "B": ["source_spec_id", "fact_sources", "related_evidence_review", "date_role"],
    "C": ["source_spec_id", "fact_sources", "related_lineage", "date_role"],
    "0.4": ["source_spec_id", "event_fingerprint", "related_lineage", "addability_outcome"],
    "0.5": [
        "source_spec_id", "source_diversity_status", "source_discovery_ledger",
        "related_lineage", "date_role",
    ],
    "0.6": [
        "source_spec_id", "content_enriched", "language_terminology_polished",
        "related_lineage", "date_role", "source_diversity_status",
    ],
    "0.7": [
        "source_spec_id", "final_qc_gates", "related_lineage",
        "source_diversity_status",
    ],
    "0.8": [
        "id", "source_spec_id", "related_lineage", "date_role",
        "source_diversity_status", "merge_prep",
    ],
}


def item_marker(item):
    identifier = item.get("id") or item.get("source_spec_id") or item.get("spec_id")
    if identifier:
        return ("id", str(identifier))
    return ("value", json.dumps(item, ensure_ascii=False, sort_keys=True))


def _bucket_items(payload, bucket):
    value = payload.get(bucket)
    if isinstance(value, dict):
        return [value]
    if isinstance(value, list):
        return [item for item in value if isinstance(item, dict)]
    return []


def collect_items(payload, stage):
    # Preserve every emitted row. Duplicate candidate identities are not a
    # normalization concern: they are contradictory stage outcomes and must be
    # surfaced by the production checker rather than silently discarded.
    items = []
    for bucket in BUCKETS.get(stage, []):
        items.extend(_bucket_items(payload, bucket))
    return items


def bucket_item_count(payload, bucket):
    return len(_bucket_items(payload, bucket))


def _pass_marker(value):
    if value == "PASS" or value is True:
        return True
    if isinstance(value, dict):
        return value.get("status") == "PASS"
    return False


def _non_empty_object(value):
    return isinstance(value, dict) and bool(value)


def _non_empty_string(value):
    return isinstance(value, str) and bool(value.strip())


VISIBLE_COPY_FIELDS = ("sub", "gate", "fact", "implication")
DENSITY_DIMENSIONS = (
    "prior_state",
    "changed_state",
    "quantitative_anchor",
    "boundary_or_uncertainty",
    "transmission_path",
    "next_watchpoint",
)
CONTENT_BASELINE_STRATEGY = "nearest_upstream_visible_copy_0.5_0.4_C"
PROMPT_06_PATH = "docs/llm_prompts/v1/08_PROMPT_0_6_Content_Polish.md"
PRESENTATION_HTML_TAG_RE = re.compile(
    r"</?(?:strong|b|em|i|u|s|del|mark|span|small|sub|sup)(?:\s+[^<>]*?)?\s*/?>",
    re.IGNORECASE,
)


def _prompt_06_version(item):
    if not isinstance(item, dict):
        return None
    for key in ("prompt_provenance_0_6", "prompt_provenance"):
        provenance = item.get(key)
        if not isinstance(provenance, dict):
            continue
        version = provenance.get("prompt_version")
        if isinstance(version, str) and version.startswith("PROMPT_0_6_"):
            return version
    return None


def _requires_v5_content_audit(item, locked_prompt_version=None):
    version = locked_prompt_version if locked_prompt_version is not None else _prompt_06_version(item)
    return not (isinstance(version, str) and version.startswith("PROMPT_0_6_V4_"))


def _extract_prompt_06_version(text):
    if not isinstance(text, str):
        return None
    match = re.search(r"\*\*Version:\*\*\s*`?([^\s`]+)", text)
    return match.group(1).strip() if match else None


def _artifact_locked_prompt_06_version(payload):
    provenance = payload.get("prompt_provenance") if isinstance(payload, dict) else None
    declared = provenance.get("prompt_version") if isinstance(provenance, dict) else None
    base = payload.get("base_main_commit_sha") if isinstance(payload, dict) else None
    if isinstance(base, str) and len(base) == 40:
        proc = subprocess.run(
            ["git", "-C", _REPO_ROOT, "show", f"{base}:{PROMPT_06_PATH}"],
            text=True, capture_output=True,
        )
        if proc.returncode != 0:
            detail = (proc.stderr or proc.stdout or "git show failed").strip()
            return None, declared, f"locked Prompt 0.6 cannot be read at {base}: {detail[:240]}"
        locked = _extract_prompt_06_version(proc.stdout)
        if not locked:
            return None, declared, f"locked Prompt 0.6 version marker missing at {base}:{PROMPT_06_PATH}"
        return locked, declared, None
    return declared if isinstance(declared, str) else None, declared, None


def _strip_paired_presentation_markup(text):
    if text.strip() in {"**","__","~~","`","*","_"}:
        return ""
    patterns = (
        r"\*\*(?=\S)(.+?)(?<=\S)\*\*",
        r"__(?=\S)(.+?)(?<=\S)__",
        r"`(?=\S)(.+?)(?<=\S)`",
        r"(?<!\w)\*(?=\S)(.+?)(?<=\S)\*(?!\w)",
        r"(?<!\w)_(?=\S)(.+?)(?<=\S)_(?!\w)",
    )
    previous = None
    while previous != text:
        previous = text
        for pattern in patterns:
            text = re.sub(pattern, r"\1", text)
    return text


def _normalize_text(value):
    if not isinstance(value, str):
        return value
    text = value
    text = re.sub(r"\[([^\]]+)\]\([^)]*\)", r"\1", text)
    text = PRESENTATION_HTML_TAG_RE.sub("", text)
    text = re.sub(r"^\s{0,3}#{1,6}\s+", "", text)
    text = re.sub(r"^\s*[-+>]\s+", "", text)
    text = _strip_paired_presentation_markup(text)
    return " ".join(text.split())


def _normalized_visible_value(field, value):
    if field in {"sub", "gate", "fact"}:
        normalized = _normalize_text(value)
        return normalized if isinstance(normalized, str) and normalized else None
    if field == "implication":
        if not isinstance(value, list) or not value:
            return None
        normalized = tuple(_normalize_text(x) for x in value)
        if any(not isinstance(x, str) or not x for x in normalized):
            return None
        return normalized
    return None


def _row_evidence_tokens(item):
    tokens = set()
    if not isinstance(item, dict):
        return tokens
    sources = item.get("fact_sources")
    if isinstance(sources, list):
        for source in sources:
            if not isinstance(source, dict):
                continue
            for key in ("id", "source_id", "url", "source_url"):
                value = source.get(key)
                if _non_empty_string(value):
                    tokens.add(value.strip())
    ledger = item.get("source_discovery_ledger")
    if isinstance(ledger, list):
        for entry in ledger:
            if not isinstance(entry, dict):
                continue
            for key in ("source_id", "source_url", "canonical_url"):
                value = entry.get(key)
                if _non_empty_string(value):
                    tokens.add(value.strip())
    coverage = item.get("claim_source_coverage")
    if isinstance(coverage, dict):
        visible = coverage.get("visible_fact")
        if isinstance(visible, dict):
            refs = visible.get("supported_by_source_ids")
            if isinstance(refs, list):
                tokens.update(x.strip() for x in refs if _non_empty_string(x))
    return tokens


def _dimension_evidence_findings(item, density, scope, true_dimensions):
    findings = []
    mapping = density.get("dimension_evidence")
    if not isinstance(mapping, dict) or set(mapping) != set(true_dimensions):
        findings.append(_field_finding(
            scope,
            "content_enrichment_audit.density_audit.dimension_evidence",
            f"exact mapping for true dimensions {sorted(true_dimensions)}",
            mapping,
            "zero-delta exception must bind every claimed density dimension to visible copy and evidence",
        ))
        return findings

    evidence_tokens = _row_evidence_tokens(item)
    if not evidence_tokens:
        findings.append(_field_finding(
            scope,
            "content_enrichment_audit.density_audit.dimension_evidence",
            "references resolvable against fact_sources/source_discovery/claim coverage",
            mapping,
            "zero-delta exception requires concrete upstream evidence tokens",
        ))
        return findings

    for name in true_dimensions:
        entry = mapping.get(name)
        if not isinstance(entry, dict):
            findings.append(_field_finding(
                scope, f"content_enrichment_audit.density_audit.dimension_evidence.{name}",
                "object", entry, "dimension evidence must be structured",
            ))
            continue
        fields = entry.get("fields")
        if not isinstance(fields, list) or not fields or len(fields) != len(set(fields)) \
                or any(field not in VISIBLE_COPY_FIELDS for field in fields):
            findings.append(_field_finding(
                scope, f"content_enrichment_audit.density_audit.dimension_evidence.{name}.fields",
                f"non-empty unique subset of {list(VISIBLE_COPY_FIELDS)}", fields,
                "each claimed dimension must name the concrete visible field(s) that express it",
            ))
        else:
            empty_refs = [field for field in fields if _normalized_visible_value(field, item.get(field)) is None]
            if empty_refs:
                findings.append(_field_finding(
                    scope, f"content_enrichment_audit.density_audit.dimension_evidence.{name}.fields",
                    "only non-empty governed visible fields", fields,
                    f"dimension evidence references empty/missing fields {empty_refs}",
                ))
        refs = entry.get("evidence_refs")
        if not isinstance(refs, list) or not refs or any(not _non_empty_string(x) for x in refs):
            findings.append(_field_finding(
                scope, f"content_enrichment_audit.density_audit.dimension_evidence.{name}.evidence_refs",
                "non-empty evidence refs", refs,
                "each claimed dimension must bind to concrete upstream evidence",
            ))
        else:
            unknown = [x for x in refs if x.strip() not in evidence_tokens]
            if unknown:
                findings.append(_field_finding(
                    scope, f"content_enrichment_audit.density_audit.dimension_evidence.{name}.evidence_refs",
                    "refs present in fact_sources/source_discovery/claim coverage", unknown,
                    "dimension evidence contains unbound references",
                ))
    return findings


def _content_enrichment_audit_findings(item, scope):
    findings = []
    audit = item.get("content_enrichment_audit")
    if not _non_empty_object(audit):
        return [_field_finding(
            scope, "content_enrichment_audit", "non-empty structured audit", audit,
            "0.6 V5+ content_enriched=true requires a machine-checkable enrichment audit",
        )]

    if audit.get("baseline_strategy") != CONTENT_BASELINE_STRATEGY:
        findings.append(_field_finding(
            scope, "content_enrichment_audit.baseline_strategy", CONTENT_BASELINE_STRATEGY,
            audit.get("baseline_strategy"),
            "0.6 must use the governed nearest-upstream visible-copy baseline",
        ))

    changed = audit.get("changed_fields")
    changed_valid = isinstance(changed, list) and all(field in VISIBLE_COPY_FIELDS for field in changed) \
        and len(changed) == len(set(changed))
    if not changed_valid:
        findings.append(_field_finding(
            scope, "content_enrichment_audit.changed_fields",
            f"unique subset of {list(VISIBLE_COPY_FIELDS)}", changed,
            "declared visible-copy changes must use only governed content fields",
        ))

    if changed_valid and changed:
        empty_changed = [
            field for field in changed
            if _normalized_visible_value(field, item.get(field)) is None
        ]
        if empty_changed:
            findings.append(_field_finding(
                scope, "content_enrichment_audit.changed_fields",
                "declared changed fields with non-empty normalized visible copy",
                empty_changed,
                "removal/null/empty/format-only values cannot be certified as changed content",
            ))

    no_change = audit.get("no_change_required")
    if not isinstance(no_change, bool):
        findings.append(_field_finding(
            scope, "content_enrichment_audit.no_change_required", "boolean", no_change,
            "0.6 must explicitly attest whether an unchanged-copy exception is being used",
        ))
    elif changed_valid:
        if not changed and no_change is not True:
            findings.append(_field_finding(
                scope, "content_enrichment_audit.no_change_required", True, no_change,
                "an empty declared delta must use the explicit no-change exception",
            ))
        if changed and no_change is not False:
            findings.append(_field_finding(
                scope, "content_enrichment_audit.no_change_required", False, no_change,
                "a declared visible-copy delta cannot simultaneously claim no_change_required",
            ))

    density = audit.get("density_audit")
    if not _non_empty_object(density):
        findings.append(_field_finding(
            scope, "content_enrichment_audit.density_audit", "non-empty structured audit", density,
            "0.6 passing content requires a Deep Summary density audit",
        ))
        return findings

    if density.get("status") != "PASS":
        findings.append(_field_finding(
            scope, "content_enrichment_audit.density_audit.status", "PASS",
            density.get("status"),
            "0.6 passing content requires a passing density audit",
        ))

    dimensions = density.get("dimensions")
    valid_dimensions = False
    true_dimensions = []
    if not isinstance(dimensions, dict):
        findings.append(_field_finding(
            scope, "content_enrichment_audit.density_audit.dimensions",
            f"object with boolean keys {list(DENSITY_DIMENSIONS)}", dimensions,
            "density audit must explicitly evaluate every governed Deep Summary dimension",
        ))
    else:
        missing = [name for name in DENSITY_DIMENSIONS if name not in dimensions]
        invalid = [name for name in DENSITY_DIMENSIONS if name in dimensions and not isinstance(dimensions[name], bool)]
        extra = [name for name in dimensions if name not in DENSITY_DIMENSIONS]
        if missing or invalid or extra:
            findings.append(_field_finding(
                scope, "content_enrichment_audit.density_audit.dimensions",
                f"exact boolean keys {list(DENSITY_DIMENSIONS)}", dimensions,
                f"density dimensions malformed; missing={missing}, invalid={invalid}, extra={extra}",
            ))
        else:
            valid_dimensions = True
            true_dimensions = [name for name in DENSITY_DIMENSIONS if dimensions[name]]
            actual_count = len(true_dimensions)
            declared_count = density.get("supported_dimension_count")
            if not isinstance(declared_count, int) or isinstance(declared_count, bool):
                findings.append(_field_finding(
                    scope, "content_enrichment_audit.density_audit.supported_dimension_count",
                    "non-boolean integer", declared_count,
                    "supported_dimension_count must be a numeric count, not a boolean",
                ))
            elif declared_count != actual_count:
                findings.append(_field_finding(
                    scope, "content_enrichment_audit.density_audit.supported_dimension_count",
                    actual_count, declared_count,
                    "supported_dimension_count must equal the audited true dimensions",
                ))

    if not _non_empty_string(density.get("evidence_notes")):
        findings.append(_field_finding(
            scope, "content_enrichment_audit.density_audit.evidence_notes",
            "non-empty evidence-bounded explanation", density.get("evidence_notes"),
            "density audit must explain its evidence-supported dimensions",
        ))

    if changed_valid and not changed and no_change is True:
        if not _non_empty_string(audit.get("no_change_reason")):
            findings.append(_field_finding(
                scope, "content_enrichment_audit.no_change_reason",
                "non-empty reason", audit.get("no_change_reason"),
                "zero-delta exception requires an explicit reason",
            ))
        if valid_dimensions:
            if len(true_dimensions) < 4:
                findings.append(_field_finding(
                    scope, "content_enrichment_audit.density_audit.supported_dimension_count",
                    ">= 4", len(true_dimensions),
                    "zero-delta exception requires at least four supported dimensions",
                ))
            if dimensions.get("changed_state") is not True:
                findings.append(_field_finding(
                    scope, "content_enrichment_audit.density_audit.dimensions.changed_state",
                    True, dimensions.get("changed_state"),
                    "zero-delta exception requires changed_state=true",
                ))
            findings.extend(_dimension_evidence_findings(item, density, scope, true_dimensions))

    if changed_valid and changed and no_change is False and valid_dimensions:
        if not true_dimensions:
            findings.append(_field_finding(
                scope, "content_enrichment_audit.density_audit.supported_dimension_count",
                ">= 1", 0,
                "a changed visible-copy delta needs at least one evidence-supported Deep Summary dimension",
            ))
        else:
            findings.extend(_dimension_evidence_findings(item, density, scope, true_dimensions))
            mapping = density.get("dimension_evidence")
            if isinstance(mapping, dict):
                bound_changed = {
                    field
                    for entry in mapping.values()
                    if isinstance(entry, dict)
                    for field in entry.get("fields", [])
                    if field in set(changed)
                }
                if not bound_changed:
                    findings.append(_field_finding(
                        scope, "content_enrichment_audit.density_audit.dimension_evidence",
                        "at least one true dimension bound to a declared changed field",
                        mapping,
                        "terminology/format-only string deltas cannot satisfy substantive content enrichment",
                    ))
    return findings


def _top_level_gate_finding(stage, field, value):
    expected = STAGE_TOP_LEVEL_EXPECTED.get(stage, {}).get(field)
    if expected is not None:
        if expected == "PASS":
            if _pass_marker(value):
                return None
        elif value == expected:
            return None
        return {
            "scope": "top_level",
            "field": field,
            "expected": expected,
            "actual": value,
            "message": "stage-specific production gate must carry its passing value",
        }

    if stage == "0.8" and field == "github_main_sync_gate":
        if isinstance(value, dict) and value.get("status") == "PASS" \
                and value.get("baseline_locked") is True \
                and value.get("main_unchanged_since_locked_preflight") is True \
                and value.get("silent_rebase_performed") is False:
            return None
        return {
            "scope": "top_level",
            "field": field,
            "expected": "structured PASS with baseline_locked/main_unchanged true and silent_rebase false",
            "actual": value,
            "message": "0.8 github/main synchronization gate requires the structured production proof",
        }

    if stage == "0.8" and field == "lineage_merge_gate":
        if isinstance(value, dict) \
                and value.get("final_qc_lineage_passed") is True \
                and value.get("anchor_path_lineage_passed") is True \
                and value.get("github_ready_allowed") is True \
                and value.get("anchor_path_hold_count") == 0:
            return None
        return {
            "scope": "top_level",
            "field": field,
            "expected": "structured passing lineage merge gate with zero holds",
            "actual": value,
            "message": "0.8 lineage merge gate requires the structured zero-hold production proof",
        }
    return None


def _field_finding(scope, field, expected, actual, message):
    return {
        "scope": scope,
        "field": field,
        "expected": expected,
        "actual": actual,
        "message": message,
    }


def _related_lineage_findings(item, scope):
    findings = []
    lineage = item.get("related_lineage")
    if not _non_empty_object(lineage):
        return [_field_finding(scope, "related_lineage", "non-empty object with status=PASS", lineage,
                               "passing downstream item requires a concrete Related lineage decision")]
    if lineage.get("status") != "PASS":
        findings.append(_field_finding(scope, "related_lineage.status", "PASS", lineage.get("status"),
                                       "passing downstream item cannot carry blocked/unresolved Related lineage"))
    relation_type = lineage.get("relation_type")
    if relation_type not in PASS_RELATION_TYPES:
        findings.append(_field_finding(scope, "related_lineage.relation_type", sorted(PASS_RELATION_TYPES), relation_type,
                                       "passing new-card lineage must use a publishable canonical relation type"))
    related_ids = lineage.get("related_ids")
    if not isinstance(related_ids, list) or any(not _non_empty_string(value) for value in related_ids):
        findings.append(_field_finding(scope, "related_lineage.related_ids", "array of production/candidate IDs", related_ids,
                                       "Related lineage targets must use an array representation"))
    elif relation_type == "new_unrelated_event" and related_ids:
        findings.append(_field_finding(scope, "related_lineage.related_ids", [], related_ids,
                                       "new_unrelated_event must not carry Related targets"))
    elif relation_type in {"distinct_follow_up", "program_lineage"} and not related_ids:
        findings.append(_field_finding(scope, "related_lineage.related_ids", "non-empty predecessor/program target array", related_ids,
                                       "follow-up/program lineage requires a direct target"))
    return findings


def _item_value_findings(stage, item, scope, locked_prompt_version=None):
    findings = []
    if stage != "A" and not _non_empty_string(item.get("source_spec_id")):
        findings.append(_field_finding(scope, "source_spec_id", "non-empty string", item.get("source_spec_id"),
                                       "passing downstream item must preserve candidate identity"))

    if stage in {"B", "C"}:
        fact_sources = item.get("fact_sources")
        if not isinstance(fact_sources, list) or not fact_sources or any(not isinstance(row, dict) for row in fact_sources):
            findings.append(_field_finding(scope, "fact_sources", "non-empty array of source objects", fact_sources,
                                           "passing evidence/fact-safe item requires body-level evidence records"))

    if stage == "B":
        review = item.get("related_evidence_review")
        if not _non_empty_object(review):
            findings.append(_field_finding(scope, "related_evidence_review", "non-empty object with status=PASS", review,
                                           "Stage B passing draft requires resolved Related evidence review"))
        elif review.get("status") != "PASS":
            findings.append(_field_finding(scope, "related_evidence_review.status", "PASS", review.get("status"),
                                           "Stage B passing draft requires the canonical resolved Related review status"))
        if not _non_empty_object(item.get("date_role")):
            findings.append(_field_finding(scope, "date_role", "non-empty object", item.get("date_role"),
                                           "Stage B passing draft requires a concrete date-role decision"))

    if stage in {"C", "0.4", "0.5", "0.6", "0.7", "0.8"}:
        findings.extend(_related_lineage_findings(item, scope))

    if stage in {"C", "0.5", "0.6", "0.7", "0.8"} and not _non_empty_object(item.get("date_role")):
        findings.append(_field_finding(scope, "date_role", "non-empty object", item.get("date_role"),
                                       "passing downstream item requires a concrete date-role decision"))

    if stage == "0.4":
        fingerprint = item.get("event_fingerprint")
        if not (_non_empty_object(fingerprint) or _non_empty_string(fingerprint)):
            findings.append(_field_finding(scope, "event_fingerprint", "non-empty object or string", fingerprint,
                                           "0.4 addability PASS requires a concrete event fingerprint"))

    if stage in {"0.5", "0.6", "0.7", "0.8"}:
        source_status = item.get("source_diversity_status")
        if source_status not in PASS_SOURCE_DIVERSITY:
            findings.append(_field_finding(scope, "source_diversity_status", sorted(PASS_SOURCE_DIVERSITY), source_status,
                                           "passing downstream bucket cannot carry HOLD/FAIL source-diversity state"))

    if stage == "0.5" and not isinstance(item.get("source_discovery_ledger"), list):
        findings.append(_field_finding(scope, "source_discovery_ledger", "array", item.get("source_discovery_ledger"),
                                       "0.5 passing item must preserve the source-discovery ledger"))

    if stage == "0.6":
        for field in ("content_enriched", "language_terminology_polished"):
            if item.get(field) is not True:
                findings.append(_field_finding(scope, field, True, item.get(field),
                                               "combined 0.6 passing bucket requires both component attestations=true"))
        declared_prompt_version = _prompt_06_version(item)
        if locked_prompt_version is not None and declared_prompt_version is not None \
                and declared_prompt_version != locked_prompt_version:
            findings.append(_field_finding(
                scope, "prompt_provenance_0_6.prompt_version", locked_prompt_version,
                declared_prompt_version,
                "item-level Prompt 0.6 version must match the locked artifact/base contract",
            ))
        if _requires_v5_content_audit(item, locked_prompt_version=locked_prompt_version):
            findings.extend(_content_enrichment_audit_findings(item, scope))

    if stage == "0.7":
        gates = item.get("final_qc_gates")
        if not _non_empty_object(gates):
            findings.append(_field_finding(scope, "final_qc_gates", "non-empty object", gates,
                                           "publish_ready requires recorded Final-QC gate results"))
        elif "status" in gates and not _pass_marker(gates.get("status")):
            findings.append(_field_finding(scope, "final_qc_gates.status", "PASS", gates.get("status"),
                                           "publish_ready cannot carry a non-passing final_qc_gates status"))

    if stage == "0.8":
        if not _non_empty_string(item.get("id")):
            findings.append(_field_finding(scope, "id", "final production ID", item.get("id"),
                                           "github_merge_ready item requires its final production ID"))
        merge_prep = item.get("merge_prep")
        if not _non_empty_object(merge_prep):
            findings.append(_field_finding(scope, "merge_prep", "non-empty object", merge_prep,
                                           "github_merge_ready item requires concrete merge-prep results"))
        elif "status" in merge_prep and not _pass_marker(merge_prep.get("status")):
            findings.append(_field_finding(scope, "merge_prep.status", "PASS", merge_prep.get("status"),
                                           "github_merge_ready item cannot carry a failing merge-prep status"))

    return findings


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("stage", choices=sorted(STAGE_TOP_LEVEL))
    parser.add_argument("input")
    args = parser.parse_args()

    payload = json.loads(Path(args.input).read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        print("input must be a JSON object", file=sys.stderr)
        return 2

    findings = []
    declared_stage = payload.get("stage")
    if declared_stage is not None:
        if not isinstance(declared_stage, str) or declared_stage.strip().lower() not in DECLARED_STAGE_ALIASES[args.stage]:
            findings.append({
                "scope": "top_level",
                "field": "stage",
                "expected": sorted(DECLARED_STAGE_ALIASES[args.stage]),
                "actual": declared_stage,
                "message": "declared repair/revise or mismatched stage cannot substitute for the requested ordinary stage exit",
            })

    if args.stage == "0.8" and payload.get("status") not in {"PASS", "GITHUB_MERGE_READY"}:
        findings.append(_field_finding("top_level", "status", ["PASS", "GITHUB_MERGE_READY"], payload.get("status"),
                                       "0.8 merge-prep artifact must itself be passing"))

    for field in STAGE_TOP_LEVEL[args.stage]:
        if field not in payload:
            findings.append({"scope": "top_level", "field": field})
            continue
        gate_finding = _top_level_gate_finding(args.stage, field, payload[field])
        if gate_finding:
            findings.append(gate_finding)

    locked_prompt_version = None
    if args.stage == "0.6":
        locked_prompt_version, declared_artifact_prompt_version, prompt_resolution_error = _artifact_locked_prompt_06_version(payload)
        if prompt_resolution_error:
            findings.append(_field_finding(
                "top_level", "base_main_commit_sha",
                "readable locked Prompt 0.6 with version marker",
                payload.get("base_main_commit_sha"),
                prompt_resolution_error,
            ))
            locked_prompt_version = "UNRESOLVED_LOCKED_PROMPT_FAIL_CLOSED"
        if locked_prompt_version is not None and isinstance(declared_artifact_prompt_version, str) \
                and declared_artifact_prompt_version != locked_prompt_version:
            findings.append(_field_finding(
                "top_level", "prompt_provenance.prompt_version", locked_prompt_version,
                declared_artifact_prompt_version,
                "artifact Prompt 0.6 version must match the prompt stored at the locked base when that commit is available",
            ))

    items = collect_items(payload, args.stage)
    marker_counts = {}
    for item in items:
        marker = item_marker(item)
        marker_counts[marker] = marker_counts.get(marker, 0) + 1
    for marker, count in marker_counts.items():
        if count > 1:
            findings.append({
                "scope": marker[1],
                "field": "duplicate_stage_item_identity",
                "actual": count,
                "message": "the same candidate/item identity cannot appear more than once in a stage artifact",
            })

    if args.stage in {"A", "0.5", "0.6", "0.7", "0.8"} and not items:
        findings.append({"scope": "top_level", "field": f"non_empty_{BUCKETS[args.stage][0]}"})

    if args.stage == "0.4":
        route_specific_count = sum(bucket_item_count(payload, bucket) for bucket in PROMPT_04_ROUTE_PASS_BUCKETS)
        if route_specific_count and not items:
            findings.append({
                "scope": "top_level",
                "field": "addable_merge_safe",
                "message": "route-specific passing buckets cannot substitute for addable_merge_safe[]",
            })

    accepted_c_markers = {item_marker(item) for item in _bucket_items(payload, "accepted_fact_safe")}
    for index, item in enumerate(items):
        item_id = item.get("id") or item.get("source_spec_id") or item.get("spec_id")
        for field in ITEM_REQUIRED.get(args.stage, []):
            if field not in item:
                findings.append({"scope": item_id, "field": field})
        if args.stage == "A":
            v4_messages: list[str] = []
            validate_stage_a_v4_spec(item, index, v4_messages, require_contract=True)
            validate_stage_a_v4_hardening(item, index, v4_messages, require_contract=True)
            for message in v4_messages:
                findings.append({
                    "scope": item_id,
                    "contract": "stage_a_v4",
                    "message": message,
                })
        if args.stage == "0.4" and item.get("addability_outcome") not in PROMPT_04_OUTCOMES:
            findings.append({
                "scope": item_id,
                "field": "addability_outcome",
                "message": "must be a validator-bound addable_merge_safe route",
            })

        # Stage C artifacts also contain revise/rejected rows. Only
        # accepted_fact_safe is a passing bucket; every other stage bucket here
        # is itself the passing bucket consumed by the formal chain.
        if args.stage != "A" and (args.stage != "C" or item_marker(item) in accepted_c_markers):
            findings.extend(_item_value_findings(
                args.stage, item, item_id, locked_prompt_version=locked_prompt_version
            ))

    result = {
        "status": "PASS" if not findings else "BLOCKED_STAGE_OUTPUT_SCHEMA_NONCOMPLIANT",
        "stage": args.stage,
        "item_count": len(items),
        "missing_count": len(findings),
        "findings": findings,
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 1 if findings else 0


if __name__ == "__main__":
    sys.exit(main())
