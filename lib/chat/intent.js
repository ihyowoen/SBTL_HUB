export function classifyIntent(message = "", context = {}) {
  const txt = String(message || "").trim();
  const l = txt.toLowerCase();
  const hasCtx = !!context?.last_answer_type;

  if (/(그\s*기사|방금|직전|저\s*카드|그\s*카드|아까\s*그|첫\s*번째|두\s*번째|세\s*번째|네\s*번째|1번|2번|3번|4번|더\s*찾|더\s*보여|관련.*더)/.test(l) && hasCtx) {
    return "follow_up";
  }
  if (/(일정|정책|규제|시행|법안|언제|예정|스케줄|feoc|ira|cbam|battery\s*passport|meti|gx)/.test(l)) return "policy";
  if (/(비교|차이|vs|대비|어떤 게|뭐가 더)/.test(l)) return "compare";
  if (/(요약|정리|핵심|브리핑|한 줄|한줄)/.test(l)) return "summary";
  if (/(최신|뉴스|소식|현황|지금|오늘|최근|이번|기사)/.test(l)) return "news";
  return "general";
}
