# PR #385 — 구조 재설계 및 원본 재현 체크포인트

기준 head: `bd7b7c835e45b70466ac599c5f7a17278e68eaa8`  
기준 main: `34386663f1795aef6cb730f9320f6cae715a5c79`  
판정: **병합 보류 / 재현·재설계 진행 중**

이 문서는 대화에서 작성한 `AUDIT_KO.md`와 `REBUILD_SPEC_KO.md`의 저장소용 진단 요약 및 실행 계획이다. 최초 검토는 원본 소스 추적과 수동 전사한 함수 발췌본의 component 실행이었다. 최초 검토만으로 실제 production run의 최종 승인 우회를 확정하지 않는다. 아래 재현 도구는 그 한계를 해소하기 위해 원본 저장소 모듈을 직접 import한다. 재현 코드 추가는 수정 완료가 아니다.

## 1. 구조 진단

| ID | 발견사항 | 최초 증거 수준 | 원본 재현에서 확인할 사항 |
|---|---|---|---|
| F01 | marker/token Counter에서 주체·역할별 인자·지표·기간이 유실되는 경로 | 소스 추적 및 projection 진단 | boundary 주체, 대명사 관계, 거래 인자 묶음, 동일 주체의 지표별 수치 교환 |
| F02 | 지원하지 않는 부정·조건이 realized strength 2 기본값으로 떨어짐 | 발췌 함수 실행 | 한국어 부정 및 영어 조건절이 zero-delta 예외를 승인하는지 |
| F03 | Unicode minus 및 한국어 억/조 규모가 수치 identity에서 누락 | 발췌 함수 실행 | 다른 부호·금액 규모의 증거로 실제 content gate가 승인되는지 |
| F04 | 한국어 설명형 사실이 누락되고, 정량 신호가 있으면 관계 clause를 skip | 발췌 함수 실행 및 명시적 분기 | 설명형 사실 추가, 자연스러운 숫자 혼합 관계 교환 |
| F05 | full/standalone 정책 중복과 zero-delta realized 조건 불일치 | 소스 호출 경로 | 동일 tentative 입력에 대한 양쪽 결과와 changed 경로 과차단 |
| F06 | 회귀 테스트 수와 실제 릴리스 검증 범위가 다름 | CI 로그 및 job 상태 | 정상/오허용/과차단/실행 오류를 분리하고 최종 operation 및 full CLI를 별도 검증 |

Counter가 의미를 축약하는 것 자체를 버그라고 판정하지 않는다. 그 축약값이 사실·증거·정보 개선의 충분조건으로 사용되는 호출 경로가 검사 대상이다. 동일 문장 반복이 distinct 정보 증가인지도 전체 content-gate 입력으로 확인한다.

## 2. 보존할 통제와 범위

보존: locked Prompt version, 역사적 V4 provenance, field별 `0.5 → 0.4 → C` 비어 있지 않은 baseline, nearest authoritative evidence의 scope/quote/package 일치, 명시적 증거 제외, alias 중복 방지, 증거 패키지 보존, audited copy와 materialized operation 일치.

비범위: collecting/selection 프로세스 변경, 새 R/P stage, canonical 뉴스 데이터 재작성, Related 그래프 변경, 앱 전체 재개발, 기존 검증 강도 완화. 기존 리뷰 스레드를 일괄 resolved로 만들지 않는다. production parser에 예문별 regex를 더하는 방식으로 이 체크포인트를 닫지 않는다.

## 3. 재현 실행 계약

`reproduce.py`는 원본 checkout의 Git HEAD와 실제 import 경로를 확인하고, 모듈의 working bytes가 해당 commit의 Git blob과 일치하는지 검사한다. Git blob 및 SHA-256, locked Prompt version, 정확한 합성 입력, 기대/관찰 결과와 오류를 JSON으로 남긴다. 원본 모듈 monkeypatch, 함수 전사, 외부 API 호출, production 데이터 쓰기는 하지 않는다.

검증 범위를 구분한다.

- `component.*`: 수치/상태/한국어 추출 함수의 동작이다. 최종 승인 결과가 아니다.
- `content_gate.with_operation_card`: 실제 `validate_content_enrichment_delta`에 원본 fixture builder로 생성한 bound rows, locked Prompt version, 감사 문구와 같은 operation card를 전달한다. 이 함수 안의 operation-copy/evidence 보존 검사까지 포함하지만 전체 run CLI와 production applier 검증은 아니다.
- `standalone.audit_helper`: 실제 단독 검증기의 audit helper를 실행한다. 완전한 stage CLI 검증으로 확대하지 않는다.

모든 반례는 synthetic fixture다. source quote의 verified 플래그는 테스트 입력이며 현실 기사의 검증 인증이 아니다. 정상 대조군도 함께 검사한다. `P04_tentative_changed`는 zero-delta 전용 realized 조건이 정상적인 changed 경로에 새는지 검사하는 양성 대조군이다.

Exit 0은 이 유한한 재현 집합의 기대 충족일 뿐 일반적 안전성 증명이 아니다. Exit 1은 기대 위반, Exit 2는 setup/runtime 오류다. 기대 위반을 expectedFailure/skip으로 숨기지 않는다. 원본에서 반례가 통과하면 진단 job은 실패 상태로 남긴다. 기존 active suite와 진단 job의 결과는 별도 기록한다.

```bash
python docs/audits/pr385/reproduce.py \
  --repo /path/to/original-checkout \
  --expect-head bd7b7c835e45b70466ac599c5f7a17278e68eaa8 \
  --output /path/outside/checkout/reproduction.json
```

