# SBTL_HUB 운영 매뉴얼

## 0. 이 문서의 역할

이 문서는 **실무자가 실제로 무엇을 백업하고, 무엇을 실행하고, 무엇을 확인해야 하는지**를 적는 운영 매뉴얼이다.

신규 카드 기준은 **full schema only** 다.

---

## 1. 운영 기본 규칙

### Rule 1. production 기준은 main이다
### Rule 2. cards.json은 민감 파일이다
### Rule 3. merge 전에 반드시 백업
### Rule 4. merge는 production 확인이 끝나야 종료
### Rule 5. 신규 카드 payload는 full schema 기준이다

필수 필드:
- `id`
- `region`
- `date`
- `cat`
- `signal`
- `title`
- `sub`
- `gate`
- `fact`
- `implication`
- `urls`

---

## 2. 작업 전 준비
## 3. 표준 병합 절차
## 4. 병합 전 체크 기준
## 5. 병합 도구 운영상 주의점
## 6. 실수 방지 규칙
## 7. 실제 검증 항목

최소 확인 항목:
- `title`
- `region`
- `date`
- `cat`
- `signal`
- `gate`
- `fact`
- `implication`
- `urls`

---

## 8. 최종 한 줄 원칙

**SBTL_HUB는 자동 수집 앱이 아니라 편집된 intelligence 앱이다.**
