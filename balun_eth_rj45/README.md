# balun_eth_rj45 Rev B

**2026-09-05 현재 역할:** 교체형 수동 어댑터와 공유하는 공통 balun PCB다. 방향 전환 당시 회로/동박을 유지했으며, 후속 임피던스 확인에서 배선 폭을 수정했다. [2026-09-05 계산·검증](../docs/jlcpcb/IMPEDANCE.md)과 [주문 화면 가이드](../docs/jlcpcb/README.md)를 따른다. 설계 선택 이유와 검증 한계는 [설계 검토 인계](../DESIGN_REVIEW_HANDOFF.md), 실제 CAD 검토는 [FIXTURE_REVIEW](../adapters/FIXTURE_REVIEW.md)를 참고한다.

2026-09-03: 기존 회로도를 채널별 A3 한 장으로 재배치했다. 연결·부품·DNP와 PCB는 그대로이며, [가독성 정리 결과 및 PDF](../SCHEMATIC_READABILITY_2026-09-03.md)를 참고한다.

LibreVNA 2-port로 일반 Ethernet 케이블과 전용 Ethernet 슬립링을 측정하기 위한 수동 4-pair RJ45 지그다. 동일 보드 2장을 DUT 양쪽에 사용하며, 한 번에 한 pair를 VNA의 두 포트로 측정한다. through 측정에서는 각 보드의 미사용 SMA 3개씩, 두 장 합계 **6개**에 외부 50 Ω 종단기를 연결한다. NEXT/FEXT 등 다른 포트 배치에서도 전체 8개 중 미사용 6개를 종단한다.

> 수동 DUT 전용이다. PoE나 동작 중인 Ethernet 장비에는 연결하지 않는다.

현재 기본안은 이 공통 PCB 두 장과 교체형 RJ45–M12/Molex 어댑터다. 최종 기준면은 어댑터 뒤 DUT 접속면으로 두며 [공통 측정 계획](../VNA_TEST_PLAN.md)과 [어댑터 설계](../adapters/README.md)를 따른다. 기존 LLC/M12 전용 balun PCB와 PCBA 10장 계획은 이전 설계 선택지로 보존한다.

## 채널 구성

| SMA | RJ45 pair | Balun |
|---|---|---|
| J2 / A | 1(+)–2(-) | T1 |
| J3 / B | 3(+)–6(-) | T2 |
| J4 / C | 4(+)–5(-) | T3 |
| J5 / D | 7(+)–8(-) | T4 |

T1–T4는 Mini-Circuits `ADT2-1T+`다. primary pin 3은 SMA center, pin 1은 GND이며, secondary pin 4/6은 각각 pair P/N, pin 5는 RCT, pin 2는 NC다.

ADT2-1T+의 dot은 primary pin 3과 secondary pin 6이다. 따라서 현재 `P=pin 4`, `N=pin 6` 명명은 **지그 한 장에서 한 번의 극성 반전**을 만든다. 동일한 두 보드를 back-to-back으로 쓰는 기본 비교에서는 두 번 반전되어 전달 극성이 복구되지만, 단일 지그 de-embedding, 절대 위상 또는 mixed-mode 부호에는 이 convention을 반영해야 한다.

## JLCPCB Rev B 기판 사양

- KiCad 10, 4층, 주문 두께 1.6 mm, 외층 1 oz / 내층 0.5 oz.
- JLCPCB stack-up `JLC04161H-7628 (Standard)`, nominal stack 1.5862 mm.
- 재료 `FR-4 TG155 / Nan Ya NP-155F`, green solder mask, ENIG.
- L1(F.Cu): 신호와 필요한 짧은 GND 연결만 사용. blanket GND pour 없음.
- L2(In1.Cu): 끊김 없는 `/GND` plane.
- L3(In2.Cu): 끊김 없는 `/GND` plane.
- L4(B.Cu): pair B와 필요한 짧은 GND 연결만 사용. blanket GND pour 없음.
- L1/L4 신호 아래의 기준면은 각각 L2/L3이며, outer pour가 없는 non-coplanar microstrip으로 계산했다.

