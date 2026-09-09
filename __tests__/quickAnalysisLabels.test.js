import { describe, expect, it } from "vitest";
import { calendarQuickAnalysisLabel, quickAnalysisChipLabel, quickAnalysisProseLabel } from "../src/quickAnalysisLabels.js";

describe("Quick Analysis display labels", () => {
  it("labels rolling 30-day analysis without the official monthly product name", () => {
    expect(quickAnalysisChipLabel({ period: "monthly", generated_at: "2026-09-08" }, 2026)).toBe("30일 09-08");
  });

  it("labels calendar-month analysis as a quick analysis", () => {
    expect(quickAnalysisChipLabel({ period: "monthly", month: "2026-08", generated_at: "2026-09-08" }, 2026)).toBe("8월 빠른 분석");
    expect(calendarQuickAnalysisLabel("2025-12", 2026)).toBe("2025년 12월 빠른 분석");
  });

  it("keeps rolling unread prose classified as Quick Analysis", () => {
    expect(quickAnalysisProseLabel({ period: "monthly", label: "30일 09-08" })).toBe("30일 빠른 분석");
    expect(quickAnalysisProseLabel({ period: "monthly", group: "custom", label: "🧩 30일 09-08" })).toBe("🧩 30일 빠른 분석");
    expect(quickAnalysisProseLabel({ period: "weekly", label: "주간 09-08" })).toBe("주간 09-08 브리프");
  });

  it("preserves custom and duplicate disambiguation without saying 월간", () => {
    expect(quickAnalysisChipLabel({ period: "monthly", group: "custom", generated_at: "2026-09-08" }, 2026)).toBe("🧩 30일 09-08");
    expect(quickAnalysisChipLabel({ period: "monthly", month: "2026-08", group: "custom", generated_at: "2026-09-08" }, 2026, true)).toBe("8월 빠른 분석🧩 09-08");
  });
});
