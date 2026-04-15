import { fmtDate } from "./common.js";

const HIGH_CONFIDENCE_THRESHOLD = 0.8;
const MEDIUM_CONFIDENCE_THRESHOLD = 0.55;

function clamp01(v) {
  return Math.max(0, Math.min(1, Number(v) || 0));
}

export function scoreConfidence({ intent, retrieval, scope }) {
  if (retrieval?.mode === "faq" && retrieval?.faq?.answer) {
    return { score: 0.92, bucket: "high", reasons: ["faq_match"] };
  }

  const cards = retrieval?.cards || [];
  if (!cards.length) {
    return { score: 0.2, bucket: "low", reasons: ["no_internal_cards"] };
  }

  const top = Number(cards[0]?._score || 0);
  const second = Number(cards[1]?._score || 0);
  const gap = Math.max(0, top - second);
  const topTitle = String(cards[0]?.T || "").toLowerCase();
  const topicTokens = Array.isArray(scope?.topic_tokens) ? scope.topic_tokens : [];
  const tokenHitCount = topicTokens.filter((t) => t && topTitle.includes(String(t).toLowerCase())).length;
  const tokenCoverage = topicTokens.length ? (tokenHitCount / topicTokens.length) : 0;

  let base = 0.3;
  base += Math.min(0.35, top / 40);
  base += Math.min(0.15, gap / 20);
  base += Math.min(0.1, cards.length / 10);

  if (scope?.region && cards[0]?.r && (cards[0].r === scope.region || (scope.region === "US" && cards[0].r === "NA"))) {
    base += 0.08;
  }
  if (scope?.date && cards[0]?.d && fmtDate(cards[0].d) === fmtDate(scope.date)) {
    base += 0.05;
  }
  if (intent === "policy" && retrieval?.policy?.upcoming?.length) {
    base += 0.07;
  }
  if (tokenCoverage >= 0.5) base += 0.08;
  else if (tokenCoverage < 0.2 && topicTokens.length >= 2) base -= 0.1;
  if (intent === "news" && tokenCoverage < 0.25 && top < 18) base -= 0.1;
  if (intent === "policy" && !retrieval?.policy?.upcoming?.length && top < 20) base -= 0.08;

  const score = clamp01(base);
  const bucket = score >= HIGH_CONFIDENCE_THRESHOLD
    ? "high"
    : score >= MEDIUM_CONFIDENCE_THRESHOLD
      ? "medium"
      : "low";
  const reasons = [];
  if (top > 0) reasons.push("retrieval_score");
  if (gap > 0) reasons.push("top_gap");
  if (scope?.region) reasons.push("region_scope");
  reasons.push(`token_coverage:${tokenCoverage.toFixed(2)}`);
  return { score, bucket, reasons };
}
