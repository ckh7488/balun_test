# JLCPCB/LCSC 최종 구매·조립 가이드

이 문서와 [`JLCPCB_FINAL_BOM.csv`](JLCPCB_FINAL_BOM.csv)는 다음의 완전한 비교 지그 1세트를 기준으로 한다.

- `balun_eth_rj45` 2장
- `balun_slipring/molex_end` 1장
- `balun_slipring/m12_end` 1장
- 두 프로젝트가 공유하는 동일한 외부 50 Ω SMA 종단기 6개

루트 CSV는 전체 구매 수량을 합친 표이지 **JLCPCB 업로드용 BOM이 아니다**. 세 PCB 설계는 Gerber, 좌표와 connector reference가 서로 다르므로 다음 세 PCBA 작업으로 나눠야 한다.

1. `balun_eth_rj45`: 동일 artwork 2장
2. `balun_slipring/molex_end`: 1장
3. `balun_slipring/m12_end`: 1장

각 작업에서 해당 설계의 Gerber, BOM, CPL을 따로 생성하고 검토한다. JLC BOM에는 최소한 Comment, Designator, Footprint, JLCPCB/LCSC part number가, CPL에는 Designator, X/Y, Rotation, Layer가 필요하다. 루트의 합산 CSV를 세 작업 중 어느 하나의 BOM으로 업로드하지 않는다.

아래는 JLC 견적에서 더해질 attrition이나 최소 작업 수량을 제외한 1세트 검산값이다.

| 선정 부품 | 1세트 필요 수량 |
| --- | ---: |
| `ADT2-1T+` | 12 |
| `A-SMA-KE-16.5A` | 12 |
| `RJE591885401` RJ45 | 2 |
| Keystone `5001` test point | 4 |
| Molex `5055680571` 후보 | 1, HOLD |
| Finecables `MB12FBAFF08ST-3` 후보 | 1, HOLD |
| `C17477` 0 Ω | baseline RSH용 1; 선택형 RCT 위치 12 |
| REF Molex `5055650501` / `5054311000` | housing 1, contact 4; 각 판매 MOQ 5/100 |
| REF M12 male `858FA08-103RAU1` | 1, mating/pin-1 HOLD |
| REF cable LAPP `2170284` | 실측 완성 길이 + 종단 여유 |
| M3 비도전성 지지점 | 16, 높이/구조 TBD |
| 외부 `ANNE-50+` 종단기 | 동일품 6 |

위 보드 수량은 지그에 실제 필요한 수량이다. JLC 주문 화면에서 더 큰 제작·조립 수량을 요구하면 설계별 FIT/DNP 기준은 그대로 유지하고, 추가 PCB와 부품 attrition 수량을 최종 견적에 명시해 확인한다.

## 현재 발주 판단

이 저장소 전체는 아직 **그대로 결제 가능한 turnkey package가 아니다**. `ORDERABLE` 부품은 정확한 MPN과 JLC/LCSC 번호가 선정되었다는 뜻이고, 아래의 실물·기구 차단 항목까지 해제되었다는 뜻은 아니다. `HOLD` 행은 full PCBA 수량에 투입하지 않는다.

기본 조립 상태는 `CT-FLOAT`다.

- 네 보드의 모든 RCT를 DNP로 둔다.
- RJ45 두 보드의 `CSH1`을 모두 DNP로 둔다.
- 동일 artwork로 발주하는 RJ45 두 보드의 `RSH1`도 PCBA에서는 모두 DNP로 둔다. 입고 후 Port-1 보드를 식별·표기하고 그 보드의 `RSH1` 한 곳만 `C17477` 0 Ω로 수동 장착한다.
- 한 보드에서 `RSH1`과 `CSH1`을 동시에 장착하지 않는다.
- `ADT2-1T+`는 총 12개 모두 FIT한다.
- HOLD connector는 해당 검증이 끝난 뒤에만 정확한 MPN으로 FIT한다.

RSH1을 공통 PCBA BOM에서 제외하면 동일한 RJ45 artwork 두 장에 서로 다른 assembly variant를 억지로 섞지 않아도 된다. 나중에 `CT-GND`를 별도로 시험하려면 양 끝의 관련 RCT를 전부 동시에 장착하고 REF/bypass baseline부터 다시 측정하며, 결과를 다른 공통모드 경계조건으로 표시한다.

## 외부 50 Ω 종단기와 케이블

Mini-Circuits `ANNE-50+` SMA-male 종단기 동일품 6개를 사용한다. RJ45 지그 두 장에는 SMA jack이 총 8개이고 2-port VNA가 2개를 사용하므로 IL/RL, NEXT, FEXT 측정에서 나머지 6개를 모두 종단해야 한다. 슬립링 endpoint 두 장에는 SMA가 총 4개라 두 개만 필요하므로 동일한 6개 세트를 공유한다.

