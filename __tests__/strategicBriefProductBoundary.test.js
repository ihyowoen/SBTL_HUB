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

describe("Strategic Brief product boundary", () => {
  beforeEach(() => {
    vi.useFakeTimers();
    vi.setSystemTime(new Date("2026-09-08T00:00:00Z"));
  });

  afterEach(() => vi.useRealTimers());

  it("treats the new 30-day wording as exploratory monthly-window analysis", () => {
    expect(detectAppCommand("30일 빠른 분석 만들어줘", [], opts())).toEqual({
      type: "brief_now",
      scope: "all",
      period: "monthly",
    });
  });

  it("keeps legacy monthly brief wording as backward-compatible exploratory analysis", () => {
    const cmd = detectAppCommand("월간 브리프 만들어줘", [], opts());
    expect(cmd).toEqual({ type: "brief_now", scope: "all", period: "monthly" });
    const response = appCommandResponse(cmd);
    expect(response.answer).toContain("30일 빠른 분석");
    expect(response.answer).not.toContain("월간 브리프 만들게");
  });

  it("supports calendar-month region quick analysis without turning it into an official issue", () => {
    expect(detectAppCommand("2026년 8월 지역별 빠른 분석 만들어줘", [], opts(AUGUST))).toEqual({
      type: "brief_now",
      scope: "all",
      period: "monthly",
      month: "2026-08",
      group: "region",
    });
  });

  it("routes official monthly Strategic Brief reading to a separate command", () => {
    expect(detectAppCommand("월간 전략 브리핑 보여줘", [], opts())).toEqual({ type: "strategic_show" });
    expect(detectAppCommand("2026년 8월 전략 브리핑 보여줘", [], opts())).toEqual({ type: "strategic_show", month: "2026-08" });
    const response = appCommandResponse({ type: "strategic_show", month: "2026-08" });
    expect(response.answer).toContain("공식 월간 전략 브리핑");
    expect(response.answer).toContain("자동 생성하지 않아");
  });

  it("rejects official publication intent at the exploratory synthesis API boundary", () => {
    expect(isOfficialPublicationRequest({ publication_class: "official_editorial" })).toBe(true);
    expect(isOfficialPublicationRequest({ publication_mode: "editorial_curated" })).toBe(true);
    expect(isOfficialPublicationRequest({ publication_class: "exploratory_auto" })).toBe(false);
    expect(isOfficialPublicationRequest({ cards: RECENT })).toBe(false);
  });
});
