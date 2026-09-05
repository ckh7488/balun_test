# 구매요청서 양식 입력안 — DigiKey 우선 / 2026-09-03

부품 구매처를 **DigiKey 한국으로 통합**한다. PCB 제작은 JLCPCB, 한국 DigiKey에서 주문이 불가능한 HAKKO 인두팁 두 종류만 국내 구매 예외로 둔다. 사용자 지시에 따라 Mini-Circuits 직접 구매 및 LCSC 분산 구매는 이번 기본 주문안에서 제외했다. 상신·장바구니 추가·주문·결제는 실행하지 않았다.

작성용 예상환율은 **1 USD = 1,370원**이다. DigiKey 품목은 한국 페이지 원화 가격을 그대로 사용하고, JLCPCB USD 제작비만 환산한다. 조회 가격은 부가세 별도 예상액이며 공식 견적서가 아니다.

| 구분 | 예상액(원, 부가세 별도) |
| --- | ---: |
| JLCPCB — 3설계 × 5장 = 제작 15장 | 202,610 |
| DigiKey — 전자부품·RF 부속·플럭스·납흡입선 10품목 | 489,458 |
| 국내 — HAKKO 인두팁 2품목 | 16,640 |
| **작성 가능 예상 소계** | **708,708** |

운임·부대비, 세금, RJ45 개조 플러그, 추가 DFM, REF 하네스 및 기구물은 별도 미확정이다. 위 금액은 모든 추가 항목까지 포함한 최종 발주 총액이 아니다. 사내 손납땜이므로 PCBA·스텐실 비용은 포함하지 않는다.

**SMA는 Samtec 후보 가격을 반영한 예산이다.** 현재 CAD의 MyAntenna와 접점 위치는 명목 치수상 수용 가능하지만 권장 패드/PCB 두께까지 동일한 제품은 아니다. 완성 두께·공차 및 제조파일 정합 확인 후 확정한다. 이 문서는 PCB 또는 풋프린트 변경/제조 승인을 수행한 결과가 아니다.

## 사용자 확인 반영

- 실사용 8장: Molex 2 + RJ45 4(BONDED 2/FLOAT 2) + LLC M12 수 측 2. 제작 예산은 15장, 여분 7장은 미조립.
- 슬립링 M12 암측 PCB와 암커넥터는 제외. 기존 라이다–슬립링 케이블의 라이다측을 RJ45로 개조하여 RJ45 지그를 공유.
- LLC M12 수커넥터는 사내품으로 신규 구매하지 않음. **PCB에 잘 꽂히는 것은 사용자 확인 완료.** 필요한 2개 확보·전기적 핀맵·무전원 확인은 별도.
- 사용자 확인 Mini-Circuits 직구 장바구니 **$215 = 294,550원**. 포함 품목/세금 내역은 독립 확인하지 않았으며 발룬만의 가격으로 간주하지 않음.
- DigiKey에서 발룬 26 + TE 종단기 6 + THRU 1은 **294,191원(배송·세금 별도)**. 사용자 지시대로 직구 대신 DigiKey 선택.

## 상단 항목

| 항목 | 입력안 |
| --- | --- |
| 제목 | **[실제 과제명] 이더넷 VNA 측정 지그-PCB 및 부품 구매** |
| 과제명 / 적용과제 | 실제 회사 과제명 및 코드 확인. 화면에 선택된 기본값을 그대로 사용하지 않음 |
| 장비명(계약서 기준) | 회사 등록 장비명 확인. 해당 없으면 사내 작성 기준에 따라 처리 |
| 장비명(상세설계 기준) | 이더넷 VNA 측정 지그 — 작성안 |
| 적용 구분 | 사내 검증용이므로 **자체시험 추천**. 실제 개발/시험 분류는 회사 기준 확인 |
| 선진행 | 미진행이면 제외. 실제 선진행 승인 유무 확인 |
| 구매 목적 | 슬립링, RJ45 및 LLC-13M-1 케이블의 이더넷 전송 특성(S11~S22, NEXT/FEXT)을 VNA로 비교·검증하기 위한 측정 지그 PCB, 구성 부품 및 조립용 소모품 구매. |
| 거래처명 | 복수 거래처 (품목별 비고 참조) |
| 기존/신규 거래 | 회사 거래처 등록 이력 확인 후 선택 |
| 거래처 담당자/연락처 | 구매처별 실제 주문 담당자 확인. 온라인 주문은 해당 사실과 확인 가능한 연락처 기재 |
| 요청 납기일 | 희망 날짜 확인 필요. 최종 제조파일 승인 및 공급처 출고일 확인 후 확정 |
| 대금 결제 조건 | 협의 작성안. 해외 온라인 주문의 선결제 및 회사 결제 절차 확인 후 선택 |
| 이전문서번호 / 재제작 사유 | 신규 제작안. 이전 발주가 있었다면 해당 문서번호와 사유 보완 |
| 발주 유무 | **발주 요청** — 현재 미발주 |
| 통화 | **WON**, 부가세 별도. USD 항목은 사용자 지정 예상환율 **1,370원/USD**로 환산 |


