import { loadKnowledge } from "../lib/chat/common.js";
import { enrichNewsWithOgImages } from "../lib/chat/retrieve/ogExtractor.js";

const MAX_KEYS = 18;

function setCors(res) {
  res.setHeader("Access-Control-Allow-Origin", "*");
  res.setHeader("Access-Control-Allow-Methods", "POST, OPTIONS");
  res.setHeader("Access-Control-Allow-Headers", "Content-Type");
}

export function getArticleImageKey(card) {
  if (!card || typeof card !== "object") return "";
  const primaryUrl = card.primaryUrl || card.primary_url || (Array.isArray(card.urls) ? card.urls[0] : "") || card.url || "";
  return String(card.id || card.news_id || primaryUrl || "");
}

export default async function handler(req, res) {
  setCors(res);
  if (req.method === "OPTIONS") return res.status(204).end();
  if (req.method !== "POST") return res.status(405).json({ ok: false, error: "method_not_allowed", images: {} });

  const requested = Array.isArray(req.body?.keys)
    ? req.body.keys.map((value) => String(value || "").trim()).filter(Boolean).slice(0, MAX_KEYS)
    : [];
  if (!requested.length) return res.status(200).json({ ok: true, images: {}, meta: { requested: 0, matched: 0, found: 0 } });

  try {
    const data = await loadKnowledge();
    const canonicalCards = Array.isArray(data.cards) ? data.cards : [];
    const byKey = new Map();
    canonicalCards.forEach((card) => {
      const key = getArticleImageKey(card);
      if (key && !byKey.has(key)) byKey.set(key, card);
    });

    const selected = requested.map((key) => byKey.get(key)).filter(Boolean);
    const result = await enrichNewsWithOgImages(selected, { trustedCards: canonicalCards });
    const images = {};
    result.cards.forEach((card) => {
      const key = getArticleImageKey(card);
      if (key && card.image) images[key] = card.image;
    });

    res.setHeader("Cache-Control", "private, max-age=0, must-revalidate");
    return res.status(200).json({
      ok: true,
      images,
      meta: {
        requested: requested.length,
        matched: selected.length,
        found: Object.keys(images).length,
        ...result.meta,
      },
    });
  } catch (error) {
    console.error(`[news-images] ${error?.message || error}`);
    return res.status(200).json({ ok: false, error: "image_enrichment_failed", images: {} });
  }
}
