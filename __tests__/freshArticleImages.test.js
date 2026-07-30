import { describe, expect, it } from "vitest";
import {
  ARTICLE_IMAGE_BATCH_SIZE,
  chunkArticleImageKeys,
  clearAttemptedArticleImageKeys,
  getArticleImageMonth,
  mergeUniqueArticleImages,
  selectArticleImageKeys,
} from "../src/story/useFreshArticleImages.js";

describe("July article-image scope", () => {
  it.each([
    [{ date: "2026.07.30" }, "2026-07"],
    [{ d: "2026-07-01" }, "2026-07"],
    [{ date: "2026/07/15" }, "2026-07"],
    [{ date: "2026.06.30" }, "2026-06"],
    [{ date: "" }, ""],
  ])("normalizes a card month", (card, expected) => {
    expect(getArticleImageMonth(card)).toBe(expected);
  });

  it("selects every unique July card with a canonical URL and excludes other months", () => {
    const cards = [
      { id: "jul-1", date: "2026.07.30", url: "https://news.example.com/1" },
      { id: "jun-1", date: "2026.06.30", url: "https://news.example.com/2" },
      { id: "jul-2", d: "2026-07-02", urls: ["https://news.example.com/3"] },
      { id: "jul-1", date: "2026.07.30", url: "https://news.example.com/1" },
      { id: "jul-no-url", date: "2026.07.12" },
    ];

    expect(selectArticleImageKeys(cards, { month: "2026-07" })).toEqual(["jul-1", "jul-2"]);
  });

  it("keeps the legacy numeric limit compatible", () => {
    const cards = Array.from({ length: 25 }, (_, index) => ({
      id: `card-${index}`,
      date: "2026.07.01",
      url: `https://news.example.com/${index}`,
    }));
    expect(selectArticleImageKeys(cards, 18)).toHaveLength(18);
  });

  it("splits July keys into API-safe batches", () => {
    const keys = Array.from({ length: 41 }, (_, index) => `card-${index}`);
    const chunks = chunkArticleImageKeys(keys);
    expect(chunks.map((chunk) => chunk.length)).toEqual([ARTICLE_IMAGE_BATCH_SIZE, ARTICLE_IMAGE_BATCH_SIZE, 5]);
    expect(chunks.flat()).toEqual(keys);
  });

  it("deduplicates publisher-default images across separate API batches", () => {
    const current = { "card-1": "https://cdn.example.com/default.jpg" };
    const incoming = {
      "card-2": "https://cdn.example.com/default.jpg",
      "card-3": "https://cdn.example.com/unique.jpg",
      "card-4": "https://cdn.example.com/unique.jpg",
    };

    expect(mergeUniqueArticleImages(current, incoming)).toEqual({
      "card-1": "https://cdn.example.com/default.jpg",
      "card-3": "https://cdn.example.com/unique.jpg",
    });
  });

  it("releases in-flight attempt marks synchronously for a replacement effect", () => {
    const attempted = new Set(["overlap", "old-only"]);
    clearAttemptedArticleImageKeys(attempted, new Set(["overlap"]));
    expect([...attempted]).toEqual(["old-only"]);
  });
});