## 4. 구현 묶음

### 묶음 1 — 공통 context/core

불변 `ResolvedContentContext`에 locked version, 단일 bound rows, field별 baseline 및 stage, authoritative evidence identity/alias/scope/exclusion, 0.6 copy, operation card, 검증 가능한 범위를 모은다. 이는 제안 API이며 구현된 API가 아니다. 같은 정보를 검사마다 재조합하지 않는다.

기계적으로 결정 가능한 무결성 규칙은 stable rule_id를 가진 공통 결과를 반환한다. full은 Blocked, standalone은 findings로 표현할 수 있으나 정책 본체를 복제하지 않는다. 동작 보존 추출과 의도적인 bug fix는 별도 커밋으로 분리한다.

통과 조건: 기존 정상 사례 보존, 공통 scope parity, determinism, context 누락의 명시적 처리. 이 묶음만으로 의미 검증 완성을 선언하지 않는다.

### 묶음 2 — Claim 의미와 신뢰 경계

Claim은 주체, 술어, 역할별 인자, 지표, 수치·부호·bound·통화·규모·단위·분모, 기간/date role, 부정/modality/execution stage, evidence package/span 및 visible field/span을 함께 보존해야 한다. 없음과 미해석을 구별한다. 같은 단어가 출처에 각각 있다는 이유로 새 관계를 승인하지 않는다.

**0.6이 작성한 Claim JSON은 검증 증거가 아니다.** upstream의 검토된 출처·주장과 연결해야 한다. hash/span은 연결과 불변성 증거이지 자연어 함의의 증명 자체는 아니다. 지원 범위에서는 검증된 구조에서 문구를 생성·바인딩하는 방식을 검토하고, 자유문구의 coverage/함의가 불확실하면 기존 보완 경로로 반환한다.

claim delta와 presentation delta를 분리한다. 반복·field 이동·동등 수치 표기는 정보 증가가 아니다. 추가·심화·보존·정정을 구별한다. 수치 교체와 상태 승격은 같은 주체·지표·기간에 연결되어야 한다. zero-delta 정책이 changed 경로에 무의식적으로 적용되어서는 안 된다.

통과 조건: 원본 반례 해결 + 정상 대조군 통과. 모든 한국어·자유문구를 거부해서 통과시키지 않는다.

### 묶음 3 — 실제 artifact와 최종 operation

보존된 KR/EN artifact의 대표 집합과 주체·수치·단계·출처 변형을 고정한다. 역사적 V4 provenance는 덮어쓰지 않는다. production materializer와 full-run CLI를 실제 실행하고 executed/skipped를 기록한다. JS/Python materializer를 둘 다 유지하면 같은 입력의 결과·오류를 differential test한다.

통과 조건: 정상 허용/오허용/과차단/미판정 구분, expected rule_id, 최종 카드와 audit 일치, 완전한 source package 보존. CI 녹색·test count·all threads resolved로 대체하지 않는다.

## 5. 필수 불변조건

공백/표현 markup/동등 숫자 표기/반복/field 이동은 새로운 사실이 아니다. 주체·목적어·거래 역할·지표·기간·부정·조건·미래·단위 변경에는 해당 증거가 필요하다. 한국어 숫자 혼합 clause는 조용히 coverage에서 빠질 수 없다. 동일 source의 ID/URL alias는 근거량을 늘리지 못한다. 명시적 exclusion을 claim coverage가 되살리지 못한다. 충분히 같은 context에서는 full/standalone의 공통 정책 결과가 같아야 한다. 불충분한 context의 미검증 범위를 보고해야 한다. 좁지만 정확한 정상 문구에 불필요한 길이·기계어를 강제하지 않는다.

## 6. 체크리스트

- [x] PR Draft 및 병합 보류 리뷰 게시.
- [x] 구조 진단과 재설계 범위를 저장소에 기록.
- [x] 원본 모듈용 재현 harness 작성.
- [ ] 원본 모듈 실행 결과·source identity 확보 및 영향 분류.
- [ ] 공통 context/core 추출 및 경로 parity.
- [ ] 수치/상태/관계 의미 판정 교체.
- [ ] 실제 KR/EN artifact 및 production materializer/full-run CLI.
- [ ] 최종 head 재리뷰와 병합 판단.

## 원본 근거

- [검토 head의 핵심 binding](https://github.com/ihyowoen/SBTL_HUB/blob/bd7b7c835e45b70466ac599c5f7a17278e68eaa8/validation_scripts/card_run_v4_binding_hardening.py)
- [검토 head의 standalone checker](https://github.com/ihyowoen/SBTL_HUB/blob/bd7b7c835e45b70466ac599c5f7a17278e68eaa8/validation_scripts/stage_artifact_contract_check.py)
- [Prompt 0.6 V5](https://github.com/ihyowoen/SBTL_HUB/blob/bd7b7c835e45b70466ac599c5f7a17278e68eaa8/docs/llm_prompts/v1/08_PROMPT_0_6_Content_Polish.md)
- [기존 active-suite run](https://github.com/ihyowoen/SBTL_HUB/actions/runs/35714788477): 최초 검토에서 내려받은 로그는 924 tests PASS. 새로운 재현 결과가 아니다.
- [기존 apply-card-run](https://github.com/ihyowoen/SBTL_HUB/actions/runs/35714788450): submitted-run 경로의 skipped와 engine 검증 성공을 구별한다.
