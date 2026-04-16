# Future Card Standard — Full Schema Locked

이 문서는 **앞으로 생성될 카드**에 대한 고정 기준이다.

## 1. 신규 카드 표준

앞으로의 신규 카드는 **full schema only** 로 본다.

{
  "id": "...",
  "region": "KR|US|CN|JP|EU|GL",
  "date": "YYYY-MM-DD",
  "cat": "...",
  "signal": "top|high|mid",
  "title": "...",
  "sub": "...",
  "gate": "...",
  "fact": "...",
  "implication": ["...", "..."],
  "urls": ["..."]
}

## 2. Region Label Rule — Locked

region은 기사 출처 국가가 아니라 **사건의 직접 무대**로 붙인다.

- KR / US / CN / JP는 해당 국가가 직접 무대일 때만 사용
- 유럽 개별 국가 사건과 EU 제도 뉴스는 EU
- 두 개 이상 국가가 동등하게 핵심이면 GL
- 현재 배지 체계 밖 국가는 GL
- 애매하면 GL

## 3. 최종 원칙

**앞으로 생성되는 카드는 full schema 기준으로만 작성·검수·병합한다.**
