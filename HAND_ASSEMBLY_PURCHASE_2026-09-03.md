# BALUN 지그 — DigiKey 부품 구매 + JLCPCB 미조립 제작

2026-09-03 갱신. 사용자 지시에 따라 **Mini-Circuits 직구와 LCSC 분산 구매를 빼고 DigiKey 한국으로 통합**한다. PCB는 JLCPCB에서 제작하고 사내 손납땜한다. HAKKO 인두팁 두 종류만 DigiKey 한국 주문 불가에 따른 국내 구매 예외다.

최신 상세 가격·전체 링크·SMA 치수 대조·구매요청서 문구는 [구매요청서 입력안](PURCHASE_REQUEST_FORM_DRAFT_2026-09-03.md)을 따른다. 이번 변경은 구매 문서 갱신이며 CAD/풋프린트/제조 BOM/생산 ZIP을 변경하거나 제조 승인한 작업이 아니다. 주문·결제·업체 문의는 실행하지 않았다.

## 1. 구성과 예산

| 구분 | 수량/구성 | 예상액, 부가세 별도 |
| --- | --- | ---: |
| JLCPCB | RJ45 5장 + Molex 5장 + LLC 5장 | 202,610원 |
| DigiKey | 아래 전자부품·RF 부속·플럭스·납흡입선 10품목 | 489,458원 |
| 국내 팁 | 900M-T-1.6D와 900M-T-2.4D 각 1개 | 16,640원 |
| 합계 | 운임·세금·별도 준비 항목 제외 | **708,708원** |

실사용은 **Molex 2 + RJ45 4 + LLC M12 수 측 2 = 8장**, 나머지 7장은 미조립 여분이다. 슬립링 M12 암 보드/암커넥터는 구매 제외하고 기존 케이블을 RJ45로 개조해 기존 RJ45 지그를 공유한다. LLC M12 수커넥터도 사내품을 사용한다. **PCB 삽입 적합성은 사용자 확인 완료**이며 필요한 2개 확보·전기적 핀맵·무전원 확인은 별도다. 사내품 품번은 임의로 특정하지 않는다.

무연 HASL, 4층/1.6mm/TG155/JLC04161H-7628, 임피던스 제어 유지. PCBA와 스텐실은 제외한다. 예산 환율은 사용자 지정 1USD=1,370원이며 DigiKey 원화 가격은 재환산하지 않는다.

사용자가 확인한 Mini-Circuits 장바구니 $215는 294,550원이다. 이를 발룬만의 가격으로 간주하지 않는다. DigiKey에서 발룬 26개+TE 종단기 6개+THRU 1개는 294,191원(배송/세금 별도)이므로, 사용자 지시대로 제조사 직구는 하지 않는다.

## 2. 부품별 주문 링크

수량에 이미 예비분이 포함돼 있다. 구형 구매표의 품번을 중복 구매하지 않는다. 2026-09-03 DigiKey 한국 표시가 기준이며 국내 팁은 앞선 같은 날 조회값이다.

