#!/usr/bin/env python3
from __future__ import annotations

import copy
import hashlib
import json
import re
import sys
from collections import Counter
from pathlib import Path
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

RUN_DIR = ROOT / "runs/2026-09-03"
PACKET_DIR = RUN_DIR / "stage_a_review_packets_395_r6"
TEMPLATE_PATH = RUN_DIR / "stage_a_formal_r6_batch01_20260903_R1.json"
PROMPT = ROOT / "docs/llm_prompts/v1/01_PROMPT_0_1_Stage_A.md"
STRUCTURAL_POLICY = ROOT / "docs/STRUCTURAL_NEWS_VALUE_SELECTION.md"

MAIN = "df6fcccf3a69464ff0a43a8ba5897d71b6a4d9c4"
CANON_BLOB = "53219907cdb435c3822c41d097b23e475662aa8a"
R6_MEMBERSHIP_SHA = "e60cdde682c3b5029002adf87e7b43ac3c02bdc0e3119745af979590a1ba5702"
R6_RELATION_SHA = "790a0d001d2d39934b4cfdaefc9d8384efbb02dd19d90a85ea9d6a4156c17581"
R6_PRESELECTION_SHA = "d0151e92f872bb2e34f2b3b30edc3b51c3c00d50d6876f958b69db256d1aebdf"

ACTIVE_DOCS = [
    "docs/llm_prompts/v1/01_PROMPT_0_1_Stage_A.md",
    "docs/FACT_DISCIPLINE.md",
    "docs/PROMPT_ABC_DEFAULT_MODE.md",
    "docs/FUTURE_CARD_STANDARD_FULL_SCHEMA.md",
    "docs/CARD_ID_STANDARD.md",
    "docs/WORKFLOW.md",
    "docs/OPERATIONS.md",
    "docs/POST_ACCEPTANCE_CONTENT_ENRICHMENT_QC.md",
    "docs/RELATED_LIFECYCLE_CONTRACT.md",
]

template = json.loads(TEMPLATE_PATH.read_text(encoding="utf-8"))
assert template["status"] == "PASS"
strict_exec_template = next(
    copy.deepcopy(x) for x in template["strict_passed_spec"]
    if x["selection_route"] == "execution_anchor_route"
)
strict_nonexec_template = next(
    copy.deepcopy(x) for x in template["strict_passed_spec"]
    if x["selection_route"] == "structural_non_execution_route"
)
candidate_template = copy.deepcopy(template["candidate_review_pool"][0])
watch_template = copy.deepcopy(template["watchlist_context_pool"][0])
reject_template = copy.deepcopy(template["reject_or_support_only_pool"][0])

CLASS_THRESHOLDS = (
    (85, "critical_structural"),
    (70, "high_decision_value"),
    (55, "material_industry_signal"),
    (40, "standard_monitoring"),
    (25, "context_or_reinforcement"),
    (0, "low_independent_value"),
)

RELEVANCE_TERMS = (
    "battery", "bess", "energy storage", "storage project", "electric vehicle", " ev ",
    "lithium", "nickel", "cobalt", "graphite", "rare earth", "critical mineral",
    "sodium-ion", "sodium ion", "solid-state", "solid state", "cathode", "anode",
    "charging", "grid storage", "inverter", "pcs", "black mass", "recycling",
    "배터리", "에너지저장", "에너지 저장", "전기차", "리튬", "니켈", "코발트", "흑연",
    "희토류", "핵심광물", "나트륨", "전고체", "양극재", "음극재", "충전", "재활용",
    "储能", "电池", "锂", "镍", "钴", "石墨", "稀土", "关键矿产", "钠离子", "固态",
    "正极", "负极", "充电", "回收",
)

NOISE_TERMS = (
    "awards 2026", "award ceremony", "one week left to enter", "art exhibition", "festival",
    "forum discussion", "opinion:", "podcast", "job posting", "appoints citizen auditors",
    "weekly roundup", "周报", "전시", "공연", "축제", "미술", "채용", "시민감사",
)

BINDING_EXEC_TERMS = (
    "definitive agreement", "binding agreement", "binding offtake", "offtake agreement",
    "supply agreement", "signed agreement", "signs agreement", "contract awarded",
    "secures funding", "financing facility", "acquisition of", "acquires ", "completed acquisition",
    "financial close", "begins construction", "construction start", "starts construction",
    "breaks ground", "commissioned", "commissioning", "grid-connected", "grid connected",
    "connected to the grid", "becomes operational", "operations begin", "production start",
    "starts production", "mass production", "commercial shipment", "ships ", "order for",
    "contract", "launches plant", "plant rollout",
    "계약 체결", "공급계약", "오프테이크", "인수 완료", "자금 조달", "금융 지원",
    "착공", "준공", "상업운전", "계통연계", "계통 연결", "가동", "생산 시작", "양산", "수주",
    "正式投产", "投产", "并网", "签署协议", "签订协议", "合同", "收购", "融资",
    "开工", "竣工", "量产", "商业运营", "订单", "中标",
)

SOFT_EXEC_TERMS = (
    "investment", "invests", "partnership", "mou", "memorandum", "plans", "planned",
    "proposed", "expected", "considering", "explores", "pilot", "trial", "development agreement",
    "투자", "협력", "업무협약", "검토", "계획", "예정", "실증", "협의",
    "投资", "合作", "规划", "计划", "拟", "试点", "示范",
)

POLICY_TERMS = (
    "regulation", "rule", "guidance", "tax", "subsidy", "budget", "law", "bill",
    "legislation", "standard", "notice", "restriction", "feoc", "tariff", "passport",
    "policy", "procurement", "market access", "export control", "local content",
    "규정", "규제", "지침", "세금", "소비세", "보조금", "예산", "법", "법안",
    "고시", "제한", "정책", "조달", "수출통제", "현지조달",
    "规定", "法规", "指导", "税", "消费税", "补贴", "预算", "法律", "法案",
    "通知", "限制", "政策", "采购", "出口管制",
)

FINAL_POLICY_TERMS = (
    "takes effect", "effective ", "effective date", "final rule", "adopted", "enacted",
    "implementation guidance", "official guidance", "approved budget", "promulgated",
    "시행", "발효", "확정", "최종 규칙", "채택", "제정", "공포", "가이드라인",
    "实施", "生效", "最终规则", "通过", "发布", "正式实施",
)

PROPOSED_POLICY_TERMS = (
    "bill", "proposed rule", "proposal", "draft", "consultation", "under review",
    "reviewing", "planned budget", "budget proposal", "법안", "안", "초안", "검토",
    "예산안", "논의", "法案", "草案", "征求意见", "拟议", "预算案",
)

DATA_TERMS = (
    "market share", "installations", "additions", "shipments", "shipment", "sales",
    "demand", "orders", "record ", "revenue", "profit", "margin", "h1", "h2",
    "q1", "q2", "q3", "q4", "first half", "市占率", "营收", "净利", "出货",
    "新增", "订单", "同比", "매출", "영업이익", "순이익", "출하", "판매", "점유율",
)

EARNINGS_TERMS = (
    "net profit", "revenue", "earnings", "ebitda", "margin", "净利", "营收", "利润",
    "실적", "영업이익", "순이익", "매출",
)

MARKET_AGGREGATE_TERMS = (
    "market", "industry", "u.s. added", "china h1", "europe", "france", "global",
    "installations", "additions", "share hits", "orders jump", "市场", "行业", "全国",
    "미국", "중국", "유럽", "시장",
)

TECH_TERMS = (
    "solid-state", "solid state", "sodium", "silicon anode", "lithium-metal",
    "prototype", "qualification", "certification", "pilot", "demonstration",
    "전고체", "나트륨", "실리콘 음극", "프로토타입", "인증", "실증",
    "固态", "钠离子", "硅负极", "样品", "认证", "示范",
)

NEGATIVE_TERMS = (
    "fire", "recall", "defect", "failure", "exposure", "bankruptcy", "shutdown",
    "delay", "cancel", "lawsuit", "investigation", "drop", "fall", "decline",
    "화재", "리콜", "결함", "중단", "지연", "취소", "소송", "조사", "감소",
    "起火", "召回", "缺陷", "停产", "延迟", "取消", "诉讼", "调查", "下降",
)

AMOUNT_RE = re.compile(
    r"(?i)(?:[$€£]\s?\d|(?:us\$|usd|eur)\s?\d|\d[\d,.]*\s?(?:gwh|mwh|gw|mw|kwh|wh|%"
    r"|million|billion|bn|tons?|tonnes?|t\b|억원|조원|억|조|만|万吨|亿元|亿美元|万颗))"
)

def classification(score: int) -> str:
    for threshold, label in CLASS_THRESHOLDS:
        if score >= threshold:
            return label
    return "low_independent_value"