## 개별 품목표 — 구매 링크 포함

금액 단위 원, 부가세 별도. 모든 제품을 개별 기재하며 “외 n종”으로 생략하지 않는다. 수량은 이미 예비분을 포함하므로 실사용 수량을 다시 더하지 않는다.

| 번호 | 한글품명 | 부품번호(업체품번) | 도면번호(제조사) | 수량 | 예상단가 | 예상금액 | 개별 구매 링크 |
| ---: | --- | --- | --- | ---: | ---: | ---: | --- |
| 1 | RJ45 측정 지그 PCB | balun_eth_rj45 | JLCPCB | 5 | 13,538.4 | 67,692 | [JLCPCB 구매/견적](https://cart.jlcpcb.com/quote) |
| 2 | 슬립링 Molex 측 PCB | balun_slipring_molex | JLCPCB | 5 | 13,491.8 | 67,459 | [JLCPCB 구매/견적](https://cart.jlcpcb.com/quote) |
| 3 | LLC M12 수 측 PCB | balun_llc16 | JLCPCB | 5 | 13,491.8 | 67,459 | [JLCPCB 구매/견적](https://cart.jlcpcb.com/quote) |
| 4 | RF 발룬 | ADT2-1T+ | Mini-Circuits | 26 | 10,011 | 260,286 | [DigiKey 구매/견적](https://www.digikey.kr/ko/products/detail/mini-circuits/ADT2-1T/13927001) |
| 5 | SMA PCB 커넥터 | SMA-J-P-H-ST-EM1 | Samtec | 30 | 3,817 | 114,510 | [DigiKey 구매/견적](https://www.digikey.kr/ko/products/detail/samtec-inc/SMA-J-P-H-ST-EM1/2602450) |
| 6 | RJ45 커넥터 | RJE591885401 | Amphenol | 5 | 8,052 | 40,260 | [DigiKey 구매/견적](https://www.digikey.kr/ko/products/detail/amphenol-icc-commercial-products/RJE591885401/6189327) |
| 7 | 테스트 포인트 | 5001 | Keystone | 10 | 336.3 | 3,363 | [DigiKey 구매/견적](https://www.digikey.kr/ko/products/detail/keystone-electronics/5001/255327) |
| 8 | Molex 커넥터 | 5055680571 | Molex | 10 | 1,027 | 10,270 | [DigiKey 구매/견적](https://www.digikey.kr/ko/products/detail/molex/5055680571/7807019) |
| 9 | 0805 0Ω 저항 | RC0805JR-070RL | YAGEO | 10 | 24.5 | 245 | [DigiKey 구매/견적](https://www.digikey.kr/ko/products/detail/yageo/RC0805JR-070RL/728216) |
| 10 | SMA 50Ω 종단기 | 2467938-1 | TE Connectivity | 6 | 4,004 | 24,024 | [DigiKey 구매/견적](https://www.digikey.kr/ko/products/detail/te-connectivity-linx/2467938-1/22535225) |
| 11 | SMA THRU 어댑터 | ADP-SMAF-SMAF-G | TE Connectivity / Linx | 1 | 9,881 | 9,881 | [DigiKey 구매/견적](https://www.digikey.kr/ko/products/detail/te-connectivity-linx/ADP-SMAF-SMAF-G/9826669) |
| 12 | 전자용 플럭스 | SMD291-10M | Chip Quik | 1 | 17,213 | 17,213 | [DigiKey 구매/견적](https://www.digikey.kr/ko/products/detail/chip-quik-inc/SMD291-10M/14636534) |
| 13 | 인두팁 1.6D | 900M-T-1.6D | HAKKO | 1 | 8,140 | 8,140 | [엘레파츠 구매/견적](https://eleparts.co.kr/goods/view?no=5274) |
| 14 | 인두팁 2.4D | 900M-T-2.4D | HAKKO | 1 | 8,500 | 8,500 | [디바이스마트 구매/견적](https://www.devicemart.co.kr/goods/view?no=2291) |
| 15 | 납흡입선 1.52mm | 80-2-5 | Chemtronics | 1 | 9,406 | 9,406 | [DigiKey 구매/견적](https://www.digikey.kr/ko/products/detail/chemtronics/80-2-5/306981) |
| 16 | 운임·부대비 | 견적 참조 | 해당 업체 | 1식 | 확인 필요 | 확인 필요 | 최종 결제/견적 기준 |

PCB는 기성품 상품 링크가 없으므로 공통 JLCPCB 주문창에서 설계별 승인 Gerber를 각각 사용한다. 1–3번을 한 종류로 묶어 주문하지 않는다. 원화 단가는 PCB 로트금액을 수량으로 나눠 소수 2자리로 표시했다.

- **실단가·실금액은 구매 전이므로 공란**으로 유지한다.
- 상위도번, 과제/장비명, 거래처 담당자·연락처, 납기, 결제 조건은 실제 회사 정보로 보완한다.
- 요청서류: 업체 견적/장바구니 가격내역, 거래명세, 결제증빙. 이 파일을 업체 발행 견적서라고 표시하지 않는다.
- 재고는 2026-09-03 공개 제품 페이지 표시값이며 예약이 아니다. 장바구니 수량별 단가와 한국 배송 가능 여부를 결제 전에 재확인한다.
- Cut Tape 부품은 불필요한 Digi-Reel 서비스 추가비를 선택하지 않는다.

## 구매 변경 및 호환성 근거

### SMA — 현재 패드와 비교한 DigiKey 후보

선택 후보는 [Samtec SMA-J-P-H-ST-EM1 / SAM8857-ND](https://www.digikey.kr/ko/products/detail/samtec-inc/SMA-J-P-H-ST-EM1/2602450)이다. 50Ω SMA jack 에지마운트이며 조회 재고 67,491개, 30개 구매 시 3,817원/개다.

| 비교 | 현재 MyAntenna 풋프린트 | Samtec 접점 도면 |
| --- | --- | --- |
| 양쪽 GND 중심 간격 | 5.65mm | 5.54mm |
| 각 GND 패드/다리 폭 | 패드 1.85mm | 다리 0.81mm |
| 신호 패드/핀 폭 | 패드 1.85mm | 핀 1.27mm |
| 보드 끝에서 패드/삽입 길이 | 패드 4.50mm | 다리 3.81mm |
| 기판 두께 | 현재 주문 1.6mm | 권장 1.57mm |

명목 치수상 Samtec 접점이 현 패드 영역 안에 들어오는 **장착 가능 후보**다. 제조사 권장 패드는 현재 패드와 완전히 같지 않으며, JLC 완성 기판 두께와 공차·HASL 높이·SMA 안착 및 RF launch 성능까지 검증 완료했다는 뜻은 아니다. 실물 fit 또는 제조사 허용 범위와 생산파일 정합 확인 전 일괄 발주/제조 승인하지 않는다. [Samtec 공식 도면](https://suddendocs.samtec.com/prints/sma-j-p-x-st-em1-mkt.pdf)

비교 비용: 기존 [MyAntenna/LCSC C22467617](https://www.lcsc.com/product-detail/C22467617.html) 30개 23,989원 대비 Samtec 114,510원으로 **90,521원 증가**한다. 기존 LCSC 가격은 같은 날 재확인한 할인 단가 $0.5838이며 재고 388개였다. 현재는 DigiKey 통합 예산에 Samtec을 반영했다. MyAntenna를 중복 주문하지 않는다.

사용자가 링크한 [TE 5-1814832-2](https://www.digikey.kr/ko/products/detail/te-connectivity-amp-connectors/5-1814832-2/11611208)는 수직 THT 제품이므로 이 에지마운트 풋프린트의 대체품으로는 사용하지 않는다.

### 그대로 유지하거나 대체한 부품

- 발룬 **ADT2-1T+**: 제조사/정확한 품번 유지, 구매처만 DigiKey로 확정. 26개 × 10,011원, 재고 831개. URL에는 `+`가 빠져 있어도 실제 제조사 품번은 `ADT2-1T+`로 확인한다.
- **RJE591885401 / 5001 / 5055680571**: 기존 정확한 품번 유지. 조회 재고 각각 2,308 / 376,735 / 21,435개.
- 0Ω는 **YAGEO RC0805JR-070RL / 311-0.0ARCT-ND**로 변경. 0805 0Ω 점퍼이며 필요 2 + 예비 8 = 10개. 기존 LCSC 최소수량 100개는 유지할 이유가 없어 줄였다. BONDED 두 보드의 RSH1만 실장; 다른 RSH/RCT/CSH의 DNP 지시는 유지한다.
- 종단기는 **TE 2467938-1**로 변경: SMA 수, 50Ω, DC–18GHz, 2W, VSWR 최대 1.3, 재고 2,572개. **ANNE-50L+는 DigiKey 현재 재고 0**으로 제외. 이는 범용 미사용 포트 종단기이며 ANNE와 같은 정밀도 또는 교정 등급을 보장하지 않는다. 사용할 주파수에서 각 종단기의 S11과 교체 반복성을 먼저 확인한다. [TE 공식 도면](https://www.te.com/commerce/DocumentDelivery/DDEController?Action=srchrtrv&DocFormat=pdf&DocLang=English&DocNm=2467938&DocType=Customer+Drawing&PartCntxt=2467938-1)
- THRU는 **TE/Linx ADP-SMAF-SMAF-G**로 변경: SMA 암–암, 50Ω, DC–18GHz, VSWR 최대 1.2, 재고 8,533개. 연결 어댑터이며 인증된 zero-delay 교정 표준이 아니다. VNA의 교정 방식에 맞춰 유한 지연을 처리한다. [TE 공식 도면](https://www.te.com/commerce/DocumentDelivery/DDEController?Action=srchrtrv&DocNm=ADP-SMAF-SMAF-G&DocType=Data+Sheet&DocLang=English&DocFormat=pdf&PartCntxt=ADP-SMAF-SMAF-G)
- 플럭스 **SMD291-10M**과 납흡입선 **80-2-5**는 기존 선택 유지. 재고 692 / 6,406개, 조회가격 17,213 / 9,406원.
- 인두팁만 국내 구매: HAKKO 대체 T18-D16/T18-D24의 [DigiKey 한국 1.6D 페이지](https://www.digikey.kr/ko/products/detail/american-hakko-products-inc/T18-D16/6228930), [2.4D 페이지](https://www.digikey.kr/ko/products/detail/american-hakko-products-inc/T18-D24/6228931)는 주문 불가 표시다. 미국 재고를 한국 주문 가능 재고로 간주하지 않았다. 국내 900M-T 팁 공급가 8,140 / 8,500원은 앞선 같은 날 조회값으로 출고일 재확인이 필요하다.

## PCB 제작 예상단가 근거

2026-09-03 JLCPCB 웹 계산기, 설계별 5장 독립 작업 기준이다. **4층 / 1.6mm / FR-4 TG155 / JLC04161H-7628 / 외층 1oz·내층 0.5oz / Green / 무연 HASL / 임피던스 ±10% / 생산파일 확인 Yes**를 적용했다. 기존 Nan Ya NP-155F 소재 요구는 최종 CAM 승인 시 제조사와 별도로 확인한다.

| 설계 | 무연 HASL 5장 제작비 | ENIG 5장 비교가격 |
| --- | ---: | ---: |
| balun_eth_rj45 | $49.41 / 67,692원 | $61.41 / 84,132원 |
| balun_slipring_molex | $49.24 / 67,459원 | $61.04 / 83,625원 |
| balun_llc16 | $49.24 / 67,459원 | $61.04 / 83,625원 |
| 제작 15장 합계 | **202,610원** | **251,382원** |

무연 HASL 선택 시 **48,772원 절감**한다. ENIG는 패드 평탄도·보관 중 산화 저항에 유리하지만 이번 손납땜 지그의 필수 조건으로 보지는 않았다. 표면처리는 사용자 승인으로 변경했다. SMA 가장자리 패드의 납 두께·커넥터 안착과 접합 품질은 확인한다. [JLCPCB 표면처리 설명](https://jlcpcb.com/help/article/jlcpcb-surface-finish)

RJ45 무연 HASL 가격 내역은 $7.00 기본 + $5.10 표면처리 + $3.43 TG155 + $32.84 임피던스 제어 + $1.04 생산파일 확인이다. 68×44mm 설계는 $7.00 + $5.00 + $3.36 + $32.84 + $1.04다. [조회한 JLCPCB 견적 화면](https://cart.jlcpcb.com/quote)

Gerber 업로드·장바구니 저장·결제를 하지 않은 사양 입력 예상가다. 운임·세금·PCBA·스텐실은 제외하고 쿠폰/데스크톱 할인도 적용하지 않았다. 수량이나 사양을 바꾸면 다시 견적을 계산한다. 기존 동일 치수·사양의 68×44mm 계산값을 남은 Molex와 LLC 설계에 각각 적용했으며 합판 1작업 견적이 아니다.


## 특이사항 — 전자결재 복사용

1. 미조립 PCB는 JLCPCB, 전자부품·RF 부속·플럭스·납흡입선은 DigiKey 한국에서 구매합니다. HAKKO 인두팁 두 종류만 국내 판매처 구매입니다. Mini-Circuits 직접 구매와 LCSC 구매는 기본 주문에서 제외합니다.
2. PCB 3종을 각각 5장씩 총 15장 제작하며, Molex 2장 + RJ45 4장 + LLC M12 수 측 2장 = 총 8장을 사내 손납땜으로 조립합니다. PCBA·스텐실 비용은 포함하지 않습니다.
3. 발룬 26개(필요 24+예비 2), SMA 30개(필요 24+예비 6), 종단기 6개와 THRU 1개를 구매합니다. 0Ω 저항은 필요 2+예비 8=10개입니다.
4. 슬립링 M12 암 보드·암커넥터는 제외하고 기존 케이블을 RJ45로 개조합니다. LLC M12 수커넥터는 사내품으로 구매하지 않으며 PCB 삽입은 사용자 확인 완료입니다.
5. Samtec SMA는 현재 접점 패드와 도면 대조한 후보로 예산 반영했습니다. 권장 1.57mm와 완성 기판 두께·공차 및 CAD/제조파일 정합 확인 후 확정합니다. PCB 표면처리는 무연 HASL, 임피던스 제어는 유지합니다.
6. 미사용 SMA 포트의 50Ω 종단기는 NEXT/FEXT 측정에 공용 사용합니다. RJ45+RJ45 구성은 6개, Molex+RJ45 및 LLC+RJ45 구성은 4개 사용합니다. 기존 VNA 동봉 OSL 각 1개는 두 포트에 순차 재사용합니다. 추가 종단기는 정밀 OSL 표준이 아닙니다.
7. 작성 가능 예상 소계는 708,708원(부가세 별도)입니다. JLC 제작 202,610원 + DigiKey 489,458원 + 국내 팁 16,640원입니다. 운임·세금·RJ45 개조 플러그·추가 DFM·REF 하네스·기구물은 별도입니다.
8. 위 개별 품목표의 구매 링크를 모두 함께 첨부합니다. 실단가·실금액은 구매 후 반영합니다. 사용 전 무전원·통전·단락·전원선 분리 및 지그 baseline을 확인합니다.

## 제출 전 남은 정보

실제 회사 과제/장비명·상위도번·희망 납기·담당자/연락처·거래처 등록·결제 조건, 사내 M12 수량 2개와 전기적 핀맵, SMA 두께/제조 정합, 최종 Gerber/DFM 가격, 운임·부대비, RJ45 개조 플러그 2개의 케이블 적합 품번과 사내 재고 여부를 보완한다. 미정 가격을 0원으로 넣어 최종 총액을 확정하지 않는다.

배송/세금/특수 배송 예외는 [DigiKey 한국 공식 배송 안내](https://www.digikey.kr/ko/help-support/delivery-information/delivery-time-and-cost)와 최종 결제 화면을 따른다. 표시 재고를 확보한 주문이나 확정 납품일로 표현하지 않는다.