| 품목 / 정확한 MPN | 구매수량 | 예상단가 | 예상금액 | 개별 구매 링크 |
| --- | ---: | ---: | ---: | --- |
| RF 발룬 / **ADT2-1T+** | 26 | 10,011원 | 260,286원 | [DigiKey](https://www.digikey.kr/ko/products/detail/mini-circuits/ADT2-1T/13927001) |
| SMA PCB 커넥터 / **SMA-J-P-H-ST-EM1** | 30 | 3,817원 | 114,510원 | [DigiKey](https://www.digikey.kr/ko/products/detail/samtec-inc/SMA-J-P-H-ST-EM1/2602450) |
| RJ45 커넥터 / **RJE591885401** | 5 | 8,052원 | 40,260원 | [DigiKey](https://www.digikey.kr/ko/products/detail/amphenol-icc-commercial-products/RJE591885401/6189327) |
| 테스트 포인트 / **5001** | 10 | 336.3원 | 3,363원 | [DigiKey](https://www.digikey.kr/ko/products/detail/keystone-electronics/5001/255327) |
| Molex 커넥터 / **5055680571** | 10 | 1,027원 | 10,270원 | [DigiKey](https://www.digikey.kr/ko/products/detail/molex/5055680571/7807019) |
| 0805 0Ω 저항 / **RC0805JR-070RL** | 10 | 24.5원 | 245원 | [DigiKey](https://www.digikey.kr/ko/products/detail/yageo/RC0805JR-070RL/728216) |
| SMA 50Ω 종단기 / **2467938-1** | 6 | 4,004원 | 24,024원 | [DigiKey](https://www.digikey.kr/ko/products/detail/te-connectivity-linx/2467938-1/22535225) |
| SMA THRU 어댑터 / **ADP-SMAF-SMAF-G** | 1 | 9,881원 | 9,881원 | [DigiKey](https://www.digikey.kr/ko/products/detail/te-connectivity-linx/ADP-SMAF-SMAF-G/9826669) |
| 전자용 플럭스 / **SMD291-10M** | 1 | 17,213원 | 17,213원 | [DigiKey](https://www.digikey.kr/ko/products/detail/chip-quik-inc/SMD291-10M/14636534) |
| 인두팁 1.6D / **900M-T-1.6D** | 1 | 8,140원 | 8,140원 | [엘레파츠](https://eleparts.co.kr/goods/view?no=5274) |
| 인두팁 2.4D / **900M-T-2.4D** | 1 | 8,500원 | 8,500원 | [디바이스마트](https://www.devicemart.co.kr/goods/view?no=2291) |
| 납흡입선 1.52mm / **80-2-5** | 1 | 9,406원 | 9,406원 | [DigiKey](https://www.digikey.kr/ko/products/detail/chemtronics/80-2-5/306981) |

### SMA 후보와 변경된 부품

- **Samtec SMA-J-P-H-ST-EM1**: 기존 에지마운트 패드와 대조한 DigiKey 후보. GND 다리 중심 간격 5.54mm vs 기존 패드 5.65mm, 다리 폭 0.81mm vs 패드 1.85mm, 신호 핀 1.27mm vs 패드 1.85mm로 명목 치수상 접점이 패드 안에 들어온다. **권장 PCB 두께 1.57mm와 현재 1.6mm 완성 두께/공차 및 HASL 안착은 별도 확인**해야 한다. 권장 패드가 완전히 동일하지 않으며 CAD는 아직 MyAntenna로 남아 있다. [Samtec 공식 도면](https://suddendocs.samtec.com/prints/sma-j-p-x-st-em1-mkt.pdf)
- Samtec 30개는 114,510원으로 기존 MyAntenna/LCSC 23,989원보다 90,521원 비싸다. DigiKey 통합 구매 예산에 반영했지만, 최종 치수·제조 정합 승인 없이 완전 호환/제조 가능으로 표시하지 않는다.
- 사용자가 제시한 TE **5-1814832-2**는 수직 THT로 이번 에지마운트 대체품이 아니다.
- ADT2-1T+, RJ45 RJE591885401, Keystone 5001, Molex 5055680571은 정확한 기존 제조사/품번을 유지하고 DigiKey에서 산다.
- 0Ω는 YAGEO **RC0805JR-070RL** 0805 점퍼로 대체하고 필요 2+예비 8=10개로 줄인다. RJ45 BONDED 두 장의 RSH1만 실장. FLOAT 두 장의 RSH1, 모든 RCT/CSH는 기존 DNP 조건을 유지.
- 전자부품 Cut Tape를 선택한다. 필요 없는 Digi-Reel 서비스 비용을 추가하지 않는다.

## 3. VNA 종단·THRU

**TE 2467938-1**은 SMA 수 50Ω 종단기(DC–18GHz, 2W, VSWR≤1.3)로 NEXT/FEXT의 미사용 포트를 종단한다. 기존 ANNE-50L+는 DigiKey 재고 0이어서 제외했다. TE 제품을 같은 정밀도/교정 등급이라고 취급하지 않는다. 사용 대역에서 각 종단기의 S11과 교체 반복성을 확인한다. [TE 공식 도면](https://www.te.com/commerce/DocumentDelivery/DDEController?Action=srchrtrv&DocFormat=pdf&DocLang=English&DocNm=2467938&DocType=Customer+Drawing&PartCntxt=2467938-1)

**ADP-SMAF-SMAF-G**는 SMA 암–암 50Ω 연결 어댑터(DC–18GHz, VSWR≤1.2)다. 인증된 zero-delay 교정 표준이 아니며, VNA 교정 방식에 맞춰 유한 지연/모델을 처리한다. [TE 공식 도면](https://www.te.com/commerce/DocumentDelivery/DDEController?Action=srchrtrv&DocNm=ADP-SMAF-SMAF-G&DocType=Data+Sheet&DocLang=English&DocFormat=pdf&PartCntxt=ADP-SMAF-SMAF-G)

동봉 Open/Short/Load 각 1개는 VNA 두 포트에 순차 재사용한다. 추가 종단기 6개를 정밀 OSL 교정 표준으로 부르지 않는다. RJ45+RJ45는 6개, Molex+RJ45 및 LLC+RJ45는 4개를 사용하며 순차 측정에서 공용으로 사용한다. 동시에 여러 세트를 측정할 수량은 아니다.

## 4. 사진으로 확인한 인두·기존 페이스트

### 기존 goot BS-15는 이번 PCB에 사용하지 않는다

사용자 사진의 제품은 **goot BS-15**다. 뚜껑에 `Not applicable to PC boards` 및 약산성 표기가 있다. 제조사도 BS-10/15를 PCB에 사용하지 말라고 명시한다. **변색이나 오래된 상태 이전에 제품 용도가 맞지 않는다.** [goot 공식 설명](https://en.goot.jp/education/detail/bs_10)

사진에는 검게 오염된 부분과 사용 흔적도 보이지만, 색만으로 성능·성분 변화를 진단하지 않는다. 새 전자용 플럭스 용기에 기존 물질을 섞지 않고, 기존 페이스트에 담갔던 도구로 새 플럭스를 오염시키지 않는다. 기존 PCB에 이미 사용했다면 단순 IPA 세척만으로 잔류 문제가 해결된다고 가정하지 않는다.

### HAKKO 936 + 907은 본체부터 바꿀 필요는 없다

사진의 표기는 HAKKO 936 스테이션과 907 핸들이다. 정품 여부나 히터·센서·접지의 실제 상태까지 사진으로 확인할 수는 없다. 정상 동작한다면 이번 손납땜용으로 우선 활용할 수 있다. 사진의 팁은 작업면이 어둡고 오염돼 보이므로 세척 후 새 납이 작업면에 고르게 퍼지는지 확인하고, 복구되지 않거나 패인 경우 교체한다. [HAKKO 팁 상태 안내](https://www.hakko.com/japan/support/maintenance/detail.php?seq=88)

907 핸들은 기존 **900M-T-…**와 제조사가 호환을 명시한 T18 대체품을 사용할 수 있다. 이번에는 한국 DigiKey에서 T18-D16/T18-D24 주문이 불가하여 국내 900M-T 팁을 유지한다. 외형만 비슷한 다른 계열을 임의로 끼우지 않는다. [HAKKO 936/907 공식 호환 안내](https://www.hakko.com/japan/products/hakko_936_tips.html)

뾰족할수록 좋은 것은 아니다. 정상적인 평평한 D형 팁이 접촉 면적과 열 전달 측면에서 유리할 수 있다. 아래 크기는 이 작업을 위한 추천이며, 1.6 mm 팁으로 Molex 핀 여러 개를 동시에 누르라는 의미가 아니다. 작은 접점에는 팁 모서리를 사용하고 확대 관찰한다.

## 5. 플럭스와 최소 추가 소모품

| 품목 | 추천 수량 | 구매 링크 / 조회 가격 | 선택 이유·주의 |
| --- | ---: | --- | --- |
| **Chip Quik SMD291-10M** 전자용 tacky flux, 수동 주사기 10 cc/10 g | 1 | [DigiKey 한국](https://www.digikey.kr/ko/products/detail/chip-quik-inc/SMD291-10M/14636534), **₩17,213**, 재고 692개 표시 | 이번의 우선 추천 플럭스. no-clean, 수동 주사기 제품. 금속 분말이 든 solder paste가 아님 |
| HAKKO **900M-T-1.6D** | 1 | [엘레파츠](https://eleparts.co.kr/goods/view?no=5274), **₩8,954 VAT 포함**, 평균 발송 24시간 이내 표시 | SMT/일반 작업용. 표시된 평균 발송일은 실재고 예약·도착 보장이 아님 |
| HAKKO **900M-T-2.4D** | 1 | [디바이스마트](https://www.devicemart.co.kr/goods/view?no=2291), **₩9,350 VAT 포함**, 평균 준비 2–3일 표시 | SMA 접지 탭·큰 패드용. 실물 품번과 출고일 확인 |
| Chemtronics **80-2-5**, 1.52 mm 납흡입선 | 1 | [DigiKey 한국](https://www.digikey.kr/ko/products/detail/chemtronics/80-2-5/306981), **₩9,406**, 재고 6,406개 표시 | 브리지 제거용. 납이 굳은 상태에서 잡아당겨 패드를 뜯지 않음 |

인두팁은 판매자가 HAKKO로 표시한 제품을 연결했다. 저가 범용 호환 세트와 같은 것으로 취급하지 않는다. 수령 시 품번·포장을 확인한다. 제조사 규격 확인과 판매점의 유통/재고 표시는 구분한다.

- **SMD291-10M을 고른다. `SMD291AX` 같은 납 분말 포함 솔더페이스트와 혼동하지 않는다.** 인두+실납 작업에는 전자용 플럭스와 실납을 따로 사용한다.
- 기존 실납의 합금과 굵기를 확인한다. 회사의 무연 정책에 맞는 전자용 flux-cored 실납, 약 0.3–0.5 mm가 작은 SMT 작업에 다루기 편하다. 사진만으로 기존 실납 규격은 확인하지 못했다.
- 보드 고정대, 핀셋, 확대경/현미경, 멀티미터도 필요하다. 기존 장비가 있으면 중복 구매하지 않는다.
- 사진의 스펀지는 오염이 많아 보인다. 새 인두용 스펀지 또는 인두용 황동 클리너로 교체를 권한다. 팁 작업면을 줄로 갈아 모양을 바꾸지 않는다. 작업 후 팁에 새 납을 입혀 보관한다. [HAKKO 팁 관리](https://www.hakko.com/english/support/maintenance/detail.php?seq=183)
- no-clean이 무연기·무해하다는 뜻은 아니다. 국소 배기/환기를 확보하고 제조사의 SDS를 따른다. 뜨거운 인두 근처에서 가연성 세척제를 사용하지 않는다.
- RF 지그는 과도한 플럭스 잔류와 납 뭉침을 피한다. 세척은 플럭스 및 부품 제조사가 허용한 방법을 사용하며, 커넥터/변압기를 임의로 침수·초음파 세척하지 않는다.
- 새 플럭스는 제조일·유효기간을 확인한다. SMD291-10M 상품 자료는 제조 후 24개월 및 3–25 °C 보관을 안내한다. 실제 포장 지침이 우선한다.

### 손납땜 난이도에 대한 정정

손납땜 가능과 현재 오염된 팁 하나로 쉽게 끝난다는 것은 다르다. 다음은 현재 풋프린트와 부품 형태에 따른 작업 판단이다.

| 작업 | 판단 |
| --- | --- |
| 0805 저항, 테스트 포인트 | 비교적 쉬움 |
| RJ45/M12 신호 핀 | 핀이 맞고 작업 공간을 확보하면 가능. shell/고정 부위는 별도 열량·기구 고려 |
| ADT2-1T+ 발룬 | 손납땜 가능한 SMT이나 방향과 과열에 주의. 첫 보드로 연습하지 않음 |
| SMA | 미세 피치보다 접지부의 열 전달과 수평 고정이 관건. 발룬/패드까지 오래 가열하지 않음 |
| Molex 5055680571 | 이번 구성에서 정렬·브리지·플라스틱 손상에 특히 주의. 확대 관찰, 적절한 팁, 고정과 연습 필요 |

사용자가 이전에 Molex 작업에서 파손을 경험했으므로 '아무 준비 없이 전부 쉽다'고 판단하지 않는다. 새 팁과 전자용 플럭스로 연습 기판에서 먼저 젖음/브리지 제거를 확인한다. 접지부가 잘 가열되지 않으면 최고 온도로 오래 누르는 대신 열 전달·팁·작업 방법을 점검한다. 936 한 대만으로 모든 접지부의 납땜 품질을 보장하지 않는다.


## 6. 발주와 배송

1. **DigiKey:** 위 표 중 10품목을 한국 배송으로 한 번에 주문한다. 현 재고를 우선하고 재고 없는 품목의 제조 표준 리드타임을 실제 출하일과 혼동하지 않는다. 가격·세금·배송 조건은 최종 결제 화면과 [DigiKey 한국 배송 안내](https://www.digikey.kr/ko/help-support/delivery-information/delivery-time-and-cost)를 따른다.
2. **국내 팁:** HAKKO T18-D16/T18-D24의 DigiKey 한국 페이지는 주문 불가로 표시된다. 국내 900M-T 팁 두 개만 예외로 유지하며 같은 판매처에서 정확한 두 품번과 재고가 확보되면 합배송 가능하다. 출고일은 재확인한다.
3. **JLCPCB:** 미조립 PCB 3설계를 각 5장씩 별도 작업으로 주문. 부품 Pre-order와 PCBA는 사용하지 않는다. 이번 구매목록은 제조용 BOM/CPL이 아니다.
4. **M12:** 신규 구매 없음. 사내 수커넥터 PCB 삽입은 사용자 확인 완료. 전기적 핀맵/무전원 확인과 최신 생산파일 검증은 별개다.
5. **제조 승인:** Samtec SMA의 기판 두께/공차·제조파일 정합, Molex 체결, ERC/DRC/parity와 최신 생산 ZIP 검증은 완료 전이다. 과거 HOLD 파일 또는 MyAntenna가 적힌 CAD/BOM을 Samtec 승인 자료로 그대로 사용하지 않는다.

RJ45 개조 플러그 2개는 케이블 도체 굵기·연선·외경과 사내 재고 여부에 따라 정확한 품번을 확정해 링크와 가격을 추가한다. REF/bypass 하네스, 고정판/케이스·스페이서, 운임·세금 역시 별도 항목이다. VNA 연결 전 무전원·통전/단락·전원선 분리와 지그 baseline을 확인한다.

구매요청서 엑셀은 모든 품목 개별 기재, 품목별 전체 URL, 수량×단가 일치, 환율/미정 운임 처리 및 표시 검증을 적용했다. 제조사 도면 대조는 구매 후보 검토이며 실물 RF 성능 시험을 대신하지 않는다.