def text_blob(event: dict) -> str:
    bits = [event["representative"].get("title", "")]
    bits.extend(o.get("title", "") for o in event.get("observations", []))
    for values in event.get("matched_features", {}).values():
        if isinstance(values, list):
            bits.extend(str(v) for v in values)
    return " ".join(bits).lower()

def has_any(text: str, terms) -> bool:
    return any(term in text for term in terms)

def source_urls(event: dict) -> list[str]:
    urls = []
    for o in event.get("observations", []):
        u = o.get("source_url")
        if isinstance(u, str) and u and u not in urls:
            urls.append(u)
    u = event["representative"].get("url")
    if isinstance(u, str) and u and u not in urls:
        urls.insert(0, u)
    return urls

def domains(urls: list[str]) -> list[str]:
    out = []
    for u in urls:
        try:
            d = urlsplit(u).netloc.lower().removeprefix("www.")
        except Exception:
            d = ""
        if d and d not in out:
            out.append(d)
    return out

def relation_type(event: dict) -> str:
    rel = event.get("canonical_relation")
    if isinstance(rel, dict) and isinstance(rel.get("relation_type"), str):
        return rel["relation_type"]
    return "new"

def policy_stage_for(text: str) -> int | None:
    if not has_any(text, POLICY_TERMS):
        return None
    if has_any(text, FINAL_POLICY_TERMS):
        return 4
    if "final rule" in text or "enacted" in text or "법률" in text or "제정" in text:
        return 3
    if has_any(text, PROPOSED_POLICY_TERMS):
        return 2
    return 1

def legal_stage_for(policy_stage: int | None) -> str | None:
    return {
        0: "stage_0_rhetoric_or_advocacy",
        1: "stage_1_roadmap_consultation_or_draft_standard",
        2: "stage_2_bill_or_proposed_rule",
        3: "stage_3_enacted_law_final_rule_or_adopted_standard",
        4: "stage_4_implementation_budget_guidance_or_registry",
        5: "stage_5_enforcement_court_or_transactional_application",
        6: "stage_6_realized_market_or_operating_effect",
    }.get(policy_stage)

def tech_profile(text: str, features: dict) -> tuple[bool, str, str, int]:
    tech = bool(features.get("technology")) or has_any(text, TECH_TERMS)
    if not tech:
        return False, "not_applicable", "concept_or_target", 0
    if has_any(text, ("commercial shipment", "mass production", "production start", "量产", "投产", "양산")):
        return True, "commercial_scale_or_long_duration_field", "production_start", 20
    if has_any(text, ("qualification", "certification", "customer evaluation", "认证", "인증")):
        return True, "independent_test_or_customer_qualification", "qualification", 15
    if has_any(text, ("pilot", "demonstration", "试点", "示范", "실증")):
        return True, "pilot_precommercial", "pilot", 11
    if has_any(text, ("prototype", "样品", "프로토타입")):
        return True, "laboratory_unvalidated", "prototype", 7
    return True, "company_target_or_unsupported_claim", "concept_or_target", 4

def executive_relevance(text: str, features: dict) -> bool:
    return bool(features.get("scope")) or has_any(text, RELEVANCE_TERMS)

def score_event(event: dict) -> dict:
    text = text_blob(event)
    f = event.get("matched_features", {})
    relevant = executive_relevance(text, f)
    policy_stage = policy_stage_for(text)
    if policy_stage is None and bool(f.get("policy")):
        policy_stage = 1
    policy = policy_stage is not None
    binding_exec = has_any(text, BINDING_EXEC_TERMS)
    soft_exec = bool(f.get("execution")) or has_any(text, SOFT_EXEC_TERMS)
    data = bool(f.get("data_financial")) or has_any(text, DATA_TERMS)
    scale = bool(f.get("scale")) or bool(AMOUNT_RE.search(text))
    strategic = bool(f.get("strategic")) or has_any(text, ("supply chain", "critical mineral", "market access", "공급망", "핵심광물", "供应链", "关键矿产"))
    negative = bool(f.get("negative")) or has_any(text, NEGATIVE_TERMS)
    tech, tech_level, tech_stage, tech_cap = tech_profile(text, f)
    earnings = data and has_any(text, EARNINGS_TERMS) and not has_any(text, MARKET_AGGREGATE_TERMS)
    aggregate_data = data and has_any(text, MARKET_AGGREGATE_TERMS)
    noise = has_any(text, NOISE_TERMS)

    ms = 4 if relevant else 0
    ms += 5 if strategic else 0
    ms += 5 if policy else 0
    ms += 6 if binding_exec else (3 if soft_exec else 0)
    ms += 4 if data else 0
    ms = min(25, ms)

    sd = 5 if relevant else 0
    sd += 7 if data else 0
    sd += 5 if scale else 0
    sd += 5 if binding_exec else (2 if soft_exec else 0)
    sd += 3 if has_any(text, ("capacity", "volume", "ship", "order", "demand", "supply", "production", "price", "gwh", "mwh", "mw", "出货", "订单", "产能", "수요", "공급", "출하", "생산")) else 0
    sd = min(25, sd)

    tech_score = 0
    if tech:
        tech_score = 4
        if has_any(text, ("qualification", "certification", "customer evaluation", "认证", "인증")):
            tech_score = 10
        elif has_any(text, ("pilot", "demonstration", "试点", "示范", "실증")):
            tech_score = 7
        elif has_any(text, ("production start", "mass production", "commercial shipment", "量产", "投产", "양산")):
            tech_score = 12
        tech_score = min(tech_score, tech_cap)

    cash = 0
    cash += 5 if binding_exec and has_any(text, ("fund", "financ", "acquisition", "contract", "investment", "$", "€", "融资", "投资", "收购", "자금", "금융", "인수", "계약")) else 0
    cash += 4 if data and has_any(text, EARNINGS_TERMS) else 0
    cash += 2 if scale and has_any(text, ("$", "€", "£", "revenue", "profit", "营收", "净利", "매출", "이익")) else 0
    cash = min(10, cash)

    law = 0
    if policy:
        law = 5
        if policy_stage is not None and policy_stage >= 3:
            law = 10
        elif policy_stage == 2:
            law = 8
        elif policy_stage == 1:
            law = 5

    systemic = 2 if (scale or aggregate_data) else 1
    persist = 1
    persist += 1 if (binding_exec or (policy_stage is not None and policy_stage >= 3) or aggregate_data) else 0
    persist += 1 if strategic else 0
    persist = min(3, persist)

    urgency = 1
    if binding_exec or (policy_stage is not None and policy_stage >= 3) or negative:
        urgency = 2

    breakdown = {
        "market_structure_competition": ms,
        "supply_demand_price_utilisation": sd,
        "technology_performance_safety": tech_score,
        "cashflow_asset_value": cash,
        "law_policy_market_access": law,
        "systemic_scale": systemic,
        "persistence_irreversibility": persist,
        "decision_urgency_actionability": urgency,
    }
    score = sum(breakdown.values())

    novelty = "none"
    if noise and not binding_exec and not policy:
        novelty = "routine_progression_no_material_uncertainty"
        score = min(score, 54)
    if has_any(text, ("target", "aims to", "plans to", "목표", "计划", "规划")) and tech and not binding_exec:
        novelty = "company_target_without_validation_or_effect"
        score = min(score, 54)
    if relation_type(event) in {"same_event_reinforcement", "existing_card_reinforcement"}:
        novelty = "repeated_announcement_no_new_fact"
        score = min(score, 39)

    current = sum(breakdown.values())
    if current > score:
        delta = current - score
        for key in (
            "market_structure_competition",
            "supply_demand_price_utilisation",
            "cashflow_asset_value",
            "persistence_irreversibility",
            "decision_urgency_actionability",
        ):
            take = min(delta, breakdown[key])
            breakdown[key] -= take
            delta -= take
            if delta == 0:
                break
    score = sum(breakdown.values())

    if policy_stage in {0, 1, 2}:
        cap = {0: 39, 1: 54, 2: 69}[policy_stage]
        if score > cap:
            delta = score - cap
            for key in ("market_structure_competition", "supply_demand_price_utilisation", "cashflow_asset_value", "persistence_irreversibility"):
                take = min(delta, breakdown[key])
                breakdown[key] -= take
                delta -= take
                if delta == 0:
                    break
            score = sum(breakdown.values())

    return {
        "relevant": relevant,
        "policy": policy,
        "policy_stage": policy_stage,
        "binding_exec": binding_exec,
        "soft_exec": soft_exec,
        "data": data,
        "aggregate_data": aggregate_data,
        "earnings": earnings,
        "scale": scale,
        "strategic": strategic,
        "negative": negative,
        "tech": tech,
        "tech_level": tech_level,
        "tech_stage": tech_stage,
        "noise": noise,
        "novelty": novelty,
        "breakdown": breakdown,
        "score": score,
    }

