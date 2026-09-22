#!/usr/bin/env python3
"""Original-module PR385 characterization; never an authorization to publish.

Exit 0: this finite probe set meets its expectations (not proof of correctness).
Exit 1: at least one safety/positive-control expectation is violated.
Exit 2: setup/runtime error. All observed outputs are retained as JSON.
No monkeypatches, source excerpts, network requests, or production writes.
"""
from __future__ import annotations

import argparse
import copy
import hashlib
import importlib
import json
import subprocess
import sys
import traceback
from collections import Counter
from pathlib import Path

REVIEWED_HEAD = "bd7b7c835e45b70466ac599c5f7a17278e68eaa8"
GOVERNED_MODULES = (
    "validation_scripts/card_run_v4_binding_hardening.py",
    "validation_scripts/stage_artifact_contract_check.py",
    "validation_scripts/tests/test_content_enrichment_delta_contract.py",
    "validation_scripts/tests/test_review_5265937741_contracts.py",
    "docs/llm_prompts/v1/08_PROMPT_0_6_Content_Polish.md",
)
DENSE_DIMENSIONS = (
    "prior_state", "changed_state", "quantitative_anchor", "boundary_or_uncertainty",
)


def serial(value):
    if isinstance(value, dict):
        return {str(k): serial(v) for k, v in value.items()}
    if isinstance(value, (tuple, list)):
        return [serial(v) for v in value]
    return value


