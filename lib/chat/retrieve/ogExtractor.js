// ============================================================================
// retrieve/ogExtractor.js — trusted news-card Open Graph image enrichment
// ============================================================================
// Server-side only. Client-supplied URLs are never fetched: callers must pass
// the canonical server-loaded card list, and only exact canonical article URLs
// are eligible. Failures are silent so the existing deterministic image pool
// remains the UI fallback.
// ============================================================================

const DEFAULT_TIMEOUT_MS = 1200;
const MAX_REDIRECTS = 3;
const MAX_HTML_BYTES = 256 * 1024;
const CACHE_TTL_MS = 6 * 60 * 60 * 1000;
const CACHE_MAX_ENTRIES = 200;
const ogImageCache = new Map();

function cacheGet(key) {
  const hit = ogImageCache.get(key);
  if (!hit) return undefined;
  if (Date.now() - hit.at > CACHE_TTL_MS) {
    ogImageCache.delete(key);
    return undefined;
  }
  ogImageCache.delete(key);
  ogImageCache.set(key, hit);
  return hit.value;
}

function cacheSet(key, value) {
  ogImageCache.delete(key);
  ogImageCache.set(key, { value, at: Date.now() });
  while (ogImageCache.size > CACHE_MAX_ENTRIES) {
    ogImageCache.delete(ogImageCache.keys().next().value);
  }
}

function isPrivateIpv4(hostname) {
  const parts = hostname.split(".");
  if (parts.length !== 4 || parts.some((part) => !/^\d{1,3}$/.test(part))) return false;
  const octets = parts.map(Number);
  if (octets.some((n) => n < 0 || n > 255)) return true;
  const [a, b, c] = octets;
  return a === 0
    || a === 10
    || a === 127
    || (a === 100 && b >= 64 && b <= 127)
    || (a === 169 && b === 254)
    || (a === 172 && b >= 16 && b <= 31)
    || (a === 192 && b === 0 && c === 0)
    || (a === 192 && b === 0 && c === 2)
    || (a === 192 && b === 168)
    || (a === 198 && (b === 18 || b === 19))
    || (a === 198 && b === 51 && c === 100)
    || (a === 203 && b === 0 && c === 113)
    || a >= 224;
}

function isPrivateIpv6(hostname) {
  const host = hostname.replace(/^\[|\]$/g, "").toLowerCase();
  return host === "::"
    || host === "::1"
    || host.startsWith("fc")
    || host.startsWith("fd")
    || /^fe[89ab]/.test(host)
    || host.startsWith("::ffff:127.")
    || host.startsWith("::ffff:10.")
    || host.startsWith("::ffff:192.168.");
}

export function isSafePublicHttpUrl(value) {
  try {
    const url = new URL(String(value || "").trim());
    if (!["http:", "https:"].includes(url.protocol)) return false;
    if (url.username || url.password) return false;
    if (url.port && !["80", "443"].includes(url.port)) return false;
    const host = url.hostname.toLowerCase();
    if (!host || host === "localhost" || host.endsWith(".localhost") || host.endsWith(".local") || host.endsWith(".internal")) return false;
    if (isPrivateIpv4(host) || isPrivateIpv6(host)) return false;
    return true;
  } catch {
    return false;
  }
}