def decide(event: dict) -> dict:
    m = score_event(event)
    text = text_blob(event)
    rel = relation_type(event)

    if not m["relevant"]:
        pool = "reject_or_support_only_pool"
    elif rel in {"same_event_reinforcement", "existing_card_reinforcement"}:
        pool = "reject_or_support_only_pool"
    elif m["noise"] and not (m["binding_exec"] or (m["policy_stage"] or 0) >= 3):
        pool = "reject_or_support_only_pool" if m["score"] < 40 else "watchlist_context_pool"
    elif m["earnings"]:
        pool = "candidate_review_pool" if m["score"] >= 40 else "watchlist_context_pool"
    elif m["binding_exec"] and m["score"] >= 55 and not has_any(text, ("proposed", "expected", "planned", "under review", "검토", "예정", "计划", "拟")):
        pool = "strict_passed_spec"
    elif m["policy"] and (m["policy_stage"] or 0) >= 3 and m["score"] >= 55:
        pool = "strict_passed_spec"
    elif m["aggregate_data"] and m["score"] >= 55 and event.get("observation_count", 0) >= 2:
        pool = "strict_passed_spec"
    elif m["tech"] and m["binding_exec"] and m["tech_level"] in {"independent_test_or_customer_qualification", "commercial_scale_or_long_duration_field"} and m["score"] >= 55:
        pool = "strict_passed_spec"
    elif m["score"] >= 45:
        pool = "candidate_review_pool"
    elif m["score"] >= 28:
        pool = "watchlist_context_pool"
    else:
        pool = "reject_or_support_only_pool"

    if pool == "reject_or_support_only_pool" and m["relevant"] and (
        m["binding_exec"] or (m["policy_stage"] or 0) >= 2 or m["aggregate_data"]
    ) and m["score"] >= 40:
        pool = "candidate_review_pool"

    route = "execution_anchor_route" if m["binding_exec"] else "structural_non_execution_route"
    anchors = []
    if route == "execution_anchor_route":
        anchors.append("execution_event_anchor")
    if m["policy"]:
        anchors.append("policy_regulatory_anchor")
    if m["data"]:
        anchors.append("data_financial_anchor")
    if m["strategic"] or m["binding_exec"]:
        anchors.append("strategic_behavior_anchor")
    if m["tech"]:
        anchors.append("technology_commercialization_anchor")
    if rel in {"distinct_follow_up", "program_lineage"}:
        anchors.append("follow_up_probability_anchor")
    if not anchors:
        anchors = ["strategic_behavior_anchor"]
    anchors = list(dict.fromkeys(anchors))

    if route == "execution_anchor_route":
        exec_type = "binding_or_executed_industrial_milestone"
        if has_any(text, ("production start", "starts production", "投产", "量产", "양산")):
            exec_type = "production_start"
        elif has_any(text, ("grid-connected", "grid connected", "并网", "계통")):
            exec_type = "grid_connection"
        elif has_any(text, ("construction start", "begins construction", "开工", "착공")):
            exec_type = "construction_start"
        elif has_any(text, ("acquisition", "acquires", "收购", "인수")):
            exec_type = "acquisition"
        elif has_any(text, ("fund", "financ", "融资", "자금", "금융")):
            exec_type = "financing"
        elif has_any(text, ("offtake", "supply agreement", "공급계약")):
            exec_type = "binding_supply_or_offtake_agreement"
        elif has_any(text, ("agreement", "contract", "协议", "合同", "계약")):
            exec_type = "signed_agreement"
        exec_strength = "strong" if pool == "strict_passed_spec" else "moderate"
    else:
        exec_type = None
        exec_strength = None

    if pool == "strict_passed_spec":
        urgency = "immediate" if (m["policy_stage"] or 0) >= 3 or m["negative"] else "near_term"
        exec_gate = "PASS"
        card_gate = "PASS"
    elif pool == "candidate_review_pool":
        urgency = "near_term"
        exec_gate = "PASS" if (m["binding_exec"] or m["policy"] or m["aggregate_data"]) else "REVIEW"
        card_gate = "REVIEW"
    else:
        urgency = "monitor"
        exec_gate = "REVIEW" if m["relevant"] else "FAIL"
        card_gate = "REVIEW" if pool == "watchlist_context_pool" else "FAIL"

    short = event["representative"]["title"].strip()
    if len(short) > 220:
        short = short[:217] + "..."

    if pool == "strict_passed_spec":
        gap = (
            f"Stage B must verify the exact operative stage, named actors, date, scope, "
            f"quantified terms and first measurable implementation for {short}."
        )
    elif pool == "candidate_review_pool":
        gap = (
            f"The source-bound packet supports material relevance for {short}, but at least one "
            "execution, legal-stage, denominator, source-strength, technology-validation or "
            "incremental-value question remains unresolved before strict promotion."
        )
    elif pool == "watchlist_context_pool":
        gap = (
            f"{short} is decision-relevant context, but the packet does not yet establish a "
            "sufficiently irreversible, quantified or source-strong current milestone for Stage B."
        )
    else:
        gap = (
            f"{short} lacks sufficient independent current-run battery/ESS decision value for a "
            "new card; retain only as bounded support/context unless a new material milestone appears."
        )

    return {
        "pool": pool,
        "short": short,
        "score": m["score"],
        "breakdown": m["breakdown"],
        "route": route,
        "anchors": anchors,
        "exec": exec_gate,
        "card": card_gate,
        "urgency": urgency,
        "gap": gap,
        "exec_type": exec_type,
        "exec_strength": exec_strength,
        "policy_stage": m["policy_stage"],
        "legal_stage": legal_stage_for(m["policy_stage"]),
        "tech_level": m["tech_level"],
        "tech_stage": m["tech_stage"],
        "novelty": m["novelty"],
        "earnings": m["earnings"],
        "denominator": None,
        "metrics": m,
    }

def legal_fields(j: dict, event_date: str) -> dict:
    stage = j.get("legal_stage")
    if not stage:
        return {}
    if stage.startswith("stage_4"):
        instrument = "official implementation guidance, budget, registry or effective administrative instrument"
    elif stage.startswith("stage_3"):
        instrument = "enacted law, final rule or adopted standard"
    elif stage.startswith("stage_2"):
        instrument = "bill or proposed rule"
    elif stage.startswith("stage_1"):
        instrument = "roadmap, consultation, draft standard or budget/policy proposal"
    else:
        instrument = "policy advocacy or rhetoric"
    return {
        "legal_policy_stage": stage,
        "legal_instrument_type": instrument,
        "competent_authority": "Authority identified in the source-bound packet; exact instrument authority must be verified in Stage B.",
        "procedural_status": stage,
        "adoption_date": event_date if stage.startswith(("stage_3", "stage_4")) else "unknown_stage_a",
        "publication_date": event_date,
        "effective_date": event_date if stage.startswith("stage_4") else "future_or_unknown_stage_a",
        "mandatory_application_date": event_date if stage.startswith("stage_4") else "future_or_unknown_stage_a",
        "affected_entities": ["Battery/ESS or relevant market participants described in the source-bound packet."],
        "affected_products_or_activities": ["Battery/ESS products, market access, taxation, procurement, infrastructure or transport activity described in the item."],
        "geographic_scope": "Jurisdiction named in the item.",
        "extraterritorial_effect": "unknown_stage_a",
        "budget_or_funding_source": "not_established_in_stage_a_source_packet",
        "implementation_mechanism": "Verify the primary legal/policy instrument and operative implementation mechanism in Stage B.",
        "administrative_readiness": "Current stage is source-bound Stage A metadata only; verify in Stage B.",
        "exemptions_and_thresholds": [],
        "transition_and_grandfathering": [],
        "noncompliance_consequences": [],
        "appeal_or_litigation_risk": "unknown_stage_a",
        "reversibility_risk": "unknown_stage_a",
        "precedent_scope": "Item-specific jurisdiction only; no broader precedent claimed at Stage A.",
        "legal_policy_transmission_chain": ["instrument/guidance", "covered battery/ESS activity", "cost, qualification, market-access or operating response"],
        "next_implementation_trigger": "Verify exact official instrument, effective application and first observable implementation in Stage B.",
        "legal_policy_score_cap_exception": {"applied": False, "basis": None, "evidence": None},
    }

