import { afterEach, describe, expect, it, vi } from "vitest";
import {
  __resetOgImageCacheForTests,
  enrichNewsWithOgImages,
  extractOgImageFromHtml,
  getOgImage,
  isSafePublicHttpUrl,
} from "../lib/chat/retrieve/ogExtractor.js";

afterEach(() => {
  __resetOgImageCacheForTests();
  vi.restoreAllMocks();
});

describe("OG image parser", () => {
  it("handles attribute order and relative URLs", () => {
    const html = '<head><meta content="/media/hero.jpg?x=1&amp;y=2" property="og:image"></head>';
    expect(extractOgImageFromHtml(html, "https://example.com/news/1")).toBe("https://example.com/media/hero.jpg?x=1&y=2");
  });

  it("prefers secure OG image and falls back to Twitter image", () => {
    const secure = '<meta property="og:image" content="http://cdn.example.com/a.jpg"><meta property="og:image:secure_url" content="https://cdn.example.com/a.jpg">';
    expect(extractOgImageFromHtml(secure, "https://example.com")).toBe("https://cdn.example.com/a.jpg");
    const twitter = "<meta name='twitter:image' content='//cdn.example.com/t.jpg'>";
    expect(extractOgImageFromHtml(twitter, "https://example.com")).toBe("https://cdn.example.com/t.jpg");
  });

  it("rejects private or credentialed image targets from article metadata", () => {
    const privateImage = '<meta property="og:image" content="http://127.0.0.1/admin.png">';
    const credentialedImage = '<meta property="og:image" content="https://user:pass@cdn.example.com/a.jpg">';
    expect(extractOgImageFromHtml(privateImage, "https://example.com")).toBeNull();
    expect(extractOgImageFromHtml(credentialedImage, "https://example.com")).toBeNull();
  });
});

describe("URL safety", () => {
  it.each([
    "http://localhost/a",
    "http://127.0.0.1/a",
    "http://10.0.0.1/a",
    "http://169.254.169.254/latest/meta-data",
    "http://192.168.0.1/a",
    "http://[::1]/a",
    "http://[::ffff:127.0.0.1]/a",
    "http://[::ffff:7f00:1]/a",
    "http://[::ffff:10.0.0.1]/a",
    "http://[64:ff9b::7f00:1]/a",
    "http://0x7f000001/a",
    "http://2130706433/a",
    "ftp://example.com/a",
    "https://user:pass@example.com/a",
    "https://example.com:8443/a",
  ])("rejects unsafe URL %s", (url) => {
    expect(isSafePublicHttpUrl(url)).toBe(false);
  });

  // IP 리터럴은 공인 대역이라도 클래스로 거부한다 — 사설 대역 열거는 WHATWG 정규화
  // 표기 변형(16진 IPv6 등)에 지므로, 실사용 0건(카드 전수)인 리터럴 자체를 닫는다.
  it.each([
    "http://1.2.3.4/a",
    "http://[2001:db8::1]/a",
  ])("rejects any IP-literal host even if public: %s", (url) => {
    expect(isSafePublicHttpUrl(url)).toBe(false);
  });

  it("accepts ordinary public HTTPS URLs", () => {
    expect(isSafePublicHttpUrl("https://www.reuters.com/world/example")).toBe(true);
  });
});

describe("network extraction", () => {
  it("follows a validated redirect and reads HTML only", async () => {
    const fetchImpl = vi.fn()
      .mockResolvedValueOnce(new Response(null, { status: 302, headers: { location: "https://example.com/final" } }))
      .mockResolvedValueOnce(new Response('<head><meta property="og:image" content="/hero.jpg"></head>', {
        status: 200,
        headers: { "content-type": "text/html; charset=utf-8" },
      }));
    await expect(getOgImage("https://example.com/start", { fetchImpl, timeoutMs: 500 })).resolves.toBe("https://example.com/hero.jpg");
    expect(fetchImpl).toHaveBeenCalledTimes(2);
  });

  it("does not fetch a private URL", async () => {
    const fetchImpl = vi.fn();
    await expect(getOgImage("http://127.0.0.1/private", { fetchImpl })).resolves.toBeNull();
    expect(fetchImpl).not.toHaveBeenCalled();
  });
});

describe("news enrichment trust boundary", () => {
  it("fetches only canonical server-loaded card URLs and deduplicates identical images", async () => {
    const fetchImpl = vi.fn(async () => new Response('<meta property="og:image" content="https://cdn.example.com/shared.jpg">', {
      status: 200,
      headers: { "content-type": "text/html" },
    }));
    const trustedCards = [
      { id: "a", url: "https://news.example.com/a" },
      { id: "b", url: "https://news.example.com/b" },
    ];
    const input = [
      ...trustedCards,
      { id: "evil", url: "http://127.0.0.1/admin", image: "https://tracker.example/pixel.gif" },
    ];
    const result = await enrichNewsWithOgImages(input, { trustedCards, fetchImpl, timeoutMs: 500 });
    expect(fetchImpl).toHaveBeenCalledTimes(2);
    expect(result.cards[0].image).toBe("https://cdn.example.com/shared.jpg");
    expect(result.cards[1].image).toBe("");
    expect(result.cards[2].image).toBe("");
    expect(result.meta).toMatchObject({ attempted: 2, found: 1, deduped: 1, skipped_untrusted: 1 });
  });
});