상세 주문값과 적층 구조는 [JLCPCB_FAB_NOTES.md](JLCPCB_FAB_NOTES.md)를 따른다. 주문 화면에서 다른 stack-up으로 자동 변경되면 그대로 발주하지 말고 선폭을 다시 계산한다.

## 임피던스와 배선 규칙

- SMA single-ended 50 Ω 목표: 외층 폭 `0.357 mm`.
- Ethernet differential 100 Ω 목표: 외층 폭 `0.234 mm`, edge-to-edge gap `0.216 mm`. 2026-09-05 공식 계산기 결과를 반영한 nominal 치수이며 제조 CAM/coupon은 별도 확인한다.
- RJ45 pin field만 폭 `0.15 mm`로 짧게 neck-down한다.
- J1 signal PTH는 pad `1.30 mm`, drill `0.90 mm`; 인접 PTH와 escape trace 사이 최소 동박 간격은 약 `0.295 mm`다.
- 일반 신호 via는 `0.60/0.30 mm`; pair B만 P/N에 각각 같은 through-via 1개를 쓴다.
- A/C/D는 F.Cu, B는 J1 쪽 B.Cu에서 진행한 뒤 T2 앞에서 대칭적으로 F.Cu로 전환한다.
- T2의 기준면 전환용 GND via 네 개는 P/N 사이가 아닌 바깥쪽에 대칭 배치한다. 각 signal via와의 중심 간격은 `1.355 mm`, 동박 가장자리 간격은 `0.755 mm`다.
- T4도 F.Cu에 둔다. B.Cu로 뒤집으면 F.Cu 전용 SMA center launch 때문에 single-ended 쪽 via가 필요하고 채널 간 fixture 대칭성이 나빠진다.
- SMA는 MyAntenna `A-SMA-KE-16.5A` (`C22467617`)로 통일한다. 권장 PCB 두께 `1.6 ±0.05 mm`에 nominal 1.5862 mm는 들어가지만 JLC 일반 두께 ±10%는 이 기구 공차를 보장하지 않으며, 정격은 50 Ω / DC–6 GHz다. 기존 Amphenol `132289`는 PCB 두께 상한 1.57 mm가 nominal stack보다 작아 최종 BOM에서 제외했다.
- `A-SMA-KE-16.5A`는 기존 JLC 조달 검토에서 Standard PCBA의 wave-solder/high-difficulty 품목으로 분류됐다. 현재 CAD의 부품/land pattern을 유지하며, 실제 조립 방식에 맞춰 board-edge 안착, 방향, 납땜 접근성과 두께 공차를 확인한다. PCBA를 선택하면 업체 공정도 확인한다.
- 서로 다른 controlled signal 사이 최소 clearance는 `0.60 mm`; 가능하면 그 이상을 유지한다.
- 결합 gap은 최소 `0.21 mm` / 권장 `0.216 mm`; fan-out을 포함한 uncoupled 길이는 일반 pair `16.0 mm`, split pair B `16.5 mm` 이하로 제한한다.
- transformer 앞에서는 한쪽 선에 짧은 U자 보정을 넣지 않는다. 대신 coupled trunk의 마지막 분기점을 약 1.3 mm 이동해 부드러운 fan-out 형상으로 end-to-end 길이를 맞춘다.
- RCT4를 포함한 선택형 CT-GND 경로는 0 Ω 저항의 GND pad를 내부 GND plane에 짧게 연결한다. RCT가 DNP이면 GND측 동박과 via는 plane에 남지만 transformer center-tap으로 이어지는 경로는 개방된다.
- L2/L3에는 track 및 non-GND zone을 금지한다.

저장된 외층 선분 길이 검산 결과는 다음과 같다. B만 P/N에 동일한 via 한 개가 있으므로 via 지연도 대칭이다.

