# PR #385 — 원본 모듈 재현 결과

**진단·원본 재현 단계 완료 / 운영 검증기 수정은 아직 미수행 / 병합 보류**

이 결과는 `STRUCTURAL_REVIEW_AND_PLAN.md`의 실행 전 체크리스트 중 원본 실행·영향 분류 항목을 완료한다. 공통 core 추출, 의미 판정 교체, 실제 KR/EN artifact replay와 full-run CLI/production applier 검증은 남아 있다.

## 실행과 원본 동일성

- 검사 대상: `bd7b7c835e45b70466ac599c5f7a17278e68eaa8`의 실제 Git checkout.
- 재현 도구 commit: `9533786baa16fe845a8cc7253b5613a02f78c14b`.
- [실행 run 35755432854](https://github.com/ihyowoen/SBTL_HUB/actions/runs/35755432854), job `106839876914`.
- Artifact: `pr385-original-proof-35755432854`, ID `10708350279`.
- Python 3.12.14 / Node v20.20.2.
- 각 검사 모듈의 실제 working bytes와 검사 commit의 Git blob을 대조한 후 import했다. 함수 전사본이나 monkeypatch를 쓰지 않았다.
- 내려받은 전체 artifact ZIP SHA-256: `68177c3daf397444376afaa424082e71eb8c2d842ad3100b4d6c2bc63d1dc4a0`.
- 원본 tracked-source archive SHA-256: `f951910251daab0c43b30869ac322401b067934e9645c0ba75cfb99c37dd240d`.
- 전체 입력·출력을 담은 `reproduction.json`: 19,721 bytes, SHA-256 `f125a15a76ec41b8d61c0d65d08733553736ce7bd20f26e4d4ceff9181c944b1`.

원본 archive도 내려받아 위 hash와 일치하는 것을 확인했다. `OBSERVATIONS.json`은 영구 보존용 결과 요약이며 raw JSON 자체가 아니다. 정확한 합성 입력은 위 harness commit의 `reproduce.py`에 고정되어 있고 전체 raw 결과와 실행 로그는 artifact에 있다. Artifact 보존 기간은 7일이므로 장기 사용 시 증거 묶음을 별도 보존한다.

## 집계

| 실행 집합 | 실제 결과 |
|---|---|
| 원본 active workflow suite | **924 tests PASS** — 이번 체크포인트에서 실제 재실행 |
| 원본 binding self-test | PASS |
| 신규 원본 재현 집합 | 32개 실행, 기대 일치 13개 / 위반 19개 / 실행 오류 0개 |
| component 검사 | 13개 중 정상 대조군 7개 일치, 6개 문제 동작 재현 |
| content gate + operation-card 검사 | 18개 중 오허용 11개, 정상 변경 대조군 과차단 1개, 나머지 6개 기대 일치 |
| standalone audit helper | tentative zero-delta 입력 오허용 1개 |
| full-run CLI / production applier | **미실행** |

19개 위반을 서로 독립적인 19개 production 결함이라고 세면 안 된다. 같은 원인을 component와 상위 content gate에서 재확인한 항목이 포함된다. 모든 입력은 synthetic fixture이며 실제 게시 카드나 실제 출처 진실성을 인증하는 테스트가 아니다.

## content gate가 잘못 허용한 11개 합성 시나리오

실제 `validate_content_enrichment_delta`에 bound rows, locked Prompt V5, operation card를 전달했다. 아래 사례들은 함수 안의 audited-copy/operation-copy 및 evidence-package 보존 검사도 통과했다. **전체 run orchestration이나 production applier를 통과했다는 뜻은 아니다.**

| ID | 잘못 허용된 변화 |
|---|---|
| R01 | 양수 10 MW 증거로 Unicode minus가 붙은 −10 MW 주장 허용 |
| R02 | 20억원 증거로 20조원 주장 허용 |
| R03 | 한국어 ‘승인되지 않았다’가 realized state를 요구하는 zero-delta 예외 통과 |
| R04 | ‘If Alpha is approved’ 조건절이 realized zero-delta 예외 통과 |
| R05 | 정량 변경만 입증된 상태에서 ‘알파는 수익성이 높다’ 추가 허용 |
| R06 | 정량 표현이 섞인 한국어 문장에서 알파/베타의 석탄/가스 관계 교환 허용 |
| R07 | Beta의 목표·허가조건 증거로 Alpha의 목표·허가조건 zero-delta 허용 |
| R08 | 동일 승인 문장의 단순 반복을 정보 증가로 허용 |
| R09 | Alpha/Beta 뒤의 It 문장들 사이 목적어 교환 허용 |
| R10 | 동일 판매 주체의 석탄/가스와 Beta/Gamma 구매자 조합 교환 허용 |
| R11 | 동일 Alpha의 capacity/output 수치 교환을 별도 Gamma 상태 심화와 함께 허용 |

이 결과는 최초 검토의 component-only 한계를 일부 해소한다. 실제 content gate의 호출 수준에서 관계·극성·단위 보존 문제가 확인되었고, 원본 코드 수정은 아직 하지 않았다.

## 경로 불일치와 과차단

**R12/R13:** 동일한 `Previously planned at 10 MW; Alpha may be approved; target remains subject to permit.`와 동일 증거에 대해 content gate는 BLOCKED, standalone audit helper는 findings 없이 ACCEPTED였다. 전자는 realized strength-2 조건을 요구하고 후자는 대응하는 조건이 빠진다. 단독 stage CLI 전체를 실행한 결과로 확대하지 않는다.

**P04:** 근거가 있는 `10 MW -> 20 MW` 변경에 근거와 같은 tentative `Alpha may be delayed`를 추가한 정상 변경 대조군이 `zero-delta 0.6 changed_state requires at least one evidence-grounded realized strength-2 subject/state claim`로 차단되었다. actual changed가 있는 경로에 zero-delta 전용 조건이 적용되는 과차단이다. 이 조건의 분리를 공통 정책 테스트로 고정해야 한다.

영어/한국어 정상 정량 변경, 실제 realized 상태의 zero-delta, ASCII 부호 불일치 차단, MW/MWh 불일치 차단 대조군은 기대대로 동작했다. 안전한 검증은 오허용과 과차단을 함께 해결해야 한다.

## CI 실패의 의미

전용 진단 workflow는 artifact를 업로드하기 위해 probe 단계의 오류 후에도 계속 실행하지만, 마지막 gate에서 원래 probe outcome을 다시 검사해 전체 job을 **failure**로 만든다. 이번 실패는 setup/import 오류가 아니라 위 기대 위반 때문이며 `execution-scope.json`에 probes=failure, active_suite=success, binding_selftest=success가 기록되어 있다.

이 workflow는 의도적으로 과거 reviewed head에 고정한 역사적 재현이다. 나중에 현재 코드를 고친다고 이 과거 head의 실패가 사라지지는 않는다. 수정 검증 단계에서는 이 증거를 보존하고, 동일 반례를 현재 후보 head에 적용하는 별도 gate로 전환해야 한다. 과거 진단을 삭제하거나 expectedFailure로 숨긴 뒤 수정 완료라고 해서는 안 된다.

## 이번 PR 반영과 다음 작업

이번 체크포인트는 문서·진단 harness·진단 workflow·결과만 추가했다. 운영 validator, Prompt 0.6, canonical 카드 데이터, baseline, Related 그래프는 변경하지 않았다. merge/force-push/기존 리뷰 일괄 resolution은 하지 않았다.

다음 묶음은 **공통 context/core 추출과 full/standalone 정책 일치**다. 그 후 수치·상태·관계 의미 보존을 구현하고, 여기서 확보한 반례와 정상 대조군을 모두 재실행한다. 실제 run 및 최종 적용 결과에 관한 검증은 별도 종료 조건으로 남는다.
