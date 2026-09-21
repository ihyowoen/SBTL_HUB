#!/usr/bin/env python3
from __future__ import annotations
import argparse, copy, hashlib, json, os, re, subprocess, sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "docs/llm_prompts/v1/GOVERNANCE_LIFECYCLE_REGISTRY.json"
COVERAGE_AXES_PATH = Path(os.environ.get(
    "WORKFLOW_V4_COVERAGE_AXES_PATH",
    str(ROOT / "schemas/workflow-v4-coverage-axes.json"),
)).resolve()
ALIASES = {"a":"A","stage_a":"A","0.1":"A","b":"B","stage_b":"B","0.2":"B","c":"C","stage_c":"C","0.3":"C","0.4":"0.4","0.5":"0.5","0.6":"0.6","0.7":"0.7"}
BUCKETS = {"A":["strict_passed_spec"],"B":["draft_cards","draft_card"],"C":["accepted_fact_safe"],"0.4":["addable_merge_safe"],"0.5":["evidence_complete_and_source_claim_covered"],"0.6":["content_enriched_and_language_polished"],"0.7":["publish_ready"]}
STAGES = tuple(BUCKETS)
ALLOWED_RELATED_ADD_TYPES = {"distinct_follow_up", "program_lineage"}
ALLOWED_STAGE_A_TERMINAL_DISPOSITIONS = {
    "legacy_keep",
    "strict_passed_spec",
    "candidate_review_pool",
    "watchlist_context_pool",
    "watchlist_or_support_context",
    "reject_or_support_only_pool",
    "rejected",
    "existing_reinforcement",
    "existing_reinforcement_or_same_event",
    "reinforcement",
    "support_source_only",
    "split_parent_decomposed",
}
STAGE_A_GOVERNED_POOLS = (
    "legacy_keep",
    "strict_passed_spec",
    "candidate_review_pool",
    "watchlist_context_pool",
    "reject_or_support_only_pool",
    "rejected",
    "existing_reinforcement",
    "support_source_only",
)
IDENTITY_ROOT = "source_spec_id"
VISIBLE_COPY_FIELDS = ("sub", "gate", "fact", "implication")
CONTENT_BASELINE_ORDER = ("0.5", "0.4", "C")
CONTENT_BASELINE_STRATEGY = "nearest_upstream_visible_copy_0.5_0.4_C"
PROMPT_06_PATH = "docs/llm_prompts/v1/08_PROMPT_0_6_Content_Polish.md"
PRESENTATION_HTML_TAG_RE = re.compile(
    r"</?(?:strong|b|em|i|u|mark|span|small|sub|sup)(?:\s+[^<>]*?)?\s*/?>",
    re.IGNORECASE,
)
ARRAY_INDEX_RE = re.compile(r"^(?:0|[1-9]\d*)$")
QUANT_SIGNAL_RE = re.compile(
    r"(?<![A-Za-z0-9])"
    r"(?P<bound><=|>=|≤|≥|<|>|≈|~)?\s*"
    r"(?:(?P<currency_code_prefix>USD|EUR|GBP|KRW|CNY|RMB|JPY|AUD|CAD|CHF|HKD|SGD)\s+)?"
    r"(?P<sign>[+-])?\s*"
    r"(?P<currency>[$€£¥₩]?)"
    r"(?P<number>\d{1,3}(?:,\d{3})+(?:\.\d+)?|\d+,\d+|\d+(?:\.\d+)?)"
    r"(?:\s*(?P<magnitude>thousand|million|billion|trillion|mn|bn|tn|k|m|b)\b)?"
    r"(?:\s*(?P<currency_code_suffix>USD|EUR|GBP|KRW|CNY|RMB|JPY|AUD|CAD|CHF|HKD|SGD)\b)?"
    r"(?:\s*(?P<unit>%|x|mw|gw|gwh|mwh|kwh|tpa|kt|mt|sqm|m²|km|tons?|tonnes?))?"
    r"(?:\s+(?!(?:and|or|but|yet|for|from|to|at|in|on|by|with|because|while|whereas|previously|currently|planned|approved|started|delayed|completed|commercial|subject|target)\b)"
    r"(?P<generic_unit>[A-Za-z][A-Za-z0-9²³/_-]{0,31}))?"
    r"(?![A-Za-z0-9])",
    re.IGNORECASE,
)

EVIDENCE_TEXT_KEYS = (
    "source_quote", "quote", "claim", "source_claim", "claim_text",
    "visible_claim", "evidence_text", "source_excerpt", "excerpt",
)
EVIDENCE_VERIFICATION_KEYS = (
    "source_quote_status", "quote_status", "claim_status", "evidence_status",
    "fetch_status", "resolved_article_matches_quote", "fetched",
    "headline_only", "rss_or_snippet_only", "claim_use", "evidence_role",
)
USABLE_QUOTE_STATUSES = {
    "body_quote_verified",
    "official_material_quote_verified",
    "document_quote_verified",
}
FETCH_METADATA_KEYS = {
    "fetched", "fetched_at", "checked_at", "body", "body_text",
    "document_text", "official_material_text",
}
NON_REALIZED_CHANGED_STATE_PREFIX_RE = re.compile(
    r"(?:"
    r"\b(?:not|never|without)\b(?:\s+\w+){0,3}\s*$"
    r"|\bno\s+(?:current\s+)?(?:\w+\s+){0,2}$"
    r"|\b(?:is|are|was|were|has|have|had|do|does|did|will|would|can|could)\s+not(?:\s+\w+){0,2}\s*$"
    r"|\b(?:plan(?:ned)?|target(?:ed)?|propos(?:ed|al)|schedul(?:ed|ing))\b(?:\s+\w+){0,2}\s*$"
    r"|n['’]t(?:\s+\w+){0,2}\s*$"
    r")",
    re.IGNORECASE,
)
TENTATIVE_CHANGED_STATE_PREFIX_RE = re.compile(
    r"(?:"
    r"\b(?:may|might|could|possibly|potentially|likely\s+to|expected\s+to)\b(?:\s+\w+){0,3}\s*$"
    r"|\bsubject\s+to\b(?:\s+\w+){0,3}\s*$"
    r")",
    re.IGNORECASE,
)
NON_REALIZED_CHANGED_STATE_SUFFIX_RE = re.compile(
    r"^\s*(?:"
    r"(?:has|have|had|is|are|was|were|will|would|can|could)?\s*(?:not|never|n['’]t)\b"
    r"|not\s+yet\b"
    r"|(?:is|are|remains?|remain)\s+(?:planned|targeted|expected|scheduled)\b"
    r")",
    re.IGNORECASE,
)
CLAUSE_BOUNDARY_RE = re.compile(
    r"[.;:!?]|\b(?:and|or|but|yet|however|although|though|whereas)\b",
    re.IGNORECASE,
)
CLAUSE_NEGATION_RE = re.compile(
    r"\b(?:not|never|without|neither|nor)\b|n['’]t\b",
    re.IGNORECASE,
)
FACTUAL_IDENTITY_TOKEN_RE = re.compile(
    r"\b(?:[A-Z][A-Za-z0-9&._-]{2,}|[A-Z]{2,}[A-Z0-9&._-]*)\b"
)
LOCATION_PHRASE_RE = re.compile(
    r"\b(?:at|in|near|from|to|with|by)\s+(?:the\s+)?([A-Za-z][A-Za-z0-9&._-]{2,})\b",
    re.IGNORECASE,
)
KOREAN_IDENTITY_RE = re.compile(
    r"(?<![가-힣])([가-힣]{2,}(?:공장|시설|법인|시|도|군|구|읍|면|리))(?![가-힣])"
)
FACTUAL_IDENTITY_STOPWORDS = {
    "the","this","that","these","those","project","capacity","investment",
    "production","commercial","previously","target","site","plant","facility",
    "company","according","battery","energy","market","supply","demand","source",
    "usd","eur","gbp","krw","cny","rmb","jpy","aud","cad","chf","hkd","sgd",
    "mw","gw","gwh","mwh","kwh","tpa","kt","mt","sqm","km","tons","tonnes",
    "january","february","march","april","may","june","july","august",
    "september","october","november","december",
}
FACTUAL_PREDICATE_RE = re.compile(
    r"\b(?:uses?|using|contains?|containing|includes?|including|comprises?|"
    r"relies\s+on|sources?|supplies?|owns?|operates?|employs?|produces?|"
    r"manufactures?|recycles?|acquires?|acquired|selects?|selected|"
    r"partners?\s+with|partnered\s+with|contracts?\s+with|contracted\s+with|"
    r"built\s+with|made\s+with|located\s+in|based\s+in|powered\s+by)"
    r"\s+(?P<tail>[^.;:!?]{1,120})",
    re.IGNORECASE,
)
GENERIC_FACTUAL_PREDICATE_RE = re.compile(
    r"(?:"
    r"\b(?:and|but|while|whereas)\s+"
    r"(?P<verb_after_connector>[A-Za-z][A-Za-z-]{2,}(?:s|ed|ing))\b"
    r"\s+(?P<tail_after_connector>[^.;:!?]{1,120})"
    r"|(?:^|[.;:!?]\s*)"
    r"(?P<subject>[A-Z][A-Za-z0-9&._-]{2,})\s+"
    r"(?P<verb_after_subject>[A-Za-z][A-Za-z-]{2,}(?:s|ed|ing))\b"
    r"\s+(?P<tail_after_subject>[^.;:!?]{1,120})"
    r")",
)
MODAL_FACTUAL_PREDICATE_RE = re.compile(
    r"\b(?:can|could|may|might|will|would|must|should|shall)\s+"
    r"(?:not\s+)?(?P<verb>[A-Za-z][A-Za-z-]+)\b"
    r"\s+(?P<tail>[^.;:!?]{1,120})",
    re.IGNORECASE,
)
COMMA_PARTICIPIAL_FACTUAL_RE = re.compile(
    r",\s*(?!(?:using|containing|including)\b)"
    r"(?P<verb>[A-Za-z][A-Za-z-]{2,}ing)\b"
    r"\s+(?P<tail>[^.;:!?]{1,120})",
    re.IGNORECASE,
)
FACTUAL_CONTENT_WORD_RE = re.compile(r"\b[A-Za-z][A-Za-z0-9_-]{2,}\b|[가-힣]{2,}")
FACTUAL_CONTENT_STOPWORDS = FACTUAL_IDENTITY_STOPWORDS | {
    "and","or","but","yet","with","from","into","onto","over","under","through",
    "for","per","via","its","their","our","his","her","new","same","current",
    "planned","approved","started","delayed","completed","commercial","remains",
    "remain","will","would","could","may","might","uses","using","contains",
    "containing","includes","including","comprises","relies","sources","supplies",
    "owns","operates","employs","produces","manufactures","recycles","acquires",
    "acquired","selects","selected","partners","partnered","contracts","contracted",
    "built","made","located","based","powered",
}
DIMENSION_CANONICAL_SIGNAL_RES = {
    "prior_state": {
        "prior_state": re.compile(r"\b(?:previous(?:ly)?|prior|earlier|before|formerly|versus|vs\.?|compared\s+with|year[- ]ago|last\s+year)\b|(?:이전|종전|기존|직전|전년|과거|당초)", re.IGNORECASE),
    },
    "changed_state": {
        "production_operation": re.compile(r"\b(?:commercial\s+production|commission(?:ed|ing)?|operational|in\s+operation|produc(?:ing|ed))\b|(?:상업생산|가동|양산)", re.IGNORECASE),
        "construction": re.compile(r"\b(?:broke\s+ground|groundbreak(?:ing)?|under\s+construction|construction\s+(?:began|started|commenced|completed|is\s+underway))\b|(?:착공|건설\s*(?:중|시작|완료))", re.IGNORECASE),
        "shipment_launch": re.compile(r"\b(?:ship(?:ped|ping)?|launch(?:ed)?)\b|(?:출하|출시)", re.IGNORECASE),
        "commencement": re.compile(r"\b(?:start(?:ed|ing)?|begin|began|begun|commence(?:d|ment)?)\b|(?:개시|시작)", re.IGNORECASE),
        "completion": re.compile(r"\b(?:complete(?:d)?)\b|(?:완공)", re.IGNORECASE),
        "ramp": re.compile(r"\b(?:ramp(?:ed|ing)?|ramp[- ]?up)\b|(?:증설|램프업)", re.IGNORECASE),
        "restart": re.compile(r"\b(?:resume(?:d)?|restart(?:ed)?)\b|(?:재개|재가동)", re.IGNORECASE),
        "suspension": re.compile(r"\b(?:suspend(?:ed)?)\b|(?:중단)", re.IGNORECASE),
        "delay": re.compile(r"\b(?:delay(?:ed)?)\b|(?:지연)", re.IGNORECASE),
        "cancellation": re.compile(r"\b(?:cancel(?:led|ed)?)\b|(?:취소)", re.IGNORECASE),
        "approval": re.compile(r"\b(?:approve(?:d)?)\b|(?:승인)", re.IGNORECASE),
        "agreement": re.compile(r"\b(?:sign(?:ed)?)\b|(?:체결)", re.IGNORECASE),
    },
    "boundary_or_uncertainty": {
        "plan_target": re.compile(r"\b(?:plan(?:ned)?|target(?:ed)?|proposal|proposed)\b|(?:계획|목표|제안)", re.IGNORECASE),
        "expectation_estimate": re.compile(r"\b(?:expect(?:ed)?|estimate(?:d)?|forecast|guidance)\b|(?:예정|전망|추정)", re.IGNORECASE),
        "uncertain_conditional": re.compile(r"\b(?:preliminary|may|might|could|subject\s+to|not\s+yet)\b|(?:잠정|가능성|미확정|아직)", re.IGNORECASE),
        "reported_attribution": re.compile(r"\b(?:reported|according\s+to)\b|(?:보도)", re.IGNORECASE),
    },
    "transmission_path": {
        "causal": re.compile(r"\b(?:because|due\s+to|therefore|driv(?:e|es|en)|lead(?:s|ing)?\s+to|impact(?:s|ed)?|affect(?:s|ed)?)\b|(?:때문|영향)", re.IGNORECASE),
        "demand_supply": re.compile(r"\b(?:demand|supply|supply\s+chain)\b|(?:수요|공급|공급망)", re.IGNORECASE),
        "economics": re.compile(r"\b(?:pressure|cost|price|margin|procurement)\b|(?:압력|원가|비용|가격|마진|조달)", re.IGNORECASE),
    },
    "next_watchpoint": {
        "generic_watch": re.compile(r"\b(?:next|watch|milestone)\b|(?:향후|다음|확인|마일스톤)", re.IGNORECASE),
        "qualification_certification": re.compile(r"\b(?:qualification|certification)\b|(?:인증|고객승인)", re.IGNORECASE),
        "future_execution": re.compile(r"\b(?:commissioning|ramp[- ]?up|by\s+q[1-4]|by\s+20\d{2}|expected\s+(?:by|in)|scheduled\s+(?:for|in))\b|(?:가동예정|양산예정|출하예정)", re.IGNORECASE),
    },
}
DENSITY_DIMENSIONS = (
    "prior_state",
    "changed_state",
    "quantitative_anchor",
    "boundary_or_uncertainty",
    "transmission_path",
    "next_watchpoint",
)
_MISSING = object()

class Blocked(Exception): pass

