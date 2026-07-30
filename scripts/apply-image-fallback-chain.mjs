import fs from "node:fs";

function replaceOnce(file, before, after) {
  const source = fs.readFileSync(file, "utf8");
  if (!source.includes(before)) throw new Error(`Expected snippet not found in ${file}`);
  fs.writeFileSync(file, source.replace(before, after));
}

replaceOnce(
  "src/App.jsx",
  `  const fallbackCoverUrls = useMemo(
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
  };`,
  `  const fallbackCoverChains = useMemo(() => {
    const used = new Set(Object.values(articleImages).filter(Boolean));
    const layers = Array.from({ length: 3 }, () => {
      const layer = assignCardCoverImages(coverCards, { alreadyUsed: used });
      layer.forEach((url) => { if (url) used.add(url); });
      return layer;
    });
    return coverCards.map((_, idx) => layers.map((layer) => layer[idx]).filter(Boolean));
  }, [coverCards, articleImages]);
  const fallbackCoverMap = useMemo(() => {
    const map = {};
    coverCards.forEach((card, idx) => {
      const key = getArticleImageKey(card) || getCardId(card, idx);
      if (key) map[key] = fallbackCoverChains[idx] || [];
    });
    return map;
  }, [coverCards, fallbackCoverChains]);
  const imagePropsFor = (card, idx) => {
    const articleKey = getArticleImageKey(card);
    const mapKey = articleKey || getCardId(card, idx);
    const fresh = articleKey ? (articleImages[articleKey] || "") : "";
    const fallbackImages = fallbackCoverMap[mapKey] || [];
    return {
      coverImage: fresh || fallbackImages[0] || "",
      fallbackImages,
    };
  };`,
);

replaceOnce(
  "src/story/StoryNewsItem.jsx",
  `  coverImage = '',
  fallbackImage = '',
  featured = false,`,
  `  coverImage = '',
  fallbackImage = '',
  fallbackImages = null,
  featured = false,`,
);

replaceOnce(
  "src/story/StoryNewsItem.jsx",
  `  const imagePool = useMemo(() => {
    const pool = IMAGE_POOLS[imageCategory] || IMAGE_POOLS.DEFAULT;
    // 실제 기사 이미지 → 페이지 단위로 중복 제거된 deterministic fallback → 카테고리 풀.
    // fallbackImage는 기사 hotlink가 차단될 때 한 번만 사용하고, 이후에는 gradient로 끝낸다.
    const candidates = coverImage
      ? [coverImage, fallbackImage, ...pool]
      : (fallbackImage ? [fallbackImage, ...pool] : pool);
    return Array.from(new Set(candidates.filter(Boolean)));
  }, [imageCategory, coverImage, fallbackImage]);`,
  `  const imagePool = useMemo(() => {
    const pool = IMAGE_POOLS[imageCategory] || IMAGE_POOLS.DEFAULT;
    // 실제 기사 이미지 뒤에 부모가 페이지 단위로 중복 제거한 최대 3개의 폴백을 둔다.
    // 명시적 체인이 없는 단독 사용 시에만 기존 카테고리 풀을 사용한다.
    const provided = [
      coverImage,
      ...(Array.isArray(fallbackImages) ? fallbackImages : []),
      fallbackImage,
    ].filter(Boolean);
    const candidates = provided.length ? provided : pool;
    return Array.from(new Set(candidates));
  }, [imageCategory, coverImage, fallbackImage, fallbackImages]);`,
);

replaceOnce(
  "src/story/StoryNewsItem.jsx",
  `  useEffect(() => {
    setImageOffset(0);
    setImageLoaded(false);
  }, [imageStartIndex, imageCategory, coverImage, fallbackImage]);`,
  `  useEffect(() => {
    setImageOffset(0);
    setImageLoaded(false);
  }, [imageStartIndex, imageCategory, imagePool]);`,
);

replaceOnce(
  "src/story/StoryNewsItem.jsx",
  `          onError={() => {
            setImageLoaded(false);
            // 원문 OG hotlink 실패 때만 부모가 미리 unique 배정한 단일 fallback으로 이동한다.
            // fallback까지 실패하면 추가 풀 점프 없이 gradient로 끝내 dedup 결과를 보존한다.
            if (coverImage && fallbackImage && imageOffset === 0 && imageSrc === coverImage) {
              setImageOffset(1);
            }
          }}`,
  `          onError={() => {
            setImageLoaded(false);
            // 기사 원본이나 폴백이 차단되면 다음 unique 후보로 이동한다.
            // 최대 3개 폴백까지 소진한 뒤에만 gradient로 끝낸다.
            setImageOffset((current) => (
              current + 1 < imagePool.length ? current + 1 : imagePool.length
            ));
          }}`,
);

const testFile = "__tests__/imagePools.test.js";
let tests = fs.readFileSync(testFile, "utf8");
const testAnchor = `  it('같은 카드는 안정적으로 같은 이미지를 받는다 (stable seed)', () => {
    const card = { id: 'stable-test', title: 'Test card', region: 'NA' };
    const result1 = assignCardCoverImages([card])[0];
    const result2 = assignCardCoverImages([card])[0];
    expect(result1).toBe(result2);
  });`;
const testReplacement = `${testAnchor}

  it('3단계 폴백 레이어도 앞선 이미지와 겹치지 않게 배정한다', () => {
    const cards = [
      { id: 'f1', title: 'Greenbushes lithium mine earnings', region: 'GL' },
      { id: 'f2', title: 'EU battery policy update', region: 'EU' },
      { id: 'f3', title: 'ESS grid project', region: 'US' },
      { id: 'f4', title: 'Battery factory ramp-up', region: 'KR' },
    ];
    const used = new Set();
    const all = [];
    for (let depth = 0; depth < 3; depth += 1) {
      const layer = assignCardCoverImages(cards, { alreadyUsed: used });
      layer.forEach((url) => { used.add(url); all.push(url); });
    }
    expect(all).toHaveLength(12);
    expect(new Set(all).size).toBe(12);
  });`;
if (!tests.includes(testAnchor)) throw new Error(`Expected test anchor not found in ${testFile}`);
tests = tests.replace(testAnchor, testReplacement);
fs.writeFileSync(testFile, tests);

for (const temp of [
  "scripts/apply-image-fallback-chain.mjs",
  ".github/workflows/apply-image-fallback-chain.yml",
]) {
  try { fs.unlinkSync(temp); } catch { /* noop */ }
}

console.log("Multi-step image fallback chain applied");
