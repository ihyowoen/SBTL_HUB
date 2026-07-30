import { useEffect, useMemo, useRef, useState } from "react";

const SESSION_KEY = "sbtl_article_images_v1";

export function getArticleImageKey(card) {
  if (!card || typeof card !== "object") return "";
  const primaryUrl = card.primaryUrl || card.primary_url || (Array.isArray(card.urls) ? card.urls[0] : "") || card.url || "";
  return String(card.id || card.news_id || primaryUrl || "");
}

function readSessionCache() {
  try {
    const value = JSON.parse(sessionStorage.getItem(SESSION_KEY) || "{}");
    return value && typeof value === "object" && !Array.isArray(value) ? value : {};
  } catch {
    return {};
  }
}

function writeSessionCache(images) {
  try { sessionStorage.setItem(SESSION_KEY, JSON.stringify(images)); } catch { /* storage unavailable */ }
}

export function useFreshArticleImages(cards = [], limit = 18) {
  const [images, setImages] = useState(readSessionCache);
  const attemptedRef = useRef(new Set());

  const selected = useMemo(() => {
    const out = [];
    const seen = new Set();
    for (const card of Array.isArray(cards) ? cards : []) {
      const key = getArticleImageKey(card);
      const url = card?.primaryUrl || card?.primary_url || (Array.isArray(card?.urls) ? card.urls[0] : "") || card?.url || "";
      if (!key || !url || seen.has(key)) continue;
      seen.add(key);
      out.push(key);
      if (out.length >= limit) break;
    }
    return out;
  }, [cards, limit]);

  const signature = selected.join("\u001f");

  useEffect(() => {
    if (!selected.length) return undefined;
    const missing = selected.filter((key) => !images[key] && !attemptedRef.current.has(key));
    if (!missing.length) return undefined;
    missing.forEach((key) => attemptedRef.current.add(key));

    const controller = new AbortController();
    fetch("/api/news-images", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ keys: missing }),
      signal: controller.signal,
    })
      .then((response) => response.ok ? response.json() : null)
      .then((payload) => {
        const next = payload?.images && typeof payload.images === "object" ? payload.images : null;
        if (!next || !Object.keys(next).length) return;
        setImages((current) => {
          const merged = { ...current, ...next };
          writeSessionCache(merged);
          return merged;
        });
      })
      .catch((error) => {
        if (error?.name !== "AbortError") console.warn(`[feed-images] ${error?.message || error}`);
      });

    return () => controller.abort();
    // `images` is intentionally included so a successful partial response can request any remaining keys once.
  }, [signature, images]);

  return images;
}