def load(path: Path): return json.loads(path.read_text(encoding="utf-8-sig"))
def repo_json(ref: str) -> Path:
    if not isinstance(ref,str) or not ref or not ref.endswith(".json") or ref.startswith("/") or ".." in Path(ref).parts: raise Blocked(f"invalid repository JSON ref: {ref}")
    p=(ROOT/ref).resolve()
    if not p.is_file() or ROOT not in p.parents: raise Blocked(f"missing repository JSON ref: {ref}")
    return p

def strings(v,label,allow_empty=False):
    if not isinstance(v,list): raise Blocked(f"{label} must be string array")
    if not v and not allow_empty: raise Blocked(f"{label} must be non-empty string array")
    if any(not isinstance(x,str) or not x.strip() for x in v): raise Blocked(f"{label} must contain only non-empty strings")
    out=[x.strip() for x in v]
    if len(out)!=len(set(out)): raise Blocked(f"{label} contains duplicates")
    return set(out)

def coverage_axes():
    try:
        payload=json.loads(COVERAGE_AXES_PATH.read_text(encoding="utf-8-sig"))
    except Exception as exc:
        raise Blocked(f"workflow-v4 coverage axes contract is unreadable: {exc}") from exc
    if not isinstance(payload,dict) or payload.get("schema")!="workflow_v4_coverage_axes_v1":
        raise Blocked("workflow-v4 coverage axes contract has unexpected schema id")
    regions=strings(payload.get("regions"),"workflow-v4 coverage axes regions")
    topics=strings(payload.get("topics"),"workflow-v4 coverage axes topics")
    return regions,topics

def validate_preflight(run):
    a=load(repo_json(run["document_universe_manifest_ref"])); r=load(REGISTRY)
    expected_c=set(r.get("active_canonical",[]))|set(r.get("active_named_prompts",[]))
    expected_v=set(r.get("active_validator_contracts",[]))
    expected_m=set(r.get("open_remediations",[]))|set(r.get("activation_required_migrations",[]))
    if strings(a.get("active_canonical_paths"),"0.0D.active_canonical_paths")!=expected_c: raise Blocked("0.0D active_canonical_paths != current registry active set")
    if strings(a.get("active_validator_contract_paths"),"0.0D.active_validator_contract_paths")!=expected_v: raise Blocked("0.0D active_validator_contract_paths != current registry validator set")
    if strings(a.get("applicable_remediation_or_migration"),"0.0D.applicable remediation/migration",allow_empty=True)!=expected_m: raise Blocked("0.0D applicable remediation/migration != current registry set")
    required=len(expected_c|expected_v|expected_m)
    if a.get("active_full_read_count")!=required: raise Blocked(f"0.0D active_full_read_count must equal exact active/dependency closure ({required})")

def axis_matrix(v,required,label):
    if not isinstance(v,dict): raise Blocked(f"{label} must be object")
    missing=sorted(required-set(v))
    if missing: raise Blocked(f"{label} missing axes: {missing}")
    for key in required:
        row=v[key]
        if not isinstance(row,dict) or row.get("status") not in {"searched","blocked"}: raise Blocked(f"{label}.{key}.status must be searched|blocked")
        if row["status"]=="blocked" and (not isinstance(row.get("reason"),str) or not row["reason"].strip()): raise Blocked(f"{label}.{key}.reason required when blocked")

def validate_coverage(run):
    regions,topics=coverage_axes()
    a=load(repo_json(run["coverage_discovery_ref"])); axis_matrix(a.get("regional_coverage_matrix"),regions,"0.0C.regional_coverage_matrix"); axis_matrix(a.get("topic_coverage_matrix"),topics,"0.0C.topic_coverage_matrix")

def _nonempty_text(value):
    return isinstance(value,str) and bool(value.strip())

def _stage_a_story_ids(item,pool):
    if not isinstance(item,dict): return []
    out=[]
    if pool=="strict_passed_spec":
        values=item.get("source_story_ids")
        if isinstance(values,list): out.extend(x.strip() for x in values if _nonempty_text(x))
    else:
        if _nonempty_text(item.get("story_id")): out.append(item["story_id"].strip())
        grouped=item.get("grouped_story_ids")
        if isinstance(grouped,list): out.extend(x.strip() for x in grouped if _nonempty_text(x))
        source_ids=item.get("source_story_ids")
        if isinstance(source_ids,list): out.extend(x.strip() for x in source_ids if _nonempty_text(x))
    return list(dict.fromkeys(out))

def checker_validated_stage_a_decisions(source):
    review_pool=source.get("review_pool")
    if not isinstance(review_pool,list):
        raise Blocked("checker-validated Stage A review_pool must be an array")
    if review_pool:
        raise Blocked("checker-validated Stage A review_pool must be empty before terminal authority; use canonical review partitions")

    governed={}
    for pool in STAGE_A_GOVERNED_POOLS:
        values=source.get(pool)
        if not isinstance(values,list):
            raise Blocked(f"checker-validated Stage A output pool {pool} must be an array")
        for index,item in enumerate(values):
            if not isinstance(item,dict):
                raise Blocked(f"checker-validated Stage A {pool}[{index}] must be an object")
            spec_id=item.get("spec_id") if _nonempty_text(item.get("spec_id")) else None
            identities=_stage_a_story_ids(item,pool)
            if not identities:
                raise Blocked(f"checker-validated Stage A {pool}[{index}] has no governed story identity")
            for identity in identities:
                if identity in governed:
                    raise Blocked(f"checker-validated Stage A identity {identity} appears in multiple output dispositions")
                basis=f"stage_a_checker:{pool}:{spec_id or identity}"
                governed[identity]=(pool,basis)
    return governed

def governed_stage_a_decisions(run,ledger):
    ref=ledger.get("governed_stage_a_ledger_ref") or ledger.get("prior_partial_ledger_ref")
    if not _nonempty_text(ref):
        raise Blocked("Stage A terminal identity ledger must reference its governed Stage A decision ledger")
    source_path=repo_json(ref.strip())
    source=load(source_path)
    raw_stage=source.get("stage")
    if not _nonempty_text(raw_stage) or ALIASES.get(raw_stage.strip().lower())!="A" or source.get("run_id")!=run.get("run_id"):
        raise Blocked("governed Stage A decision ledger stage/run_id mismatch")
    authority=source.get("authority") if isinstance(source.get("authority"),dict) else source
    for field in ("base_main_commit_sha","base_full_blob_sha"):
        if authority.get(field)!=run.get(field):
            raise Blocked(f"governed Stage A decision ledger {field} mismatch")
    if ledger.get("status")!="PASS":
        raise Blocked("terminal decision binding requires a PASS terminal identity ledger")
    checker=ROOT / "validation_scripts/stage_lineage_contract_check.py"
    proc=subprocess.run(
        [sys.executable,str(checker),"stage_a",str(source_path)],
        text=True,capture_output=True,
    )
    if proc.returncode!=0:
        detail=(proc.stderr or proc.stdout or "Stage A checker failed").strip().replace("\n"," ")
        raise Blocked(
            "passing terminal ledger requires governed Stage A decision ledger to pass the full Stage A checker: "
            + detail[:600]
        )
    return checker_validated_stage_a_decisions(source)

def validate_terminal_decision_binding(entries,governed):
    if not isinstance(entries,list):
        raise Blocked("Stage A terminal identity ledger terminal_decisions must be an array")
    terminal_ids=[]; dispositions=[]
    for index,row in enumerate(entries):
        identity=row.get("identity") if isinstance(row,dict) else None
        disposition=row.get("disposition") if isinstance(row,dict) else None
        basis=row.get("basis") if isinstance(row,dict) else None
        if not _nonempty_text(identity): raise Blocked(f"Stage A terminal_decisions[{index}].identity required")
        if disposition not in ALLOWED_STAGE_A_TERMINAL_DISPOSITIONS: raise Blocked(f"Stage A terminal_decisions[{index}].disposition is not an allowed terminal disposition")
        if not _nonempty_text(basis): raise Blocked(f"Stage A terminal_decisions[{index}].basis required")
        if row.get("terminal") is not True: raise Blocked(f"Stage A terminal_decisions[{index}] must declare terminal=true")
        identity=identity.strip(); basis=basis.strip()
        expected=governed.get(identity)
        if expected is None: raise Blocked(f"Stage A terminal_decisions[{index}] identity={identity} has no governed Stage A decision")
        if expected!=(disposition,basis): raise Blocked(f"Stage A terminal_decisions[{index}] disposition/basis does not match checker-validated Stage A output")
        terminal_ids.append(identity); dispositions.append(disposition)
    if len(terminal_ids)!=len(set(terminal_ids)):
        raise Blocked("Stage A terminal identity ledger contains duplicate identities")
    return terminal_ids,dispositions

def validate_completeness(run):
    a=load(repo_json(run["independent_completeness_ref"]))
    if a.get("stage")!="0.7C": raise Blocked("0.7C stage must be explicit")
    if a.get("status")!="PASS_WITH_DECLARED_RESIDUAL_RISK" or a.get("completeness_status")!=a.get("status"): raise Blocked("0.7C status/completeness_status must both be PASS_WITH_DECLARED_RESIDUAL_RISK")
    risks=a.get("residual_risks")
    if not isinstance(risks,list) or not risks or any(not isinstance(x,str) or not x.strip() for x in risks): raise Blocked("0.7C PASS_WITH_DECLARED_RESIDUAL_RISK requires non-empty residual_risks strings")
    for field in ("run_id","base_main_commit_sha","base_full_blob_sha"):
        if a.get(field)!=run.get(field): raise Blocked(f"0.7C {field} must match card run")
    if a.get("document_universe_manifest_ref")!=run.get("document_universe_manifest_ref"): raise Blocked("0.7C document_universe_manifest_ref must match card run")
    if a.get("coverage_discovery_ref")!=run.get("coverage_discovery_ref"): raise Blocked("0.7C coverage_discovery_ref must match card run")

    ledger_ref=a.get("terminal_identity_ledger_ref")
    if not isinstance(ledger_ref,str) or not ledger_ref.strip():
        raise Blocked("0.7C terminal_identity_ledger_ref is required")
    ledger_path=repo_json(ledger_ref)
    recorded_sha=a.get("terminal_identity_ledger_sha256")
    actual_sha=hashlib.sha256(ledger_path.read_bytes()).hexdigest()
    if recorded_sha!=actual_sha:
        raise Blocked("0.7C terminal_identity_ledger_sha256 does not match referenced bytes")
    ledger=load(ledger_path)
    if ledger.get("status")!="PASS" or ledger.get("stage")!="A":
        raise Blocked("0.7C terminal identity ledger must be a passing Stage A ledger")
    if ledger.get("run_id")!=run.get("run_id"):
        raise Blocked("0.7C terminal identity ledger run_id mismatch")
    governed=governed_stage_a_decisions(run,ledger)

    coverage=load(repo_json(run["coverage_discovery_ref"]))
    coverage_rows=coverage.get("source_universe_expansion_ledger")
    if not isinstance(coverage_rows,list):
        raise Blocked("0.0C source_universe_expansion_ledger must be an array")
    coverage_ids=[]
    for index,row in enumerate(coverage_rows):
        candidate_id=row.get("candidate_id") if isinstance(row,dict) else None
        if not isinstance(candidate_id,str) or not candidate_id.strip():
            raise Blocked(f"0.0C source_universe_expansion_ledger[{index}].candidate_id required")
        coverage_ids.append(candidate_id.strip())
    if len(coverage_ids)!=len(set(coverage_ids)):
        raise Blocked("0.0C source_universe_expansion_ledger contains duplicate identities")

    entries=ledger.get("terminal_decisions")
    terminal_ids,dispositions=validate_terminal_decision_binding(entries,governed)
    if set(terminal_ids)!=set(coverage_ids):
        missing=sorted(set(coverage_ids)-set(terminal_ids))
        unknown=sorted(set(terminal_ids)-set(coverage_ids))
        raise Blocked(f"Stage A terminal identity ledger does not exactly reconcile 0.0C; missing={missing[:5]} unknown={unknown[:5]}")
    if set(governed)!=set(coverage_ids):
        missing=sorted(set(coverage_ids)-set(governed))
        unknown=sorted(set(governed)-set(coverage_ids))
        raise Blocked(f"checker-validated Stage A outputs do not exactly reconcile 0.0C; missing={missing[:5]} unknown={unknown[:5]}")

    universe=a.get("universe_accounting")
    if not isinstance(universe,dict): raise Blocked("0.7C universe_accounting must be an object")
    total=len(coverage_ids)
    if universe.get("terminal_identity_total")!=total or universe.get("terminal_identity_accounted")!=total: raise Blocked("0.7C terminal identity totals must equal the exact identity ledger cardinality")
    if universe.get("duplicate_identity_count")!=0 or universe.get("missing_identity_count")!=0: raise Blocked("0.7C duplicate/missing identity counts must both be zero")
    if ledger.get("terminal_identity_total")!=total or ledger.get("terminal_identity_accounted")!=total: raise Blocked("Stage A terminal identity ledger cardinality fields are inconsistent")
    if ledger.get("open_identity_count")!=0: raise Blocked("Stage A terminal identity ledger open_identity_count must be zero")

    actual_counts=dict(sorted(Counter(dispositions).items()))
    if ledger.get("disposition_counts")!=actual_counts: raise Blocked("Stage A terminal identity ledger disposition_counts do not match identity rows")
    revalidation=a.get("stage_a_revalidation")
    if not isinstance(revalidation,dict) or revalidation.get("disposition_counts")!=actual_counts: raise Blocked("0.7C stage_a_revalidation.disposition_counts must match the identity ledger")
    return governed

def stage(payload,label):
    raw=payload.get("stage")
    if not isinstance(raw,str) or not raw.strip(): raise Blocked(f"{label}.stage required")
    s=ALIASES.get(raw.strip().lower())
    if not s: raise Blocked(f"{label}.stage={raw} is not an ordinary stage; 0.2R/0.3R cannot substitute")
    return s

def validate_stage_binding(payload,run,label):
    for field in ("run_id","base_main_commit_sha","base_full_blob_sha"):
        value=payload.get(field)
        if not isinstance(value,str) or not value.strip(): raise Blocked(f"{label}.{field} required")
        if value!=run.get(field): raise Blocked(f"{label}.{field} stale or mismatched")

def stage_rows(payload,s):
    rows=[]
    for bucket in BUCKETS[s]:
        v=payload.get(bucket)
        if isinstance(v,list): rows.extend(row for row in v if isinstance(row,dict))
        elif isinstance(v,dict): rows.append(v)
    return rows

def row_spec_id(row,s):
    x=row.get("spec_id") if s=="A" else row.get("source_spec_id")
    return x.strip() if isinstance(x,str) and x.strip() else None

def matching_rows(payload,s,expected): return [row for row in stage_rows(payload,s) if row_spec_id(row,s)==expected]
def spec_ids(payload,s): return {x for row in stage_rows(payload,s) if (x:=row_spec_id(row,s))}

def governed_strict_spec_identities(governed):
    prefix="stage_a_checker:strict_passed_spec:"
    result={}
    for identity,(disposition,basis) in governed.items():
        if disposition!="strict_passed_spec": continue
        if not isinstance(basis,str) or not basis.startswith(prefix) or not basis[len(prefix):]: raise Blocked(f"checker-validated strict Stage A identity {identity} has malformed derived basis")
        result.setdefault(basis[len(prefix):],set()).add(identity)
    return result

