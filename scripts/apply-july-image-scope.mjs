import fs from "node:fs";

const file = "src/App.jsx";
const source = fs.readFileSync(file, "utf8");
const before = `  // 최신 18장은 실제 기사 OG 이미지를 우선 사용하고, 나머지/실패 건은 StoryNewsItem의
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
  const articleImages = useFreshArticleImages(coverCards, 18);`;
const after = `  // 2026년 7월 뉴스는 실제 기사 OG 이미지를 우선 사용한다. API는 한 번에 18건씩
  // 안전하게 나눠 처리하므로 18장은 총 제한이 아니라 배치 크기다. 화면에 추가로 표시되는
  // 7월 카드도 이어서 조회하고, 다른 월/추출 실패 건은 165장 deterministic 풀로 내려간다.
  const coverCards = useMemo(() => {
    const seen = new Set();
    return [...highlights, ...visible].filter((card, idx) => {
      const key = getArticleImageKey(card) || getCardId(card, idx);
      if (!key || seen.has(key)) return false;
      seen.add(key);
      return true;
    });
  }, [highlights, visible]);
  const articleImages = useFreshArticleImages(coverCards, { month: "2026-07" });`;

if (!source.includes(before)) throw new Error("Expected latest-18 image scope snippet not found");
fs.writeFileSync(file, source.replace(before, after));

for (const temp of ["scripts/apply-july-image-scope.mjs", ".github/workflows/apply-july-image-scope.yml"]) {
  try { fs.unlinkSync(temp); } catch { /* noop */ }
}

console.log("July image scope applied");