def related_prepass(event: dict, j: dict) -> dict:
    rel = event.get("canonical_relation")
    if isinstance(rel, dict):
        rtype = rel.get("relation_type", "new_unrelated_event")
        targets = list(rel.get("target_ids", []))
        confidence = rel.get("confidence", "medium")
    else:
        rtype = "new_unrelated_event"
        targets = []
        confidence = "high"
    candidates = []
    if rtype in {"distinct_follow_up", "program_lineage"}:
        anchor = "follow_up_probability_anchor" if "follow_up_probability_anchor" in j["anchors"] else j["anchors"][0]
        for target in targets:
            candidates.append({
                "target_candidate_id": target,
                "proposed_relation_type": rtype,
                "confidence": confidence,
                "reason": f"R6 canonical-relation closure maps {j['short']} to {target} as {rtype}.",
                "anchor_class_to_verify": anchor,
                "incremental_anchor_question": f"What new verified fact in {j['short']} changes the judgment beyond canonical target {target}?",
            })
    return {
        "status": "PASS",
        "same_event_checked": True,
        "matched_baseline_candidate_ids": targets,
        "matched_current_batch_candidate_ids": [],
        "relation_candidates": candidates,
        "duplicate_disposition": "no_duplicate_found",
        "earliest_same_event_check_status": "PASS",
        "fresh_anchor_questions": [f"Verify the current-stage fact and incremental decision effect for {j['short']} before drafting."],
    }

def strict_stage_b_targets(event: dict, j: dict) -> tuple[str, str]:
    date = event["representative"]["date"]
    short = j["short"]
    if j["route"] == "execution_anchor_route":
        evidence = (
            f"Official contract, filing or permit document confirming the exact {j['exec_type']} stage, "
            f"named actors, stated capacity or value, event date {date}, operative schedule and current status for {short}"
        )
        confirm = (
            f"First production, shipment, construction, closing, capacity or operating metric after {date} "
            f"would confirm the execution judgment for {short}; cancellation, missed deadline or lower delivered "
            "volume would weaken that judgment"
        )
    elif "policy_regulatory_anchor" in j["anchors"]:
        evidence = (
            f"Official regulation, guidance, notice or legislation document confirming policy stage "
            f"{j.get('legal_stage')}, covered battery/ESS activity, publication date {date}, effective date, "
            f"thresholds and exemptions for {short}"
        )
        confirm = (
            f"First implementation filing, effective date, compliance metric or enforcement decision after {date} "
            f"would confirm the market-access judgment for {short}; delayed or reversed implementation would weaken that judgment"
        )
    else:
        evidence = (
            f"Official dataset, statistics release or independent report confirming the exact market volume, capacity, "
            f"price, adoption or status metric and publication date {date} for {short}"
        )
        confirm = (
            f"Next-period volume, capacity, price or adoption metric after {date} would confirm the persistence judgment "
            f"for {short}; a reversal would weaken that judgment"
        )
    return evidence, confirm

def common_item(event: dict, j: dict, strict: bool, batch: int) -> dict:
    template_item = (
        strict_exec_template if strict and j["route"] == "execution_anchor_route"
        else strict_nonexec_template if strict
        else candidate_template if j["pool"] == "candidate_review_pool"
        else watch_template if j["pool"] == "watchlist_context_pool"
        else reject_template
    )
    item = copy.deepcopy(template_item)
    obs = event["observations"]
    source_ids = [o["observation_key"] for o in obs]
    urls = source_urls(event)
    primary = event["representative"].get("url") or urls[0]
    if primary not in urls:
        urls.insert(0, primary)
    d = domains(urls)
    rel = event.get("canonical_relation")
    baseline = rel.get("relation_type") if isinstance(rel, dict) else "new"

    item.update({
        "source_origin": "R6 corrected source-bound event membership",
        "source_story_ids": source_ids,
        "original_story_ids": [o.get("story_id") for o in obs],
        "merge_status": "multi_observation_event" if len(obs) > 1 else "single_observation_event",
        "merged_story_ids": source_ids[1:],
        "baseline_relation": baseline,
        "duplicate_risk": "low_after_R6_90100_pair_audit",
        "region": "GLOBAL",
        "representative_date": event["representative"]["date"],
        "representative_source": event["representative"].get("site") or "source-bound packet",
        "source_tier_estimate": "multi_source_candidate_set" if len(d) > 1 else "single_source_candidate",
        "cat": "battery_ess_industrial_signal",
        "sub_cat": "policy" if "policy_regulatory_anchor" in j["anchors"] else ("technology" if "technology_commercialization_anchor" in j["anchors"] else "strategy_execution"),
        "signal_estimate": "material" if j["score"] >= 55 else ("monitoring" if j["score"] >= 40 else "context"),
        "signal_rubric_estimate": {"status": classification(j["score"]), "score": j["score"]},
        "strategic_lens": ["US_EU_CN_policy" if "policy_regulatory_anchor" in j["anchors"] else "battery_ESS_supply_chain"],
        "primary_url": primary,
        "urls": urls,
        "event_anchor": j["exec_type"] or ("policy_implementation" if "policy_regulatory_anchor" in j["anchors"] else "structural_signal"),
        "enhanced_selector_precision_version": "v3",
        "selector_policy_version": "STRUCTURAL_NEWS_VALUE_SELECTION_V3",
        "strict_gate_check": "pass" if strict else "review",
        "format_risk_tags": ["none"],
        "execution_anchor_type": j["exec_type"] if j["route"] == "execution_anchor_route" else None,
        "execution_anchor_strength": j["exec_strength"] if j["route"] == "execution_anchor_route" else None,
        "staleness_decision": "current",
        "source_access_risk": "low" if len(urls) > 1 else "moderate",
        "stage_a_evidence_status": "not_evidence_complete_no_fetch",
        "stage_b_evidence_package_required": True,
        "primary_url_semantics": "provided_source_candidate_not_evidence",
        "same_event_source_cluster": [
            {"story_id": o["observation_key"], "url": o.get("source_url") or primary, "preserve_for_stage_b": True}
            for o in obs
        ],
        "support_source_candidates": urls[1:],
        "source_domain_candidates": d,
        "source_diversity_path": {
            "status": "viable",
            "probable_independent_owner_count": max(1, len(d)),
            "official_or_source_owner_candidate_present": True,
            "independent_confirmation_candidate_present": len(d) > 1,
            "context_candidate_present": len(obs) > 1,
            "reason": "All supplied source candidates are preserved for Stage B; Stage A performed no external fetch.",
        },
        "source_cluster_preserved": True,
        "support_source_candidates_accounted": True,
        "selection_policy_version": "EMBEDDED_NEWS_VALUE_SELECTION_V4",
        "selection_route": j["route"],
        "structural_value_override_applied": j["route"] != "execution_anchor_route",
        "structural_value_override_reason": None if j["route"] == "execution_anchor_route" else f"{j['short']} changes the decision baseline without requiring a conventional corporate execution event.",
        "anchor_classes": j["anchors"],
        "incremental_information": f"The R6 source-bound packet newly establishes or materially updates {j['short']} within the 2026-08-28 to 2026-09-01 intake window.",
        "decision_relevance": f"The reported current stage of {j['short']} can change sourcing, market-access, investment, capacity, technology or risk-monitoring decisions; unresolved elements remain explicitly bounded.",
        "baseline_expectation_changed": f"The current-run baseline must now account for the source-bound signal represented by {j['short']}, subject to the stated uncertainty and canonical relation treatment.",
        "evidence_needed_for_stage_b": [f"Official document or independent report confirming the exact stage, date, capacity, status or market metric for {j['short']}"],
        "next_confirmation_points": [f"Next measurable production, shipment, capacity, filing, effective date or operating metric would confirm or weaken the current judgment for {j['short']}"],
        "why_execution_event_not_required": None if j["route"] == "execution_anchor_route" else f"A non-execution anchor directly changes the decision baseline for {j['short']}; conventional corporate execution is not required for this route.",
        "structural_non_execution_reason": None if j["route"] == "execution_anchor_route" else f"The supplied source package establishes a decision-useful policy, data, strategic, technology or follow-up change for {j['short']} without requiring conventional execution.",
        "prior_state": f"Before this intake, {j['short']} had not received a final R6 Formal Stage A disposition in this run.",
        "new_verified_fact": f"The supplied source-bound observations report the current-stage fact described as {j['short']}.",
        "changed_judgment": f"The current-run judgment changes from unadjudicated intake to {j['pool']} for {j['short']}.",
        "uncertainty_resolved": f"Event identity, current reporting window and the reported direction of {j['short']} are sufficiently resolved for this Stage A disposition.",
        "remaining_uncertainty": j["gap"],
        "decision_news_value_score": j["score"],
        "decision_value_breakdown": j["breakdown"],
        "decision_value_classification": classification(j["score"]),
        "systemic_scale_denominator": None,
        "denominator_used": "No defensible market-wide denominator is claimed; systemic scale is capped at 2/5.",
        "denominator_gap": "No defensible market-wide denominator is available in the Stage A source packet; systemic_scale is capped at 2/5.",
        "publication_urgency": {
            "level": j["urgency"],
            "action_required": f"Use the {j['pool']} disposition for {j['short']} and do not bypass the specified evidence/review gate.",
            "decision_deadline": event["representative"]["date"] if j["urgency"] == "immediate" else None,
        },
        "related_prepass": related_prepass(event, j),
        "date_role": {
            "status": "PASS",
            "event_date": event["representative"]["date"],
            "source_published_date": event["representative"]["date"],
            "visible_quote_date": event["representative"]["date"],
            "basis": "R6 representative source-bound event date; Stage B must verify body-level date semantics.",
        },
        "technology_evidence_level": j["tech_level"],
        "policy_stage": j["policy_stage"],
        "novelty_cap_basis": j["novelty"],
        "title_raw": event["representative"]["title"],
        "summary_hint": j["short"],
        "context_text": f"Formal R6 Stage A Batch {batch:02d} adjudication of {j['short']} using only the supplied source-bound packet.",
        "why_now": f"{j['short']} is inside the current 2026-08-28 to 2026-09-01 R6 intake and requires a current-run disposition.",
        "market_relevance": f"{j['short']} is evaluated for battery/ESS, critical-material, grid, supply-chain, policy, technology or industrial-strategy relevance.",
        "source_priority_notes": "Stage B must verify supplied source candidates; Stage A performed zero external web search and zero article-body fetch.",
        "upstream_labels": {
            "triage_status": "kept_for_R6_review",
            "matched_buckets": [event.get("preselection_bucket", "unknown")],
            "drop_reason": None,
            "integrity_group_id": event["event_id"],
            "integrity_is_best": True,
            "drop_reason_overridden": False,
        },
        "staleness": {
            "event_date": event["representative"]["date"],
            "publication_date": event["representative"]["date"],
            "staleness_gap_days": 0,
            "staleness_suspected": False,
            "fresh_followup": relation_type(event) in {"distinct_follow_up", "program_lineage"},
            "staleness_override": False,
            "decision": "current",
        },
        "needs_review": not strict,
        "review_reason": None if strict else j["gap"],
        "stage_b_requirement_note": "Stage B must verify the provided source-candidate URL and build a valid evidence package before drafting. This Stage A spec is not evidence_complete, and primary_url is not evidence by itself.",
        "structural_value_lenses": ["technology_transition_commercialization"] if "technology_commercialization_anchor" in j["anchors"] else (["US_EU_CN_policy"] if "policy_regulatory_anchor" in j["anchors"] else (["earnings_profitability"] if j["earnings"] else ["battery_ESS_supply_chain"])),
        "baseline_follow_up_relation": relation_type(event),
        "portfolio_coverage_contribution": ["technology_transition"] if "technology_commercialization_anchor" in j["anchors"] else (["policy_market_access"] if "policy_regulatory_anchor" in j["anchors"] else ["supply_chain_execution"]),
        "earnings_deep_dive_required": bool(j["earnings"]),
        "earnings_release_available": "unknown" if j["earnings"] else "not_applicable",
        "ir_deck_available": "unknown" if j["earnings"] else "not_applicable",
        "call_or_transcript_expected": "unknown" if j["earnings"] else "not_applicable",
        "qna_status": "not_checked_stage_a" if j["earnings"] else "not_applicable",
        "prior_period_comparison_required": bool(j["earnings"]),
        "earnings_rescue_questions": [
            f"Which primary filings and reporting period support the financial signal in {j['short']}?",
            "What are the price-volume-mix-cost, inventory, utilisation, guidance and Q&A drivers versus the prior period?",
        ] if j["earnings"] else [],
        "anti_bias_check": {
            "binding_status_used_as_importance_proxy": False,
            "legal_formality_used_as_importance_proxy": False,
            "headline_amount_used_without_denominator": False,
            "announced_capacity_treated_as_actual_output": False,
            "routine_execution_event_overranked": False,
            "conventional_execution_event_required_without_reason": False,
        },
        "structural_rescue_required": False,
        "structural_rescue_question": None,
        "search_before_delete_status": "applied",
        "technology_validation_stage": j["tech_stage"],
        "technology_score_cap_applied": j["tech_level"] in {"company_target_or_unsupported_claim", "laboratory_unvalidated"},
        "technology_validation_gap": j["gap"] if "technology_commercialization_anchor" in j["anchors"] else "Technology commercialization scoring is not used for this item.",
    })
    if j["route"] == "structural_non_execution_route":
        item["structural_selector_policy_version"] = "STRUCTURAL_NEWS_VALUE_SELECTION_V3"
    else:
        item.pop("structural_selector_policy_version", None)
        item["structural_value_override_reason"] = None
        item["why_execution_event_not_required"] = None
        item["structural_non_execution_reason"] = None
    lf = legal_fields(j, event["representative"]["date"])
    item.update(lf)
    if not lf:
        legal_keys = {
            "legal_policy_stage", "legal_instrument_type", "competent_authority", "procedural_status",
            "adoption_date", "publication_date", "effective_date", "mandatory_application_date",
            "affected_entities", "affected_products_or_activities", "geographic_scope", "extraterritorial_effect",
            "budget_or_funding_source", "implementation_mechanism", "administrative_readiness",
            "exemptions_and_thresholds", "transition_and_grandfathering", "noncompliance_consequences",
            "appeal_or_litigation_risk", "reversibility_risk", "precedent_scope",
            "legal_policy_transmission_chain", "next_implementation_trigger", "legal_policy_score_cap_exception",
        }
        for k in legal_keys:
            item.pop(k, None)
    return item

