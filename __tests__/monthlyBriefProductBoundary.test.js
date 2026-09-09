import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { appCommandResponse, detectAppCommand } from "../lib/chat/appCommand.js";
import { isOfficialPublicationRequest } from "../api/brief.js";

const RECENT = [
  { date: "2026-09-07", title: "CATL ESS update", fact: "fact", gate: "gate" },
  { date: "2026-09-06", title: "LGES ESS update", fact: "fact", gate: "gate" },
];
const AUGUST = [
  { date: "2026-08-20", title: "August A", fact: "fact", gate: "gate" },
  { date: "2026-08-10", title: "August B", fact: "fact", gate: "gate" },
];

function opts(cards = RECENT) {
  return { cards, watchTerms: [], lastBriefAt: 0, lastMonthlyBriefAt: 0 };
}

describe("SBTL Monthly Brief product boundary", () => {
  beforeEach(() => {
    vi.useFakeTimers();
    vi.setSystemTime(new Date("2026-09-08T00:00:00Z"));
  });

  afterEach(() => vi.useRealTimers());

  it("keeps 30-day quick analysis exploratory", () => {
    expect(detectAppCommand("30일 빠른 분석 만들어줘", [], opts())).toEqual({
      type: "brief_now",
      scope: "all",
      period: "monthly",
    });
  });

  it("preserves the calendar month in the advertised 월별 빠른 분석 wording", () => {
    expect(detectAppCommand("2026년 8월 월별 빠른 분석 만들어줘", [], opts(AUGUST))).toEqual({
      type: "brief_now",
      scope: "all",
      period: "monthly",
      month: "2026-08",
    });
  });

  it("routes the official Monthly Brief reader by month identity", () => {
    expect(detectAppCommand("월간 브리프 보여줘", [], opts())).toEqual({ type: "monthly_show" });
    expect(detectAppCommand("2026년 8월 월간 브리프 보여줘", [], opts())).toEqual({ type: "monthly_show", month: "2026-08" });
    const response = appCommandResponse({ type: "monthly_show", month: "2026-08" });
    expect(response.answer).toContain("SBTL Monthly Brief");
    expect(response.answer).toContain("자동 생성하지 않아");
  });

  it("preserves optional 월호 qualifiers in official Monthly Brief commands", () => {
    expect(detectAppCommand("8월호 월간 브리프 보여줘", [], opts())).toEqual({ type: "monthly_show", month: "2026-08" });
    expect(detectAppCommand("2025년 8월호 월간 브리프 만들어줘", [], opts())).toMatchObject({ type: "monthly_show", month: "2025-08", requested_action: "create" });
  });

  it("does not let Monthly Brief create wording fall into the automatic generator", () => {
    for (const text of ["월간 브리프 만들어줘", "월간 브리프 하나 만들어줘", "2026년 8월 월간 브리프 하나 만들어줘"]) {
      const cmd = detectAppCommand(text, [], opts());
      expect(cmd?.type).toBe("monthly_show");
      expect(cmd?.requested_action).toBe("create");
      expect(appCommandResponse(cmd).answer).toContain("편집 승인");
      expect(appCommandResponse(cmd).suggestions.some((s) => s.label.includes("30일 빠른 분석"))).toBe(true);
    }
    expect(detectAppCommand("2026년 8월 월간 브리프 하나 만들어줘", [], opts())).toMatchObject({ month: "2026-08" });
  });

  it("supports calendar-month region quick analysis without turning it into an official brief", () => {
    expect(detectAppCommand("2026년 8월 지역별 빠른 분석 만들어줘", [], opts(AUGUST))).toEqual({
      type: "brief_now",
      scope: "all",
      period: "monthly",
      month: "2026-08",
      group: "region",
    });
  });

  it("does not route legacy Strategic/VOL newsletter identity into the HUB Monthly Brief", () => {
    expect(detectAppCommand("월간 전략 브리핑 보여줘", [], opts())).toBeNull();
    expect(detectAppCommand("VOL.10 전략 브리핑 보여줘", [], opts())).toBeNull();
  });

  it("rejects official publication intent at the exploratory synthesis API boundary", () => {
    expect(isOfficialPublicationRequest({ publication_class: "official_editorial" })).toBe(true);
    expect(isOfficialPublicationRequest({ publication_mode: "editorial_curated" })).toBe(true);
    expect(isOfficialPublicationRequest({ publication_class: "exploratory_auto" })).toBe(false);
    expect(isOfficialPublicationRequest({ cards: RECENT })).toBe(false);
  });
});