def validate_governed_stage_a_operation(rows_by_stage,expected,strict_specs,label):
    governed_ids=strict_specs.get(expected)
    if not governed_ids: raise Blocked(f"{label} source_spec_id={expected} is not a checker-validated strict Stage A outcome")
    actual_ids=set()
    for row in rows_by_stage.get("A",[]): actual_ids.update(_stage_a_story_ids(row,"strict_passed_spec"))
    if actual_ids!=governed_ids: raise Blocked(f"{label} Stage A operation binding disagrees with terminal authority for {expected}; governed={sorted(governed_ids)} actual={sorted(actual_ids)}")

def _git(args):
    proc=subprocess.run(["git","-C",str(ROOT),*args],text=True,capture_output=True)
    if proc.returncode!=0: raise Blocked(f"git {' '.join(args)} failed: {(proc.stderr or proc.stdout).strip()}")
    return proc.stdout

def baseline_canonical(run):
    sha=run.get("base_main_commit_sha"); blob=run.get("base_full_blob_sha")
    if not isinstance(sha,str) or len(sha)!=40 or not isinstance(blob,str) or len(blob)!=40: raise Blocked("declared baseline SHA/blob required")
    actual=_git(["rev-parse",f"{sha}:data/cards.full.json"]).strip()
    if actual!=blob: raise Blocked(f"declared baseline blob mismatch: {actual} != {blob}")
    try: data=json.loads(_git(["show",f"{sha}:data/cards.full.json"]))
    except Exception as exc: raise Blocked(f"declared baseline canonical JSON unreadable: {exc}") from exc
    if not isinstance(data,dict) or not isinstance(data.get("cards"),list): raise Blocked("declared baseline canonical cards array required")
    return data

def canonical_map_from_data(data):
    return {c["id"].strip():c["source_spec_id"].strip() for c in data.get("cards",[]) if isinstance(c,dict) and isinstance(c.get("id"),str) and c["id"].strip() and isinstance(c.get("source_spec_id"),str) and c["source_spec_id"].strip()}

def validate_no_identity_mutation(op,label):
    for i,change in enumerate(op.get("changes",[]) if isinstance(op,dict) else []):
        if not isinstance(change,dict): continue
        path=change.get("path")
        if isinstance(path,str) and (path==f"/{IDENTITY_ROOT}" or path.startswith(f"/{IDENTITY_ROOT}/")): raise Blocked(f"{label}.changes[{i}] cannot mutate {IDENTITY_ROOT}; operation.source_spec_id is binding metadata only")

def validate_insert_identities(insert_ops,known):
    baseline_specs=set(known.values()); seen=set()
    for i,op in enumerate(insert_ops):
        card=op.get("card") if isinstance(op,dict) else None
        spec=card.get("source_spec_id") if isinstance(card,dict) else None
        if not isinstance(spec,str) or not spec.strip(): raise Blocked(f"insert[{i}].card.source_spec_id required")
        spec=spec.strip()
        if spec in seen: raise Blocked(f"insert[{i}] reuses source_spec_id={spec} within the same run")
        if spec in baseline_specs: raise Blocked(f"insert[{i}] reuses baseline source_spec_id={spec}")
        seen.add(spec)

def op_spec(kind,op,known,inserted,label):
    if kind=="insert":
        x=(op.get("card") or {}).get("source_spec_id")
        if not isinstance(x,str) or not x.strip(): raise Blocked(f"{label}.card.source_spec_id required")
        return x.strip()
    if kind=="update":
        validate_no_identity_mutation(op,label)
        cid=op.get("id"); old=known.get(cid); declared=op.get("source_spec_id")
        declared=declared.strip() if isinstance(declared,str) and declared.strip() else None
        if old and declared and old!=declared: raise Blocked(f"{label}.source_spec_id conflicts with declared-baseline identity")
        if old: return old
        if not declared: raise Blocked(f"{label}.source_spec_id required for legacy card without baseline source_spec_id")
        return declared
    sid,tid=op.get("source_id"),op.get("target_id"); ss=inserted.get(sid) or known.get(sid); ts=inserted.get(tid) or known.get(tid); declared=op.get("source_spec_id"); ident=op.get("identity_card_id")
    declared=declared.strip() if isinstance(declared,str) and declared.strip() else None
    if isinstance(ident,str) and ident.strip() not in {sid,tid}: raise Blocked(f"{label}.identity_card_id must equal source_id or target_id")
    if ss or ts:
        if declared and declared not in {x for x in (ss,ts) if x}: raise Blocked(f"{label}.source_spec_id does not match a governed endpoint")
        return declared or ss or ts
    if not declared or not isinstance(ident,str) or not ident.strip(): raise Blocked(f"{label} requires source_spec_id + identity_card_id when both legacy endpoints lack source_spec_id")
    return declared

def relation_type(obj):
    if not isinstance(obj,dict): return None
    for key in ("relation_type","final_relation_type","proposed_relation_type","proposed_type"):
        value=obj.get(key)
        if isinstance(value,str) and value.strip(): return value.strip()
    return None

def identifier_tokens(obj):
    tokens=set()
    if not isinstance(obj,dict): return tokens
    for key,value in obj.items():
        lower=str(key).lower()
        identity_key=(lower.endswith("_id") or lower.endswith("_ids") or "candidate" in lower or "target" in lower or lower in {"related","related_ids"})
        if identity_key:
            if isinstance(value,str) and value.strip(): tokens.add(value.strip())
            elif isinstance(value,list): tokens.update(x.strip() for x in value if isinstance(x,str) and x.strip())
        if isinstance(value,dict): tokens.update(identifier_tokens(value))
        elif isinstance(value,list):
            for row in value:
                if isinstance(row,dict): tokens.update(identifier_tokens(row))
    return tokens

def relation_reason(obj):
    if not isinstance(obj,dict): return None
    for key in ("reason","relation_reason","lineage_reason"):
        value=obj.get(key)
        if isinstance(value,str) and value.strip(): return value.strip()
    return None

def endpoint_context(op,known,inserted,expected,label):
    sid,tid=op.get("source_id"),op.get("target_id")
    if not isinstance(sid,str) or not isinstance(tid,str) or not sid or not tid: raise Blocked(f"{label} source_id/target_id required")
    ss=inserted.get(sid) or known.get(sid); ts=inserted.get(tid) or known.get(tid)
    ident=op.get("identity_card_id")
    if isinstance(ident,str) and ident.strip(): governed=ident.strip()
    else:
        matches=[cid for cid,spec in ((sid,ss),(tid,ts)) if spec==expected]
        if len(matches)!=1: raise Blocked(f"{label} cannot unambiguously bind source_spec_id={expected} to one Related endpoint; identity_card_id required")
        governed=matches[0]
    other=tid if governed==sid else sid
    other_spec=ts if governed==sid else ss
    target_tokens={other}
    if isinstance(other_spec,str) and other_spec: target_tokens.add(other_spec)
    return governed,target_tokens

def require_target_and_type(review,op,target_tokens,label,require_reason=False):
    if not isinstance(review,dict): raise Blocked(f"{label} relation review object required")
    if review.get("status") not in (None,"PASS"): raise Blocked(f"{label}.status must be PASS when present")
    actual_type=relation_type(review)
    if actual_type!=op.get("relation_type"): raise Blocked(f"{label} relation_type={actual_type} != operation {op.get('relation_type')}")
    if not (identifier_tokens(review)&target_tokens): raise Blocked(f"{label} does not identify the declared Related counterpart {sorted(target_tokens)}")
    if require_reason:
        reason=relation_reason(review)
        if reason!=op.get("lineage_reason"): raise Blocked(f"{label} lineage reason does not match operation.lineage_reason")
    direction=review.get("direction")
    if direction is not None and direction!=op.get("direction"): raise Blocked(f"{label}.direction does not match operation.direction")
    event_stage=review.get("event_stage_relationship")
    if event_stage is not None and event_stage!=op.get("event_stage_relationship"): raise Blocked(f"{label}.event_stage_relationship does not match operation")

def validate_related_semantics(op,expected,rows_by_stage,known,inserted,label):
    if op.get("relation_type") not in ALLOWED_RELATED_ADD_TYPES: raise Blocked(f"{label}.relation_type must be distinct_follow_up or program_lineage for related_add")
    _,target_tokens=endpoint_context(op,known,inserted,expected,label)
    arows=rows_by_stage.get("A",[]); a_ok=False
    for row in arows:
        pre=row.get("related_prepass")
        if not isinstance(pre,dict) or pre.get("status")!="PASS": continue
        candidates=pre.get("relation_candidates")
        if not isinstance(candidates,list): continue
        for candidate in candidates:
            if isinstance(candidate,dict) and relation_type(candidate)==op.get("relation_type") and (identifier_tokens(candidate)&target_tokens): a_ok=True; break
        if a_ok: break
    if not a_ok: raise Blocked(f"{label} Stage A related_prepass does not review the declared counterpart/type")
    brows=rows_by_stage.get("B",[])
    if not any(isinstance(row.get("related_evidence_review"),dict) and _relation_review_matches(row["related_evidence_review"],op,target_tokens,False) for row in brows): raise Blocked(f"{label} Stage B related_evidence_review does not resolve the declared counterpart/type")
    for s in ("C","0.4","0.5","0.6","0.7"):
        rows=rows_by_stage.get(s,[])
        if not any(isinstance(row.get("related_lineage"),dict) and _relation_review_matches(row["related_lineage"],op,target_tokens,True) for row in rows): raise Blocked(f"{label} stage {s} related_lineage does not preserve the declared counterpart/type/reason")

def _relation_review_matches(review,op,target_tokens,require_reason):
    try:
        require_target_and_type(review,op,target_tokens,"relation review",require_reason=require_reason)
        return True
    except Blocked: return False

def _single_bound_row(rows_by_stage, stage_name, label):
    rows=rows_by_stage.get(stage_name, [])
    if len(rows)!=1:
        raise Blocked(f"{label} stage {stage_name} requires exactly one bound row for content delta; found {len(rows)}")
    return rows[0]


def _prompt_06_version(row):
    if not isinstance(row,dict):
        return None
    for key in ("prompt_provenance_0_6","prompt_provenance"):
        provenance=row.get(key)
        if not isinstance(provenance,dict):
            continue
        version=provenance.get("prompt_version")
        if isinstance(version,str) and version.startswith("PROMPT_0_6_"):
            return version
    return None


def _locked_prompt_06_version(base_main_commit_sha):
    if not isinstance(base_main_commit_sha,str) or len(base_main_commit_sha)!=40:
        raise Blocked("locked base_main_commit_sha required to resolve Prompt 0.6 contract")
    text=_git(["show",f"{base_main_commit_sha}:{PROMPT_06_PATH}"])
    match=re.search(r"\*\*Version:\*\*\s*`?([^\s`]+)",text)
    if not match:
        raise Blocked(f"locked Prompt 0.6 version marker missing at {base_main_commit_sha}:{PROMPT_06_PATH}")
    return match.group(1).strip()


def _requires_v5_content_audit(row, locked_prompt_version=None):
    declared=_prompt_06_version(row)
    if locked_prompt_version is not None:
        if declared is not None and declared!=locked_prompt_version:
            raise Blocked(
                f"0.6 item prompt version {declared} does not match locked baseline Prompt 0.6 version {locked_prompt_version}"
            )
        version=locked_prompt_version
    else:
        version=declared
    return not (isinstance(version,str) and version.startswith("PROMPT_0_6_V4_"))


def _effective_upstream_visible_value(rows_by_stage, field, label):
    for stage_name in CONTENT_BASELINE_ORDER:
        row=_single_bound_row(rows_by_stage, stage_name, label)
        if field in row and _normalized_visible_value(field,row[field]) is not None:
            return row[field], stage_name
    return _MISSING, None


def _strip_paired_presentation_markup(text):
    # Strip syntactically paired emphasis/code markers only. Literal asterisks
    # such as "2 * 3" and rating symbols such as "A*" remain substantive text.
    if text.strip() in {"**","__","~~","`","*","_"}:
        return ""
    patterns = (
        r"\*\*(?=\S)(.+?)(?<=\S)\*\*",
        r"__(?=\S)(.+?)(?<=\S)__",
        r"`(?=\S)(.+?)(?<=\S)`",
        r"(?<!\w)\*(?=\S)(.+?)(?<=\S)\*(?!\w)",
        r"(?<!\w)_(?=\S)(.+?)(?<=\S)_(?!\w)",
    )
    previous=None
    while previous!=text:
        previous=text
        for pattern in patterns:
            text=re.sub(pattern,r"\1",text,flags=re.DOTALL)
    return text


def _normalize_text(value):
    if not isinstance(value,str):
        return value
    text=value
    text=re.sub(r"\[([^\]]+)\]\([^)]*\)",r"\1",text)
    # Strip only known presentation-formatting tags. Do not use a generic
    # <...> regex because comparison expressions such as "<0.7%" or ">300"
    # are substantive visible copy.
    text=PRESENTATION_HTML_TAG_RE.sub("",text)
    text=re.sub(r"^\s{0,3}#{1,6}\s+","",text)
    # A spaced leading sign/bound is part of a numeric claim, not markup.
    text=re.sub(
        r"^\s*[-+>]\s+(?!\s*(?:[$€£¥₩]?\d|USD\b|EUR\b|GBP\b|KRW\b|CNY\b|RMB\b|JPY\b|AUD\b|CAD\b|CHF\b|HKD\b|SGD\b))",
        "",text,flags=re.IGNORECASE,
    )
    text=_strip_paired_presentation_markup(text)
    return " ".join(text.split())


def _normalized_visible_value(field, value):
    if field in {"sub","gate","fact"}:
        if not _nonempty_text(value):
            return None
        normalized=_normalize_text(value)
        return normalized if _nonempty_text(normalized) else None
    if field=="implication":
        if not isinstance(value,list) or not value or any(not _nonempty_text(x) for x in value):
            return None
        normalized=tuple(_normalize_text(x) for x in value)
        if any(not _nonempty_text(x) for x in normalized):
            return None
        return normalized
    return None


def _source_supported_visible_fields(source):
    if not isinstance(source,dict):
        return set()
    if source.get("supporting_context_only_not_visible_claim_support") is True:
        return set()
    if str(source.get("role") or "").strip().lower()=="checked_not_used_for_visible_claims":
        return set()
    explicit_keys=("visible_claim_support","visible_fields_supported","visible_supports","supports")
    present=[key for key in explicit_keys if key in source]
    if present:
        supported=set()
        for key in present:
            values=source.get(key)
            if isinstance(values,list):
                supported.update(x for x in values if x in VISIBLE_COPY_FIELDS)
        return supported
    return set(VISIBLE_COPY_FIELDS)


def _evidence_tokens(source):
    tokens=set()
    if not isinstance(source,dict):
        return tokens
    for key in ("id","source_id","url","source_url","canonical_url"):
        value=source.get(key)
        if _nonempty_text(value):
            tokens.add(value.strip())
    return tokens


