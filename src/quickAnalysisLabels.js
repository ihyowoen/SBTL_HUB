// User-facing labels for automated brief-window outputs.
// Internal `period="monthly"` is a storage/time-window detail; it must not leak as
// the official product name now reserved for SBTL Monthly Brief.

export function calendarQuickAnalysisLabel(month, nowYear = null) {
  const m = String(month || "").match(/^(\d{4})-(\d{2})$/);
  if (!m) return "월별 빠른 분석";
  const year = Number(m[1]);
  const monthNum = Number(m[2]);
  const yearPrefix = Number.isFinite(nowYear) && year !== nowYear ? `${year}년 ` : "";
  return `${yearPrefix}${monthNum}월 빠른 분석`;
}

export function quickAnalysisChipLabel(entry, nowYear, dupMonth = false) {
  const e = entry || {};
  const dd = String(e.generated_at || "").slice(5);
  if (e.month) {
    const base = calendarQuickAnalysisLabel(e.month, nowYear);
    return `${base}${e.group === "custom" ? "🧩" : ""}${dupMonth ? ` ${dd}` : ""}`;
  }
  if (e.group === "custom") return `🧩 ${e.period === "monthly" ? "30일" : "주간"} ${dd}`;
  return `${e.period === "monthly" ? "30일" : "주간"} ${dd}`;
}
