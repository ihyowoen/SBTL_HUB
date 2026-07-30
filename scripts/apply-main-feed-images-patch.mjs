import fs from "node:fs";

function replaceOnce(file, before, after) {
  const current = fs.readFileSync(file, "utf8");
  if (current.includes(after)) return;
  const first = current.indexOf(before);
  if (first < 0) throw new Error(`Expected snippet not found in ${file}`);
  if (current.indexOf(before, first + before.length) >= 0) throw new Error(`Snippet is not unique in ${file}`);
  fs.writeFileSync(file, current.slice(0, first) + after + current.slice(first + before.length));
}

function removeBetween(file, startMarker, endMarker) {
  const current = fs.readFileSync(file, "utf8");
  const start = current.indexOf(startMarker);
  if (start < 0) return;
  const end = current.indexOf(endMarker, start);
  if (end < 0) throw new Error(`End marker not found in ${file}`);
  fs.writeFileSync(file, current.slice(0, start) + current.slice(end));
}

const app = "src/App.jsx";
replaceOnce(
  app,
  'import { getCardId } from "./story/normalizeCard";\n',
  'import { getCardId } from "./story/normalizeCard";\nimport { getArticleImageKey, useFreshArticleImages } from "./story/useFreshArticleImages";\n',
);

// Remove the obsolete 21-image parent override. StoryNewsItem already owns the
// larger 165-image deterministic pool and should be the only fallback source.
removeBetween(app, "const AUTO_IMAGES = {", "function ReceiptBubble");

replaceOnce(
  app,
  `  // 화면 내 unique 커버 배정 — highlights와 visible 합쳐서 한 번에 (Copilot review #98 #2)
  const coverMap = useMemo(() => assignHomeCovers([...highlights, ...visible]), [highlights, visible]);
  const coverFor = (card, idx) => coverMap[String(card?.id || card?.T || card?.title || \`idx_\${idx}\`)] || pickHomeCover(card);
`,
  `  // 최신 18장은 실제 기사 OG 이미지를 우선 사용하고, 나머지/실패 건은 StoryNewsItem의
  // 165장 deterministic 풀로 내려간다. highlights와 visible 중복은 먼저 제거한다.
  const coverCards = useMemo(() => {
    const seen = new Set();
    return [...highlights, ...visible].filter((card, idx) => {
      const key = getArticleImageKey(card) || getCardId(card, idx);
      if (!key || seen.has(key)) return false;
      seen.add(key);
      return true;
    });
  }, [highlights, visible]);
  const articleImages = useFreshArticleImages(coverCards, 18);
  const fallbackCoverUrls = useMemo(
    () => assignCardCoverImages(coverCards, { alreadyUsed: Object.values(articleImages) }),
    [coverCards, articleImages],
  );
  const fallbackCoverMap = useMemo(() => {
    const map = {};
    coverCards.forEach((card, idx) => {
      const key = getArticleImageKey(card) || getCardId(card, idx);
      if (key) map[key] = fallbackCoverUrls[idx] || "";
    });
    return map;
  }, [coverCards, fallbackCoverUrls]);
  const imagePropsFor = (card, idx) => {
    const articleKey = getArticleImageKey(card);
    const mapKey = articleKey || getCardId(card, idx);
    const fresh = articleKey ? (articleImages[articleKey] || "") : "";
    const fallbackImage = fallbackCoverMap[mapKey] || "";
    return {
      coverImage: fresh || fallbackImage,
      fallbackImage: fresh && fallbackImage && fresh !== fallbackImage ? fallbackImage : "",
    };
  };
`,
);

let appSource = fs.readFileSync(app, "utf8");
const oldProp = "coverImage={coverFor(card, i)}";
const count = appSource.split(oldProp).length - 1;
if (count !== 2 && !appSource.includes("{...imagePropsFor(card, i)}")) {
  throw new Error(`Expected 2 StoryNewsItem cover props, found ${count}`);
}
appSource = appSource.split(oldProp).join("{...imagePropsFor(card, i)}");
fs.writeFileSync(app, appSource);

const story = "src/story/StoryNewsItem.jsx";
replaceOnce(
  story,
  `  coverImage = '',
  featured = false,`,
  `  coverImage = '',
  fallbackImage = '',
  featured = false,`,
);
replaceOnce(
  story,
  `    // coverImage prop이 있으면 항상 첫 후보로 사용 (featured 무관) —
    // 부모 컴포넌트의 assignCardCoverImages dedup 결과가 자식까지 그대로 전달되도록.
    const candidates = coverImage ? [coverImage, ...pool] : pool;
    return Array.from(new Set(candidates.filter(Boolean)));
  }, [imageCategory, coverImage]);`,
  `    // 실제 기사 이미지 → 페이지 단위로 중복 제거된 deterministic fallback → 카테고리 풀.
    // fallbackImage는 기사 hotlink가 차단될 때 한 번만 사용하고, 이후에는 gradient로 끝낸다.
    const candidates = coverImage
      ? [coverImage, fallbackImage, ...pool]
      : (fallbackImage ? [fallbackImage, ...pool] : pool);
    return Array.from(new Set(candidates.filter(Boolean)));
  }, [imageCategory, coverImage, fallbackImage]);`,
);
replaceOnce(
  story,
  `  }, [imageStartIndex, imageCategory]);`,
  `  }, [imageStartIndex, imageCategory, coverImage, fallbackImage]);`,
);
replaceOnce(
  story,
  `          onError={() => {
            // 2026-05-02b 정석 fix: 풀 점프 제거.
            // 기존: imageOffset++ 로 풀 안 다음 사진 점프 → cross-pool 중복 사진 만나면 부모 dedup 깨짐
            // 현재: ad-blocker 차단 사진은 gradient placeholder로 fallback (renderVisualImage에 이미 구현)
            setImageLoaded(false);
          }}`,
  `          onError={() => {
            setImageLoaded(false);
            // 원문 OG hotlink 실패 때만 부모가 미리 unique 배정한 단일 fallback으로 이동한다.
            // fallback까지 실패하면 추가 풀 점프 없이 gradient로 끝내 dedup 결과를 보존한다.
            if (coverImage && fallbackImage && imageOffset === 0 && imageSrc === coverImage) {
              setImageOffset(1);
            }
          }}`,
);

for (const temp of ["scripts/apply-main-feed-images-patch.mjs", ".github/workflows/apply-main-feed-images-patch.yml"]) {
  try { fs.unlinkSync(temp); } catch { /* noop */ }
}

console.log("Main feed article image patch applied");
