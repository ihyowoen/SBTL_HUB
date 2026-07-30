import { EventEmitter } from "node:events";
import { Readable } from "node:stream";
import { describe, expect, it, vi } from "vitest";
import {
  createPinnedLookup,
  isPublicIpAddress,
  requestHtmlPinned,
  resolvePinnedAddress,
} from "../lib/chat/retrieve/safeHttp.js";

describe("public IP classification", () => {
  it.each([
    "8.8.8.8",
    "1.1.1.1",
    "2606:4700:4700::1111",
  ])("accepts public address %s", (address) => {
    expect(isPublicIpAddress(address)).toBe(true);
  });

  it.each([
    "127.0.0.1",
    "10.0.0.1",
    "100.64.0.1",
    "169.254.169.254",
    "172.16.0.1",
    "192.168.1.1",
    "198.18.0.1",
    "203.0.113.1",
    "::1",
    "::ffff:127.0.0.1",
    "fc00::1",
    "fe80::1",
    "64:ff9b::7f00:1",
    "2001:db8::1",
    "2002:7f00:1::",
  ])("rejects non-public address %s", (address) => {
    expect(isPublicIpAddress(address)).toBe(false);
  });
});

describe("DNS validation and pinning", () => {
  it("rejects a mixed public/private DNS answer", async () => {
    const lookupImpl = vi.fn(async () => [
      { address: "93.184.216.34", family: 4 },
      { address: "127.0.0.1", family: 4 },
    ]);
    await expect(resolvePinnedAddress("news.example", lookupImpl)).resolves.toBeNull();
  });

  it("returns one approved public address", async () => {
    const lookupImpl = vi.fn(async () => [
      { address: "2606:4700:4700::1111", family: 6 },
      { address: "93.184.216.34", family: 4 },
    ]);
    await expect(resolvePinnedAddress("news.example", lookupImpl)).resolves.toEqual({ address: "93.184.216.34", family: 4 });
  });

  it("pins the approved address into the actual request lookup", async () => {
    const dnsLookupImpl = vi.fn(async () => [{ address: "93.184.216.34", family: 4 }]);
    const requestImpl = vi.fn((_url, options, onResponse) => {
      options.lookup("news.example", {}, (error, address, family) => {
        expect(error).toBeNull();
        expect(address).toBe("93.184.216.34");
        expect(family).toBe(4);
      });
      const response = Readable.from(['<head><meta property="og:image" content="/hero.jpg"></head>']);
      response.statusCode = 200;
      response.headers = { "content-type": "text/html" };
      queueMicrotask(() => onResponse(response));
      const request = new EventEmitter();
      request.end = vi.fn();
      return request;
    });

    const response = await requestHtmlPinned("https://news.example/article", { dnsLookupImpl, requestImpl });
    expect(requestImpl).toHaveBeenCalledTimes(1);
    expect(await response.text()).toContain("og:image");
  });

  it("does not create a request when DNS resolves to a private address", async () => {
    const dnsLookupImpl = vi.fn(async () => [{ address: "127.0.0.1", family: 4 }]);
    const requestImpl = vi.fn();
    await expect(requestHtmlPinned("https://news.example/article", { dnsLookupImpl, requestImpl })).resolves.toBeNull();
    expect(requestImpl).not.toHaveBeenCalled();
  });

  it("includes a stalled DNS lookup in the caller abort deadline", async () => {
    const controller = new AbortController();
    const dnsLookupImpl = vi.fn(() => new Promise(() => {}));
    const requestImpl = vi.fn();
    const pending = requestHtmlPinned("https://news.example/article", {
      dnsLookupImpl,
      requestImpl,
      signal: controller.signal,
    });

    controller.abort();
    await expect(pending).rejects.toMatchObject({ name: "AbortError" });
    expect(requestImpl).not.toHaveBeenCalled();
  });

  it("supports all:true without releasing the pinned address", () => {
    const lookup = createPinnedLookup({ address: "93.184.216.34", family: 4 });
    lookup("news.example", { all: true }, (error, records) => {
      expect(error).toBeNull();
      expect(records).toEqual([{ address: "93.184.216.34", family: 4 }]);
    });
  });
});