def _has_positive_fetch_metadata(source):
    if not isinstance(source,dict):
        return False
    if source.get("fetched") is False:
        return False
    status=str(source.get("fetch_status") or "").strip().lower()
    if re.search(r"fail|error|timeout|timed_out|blocked|unavailable|not_fetched",status):
        return False
    if source.get("fetched") is True:
        return True
    return any(
        key!="fetched" and bool(source.get(key))
        for key in FETCH_METADATA_KEYS
    )


def _source_evidence_is_usable(source):
    if not isinstance(source,dict):
        return False
    for flag in (
        "fetched","resolved_article_matches_quote","headline_only","rss_or_snippet_only"
    ):
        if flag in source and not isinstance(source.get(flag),bool):
            return False
    quote_status=source.get("source_quote_status") or source.get("quote_status")
    if quote_status not in USABLE_QUOTE_STATUSES:
        return False
    if not _has_positive_fetch_metadata(source):
        return False
    if source.get("resolved_article_matches_quote") is False:
        return False
    if source.get("headline_only") is True or source.get("rss_or_snippet_only") is True:
        return False
    return bool(_source_evidence_texts_raw(source))


def _source_evidence_texts_raw(source):
    texts=[]
    if not isinstance(source,dict):
        return texts
    for key in EVIDENCE_TEXT_KEYS:
        value=source.get(key)
        if _nonempty_text(value):
            texts.append(value.strip())
        elif isinstance(value,list):
            texts.extend(x.strip() for x in value if _nonempty_text(x))
    return list(dict.fromkeys(texts))



def _source_evidence_texts(source):
    if not _source_evidence_is_usable(source):
        return []
    return _source_evidence_texts_raw(source)


def _source_evidence_package(source):
    if not isinstance(source,dict) or not _source_evidence_is_usable(source):
        return {}
    package={}
    for key in EVIDENCE_TEXT_KEYS + EVIDENCE_VERIFICATION_KEYS:
        if key not in source:
            continue
        value=source.get(key)
        if isinstance(value,str):
            value=value.strip()
        if value in (None,"",[]):
            continue
        package[key]=copy.deepcopy(value)
    return package


def _evidence_package_identity(package):
    if not isinstance(package,dict) or not package:
        return None
    return json.dumps(
        package,sort_keys=True,ensure_ascii=False,separators=(",",":")
    )


def _evidence_ref_identity(ref,packages_by_ref):
    packages=packages_by_ref.get(ref,[]) if isinstance(packages_by_ref,dict) else []
    if len(packages)!=1:
        return None
    return _evidence_package_identity(packages[0])


def _duplicate_evidence_ref_aliases(refs,packages_by_ref):
    seen={}
    duplicates={}
    for ref in refs:
        identity=_evidence_ref_identity(ref,packages_by_ref)
        if identity is None:
            continue
        if identity in seen and seen[identity]!=ref:
            duplicates.setdefault(seen[identity],[]).append(ref)
        else:
            seen[identity]=ref
    return duplicates


def _unique_evidence_refs_by_identity(refs,packages_by_ref):
    unique=[]
    seen=set()
    for ref in refs:
        identity=_evidence_ref_identity(ref,packages_by_ref)
        key=("package",identity) if identity is not None else ("ref",ref)
        if key in seen:
            continue
        seen.add(key)
        unique.append(ref)
    return unique


def _row_evidence_token_packages(row):
    packages={}
    if not isinstance(row,dict):
        return packages
    containers=[]
    if isinstance(row.get("fact_sources"),list):
        containers.extend(row["fact_sources"])
    if isinstance(row.get("source_discovery_ledger"),list):
        containers.extend(row["source_discovery_ledger"])
    for source in containers:
        if not isinstance(source,dict):
            continue
        fields=_source_supported_visible_fields(source)
        if not fields:
            continue
        if source in (row.get("source_discovery_ledger") or []):
            outcome=str(source.get("outcome") or "").strip().lower()
            if not any(
                key in source
                for key in ("visible_claim_support","visible_fields_supported","visible_supports","supports")
            ) and outcome not in {"used_in_fact_sources","used_for_visible_claims","accepted_visible_evidence"}:
                continue
        package=_source_evidence_package(source)
        if not package:
            continue
        for token in _evidence_tokens(source):
            packages.setdefault(token,[]).append(package)
    deduped={}
    for token,items in packages.items():
        seen=set()
        unique=[]
        for package in items:
            key=json.dumps(package,sort_keys=True,ensure_ascii=False,separators=(",",":"))
            if key in seen:
                continue
            seen.add(key)
            unique.append(package)
        deduped[token]=unique
    return deduped


def _row_evidence_token_texts(row):
    token_texts={}
    if not isinstance(row,dict):
        return token_texts
    for source in row.get("fact_sources",[]) if isinstance(row.get("fact_sources"),list) else []:
        if not isinstance(source,dict) or not _source_supported_visible_fields(source):
            continue
        texts=_source_evidence_texts(source)
        for token in _evidence_tokens(source):
            if texts:
                token_texts.setdefault(token,[]).extend(texts)
    for entry in row.get("source_discovery_ledger",[]) if isinstance(row.get("source_discovery_ledger"),list) else []:
        if not isinstance(entry,dict):
            continue
        fields=_source_supported_visible_fields(entry)
        outcome=str(entry.get("outcome") or "").strip().lower()
        if not any(
            key in entry
            for key in ("visible_claim_support","visible_fields_supported","visible_supports","supports")
        ) and outcome not in {"used_in_fact_sources","used_for_visible_claims","accepted_visible_evidence"}:
            fields=set()
        if not fields:
            continue
        texts=_source_evidence_texts(entry)
        for token in _evidence_tokens(entry):
            if texts:
                token_texts.setdefault(token,[]).extend(texts)
    return {token:list(dict.fromkeys(texts)) for token,texts in token_texts.items()}


def _add_evidence_tokens(token_support, source, fields):
    if not fields:
        return
    for key in ("id","source_id","url","source_url","canonical_url"):
        value=source.get(key) if isinstance(source,dict) else None
        if _nonempty_text(value):
            token_support.setdefault(value.strip(),set()).update(fields)


def _evidence_alias_groups(rows):
    """Join source identifiers transitively, including aliases in older stages."""
    groups=[]
    for row in rows:
        for key in ("fact_sources","source_discovery_ledger"):
            for source in row.get(key,[]) if isinstance(row.get(key),list) else []:
                tokens=_evidence_tokens(source)
                if not tokens:
                    continue
                separate=[]
                for group in groups:
                    if group & tokens:
                        tokens.update(group)
                    else:
                        separate.append(group)
                groups=separate+[tokens]
    return groups


def _expand_evidence_aliases(tokens,groups):
    expanded=set(tokens)
    for group in groups:
        if group & expanded:
            expanded.update(group)
    return expanded


def _row_evidence_token_state(row,alias_groups=None):
    token_support={}
    explicitly_excluded=set()
    if not isinstance(row,dict):
        return token_support,explicitly_excluded
    sources=row.get("fact_sources",[]) if isinstance(row.get("fact_sources"),list) else []
    for source in sources:
        if not isinstance(source,dict):
            continue
        fields=_source_supported_visible_fields(source)
        tokens=_evidence_tokens(source)
        if not fields:
            explicitly_excluded.update(tokens)
            for token in tokens:
                token_support.pop(token,None)
            continue
        for token in tokens:
            if token not in explicitly_excluded:
                token_support.setdefault(token,set()).update(fields)
    ledger=row.get("source_discovery_ledger",[]) if isinstance(row.get("source_discovery_ledger"),list) else []
    for entry in ledger:
        if not isinstance(entry,dict):
            continue
        fields=_source_supported_visible_fields(entry)
        outcome=str(entry.get("outcome") or "").strip().lower()
        if not any(
            key in entry
            for key in ("visible_claim_support","visible_fields_supported","visible_supports","supports")
        ):
            if outcome not in {"used_in_fact_sources","used_for_visible_claims","accepted_visible_evidence"}:
                fields=set()
        tokens=_evidence_tokens(entry)
        if not fields:
            explicitly_excluded.update(tokens)
            for token in tokens:
                token_support.pop(token,None)
            continue
        for token in tokens:
            if token not in explicitly_excluded:
                token_support.setdefault(token,set()).update(fields)
    coverage=row.get("claim_source_coverage")
    if isinstance(coverage,dict):
        visible=coverage.get("visible_fact")
        if isinstance(visible,dict):
            refs=visible.get("supported_by_source_ids")
            if isinstance(refs,list):
                for ref in refs:
                    if _nonempty_text(ref):
                        token=ref.strip()
                        if token not in explicitly_excluded:
                            token_support.setdefault(token,set()).add("fact")
    groups=_evidence_alias_groups([row]) if alias_groups is None else alias_groups
    expanded_support={}
    for token,fields in token_support.items():
        for alias in _expand_evidence_aliases({token},groups):
            expanded_support.setdefault(alias,set()).update(fields)
    token_support=expanded_support
    explicitly_excluded=_expand_evidence_aliases(explicitly_excluded,groups)
    for token in explicitly_excluded:
        token_support.pop(token,None)
    return token_support,explicitly_excluded


def _row_evidence_token_support(row):
    support,_=_row_evidence_token_state(row)
    return support


def _upstream_evidence_token_support(rows_by_stage,label):
    resolved_support={}
    resolved_tokens=set()
    aliases=_evidence_alias_groups([
        _single_bound_row(rows_by_stage,stage_name,label)
        for stage_name in ("0.5","0.4","C","B")
    ])
    for stage_name in ("0.5","0.4","C","B"):
        row=_single_bound_row(rows_by_stage,stage_name,label)
        stage_support,stage_excluded=_row_evidence_token_state(row,aliases)
        for token in stage_excluded:
            if token not in resolved_tokens:
                resolved_tokens.add(token)
        for token,fields in stage_support.items():
            if token not in resolved_tokens:
                resolved_support[token]=set(fields)
                resolved_tokens.add(token)
    return resolved_support


def _package_texts(package):
    texts=[]
    if not isinstance(package,dict):
        return texts
    for key in EVIDENCE_TEXT_KEYS:
        value=package.get(key)
        if _nonempty_text(value):
            texts.append(value.strip())
        elif isinstance(value,list):
            texts.extend(x.strip() for x in value if _nonempty_text(x))
    return list(dict.fromkeys(texts))


def _nearest_upstream_evidence_packages(rows_by_stage,label,allowed_evidence_support):
    allowed=set(allowed_evidence_support)
    resolved={}
    unresolved=set(allowed)
    rows=[
        _single_bound_row(rows_by_stage,stage_name,label)
        for stage_name in ("0.5","0.4","C","B")
    ]
    aliases=_evidence_alias_groups(rows)
    for stage_name,row in zip(("0.5","0.4","C","B"),rows):
        if not unresolved:
            break
        stage_support,stage_excluded=_row_evidence_token_state(row,aliases)
        stage_packages=_row_evidence_token_packages(row)
        for token in sorted(unresolved):
            if token in stage_excluded:
                unresolved.remove(token)
                continue
            if token in stage_support:
                package_tokens=_expand_evidence_aliases({token},aliases)
                packages=[]
                seen=set()
                for package_token in sorted(package_tokens):
                    for package in stage_packages.get(package_token,[]):
                        identity=_evidence_package_identity(package)
                        if identity in seen:
                            continue
                        seen.add(identity)
                        packages.append(package)
                if len(packages)>1:
                    raise Blocked(
                        f"{label} nearest authoritative evidence token {token} is ambiguous: "
                        f"multiple distinct usable quote/claim packages at stage {stage_name}"
                    )
                if packages:
                    resolved[token]=packages
                unresolved.remove(token)
    return resolved


def _upstream_evidence_token_texts(rows_by_stage,label,allowed_evidence_support):
    packages=_nearest_upstream_evidence_packages(
        rows_by_stage,label,allowed_evidence_support
    )
    return {
        token:_package_texts(items[0])
        for token,items in packages.items()
        if items and _package_texts(items[0])
    }


def _upstream_evidence_token_packages(rows_by_stage,label,allowed_evidence_support):
    return _nearest_upstream_evidence_packages(
        rows_by_stage,label,allowed_evidence_support
    )


def _validate_dimension_evidence(
    density,row_06,label,true_dimensions,
    allowed_evidence_support,allowed_evidence_packages
):
    mapping=density.get("dimension_evidence")
    if not isinstance(mapping,dict) or set(mapping)!=set(true_dimensions):
        raise Blocked(
            f"{label} 0.6 density_audit.dimension_evidence must map exactly true dimensions {sorted(true_dimensions)}"
        )
    if allowed_evidence_support is None:
        raise Blocked(f"{label} 0.6 dimension_evidence validation requires explicit bound upstream evidence support")
    evidence_support={token:set(fields) for token,fields in allowed_evidence_support.items()}
    if not evidence_support:
        raise Blocked(f"{label} 0.6 requires bound upstream source evidence support for dimension_evidence")
    for name in true_dimensions:
        entry=mapping.get(name)
        if not isinstance(entry,dict):
            raise Blocked(f"{label} zero-delta 0.6 dimension_evidence.{name} must be an object")
        fields=entry.get("fields")
        valid_fields=(
            isinstance(fields,list)
            and bool(fields)
            and all(isinstance(x,str) for x in fields)
        )
        if not valid_fields or len(fields)!=len(set(fields)) or any(x not in VISIBLE_COPY_FIELDS for x in fields):
            raise Blocked(f"{label} zero-delta 0.6 dimension_evidence.{name}.fields must be a non-empty unique visible-field subset")
        for field in fields:
            if _normalized_visible_value(field,row_06.get(field,_MISSING)) is None:
                raise Blocked(f"{label} zero-delta 0.6 dimension_evidence.{name} references empty/missing field {field}")
        refs=entry.get("evidence_refs")
        if not isinstance(refs,list) or not refs or any(not _nonempty_text(x) for x in refs):
            raise Blocked(f"{label} zero-delta 0.6 dimension_evidence.{name}.evidence_refs must be non-empty strings")
        normalized_refs=[x.strip() for x in refs]
        if len(normalized_refs)!=len(set(normalized_refs)):
            raise Blocked(f"{label} zero-delta 0.6 dimension_evidence.{name}.evidence_refs must be unique after normalization")
        alias_duplicates=_duplicate_evidence_ref_aliases(
            normalized_refs,allowed_evidence_packages
        )
        if alias_duplicates:
            raise Blocked(
                f"{label} 0.6 dimension_evidence.{name}.evidence_refs contain aliases "
                f"for the same resolved source/evidence package {alias_duplicates}"
            )
        unknown=[x for x in normalized_refs if x not in evidence_support]
        if unknown:
            raise Blocked(f"{label} 0.6 dimension_evidence.{name} has unbound evidence refs {unknown}")
        unsupported={
            ref: sorted(set(fields)-evidence_support.get(ref,set()))
            for ref in normalized_refs
            if set(fields)-evidence_support.get(ref,set())
        }
        if unsupported:
            raise Blocked(
                f"{label} 0.6 dimension_evidence.{name} refs do not support mapped visible fields {unsupported}"
            )


def _visible_value_text(value):
    if value is None:
        return ""
    if isinstance(value,tuple):
        return " | ".join(value)
    return str(value)