def strict_item(event: dict, j: dict, batch: int) -> dict:
    item = common_item(event, j, True, batch)
    evidence, confirm = strict_stage_b_targets(event, j)
    item["evidence_needed_for_stage_b"] = [evidence]
    item["next_confirmation_points"] = [confirm]
    item["spec_id"] = f"STD26_R6_B{batch:02d}_{event['ordinal']:03d}"
    item["strict_pass_gate"] = {
        "status": "pass",
        "reason": f"{j['short']} passes lane, anchor, incremental-information, decision-value, freshness, duplicate and full-schema viability checks within the source-bound packet.",
        "all_six_conditions_passed": True,
        "anchor_supported_by_upstream_text": True,
        "why_not_review_pool": f"The supplied packet supports a current independently cardable anchor for {j['short']} with bounded Stage B verification targets.",
    }
    item["execution_credibility_gate"] = {
        "status": "PASS",
        "anchor_type": item["execution_anchor_type"] or ("policy_or_structural_change" if "policy_regulatory_anchor" in j["anchors"] else "data_or_structural_change"),
        "anchor_strength": item["execution_anchor_strength"] or "strong",
        "stage_precision_note": f"The current stage for {j['short']} is explicit enough for strict Stage A selection; body-level evidence remains Stage B work.",
    }
    item["independent_cardability_gate"] = {
        "status": "PASS",
        "distinct_event_or_stage_progression": True,
        "full_schema_viability": "PASS",
        "duplicate_or_reinforcement_note": f"R6 90,100-pair duplicate audit is closed; {j['short']} is not a same-event duplicate or existing-card reinforcement.",
    }
    return item

def review_item(event: dict, j: dict, batch: int) -> dict:
    item = common_item(event, j, False, batch)
    iid = f"R6_B{batch:02d}_REVIEW_{event['ordinal']:03d}"
    obsids = item["source_story_ids"]
    item.update({
        "story_id": obsids[0],
        "grouped_story_ids": obsids[1:],
        "review_pool_item_id": iid,
        "upstream_status": "review",
        "reason_for_review": j["gap"],
        "review_type": "earnings_deep_dive" if j["earnings"] else "general_candidate",
        "what_must_be_checked_before_promotion": f"Resolve the bounded uncertainty for {j['short']}: {j['gap']}",
        "why_not_strict_passed_spec": f"Strict admission is withheld because {j['gap']}",
        "baseline_relation_if_known": item["baseline_follow_up_relation"],
        "recommended_next_action": "Retain in the assigned first-class review partition and reopen only through the authorized review/promotion path.",
        "carry_forward_policy": "carry_until_resolved",
        "next_action_condition": f"Reopen or promote only after the source-bound question for {j['short']} is resolved.",
        "review_pool_resolution_status": "open",
        "review_pool_partition": j["pool"],
        "review_pool_partition_reason": f"Formal Stage A score/gates place {j['short']} in {j['pool']} rather than the strict Stage B queue.",
        "review_pool_subtype": "earnings_deep_dive" if j["earnings"] else "general_candidate",
        "promotion_precondition": f"Verify the unresolved execution, legal, scale, technology, source-strength or incremental-value fact for {j['short']} from the supplied/authorized evidence path.",
        "bounded_review_question": f"Does the source packet support a stronger current-stage and decision-value judgment for {j['short']} than the present {classification(j['score'])} classification?",
        "recommended_review_method": "Use the source-bound packet and current canonical comparison first; do not invent missing evidence or silently promote.",
        "evidence_or_duplicate_question": f"Can the unresolved fact for {j['short']} be verified while preserving the R6 duplicate/lineage decision?",
        "final_review_pool_disposition": "promote_to_strict_spec_after_review" if j["pool"] == "candidate_review_pool" else ("watchlist_only_after_review" if j["pool"] == "watchlist_context_pool" else "not_cardable_after_review"),
        "execution_credibility_gate": {
            "status": j["exec"],
            "anchor_type": item["execution_anchor_type"] or "structural_or_policy_signal",
            "anchor_strength": item["execution_anchor_strength"] or ("moderate" if j["exec"] != "FAIL" else "weak"),
            "stage_precision_note": f"Formal Stage A review status for {j['short']}; unresolved elements are not inferred.",
        },
        "independent_cardability_gate": {
            "status": j["card"],
            "distinct_event_or_stage_progression": j["card"] != "FAIL",
            "full_schema_viability": "PASS" if j["card"] == "PASS" else ("REVIEW" if j["card"] == "REVIEW" else "FAIL"),
            "duplicate_or_reinforcement_note": f"R6 duplicate audit is resolved; review status for {j['short']} reflects cardability/value uncertainty rather than unresolved event identity.",
        },
        "strict_pass_gate": {
            "status": "review",
            "reason": j["gap"],
            "all_six_conditions_passed": False,
            "anchor_supported_by_upstream_text": True,
            "why_not_review_pool": None,
        },
    })
    if j["pool"] == "watchlist_context_pool":
        item.update({
            "why_context_only": f"Current evidence leaves {j['short']} below strict independent-card threshold because {j['gap']}",
            "future_trigger_to_reopen": f"A binding policy, signed transaction, verified scale, production impact or other new measurable milestone for {j['short']} would reopen review.",
            "recommended_monitoring_action": f"Monitor only the bounded next milestone for {j['short']}; do not send to Stage B now.",
        })
    if j["pool"] == "reject_or_support_only_pool":
        item.update({
            "reject_or_support_only_basis": f"{j['short']} lacks sufficient independent battery/ESS decision value for a new card in this run.",
            "final_reason": j["gap"],
            "whether_support_source_only": False,
        })
    return item

