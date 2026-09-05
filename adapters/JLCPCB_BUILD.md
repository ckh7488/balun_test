# JLCPCB 제작·조립 기준

현재 수동 어댑터 3종에 대한 제작 초안이다. [설계 검토 인계](../DESIGN_REVIEW_HANDOFF.md)에 전체 범위와 미완료 항목이 정리되어 있다. 과거 루트 구매 문서의 총수량은 이 구성에 자동 적용하지 않는다. **기존 `export_jlc_release.ps1`는 새 어댑터를 처리하지 않으며**, 이 문서가 새 Gerber/BOM/CPL 패키지의 생성 완료를 의미하지 않는다.

세 어댑터는 기존 RJ45 지그와 같은 stack-up을 사용한다. **임피던스 제어를 선택하는 편이 맞다.** 이로써 일정한 pair 구간의 제조 편차를 관리한다. 커넥터 접점, pad fanout, 표준의 기생성분은 별도 문제다.

## 주문 입력

| 항목 | 요청값 |
| --- | --- |
| board 종류 | 세 종류를 각각 식별하여 주문; universal M12로 합치지 않음 |
| 층 / 외형 | 4 layers / 각 66 × 40 mm |
| 두께 | 1.6 mm |
| stack-up | JLC04161H-7628 |
| 동박 | outer 1 oz / inner 0.5 oz |
| 재료 | FR-4 TG155, NP-155F 기준 설계; 변경 시 재계산 |
| mask / finish | green / ENIG |
| impedance control | Yes, differential 100 Ω, L1→L2 및 L4→L3 |
| pair 구조 | outer edge-coupled microstrip; 외층 blanket ground pour 없음 |
| 초기 geometry | W 0.23 mm / edge gap 0.22 mm |
| impedance 검사 | 가능한 coupon 측정·성적서와 공차를 견적에 포함 |
| plate/drill | 신호 via 0.60/0.30 mm, M12 pin PTH 1.80/1.00 mm, RJ45 signal PTH 1.30/0.90 mm |

JLC의 [공개 stack-up](https://jlcpcb.com/impedance)과 [계산기 안내](https://jlcpcb.com/help/article/user-guide-to-the-jlcpcb-impedance-calculator)를 확인했다. 해당 적층의 outer dielectric 0.2104 mm, inner Cu 0.0152 mm, core 1.065 mm를 CAD에 넣었다. **0.23/0.22 mm는 현재 설계 시작값이며 이번 작업에서 JLC field solver/coupon이 100 Ω을 인증한 수치는 아니다.** 제조사가 실제 stack revision과 재료값으로 확인한 폭/간격을 받아 적용해야 한다. 기본 목표 공차는 ±10%로 견적 확인하되 실제 보증 공차·검사 비용은 업체 응답을 따른다.

다른 stack-up을 선택하면서 선폭/간격을 그대로 쓰지 않는다. 0.15 mm RJ45 escape, 커넥터 pin field와 넓은 fanout은 일정한 controlled trunk로 표시하지 않는다. coupon의 100 Ω 결과가 커넥터 전체의 100 Ω이나 RF 합격을 의미하지 않는다.

## 어댑터 한 장당 BOM

| Ref | 공통/종류 | 부품 | 수량 | 조립 |
| --- | --- | --- | ---: | --- |
| J1 | 세 종류 공통 | Amphenol RJE591885401, magnetics 없는 shielded RJ45 | 1 | THT |
| J2 | m12_slipring | Finecables MB12FBAFF08ST-3 | 1 | THT, 수동 또는 업체 삽입·납땜 |
| J2 | m12_llc | Finecables MB12MBAFF08ST-3 | 1 | THT, 수동 또는 업체 삽입·납땜 |
| J2 | molex_slipring | Molex 5055680571 | 1 | SMT, reflow 권장 |
| TP1 | 공통 | shield solder point | — | PCB 동박/홀, 별도 부품 없음 |
| H1–H4 | 공통 | Ø3.2 mm mounting hole | — | 별도 브래킷/standoff |

J2는 해당 보드의 한 행만 사용한다. JLC 공급 가능 여부/재고는 확인 완료 상태가 아니다. M12를 직접 조달해 bare PCB에 손납땜하거나, JLC의 해당 부품 조달/위탁 지원을 확인한다. Molex까지 포함한 PCBA는 SMT+THT 혼합 조립 조건으로 견적을 받는다. 승인 없이 같은 외관의 다른 부품으로 대체하지 않는다.

공통 balun 보드의 ADT2-1T+와 SMA 조립은 [기존 BOM/제작 조건](../balun_eth_rj45/JLCPCB_FAB_NOTES.md)을 따른다. 어댑터에는 balun, 50 Ω 종단 또는 100 Ω Load 표준 저항을 실장하지 않는다. 외부 미사용 SMA load와 커넥터 끝 표준은 별도 준비물이다.

## 제작 전 확인할 실제 항목

1. 커넥터 샘플 또는 제조사 치수도로 정확한 suffix, 성별, component-side pin 번호, finished hole과 핀 길이를 확인한다. 사내 DUT에 실제 체결하고 continuity를 확인한다.
2. M12는 F면 수직 장착 + PG9 패널 고정이다. 패널 두께/홀 형상, connector seating 높이와 nut 공간, PCB standoff 높이는 실제 부품 도면으로 결정한다. PCB 4개 장착홀만으로 mating 토크를 신호 핀에 가하지 않는다.
3. shield patch cable과 TP1↔M12 body/패널 접속 여부를 결정한다. 선택한 상태는 OSL/thru/DUT에 동일하게 유지한다.
4. JLC impedance solver 결과에 맞춘 최종 geometry와 stack-up을 확정하고 CAD DRC/ERC/parity를 다시 수행한다.
5. KiCad에서 zone을 refill/save한 후 Gerber와 PTH/NPTH drill을 export한다. F.Cu/In1.Cu/In2.Cu/B.Cu, mask, silk, Edge.Cuts를 포함하고 내층 plane fill과 drill map을 CAM에서 확인한다.
6. JLC DFM/placement 화면에서 RJ45 방향, M12 성별·key, Molex pin 1을 확인한다. 첫 샘플은 continuity 및 보정 검증 뒤 평가용으로 사용한다.

현재 저장소는 이 확인에 사용할 **배선된 KiCad 설계와 검사 자료**를 제공한다. 실물 도면으로 확정되지 않은 패널 치수나 임피던스 성적서를 만들어내지 않았으며, 미확정 상태를 제작 완료로 표시하지 않는다.
