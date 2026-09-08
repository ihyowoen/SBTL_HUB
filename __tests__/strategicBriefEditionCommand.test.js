import { describe, expect, it } from "vitest";
import { detectAppCommand } from "../lib/chat/appCommand.js";

const opts = { cards: [], watchTerms: [], lastBriefAt: 0, lastMonthlyBriefAt: 0 };

describe("official Strategic Brief edition command", () => {
  it("preserves VOL.10 when followed by natural whitespace", () => {
    expect(detectAppCommand("VOL.10 전략 브리핑 보여줘", [], opts)).toEqual({
      type: "strategic_show",
      edition: "VOL.10",
    });
  });

  it("preserves VOL. 10 with internal whitespace", () => {
    expect(detectAppCommand("VOL. 10 전략 브리핑 보여줘", [], opts)).toEqual({
      type: "strategic_show",
      edition: "VOL.10",
    });
  });
});
