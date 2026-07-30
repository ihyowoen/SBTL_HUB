import fs from "node:fs";

function replaceExact(path, before, after) {
  const source = fs.readFileSync(path, "utf8");
  if (!source.includes(before)) {
    throw new Error(`Expected snippet not found in ${path}`);
  }
  fs.writeFileSync(path, source.replace(before, after));
}

replaceExact(
  "src/story/StoryNewsItem.jsx",
  `  const [imageOffset, setImageOffset] = useState(0);\n  const [imageLoaded, setImageLoaded] = useState(false);\n\n  useEffect(() => {\n    setImageOffset(0);\n    setImageLoaded(false);\n  }, [imageStartIndex, imageCategory, imagePool]);\n\n  const hasImageCandidate = imagePool.length > 0 && imageOffset < imagePool.length;\n  const imageSrc = hasImageCandidate\n    ? imagePool[(imageStartIndex + imageOffset) % imagePool.length]\n    : null;`,
  `  const [imageOffset, setImageOffset] = useState(0);\n  const [imageLoaded, setImageLoaded] = useState(false);\n  const imagePoolSignature = imagePool.join('\\u0001');\n  const primaryImageSrc = imagePool.length\n    ? imagePool[imageStartIndex % imagePool.length]\n    : null;\n\n  // 후보 체인의 실제 내용이 달라졌을 때만 첫 후보부터 다시 시도한다. 배열 identity만\n  // 바뀐 리렌더는 무시해 이미 로드된 동일 src를 투명 상태로 되돌리지 않는다.\n  useEffect(() => {\n    setImageOffset((current) => (current === 0 ? current : 0));\n  }, [primaryImageSrc, imagePoolSignature]);\n\n  const hasImageCandidate = imagePool.length > 0 && imageOffset < imagePool.length;\n  const imageSrc = hasImageCandidate\n    ? imagePool[(imageStartIndex + imageOffset) % imagePool.length]\n    : null;\n\n  // opacity 상태는 선택된 URL 자체가 바뀔 때만 초기화한다. 같은 src를 유지한 채 부모가\n  // 리렌더되면 브라우저가 load 이벤트를 다시 내지 않으므로 identity 기반 초기화는 금지한다.\n  useEffect(() => {\n    setImageLoaded(false);\n  }, [imageSrc]);`
);

replaceExact(
  "lib/chat/retrieve/safeHttp.js",
  `const DEFAULT_MAX_BYTES = 256 * 1024;\n`,
  `const DEFAULT_MAX_BYTES = 256 * 1024;\n\nfunction abortError(signal) {\n  if (signal?.reason instanceof Error) return signal.reason;\n  const error = new Error("The operation was aborted");\n  error.name = "AbortError";\n  return error;\n}\n\nfunction awaitWithAbort(promise, signal) {\n  if (!signal) return Promise.resolve(promise);\n  if (signal.aborted) return Promise.reject(abortError(signal));\n\n  return new Promise((resolve, reject) => {\n    const onAbort = () => reject(abortError(signal));\n    signal.addEventListener("abort", onAbort, { once: true });\n    Promise.resolve(promise).then(\n      (value) => {\n        signal.removeEventListener("abort", onAbort);\n        resolve(value);\n      },\n      (error) => {\n        signal.removeEventListener("abort", onAbort);\n        reject(error);\n      },\n    );\n  });\n}\n`
);

replaceExact(
  "lib/chat/retrieve/safeHttp.js",
  `export async function resolvePinnedAddress(hostname, lookupImpl = dnsLookup) {\n  const result = await lookupImpl(hostname, { all: true, verbatim: true });`,
  `export async function resolvePinnedAddress(hostname, lookupImpl = dnsLookup, signal = null) {\n  const lookupPromise = Promise.resolve().then(() => lookupImpl(hostname, { all: true, verbatim: true }));\n  const result = await awaitWithAbort(lookupPromise, signal);`
);

replaceExact(
  "lib/chat/retrieve/safeHttp.js",
  `  const pinned = await resolvePinnedAddress(url.hostname.replace(/\\.+$/, ""), options.dnsLookupImpl || dnsLookup);`,
  `  const pinned = await resolvePinnedAddress(\n    url.hostname.replace(/\\.+$/, ""),\n    options.dnsLookupImpl || dnsLookup,\n    options.signal,\n  );`
);

replaceExact(
  "__tests__/safeHttp.test.js",
  `  it("does not create a request when DNS resolves to a private address", async () => {\n    const dnsLookupImpl = vi.fn(async () => [{ address: "127.0.0.1", family: 4 }]);\n    const requestImpl = vi.fn();\n    await expect(requestHtmlPinned("https://news.example/article", { dnsLookupImpl, requestImpl })).resolves.toBeNull();\n    expect(requestImpl).not.toHaveBeenCalled();\n  });\n\n  it("supports all:true without releasing the pinned address", () => {`,
  `  it("does not create a request when DNS resolves to a private address", async () => {\n    const dnsLookupImpl = vi.fn(async () => [{ address: "127.0.0.1", family: 4 }]);\n    const requestImpl = vi.fn();\n    await expect(requestHtmlPinned("https://news.example/article", { dnsLookupImpl, requestImpl })).resolves.toBeNull();\n    expect(requestImpl).not.toHaveBeenCalled();\n  });\n\n  it("includes a stalled DNS lookup in the caller abort deadline", async () => {\n    const controller = new AbortController();\n    const dnsLookupImpl = vi.fn(() => new Promise(() => {}));\n    const requestImpl = vi.fn();\n    const pending = requestHtmlPinned("https://news.example/article", {\n      dnsLookupImpl,\n      requestImpl,\n      signal: controller.signal,\n    });\n\n    controller.abort();\n    await expect(pending).rejects.toMatchObject({ name: "AbortError" });\n    expect(requestImpl).not.toHaveBeenCalled();\n  });\n\n  it("supports all:true without releasing the pinned address", () => {`
);

for (const temp of [
  "scripts/address-review-4819086747.mjs",
  ".github/workflows/address-review-4819086747.yml",
]) {
  try { fs.unlinkSync(temp); } catch { /* noop */ }
}

console.log("Addressed review 4819086747");