function decodeHtmlEntities(value) {
  return String(value || "")
    .replace(/&amp;/gi, "&")
    .replace(/&quot;/gi, "\"")
    .replace(/&#39;|&apos;/gi, "'")
    .replace(/&#x([0-9a-f]+);/gi, (_, hex) => String.fromCodePoint(Number.parseInt(hex, 16)))
    .replace(/&#(\d+);/g, (_, dec) => String.fromCodePoint(Number.parseInt(dec, 10)));
}

function parseAttributes(tag) {
  const attrs = {};
  const re = /([^\s=/>]+)\s*=\s*(?:"([^"]*)"|'([^']*)'|([^\s"'=<>`]+))/g;
  let match;
  while ((match = re.exec(tag))) {
    attrs[String(match[1]).toLowerCase()] = decodeHtmlEntities(match[2] ?? match[3] ?? match[4] ?? "");
  }
  return attrs;
}

export function extractOgImageFromHtml(html, pageUrl) {
  if (!html || !pageUrl) return null;
  const candidates = new Map();
  for (const tag of String(html).match(/<meta\b[^>]*>/gi) || []) {
    const attrs = parseAttributes(tag);
    const key = String(attrs.property || attrs.name || attrs.itemprop || "").toLowerCase();
    const content = String(attrs.content || "").trim();
    if (!key || !content || candidates.has(key)) continue;
    candidates.set(key, content);
  }

  const raw = candidates.get("og:image:secure_url")
    || candidates.get("og:image")
    || candidates.get("og:image:url")
    || candidates.get("twitter:image")
    || candidates.get("twitter:image:src");
  if (!raw) return null;

  try {
    const absolute = new URL(raw, pageUrl);
    if (!["http:", "https:"].includes(absolute.protocol) || absolute.username || absolute.password) return null;
    return absolute.href;
  } catch {
    return null;
  }
}

async function readHtmlHead(response, maxBytes = MAX_HTML_BYTES) {
  if (!response.body || typeof response.body.getReader !== "function") {
    return (await response.text()).slice(0, maxBytes);
  }
  const reader = response.body.getReader();
  const decoder = new TextDecoder();
  let out = "";
  let bytes = 0;
  try {
    while (bytes < maxBytes) {
      const { value, done } = await reader.read();
      if (done) break;
      bytes += value.byteLength;
      out += decoder.decode(value, { stream: true });
      if (/<\/head\s*>/i.test(out)) break;
    }
    out += decoder.decode();
  } finally {
    try { await reader.cancel(); } catch { /* noop */ }
  }
  return out.slice(0, maxBytes);
}

async function fetchHtmlWithRedirects(articleUrl, { fetchImpl, signal }) {
  let current = articleUrl;
  for (let redirects = 0; redirects <= MAX_REDIRECTS; redirects += 1) {
    if (!isSafePublicHttpUrl(current)) return null;
    const response = await fetchImpl(current, {
      headers: {
        "User-Agent": "Mozilla/5.0 (compatible; SBTLHub/1.0; +https://github.com/ihyowoen/SBTL_HUB)",
        Accept: "text/html,application/xhtml+xml;q=0.9",
      },
      redirect: "manual",
      signal,
    });

    if (response.status >= 300 && response.status < 400) {
      const location = response.headers.get("location");
      if (!location || redirects === MAX_REDIRECTS) return null;
      current = new URL(location, current).href;
      continue;
    }
    if (!response.ok) return null;
    const contentType = String(response.headers.get("content-type") || "").toLowerCase();
    if (contentType && !contentType.includes("text/html") && !contentType.includes("application/xhtml+xml")) return null;
    return { html: await readHtmlHead(response), finalUrl: response.url || current };
  }
  return null;
}

export async function getOgImage(articleUrl, options = {}) {
  if (!isSafePublicHttpUrl(articleUrl)) return null;
  const cached = cacheGet(articleUrl);
  if (cached !== undefined) return cached;

  const fetchImpl = options.fetchImpl || globalThis.fetch;
  if (typeof fetchImpl !== "function") return null;
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), Number(options.timeoutMs) || DEFAULT_TIMEOUT_MS);
  try {
    const page = await fetchHtmlWithRedirects(articleUrl, { fetchImpl, signal: controller.signal });
    const image = page ? extractOgImageFromHtml(page.html, page.finalUrl) : null;
    cacheSet(articleUrl, image);
    return image;
  } catch {
    cacheSet(articleUrl, null);
    return null;
  } finally {
    clearTimeout(timeoutId);
  }
}

function canonicalArticleUrl(card) {
  return card?.url || card?.primaryUrl || card?.primary_url || (Array.isArray(card?.urls) ? card.urls[0] : "") || "";
}

export async function enrichNewsWithOgImages(newsItems = [], options = {}) {
  const startedAt = Date.now();
  if (!Array.isArray(newsItems) || newsItems.length === 0) {
    return { cards: [], meta: { attempted: 0, found: 0, deduped: 0, skipped_untrusted: 0, latency_ms: 0 } };
  }

  const trustedUrls = new Set((options.trustedCards || []).map(canonicalArticleUrl).filter(isSafePublicHttpUrl));
  const uniqueUrls = [...new Set(newsItems.map(canonicalArticleUrl).filter((url) => trustedUrls.has(url)))];
  const results = await Promise.allSettled(uniqueUrls.map(async (url) => [url, await getOgImage(url, options)]));
  const imageByArticle = new Map();
  results.forEach((result) => {
    if (result.status === "fulfilled") imageByArticle.set(result.value[0], result.value[1]);
  });

  const usedImages = new Set();
  let found = 0;
  let deduped = 0;
  let skippedUntrusted = 0;
  const cards = newsItems.map((item) => {
    const articleUrl = canonicalArticleUrl(item);
    if (!trustedUrls.has(articleUrl)) {
      skippedUntrusted += articleUrl ? 1 : 0;
      return { ...item, image: "" };
    }
    const image = imageByArticle.get(articleUrl) || "";
    if (!image) return { ...item, image: "" };
    if (usedImages.has(image)) {
      deduped += 1;
      return { ...item, image: "" };
    }
    usedImages.add(image);
    found += 1;
    return { ...item, image };
  });

  return {
    cards,
    meta: {
      attempted: uniqueUrls.length,
      found,
      deduped,
      skipped_untrusted: skippedUntrusted,
      latency_ms: Date.now() - startedAt,
    },
  };
}

export function __resetOgImageCacheForTests() {
  ogImageCache.clear();
}