가장 안전한 구매 수량은 신규 동일품 6개다. 기존 종단기가 정품 `ANNE-50+`로 명확히 식별되고 손상 없이 측정 세트에 사용할 수 있다고 확인된 경우에만 신규 5개를 산다. 그 외에는 기존 미확인품을 예비품으로 두고 crosstalk 측정 세트에 섞지 않는다. 조회 시 LCSC `C6125302`는 재고 0이었고 Mini-Circuits direct는 1,000개 초과 재고를 표시했다.

검증된 coax 2개가 없다면 Mini-Circuits `CBL-2FT-SMSM+` 동일품 2개를 추가한다. 이는 PCB 부품이 아닌 선택형 계측 액세서리다. 조회 시 LCSC `C18117095`는 재고 0, Mini-Circuits direct는 100개 초과였다. NEXT/FEXT에서는 cable-to-cable leakage가 측정 바닥값이 될 수 있으므로 두 케이블의 배치, 간격, 굽힘과 connector torque를 REF/DUT 사이에 고정한다.

## 해제해야 할 차단 항목

### 선정 SMA의 PCBA 검토

모든 보드의 SMA 12개는 MyAntenna `A-SMA-KE-16.5A`, JLC/LCSC `C22467617`로 통일한다. 권장 PCB 두께 `1.6 ±0.05 mm`는 nominal 1.5862 mm 적층과 맞고, catalog 정격은 50 Ω / DC–6 GHz다. JLC에는 Standard-PCBA-only, wave solder, assembly difficulty High로 등록되어 있으며 조회 재고는 491개였다.

세 PCBA 작업에서 checked-in footprint/launch가 제조사 land pattern과 같은지, body가 routed board edge에 제대로 안착하는지, connector가 모두 바깥쪽을 향하는지, JLC가 wave-solder fixture/engineering 비고를 승인하는지 확인한다. 자동 대체품은 승인하지 않는다. 기존 Amphenol `132289` / `C3172723`은 PCB 두께 상한 1.57 mm가 선정 적층보다 작으므로 최종 BOM에서 제외한 legacy 부품이다.

### 슬립링 connector와 핀맵

Molex `5055680571` / `C585386`은 catalog와 footprint가 정의된 5핀 header지만, 문서에 적힌 housing `5055650501`의 PCB 상대물로는 아직 **추론 후보**다. endpoint PCBA 전에 실제 REV-504와의 체결, key 방향, pin 1, pad numbering, 1:1 footprint 출력을 확인한다.

Finecables `MB12FBAFF08ST-3` / `C22378785`는 조회 시 JLC 재고 0이라 global sourcing 또는 preorder가 필요하다. 조달 전에 정확한 suffix, mating-face view, A-key와 pin 1, 후면 실장 방향, panel/nut 접근과 cable exit를 실물 DUT에 대조한다. `balun_slipring/PINMAP.md`의 Ethernet 4선 continuity 측정도 완료한다. 따라서 transformer와 SMA를 조달할 수 있더라도 이 두 검증 전에는 슬립링 PCBA 두 작업 모두 HOLD다.

REF/bypass harness는 Molex `5055650501` housing, `5054311000` contact 4개, NorComp `858FA08-103RAU1` M12 A-code male plug과 LAPP `2170284` 2-pair 100 Ω Cat.5e cable로 선정했다. Cable OD 5.6 ±0.3 mm는 M12 plug의 4–6 mm gland에 들어가지만, cable core 최대 Ø1.04 mm가 Molex terminal 상한 Ø1.02 mm보다 0.02 mm 큰 최악 공차가 있다. 따라서 contact/cable는 샘플 4가닥을 먼저 압착해 crimp height, pull force, housing 삽입과 continuity를 통과시켜야 한다. 완성 cable 길이는 DUT의 connector-to-connector 실측 후 정하고, 전체 shield/drain은 CT-FLOAT baseline에서 양단 모두 절연한다.

재고가 있는 CAZN `M12-S8A-GPB M12` / `C19108981`은 drop-in 대안이 아니다. 조회 재고는 JLC 31개/LCSC 30개지만, 이 부품은 straight PCB front-mount M12x1/D-cut/ring 구조이고 현재 Finecables 후보의 PG9/후면 실장 기구와 footprint가 다르며 지원 PCB 두께도 명시되지 않았다. 기구 방향을 먼저 결정한 뒤 필요하면 loose sample 1개만 구매해 **재설계 후보**로 평가한다. 현재 BOM/CPL에서 Finecables 부품 대신 자동 매칭하거나 실장하지 않는다.

### Controlled impedance와 최종 DFM

각 제작 작업에서 문서대로 4층 `JLC04161H-7628 (Standard)`, 주문 두께 1.6 mm, 외층 1 oz/내층 0.5 oz와 impedance control을 선택한다. 저장된 50 Ω `0.35 mm`와 100 Ω 차동 `0.23/0.22 mm` geometry를 주문 시점의 JLC field solver로 다시 확인한다. 다른 stack으로 대체되거나 선폭이 자동 변경되면 그대로 승인하지 말고 KiCad 규칙과 routing을 갱신한 뒤 ERC/DRC를 다시 수행한다.

