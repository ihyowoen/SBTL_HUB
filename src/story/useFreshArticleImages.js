import { useEffect, useMemo, useRef, useState } from "react";

const SESSION_KEY = "sbtl_article_images_v1";
export const ARTICLE_IMAGE_BATCH_SIZE = 18;

export function getArticleImageKey(card) {
  if (!card || typeof card !== "object") return "";
  const primaryUrl = card.primaryUrl || card.primary_url || (Array.isArray(card.urls) ? card.urls[0] : "") || card.url || "";
  return String(card.id || card.news_id || primaryUrl || "");
}

export function getArticleImageMonth(card) {
  const raw = String(card?.date || card?.d || "").trim();
  const match = raw.match(/^(\d{4})[./-](\d{2})/);
  return match ? `${match[1]}-${match[2]}` : "";
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

  const signature = selected.join("\u001f");

  useEffect(() => {
    if (!selected.length) return undefined;
    const missing = selected.filter((key) => !images[key] && !attemptedRef.current.has(key));
    if (!missing.length) return undefined;

    const controller = new AbortController();
    let active = true;

    (async () => {
      for (const batch of chunkArticleImageKeys(missing)) {
        if (!active || controller.signal.aborted) break;
        batch.forEach((key) => attemptedRef.current.add(key));
        try {
          const response = await fetch("/api/news-images", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ keys: batch }),
            signal: controller.signal,
          });
          if (!response.ok) throw new Error(`HTTP ${response.status}`);
          const payload = await response.json();
          const next = payload?.images && typeof payload.images === "object" ? payload.images : null;
          if (!active || !next || !Object.keys(next).length) continue;
          setImages((current) => {
            const merged = { ...current, ...next };
            writeSessionCache(merged);
            return merged;
          });
        } catch (error) {
          if (error?.name === "AbortError") {
            batch.forEach((key) => attemptedRef.current.delete(key));
            break;
          }
          batch.forEach((key) => attemptedRef.current.delete(key));
          console.warn(`[feed-images] ${error?.message || error}`);
        }
      }
    })();

    return () => {
      active = false;
      controller.abort();
    };
    // images is intentionally omitted: one signature run processes every missing key in bounded batches.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [signature]);

  return images;
}
