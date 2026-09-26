# PR #385 — 공통 검증 핵심부 및 모드 정책 분리

## 범위

이 변경은 재설계의 3단계 체크포인트다. 의미 해석 엔진 전체 교체나 병합 승인이 아니다.
원본 진단 `bd7b7c835e45b70466ac599c5f7a17278e68eaa8` 및 1~2단계 기록
`d9e4d7c22fad275e8d2b058e6c69d8a4dcffe12a`를 보존한다.

## 코드 경계

`validation_scripts/content_enrichment_core.py`는 독립적인 순수 정책 모듈이다.
full/standalone 진입점을 import하지 않으며 문구 정규화, density 형태/최소 기준,
발생 횟수·주체별 상태 강도 비교 규칙, stable rule_id를 공유한다.
기존 함수명은 호환 alias로 남겨 기존 테스트·호출자의 경로를 보존한다.

`ResolvedEvidenceContext`는 기존 resolver가 해석한 support/text/package를 불변 JSON
스냅샷으로 받는다. 입력·반환 컨테이너를 나중에 변경해도 스냅샷이 바뀌지 않는다.
full은 nearest authoritative package를 한 번만 해석하고 같은 결과에서 text와
package를 파생한다. standalone은 local-row 범위로 명시한다.
**이 객체 자체가 출처 진실성이나 upstream 권위를 인증하지 않는다.**

기존 source resolver, alias/제외 규칙, locked Prompt 버전, baseline fallback,
actual changed-fields 계산, operation 문구/근거 패키지 바인딩은 보존한다.
모든 evidence resolver와 모든 audit shape가 이미 하나로 통합됐다는 뜻은 아니다.

## 별도 커밋으로 분리한 판정 변경

- R13: tentative zero-delta를 standalone도 `C06.GROUNDING.REALIZED`로 차단한다.
- P04: 근거가 있는 실제 변경에는 zero-delta 전용 realized 조건을 강제하지 않는다.
- full의 중복 zero-delta realization 구현을 제거하고 공통 grounding 정책으로 대체한다.
- standalone CLI는 PASS여도 `validation_scope.mode=stage_artifact_only`와
  upstream evidence authority / actual delta / materialized operation 미확인 범위를 출력한다.

부정/조건의 해석 자체는 아직 기존 extractor다. 따라서 이 변경은 한국어 부정,
조건절, Unicode 부호, 억/조, 관계·지표 교환의 의미 손실을 해결했다고 주장하지 않는다.

## 검증 기준과 증거

구조 분리 커밋 A는 기존 924개 회귀 테스트를 보존하고 원본 32개 probe의 관찰값이
모두 같아야 한다. 알려진 실패를 성공으로 바꿔 리팩터링이라고 부르지 않는다.

정책 수정 커밋 B는 기존 924개 + 신규 22개 테스트를 실행한다. 신규 검사는 불변성,
입력 순서 결정성, 정규화 재사용, source resolution 1회, explicit mode,
full/helper 및 실제 standalone CLI 정책 일치, context 부족,
source exclusion 및 operation/증거 패키지 보존을 포함한다.

32개 재현 집합에서는 R13/P04 두 관찰값만 의도적으로 바뀌어야 한다.
나머지 17개 기대 위반과 11개 합성 content-gate 오허용은 후속 수정 대상으로 남긴다.

GitHub Actions의 `PR385 phase3 checkpoint preparation` artifact에는 exact commit/tree/blob,
각 실행 로그와 종료 코드, baseline/A/B 재현 JSON, 변경 파일 hash를 남긴다.
준비 job 성공은 **이 체크포인트의 동등성·정책 수정 확인**이지 전체 32개 safety PASS가 아니다.
원본 pinned 진단 workflow는 변경/삭제하지 않는다.

full-run CLI, production materializer 및 실제 KR/EN artifact replay는 이 단계의
실행 범위가 아니다. 다음 단계에서 수치·상태·관계 표현과 함께 검증한다.

## 원격 반영

임시 preparation workflow는 테스트가 완료된 두 커밋을 별도의 proof branch에만 올린다.
PR branch는 외부 검토 후 non-force fast-forward로 갱신하며, main은 변경하지 않는다.
임시 workflow와 staging template은 최종 후보 tree에서 제거한다. 실행 원본은 commit
history와 Actions artifact로 보존한다. 권한 확대나 새 수집/R/P stage는 추가하지 않는다.