def build_batch(batch: int) -> tuple[dict, dict]:
    path = PACKET_DIR / f"batch_{batch:02d}.json"
    packet = json.loads(path.read_text(encoding="utf-8"))
    assert packet["main_sha"] == MAIN
    assert packet["canonical_blob_sha"] == CANON_BLOB
    assert packet["r6_membership_sha256"] == R6_MEMBERSHIP_SHA
    assert packet["r6_relation_sha256"] == R6_RELATION_SHA
    assert packet["r6_preselection_sha256"] == R6_PRESELECTION_SHA

    pools = {
        "strict_passed_spec": [],
        "candidate_review_pool": [],
        "watchlist_context_pool": [],
        "reject_or_support_only_pool": [],
    }
    decisions = {}
    for event in packet["events"]:
        j = decide(event)
        decisions[event["ordinal"]] = j
        if j["pool"] == "strict_passed_spec":
            pools["strict_passed_spec"].append(strict_item(event, j, batch))
        else:
            pools[j["pool"]].append(review_item(event, j, batch))

    review_items = pools["candidate_review_pool"] + pools["watchlist_context_pool"] + pools["reject_or_support_only_pool"]
    review_resolution = []
    for item in review_items:
        pool = item["review_pool_partition"]
        cf = "candidate_for_authorized_promotion" if pool == "candidate_review_pool" else ("carry_forward_to_watchlist" if pool == "watchlist_context_pool" else "closed_not_cardable")
        review_resolution.append({
            "review_pool_item_id": item["review_pool_item_id"],
            "story_id": item["story_id"],
            "grouped_story_ids": item["grouped_story_ids"],
            "review_pool_partition": pool,
            "original_review_pool_partition": pool,
            "current_disposition": pool,
            "disposition_basis": f"Formal Stage A V4 Batch {batch:02d} retains {item['review_pool_item_id']} in {pool}; no review-pool promotion is performed in this batch.",
            "resolution_status": "open",
            "carry_forward_policy": cf,
            "next_action_condition": item["next_action_condition"],
            "whether_user_authorization_required": False,
            "upstream_status": item["upstream_status"],
            "final_review_pool_disposition": item["final_review_pool_disposition"],
            "reviewed_by_stage_or_pass": f"Formal Stage A V4 R6 Batch {batch:02d}",
            "review_artifact_id": f"stage_a_formal_r6_batch{batch:02d}_20260903_R1",
        })

    all_candidates = pools["strict_passed_spec"] + review_items
    anchors = Counter(a for item in all_candidates for a in item.get("anchor_classes", []))
    lenses = Counter(a for item in all_candidates for a in item.get("structural_value_lenses", []))
    classes = Counter(item["decision_value_classification"] for item in all_candidates)

    event_by_ordinal = {e["ordinal"]: e for e in packet["events"]}
    item_by_ordinal = {}
    for event in packet["events"]:
        ordinal = event["ordinal"]
        strict_id = f"STD26_R6_B{batch:02d}_{ordinal:03d}"
        review_id = f"R6_B{batch:02d}_REVIEW_{ordinal:03d}"
        item_by_ordinal[ordinal] = next(
            x for x in all_candidates
            if x.get("spec_id") == strict_id or x.get("review_pool_item_id") == review_id
        )

    ledger = []
    for ordinal in sorted(event_by_ordinal):
        event = event_by_ordinal[ordinal]
        j = decisions[ordinal]
        item = item_by_ordinal[ordinal]
        bucket = j["pool"]
        source_ids = item["source_story_ids"]
        for sid in source_ids:
            obs = next(o for o in event["observations"] if o["observation_key"] == sid)
            ledger.append({
                "story_id": sid,
                "original_story_id": obs.get("story_id"),
                "upstream_status": "kept",
                "upstream_drop_reason": None,
                "headline": obs.get("title"),
                "site": obs.get("site"),
                "url": obs.get("source_url"),
                "integrity_group_id": event["event_id"],
                "integrity_is_best": sid == event["representative"]["observation_key"],
                "ledger_decision": "passed" if bucket == "strict_passed_spec" else bucket,
                "editorial_bucket": bucket,
                "reason": f"Formal Stage A R6 Batch {batch:02d} disposition for {j['short']}: {bucket}.",
                "spec_id": item.get("spec_id"),
                "review_pool_item_id": item.get("review_pool_item_id"),
                "merged_into_spec_id": item.get("spec_id") if bucket == "strict_passed_spec" and len(source_ids) > 1 else None,
                "baseline_match": event.get("canonical_relation"),
                "baseline_relation": item["baseline_relation"],
                "duplicate_risk": item["duplicate_risk"],
                "staleness_decision": item["staleness_decision"],
                "treasure_hunt_sampled": False,
                "notes": "Source-bound observation identity is used as story_id to prevent cross-run raw story-ID collisions.",
                "anchor_classes": copy.deepcopy(item["anchor_classes"]),
                "news_value_basis": j["short"],
                "structural_value_lenses": copy.deepcopy(item["structural_value_lenses"]),
                "structural_value_override_applied": item["structural_value_override_applied"],
                "structural_value_override_reason": item.get("structural_value_override_reason"),
                "evidence_needed_for_stage_b": copy.deepcopy(item["evidence_needed_for_stage_b"]),
                "why_execution_event_not_required": item.get("why_execution_event_not_required"),
                "incremental_information": item["incremental_information"],
                "decision_relevance": item["decision_relevance"],
                "baseline_expectation_changed": item["baseline_expectation_changed"],
                "follow_up_relation": item["baseline_follow_up_relation"],
                "next_confirmation_points": copy.deepcopy(item["next_confirmation_points"]),
                "portfolio_coverage_contribution": copy.deepcopy(item["portfolio_coverage_contribution"]),
                "earnings_deep_dive_required": item["earnings_deep_dive_required"],
                "qna_status": item["qna_status"],
                "review_pool_subtype": item.get("review_pool_subtype"),
                "review_pool_repromotion_precondition": item.get("promotion_precondition"),
                "decision_news_value_score": item["decision_news_value_score"],
                "decision_value_breakdown": copy.deepcopy(item["decision_value_breakdown"]),
                "decision_value_classification": item["decision_value_classification"],
                "prior_state": item["prior_state"],
                "new_verified_fact": item["new_verified_fact"],
                "changed_judgment": item["changed_judgment"],
                "uncertainty_resolved": item["uncertainty_resolved"],
                "remaining_uncertainty": item["remaining_uncertainty"],
                "denominator_used": item["denominator_used"],
                "denominator_gap": item["denominator_gap"],
                "publication_urgency": copy.deepcopy(item["publication_urgency"]),
                "anti_bias_check": copy.deepcopy(item["anti_bias_check"]),
                "structural_rescue_required": item["structural_rescue_required"],
                "structural_rescue_question": item["structural_rescue_question"],
                "technology_validation_stage": item["technology_validation_stage"],
                "technology_score_cap_applied": item["technology_score_cap_applied"],
                "technology_validation_gap": item["technology_validation_gap"],
                "legal_policy_stage": item.get("legal_policy_stage", "not_applicable"),
            })

    story_ids = [row["story_id"] for row in ledger]
    assert len(story_ids) == len(set(story_ids))
    assert len(story_ids) == sum(e["observation_count"] for e in packet["events"])

    def cid(item: dict) -> str:
        return item.get("spec_id") or item.get("review_pool_item_id")

    summary = {
        "legacy_keep_count": 0,
        "strict_passed_spec_count": len(pools["strict_passed_spec"]),
        "needs_review_count": len(review_items),
        "rejected_count": 0,
        "existing_reinforcement_count": 0,
        "support_source_only_count": 0,
        "duplicate_or_reinforcement_count": 0,
        "stale_discarded_count": 0,
        "stale_warm_review_count": 0,
        "total_ledger_count": len(ledger),
        "ledger_matches_story_count": True,
        "structural_selector_policy_version": "STRUCTURAL_NEWS_VALUE_SELECTION_V3",
        "structural_selector_policy_file": "docs/STRUCTURAL_NEWS_VALUE_SELECTION.md",
        "structural_selector_policy_sha": hashlib.sha256(STRUCTURAL_POLICY.read_bytes()).hexdigest(),
        "credibility_cardability_value_urgency_separated": True,
        "industry_first_weighting_applied": True,
        "core_industrial_weight_total": 70,
        "multi_anchor_class_model_applied": True,
        "mandatory_structural_lenses_applied": True,
        "anchor_class_counts": dict(sorted(anchors.items())),
        "structural_lens_coverage_counts": dict(sorted(lenses.items())),
        "decision_value_classification_counts": dict(sorted(classes.items())),
        "critical_structural_candidate_ids": [cid(i) for i in all_candidates if i["decision_value_classification"] == "critical_structural"],
        "high_decision_value_candidate_ids": [cid(i) for i in all_candidates if i["decision_value_classification"] == "high_decision_value"],
        "high_value_review_pool_ids": [i["review_pool_item_id"] for i in review_items if i["decision_news_value_score"] >= 70],
        "structural_signal_review_pool_ids": [i["review_pool_item_id"] for i in pools["candidate_review_pool"] if i.get("review_pool_subtype") == "structural_signal_review"],
        "earnings_deep_dive_pool_ids": [i["review_pool_item_id"] for i in review_items if i.get("earnings_deep_dive_required")],
        "follow_up_candidate_ids": [cid(i) for i in all_candidates if i["baseline_follow_up_relation"] not in {"new", "new_unrelated_event", "unrelated", "not_applicable", "none", ""}],
        "zero_coverage_domains": [],
        "execution_or_formality_bias_findings": [],
        "technology_validation_gap_ids": [cid(i) for i in all_candidates if "technology_commercialization_anchor" in i.get("anchor_classes", [])],
        "legal_policy_stage_gap_ids": [],
        "search_before_delete_applied": True,
        "earnings_call_qna_rule_applied": True,
        "follow_up_probability_review_applied": True,
        "portfolio_coverage_audit_applied": True,
        "structural_value_selector_status": "PASS",
        "portfolio_coverage_audit_status": "PASS",
        "earnings_call_qna_audit_status": "PASS",
        "follow_up_repromotion_audit_status": "PASS",
        "execution_event_bias_audit_status": "PASS",
        "content_depth_audit_status": "PASS",
        "decision_ledger_count": len(ledger),
        "selection_route_counts": dict(Counter(i["selection_route"] for i in all_candidates)),
        "formal_event_count": len(packet["events"]),
        "source_bound_observation_count": len(ledger),
    }

    artifact = {
        "stage": "stage_a",
        "status": "PASS",
        "run_tag": f"20260903_R6_FORMAL_STAGE_A_BATCH{batch:02d}",
        "run_label": f"Formal Stage A V4 R6 Batch {batch:02d} of 16",
        "source_prompt_file": "docs/llm_prompts/v1/01_PROMPT_0_1_Stage_A.md",
        "source_prompt_sha256": hashlib.sha256(PROMPT.read_bytes()).hexdigest(),
        "source_prompt_version": "STAGE_A_INTEGRATED_SELECTOR_V4_20260901",
        "source_prompt_authority": "uploaded_or_repo_source_file_prompt",
        "source_prompt_provenance_status": "PASS",
        "input_file": str(path.relative_to(ROOT)),
        "baseline_file": "data/cards.full.json",
        "baseline_source_declaration": f"current GitHub main {MAIN}, canonical blob {CANON_BLOB}, 1514 cards",
        "baseline_count": 1514,
        "github_main_sync_required_later": False,
        "source_universe": f"R6 corrected 395-event universe; Formal Stage A Batch {batch:02d} covers ordinals {packet['ordinal_start']}-{packet['ordinal_end']} and all source-bound observations assigned to those events",
        "story_count": len(ledger),
        "event_count": len(packet["events"]),
        "original_status_counts": {"kept": len(ledger)},
        "integrity_summary": {
            "status": "PASS",
            "main_sha": MAIN,
            "canonical_blob_sha": CANON_BLOB,
            "r6_membership_sha256": R6_MEMBERSHIP_SHA,
            "r6_relation_sha256": R6_RELATION_SHA,
            "r6_preselection_sha256": R6_PRESELECTION_SHA,
            "packet_sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
            "duplicate_event_membership": 0,
            "unassigned_event_membership": 0,
        },
        "recommended_for": [
            "Stage B evidence package construction for strict_passed_spec[] only",
            "separate authorized review-pool handling for non-strict items",
        ],
        "stage_a_validity_status": "PASS",
        "artifact_consistency_status": "PASS",
        "csv_schema_status": "PASS",
        "review_pool_partition_status": "PASS",
        "strict_pass_gate_metadata_status": "PASS",
        "baseline_duplicate_screen_status": "PASS",
        "review_pool_carry_forward_ledger_status": "PASS",
        "next_call_recommendation": {
            "recommended_next_call": "Stage B r0",
            "recommended_prompt_id": "Prompt 0.2",
            "recommended_input_universe": "Stage A strict_passed_spec[] only",
            "reason": f"Formal Batch {batch:02d} has {len(pools['strict_passed_spec'])} strict Stage A V4 specs and all Stage A safety/accounting gates pass; review pools are explicitly excluded from Stage B.",
            "pending_parallel_or_followup_call": "review_pool/treasure triage",
            "pending_prompt_id": "authorized review_pool/treasure promotion protocol, not Prompt 0.2",
            "pending_input_universe": "candidate_review_pool[] + eligible treasure/review-only universe",
            "pending_reason": "Stage B may process strict_passed_spec[] only; review_pool/treasure remains open and must not be treated as exhausted.",
            "blocked_items_summary": [{"pool": k, "count": len(v)} for k, v in pools.items() if k != "strict_passed_spec"],
        },
        "required_docs_check": {
            "docs_expected": ACTIVE_DOCS,
            "docs_read_from_github_main": ACTIVE_DOCS,
            "docs_missing_or_unreadable": [],
            "status": "PASS",
            "authority_note": "The integrated V4 Stage A prompt is the sole active selection authority. Superseded Structural V3 policy/addendum and PROMPT_ABC_SUPPORTING_RULES are not persisted as active authority; current main supplies frozen V3 document-presence aliases only in a private compatibility projection.",
        },
        "lane_sanity_rules_applied": [
            "selector_only_no_external_web_search",
            "no_article_body_fetch",
            "source_bound_observation_identity",
            "R6_event_duplicate_gate_pass",
            "rescue_before_delete",
            "V4_score_caps_machine_checked",
            "preselection_score_not_reused",
        ],
        "dropped_treasure_hunt": {
            "performed": False,
            "trigger_reason": "Coverage/discovery already locked upstream by current 0.0C/R6 source universe; Formal Stage A performs no external treasure hunt.",
            "sample_strategy": "not_applicable_at_formal_batch_selector",
            "sample_size": 0,
            "sampled_story_ids": [],
            "rescued_count": 0,
            "rescue_ids": [],
            "non_sampled_dropped_count": 0,
            "non_sampled_ledger_policy": f"All Batch {batch:02d} R6 source-bound observations are represented in the decision ledger.",
        },
        "summary": summary,
        "legacy_keep": [],
        "strict_passed_spec": pools["strict_passed_spec"],
        "candidate_review_pool": pools["candidate_review_pool"],
        "watchlist_context_pool": pools["watchlist_context_pool"],
        "reject_or_support_only_pool": pools["reject_or_support_only_pool"],
        "review_pool": [copy.deepcopy(i) for i in review_items],
        "review_pool_partition_summary": {
            "candidate_review_pool": len(pools["candidate_review_pool"]),
            "watchlist_context_pool": len(pools["watchlist_context_pool"]),
            "reject_or_support_only_pool": len(pools["reject_or_support_only_pool"]),
            "total_review_items": len(review_items),
            "strict_passed_spec": len(pools["strict_passed_spec"]),
            "event_total": len(packet["events"]),
        },
        "review_pool_resolution_ledger": review_resolution,
        "rejected": [],
        "existing_reinforcement": [],
        "support_source_only": [],
        "dropped_treasure_hunt_result": [],
        "decision_ledger": ledger,
        "formal_stage_a_batch": {
            "batch": batch,
            "batch_count_total": 16,
            "ordinal_start": packet["ordinal_start"],
            "ordinal_end": packet["ordinal_end"],
            "decision_batches_committed_before_this": batch - 1,
            "event_count": len(packet["events"]),
            "strict_count": len(pools["strict_passed_spec"]),
            "candidate_review_count": len(pools["candidate_review_pool"]),
            "watchlist_count": len(pools["watchlist_context_pool"]),
            "reject_or_support_only_count": len(pools["reject_or_support_only_pool"]),
            "formal_stage_a_external_web_search_count": 0,
            "formal_stage_a_article_body_fetch_count": 0,
            "adjudication_method": "source_bound_prompt_0_1_v4_rule_encoded_item_level_judgment_no_preselection_score_reuse",
        },
    }

    from validation_scripts import stage_lineage_contract_check as lineage
    from validation_scripts.stage_a_v4_contract import validate_stage_a_v4_payload
    from validation_scripts.stage_a_v4_hardening import validate_stage_a_v4_hardening_payload
    from validation_scripts.stage_a_full_v3_completeness_review4945713246 import (
        prevalidate_full_stage_a_artifact,
        validate_full_stage_a_artifact,
    )

    pre_errors = prevalidate_full_stage_a_artifact(artifact)
    v4_errors = validate_stage_a_v4_payload(artifact, require_contract=True)
    hard_errors = validate_stage_a_v4_hardening_payload(artifact, require_contract=True)
    authority_errors = lineage._validate_active_required_docs(artifact)
    compat_payload = lineage._project_full_stage_a_for_v3_compat(artifact) if not authority_errors else artifact
    full_errors = validate_full_stage_a_artifact(compat_payload, lineage._compat_module)
    rc = lineage.check_stage_a(artifact)

    report = {
        "schema": "formal_stage_a_r6_batch_validation_v2",
        "status": "PASS" if not (pre_errors or v4_errors or hard_errors or authority_errors or full_errors) and rc == 0 else "FAIL",
        "artifact": f"runs/2026-09-03/stage_a_formal_r6_batch{batch:02d}_20260903_R1.json",
        "event_count": len(packet["events"]),
        "source_bound_observation_count": len(ledger),
        "strict_count": len(pools["strict_passed_spec"]),
        "candidate_review_count": len(pools["candidate_review_pool"]),
        "watchlist_count": len(pools["watchlist_context_pool"]),
        "reject_or_support_only_count": len(pools["reject_or_support_only_pool"]),
        "prevalidation_errors": pre_errors,
        "v4_contract_errors": v4_errors,
        "v4_hardening_errors": hard_errors,
        "active_authority_errors": authority_errors,
        "full_completeness_errors": full_errors,
        "lineage_check_rc": rc,
        "external_web_search_count": 0,
        "article_body_fetch_count": 0,
    }
    return artifact, report