| Pair | P length | N length | P–N 차이 | P/N via |
|---|---:|---:|---:|---:|
| A | 44.9649 mm | 44.9649 mm | 0.0000 mm | 0 / 0 |
| B | 32.9301 mm | 32.9301 mm | 0.0000 mm | 1 / 1 |
| C | 32.8357 mm | 32.8357 mm | 0.0000 mm | 0 / 0 |
| D | 43.6677 mm | 43.6677 mm | 0.0000 mm | 0 / 0 |

KiCad의 `skew (within_diff_pairs)`는 전체 선분 합이 아니라 결합 구간을 평가한다. bend의 안쪽/바깥쪽 차이를 허용하도록 최대 `0.55 mm`로 두었고, 위 표의 end-to-end 합계는 별도로 검산했다.

## 조립

- T1–T4: Mini-Circuits `ADT2-1T+`, CD542.
- J1: Amphenol `RJE591885401`, CAT6 shielded, LED/magnetics 없음.
- J2–J5: MyAntenna `A-SMA-KE-16.5A` edge-mount SMA, JLC/LCSC `C22467617`; 현재 CAD 기준 부품. 손납땜/PCBA 중 실제 조립 방법에 맞는 안착·납땜 조건을 확인한다.
- RCT1–RCT4: 각 보드에서 기본 DNP이며, 이 `CT-FLOAT` 상태를 golden/DUT 비교의 baseline으로 사용한다.
- `CT-GND` 영향만 별도로 비교할 때 두 보드의 RCT1–RCT4, 총 8개 위치에 0 Ω을 모두 장착한다. 보드 한쪽만 또는 일부 pair만 장착한 mixed 상태는 사용하지 않는다.
- RSH1: 동일 PCB 두 장 중 VNA Port 1 쪽 보드에만 기본 0 Ω을 장착하고, Port 2 쪽 보드는 DNP로 둬 DUT shield의 DC 접점을 한 점으로 만든다. 어느 쪽을 접지했는지는 결과와 함께 기록한다.
- CSH1: 두 보드 모두 기본 DNP. AC shield bond 시험 시 해당 보드의 RSH1을 제거한 뒤 1 nF / 2 kV를 장착한다. 한 보드에서 RSH1과 CSH1을 동시에 장착하지 않는다.

LibreVNA의 두 RF port는 공통 GND를 사용하므로 RCT 8개를 장착하면 두 fixture의 center tap에 공통모드 기준 경로가 추가된다. 따라서 `CT-GND` 결과는 케이블/슬립링 고유값이 아니라 해당 종단 조건을 포함한 비교값으로 해석한다.

두 지그는 같은 PCB artwork를 사용하지만 기본 RSH1 상태는 서로 다르다. CT-FLOAT와 CT-GND를 비교할 때 RSH1/CSH1과 cable 배치를 고정하고, **CT 상태 변경 후 커넥터 끝 O/S/L/T 보정을 다시 취득**한다. patch shield, 어댑터 SHIELD plane, M12 body/패널에 추가 접지 경로가 있으면 한쪽 RSH1만 장착했다는 사실만으로 전체가 단일 접지점이라고 할 수 없다. 실제 경계를 기록한다.

현재 구성의 최소 공통 지그는 한 측정 세트당 **2장**이며, 예비품과 동시 운용 세트 수를 포함한 신규 총 발주량은 아직 정하지 않았다. 사용자가 희망한 bare PCB + 손납땜을 기본 조립 선택지로 검토하고, 작은 RF/SMT 부품의 작업성에 따라 부분 reflow/PCBA를 선택할 수 있다. 과거 문서의 “사용자 납땜을 가정하지 않는다”는 조건을 현재 요구에 적용하지 않는다.

RSH1 조립 상태는 실제 작업 지시와 보드 표기에 반영한다. 공통 CAD/export의 RSH1 DNP 후보를 그대로 쓰면 bonded variant가 자동으로 만들어지지 않는다. 과거 구매 수량·BOM은 [이력 자료](../docs/legacy/README.md)이며, 새 어댑터의 조립 부품은 [JLCPCB_BUILD](../adapters/JLCPCB_BUILD.md)에 있다. 조립 후 RJ45 1–8, shield tab, SMA–transformer 연결과 RSH1 상태를 continuity로 확인한다.

