import fs from "node:fs";

function replaceOnce(file, before, after) {
  const current = fs.readFileSync(file, "utf8");
  if (current.includes(after)) return;
  const first = current.indexOf(before);
  if (first < 0) throw new Error(`Expected snippet not found in ${file}`);
  if (current.indexOf(before, first + before.length) >= 0) throw new Error(`Snippet is not unique in ${file}`);
  fs.writeFileSync(file, current.slice(0, first) + after + current.slice(first + before.length));
}

const extractor = "lib/chat/retrieve/ogExtractor.js";
const importLine = 'import { requestHtmlPinned } from "./safeHttp.js";\n\n';
const extractorSource = fs.readFileSync(extractor, "utf8");
if (!extractorSource.startsWith(importLine)) {
  fs.writeFileSync(extractor, importLine + extractorSource);
}

replaceOnce(
  extractor,
  `async function fetchHtmlWithRedirects(articleUrl, { fetchImpl, signal }) {
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
}`,
  `async function fetchHtmlWithRedirects(articleUrl, { fetchImpl, signal, dnsLookupImpl, requestImpl }) {
  let current = articleUrl;
  for (let redirects = 0; redirects <= MAX_REDIRECTS; redirects += 1) {
    if (!isSafePublicHttpUrl(current)) return null;
    const response = fetchImpl
      ? await fetchImpl(current, {
          headers: {
            "User-Agent": "Mozilla/5.0 (compatible; SBTLHub/1.0; +https://github.com/ihyowoen/SBTL_HUB)",
            Accept: "text/html,application/xhtml+xml;q=0.9",
          },
          redirect: "manual",
          signal,
        })
      : await requestHtmlPinned(current, {
          signal,
          dnsLookupImpl,
          requestImpl,
          maxBytes: MAX_HTML_BYTES,
        });
    if (!response) return null;

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
}`,
);

replaceOnce(
  extractor,
  `export async function getOgImage(articleUrl, options = {}) {
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
}`,
  `export async function getOgImage(articleUrl, options = {}) {
  if (!isSafePublicHttpUrl(articleUrl)) return null;
  const cached = cacheGet(articleUrl);
  if (cached !== undefined) return cached;

  const fetchImpl = options.fetchImpl || null;
  if (fetchImpl !== null && typeof fetchImpl !== "function") return null;
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), Number(options.timeoutMs) || DEFAULT_TIMEOUT_MS);
  try {
    const page = await fetchHtmlWithRedirects(articleUrl, {
      fetchImpl,
      signal: controller.signal,
      dnsLookupImpl: options.dnsLookupImpl,
      requestImpl: options.requestImpl,
    });
    const image = page ? extractOgImageFromHtml(page.html, page.finalUrl) : null;
    cacheSet(articleUrl, image);
    return image;
  } catch {
    cacheSet(articleUrl, null);
    return null;
  } finally {
    clearTimeout(timeoutId);
  }
}`,
);

const testFile = "__tests__/ogExtractor.test.js";
const testMarker = `  it("does not fetch a private URL", async () => {`;
const redirectTest = `  it("re-resolves every redirect and blocks a private DNS target", async () => {
    const dnsLookupImpl = vi.fn(async (hostname) => hostname === "example.com"
      ? [{ address: "93.184.216.34", family: 4 }]
      : [{ address: "127.0.0.1", family: 4 }]);
    const requestImpl = vi.fn((url, options, onResponse) => {
      options.lookup(url.hostname, {}, (error, address, family) => {
        expect(error).toBeNull();
        expect(address).toBe("93.184.216.34");
        expect(family).toBe(4);
      });
      const response = {
        statusCode: 302,
        headers: { location: "https://rebinding.example/final" },
        resume: vi.fn(),
      };
      queueMicrotask(() => onResponse(response));
      const request = {
        on: vi.fn(() => request),
        end: vi.fn(),
      };
      return request;
    });

    await expect(getOgImage("https://example.com/start", {
      dnsLookupImpl,
      requestImpl,
      timeoutMs: 500,
    })).resolves.toBeNull();
    expect(dnsLookupImpl).toHaveBeenCalledTimes(2);
    expect(requestImpl).toHaveBeenCalledTimes(1);
  });

`;
const tests = fs.readFileSync(testFile, "utf8");
if (!tests.includes(redirectTest)) {
  replaceOnce(testFile, testMarker, redirectTest + testMarker);
}

for (const temp of ["scripts/apply-dns-pinning-patch.mjs", ".github/workflows/apply-dns-pinning-patch.yml"]) {
  try { fs.unlinkSync(temp); } catch { /* noop */ }
}

console.log("DNS pinning patch applied");