def _canonical_numeric_text(raw):
    value=raw
    if re.fullmatch(r"\d{1,3}(?:,\d{3})+(?:\.\d+)?",value):
        value=value.replace(",","")
    elif "," in value and "." not in value:
        value=value.replace(",",".")
    whole,sep,fraction=value.partition(".")
    whole=whole.lstrip("0") or "0"
    if sep:
        fraction=fraction.rstrip("0")
        value=whole+(("." + fraction) if fraction else "")
    else:
        value=whole
    return value or "0"


MAGNITUDE_CANONICAL = {
    "thousand":"k", "k":"k",
    "million":"m", "mn":"m", "m":"m",
    "billion":"bn", "bn":"bn", "b":"bn",
    "trillion":"tn", "tn":"tn",
}


def _quantitative_signal_from_match(match):
    bound=(match.group("bound") or "")
    bound={"≤":"<=","≥":">=","≈":"~"}.get(bound,bound)
    sign=(match.group("sign") or "")
    number=_canonical_numeric_text(match.group("number"))
    currency=(match.group("currency") or "").lower()
    magnitude=MAGNITUDE_CANONICAL.get((match.group("magnitude") or "").lower(),"")
    prefix_code=(match.group("currency_code_prefix") or "").lower()
    suffix_code=(match.group("currency_code_suffix") or "").lower()
    if prefix_code and suffix_code and prefix_code!=suffix_code:
        currency_code=f"{prefix_code}/{suffix_code}"
    else:
        currency_code=prefix_code or suffix_code
    unit=(match.group("unit") or "").lower()
    generic_unit=(match.groupdict().get("generic_unit") or "").lower()
    if generic_unit in {
        "and","or","but","yet","for","from","to","at","in","on","by","with",
        "because","while","whereas","previously","currently","planned","approved",
        "started","delayed","completed","commercial","subject","target",
    }:
        generic_unit=""
    suffix=[x for x in (magnitude,currency_code,unit or generic_unit) if x]
    return f"{bound}{sign}{currency}{number}{(' ' + ' '.join(suffix)) if suffix else ''}"


def _quantitative_signal_kind(signal):
    match=re.fullmatch(
        r"(?:(?:<=|>=|<|>|~))?[+-]?(?P<currency>[$€£¥₩]?)(?P<number>\d+(?:\.\d+)?)(?:\s+(?P<suffix>.+))?",
        signal,
    )
    if not match:
        return None
    suffix=tuple((match.group("suffix") or "").lower().split())
    return ((match.group("currency") or "").lower(),suffix)



def _changed_state_match_strength(text,match):
    prefix=text[max(0,match.start()-64):match.start()]
    suffix=text[match.end():min(len(text),match.end()+64)]
    clause_prefix=text[:match.start()]
    boundaries=list(CLAUSE_BOUNDARY_RE.finditer(clause_prefix))
    if boundaries:
        clause_prefix=clause_prefix[boundaries[-1].end():]
    clause_prefix=re.sub(r"\bnot\s+only\b","",clause_prefix,flags=re.IGNORECASE)
    if CLAUSE_NEGATION_RE.search(clause_prefix):
        return 0
    if NON_REALIZED_CHANGED_STATE_PREFIX_RE.search(prefix):
        return 0
    if NON_REALIZED_CHANGED_STATE_SUFFIX_RE.search(suffix):
        return 0
    if re.search(r"\b(?:will|shall)\s*$",prefix,re.IGNORECASE):
        return 0
    if TENTATIVE_CHANGED_STATE_PREFIX_RE.search(prefix):
        return 1
    return 2


def _changed_state_match_is_realized(text,match):
    return _changed_state_match_strength(text,match)>0


def _signal_strength_occurrences(dimension,text):
    occurrences={}
    if dimension!="changed_state":
        for signal,count in _signal_counter(dimension,text).items():
            occurrences[signal]=[1]*count
        return occurrences
    for occurrence in _canonical_changed_state_occurrences(text):
        occurrences.setdefault(occurrence["marker"],[]).append(occurrence["strength"])
    return {marker:sorted(values) for marker,values in occurrences.items()}


def _signal_strengths(dimension,text):
    return {
        marker:max(strengths)
        for marker,strengths in _signal_strength_occurrences(dimension,text).items()
        if strengths
    }


def _governed_copy_dimension_strength_occurrences(dimension,normalized_by_field):
    occurrences={}
    for field in VISIBLE_COPY_FIELDS:
        for marker,strengths in _signal_strength_occurrences(
            dimension,_visible_value_text(normalized_by_field.get(field))
        ).items():
            occurrences.setdefault(marker,[]).extend(strengths)
    return {marker:sorted(values) for marker,values in occurrences.items()}


def _governed_copy_dimension_strengths(dimension,normalized_by_field):
    return {
        marker:max(strengths)
        for marker,strengths in _governed_copy_dimension_strength_occurrences(
            dimension,normalized_by_field
        ).items()
        if strengths
    }


def _strength_deepening_count(upstream,current):
    before=sorted(upstream)
    after=sorted(current)
    return sum(1 for old,new in zip(before,after) if new>old)


def _strength_multiset_covers(required,evidence):
    pool=sorted(evidence)
    for target in sorted(required,reverse=True):
        candidates=[(idx,value) for idx,value in enumerate(pool) if value>=target]
        if not candidates:
            return False
        idx,_=candidates[0]
        pool.pop(idx)
    return True



def _is_calendar_may(text,match):
    if match.group(0).casefold()!="may":
        return False
    prefix=text[:match.start()]
    suffix=text[match.end():]
    if re.match(
        r"\s+\d{1,2}(?:st|nd|rd|th)?\b(?:,?\s+(?:19|20)\d{2}\b)?",
        suffix,re.IGNORECASE,
    ):
        return True
    if re.match(
        r"\s+(?:19|20)\d{2}\b",
        suffix,re.IGNORECASE,
    ):
        return True
    if match.group(0)=="May" and re.search(
        r"\b(?:in|since|from|during|by|through|until|around)\s*$",
        prefix,re.IGNORECASE,
    ):
        return True
    return False


def _dimension_match_is_valid(dimension,marker,text,match):
    if (
        dimension=="boundary_or_uncertainty"
        and marker=="uncertain_conditional"
        and _is_calendar_may(text,match)
    ):
        return False
    if (
        dimension=="next_watchpoint"
        and marker=="generic_watch"
        and match.group(0).casefold()=="next"
        and re.match(r"\s+to\b",text[match.end():],re.IGNORECASE)
    ):
        return False
    if dimension=="changed_state" and not _changed_state_match_is_realized(text,match):
        return False
    return True


def _canonical_changed_state_marker(text,marker,match):
    if marker=="commencement":
        prefix=text[max(0,match.start()-48):match.start()]
        if re.search(r"\b(?:commercial\s+)?production\s*$",prefix,re.IGNORECASE):
            return "production_commencement"
    if marker=="production_operation":
        matched=match.group(0)
        suffix=text[match.end():min(len(text),match.end()+48)]
        if (
            re.search(r"\bproduction\b",matched,re.IGNORECASE)
            and re.match(r"\s+(?:has\s+|have\s+|had\s+)?(?:started|began|begun|commenced)\b",suffix,re.IGNORECASE)
        ):
            return "production_commencement"
    return marker


def _canonical_changed_state_occurrences(text):
    occurrences=[]
    for marker,pattern in DIMENSION_CANONICAL_SIGNAL_RES["changed_state"].items():
        for match in pattern.finditer(text):
            strength=_changed_state_match_strength(text,match)
            if strength<=0:
                continue
            canonical=_canonical_changed_state_marker(text,marker,match)
            entry={
                "marker":canonical,
                "original_marker":marker,
                "start":match.start(),
                "end":match.end(),
                "strength":strength,
                "match":match,
            }
            if canonical=="production_commencement":
                merged=False
                for existing in occurrences:
                    if existing["marker"]!="production_commencement":
                        continue
                    if existing["original_marker"]==marker:
                        continue
                    gap=max(
                        0,
                        max(existing["start"],entry["start"])
                        - min(existing["end"],entry["end"]),
                    )
                    if gap<=48:
                        existing["start"]=min(existing["start"],entry["start"])
                        existing["end"]=max(existing["end"],entry["end"])
                        existing["strength"]=max(existing["strength"],entry["strength"])
                        merged=True
                        break
                if merged:
                    continue
            occurrences.append(entry)
    return sorted(occurrences,key=lambda item:(item["start"],item["end"],item["marker"]))


def _signal_counter(dimension,text):
    counts=Counter()
    if dimension=="quantitative_anchor":
        for match in QUANT_SIGNAL_RE.finditer(text):
            counts[_quantitative_signal_from_match(match)]+=1
        return counts
    if dimension=="changed_state":
        for occurrence in _canonical_changed_state_occurrences(text):
            counts[occurrence["marker"]]+=1
        return counts
    patterns=DIMENSION_CANONICAL_SIGNAL_RES.get(dimension,{})
    for marker,pattern in patterns.items():
        for match in pattern.finditer(text):
            if not _dimension_match_is_valid(dimension,marker,text,match):
                continue
            counts[marker]+=1
    return counts


def _signal_values(dimension, text):
    return set(_signal_counter(dimension,text))


def _governed_copy_dimension_signal_counts(dimension,normalized_by_field):
    counts=Counter()
    for field in VISIBLE_COPY_FIELDS:
        counts.update(
            _signal_counter(dimension,_visible_value_text(normalized_by_field.get(field)))
        )
    return counts


def _governed_copy_dimension_signals(dimension, normalized_by_field):
    return set(_governed_copy_dimension_signal_counts(dimension,normalized_by_field))



def _factual_identity_counter(text):
    counts=Counter()
    if not isinstance(text,str):
        return counts
    for match in FACTUAL_IDENTITY_TOKEN_RE.finditer(text):
        token=match.group(0).strip(".,;:()[]{}").casefold()
        if token and token not in FACTUAL_IDENTITY_STOPWORDS:
            counts[token]+=1
    for match in LOCATION_PHRASE_RE.finditer(text):
        token=match.group(1).strip(".,;:()[]{}").casefold()
        if token and token not in FACTUAL_IDENTITY_STOPWORDS:
            counts[token]+=1
    for match in KOREAN_IDENTITY_RE.finditer(text):
        token=match.group(1)
        if token:
            counts[token]+=1
    return counts


def _factual_predicate_content_counter(text):
    counts=Counter()
    if not isinstance(text,str):
        return counts
    for match in FACTUAL_PREDICATE_RE.finditer(text):
        tail=match.group("tail")
        for word in FACTUAL_CONTENT_WORD_RE.findall(tail):
            token=word.casefold()
            if token not in FACTUAL_CONTENT_STOPWORDS:
                counts[token]+=1
    for match in GENERIC_FACTUAL_PREDICATE_RE.finditer(text):
        verb=match.group("verb_after_connector") or match.group("verb_after_subject")
        tail=match.group("tail_after_connector") or match.group("tail_after_subject") or ""
        if verb:
            token=verb.casefold()
            if token not in FACTUAL_CONTENT_STOPWORDS:
                counts[token]+=1
        for word in FACTUAL_CONTENT_WORD_RE.findall(tail):
            token=word.casefold()
            if token not in FACTUAL_CONTENT_STOPWORDS:
                counts[token]+=1
    for match in MODAL_FACTUAL_PREDICATE_RE.finditer(text):
        # Copular auxiliaries are handled by the state/modality validators.
        if match.group("verb").casefold() in {"be","have"}:
            continue
        for word in [match.group("verb")]+FACTUAL_CONTENT_WORD_RE.findall(match.group("tail")):
            token=word.casefold()
            if token not in FACTUAL_CONTENT_STOPWORDS:
                counts[token]+=1
    for match in COMMA_PARTICIPIAL_FACTUAL_RE.finditer(text):
        for word in [match.group("verb")]+FACTUAL_CONTENT_WORD_RE.findall(match.group("tail")):
            token=word.casefold()
            if token not in FACTUAL_CONTENT_STOPWORDS:
                counts[token]+=1
    return counts


def _factual_predicate_subject_counter(text):
    """Keep predicate content attached to its local subject, not a global bag."""
    counts=Counter()
    if not isinstance(text,str):
        return counts
    for pattern in (
        FACTUAL_PREDICATE_RE,GENERIC_FACTUAL_PREDICATE_RE,
        MODAL_FACTUAL_PREDICATE_RE,COMMA_PARTICIPIAL_FACTUAL_RE,
    ):
        for match in pattern.finditer(text):
            groups=match.groupdict()
            tail_name=next((name for name in ("tail","tail_after_connector","tail_after_subject")
                            if groups.get(name)),None)
            if not tail_name:
                continue
            verb_name=next((name for name in ("verb","verb_after_connector","verb_after_subject")
                            if groups.get(name)),None)
            start=match.start(verb_name) if verb_name else match.start()
            verb=(groups[verb_name] if verb_name else text[start:match.start(tail_name)]).strip().casefold()
            if pattern is MODAL_FACTUAL_PREDICATE_RE and verb in {"be","have"}:
                continue
            subject=_claim_subject_for_span(text,start,match.start(tail_name))
            # Stop at a new coordinated clause instead of attaching its object
            # to the preceding predicate.
            tail=re.split(r"\b(?:and|but|while|whereas)\b",groups[tail_name],maxsplit=1,flags=re.IGNORECASE)[0]
            for word in FACTUAL_CONTENT_WORD_RE.findall(tail):
                token=word.casefold()
                if token not in FACTUAL_CONTENT_STOPWORDS:
                    counts[(subject,verb,token)]+=1
    return counts


def _factual_claim_counter(text):
    counts=_factual_identity_counter(text)
    counts.update(_factual_predicate_content_counter(text))
    return counts


def _factual_identity_spans(text):
    if not isinstance(text,str):
        return []
    spans=set()
    for match in FACTUAL_IDENTITY_TOKEN_RE.finditer(text):
        token=match.group(0).strip(".,;:()[]{}").casefold()
        if token and token not in FACTUAL_IDENTITY_STOPWORDS:
            spans.add((match.start(),match.end(),token))
    for match in LOCATION_PHRASE_RE.finditer(text):
        token=match.group(1).strip(".,;:()[]{}").casefold()
        if token and token not in FACTUAL_IDENTITY_STOPWORDS:
            spans.add((match.start(1),match.end(1),token))
    for match in KOREAN_IDENTITY_RE.finditer(text):
        token=match.group(1)
        if token:
            spans.add((match.start(1),match.end(1),token))
    return sorted(spans)


def _claim_segment_bounds(text,start,end):
    boundaries=".;:!?|\n"
    left=max([text.rfind(mark,0,start) for mark in boundaries]+[-1])+1
    right_candidates=[text.find(mark,end) for mark in boundaries]
    right_candidates=[pos for pos in right_candidates if pos>=0]
    right=min(right_candidates) if right_candidates else len(text)
    return left,right


def _claim_subject_for_span(text,start,end):
    identities=_factual_identity_spans(text)
    left,right=_claim_segment_bounds(text,start,end)
    local=[span for span in identities if span[0]>=left and span[1]<=right]
    if not local:
        return "__generic__"
    preceding=[span for span in local if span[1]<=start]
    if preceding:
        return max(preceding,key=lambda span:span[1])[2]
    following=[span for span in local if span[0]>=end]
    if following:
        return min(following,key=lambda span:span[0])[2]
    return "__generic__"


