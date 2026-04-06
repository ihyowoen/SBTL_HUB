export function decideFallback({ scope, confidence, retrieval }) {
  const explicitExternal = !!scope?.explicit_external;
  const low = confidence?.bucket === "low";
  const medium = confidence?.bucket === "medium";
  const hasInternal = (retrieval?.cards || []).length > 0 || !!retrieval?.faq;

  if (explicitExternal) {
    return { fallbackTriggered: true, sourceMode: hasInternal ? "hybrid" : "external", reason: "explicit_external_request" };
  }

  if (low) {
    return { fallbackTriggered: true, sourceMode: hasInternal ? "hybrid" : "external", reason: "low_confidence" };
  }

  if (medium && !hasInternal) {
    return { fallbackTriggered: true, sourceMode: "external", reason: "insufficient_internal_coverage" };
  }

  return { fallbackTriggered: false, sourceMode: "internal", reason: "internal_confident" };
}
