import fs from "node:fs/promises";
import path from "node:path";

export const REGION_KR_LABEL = { US: "미국", KR: "한국", CN: "중국", EU: "유럽", JP: "일본", GL: "글로벌", NA: "북미" };

export const BRAVE_KEYWORDS = /(실시간|외부|원문|링크|기사\s*검색|brave|외부\s*기사|최신\s*기사|검색해|찾아줘.*기사|뉴스\s*링크|외부\s*링크)/i;

export function fmtDate(date) {
  if (!date) return "-";
  const s = String(date).trim();
  const m = s.match(/^(\d{4})[.-](\d{2})[.-](\d{2})/);
  if (m) return `${m[1]}.${m[2]}.${m[3]}`;
  return s;
}

export function kstToday() {
  const now = new Date();
  const kst = new Date(now.getTime() + (now.getTimezoneOffset() + 540) * 60000);
  return `${kst.getFullYear()}.${String(kst.getMonth() + 1).padStart(2, "0")}.${String(kst.getDate()).padStart(2, "0")}`;
}

export function toCardView(card) {
  return {
    title: card?.T || "",
    subtitle: card?.sub || "",
    signal: card?.s || "i",
    url: card?.url || "",
    region: card?.r || "",
    date: card?.d || "",
    source: card?.src || "",
    gist: card?.g || "",
  };
}

export function toLinkView(link) {
  return {
    title: link?.title || "",
    description: link?.description || "",
    url: link?.url || "",
  };
}

function projectRoot() {
  return process.cwd();
}

async function readJsonFile(absPath, fallback) {
  try {
    const raw = await fs.readFile(absPath, "utf8");
    return JSON.parse(raw);
  } catch {
    return fallback;
  }
}

export async function loadKnowledge() {
  const root = projectRoot();
  const cardsPath = path.join(root, "public", "data", "cards.json");
  const faqPath = path.join(root, "public", "data", "faq.json");
  const trackerPath = path.join(root, "public", "data", "tracker_data.json");

  const [cardsRaw, faqRaw, trackerRaw] = await Promise.all([
    readJsonFile(cardsPath, []),
    readJsonFile(faqPath, []),
    readJsonFile(trackerPath, { meta: {}, items: [] }),
  ]);

  const cards = Array.isArray(cardsRaw) ? cardsRaw : (cardsRaw?.cards || []);
  const faq = Array.isArray(faqRaw) ? faqRaw : [];
  const tracker = {
    meta: trackerRaw?.meta || {},
    items: Array.isArray(trackerRaw?.items) ? trackerRaw.items : [],
    sources: trackerRaw?.sources || {},
  };

  return { cards, faq, tracker };
}
