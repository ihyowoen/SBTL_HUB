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

  let base = 0.3;
  base += Math.min(0.35, top / 40);
  base += Math.min(0.15, gap / 20);
  base += Math.min(0.1, cards.length / 10);

  if (scope?.region && cards[0]?.r && (cards[0].r === scope.region || (scope.region === "US" && cards[0].r === "NA"))) {
    base += 0.08;
  }
  if (scope?.date && cards[0]?.d && String(cards[0].d).includes(String(scope.date).slice(0, 7))) {
    base += 0.05;
  }
  if (intent === "policy" && retrieval?.policy?.upcoming?.length) {
    base += 0.07;
  }

  const score = clamp01(base);
  const bucket = score >= 0.8 ? "high" : score >= 0.55 ? "medium" : "low";
  const reasons = [];
  if (top > 0) reasons.push("retrieval_score");
  if (gap > 0) reasons.push("top_gap");
  if (scope?.region) reasons.push("region_scope");
  return { score, bucket, reasons };
}
