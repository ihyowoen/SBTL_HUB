export function matchesStrategicRequest(item, requested) {
  if (!item || !requested) return false;
  if (requested.edition && item.edition !== requested.edition) return false;
  if (requested.month && item.month !== requested.month) return false;
  return true;
}

export function selectStrategicIssue(items = [], requested = null, selectedId = null) {
  const safe = Array.isArray(items) ? items : [];
  if (requested) {
    const exact = safe.find((item) => matchesStrategicRequest(item, requested)) || null;
    return { issue: exact, requestMissing: !exact };
  }
  return {
    issue: safe.find((item) => item?.id === selectedId) || safe[0] || null,
    requestMissing: false,
  };
}
