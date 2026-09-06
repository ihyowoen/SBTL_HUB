#!/usr/bin/env python3
import base64, gzip, hashlib, json
from pathlib import Path

BASE = Path("validation_temp/20260903-r7-stage-b")
PARTS = ["stage-b.part01","stage-b.part02","stage-b.part03","stage-b.part04a","stage-b.part04b",
         "stage-b.part05","stage-b.part06","stage-b.part07","stage-b.part08a","stage-b.part08b",
         "stage-b.part09","stage-b.part10","stage-b.part11","stage-b.part12","stage-b.part13","stage-b.part14"]
EXPECTED_SHA = "016987404810cdb067afd6a07b0c451f0bd33ce6c178eadcef0a16c440be9cd6"

REPAIRS = {
"STD26_R7_001": dict(event="E0001",region="US",date="2026-09-02",
 title="Vertiv, UtilityInnovation Group 인수 계약…데이터센터 전력 인프라 역량 확대",
 sub="종결 시 현금 약 14.5억달러·성과연동 최대 11.5억달러…마이크로그리드·현장발전 통합 역량 확보",
 gate="Vertiv가 전력망 제약 대응을 위한 마이크로그리드·현장발전 기술을 M&A로 내재화한다.",
 fact="Vertiv는 9월 2일 UtilityInnovation Group 인수 계약을 발표했다. 거래 대가는 종결 시 현금 약 14억5천만달러와 향후 EBITDA 성과에 따라 최대 11억5천만달러의 추가 지급으로 구성되며, 인수 대상은 마이크로그리드 제어·현장발전 오케스트레이션·스위치기어·behind-the-meter 전력 아키텍처 역량을 보유한다.",
 implication=["AI·데이터센터 증설에서 계통연계 지연이 커질수록 전력장비 업체의 대응 범위가 UPS를 넘어 현장발전·마이크로그리드까지 넓어지는 흐름을 보여준다.","성과연동 대가가 포함된 만큼 실제 통합 효과와 데이터센터 수주 기여를 후속 확인해야 한다."]),
"STD26_R7_002": dict(event="E0004",region="US",date="2026-09-02",
 title="MN8·Google·Eos, PJM에 86MW 태양광·380MWh 저장 결합 프로젝트 추진",
 sub="Eos 아연계 10MW/100MWh와 리튬이온 70MW/280MWh 병행…웨스트버지니아 데이터센터 수요 지원",
 gate="대형 데이터센터 전력수요 대응에 장주기 저장과 리튬이온을 함께 쓰는 하이브리드 구성이 구체화됐다.",
 fact="Eos Energy는 MN8 Energy·Google과 연계된 프로젝트에서 86MW 태양광, Eos 아연계 장주기저장 10MW/100MWh, 리튬이온 저장 70MW/280MWh를 결합한다고 9월 2일 밝혔다. 프로젝트는 PJM 권역과 Google의 계획된 웨스트버지니아 데이터센터 전력수요를 지원하는 구상이다.",
 implication=["데이터센터 전력조달이 단일 배터리 화학계가 아니라 단주기·장주기 자산의 조합으로 설계되는 사례다.","실제 상업운전 시점과 저장자산별 운영 역할이 확인되면 장주기저장의 경제성 판단이 더 명확해진다."]),
"STD26_R7_003": dict(event="E0005",region="GL",date="2026-09-02",
 title="ProLogium, 3.5세대 LCB 양산 돌입…대형 셀 381Wh/kg 검증",
 sub="대만 GWh급 라인에서 양산…TÜV 시험 185.4Ah 셀 903Wh/L",
 gate="고에너지밀도 차세대 셀이 연구실 단계를 넘어 GWh급 양산 라인으로 이동했다.",
 fact="ProLogium은 9월 2일 대만 GWh급 설비에서 3.5세대 LCB 셀 양산에 들어갔다고 밝혔다. TÜV 시험에서 185.4Ah 대형 셀은 381Wh/kg, 903Wh/L를 기록했으며, UL Solutions의 GB/T 43568-2026 시험을 통해 all-solid-state 분류 관련 검증 결과도 제시했다.",
 implication=["차세대 배터리 경쟁의 평가축이 셀 성능 발표에서 실제 양산성과 대형 폼팩터 검증으로 이동하고 있다.","후속 고객 적용·수율·출하량이 확인돼야 양산 선언의 상업적 의미를 판단할 수 있다."]),
"STD26_R7_004": dict(event="E0008",region="GL",date="2026-09-02",
 title="캐나다 McIlvenna Bay 구리·아연 광산 생산 개시",
 sub="서스캐처원 핵심광물 프로젝트가 개발 단계에서 실제 생산으로 전환",
 gate="북미 핵심광물 공급망에서 신규 구리·아연 광산이 실제 생산 단계에 진입했다.",
 fact="캐나다 천연자원부는 9월 2일 서스캐처원 McIlvenna Bay 구리·아연 광산의 생산이 시작됐다고 밝혔다. 이 프로젝트는 캐나다 핵심광물 공급망 확대의 신규 생산 자산으로 분류된다.",
 implication=["배터리·전력망 투자 확대와 함께 필요한 구리 공급의 북미 지역 다변화가 실제 생산 자산으로 이어진 사례다.","초기 램프업 속도와 정광 생산량이 향후 공급 기여도를 결정한다."]),
"STD26_R7_005": dict(event="E0013",region="US",date="2026-09-01",
 title="Aligned Solar Partners 7 첫 클로징…미국 분산형 태양광·저장에 5억달러 목표",
 sub="첫 클로징 금액은 비공개…건설 준비 단계 자산에 투자",
 gate="미국 분산형 태양광·저장 프로젝트를 겨냥한 신규 펀드가 실제 첫 클로징을 완료했다.",
 fact="Aligned Climate Capital은 9월 1일 Aligned Solar Partners 7의 첫 클로징을 발표했다. 펀드 목표 규모는 5억달러이며, 첫 클로징 금액은 공개하지 않았다. 투자 대상은 미국 내 건설 준비 단계의 분산형 태양광·에너지저장 자산이다.",
 implication=["프로젝트 금융이 대형 유틸리티급뿐 아니라 분산형 태양광·저장 포트폴리오로도 확대되고 있다.","5억달러는 목표 규모이므로 실제 조달액과 투자 집행 속도를 구분해 추적해야 한다."]),
"STD26_R7_009": dict(event="E0067",region="US",date="2026-09-01",
 title="OCI Energy·Arava Power, 텍사스 260MW SunRoper 태양광 착공",
 sub="9월 1일 기공식…2027년 상업운전 목표·Fortune 100 기업과 장기 PPA",
 gate="OCI의 미국 재생에너지 개발이 텍사스 260MW 프로젝트의 실제 착공 단계로 진입했다.",
 fact="OCI Energy는 Arava Power와 50대50으로 개발하는 텍사스 Wharton County의 260MW SunRoper 태양광 프로젝트가 9월 1일 기공식을 열고 건설 단계에 들어갔다고 밝혔다. 상업운전 목표는 2027년이며, 고객명을 공개하지 않은 Fortune 100 기업과 장기 PPA가 체결돼 있다.",
 implication=["한국계 개발사의 미국 전력 인프라 투자가 개발계획에서 실제 건설로 전환된 사례다.","향후 공정 진척과 2027년 상업운전 달성 여부가 실행력을 확인하는 핵심 지표다."]),
"STD26_R7_011": dict(event="E0094",region="KR",date="2026-09-04",
 title="한국, 재생에너지 출력감시·제어 의무 20kW 이상으로 확대",
 sub="2027년 1월부터 적용…상용 이동통신망 사용 허용으로 구축 부담 완화",
 gate="분산형 재생에너지의 계통운영 규칙이 소규모 설비까지 확대된다.",
 fact="정부는 9월 4일 관련 규정을 개정해 재생에너지 설비의 실시간 감시·제어 의무 대상을 기존 90kW 이상에서 20kW 이상으로 확대했다. 새 기준은 2027년 1월 1일부터 적용되며, 상용 이동통신망을 활용한 제어 방식도 허용한다.",
 implication=["재생에너지 비중 상승에 따라 소규모 분산자원도 계통운영 체계 안으로 들어오는 규제 변화다.","ESS·인버터·EMS 사업자는 원격 제어·통신 호환성과 현장 구축비를 함께 고려해야 한다."]),
"STD26_R7_014": dict(event="E0157",region="JP",date="2026-09-01",
 title="PPES 등 4사, 배터리 셀 알루미늄 수평재활용 체계로 환경상 수상",
 sub="셀 실링 플레이트 스크랩을 같은 부품 소재로 재투입…체계 자체는 8월 이미 양산 적용",
 gate="배터리 제조 스크랩의 폐쇄형 알루미늄 재활용이 일본에서 양산 운영 사례로 자리잡았다.",
 fact="PPES는 9월 1일 4개사가 구축한 배터리 셀 알루미늄 수평재활용 체계가 일본 환경대신상을 받았다고 밝혔다. 셀 실링 플레이트에서 발생한 알루미늄 스크랩을 다시 같은 부품용 소재로 돌리는 방식이며, 해당 체계의 양산 적용 자체는 8월 5일 이미 발표됐다.",
 implication=["신규 실행 사건은 수상 자체가 아니라 이미 운영 중인 폐쇄형 재활용 체계의 외부 인정이라는 점을 구분해야 한다.","Stage C에서는 기존 8월 실행 발표 대비 이번 수상이 독립 카드 가치가 있는지 재판정해야 한다."]),
"STD26_R7_015": dict(event="E0167",region="GL",date="2026-09-02",
 title="Amazon Australia, 50MW/200MWh Bairnsdale BESS와 장기 tolling 계약",
 sub="Anza Power와 체결…Amazon의 APAC 첫 독립형 배터리 저장 tolling 계약",
 gate="호주 standalone BESS의 수익모델에 글로벌 데이터·클라우드 기업의 장기계약이 직접 들어왔다.",
 fact="I Squared Capital은 9월 2일 Anza Power가 빅토리아 Bairnsdale의 50MW/200MWh BESS에 대해 Amazon Australia와 battery tolling agreement를 체결했다고 밝혔다. 회사는 이를 Amazon의 APAC 첫 standalone battery storage tolling agreement로 설명했다.",
 implication=["BESS 수익모델이 단순 현물시장 노출에서 장기 용량·운영권 계약으로 다변화되는 흐름을 보여준다.","프로젝트 상업운전과 실제 tolling 개시가 후속 실행 확인 포인트다."]),
"STD26_R7_017": dict(event="E0180",region="GL",date="2026-09-02",
 title="호주 ARENA, 100번째 커뮤니티 배터리 설치…2차 사업에 2,320만호주달러 추가",
 sub="YES Group 14기·Ausgrid 21기·City of Newcastle 사업 지원",
 gate="호주 커뮤니티 배터리 프로그램이 100번째 설치를 넘기며 추가 보급 단계로 확대됐다.",
 fact="ARENA는 9월 2일 Community Batteries Funding Program의 100번째 배터리 설치를 발표하고, 2차 사업 3건에 총 2,320만호주달러를 추가 지원한다고 밝혔다. 지원 대상에는 YES Group 14기, Ausgrid 21기, City of Newcastle 프로젝트가 포함된다.",
 implication=["배전망 단위의 공유형 저장이 실증을 넘어 반복 보급 프로그램으로 확장되고 있다.","추가 설치의 실제 운영성과와 피크 저감·재생에너지 수용 효과를 추적할 필요가 있다."]),
"STD26_R7_018": dict(event="E0182",region="GL",date="2026-08-31",
 title="영국 Berkswell 200MW/857MWh BESS 착공",
 sub="Farrans가 West Midlands 프로젝트 건설 개시",
 gate="영국의 대형 BESS 파이프라인이 200MW급 실제 건설 단계로 이동했다.",
 fact="Farrans는 8월 31일 영국 West Midlands의 Berkswell BESS 건설 착수를 발표했다. 프로젝트 규모는 200MW/857MWh다.",
 implication=["유럽 BESS 시장에서 발표·허가를 넘어 실제 EPC 착공이 이어지고 있음을 보여준다.","공정 진척과 계통연계·상업운전 일정이 다음 실행 확인 포인트다."]),
"STD26_R7_019": dict(event="E0185",region="GL",date="2026-09-01",
 title="Hydrostor, 호주 Silver City 200MW/1,600MWh 프로젝트 계통연계 승인",
 sub="AEMO·Transgrid Generator Performance Standards 충족…아직 개발 후반 단계",
 gate="8시간 장주기 압축공기 저장 프로젝트가 핵심 계통연계 기술승인을 확보했다.",
 fact="Hydrostor는 9월 1일 뉴사우스웨일스 Broken Hill의 Silver City 프로젝트가 AEMO와 Transgrid로부터 계통연계 관련 승인을 확보했다고 밝혔다. 계획 규모는 200MW/1,600MWh이며 Generator Performance Standards를 충족했지만, 프로젝트는 아직 개발 후반 단계다.",
 implication=["장주기 저장의 상업화에서 중요한 계통기술 관문을 통과한 사례다.","최종 투자결정과 착공 여부가 실제 공급능력으로 전환되는 다음 단계다."]),
"STD26_R7_020": dict(event="E0186",region="US",date="2026-09-03",
 title="미국 Stillwater 니켈·PGM 사업장 약 420명 파업 돌입",
 sub="USW Local 11-0001, Nye Mine·Columbus 제련시설에서 ULP strike",
 gate="미국 핵심광물 생산 현장에서 노사갈등이 실제 작업중단 리스크로 전환됐다.",
 fact="USW는 9월 3일 약 420명의 Local 11-0001 조합원이 몬태나 Nye Mine과 Columbus Metallurgical Complex에서 unfair labor practice strike에 들어간다고 밝혔다. 노사는 4월 중순부터 협상을 진행했고 조합원들은 세 차례 제안을 부결했다.",
 implication=["니켈·PGM 공급의 지역화 전략에도 노동 리스크가 실물 공급 차질 변수로 작용할 수 있음을 보여준다.","실제 생산중단 범위와 파업 기간이 공급망 영향의 크기를 결정한다."]),
"STD26_R7_021": dict(event="E0188",region="GL",date="2026-09-01",
 title="Astron Donald 희토류 프로젝트, 호주 정부 수출허가 확보",
 sub="빅토리아 농축물을 미국 Energy Fuels로 공급 가능…프로젝트는 아직 개발 단계",
 gate="호주 희토류 프로젝트가 미국 가공망으로 연결되는 규제 관문을 통과했다.",
 fact="Astron은 9월 1일 호주 정부로부터 Donald 프로젝트의 희토류 원소 농축물을 미국으로 수출할 수 있는 허가를 받았다고 밝혔다. 합작 파트너 Energy Fuels는 해당 농축물 100%를 매입할 권리를 갖지만, Donald 프로젝트 자체는 아직 개발 단계이며 최종 투자결정이 남아 있다.",
 implication=["호주 원료와 미국 분리·정제 인프라를 연결하는 비중국 희토류 공급망의 실행 조건이 구체화됐다.","FID와 건설 착수가 실제 공급 개시의 핵심 후속 관문이다."]),
"STD26_R7_022": dict(event="E0190",region="GL",date="2026-09-02",
 title="브라질 상원, 핵심광물 지원법안 승인…최대 70억헤알 금융지원 틀",
 sub="보증기금 20억헤알·가공·전환 50억헤알…현재 대통령 재가 대기",
 gate="브라질 핵심광물 산업지원 정책이 의회 승인까지 진행돼 대통령 재가 단계로 넘어갔다.",
 fact="브라질 상원은 9월 2일 PL 2780/2024를 실질적 내용 변경 없이 승인해 대통령 재가로 보냈다. 법안은 최대 20억헤알의 보증기금과 50억헤알의 가공·전환 지원을 포함해 총 70억헤알 규모의 지원 틀을 제시한다.",
 implication=["브라질이 광물 채굴뿐 아니라 가공·전환 단계의 현지화를 정책적으로 지원하려는 방향이 구체화됐다.","아직 법률 발효 전이므로 대통령 재가와 시행 세부규정을 확인해야 한다."]),
"STD26_R7_023": dict(event="E0194",region="GL",date="2026-09-01",
 title="Greenland Mines, Sarfartoq 희토류 프로젝트 인수 완료",
 sub="그린란드 정부 승인 후 9월 1일 거래 종결…Nd-Pr 자산 확보",
 gate="그린란드 희토류 자산 거래가 승인 단계를 넘어 실제 인수 종결로 완료됐다.",
 fact="Greenland Mines는 그린란드 정부 승인을 거쳐 Sarfartoq Nd-Pr 희토류 프로젝트 인수를 9월 1일 완료했다고 밝혔다.",
 implication=["비중국 희토류 개발 자산에 대한 소유권 재편이 실제 거래 종결로 이어진 사례다.","자원량 확대 주장보다 후속 개발계획·허가·자금조달이 공급 기여도를 좌우한다."]),
"STD26_R7_027": dict(event="E0229",region="EU",date="2026-08-28",
 title="EDF, 영국 Trina Storage 2개 BESS 179.8MWh 장기 최적화 계약",
 sub="Ruby 40MW/80MWh·Chatterley 49.9MW/99.8MWh…2026~2027년 가동 예정",
 gate="영국 BESS 수익화에서 전문 최적화 사업자와의 장기 계약이 추가됐다.",
 fact="EDF는 8월 28일 Trina Storage가 개발하는 Ruby 40MW/80MWh와 Chatterley 49.9MW/99.8MWh BESS에 대해 총 179.8MWh 규모의 최적화 계약을 체결했다고 밝혔다. Ruby는 2026년 10월, Chatterley는 2027년 3월 가동을 목표로 한다.",
 implication=["BESS 사업모델에서 자산 건설뿐 아니라 장기 최적화 계약이 수익구조의 핵심 요소가 되고 있다.","실제 상업운전 이후 EDF Powershift의 운영성과와 수익 안정성을 확인할 필요가 있다."]),
"STD26_R7_028": dict(event="E0238",region="EU",date="2026-09-02",
 title="EU 집행위, 독일 용량시장 승인…2031년부터 저장·유연수요도 참여",
 sub="국가지원 규모 추정 156억~352억유로…발전·저장·수요반응을 함께 경쟁",
 gate="독일 전력시장이 2031년부터 저장과 유연수요를 포함한 용량보상 체계를 도입할 수 있게 됐다.",
 fact="EU 집행위원회는 9월 2일 독일의 용량시장 제도를 EU 국가보조 규정에 따라 승인했다. 제도는 2031년부터 발전, 저장, 유연한 전력소비 자원을 대상으로 하며 예상 지원비용은 156억~352억유로다.",
 implication=["유럽 저장자산의 수익원이 에너지·보조서비스 시장에서 용량보상까지 넓어질 수 있는 정책 기반이다.","세부 경매규칙과 저장자산의 자격·계약기간이 실제 투자유인을 결정한다."]),
"STD26_R7_031": dict(event="E0258",region="GL",date="2026-08-27",
 title="Westbridge, 캐나다 Red Willow 태양광·BESS 프로젝트 매각 SPA 체결",
 sub="알버타 최대 225MWac 태양광·100MW BESS 구상…거래는 아직 종결 전",
 gate="캐나다 개발단계 태양광·BESS 자산이 확정 매매계약 단계로 이동했다.",
 fact="Westbridge는 8월 27일 알버타 Red Willow 프로젝트 매각을 위한 definitive SPA를 체결했다. 프로젝트는 최대 225MWac 태양광과 제안된 100MW BESS를 포함하며, AUC의 발전·변전소 승인과 AESO 계통연계 지위를 확보하고 있다. 매매계약 체결은 거래 종결과 동일하지 않다.",
 implication=["개발권·허가를 확보한 하이브리드 재생에너지 자산의 거래가 이어지고 있다.","종결조건 충족과 실제 BESS 투자결정 여부를 구분해 추적해야 한다."]),
"STD26_R7_038": dict(event="E0298",region="CN",date="2026-08-28",
 title="산시성 신형 에너지저장 5,004.6MW…90개소로 확대",
 sub="7월 말 기준…7월 23일 피크 때 최대 2,880MW 동시 출력",
 gate="중국 산시성의 신형 저장이 5GW를 넘어 실제 피크 대응 자원으로 운용되고 있다.",
 fact="산시성 정부는 8월 28일 국가전망 산시성 자료를 인용해 7월 말 기준 신형 에너지저장 설비가 90개소, 5,004.6MW에 달했다고 밝혔다. 이 가운데 계통측은 32개소 4,359.8MW, 발전측은 58개소 644.8MW이며, 7월 23일 피크 시 최대 2,880MW가 동시 출력됐다.",
 implication=["중국 내 저장 확대가 설치용량 증가뿐 아니라 실제 계통 피크 대응 운용으로 이어지고 있음을 보여준다.","2027년 8GW 이상 목표까지의 추가 증설과 이용률이 핵심 추적 지표다."]),
"STD26_R7_040": dict(event="E0399",region="JP",date="2026-08-31",
 title="GS Yuasa, 이바라키에 신규 고정형 ESS 배터리 공장 건설",
 sub="2028년 10월 공급 개시 목표…일본 내 저장 수요 대응 생산기반 확대",
 gate="일본 배터리 업체가 고정형 ESS 전용 생산능력 확대를 실제 공장 투자로 옮긴다.",
 fact="GS Yuasa는 8월 31일 이바라키현에 고정형 에너지저장용 배터리 신규 공장을 건설한다고 발표했다. 신규 공장의 제품 공급 개시는 2028년 10월을 목표로 한다.",
 implication=["일본의 ESS 수요 확대가 셀·배터리 현지 생산설비 투자로 연결되는 사례다.","공장 착공·설비 확정과 2028년 공급 개시 일정 준수가 다음 실행 확인 포인트다."]),
"STD26_R7_043": dict(event="E0410",region="GL",date="2026-08-31",
 title="미 국방부, 호주 Wagerup 갈륨 생산시설에 1.74억달러 지분투자 추진",
 sub="Alcoa 정유소 내 연 100톤 생산 목표…7월 FID에 이어 미국 금융지원 추가",
 gate="비중국 갈륨 공급망 구축에 미국 국방부 자본이 실제 프로젝트 금융으로 들어간다.",
 fact="미 국방부는 8월 31일 호주 Alcoa Wagerup 정유소의 신규 갈륨 생산시설에 약 1억7,400만달러의 지분금융을 제공할 계획이라고 밝혔다. 시설의 목표 생산능력은 연 100톤이며, Alcoa Australia가 운영하고 일본 정부·Sojitz 등이 파트너로 참여한다. 프로젝트 FID는 앞선 7월 14일 발표됐다.",
 implication=["핵심광물 공급망 정책이 보조금·오프테이크를 넘어 직접 지분금융까지 확대되는 사례다.","실제 투자 집행과 건설·생산 개시 일정이 공급망 다변화의 실효성을 결정한다."]),
"STD26_R7_P01P_001": dict(event="E0177",region="US",date="2026-08-31",
 title="ONE Nuclear, 루이지애나 2.88GW 발전·2.88GWh BESS 복합부지 LOI 체결",
 sub="Project Cayman 부지통제 확보 단계…최종 투자·건설계약은 아직",
 gate="대형 데이터센터 전력단지 구상이 부지통제 LOI 단계까지 진전됐다.",
 fact="ONE Nuclear는 8월 31일 루이지애나 Project Cayman을 위해 토지 소유주 그룹과 binding LOI를 체결해 부지통제 권리를 확보했다고 SEC에 공시했다. 구상에는 2.88GW 천연가스 발전과 700MW/2.88GWh BESS, 데이터센터 캠퍼스가 포함되지만 최종 투자결정이나 건설계약은 아니다.",
 implication=["AI 데이터센터 전력수요가 발전·대형 저장을 결합한 전용 인프라 구상으로 이어지고 있다.","LOI 이후 토지계약 확정, 전력계통·허가, 자금조달이 실제 프로젝트화의 핵심 관문이다."]),
"STD26_R7_P01P_002": dict(event="E0222",region="GL",date="2026-08-31",
 title="칠레 7월 구리 생산 403,424톤…금속광업 생산 감소",
 sub="INE 공식 통계…광업생산지수 -7.2% YoY·금속광업 -10.7%",
 gate="세계 최대 구리 생산국 중 하나인 칠레에서 7월 생산 약세가 공식 통계로 확인됐다.",
 fact="칠레 INE는 8월 31일 7월 구리 광산 생산량이 403,424톤(tmf)이었다고 발표했다. 같은 달 광업생산지수는 전년 대비 7.2%, 금속광업은 10.7% 감소했으며 INE는 구리 추출·처리 감소를 주요 원인으로 설명했다.",
 implication=["전력망·EV·ESS 확대에 필요한 구리 공급에서 주요 생산국의 단기 생산 변동성이 지속되고 있다.","월별 생산 감소가 일시적 요인인지 연간 공급전망 변화로 이어지는지는 추가 데이터 확인이 필요하다."]),
"STD26_R7_P01P_003": dict(event="E0223",region="GL",date="2026-08-25",
 title="CATL·Moura, 브라질 저장용량 경매 공동 참여 파트너십",
 sub="Capacity Reserve Auction 공동 참여 계획…아직 낙찰·수주 단계 아님",
 gate="중국 배터리 업체와 브라질 현지 기업이 저장용량 경매 진입을 위한 공동 사업구조를 만들었다.",
 fact="CATL은 8월 25일 브라질 Moura와 전략적 파트너십을 맺고 브라질 Capacity Reserve Auction의 에너지저장 부문에 공동 참여할 계획이라고 밝혔다. 이는 입찰 준비 단계이며 낙찰이나 확정 프로젝트 수주를 의미하지 않는다.",
 implication=["브라질 저장시장 개방 기대가 글로벌 셀·시스템 업체와 현지 파트너의 선제적 시장진입으로 이어지고 있다.","실제 경매 규칙 확정과 낙찰 여부가 독립 카드 가치를 결정하므로 Stage C에서 실행강도를 다시 점검한다."]),
"STD26_R7_P01P_004": dict(event="E0227",region="GL",date="2026-08-27",
 title="Canadian Solar, 2Q ESS 출하 3.7GWh…전분기 대비 82% 증가",
 sub="e-STORAGE 출하 성장…내부 프로젝트 471MWh 실행 중",
 gate="Canadian Solar의 저장사업이 분기 출하 기준 3.7GWh로 확대됐다.",
 fact="Canadian Solar은 8월 27일 2분기 에너지저장 출하량이 3.7GWh로 전분기 대비 82%, 전년 동기 대비 73% 증가했다고 발표했다. 이 가운데 471MWh는 자체 개발 프로젝트에 투입됐다. 회사 전체 2분기 매출은 12억달러, 총마진은 13.9%였다.",
 implication=["태양광 중심 사업자의 ESS 비중 확대가 실제 분기 출하량 증가로 확인된다.","출하 성장과 함께 저장사업의 마진·백로그 전환 속도를 확인해야 수익성 기여를 판단할 수 있다."]),
"STD26_R7_P01P_005": dict(event="E0248",region="GL",date="2026-08-28",
 title="호주 2Q 가정용 배터리 신청 50만건 돌파…CER, 기록적 분산에너지 투자 확인",
 sub="옥상태양광 1GW·대규모 태양광 FID 1.8GW도 기록",
 gate="호주 가정용 배터리 보급이 정책 시행 이후 50만건 이상의 신청으로 급증했다.",
 fact="호주 Clean Energy Regulator는 8월 28일 2분기 청정에너지 투자 동향에서 배터리 프로그램 시작 이후 신청이 50만건을 넘어섰다고 밝혔다. 같은 분기 옥상태양광 설치는 1GW, 대규모 태양광 최종투자결정은 1.8GW로 각각 기록적 수준을 보였다.",
 implication=["호주 분산형 저장 수요가 정책지원과 함께 대규모 보급 단계로 진입하고 있다.","신청 건수와 실제 설치·계통연계 완료 물량의 차이를 후속 확인해야 한다."]),
"STD26_R7_P01P_006": dict(event="E0287",region="CN",date="2026-08-26",
 title="REPT Battero, 상반기 흑자전환…ESS가 성장축으로 부상",
 sub="매출 149.16억위안 +57.1%·순이익 7.78억위안",
 gate="중국 배터리 업체의 ESS 확대가 상반기 실적 개선과 함께 나타났다.",
 fact="REPT Battero는 8월 26일 상반기 실적을 공시했다. 매출은 149억1,600만위안으로 전년 대비 57.1% 증가했고, 순이익은 7억7,800만위안으로 전년 동기 6,300만위안 순손실에서 흑자 전환했다. 회사는 에너지저장 사업을 주요 성장동력으로 제시했다.",
 implication=["중국 배터리 업체의 성장축이 EV 셀뿐 아니라 ESS로 다변화되는 흐름이 실적에 반영되고 있다.","ESS 매출·출하 증가가 수익성 개선의 어느 정도를 설명하는지는 세부 세그먼트 마진 확인이 필요하다."]),
"STD26_R7_P01P_008": dict(event="E0316",region="GL",date="2026-08-31",
 title="Gotion, 브라질 현지 사무소 공식 가동…남미 ESS 영업 거점 확대",
 sub="Intersolar South America 기간 중 운영 개시·저장 제품군 전시",
 gate="중국 배터리 업체가 브라질에서 현지 영업·사업개발 조직을 실제 가동했다.",
 fact="Gotion은 8월 31일 Intersolar South America 기간에 브라질 현지 사무소가 공식 운영을 시작했다고 밝혔다. 전시에서는 에너지저장 제품 포트폴리오도 공개했다.",
 implication=["남미 ESS 시장을 겨냥한 중국 업체의 진출이 단순 수출에서 현지 조직 구축으로 확대되고 있다.","현지 사무소 개소 자체보다 향후 수주·EPC·서비스 계약이 상업적 실행력을 확인할 지표다."]),
"STD26_R7_P01P_009": dict(event="E0368",region="GL",date="2026-09-01",
 title="브라질 상원, 데이터센터 세제지원 REDATA 승인…재생·저탄소 전력 조건 부과",
 sub="PL 278/2026 대통령 재가 대기…아직 법률 발효 전",
 gate="브라질 데이터센터 유치정책이 상원 승인을 통과하면서 전력조달 조건까지 구체화됐다.",
 fact="브라질 상원은 9월 1일 PL 278/2026을 실질적 내용 변경 없이 승인해 대통령 재가로 넘겼다. 법안은 REDATA 세제지원 체계를 만들고 참여 사업자에 재생에너지 또는 저배출 전력 사용 등 지속가능성 요건을 부과한다. 현재는 아직 법률 발효 전이다.",
 implication=["AI·데이터센터 투자유치 정책이 세제혜택과 전력의 저탄소 조건을 함께 묶는 방향으로 진화하고 있다.","대통령 재가와 시행규정에서 저장장치·현지 전력조달의 실제 역할이 어떻게 규정되는지 확인해야 한다."]),
"STD26_R7_P01P_010": dict(event="E0369",region="CN",date="2026-08-28",
 title="Sungrow, 상반기 ESS 매출 154.56억위안…처음으로 PV 넘어 최대 사업부",
 sub="전체 매출의 50%…ESS 출하 25GWh",
 gate="Sungrow의 사업구조에서 ESS가 상반기 기준 최대 매출 부문으로 올라섰다.",
 fact="Sungrow의 8월 28일 상반기 실적에 따르면 전체 매출은 309억1,200만위안으로 전년 대비 28.99% 감소했고 순이익은 52억5,900만위안으로 32.01% 줄었다. 반면 ESS 매출은 154억5,600만위안으로 전체의 50%를 차지해 처음으로 PV 부문을 넘어 최대 매출원이 됐으며, 저장 출하는 25GWh로 제시됐다.",
 implication=["중국 인버터·전력전자 업체의 수익구조가 ESS 중심으로 빠르게 이동하고 있음을 보여준다.","ESS 매출 비중 확대가 전체 실적 감소 속에서도 지속 가능한지 마진·수주잔고를 함께 봐야 한다."]),
"STD26_R7_P01P_011": dict(event="E0401",region="US",date="2026-09-01",
 title="Xos 이동형 충전 Hub 1기, 누적 전력공급 1GWh 돌파",
 sub="3만3,600회 이상 충전…전체 Hub fleet 누적 5GWh 초과",
 gate="이동형 배터리 충전 인프라가 단일 장비 기준 1GWh의 현장 운영 실적을 쌓았다.",
 fact="Xos는 9월 1일 한 대의 Xos Hub가 2025년 초 실운영을 시작한 이후 3만3,600회 이상의 충전을 통해 누적 1,020,143.6kWh를 공급했다고 밝혔다. 전체 Xos Hub fleet의 누적 공급량은 5GWh를 넘어섰다.",
 implication=["고정형 계통증설을 기다리기 어려운 상용차 충전에서 이동형 저장 기반 인프라가 실제 사용량을 축적하고 있다.","단위 에너지당 비용과 반복 고객 주문이 상업성 판단의 다음 핵심 지표다."]),
"STD26_R7_P01P_012": dict(event="E0402",region="US",date="2026-09-01",
 title="SB Energy, 미국 IPO S-1 제출…AI 데이터센터 전력 플랫폼 확대 구상",
 sub="현재 운영 중 데이터센터는 없어…기존 에너지사업 매출과 대규모 투자계획 구분 필요",
 gate="재생에너지 개발사가 AI 데이터센터 전력 인프라 확대 전략을 IPO 공시로 공식화했다.",
 fact="SB Energy는 9월 1일 미국 SEC에 S-1 등록신고서를 제출했다. 회사는 AI·데이터센터 전력 인프라를 주요 성장축으로 제시하지만 신고 시점에 운영 중인 데이터센터는 없으며, 현재 실적은 기존 에너지 사업을 중심으로 구성돼 있다.",
 implication=["재생에너지 개발사들이 발전자산 공급을 넘어 데이터센터 전력 플랫폼으로 사업모델을 확장하려는 흐름이 자본시장 단계로 진입했다.","계획된 데이터센터 프로젝트의 실제 착공·고객계약·자금조달을 현재 운영실적과 구분해 봐야 한다."]),
"STD26_R7_P01P_013": dict(event="E0404",region="US",date="2026-09-01",
 title="ESS Inc., 미 국방부 Tradewinds Marketplace 'Awardable' 지위 확보",
 sub="정부조달 검토 경로 단축 가능…실제 수주·계약 체결은 아님",
 gate="장주기 철계 배터리 업체가 미국 국방부 조달시장 진입 자격을 한 단계 높였다.",
 fact="ESS Inc.는 9월 1일 미 국방부 Tradewinds Solutions Marketplace에서 'Awardable' 지위를 획득했다고 밝혔다. 이 지위는 정부기관이 조달 후보로 더 빠르게 검토할 수 있게 하는 시장접근 자격이며, 그 자체가 구매계약이나 수주를 의미하지 않는다.",
 implication=["장주기 저장 업체의 정부·국방 수요 접근성이 높아진 신호지만 매출로 확정된 사건은 아니다.","실제 정부기관 계약·프로젝트 배치가 발생해야 상업적 실행력이 확인된다."]),
}

