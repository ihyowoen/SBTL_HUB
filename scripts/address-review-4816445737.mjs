import fs from "node:fs";

const hookPath = "src/story/useFreshArticleImages.js";
const testPath = "__tests__/freshArticleImages.test.js";
const chatPath = "api/chat.js";

const hook = `import { useEffect, useMemo, useRef, useState } from "react";

const SESSION_KEY = "sbtl_article_images_v1";
export const ARTICLE_IMAGE_BATCH_SIZE = 18;

export function getArticleImageKey(card) {
  if (!card || typeof card !== "object") return "";
  const primaryUrl = card.primaryUrl || card.primary_url || (Array.isArray(card.urls) ? card.urls[0] : "") || card.url || "";
  return String(card.id || card.news_id || primaryUrl || "");
}

export function getArticleImageMonth(card) {
  const raw = String(card?.date || card?.d || "").trim();
  const match = raw.match(/^(\\d{4})[./-](\\d{2})/);
  return match ? \`${"${match[1]}-${match[2]}"}\` : "";
}

export function selectArticleImageKeys(cards = [], options = {}) {
  const normalizedOptions = typeof options === "number" ? { limit: options } : (options || {});
  const month = String(normalizedOptions.month || "").trim();
  const parsedLimit = Number(normalizedOptions.limit);
  const limit = Number.isFinite(parsedLimit) && parsedLimit > 0 ? Math.floor(parsedLimit) : Number.POSITIVE_INFINITY;
  const out = [];
  const seen = new Set();

  for (const card of Array.isArray(cards) ? cards : []) {
    if (month && getArticleImageMonth(card) !== month) continue;
    const key = getArticleImageKey(card);
    const url = card?.primaryUrl || card?.primary_url || (Array.isArray(card?.urls) ? card.urls[0] : "") || card?.url || "";
    if (!key || !url || seen.has(key)) continue;
    seen.add(key);
    out.push(key);
    if (out.length >= limit) break;
  }

  return out;
}

export function chunkArticleImageKeys(keys = [], size = ARTICLE_IMAGE_BATCH_SIZE) {
  const batchSize = Number.isFinite(Number(size)) && Number(size) > 0 ? Math.floor(Number(size)) : ARTICLE_IMAGE_BATCH_SIZE;
  const chunks = [];
  for (let index = 0; index < keys.length; index += batchSize) {
    chunks.push(keys.slice(index, index + batchSize));
  }
  return chunks;
}

export function mergeUniqueArticleImages(current = {}, incoming = {}) {
  const merged = { ...(current && typeof current === "object" ? current : {}) };
  const usedUrls = new Set(
    Object.values(merged)
      .map((value) => String(value || "").trim())
      .filter(Boolean),
  );

  for (const [rawKey, rawUrl] of Object.entries(incoming && typeof incoming === "object" ? incoming : {})) {
    const key = String(rawKey || "").trim();
    const url = String(rawUrl || "").trim();
    if (!key || !url || merged[key] || usedUrls.has(url)) continue;
    merged[key] = url;
    usedUrls.add(url);
  }

  return merged;
}

export function clearAttemptedArticleImageKeys(attempted, keys = []) {
  if (!attempted || typeof attempted.delete !== "function") return;
  for (const key of keys) attempted.delete(key);
}

function readSessionCache() {
  try {
    const value = JSON.parse(sessionStorage.getItem(SESSION_KEY) || "{}");
    return value && typeof value === "object" && !Array.isArray(value)
      ? mergeUniqueArticleImages({}, value)
      : {};
  } catch {
    return {};
  }
}

function writeSessionCache(images) {
  try { sessionStorage.setItem(SESSION_KEY, JSON.stringify(images)); } catch { /* storage unavailable */ }
}

export function useFreshArticleImages(cards = [], options = {}) {
  const [images, setImages] = useState(readSessionCache);
  const attemptedRef = useRef(new Set());
  const normalizedOptions = typeof options === "number" ? { limit: options } : (options || {});
  const month = String(normalizedOptions.month || "").trim();
  const limit = normalizedOptions.limit;

  const selected = useMemo(
    () => selectArticleImageKeys(cards, { month, limit }),
    [cards, month, limit],
  );

  const signature = selected.join("\\u001f");

  useEffect(() => {
    if (!selected.length) return undefined;
    const missing = selected.filter((key) => !images[key] && !attemptedRef.current.has(key));
    if (!missing.length) return undefined;

    const controller = new AbortController();
    const inFlightKeys = new Set();
    let active = true;

    (async () => {
      for (const batch of chunkArticleImageKeys(missing)) {
        if (!active || controller.signal.aborted) break;
        batch.forEach((key) => {
          attemptedRef.current.add(key);
          inFlightKeys.add(key);
        });
        try {
          const response = await fetch("/api/news-images", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ keys: batch }),
            signal: controller.signal,
          });
          if (!response.ok) throw new Error(\`HTTP ${"${response.status}"}\`);
          const payload = await response.json();
          const next = payload?.images && typeof payload.images === "object" ? payload.images : null;
          if (!active || !next || !Object.keys(next).length) continue;
          setImages((current) => {
            const merged = mergeUniqueArticleImages(current, next);
            writeSessionCache(merged);
            return merged;
          });
        } catch (error) {
          clearAttemptedArticleImageKeys(attemptedRef.current, batch);
          if (error?.name === "AbortError") break;
          console.warn(\`[feed-images] ${"${error?.message || error}"}\`);
        } finally {
          clearAttemptedArticleImageKeys(inFlightKeys, batch);
        }
      }
    })();

    return () => {
      active = false;
      // React runs cleanup before the replacement effect. Release pending keys synchronously
      // so overlapping cards remain eligible in that immediately-following effect.
      clearAttemptedArticleImageKeys(attemptedRef.current, inFlightKeys);
      inFlightKeys.clear();
      controller.abort();
    };
    // images is intentionally omitted: one signature run processes every missing key in bounded batches.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [signature]);

  return images;
}
`;

const tests = `import { describe, expect, it } from "vitest";
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
      id: \`card-${"${index}"}\`,
      date: "2026.07.01",
      url: \`https://news.example.com/${"${index}"}\`,
    }));
    expect(selectArticleImageKeys(cards, 18)).toHaveLength(18);
  });

  it("splits July keys into API-safe batches", () => {
    const keys = Array.from({ length: 41 }, (_, index) => \`card-${"${index}"}\`);
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
`;

fs.writeFileSync(hookPath, hook);
fs.writeFileSync(testPath, tests);

let chat = fs.readFileSync(chatPath, "utf8");
const before = 'const ogImageTask = parsed.topic === "news" && (retrieval.cards || []).length';
const after = 'const ogImageTask = parsed.topic === "news" && parsed.action !== "analyze_card" && (retrieval.cards || []).length';
if (!chat.includes(before)) throw new Error("Expected OG task condition not found in api/chat.js");
chat = chat.replace(before, after);
fs.writeFileSync(chatPath, chat);

for (const temp of [
  "scripts/address-review-4816445737.mjs",
  ".github/workflows/address-review-4816445737.yml",
]) {
  try { fs.unlinkSync(temp); } catch { /* noop */ }
}

console.log("Addressed Codex review 4816445737");
