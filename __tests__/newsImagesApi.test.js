import { beforeEach, describe, expect, it, vi } from "vitest";

const loadKnowledge = vi.fn();
const enrichNewsWithOgImages = vi.fn();

vi.mock("../lib/chat/common.js", () => ({ loadKnowledge }));
vi.mock("../lib/chat/retrieve/ogExtractor.js", () => ({ enrichNewsWithOgImages }));

const { default: handler, getArticleImageKey } = await import("../api/news-images.js");

function makeResponse() {
  const result = { statusCode: 200, body: null, headers: {} };
  return {
    result,
    setHeader(name, value) { result.headers[name] = value; },
    status(code) { result.statusCode = code; return this; },
    json(body) { result.body = body; return this; },
    end() { return this; },
  };
}

describe("news image API", () => {
  beforeEach(() => {
    loadKnowledge.mockReset();
    enrichNewsWithOgImages.mockReset();
  });

  it("uses id first and canonical URL as fallback key", () => {
    expect(getArticleImageKey({ id: "card-1", url: "https://example.com/a" })).toBe("card-1");
    expect(getArticleImageKey({ urls: ["https://example.com/a"] })).toBe("https://example.com/a");
  });

  it("matches only server-loaded cards before enrichment", async () => {
    const canonical = [
      { id: "card-1", url: "https://news.example/a" },
      { id: "card-2", url: "https://news.example/b" },
    ];
    loadKnowledge.mockResolvedValue({ cards: canonical });
    enrichNewsWithOgImages.mockResolvedValue({
      cards: [{ ...canonical[0], image: "https://cdn.example/a.jpg" }],
      meta: { attempted: 1, found: 1, deduped: 0, skipped_untrusted: 0, latency_ms: 2 },
    });
    const res = makeResponse();
    await handler({ method: "POST", body: { keys: ["card-1", "not-a-card"] } }, res);

    expect(enrichNewsWithOgImages).toHaveBeenCalledWith([canonical[0]], { trustedCards: canonical });
    expect(res.result.statusCode).toBe(200);
    expect(res.result.body.images).toEqual({ "card-1": "https://cdn.example/a.jpg" });
    expect(res.result.body.meta).toMatchObject({ requested: 2, matched: 1, found: 1 });
  });

  it("does not accept arbitrary URLs that are absent from canonical cards", async () => {
    loadKnowledge.mockResolvedValue({ cards: [] });
    enrichNewsWithOgImages.mockResolvedValue({ cards: [], meta: { attempted: 0, found: 0, deduped: 0, skipped_untrusted: 0, latency_ms: 0 } });
    const res = makeResponse();
    await handler({ method: "POST", body: { keys: ["http://127.0.0.1/admin"] } }, res);

    expect(enrichNewsWithOgImages).toHaveBeenCalledWith([], { trustedCards: [] });
    expect(res.result.body.images).toEqual({});
    expect(res.result.body.meta.matched).toBe(0);
  });
});