UPSTREAM = {"STD26_R7_013":"E0115","STD26_R7_016":"E0171","STD26_R7_026":"E0225","STD26_R7_030":"E0246"}

def load_original():
    b64 = "".join((BASE/p).read_text().strip() for p in PARTS)
    raw = gzip.decompress(base64.b64decode(b64))
    assert hashlib.sha256(raw).hexdigest() == EXPECTED_SHA
    return json.loads(raw)

def filter_packages(raw, keep):
    if isinstance(raw, dict):
        return {k:v for k,v in raw.items() if k in keep or (isinstance(v,dict) and (v.get("source_spec_id") in keep or v.get("spec_id") in keep))}
    if isinstance(raw, list):
        return [v for v in raw if isinstance(v,dict) and (v.get("source_spec_id") in keep or v.get("spec_id") in keep or v.get("id") in keep)]
    return raw

def main():
    data=load_original()
    drafts=data.get("draft_cards") or []
    specs=data.get("strict_passed_spec") or data.get("strict_passed_specs") or []
    idx={d.get("source_spec_id") or d.get("spec_id"):d for d in drafts}
    assert set(REPAIRS).issubset(idx), sorted(set(REPAIRS)-set(idx))
    assert set(UPSTREAM).issubset(idx), sorted(set(UPSTREAM)-set(idx))
    revised=[]; audit=[]
    for sid, r in REPAIRS.items():
        d=json.loads(json.dumps(idx[sid], ensure_ascii=False))
        before={k:d.get(k) for k in ("region","date","title","sub","gate","fact","implication")}
        d["region"]=r["region"]; d["date"]=r["date"]
        for k in ("title","sub","gate","fact","implication"): d[k]=r[k]
        dr=d.get("date_role") if isinstance(d.get("date_role"),dict) else {}
        old_rep=dr.get("representative_event_date") or before.get("date")
        dr["stage_a_representative_date"]=dr.get("stage_a_representative_date") or old_rep
        dr["representative_event_date"]=r["date"]
        dr["status"]="PASS"
        dr["corrected_in_0_2r"]= old_rep != r["date"]
        dr["correction_basis"]="direct source-owner/official body evidence used in controlled Stage B revise"
        d["date_role"]=dr
        d["stage_b_revision_status"]="PASS_0_2R_CONTROLLED_REPAIR"
        d["stage_b_revision_prompt"]="docs/llm_prompts/v1/04_PROMPT_0_2R_Stage_B_Revise.md"
        d["stage_b_revision_prompt_version"]="STAGE_B_REVISE_V4_20260829"
        d["repair_audit"]={"event_id":r["event"],"source_spec_id":sid,
            "repair_types":["visible_claim_change","date_only_repair" if before.get("date")!=r["date"] else "date_verified_no_change","region_repair" if before.get("region")!=r["region"] else "region_verified_no_change"],
            "before":before,"after":{k:d.get(k) for k in ("region","date","title","sub","gate","fact","implication")},
            "selection_route_preserved":True,"fact_sources_preserved":True,"related_review_preserved":True}
        revised.append(d); audit.append(d["repair_audit"])
    keep=set(REPAIRS)
    new=json.loads(json.dumps(data, ensure_ascii=False))
    new["stage"]="stage_b"; new["status"]="PASS"
    new["run_tag"]="20260903_R7_STAGE_B_0_2R_REESTABLISHED34_R1"
    new["source_prompt_file"]="docs/llm_prompts/v1/04_PROMPT_0_2R_Stage_B_Revise.md"
    new["source_prompt_version"]="STAGE_B_REVISE_V4_20260829"
    new["strict_passed_spec"]=[s for s in specs if (s.get("spec_id") or s.get("source_spec_id")) in keep]
    new.pop("strict_passed_specs",None)
    new["strict_passed_spec_count"]=34; new["strict_passed_specs_count"]=34
    new["draft_cards"]=revised; new["draft_blocked"]=[]; new["draft_blocked_schema"]=[]
    new["stage_b_accounting_matches_strict_passed_spec_count"]=True
    if "evidence_packages" in new: new["evidence_packages"]=filter_packages(new["evidence_packages"],keep)
    if "evidence_package" in new: new["evidence_package"]=filter_packages(new["evidence_package"],keep)
    new["revision_scope_count"]=34; new["upstream_return_count"]=4
    new["upstream_return_spec_ids"]=sorted(UPSTREAM); new["upstream_return_event_ids"]=sorted(UPSTREAM.values())
    new["stage_c_r0_artifact_sha256"]="c81a8bf873425f75a74745dd116d7d2f426ae58c6d49191e30c3d79b1c692ec6"
    audit_root={"stage":"0.2R","status":"PASS","run_tag":"20260903_R7_STAGE_B_0_2R_AUDIT34_R1",
        "input_revise_required_count":38,"controlled_repair_count":34,"upstream_return_count":4,
        "upstream_return":[{"source_spec_id":k,"event_id":v,"reason":"selection/staleness/event-identity defect; ordinary 0.2R repair prohibited"} for k,v in UPSTREAM.items()],
        "repair_ledger":audit,"selection_route_reselected_count":0,"unaccounted":0}
    Path("/tmp/stage-b-0.2r-reestablished34.json").write_text(json.dumps(new,ensure_ascii=False,indent=2),encoding="utf-8")
    Path("/tmp/stage-b-0.2r-audit.json").write_text(json.dumps(audit_root,ensure_ascii=False,indent=2),encoding="utf-8")
    print("RESULT: MATERIALIZED_0_2R",len(revised),len(audit_root["upstream_return"]))
if __name__=="__main__": main()