RJ45, M12, SMA와 test point는 wave solder/fixture 비용이 생길 수 있다. JLC 3D/placement viewer에서 side와 rotation을 직접 검토하고 모든 part match를 수동 확인한다. catalog 재고가 있다는 사실만으로 local footprint, 실장면과 방향이 승인되는 것은 아니다.

네 보드에는 각각 NPTH M3 hole이 4개 있지만 fixture plate와 필요한 standoff 높이가 정해지지 않았다. 따라서 나사·spacer는 전기 BOM에서 임의 선정하지 않고 mechanical HOLD로 남긴다. 기구가 확정되면 nylon 등 비도전성 부품을 우선 사용해 의도하지 않은 chassis/ground 경로가 생기지 않도록 한다.

## 권장 주문 순서

1. `ANNE-50+` 6개를 주문한다. 기존품이 위의 exact-part 예외를 만족할 때만 5개로 줄인다. 필요하면 `CBL-2FT-SMSM+` 2개도 주문한다.
2. `A-SMA-KE-16.5A` 12개와 JLC 견적이 계산한 attrition을 reserve하고 Standard PCBA의 wave 방향·fixture 비고를 명시적으로 검토한다.
3. RJ45 작업의 stack, impedance, design-specific BOM/CPL을 확인하고 RCT/CSH/RSH는 모두 PCBA DNP로 둔다.
4. REV-504/M12 continuity와 기구 검증을 완료한다. 완료 전에는 두 슬립링 connector를 validation 수량 이상 조달하지 않는다.
5. REF harness의 contact/cable 4가닥 sample crimp와 M12 mating/pin-1을 통과시킨 뒤 DUT 실측 길이로 제작한다.
6. 각 HOLD를 해제한 뒤 해당 설계의 Gerber/BOM/CPL을 다시 생성하고 ERC, DRC, schematic–PCB parity와 JLC placement/DFM을 결제 전에 재확인한다.
7. 입고 후 첫 조립품을 continuity 검사하고, 표시한 RJ45 Port-1 지그에만 `RSH1`을 수동 장착한 뒤 `CT-FLOAT` REF baseline을 만든다.

CSV의 재고는 **2026-08-13 KST** 조회 스냅샷이다. 주문 직전 다시 확인해야 하며, JLC가 실제 FIT 수량에 component attrition을 더할 수 있다.

## 선정 부품과 발주 자료

- [JLCPCB KiCad BOM/CPL format](https://jlcpcb.com/help/article/how-to-generate-the-bom-and-centroid-file-from-kicad)
- [JLCPCB component matching rules](https://jlcpcb.com/help/article/component-matching-guidelines-for-pcba-orders)
- [JLCPCB assembly fixtures](https://jlcpcb.com/help/article/pcb-assembly-fixtures)
- [Mini-Circuits ADT2-1T+ / C5223988](https://jlcpcb.com/partdetail/MiniCircuits-ADT2_1T/C5223988)
- [Amphenol RJE591885401 / C5386678](https://jlcpcb.com/partdetail/AmphenolICC-RJE591885401/C5386678)
- [Keystone 5001 / C238122](https://jlcpcb.com/partdetail/Keystone-5001/C238122)
- [UNI-ROYAL 0805W8F0000T5E / C17477](https://jlcpcb.com/partdetail/0805W8F0000T5E/C17477)
- [MyAntenna A-SMA-KE-16.5A / C22467617](https://jlcpcb.com/partdetail/MyAntenna-A_SMA_KE_165A/C22467617)
- [Molex 5055680571 / C585386](https://jlcpcb.com/partdetail/MOLEX-5055680571/C585386)
- [Finecables MB12FBAFF08ST-3 / C22378785](https://jlcpcb.com/partdetail/FINECABLES-MB12FBAFF08ST3/C22378785)
- [CAZN M12-S8A-GPB M12 / C19108981 — 재설계 후보만](https://jlcpcb.com/partdetail/CAZN-M12_S8A_GPBM12/C19108981)
- [Molex 5055650501 housing / C564750](https://www.lcsc.com/product-detail/C564750.html)
- [Molex 5054311000 terminal / C385112](https://www.lcsc.com/product-detail/C385112.html)
- [NorComp 858FA08-103RAU1 M12 male cable plug](https://www.digikey.com/en/products/detail/norcomp-inc/858FA08-103RAU1/16633408)
- [LAPP 2170284 2-pair Cat.5e cable](https://www.lapp.com/en_US/us/etherline-cat-5e-flex/p/2170284)
- [Mini-Circuits ANNE-50+ datasheet](https://www.minicircuits.com/pdfs/ANNE-50%2B.pdf) / [구매 페이지](https://www.minicircuits.com/WebStore/dashboard.html?model=ANNE-50%2B)
- [Mini-Circuits CBL-2FT-SMSM+ 구매 페이지](https://www.minicircuits.com/WebStore/dashboard.html?model=CBL-2FT-SMSM%2B)
