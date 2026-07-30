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

// IP 리터럴 호스트는 전부 거부한다 — 사설 대역을 열거하면 표기 변형에 진다: WHATWG URL은
// 정수·16진·8진 IPv4를 점표기 사수로 정규화하지만(0x7f000001→127.0.0.1), IPv6는 대괄호
// 16진 압축형으로 정규화해([::ffff:127.0.0.1]→[::ffff:7f00:1]) 점표기 프리픽스 검사
// (::ffff:127. 류)가 매핑 주소를 통과시켰다(Codex #228 P1 — 리다이렉트 경유 루프백 도달).
// 뉴스 기사 URL에 IP 리터럴 호스트는 실측 0건(cards 1343장 전수)이라 거부 비용이 없고,
// 매핑(::ffff:)·NAT64(64:ff9b::)·ULA·링크로컬 등 전 계열이 표기와 무관하게 한 번에 닫힌다.
function isIpLiteralHost(hostname) {
  if (hostname.includes(":")) return true; // URL hostname의 콜론은 대괄호 IPv6 리터럴뿐
  return /^\d{1,3}(\.\d{1,3}){3}$/.test(hostname); // 정규화 후 IPv4 리터럴은 항상 점표기 사수
}

// 호스트는 '공개 FQDN처럼 생긴 것'만 허용한다(허용목록형 판정). 차단 이름 열거는 표기
// 변형에 진다: WHATWG 파서가 DNS 루트 점을 보존해 "localhost."이 localhost도 .localhost도
// 아니게 되고(Codex #228 R2 — 실측 통과 확인), 검색 도메인으로 해석되는 단일 라벨
// ("intranet", "metadata")도 같은 구멍이다. 그래서 ①끝점(루트 점) 제거 후 판정하고
// ②점 포함 + 알파벳 2자 이상 TLD를 요구한다 — 루프백·단일 라벨·숫자 TLD가 함께 닫힌다.
// 실측 비용 0: 카드 2872개 URL·고유 호스트 850개 전부 이 조건을 통과(끝점·점없음·비알파벳
// TLD·차단 접미 각 0건). .local/.internal/.localhost 접미 차단은 그대로 둔다.
const BLOCKED_HOST_SUFFIX = /\.(localhost|local|internal)$/;
const PUBLIC_FQDN = /^[a-z0-9-]+(\.[a-z0-9-]+)*\.[a-z]{2,}$/;

export function isSafePublicHttpUrl(value) {
  try {
    const url = new URL(String(value || "").trim());
    if (!["http:", "https:"].includes(url.protocol)) return false;
    if (url.username || url.password) return false;
    if (url.port && !["80", "443"].includes(url.port)) return false;
    // 루트 점 제거는 다른 모든 호스트 검사보다 먼저 — "localhost."·"svc.internal.."이
    // 접미·동치 비교를 빠져나가지 않게 한다.
    const host = url.hostname.toLowerCase().replace(/\.+$/, "");
    if (!host || host === "localhost" || BLOCKED_HOST_SUFFIX.test(host)) return false;
    if (isIpLiteralHost(host)) return false;
    if (!PUBLIC_FQDN.test(host)) return false;
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
    if (!isSafePublicHttpUrl(absolute.href)) return null;
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
