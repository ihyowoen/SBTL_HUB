import { lookup as dnsLookup } from "node:dns/promises";
import http from "node:http";
import https from "node:https";
import { isIP } from "node:net";

const DEFAULT_MAX_BYTES = 256 * 1024;

function abortError(signal) {
  if (signal?.reason instanceof Error) return signal.reason;
  const error = new Error("The operation was aborted");
  error.name = "AbortError";
  return error;
}

function awaitWithAbort(promise, signal) {
  if (!signal) return Promise.resolve(promise);
  if (signal.aborted) return Promise.reject(abortError(signal));

  return new Promise((resolve, reject) => {
    const onAbort = () => reject(abortError(signal));
    signal.addEventListener("abort", onAbort, { once: true });
    Promise.resolve(promise).then(
      (value) => {
        signal.removeEventListener("abort", onAbort);
        resolve(value);
      },
      (error) => {
        signal.removeEventListener("abort", onAbort);
        reject(error);
      },
    );
  });
}

function ipv4ToInt(address) {
  const parts = String(address).split(".").map(Number);
  if (parts.length !== 4 || parts.some((n) => !Number.isInteger(n) || n < 0 || n > 255)) return null;
  return (((parts[0] << 24) >>> 0) + (parts[1] << 16) + (parts[2] << 8) + parts[3]) >>> 0;
}

function inCidr4(value, base, prefix) {
  const mask = prefix === 0 ? 0 : (0xffffffff << (32 - prefix)) >>> 0;
  return (value & mask) === (base & mask);
}

function isPublicIpv4(address) {
  const value = ipv4ToInt(address);
  if (value === null) return false;
  const blocked = [
    ["0.0.0.0", 8],
    ["10.0.0.0", 8],
    ["100.64.0.0", 10],
    ["127.0.0.0", 8],
    ["169.254.0.0", 16],
    ["172.16.0.0", 12],
    ["192.0.0.0", 24],
    ["192.0.2.0", 24],
    ["192.88.99.0", 24],
    ["192.168.0.0", 16],
    ["198.18.0.0", 15],
    ["198.51.100.0", 24],
    ["203.0.113.0", 24],
    ["224.0.0.0", 4],
    ["240.0.0.0", 4],
  ];
  return !blocked.some(([base, prefix]) => inCidr4(value, ipv4ToInt(base), prefix));
}

function isPublicIpv6(address) {
  const normalized = String(address || "").toLowerCase().split("%")[0];
  const firstToken = normalized.split(":")[0] || "0";
  const first = Number.parseInt(firstToken, 16);
  if (!Number.isInteger(first) || first < 0x2000 || first > 0x3fff) return false;
  if (/^2001:0*:/.test(normalized)) return false;
  if (/^2001:0*2:/.test(normalized)) return false;
  if (/^2001:0*[12][0-9a-f]:/.test(normalized)) return false;
  if (/^2001:0*db8:/.test(normalized)) return false;
  if (/^2002:/.test(normalized)) return false;
  if (/^3ffe:/.test(normalized)) return false;
  return true;
}

export function isPublicIpAddress(address) {
  const family = isIP(String(address || ""));
  if (family === 4) return isPublicIpv4(address);
  if (family === 6) return isPublicIpv6(address);
  return false;
}

export async function resolvePinnedAddress(hostname, lookupImpl = dnsLookup, signal = null) {
  const lookupPromise = Promise.resolve().then(() => lookupImpl(hostname, { all: true, verbatim: true }));
  const result = await awaitWithAbort(lookupPromise, signal);
  const records = Array.isArray(result) ? result : (result ? [result] : []);
  if (!records.length) return null;
  const normalized = records
    .map((record) => ({ address: String(record?.address || ""), family: Number(record?.family || isIP(record?.address)) }))
    .filter((record) => record.address && (record.family === 4 || record.family === 6));
  if (!normalized.length || normalized.length !== records.length) return null;
  // Mixed public/private answers are rejected as a whole; choosing only the public answer
  // would leave rebinding and resolver-order ambiguity in the security boundary.
  if (normalized.some((record) => !isPublicIpAddress(record.address))) return null;
  return normalized.find((record) => record.family === 4) || normalized[0];
}

export function createPinnedLookup(record) {
  return (_hostname, options, callback) => {
    const opts = typeof options === "object" && options ? options : {};
    const cb = typeof options === "function" ? options : callback;
    if (typeof cb !== "function") return;
    if (opts.all) cb(null, [{ address: record.address, family: record.family }]);
    else cb(null, record.address, record.family);
  };
}

function headersView(headers = {}) {
  return {
    get(name) {
      const value = headers[String(name || "").toLowerCase()];
      return Array.isArray(value) ? (value[0] || null) : (value ?? null);
    },
  };
}

async function readNodeHead(response, maxBytes) {
  const chunks = [];
  let bytes = 0;
  let text = "";
  for await (const chunk of response) {
    const buffer = Buffer.isBuffer(chunk) ? chunk : Buffer.from(chunk);
    const remaining = maxBytes - bytes;
    if (remaining <= 0) break;
    const sliced = buffer.length > remaining ? buffer.subarray(0, remaining) : buffer;
    chunks.push(sliced);
    bytes += sliced.length;
    text = Buffer.concat(chunks).toString("utf8");
    if (/<\/head\s*>/i.test(text) || bytes >= maxBytes) break;
  }
  if (!response.complete && typeof response.destroy === "function") response.destroy();
  return text.slice(0, maxBytes);
}

export async function requestHtmlPinned(targetUrl, options = {}) {
  const url = targetUrl instanceof URL ? targetUrl : new URL(String(targetUrl));
  const pinned = await resolvePinnedAddress(
    url.hostname.replace(/\.+$/, ""),
    options.dnsLookupImpl || dnsLookup,
    options.signal,
  );
  if (!pinned) return null;
  const requestFn = options.requestImpl || (url.protocol === "https:" ? https.request : http.request);
  const maxBytes = Number(options.maxBytes) > 0 ? Number(options.maxBytes) : DEFAULT_MAX_BYTES;

  return new Promise((resolve, reject) => {
    let settled = false;
    const finish = (fn, value) => {
      if (settled) return;
      settled = true;
      fn(value);
    };
    const requestOptions = {
      method: "GET",
      headers: {
        "User-Agent": "Mozilla/5.0 (compatible; SBTLHub/1.0; +https://github.com/ihyowoen/SBTL_HUB)",
        Accept: "text/html,application/xhtml+xml;q=0.9",
      },
      signal: options.signal,
      servername: url.hostname.replace(/\.+$/, ""),
      lookup: createPinnedLookup(pinned),
    };

    const req = requestFn(url, requestOptions, async (response) => {
      try {
        const status = Number(response.statusCode || 0);
        const contentType = String(response.headers?.["content-type"] || "").toLowerCase();
        const shouldRead = status >= 200 && status < 300
          && (!contentType || contentType.includes("text/html") || contentType.includes("application/xhtml+xml"));
        const html = shouldRead ? await readNodeHead(response, maxBytes) : "";
        if (!shouldRead && typeof response.resume === "function") response.resume();
        finish(resolve, {
          status,
          ok: status >= 200 && status < 300,
          headers: headersView(response.headers),
          url: url.href,
          body: null,
          text: async () => html,
        });
      } catch (error) {
        finish(reject, error);
      }
    });
    req.on("error", (error) => finish(reject, error));
    req.end();
  });
}