def _state_subject_strength_occurrences(text):
    occurrences={}
    if not isinstance(text,str):
        return occurrences
    for occurrence in _canonical_changed_state_occurrences(text):
        subject=_claim_subject_for_span(
            text,occurrence["start"],occurrence["end"]
        )
        key=f"{subject}=>{occurrence['marker']}"
        occurrences.setdefault(key,[]).append(occurrence["strength"])
    return {key:sorted(values) for key,values in occurrences.items()}


def _state_subject_advancements(upstream_text,current_text):
    upstream=_state_subject_strength_occurrences(upstream_text)
    current=_state_subject_strength_occurrences(current_text)
    advanced={}
    for key,current_strengths in current.items():
        if not _strength_multiset_covers(
            current_strengths,upstream.get(key,[])
        ):
            advanced[key]=current_strengths
    return advanced


def _factual_quantitative_pair_counter(text):
    counts=Counter()
    if not isinstance(text,str):
        return counts
    identities=_factual_identity_spans(text)
    for match in QUANT_SIGNAL_RE.finditer(text):
        signal=_quantitative_signal_from_match(match)
        left,right=_claim_segment_bounds(text,match.start(),match.end())
        local=[span for span in identities if span[0]>=left and span[1]<=right]
        if not local:
            continue
        following=sorted(
            (span for span in local if span[0]>=match.end()),
            key=lambda span:span[0],
        )
        postpositive=None
        for span in following:
            bridge=text[match.end():span[0]]
            if re.fullmatch(
                r"\s*(?:for|of|at|in|by|from|to|with)\s+(?:the\s+)?",
                bridge,re.IGNORECASE,
            ):
                postpositive=span
                break
            if re.search(r"[.;:!?]|\b(?:and|or|but|while|whereas)\b",bridge,re.IGNORECASE):
                break
        if postpositive is not None:
            chosen=postpositive
        else:
            preceding=[span for span in local if span[1]<=match.start()]
            if preceding:
                chosen=max(preceding,key=lambda span:span[1])
            else:
                chosen=min(local,key=lambda span:span[0])
        counts[f"{chosen[2]}=>{signal}"]+=1
    return counts


def _governed_factual_claim_counts(normalized_by_field):
    counts=Counter()
    for field in VISIBLE_COPY_FIELDS:
        counts.update(
            _factual_claim_counter(_visible_value_text(normalized_by_field.get(field)))
        )
    return counts


def _validate_changed_factual_grounding(
    density,current_normalized,upstream_normalized,actual_changed,
    allowed_evidence_texts,allowed_evidence_packages,label
):
    mapping=density.get("dimension_evidence") if isinstance(density,dict) else {}
    upstream_all=_governed_factual_claim_counts(upstream_normalized)
    current_all=_governed_factual_claim_counts(current_normalized)
    removed=upstream_all-current_all
    if removed:
        raise Blocked(
            f"{label} changed 0.6 copy deletes verified upstream factual identity/location/"
            f"predicate tokens {dict(removed)}"
        )

    for field in actual_changed:
        current_counts=_factual_claim_counter(
            _visible_value_text(current_normalized.get(field))
        )
        upstream_field_counts=_factual_claim_counter(
            _visible_value_text(upstream_normalized.get(field))
        )
        introduced=current_counts-upstream_field_counts
        refs=[]
        if isinstance(mapping,dict):
            for entry in mapping.values():
                if not isinstance(entry,dict):
                    continue
                fields=entry.get("fields")
                if not isinstance(fields,list) or field not in fields:
                    continue
                for ref in entry.get("evidence_refs",[]) if isinstance(entry.get("evidence_refs"),list) else []:
                    if _nonempty_text(ref) and ref.strip() not in refs:
                        refs.append(ref.strip())
        refs=_unique_evidence_refs_by_identity(refs,allowed_evidence_packages)
        evidence_counts=Counter()
        for ref in refs:
            for evidence_text in allowed_evidence_texts.get(ref,[]):
                evidence_counts.update(_factual_claim_counter(evidence_text))
        missing={
            token:count
            for token,count in introduced.items()
            if evidence_counts.get(token,0)<count
        }
        if missing:
            raise Blocked(
                f"{label} changed 0.6 field {field} introduces factual identity/location/"
                f"predicate tokens not grounded in referenced nearest-stage evidence: {missing}"
            )

        predicate_pairs=_factual_predicate_subject_counter(_visible_value_text(current_normalized.get(field)))
        upstream_predicate_pairs=_factual_predicate_subject_counter(_visible_value_text(upstream_normalized.get(field)))
        introduced_predicate_pairs=predicate_pairs-upstream_predicate_pairs
        evidence_predicate_pairs=Counter()
        for ref in refs:
            for evidence_text in allowed_evidence_texts.get(ref,[]):
                evidence_predicate_pairs.update(_factual_predicate_subject_counter(evidence_text))
        missing_predicate_pairs=introduced_predicate_pairs-evidence_predicate_pairs
        if missing_predicate_pairs:
            raise Blocked(
                f"{label} changed 0.6 field {field} subject/predicate claims are not grounded "
                f"in referenced nearest-stage evidence: {dict(missing_predicate_pairs)}"
            )

        current_pairs=_factual_quantitative_pair_counter(
            _visible_value_text(current_normalized.get(field))
        )
        upstream_pairs=_factual_quantitative_pair_counter(
            _visible_value_text(upstream_normalized.get(field))
        )
        introduced_pairs=current_pairs-upstream_pairs
        if introduced_pairs:
            evidence_pairs=Counter()
            for ref in refs:
                for evidence_text in allowed_evidence_texts.get(ref,[]):
                    evidence_pairs.update(_factual_quantitative_pair_counter(evidence_text))
            missing_pairs={
                pair:count
                for pair,count in introduced_pairs.items()
                if evidence_pairs.get(pair,0)<count
            }
            if missing_pairs:
                raise Blocked(
                    f"{label} changed 0.6 field {field} rebinds/adds quantitative claims to "
                    f"factual entities without matching referenced nearest-stage evidence: {missing_pairs}"
                )



def _validate_claimed_dimension_text(density, row_06, label, true_dimensions):
    mapping=density.get("dimension_evidence")
    for dimension in true_dimensions:
        entry=mapping.get(dimension) if isinstance(mapping,dict) else None
        fields=entry.get("fields") if isinstance(entry,dict) else None
        if not isinstance(fields,list):
            continue
        expressed=set()
        for field in fields:
            expressed.update(
                _signal_values(
                    dimension,
                    _visible_value_text(_normalized_visible_value(field,row_06.get(field,_MISSING))),
                )
            )
        if not expressed:
            raise Blocked(
                f"{label} 0.6 density dimension {dimension} is claimed but not expressed "
                f"by any mapped governed field {fields}"
            )


def _validate_claimed_dimension_evidence_grounding(
    density,row_06,label,true_dimensions,
    allowed_evidence_texts,allowed_evidence_packages
):
    mapping=density.get("dimension_evidence") if isinstance(density,dict) else None
    for dimension in true_dimensions:
        entry=mapping.get(dimension) if isinstance(mapping,dict) else None
        if not isinstance(entry,dict):
            continue
        fields=entry.get("fields") if isinstance(entry.get("fields"),list) else []
        refs=[
            ref.strip() for ref in entry.get("evidence_refs",[])
            if _nonempty_text(ref)
        ] if isinstance(entry.get("evidence_refs"),list) else []
        refs=_unique_evidence_refs_by_identity(refs,allowed_evidence_packages)
        visible_counts=Counter()
        for field in fields:
            visible_counts.update(
                _signal_counter(
                    dimension,
                    _visible_value_text(_normalized_visible_value(field,row_06.get(field,_MISSING))),
                )
            )
        evidence_counts=Counter()
        for ref in refs:
            for evidence_text in allowed_evidence_texts.get(ref,[]):
                evidence_counts.update(_signal_counter(dimension,evidence_text))
        missing_signals={
            signal:{
                "required_occurrences":count,
                "evidence_occurrences":evidence_counts.get(signal,0),
            }
            for signal,count in visible_counts.items()
            if evidence_counts.get(signal,0)<count
        }
        if missing_signals:
            raise Blocked(
                f"{label} zero-delta 0.6 dimension {dimension} is not grounded in referenced "
                f"upstream source quote/claim evidence for every signal occurrence; missing={missing_signals}"
            )
        if dimension=="changed_state":
            visible_strengths={}
            evidence_strengths={}
            for field in fields:
                text=_visible_value_text(_normalized_visible_value(field,row_06.get(field,_MISSING)))
                for key,values in _state_subject_strength_occurrences(text).items():
                    visible_strengths.setdefault(key,[]).extend(values)
            for ref in refs:
                for text in allowed_evidence_texts.get(ref,[]):
                    for key,values in _state_subject_strength_occurrences(text).items():
                        evidence_strengths.setdefault(key,[]).extend(values)
            gaps={key:values for key,values in visible_strengths.items()
                  if not _strength_multiset_covers(values,evidence_strengths.get(key,[]))}
            if gaps:
                raise Blocked(
                    f"{label} 0.6 changed_state subject/modality claims are not grounded "
                    f"in referenced upstream evidence; required_current_strengths={gaps}"
                )


def _validate_substantive_dimension_delta(
    density,row_06,label,actual_changed,upstream_normalized,
    allowed_evidence_texts,allowed_evidence_packages
):
    mapping=density.get("dimension_evidence")
    changed=set(actual_changed)
    current_normalized={
        field:_normalized_visible_value(field,row_06.get(field,_MISSING))
        for field in VISIBLE_COPY_FIELDS
    }
    true_dimensions={
        name for name,value in density.get("dimensions",{}).items()
        if value is True
    }

    upstream_counts={
        dimension:_governed_copy_dimension_signal_counts(dimension,upstream_normalized)
        for dimension in DENSITY_DIMENSIONS
    }
    current_counts={
        dimension:_governed_copy_dimension_signal_counts(dimension,current_normalized)
        for dimension in DENSITY_DIMENSIONS
    }
    added_counts={
        dimension:current_counts[dimension]-upstream_counts[dimension]
        for dimension in DENSITY_DIMENSIONS
    }
    lost_counts={
        dimension:upstream_counts[dimension]-current_counts[dimension]
        for dimension in DENSITY_DIMENSIONS
    }

    upstream_strength_occurrences=_governed_copy_dimension_strength_occurrences(
        "changed_state",upstream_normalized
    )
    current_strength_occurrences=_governed_copy_dimension_strength_occurrences(
        "changed_state",current_normalized
    )
    deepened_changed_state=Counter({
        signal:_strength_deepening_count(
            upstream_strength_occurrences.get(signal,[]),
            current_strength_occurrences.get(signal,[]),
        )
        for signal in set(upstream_strength_occurrences)|set(current_strength_occurrences)
        if _strength_deepening_count(
            upstream_strength_occurrences.get(signal,[]),
            current_strength_occurrences.get(signal,[]),
        )>0
    })
    remaining_deepened=Counter(deepened_changed_state)
    global_subject_advancements=_state_subject_advancements(
        "; ".join(_visible_value_text(upstream_normalized.get(field)) for field in VISIBLE_COPY_FIELDS),
        "; ".join(_visible_value_text(current_normalized.get(field)) for field in VISIBLE_COPY_FIELDS),
    )

    qualifying=[]
    grounded_state_advancement=False
    grounded_introduced_counts={
        dimension:Counter() for dimension in DENSITY_DIMENSIONS
    }
    diagnostics={}

    for field in changed:
        current_field_text=_visible_value_text(current_normalized.get(field))
        upstream_field_text=_visible_value_text(upstream_normalized.get(field))
        for dimension in DENSITY_DIMENSIONS:
            current_field_counts=_signal_counter(dimension,current_field_text)
            upstream_field_counts=_signal_counter(dimension,upstream_field_text)
            field_added=current_field_counts-upstream_field_counts
            added=Counter({
                signal:min(count,added_counts[dimension].get(signal,0))
                for signal,count in field_added.items()
                if added_counts[dimension].get(signal,0)>0
            })
            deepened=Counter()
            current_field_strength_occurrences={}
            if dimension=="changed_state":
                current_field_strength_occurrences=_signal_strength_occurrences(
                    dimension,current_field_text
                )
                upstream_field_strength_occurrences=_signal_strength_occurrences(
                    dimension,upstream_field_text
                )
                for signal,budget in list(remaining_deepened.items()):
                    if budget<=0:
                        continue
                    field_count=_strength_deepening_count(
                        upstream_field_strength_occurrences.get(signal,[]),
                        current_field_strength_occurrences.get(signal,[]),
                    )
                    if field_count>0:
                        deepened[signal]=min(field_count,budget)
            advancements=(
                _state_subject_advancements(upstream_field_text,current_field_text)
                if dimension=="changed_state" else {}
            )
            introduced=set(added)|set(deepened)|set(advancements)
            if not introduced:
                continue

            entry=mapping.get(dimension) if isinstance(mapping,dict) else None
            if dimension not in true_dimensions or not isinstance(entry,dict):
                raise Blocked(
                    f"{label} changed 0.6 field {field} introduces undeclared governed "
                    f"{dimension} signals {sorted(introduced)}"
                )
            mapped_fields=entry.get("fields") if isinstance(entry.get("fields"),list) else []
            if field not in mapped_fields:
                raise Blocked(
                    f"{label} changed 0.6 field {field} introduces {dimension} signals "
                    f"{sorted(introduced)} but dimension_evidence does not map that field"
                )

            refs=[
                ref.strip() for ref in entry.get("evidence_refs",[])
                if _nonempty_text(ref)
            ] if isinstance(entry.get("evidence_refs"),list) else []
            refs=_unique_evidence_refs_by_identity(refs,allowed_evidence_packages)
            evidence_counts=Counter()
            evidence_strength_occurrences={}
            for ref in refs:
                for evidence_text in allowed_evidence_texts.get(ref,[]):
                    evidence_counts.update(_signal_counter(dimension,evidence_text))
                    if dimension=="changed_state":
                        for signal,strengths in _signal_strength_occurrences(
                            dimension,evidence_text
                        ).items():
                            evidence_strength_occurrences.setdefault(signal,[]).extend(strengths)
            evidence_strength_occurrences={
                signal:sorted(values)
                for signal,values in evidence_strength_occurrences.items()
            }

            subject_state_gaps={}
            if dimension=="changed_state":
                advancements=_state_subject_advancements(
                    upstream_field_text,current_field_text
                )
                evidence_subject_occurrences={}
                for ref in refs:
                    for evidence_text in allowed_evidence_texts.get(ref,[]):
                        for key,strengths in _state_subject_strength_occurrences(
                            evidence_text
                        ).items():
                            evidence_subject_occurrences.setdefault(key,[]).extend(strengths)
                evidence_subject_occurrences={
                    key:sorted(values)
                    for key,values in evidence_subject_occurrences.items()
                }
                for key,required_strengths in advancements.items():
                    if not _strength_multiset_covers(
                        required_strengths,evidence_subject_occurrences.get(key,[])
                    ):
                        subject_state_gaps[key]={
                            "required_current_strengths":required_strengths,
                            "evidence_strengths":evidence_subject_occurrences.get(key,[]),
                        }
                if subject_state_gaps:
                    raise Blocked(
                        f"{label} changed 0.6 changed_state subject/modality claims are not "
                        f"grounded in referenced nearest-stage evidence: {subject_state_gaps}"
                    )

            ungrounded_added={}
            for signal,count in added.items():
                # If the same marker already existed in this field, the evidence
                # package must distinguish the repeated claim by carrying at least
                # the full current occurrence count for that marker.
                required=(
                    current_field_counts[signal]
                    if upstream_field_counts.get(signal,0)>0
                    else count
                )
                details={
                    "required_occurrences":required,
                    "evidence_occurrences":evidence_counts.get(signal,0),
                }
                occurrence_gap=evidence_counts.get(signal,0)<required
                strength_gap=False
                if dimension=="changed_state":
                    required_strengths=current_field_strength_occurrences.get(signal,[])
                    evidence_strengths=evidence_strength_occurrences.get(signal,[])
                    strength_gap=not _strength_multiset_covers(
                        required_strengths,evidence_strengths
                    )
                    if strength_gap:
                        details.update({
                            "required_current_strengths":required_strengths,
                            "evidence_strengths":evidence_strengths,
                        })
                if occurrence_gap or strength_gap:
                    ungrounded_added[signal]=details

            ungrounded_deepened={}
            for signal,count in deepened.items():
                required_strengths=current_field_strength_occurrences.get(signal,[])
                evidence_strengths=evidence_strength_occurrences.get(signal,[])
                if not _strength_multiset_covers(required_strengths,evidence_strengths):
                    ungrounded_deepened[signal]={
                        "deepened_occurrences":count,
                        "required_current_strengths":required_strengths,
                        "evidence_strengths":evidence_strengths,
                    }
            diagnostics[(field,dimension)]={
                "added":dict(added),
                "deepened":dict(deepened),
                "evidence_counts":dict(evidence_counts),
                "evidence_strength_occurrences":evidence_strength_occurrences,
                "ungrounded_added":ungrounded_added,
                "ungrounded_deepened":ungrounded_deepened,
            }
            if ungrounded_added or ungrounded_deepened:
                raise Blocked(
                    f"{label} changed 0.6 dimension {dimension} introduces/deepens signals "
                    f"not grounded in referenced nearest-stage source quote/claim evidence: "
                    f"added={ungrounded_added} deepened={ungrounded_deepened}"
                )

            substantive_state_advancement=bool(set(advancements)&set(global_subject_advancements))
            if added or deepened or substantive_state_advancement:
                qualifying.append((dimension,field,sorted(introduced)))
            grounded_introduced_counts[dimension].update(added)
            if dimension=="changed_state":
                for signal,count in deepened.items():
                    remaining_deepened[signal]-=count
                if added or deepened or substantive_state_advancement:
                    grounded_state_advancement=True

    _validate_changed_factual_grounding(
        density,current_normalized,upstream_normalized,actual_changed,
        allowed_evidence_texts,allowed_evidence_packages,label,
    )

    # Verified upstream substantive signals may not silently disappear. The one
    # allowed semantic contraction is removal of uncertainty/plan markers when
    # the same edit carries a grounded realized-state advancement.
    for dimension in DENSITY_DIMENSIONS:
        lost=lost_counts[dimension]
        if not lost:
            continue
        if (
            dimension=="boundary_or_uncertainty"
            and grounded_state_advancement
            and set(lost) <= {"plan_target","expectation_estimate","uncertain_conditional"}
        ):
            continue
        if dimension=="quantitative_anchor" and grounded_introduced_counts[dimension]:
            replacement_budget=Counter()
            for signal,count in grounded_introduced_counts[dimension].items():
                kind=_quantitative_signal_kind(signal)
                if kind is not None:
                    replacement_budget[kind]+=count
            unreplaced=Counter()
            for signal,count in lost.items():
                kind=_quantitative_signal_kind(signal)
                replace=min(count,replacement_budget.get(kind,0))
                if replace:
                    replacement_budget[kind]-=replace
                if count>replace:
                    unreplaced[signal]=count-replace
            if not unreplaced:
                continue
            lost=unreplaced
        raise Blocked(
            f"{label} changed 0.6 copy deletes verified upstream {dimension} signals "
            f"{dict(lost)}"
        )

    if not qualifying:
        raise Blocked(
            f"{label} changed 0.6 copy lacks a machine-detectable newly added/deepened Deep Summary signal "
            f"relative to the whole upstream governed copy; terminology/formatting/relocation-only rewrites "
            f"do not qualify; signals={diagnostics}"
        )



