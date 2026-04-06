export function decideFallback({ scope, confidence, retrieval }) {
  const explicitExternal = !!scope?.explicit_external;
  const low = confidence?.bucket === "low";
  const medium = confidence?.bucket === "medium";
  const hasInternal = (retrieval?.cards || []).length > 0 || !!retrieval?.faq;
  const top = Number(retrieval?.cards?.[0]?._score || 0);
  const second = Number(retrieval?.cards?.[1]?._score || 0);
  const gap = Math.max(0, top - second);
  const weakMedium = medium && (top < 20 || gap < 3);
  const policyWeak = retrieval?.policy && medium && (retrieval?.policy?.upcoming || []).length === 0;

  if (explicitExternal) {
    return { fallbackTriggered: true, sourceMode: hasInternal ? "hybrid" : "external", reason: "explicit_external_request" };
  }

  if (low) {
    return { fallbackTriggered: true, sourceMode: hasInternal ? "hybrid" : "external", reason: "low_confidence" };
  }

  if (medium && !hasInternal) {
    return { fallbackTriggered: true, sourceMode: "external", reason: "insufficient_internal_coverage" };
  }

  if (weakMedium || policyWeak) {
    return { fallbackTriggered: true, sourceMode: hasInternal ? "hybrid" : "external", reason: weakMedium ? "medium_confidence_weak_match" : "policy_evidence_weak" };
  }

  return { fallbackTriggered: false, sourceMode: "internal", reason: "internal_confident" };
}