## 측정 순서

1. 두 coax 끝에서 50 Ω full 2-port SOLT를 수행하고 활성화한다.
2. 이 보드와 선택한 어댑터·RJ45 연결을 고정한다. 각 보드의 미사용 SMA를 50 Ω으로 종단한다.
3. 어댑터 뒤 DUT 접속면에서 Port 1 O/S/L 3개, Port 2 O/S/L 3개, reciprocal 자작 thru 1개를 측정해 저장한다.
4. [Python 도구](../analysis/README.md)로 커넥터 끝 UnknownThru 보정계수를 만든다.
5. 같은 SMA 보정 상태에서 DUT를 측정하고 저장된 계수로 보정한 100 Ω 결과를 분석한다.
6. pair·어댑터·포트 할당·CT/shield 상태가 달라지면 해당 구성의 보정을 새로 만든다.

SMA SOLT만 적용한 원본에는 지그가 포함된다. Python 결과는 표준 모델과 고정된 두 error box 가정 아래 커넥터 기준면으로 이동한 balanced effective two-port다. full mixed-mode Sdd/Sdc/Scd/Scc나 산업 환경 적합 판정을 뜻하지 않는다. NEXT/FEXT는 별도 연결별 보정 및 fixture 누설 검증이 필요하다. 최신 설정과 결과 해석은 [VNA_TEST_PLAN.md](../VNA_TEST_PLAN.md)를 따른다.

## 파일과 재생성 주의

- `balun_eth_rj45.kicad_pcb/.kicad_pro/.kicad_dru`: Rev B 설계와 규칙.
- `balun_eth_rj45_drc.rpt`: 최종 KiCad DRC 결과.
- `apply_jlc_rev_b.py`: 수동 저장본을 JLC Rev B로 변환한 재현용 updater. 전체/`--routing-only` 경로 모두 변경 뒤 native KiCad zone refill+save와 DRC/schematic parity를 강제하고, 실패하면 nonzero로 중단한다. 이미 Rev B인 보드에는 전체 변환을 다시 실행하지 말고 fan-out만 갱신할 때 `--routing-only`를 사용한다.
- `generate_pcb.py`: 이전 Rev A 생성기. 기본 실행은 차단되어 있으며 현 Rev B PCB를 만들지 못한다.
- `fabrication/`과 `*_fabrication_HOLD.zip`: 폐기된 Rev A 로컬 참고 자료다. Git에서 제외하며 발주에 사용하지 않는다.

제작 Gerber는 항상 zone을 확인·재충전하는 `--check-zones`로 export하고, In1/In2에 실제 GND plane region이 있는지 CAM에서 확인한다. updater가 fill을 저장하더라도 이후 수동 편집본에 대한 release 검사는 생략하지 않는다.

## 공식 자료

- [JLCPCB impedance calculator guide](https://jlcpcb.com/help/article/user-guide-to-the-jlcpcb-impedance-calculator)
- [JLCPCB impedance stack-ups](https://jlcpcb.com/impedance)
- [JLCPCB multilayer structures](https://jlcpcb.com/help/article/multi-layer-pcb-standard-laminated-structures)
- [JLCPCB PCB capabilities](https://jlcpcb.com/capabilities/pcb-capabilities/)
- [ADT2-1T+ datasheet](https://www.minicircuits.com/pdfs/ADT2-1T+.pdf)
- [RJE591885401 product page](https://www.amphenol-cs.com/product/rje591885401.html)
- [MyAntenna A-SMA-KE-16.5A / C22467617](https://jlcpcb.com/partdetail/MyAntenna-A_SMA_KE_165A/C22467617)
- 현재 제작 범위는 [설계 검토 인계](../DESIGN_REVIEW_HANDOFF.md)와 [어댑터 제작 초안](../adapters/JLCPCB_BUILD.md)을 따른다. 루트의 기존 합산 구매 CSV/가이드는 과거 구성의 기록이다.