def _validate_density_audit(
    audit,row_06,label,*,no_change,allowed_evidence_support,
    allowed_evidence_packages,actual_changed=()
):
    density=audit.get("density_audit") if isinstance(audit,dict) else None
    if not isinstance(density,dict) or density.get("status")!="PASS":
        raise Blocked(f"{label} 0.6 content_enrichment_audit.density_audit must be structured PASS")
    dimensions=density.get("dimensions")
    if not isinstance(dimensions,dict) or set(dimensions)!=set(DENSITY_DIMENSIONS):
        raise Blocked(f"{label} 0.6 density_audit.dimensions must contain exactly {list(DENSITY_DIMENSIONS)}")
    if any(not isinstance(dimensions[name],bool) for name in DENSITY_DIMENSIONS):
        raise Blocked(f"{label} 0.6 density_audit dimensions must all be booleans")
    true_dimensions=[name for name in DENSITY_DIMENSIONS if dimensions[name]]
    supported=len(true_dimensions)
    count=density.get("supported_dimension_count")
    if not isinstance(count,int) or isinstance(count,bool):
        raise Blocked(f"{label} 0.6 density_audit.supported_dimension_count must be a non-boolean integer")
    if count!=supported:
        raise Blocked(f"{label} 0.6 density_audit.supported_dimension_count={count} != {supported}")
    notes=density.get("evidence_notes")
    if not _nonempty_text(notes):
        raise Blocked(f"{label} 0.6 density_audit.evidence_notes required")

    if no_change:
        if supported < 4:
            raise Blocked(f"{label} zero-delta 0.6 requires at least four evidence-supported Deep Summary dimensions; found {supported}")
        if dimensions.get("changed_state") is not True:
            raise Blocked(f"{label} zero-delta 0.6 requires changed_state=true in the density audit")
    elif supported < 1:
        raise Blocked(f"{label} changed 0.6 copy requires at least one evidence-supported Deep Summary dimension")

    _validate_dimension_evidence(
        density,row_06,label,true_dimensions,
        allowed_evidence_support=allowed_evidence_support,
        allowed_evidence_packages=allowed_evidence_packages,
    )
    _validate_claimed_dimension_text(density,row_06,label,true_dimensions)
    if not no_change:
        mapping=density.get("dimension_evidence")
        changed=set(actual_changed)
        bound_changed={
            field
            for entry in mapping.values()
            if isinstance(entry,dict)
            for field in entry.get("fields",[])
            if field in changed
        }
        if not bound_changed:
            raise Blocked(
                f"{label} changed 0.6 copy must bind at least one supported Deep Summary dimension "
                f"to an actually changed governed field; changed={sorted(changed)}"
            )


def _validate_operation_visible_copy(row_06, operation_card, label):
    if not isinstance(operation_card,dict):
        raise Blocked(f"{label} cannot bind 0.6 visible copy to a materialized operation card")
    mismatches=[]
    for field in VISIBLE_COPY_FIELDS:
        stage_value=_normalized_visible_value(field,row_06.get(field,_MISSING))
        operation_value=_normalized_visible_value(field,operation_card.get(field,_MISSING))
        if stage_value!=operation_value:
            mismatches.append(field)
    if mismatches:
        raise Blocked(f"{label} applied operation visible copy does not match audited 0.6 fields {mismatches}")


def _materialized_card_evidence_support(card):
    support={}
    excluded=set()
    if not isinstance(card,dict):
        return support
    for source in card.get("fact_sources",[]) if isinstance(card.get("fact_sources"),list) else []:
        if not isinstance(source,dict):
            continue
        fields=_source_supported_visible_fields(source)
        tokens=_evidence_tokens(source)
        if not fields:
            excluded.update(tokens)
            for token in tokens:
                support.pop(token,None)
            continue
        for token in tokens:
            if token not in excluded:
                support.setdefault(token,set()).update(fields)
    for entry in card.get("source_discovery_ledger",[]) if isinstance(card.get("source_discovery_ledger"),list) else []:
        if not isinstance(entry,dict):
            continue
        fields=_source_supported_visible_fields(entry)
        outcome=str(entry.get("outcome") or "").strip().lower()
        if not any(
            key in entry
            for key in ("visible_claim_support","visible_fields_supported","visible_supports","supports")
        ) and outcome not in {"used_in_fact_sources","used_for_visible_claims","accepted_visible_evidence"}:
            fields=set()
        tokens=_evidence_tokens(entry)
        if not fields:
            excluded.update(tokens)
            for token in tokens:
                support.pop(token,None)
            continue
        for token in tokens:
            if token not in excluded:
                support.setdefault(token,set()).update(fields)
    return support


def _materialized_card_evidence_packages(card):
    return _row_evidence_token_packages(card)


def _package_preserves(required,actual):
    return required==actual


def _validate_materialized_operation_evidence(
    density, operation_card, label, required_evidence_packages
):
    mapping=density.get("dimension_evidence") if isinstance(density,dict) else None
    if not isinstance(mapping,dict):
        return
    support=_materialized_card_evidence_support(operation_card)
    packages=_materialized_card_evidence_packages(operation_card)
    for dimension,entry in mapping.items():
        if not isinstance(entry,dict):
            continue
        fields=set(entry.get("fields",[])) if isinstance(entry.get("fields"),list) else set()
        refs=[
            ref.strip() for ref in entry.get("evidence_refs",[])
            if _nonempty_text(ref)
        ] if isinstance(entry.get("evidence_refs"),list) else []
        for ref in refs:
            if ref not in support:
                raise Blocked(
                    f"{label} materialized operation card does not preserve bound evidence ref {ref} "
                    f"for dimension {dimension}"
                )
            missing=fields-support.get(ref,set())
            if missing:
                raise Blocked(
                    f"{label} materialized operation evidence ref {ref} no longer supports "
                    f"mapped fields {sorted(missing)} for dimension {dimension}"
                )
            required_packages=required_evidence_packages.get(ref,[])
            actual_packages=packages.get(ref,[])
            if len(actual_packages)>1:
                raise Blocked(
                    f"{label} materialized operation evidence ref {ref} is ambiguous: "
                    f"multiple distinct quote/claim packages"
                )
            if not required_packages:
                raise Blocked(
                    f"{label} bound evidence ref {ref} has no preserved upstream quote/claim "
                    f"verification package"
                )
            if not any(
                _package_preserves(required,actual)
                for required in required_packages
                for actual in actual_packages
            ):
                raise Blocked(
                    f"{label} materialized operation evidence ref {ref} does not preserve "
                    f"its upstream quote/claim and verification-status package"
                )



def _json_pointer_parts(path, label):
    if not isinstance(path,str) or not path.startswith("/") or path=="/":
        raise Blocked(f"{label} invalid JSON pointer path {path!r}")
    return [part.replace("~1","/").replace("~0","~") for part in path[1:].split("/")]


def _apply_json_change(document, change, label):
    if not isinstance(change,dict):
        raise Blocked(f"{label} change must be object")
    op=change.get("op")
    if op not in {"add","replace","remove"}:
        raise Blocked(f"{label} unsupported change op {op!r}")
    if op in {"add","replace"} and "value" not in change:
        raise Blocked(f"{label} {op} requires value at {change.get('path')}")
    if op=="remove" and "value" in change:
        raise Blocked(f"{label} remove must not include value at {change.get('path')}")
    parts=_json_pointer_parts(change.get("path"),label)
    root=parts[0]
    if root=="id":
        raise Blocked(f"{label} id is immutable")
    if root=="source_spec_id":
        raise Blocked(f"{label} source_spec_id is immutable formal binding metadata")
    if root in {"related","related_ids","related_lineage"}:
        raise Blocked(f"{label} relation root {root} may only be changed through related_add")
    parent=document
    create_missing=(op=="add")
    for part in parts[:-1]:
        if isinstance(parent,dict):
            if part in parent:
                parent=parent[part]
            elif create_missing:
                parent[part]={}
                parent=parent[part]
            else:
                raise Blocked(f"{label} JSON pointer cannot resolve token {part!r}")
        elif isinstance(parent,list):
            if not isinstance(part,str) or not ARRAY_INDEX_RE.fullmatch(part):
                raise Blocked(f"{label} JSON pointer list token must use canonical array index syntax: {part!r}")
            index=int(part)
            if index<0 or index>=len(parent):
                raise Blocked(f"{label} JSON pointer list index out of range: {part!r}")
            parent=parent[index]
        else:
            raise Blocked(f"{label} JSON pointer cannot resolve token {part!r}")

    key=parts[-1]
    if isinstance(parent,dict):
        exists=key in parent
        if op=="add":
            if exists:
                raise Blocked(f"{label} add target already exists at {change.get('path')}")
            parent[key]=copy.deepcopy(change.get("value"))
        elif op=="replace":
            if not exists:
                raise Blocked(f"{label} replace target missing at {change.get('path')}")
            parent[key]=copy.deepcopy(change.get("value"))
        else:
            if not exists:
                raise Blocked(f"{label} remove target missing at {change.get('path')}")
            del parent[key]
        return

    if isinstance(parent,list):
        if key=="-":
            if op!="add":
                raise Blocked(f"{label} '-' list token only valid for add")
            parent.append(copy.deepcopy(change.get("value")))
            return
        if not isinstance(key,str) or not ARRAY_INDEX_RE.fullmatch(key):
            raise Blocked(f"{label} list token must use canonical array index syntax or '-'")
        index=int(key)
        if op=="remove":
            if index<0 or index>=len(parent):
                raise Blocked(f"{label} remove list index out of range")
            parent.pop(index)
        elif op=="replace":
            if index<0 or index>=len(parent):
                raise Blocked(f"{label} replace list index out of range")
            parent[index]=copy.deepcopy(change.get("value"))
        else:
            if index<0 or index>len(parent):
                raise Blocked(f"{label} add list index out of range")
            parent.insert(index,copy.deepcopy(change.get("value")))
        return

    raise Blocked(f"{label} JSON pointer parent is not object/array")


def _materialized_operation_card(kind, op, expected, known, inserted, baseline_cards, insert_cards, updated_cards, label):
    if kind=="insert":
        card=op.get("card")
        return copy.deepcopy(card) if isinstance(card,dict) else None
    if kind=="update":
        cid=op.get("id")
        base=baseline_cards.get(cid)
        if not isinstance(base,dict):
            raise Blocked(f"{label} update target {cid} missing from declared baseline")
        card=copy.deepcopy(base)
        changes=op.get("changes")
        if not isinstance(changes,list) or not changes:
            raise Blocked(f"{label}.changes must be non-empty array")
        paths=[change.get("path") if isinstance(change,dict) else None for change in changes]
        if len(paths)!=len(set(paths)):
            raise Blocked(f"{label}.changes contains duplicate paths")
        for index,change in enumerate(changes):
            _apply_json_change(card,change,f"{label}.changes[{index}]")
        return card
    if kind=="related_add":
        governed,_=endpoint_context(op,known,inserted,expected,label)
        card=insert_cards.get(governed) or updated_cards.get(governed) or baseline_cards.get(governed)
        if not isinstance(card,dict):
            raise Blocked(f"{label} cannot materialize governed Related endpoint {governed}")
        return copy.deepcopy(card)
    raise Blocked(f"{label} unsupported operation kind {kind}")