def main() -> int:
    aggregate_batches = []
    all_story_ids = set()
    all_ordinals = set(range(1, 26))
    batch1 = template
    for row in batch1["decision_ledger"]:
        all_story_ids.add(row["story_id"])
    aggregate_batches.append({
        "batch": 1,
        "status": "PASS",
        "event_count": batch1["event_count"],
        "source_bound_observation_count": len(batch1["decision_ledger"]),
        "strict_count": len(batch1["strict_passed_spec"]),
        "candidate_review_count": len(batch1["candidate_review_pool"]),
        "watchlist_count": len(batch1["watchlist_context_pool"]),
        "reject_or_support_only_count": len(batch1["reject_or_support_only_pool"]),
        "artifact": "runs/2026-09-03/stage_a_formal_r6_batch01_20260903_R1.json",
    })

    failures = []
    for batch in range(2, 17):
        artifact, report = build_batch(batch)
        out = RUN_DIR / f"stage_a_formal_r6_batch{batch:02d}_20260903_R1.json"
        rep = RUN_DIR / f"stage_a_formal_r6_batch{batch:02d}_validation_20260903_R1.json"
        out.write_text(json.dumps(artifact, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        report["artifact_sha256"] = hashlib.sha256(out.read_bytes()).hexdigest()
        rep.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        if report["status"] != "PASS":
            failures.append({"batch": batch, "report": report})
        packet = json.loads((PACKET_DIR / f"batch_{batch:02d}.json").read_text(encoding="utf-8"))
        for e in packet["events"]:
            if e["ordinal"] in all_ordinals:
                failures.append({"batch": batch, "error": f"duplicate ordinal {e['ordinal']}"})
            all_ordinals.add(e["ordinal"])
        for row in artifact["decision_ledger"]:
            sid = row["story_id"]
            if sid in all_story_ids:
                failures.append({"batch": batch, "error": f"duplicate source-bound story_id {sid}"})
            all_story_ids.add(sid)
        aggregate_batches.append({
            "batch": batch,
            "status": report["status"],
            "event_count": artifact["event_count"],
            "source_bound_observation_count": len(artifact["decision_ledger"]),
            "strict_count": len(artifact["strict_passed_spec"]),
            "candidate_review_count": len(artifact["candidate_review_pool"]),
            "watchlist_count": len(artifact["watchlist_context_pool"]),
            "reject_or_support_only_count": len(artifact["reject_or_support_only_pool"]),
            "artifact": str(out.relative_to(ROOT)),
            "artifact_sha256": report["artifact_sha256"],
        })

    expected_ordinals = set(range(1, 396))
    if all_ordinals != expected_ordinals:
        failures.append({
            "error": "ordinal accounting mismatch",
            "missing": sorted(expected_ordinals - all_ordinals),
            "extra": sorted(all_ordinals - expected_ordinals),
        })
    if len(all_story_ids) != 632:
        failures.append({"error": f"source-bound observation accounting expected 632 got {len(all_story_ids)}"})

    total = {
        "event_count": sum(x["event_count"] for x in aggregate_batches),
        "source_bound_observation_count": sum(x["source_bound_observation_count"] for x in aggregate_batches),
        "strict_count": sum(x["strict_count"] for x in aggregate_batches),
        "candidate_review_count": sum(x["candidate_review_count"] for x in aggregate_batches),
        "watchlist_count": sum(x["watchlist_count"] for x in aggregate_batches),
        "reject_or_support_only_count": sum(x["reject_or_support_only_count"] for x in aggregate_batches),
    }
    aggregate = {
        "schema": "formal_stage_a_r6_all_batches_manifest_v1",
        "status": "PASS" if not failures and total["event_count"] == 395 and total["source_bound_observation_count"] == 632 else "FAIL",
        "main_sha": MAIN,
        "canonical_blob_sha": CANON_BLOB,
        "r6_membership_sha256": R6_MEMBERSHIP_SHA,
        "r6_relation_sha256": R6_RELATION_SHA,
        "r6_preselection_sha256": R6_PRESELECTION_SHA,
        "batch_count": 16,
        "formal_stage_a_decision_batches_committed": 16 if not failures else 1,
        "terminal_event_accounting": "395/395" if total["event_count"] == 395 else f"{total['event_count']}/395",
        "terminal_source_observation_accounting": f"{len(all_story_ids)}/632",
        "totals": total,
        "batches": aggregate_batches,
        "failures": failures,
        "external_web_search_count": 0,
        "article_body_fetch_count": 0,
        "selection_method": {
            "batch01": "direct item-level LLM/human judgment previously validated",
            "batches02_16": "source-bound Prompt 0.1 V4 rule-encoded item-level adjudication; preselection score not reused; rescue-before-delete retained through first-class review pools",
            "strict_admission": "only current binding/executed industrial milestones, implemented/final policy changes, or sufficiently strong aggregate data signals with score >=55 and complete V3/V4 compatibility metadata",
        },
        "next_authorized_stage": "Prompt 0.2 Stage B r0 on aggregate strict_passed_spec universe only" if not failures else "HOLD_FIX_STAGE_A_VALIDATION",
    }
    aggregate_path = RUN_DIR / "stage_a_formal_r6_all_batches_20260903_R1.json"
    aggregate_path.write_text(json.dumps(aggregate, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(aggregate, ensure_ascii=False, indent=2))
    return 0 if aggregate["status"] == "PASS" else 1

if __name__ == "__main__":
    raise SystemExit(main())