def git(repo, *args):
    return subprocess.check_output(["git", "-C", str(repo), *args], text=True).strip()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", type=Path, required=True)
    parser.add_argument("--expect-head", required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    repo = args.repo.resolve()
    results = []
    report = {
        "schema": "pr385.original-module-characterization.v1",
        "reviewed_head": REVIEWED_HEAD,
        "scope": "Components, content-enrichment gate with operation-card binding, and standalone audit helper. NOT full-run CLI or production publication.",
        "synthetic_fixture": True,
        "production_modified": False,
        "results": results,
    }
    try:
        head = git(repo, "rev-parse", "HEAD")
        report["tested_head"] = head
        if head != args.expect_head:
            raise RuntimeError(f"HEAD mismatch: expected {args.expect_head}, got {head}")
        identities = {}
        for name in GOVERNED_MODULES:
            path = repo / name
            actual = git(repo, "hash-object", str(path))
            expected = git(repo, "rev-parse", f"{head}:{name}")
            if actual != expected:
                raise RuntimeError(f"Working file differs from tested Git blob: {name}")
            identities[name] = {"git_blob": actual, "sha256": hashlib.sha256(path.read_bytes()).hexdigest()}
        report["source_identity"] = identities
        sys.path.insert(0, str(repo))
        binding = importlib.import_module("validation_scripts.card_run_v4_binding_hardening")
        standalone = importlib.import_module("validation_scripts.stage_artifact_contract_check")
        fixtures = importlib.import_module("validation_scripts.tests.test_review_5265937741_contracts")
        for module in (binding, standalone, fixtures):
            if not Path(module.__file__).resolve().is_relative_to(repo):
                raise RuntimeError(f"Imported module outside selected checkout: {module.__file__}")
        locked_version = binding._locked_prompt_06_version(head)
        report["locked_prompt_version"] = locked_version

        def record(ident, scope, expected, function, inputs, kind="adversarial"):
            item = {"id": ident, "scope": scope, "kind": kind, "inputs": inputs,
                    "expected": expected, "synthetic": True}
            try:
                observed = function()
                item.update(observed=serial(observed), matches_expected=observed == expected)
            except Exception as exc:
                item.update(observed="RUNTIME_ERROR", matches_expected=False,
                            error_type=type(exc).__name__, error=str(exc), traceback=traceback.format_exc())
            results.append(item)

        def qeq(a, b):
            return binding._signal_counter("quantitative_anchor", a) == binding._signal_counter("quantitative_anchor", b)

        for ident, a, b, equal, kind in (
            ("C01", "10 MW", "10.0 MW", True, "control"),
            ("C02", "10 MW", "10 MWh", False, "control"),
            ("C03", "-10 MW", "10 MW", False, "control"),
            ("A01", "−10 MW", "10 MW", False, "adversarial"),
            ("A02", "20억원", "20조원", False, "adversarial"),
        ):
            record(ident, "component.quantity_identity", equal,
                   lambda a=a, b=b: qeq(a, b), [a, b], kind)
        approval = binding.DIMENSION_CANONICAL_SIGNAL_RES["changed_state"]["approval"]
        for ident, text, strength, kind in (
            ("C04", "Alpha was approved.", 2, "control"),
            ("C05", "Alpha has not been approved.", 0, "control"),
            ("C06", "Alpha may be approved.", 1, "control"),
            ("A03", "알파는 승인되지 않았다.", 0, "adversarial"),
            ("A04", "If Alpha is approved, the project proceeds.", 0, "adversarial"),
        ):
            record(ident, "component.state_strength", strength,
                   lambda text=text: binding._changed_state_match_strength(text, approval.search(text)), text, kind)
        record("A05", "component.korean_factual_content", True,
               lambda: bool(binding._korean_factual_tokens("알파는 수익성이 높다.")), "알파는 수익성이 높다.")
        for ident, a, b, kind in (
            ("C07", "알파는 석탄을 사용했다. 베타는 가스를 사용했다.",
             "알파는 가스를 사용했다. 베타는 석탄을 사용했다.", "control"),
            ("A06", "알파는 석탄을 사용했다 10 MW. 베타는 가스를 사용했다 10 MW.",
             "알파는 가스를 사용했다 10 MW. 베타는 석탄을 사용했다 10 MW.", "adversarial"),
        ):
            record(ident, "component.korean_relation", True,
                   lambda a=a, b=b: binding._korean_factual_relation_counter(a) != binding._korean_factual_relation_counter(b), [a, b], kind)

        def exercise(prior, current, quote, dimensions, standalone_only=False):
            chain = fixtures.chain_for(prior, current, quote, dimensions)
            row = chain["0.6"][0]
            if standalone_only:
                findings = standalone._content_enrichment_audit_findings(row, "pr385_probe")
                return {"decision": "BLOCKED" if findings else "ACCEPTED", "findings": findings}
            try:
                binding.validate_content_enrichment_delta(
                    chain, "pr385_probe", operation_card=copy.deepcopy(row),
                    locked_prompt_version=locked_version,
                )
                return {"decision": "ACCEPTED"}
            except binding.Blocked as exc:
                return {"decision": "BLOCKED", "reason": str(exc)}

        def content_case(ident, prior, current, quote, dimensions=("quantitative_anchor",),
                         expected="BLOCKED", kind="adversarial", standalone_only=False):
            detail = {}
            def invoke():
                detail.update(exercise(prior, current, quote, dimensions, standalone_only))
                return detail["decision"]
            record(ident, "standalone.audit_helper" if standalone_only else "content_gate.with_operation_card",
                   expected, invoke, {"prior": prior, "current": current, "quote": quote, "dimensions": dimensions}, kind)
            results[-1]["decision_detail"] = detail

        content_case("R01_unicode_sign", "Capacity is 5 MW", "Capacity is −10 MW", "Capacity is 10 MW")
        content_case("R02_korean_scale", "투자액은 10억원이다.", "투자액은 20조원이다.", "투자액은 20억원이다.")
        neg = "Previously planned at 10 MW; 알파는 승인되지 않았다; target remains subject to permit."
        content_case("R03_korean_negated_zero", neg, neg, neg, DENSE_DIMENSIONS)
        cond = "Previously planned at 10 MW; If Alpha is approved, demand increases; target remains subject to permit."
        content_case("R04_conditional_zero", cond, cond, cond, DENSE_DIMENSIONS)
        content_case("R05_korean_description", "용량은 10 MW이다.",
                     "용량은 20 MW이다. 알파는 수익성이 높다.", "용량은 20 MW이다.")
        before = "알파는 석탄을 10 MW 공정에 사용했다. 베타는 가스를 10 MW 공정에 사용했다. 용량은 10 MW이다."
        after = "알파는 가스를 10 MW 공정에 사용했다. 베타는 석탄을 10 MW 공정에 사용했다. 용량은 20 MW이다."
        content_case("R06_korean_quantified_swap", before, after, before.replace("용량은 10 MW", "용량은 20 MW"))
        boundary = "Previously planned at 10 MW; Gamma was approved; Alpha target remains subject to permit."
        content_case("R07_boundary_subject_zero", boundary, boundary, boundary.replace("Alpha", "Beta"), DENSE_DIMENSIONS)
        content_case("R08_repetition_not_novelty", "Alpha was approved.",
                     "Alpha was approved. Alpha was approved.",
                     "Alpha was approved. Alpha was approved.", ("changed_state",))
        before = "Capacity is 10 MW. Alpha project. It sold coal. Beta project. It sold gas."
        after = "Capacity is 20 MW. Alpha project. It sold gas. Beta project. It sold coal."
        content_case("R09_pronoun_associations", before, after, before.replace("10 MW", "20 MW"))
        before = "Capacity is 10 MW. Alpha sold coal to Beta. Alpha sold gas to Gamma."
        after = "Capacity is 20 MW. Alpha sold coal to Gamma. Alpha sold gas to Beta."
        content_case("R10_argument_grouping", before, after, before.replace("10 MW", "20 MW"))
        before = "Alpha capacity is 10 MW and output is 20 MW. Gamma may be delayed."
        after = "Alpha capacity is 20 MW and output is 10 MW. Gamma is delayed."
        content_case("R11_metric_association", before, after,
                     before.replace("may be delayed", "is delayed"), ("quantitative_anchor", "changed_state"))
        tentative = "Previously planned at 10 MW; Alpha may be approved; target remains subject to permit."
        content_case("R12_tentative_full", tentative, tentative, tentative, DENSE_DIMENSIONS)
        content_case("R13_tentative_standalone", tentative, tentative, tentative, DENSE_DIMENSIONS, standalone_only=True)
        content_case("P01_grounded_quantity", "Capacity is 10 MW", "Capacity is 20 MW", "Capacity is 20 MW", expected="ACCEPTED", kind="control")
        content_case("P02_grounded_korean", "용량은 10 MW이다.", "용량은 20 MW이다.", "용량은 20 MW이다.", expected="ACCEPTED", kind="control")
        dense = "Previously planned at 10 MW; Alpha was approved; target remains subject to permit."
        content_case("P03_realized_zero", dense, dense, dense, DENSE_DIMENSIONS, expected="ACCEPTED", kind="control")
        content_case("P04_tentative_changed", "Capacity is 10 MW; Alpha project.",
                     "Capacity is 20 MW; Alpha may be delayed.", "Capacity is 20 MW; Alpha may be delayed.",
                     ("quantitative_anchor", "changed_state", "boundary_or_uncertainty"), expected="ACCEPTED", kind="control")
        content_case("N01_wrong_ascii_sign", "Capacity is 5 MW", "Capacity is -10 MW", "Capacity is 10 MW", kind="control")
        content_case("N02_wrong_units", "Capacity is 5 MW", "Capacity is 10 MW", "Capacity is 10 MWh", kind="control")
        report["summary"] = {
            "total": len(results),
            "expectations_met": sum(r["matches_expected"] for r in results),
            "violations": sum(not r["matches_expected"] for r in results),
            "runtime_errors": sum(r["observed"] == "RUNTIME_ERROR" for r in results),
            "by_scope": dict(Counter(r["scope"] for r in results)),
            "unsafe_acceptances_at_content_gate": [r["id"] for r in results if r["scope"] == "content_gate.with_operation_card" and r["expected"] == "BLOCKED" and r["observed"] == "ACCEPTED"],
            "positive_control_blocks": [r["id"] for r in results if r["expected"] == "ACCEPTED" and r["observed"] == "BLOCKED"],
        }
        exit_code = 2 if report["summary"]["runtime_errors"] else (1 if report["summary"]["violations"] else 0)
    except Exception as exc:
        report["setup_error"] = {"type": type(exc).__name__, "message": str(exc), "traceback": traceback.format_exc()}
        exit_code = 2
    report["exit_code"] = exit_code
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    for result in results:
        print(result["id"], result["scope"], "OK" if result["matches_expected"] else "VIOLATION", result["observed"])
    print(json.dumps(report.get("summary", report.get("setup_error")), ensure_ascii=False))
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