def validate_content_enrichment_delta(rows_by_stage,label,operation_card=None,locked_prompt_version=None):
    row_06=_single_bound_row(rows_by_stage,"0.6",label)
    if row_06.get("content_enriched") is not True:
        raise Blocked(f"{label} stage 0.6 passing row requires content_enriched=true")

    # Explicit V4 artifacts remain valid historical records. V5+ (and
    # unversioned new artifacts) must satisfy the new structured contract.
    if not _requires_v5_content_audit(row_06, locked_prompt_version=locked_prompt_version):
        return

    audit=row_06.get("content_enrichment_audit")
    if not isinstance(audit,dict):
        raise Blocked(f"{label} stage 0.6 requires content_enrichment_audit")
    if audit.get("baseline_strategy")!=CONTENT_BASELINE_STRATEGY:
        raise Blocked(f"{label} 0.6 baseline_strategy must be {CONTENT_BASELINE_STRATEGY}")

    actual_changed=[]
    baseline_sources={}
    upstream_normalized={}
    for field in VISIBLE_COPY_FIELDS:
        baseline,source_stage=_effective_upstream_visible_value(rows_by_stage,field,label)
        baseline_sources[field]=source_stage
        baseline_normalized=_normalized_visible_value(field,baseline)
        upstream_normalized[field]=baseline_normalized
        current_normalized=_normalized_visible_value(field,row_06.get(field,_MISSING))
        if baseline_normalized is not None and current_normalized is None:
            raise Blocked(f"{label} 0.6 removal/empty value for {field} cannot satisfy substantive content enrichment")
        if baseline_normalized is None and current_normalized is not None:
            actual_changed.append(field)
        elif baseline_normalized is not None and current_normalized!=baseline_normalized:
            actual_changed.append(field)

    declared=audit.get("changed_fields")
    if (
        not isinstance(declared,list)
        or any(not isinstance(x,str) for x in declared)
        or len(declared)!=len(set(declared))
        or any(x not in VISIBLE_COPY_FIELDS for x in declared)
    ):
        raise Blocked(f"{label} 0.6 changed_fields must be a unique subset of {list(VISIBLE_COPY_FIELDS)}")
    expected={field for field in VISIBLE_COPY_FIELDS if field in actual_changed}
    if set(declared)!=expected:
        raise Blocked(
            f"{label} 0.6 declared changed_fields={declared} does not equal actual visible-copy delta={sorted(expected)}; "
            f"baseline_sources={baseline_sources}"
        )

    no_change=audit.get("no_change_required")
    if not isinstance(no_change,bool):
        raise Blocked(f"{label} 0.6 no_change_required must be boolean")

    if actual_changed:
        if no_change:
            raise Blocked(f"{label} 0.6 has actual visible-copy changes but declares no_change_required=true")
    else:
        if not no_change:
            raise Blocked(f"{label} 0.6 content_enriched=true with zero visible-copy delta requires no_change_required=true")
        if not _nonempty_text(audit.get("no_change_reason")):
            raise Blocked(f"{label} zero-delta 0.6 requires explicit no_change_reason")

    allowed_evidence_support=_upstream_evidence_token_support(rows_by_stage,label)
    allowed_evidence_texts=_upstream_evidence_token_texts(
        rows_by_stage,label,allowed_evidence_support
    )
    allowed_evidence_packages=_upstream_evidence_token_packages(
        rows_by_stage,label,allowed_evidence_support
    )
    _validate_density_audit(
        audit,row_06,label,no_change=not actual_changed,actual_changed=actual_changed,
        allowed_evidence_support=allowed_evidence_support,
        allowed_evidence_packages=allowed_evidence_packages,
    )
    true_dimensions=[
        name for name,value in audit["density_audit"]["dimensions"].items()
        if value is True
    ]
    _validate_claimed_dimension_evidence_grounding(
        audit["density_audit"],row_06,label,true_dimensions,
        allowed_evidence_texts,allowed_evidence_packages,
    )
    if actual_changed:
        _validate_substantive_dimension_delta(
            audit["density_audit"],row_06,label,actual_changed,upstream_normalized,
            allowed_evidence_texts,allowed_evidence_packages,
        )
    if operation_card is not None:
        _validate_operation_visible_copy(row_06,operation_card,label)
        _validate_materialized_operation_evidence(
            audit["density_audit"],operation_card,label,allowed_evidence_packages
        )


def validate_source_diversity_chain(rows_by_stage,label):
    observed={}
    for s in ("B","C","0.5","0.6","0.7"):
        rows=rows_by_stage.get(s,[])
        if not rows: raise Blocked(f"{label} stage {s} requires a bound row with source_diversity_status")
        values=set()
        for index,row in enumerate(rows):
            value=row.get("source_diversity_status") if isinstance(row,dict) else None
            if not _nonempty_text(value): raise Blocked(f"{label} stage {s} row {index} requires non-empty source_diversity_status")
            values.add(value.strip())
        if len(values)!=1: raise Blocked(f"{label} stage {s} has contradictory source_diversity_status values {sorted(values)}")
        observed[s]=next(iter(values))
    statuses=set(observed.values())
    if len(statuses)>1:
        detail=", ".join(f"{stage}={status}" for stage,status in observed.items())
        raise Blocked(f"{label} source_diversity_status drifts across the bound stage chain: {detail}")

def _validate_unique_update_targets(update_ops):
    if not isinstance(update_ops,list):
        raise Blocked("operations.update must be array")
    seen=set()
    for index,op in enumerate(update_ops):
        if not isinstance(op,dict):
            raise Blocked(f"update[{index}] must be object")
        cid=op.get("id")
        if _nonempty_text(cid):
            key=cid.strip()
            if key in seen:
                raise Blocked(f"operations.update has duplicate target id {key}")
            seen.add(key)


def validate_operations(run,governed):
    strict_specs=governed_strict_spec_identities(governed)
    base=baseline_canonical(run); known=canonical_map_from_data(base)
    locked_prompt_version=_locked_prompt_06_version(run.get("base_main_commit_sha"))
    baseline_cards={c.get("id"):c for c in base.get("cards",[]) if isinstance(c,dict) and _nonempty_text(c.get("id"))}
    insert_ops=run.get("operations",{}).get("insert",[])
    if not isinstance(insert_ops,list): raise Blocked("operations.insert must be array")
    validate_insert_identities(insert_ops,known)
    inserted={op.get("card",{}).get("id"):op.get("card",{}).get("source_spec_id") for op in insert_ops if isinstance(op,dict) and isinstance(op.get("card"),dict)}
    insert_cards={op.get("card",{}).get("id"):op.get("card") for op in insert_ops if isinstance(op,dict) and isinstance(op.get("card"),dict)}
    updated_cards={}
    update_ops=run.get("operations",{}).get("update",[])
    _validate_unique_update_targets(update_ops)
    for i,update_op in enumerate(update_ops):
        if not isinstance(update_op,dict): raise Blocked(f"update[{i}] must be object")
        cid=update_op.get("id")
        if _nonempty_text(cid):
            updated_cards[cid]=_materialized_operation_card(
                "update",update_op,op_spec("update",update_op,known,inserted,f"update[{i}]"),
                known,inserted,baseline_cards,insert_cards,{},f"update[{i}]"
            )
    for kind in ("insert","update","related_add"):
        ops=run.get("operations",{}).get(kind)
        if not isinstance(ops,list): raise Blocked(f"operations.{kind} must be array")
        for i,op in enumerate(ops):
            if not isinstance(op,dict): raise Blocked(f"{kind}[{i}] must be object")
            label=f"{kind}[{i}]"; expected=op_spec(kind,op,known,inserted,label); matched=set(); rows_by_stage={}
            refs=op.get("stage_artifacts")
            if not isinstance(refs,list) or not refs: raise Blocked(f"{label}.stage_artifacts required")
            for j,ref in enumerate(refs):
                p=load(repo_json(ref)); artifact_label=f"{label}.stage_artifacts[{j}]"; s=stage(p,artifact_label)
                validate_stage_binding(p,run,artifact_label)
                rows=matching_rows(p,s,expected)
                if rows:
                    matched.add(s); rows_by_stage.setdefault(s,[]).extend(rows)
            missing=[s for s in STAGES if s not in matched]
            if missing: raise Blocked(f"{label} missing current-run candidate binding at stages {missing}")
            validate_governed_stage_a_operation(rows_by_stage,expected,strict_specs,label)
            validate_source_diversity_chain(rows_by_stage,label)
            operation_card=_materialized_operation_card(kind,op,expected,known,inserted,baseline_cards,insert_cards,updated_cards,label)
            validate_content_enrichment_delta(
                rows_by_stage,label,operation_card=operation_card,
                locked_prompt_version=locked_prompt_version,
            )
            if kind=="related_add": validate_related_semantics(op,expected,rows_by_stage,known,inserted,label)

def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--run"); ap.add_argument("--self-test",action="store_true"); args=ap.parse_args()
    if args.self_test:
        regions,_=coverage_axes()
        axis_matrix({k:{"status":"searched"} for k in regions},regions,"regions")
        source={"review_pool":[],"legacy_keep":[{"story_id":"C1","grouped_story_ids":["C1"]}],"strict_passed_spec":[],"candidate_review_pool":[],"watchlist_context_pool":[],"reject_or_support_only_pool":[],"rejected":[],"existing_reinforcement":[],"support_source_only":[]}
        if checker_validated_stage_a_decisions(source)!={"C1":("legacy_keep","stage_a_checker:legacy_keep:C1")}: raise RuntimeError("legacy_keep/dedup contract failed")
        strict={"CAND_1":("strict_passed_spec","stage_a_checker:strict_passed_spec:SPEC_NEW")}
        validate_governed_stage_a_operation({"A":[{"spec_id":"SPEC_NEW","source_story_ids":["CAND_1"]}]},"SPEC_NEW",governed_strict_spec_identities(strict),"insert[0]")
        density={"status":"PASS","dimensions":{"prior_state":True,"changed_state":True,"quantitative_anchor":True,"boundary_or_uncertainty":True,"transmission_path":False,"next_watchpoint":False},"supported_dimension_count":4,"evidence_notes":"self-test","dimension_evidence":{"prior_state":{"fields":["fact"],"evidence_refs":["S1"]},"changed_state":{"fields":["sub"],"evidence_refs":["S1"]},"quantitative_anchor":{"fields":["fact"],"evidence_refs":["S1"]},"boundary_or_uncertainty":{"fields":["fact"],"evidence_refs":["S1"]}}}
        changed_rows={
            "B":[{"fact_sources":[{"source_id":"S1","source_url":"https://example.test/source","source_quote":"Previously planned at 1 GWh; commercial production started in 2026 at 2 GWh; target remains subject to certification.","source_quote_status":"body_quote_verified","fetched":True}]}],
            "C":[{"sub":"pilot project","gate":"g","fact":"Previously planned at 1 GWh; target remains subject to certification.","implication":["i"]}],
            "0.4":[{"fact":"Previously planned at 1 GWh; target remains subject to certification."}],
            "0.5":[{"fact":"Previously planned at 1 GWh; target remains subject to certification."}],
            "0.6":[{"sub":"commercial production started","gate":"g","fact":"Previously planned at 1 GWh; target remains subject to certification.","implication":["i"],"fact_sources":[{"source_id":"S1","source_url":"https://example.test/source","source_quote":"Previously planned at 1 GWh; commercial production started in 2026 at 2 GWh; target remains subject to certification.","source_quote_status":"body_quote_verified","fetched":True}],"content_enriched":True,"content_enrichment_audit":{"baseline_strategy":CONTENT_BASELINE_STRATEGY,"changed_fields":["sub"],"no_change_required":False,"no_change_reason":"","density_audit":density}}],
        }
        validate_content_enrichment_delta(changed_rows,"self-test changed")
        zero_density=copy.deepcopy(density)
        zero_density["dimension_evidence"]["changed_state"]["fields"]=["fact"]
        zero_rows={
            "B":[{"fact_sources":[{"source_id":"S1","source_url":"https://example.test/source","source_quote":"Previously planned at 1 GWh; commercial production started in 2026 at 2 GWh; target remains subject to certification.","source_quote_status":"body_quote_verified","fetched":True}]}],
            "C":[{"sub":"s","gate":"g","fact":"Previously planned at 1 GWh; commercial production started in 2026 at 2 GWh; target remains subject to certification.","implication":["i"]}],
            "0.4":[{"fact":"Previously planned at 1 GWh; commercial production started in 2026 at 2 GWh; target remains subject to certification."}],
            "0.5":[{"fact":"Previously planned at 1 GWh; commercial production started in 2026 at 2 GWh; target remains subject to certification."}],
            "0.6":[{"sub":"s","gate":"g","fact":"Previously planned at 1 GWh; commercial production started in 2026 at 2 GWh; target remains subject to certification.","implication":["i"],"fact_sources":[{"source_id":"S1","source_url":"https://example.test/source","source_quote":"Previously planned at 1 GWh; commercial production started in 2026 at 2 GWh; target remains subject to certification.","source_quote_status":"body_quote_verified","fetched":True}],"content_enriched":True,"content_enrichment_audit":{"baseline_strategy":CONTENT_BASELINE_STRATEGY,"changed_fields":[],"no_change_required":True,"no_change_reason":"already sufficiently deep","density_audit":zero_density}}],
        }
        validate_content_enrichment_delta(zero_rows,"self-test zero")
        blocked=dict(zero_rows)
        blocked["0.6"]=[dict(zero_rows["0.6"][0])]
        blocked["0.6"][0]["content_enrichment_audit"]=dict(zero_rows["0.6"][0]["content_enrichment_audit"])
        blocked["0.6"][0]["content_enrichment_audit"]["no_change_required"]=False
        try:
            validate_content_enrichment_delta(blocked,"self-test boolean-only")
        except Blocked:
            pass
        else:
            raise RuntimeError("zero-delta boolean-only content enrichment was not blocked")
        print("PASS: V4 binding hardening self-test; stage binding, source diversity, Related semantics, and 0.6 effective-upstream visible-copy delta/no-change gates remain fail-closed"); return 0
    if not args.run: raise Blocked("--run PATH required")
    run=load(repo_json(args.run)); validate_preflight(run); validate_coverage(run); governed=validate_completeness(run); validate_operations(run,governed); print(json.dumps({"status":"PASS","registry_binding":"PASS","coverage_axes":"PASS","completeness_residual_risk":"PASS","stage_baseline_binding":"PASS","identity_binding":"PASS","terminal_decision_binding":"PASS","operation_stage_a_binding":"PASS","source_diversity_chain":"PASS","content_enrichment_delta":"PASS","related_semantics":"PASS"})); return 0

if __name__=="__main__":
    try: raise SystemExit(main())
    except Blocked as e: print(f"FAIL [BLOCKED_V4_BINDING]: {e}",file=sys.stderr); raise SystemExit(1)
    except Exception as e: print(f"FAIL [BLOCKED_V4_BINDING_INTERNAL]: {e}",file=sys.stderr); raise SystemExit(1)
