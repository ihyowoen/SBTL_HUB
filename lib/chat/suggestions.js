export function buildSuggestions(answerType = "general", ctx = {}) {
  const regionLabel = ctx?.region ? ({ US: "미국", KR: "한국", CN: "중국", EU: "유럽", JP: "일본" }[ctx.region] || "") : "";

  if (answerType === "news") {
    const base = ["요약해서 다시 정리", "관련 카드 더 보여줘", "외부 기사 링크 검색"];
    if (!regionLabel) base.push("한국 뉴스만", "미국 뉴스만");
    else {
      if (ctx?.region !== "US") base.push("미국 뉴스만");
      if (ctx?.region !== "KR") base.push("한국 뉴스만");
    }
    return base.slice(0, 5);
  }
  if (answerType === "policy") return ["다가오는 일정만", "한국/EU 비교", "실무 영향만 요약", "관련 카드 더 보여줘"];
  if (answerType === "compare") return ["한 줄 결론만", "관련 카드 더 보여줘", "왜 중요한지 한 줄로"];
  if (answerType === "summary") return ["조금 더 쉽게 설명해줘", "관련 카드 더 보여줘", "왜 중요한지 한 줄로"];
  if (answerType === "follow_up") return ["왜 중요한지 설명해줘", "관련 카드 더 보여줘", "요약해서 다시 정리"];
  return ["조금 더 쉽게 설명해줘", "관련 카드 더 보여줘", "정책 일정만 따로 정리해줘"];
}
