# JLCPCB 적층·임피던스 제조 검증 — 2026-08-31

> **과거 기록:** 이 문서의 0.35 및 0.23/0.22 mm 계산은 현 주문 기준에서 대체됐다. [2026-09-05 공식 계산기 화면·현재 CAD 검증](docs/jlcpcb/IMPEDANCE.md)을 우선한다. 과거 정량 결과를 이번 재검증 결과로 해석하지 않는다.

이 문서는 `balun_eth_rj45`, `balun_slipring/molex_end`, `balun_slipring/m12_end` 세 PCB의 JLCPCB 4층 제작 조건과 controlled-impedance geometry를 **2026-08-31 주문 화면 및 공식 계산 자료**에 맞춰 검증한 기록이다. 결론은 다음과 같다.

- 세 PCB의 주 전송선 geometry는 지정 적층에서 50 Ω / 100 Ω 목표와 잘 맞는다.
- 반드시 `JLC04161H-7628 (Standard)`를 명시하고, 다른 적층 또는 선폭으로 자동 변경된 production file은 승인하지 않는다.
- JLCPCB가 공표하는 controlled-impedance 생산 허용차는 ±10%다. 아래 계산값이 목표에 매우 가깝다는 사실은 완성 보드가 그보다 좁은 공차로 보증된다는 뜻이 아니다.
- RJ45 pad 앞의 0.15 mm neckdown, edge-launch SMA pad의 routed edge 접촉, SMA가 요구하는 보드 두께 공차는 별도의 release 위험이다. 아래 승인 절차를 생략하면 안 된다.

## 적용 범위와 authority

| 항목 | 적용 파일 |
| --- | --- |
| RJ45 지그 | `balun_eth_rj45/balun_eth_rj45.kicad_pcb`, `.kicad_pro`, `.kicad_dru` |
| Slip-ring Molex endpoint | `balun_slipring/molex_end/balun_slipring_molex.kicad_pcb`, `.kicad_pro`, `.kicad_dru` |
| Slip-ring M12 endpoint | `balun_slipring/m12_end/balun_slipring_m12.kicad_pcb`, `.kicad_pro`, `.kicad_dru` |

이 문서는 주문 설정의 release 기준이지만, 유전체와 solder-mask 입력값은 JLCPCB가 바꿀 수 있다. 따라서 **실제 주문 시점의 JLCPCB live calculator 결과, 선택된 stackup, production file이 최종 authority**다. 주문 직전에 계산 결과 화면 또는 PDF와 stack revision을 저장하고 이 문서와 대조한다.

## 지정 적층: JLC04161H-7628 (Standard)

세 `.kicad_pcb`에 저장된 적층은 서로 같고, JLCPCB 공식 `JLC04161H-7628` 치수와 일치한다.

| 위에서 아래로 | 재료/동박 | CAD 두께 | 주문 해석 |
| --- | --- | ---: | --- |
| F.Cu | Cu | 0.0350 mm | 외층 base copper 1 oz; impedance solver의 도금 후 외층 모델은 별도 |
| dielectric 1 | Nan Ya NP-155F, 7628 prepreg | 0.2104 mm | L1→L2 기준 높이, nominal Dk 4.40 |
| In1.Cu | Cu | 0.0152 mm | 내층 0.5 oz, 연속 GND reference |
| dielectric 2 | Nan Ya NP-155F core | 1.0650 mm | 중앙 core |
| In2.Cu | Cu | 0.0152 mm | 내층 0.5 oz, 연속 GND reference |
| dielectric 3 | Nan Ya NP-155F, 7628 prepreg | 0.2104 mm | L4→L3 기준 높이, nominal Dk 4.40 |
| B.Cu | Cu | 0.0350 mm | 외층 base copper 1 oz; impedance solver의 도금 후 외층 모델은 별도 |

동박과 dielectric 합은 CAD의 전체 두께 `1.5862 mm`다. JLC 주문값은 `1.6 mm`이며, JLC 공식 일반 두께 공차 ±10%를 적용하면 완성 두께 허용 범위는 약 `1.44–1.76 mm`다.

### 중앙 core Dk 불일치 — CAD를 자동 수정하지 말 것

현재 CAD의 1.065 mm core Dk는 `4.36`이다. 그런데 JLCPCB 공식 공개 calculator guide의 NP-155F core 표는 0.70 mm 초과 core에 `4.43`을 제시하고, 2026-08-31 live template API snapshot은 같은 template에 `4.38`을 제시했다. 서로 다른 공식 값이므로 `4.36`을 단순 오기로 단정할 수 없다.

현재 controlled traces는 L1/L4에서 바로 인접한 L2/L3 plane을 참조하므로 중앙 core Dk는 아래 외층 microstrip 계산에 직접 들어가지 않는다. **CAD는 현 상태로 유지**하고, 향후 내층 signal을 추가하거나 broadside coupling을 평가할 때 JLC의 그 주문 시점 stack data를 받아 다시 모델링한다.

## 공식 field-solver 재계산

계산 topology는 L1/L4의 `coated microstrip, non-coplanar`다. 인접 plane까지 `H = 0.2104 mm`, 7628 prepreg `Er = 4.40`, 외층 finished copper `T = 1.6 mil`을 사용했으며, etching compensation은 공식 guide대로 `W2 = W1 - 0.7 mil`을 사용했다. Ground pour와 via fence는 reference plane을 대신하는 coplanar side ground로 계산하지 않았다.

JLCPCB의 공식 자료 두 곳은 solder-mask 두께 입력이 서로 다르다. 두 조건을 각각 계산한 결과는 다음과 같다.

| 공식 snapshot | mask C1/C2/C3 | 50 Ω geometry 결과 | 100 Ω differential geometry 결과 |
| --- | --- | ---: | ---: |
| 공개 calculator guide, 2026-06-15 | 1.2 / 0.6 / 1.2 mil, Er 3.8 | `W=0.35 mm → 49.9328 Ω` | `W/S=0.23/0.22 mm → 100.1103 Ω` |
| live impedance API, 2026-08-31 | 1.0 / 0.6 / 1.0 mil, Er 3.8 | `W=0.35 mm → 49.9955 Ω` | `W/S=0.23/0.22 mm → 100.2795 Ω` |

두 공식 조건의 차이는 50 Ω 선로에서 약 0.063 Ω, 차동 선로에서 약 0.169 Ω로 매우 작다. 설계 결론은 변하지 않지만, live 설정이 변경될 수 있으므로 발주 당시 snapshot을 production release에 첨부한다.

JLCPCB가 공표하는 controlled-impedance tolerance ±10%를 적용하면 acceptance band는 50 Ω 선로 `45–55 Ω`, 100 Ω 차동 선로 `90–110 Ω`다. 이는 일반 선폭 공차가 아니라 JLC controlled-impedance service의 완성 임피던스 공차다.

## 실제 CAD geometry와 규칙 검증

| 검사항목 | 실제 값 | 판정/주의 |
| --- | --- | --- |
| RF50 main trace | 세 설계 모두 0.35 mm, L1/L4 | 계산 목표와 일치 |
| ETH100 main pair | 세 설계 모두 W/S 0.23/0.22 mm | 계산 목표와 일치 |
| signal reference | In1/In2 signal routing 금지, GND zone 사용 | 외층 microstrip 전제와 일치. Gerber에서 실제 plane polygon을 재확인해야 함 |
| Slip-ring RF launch | transformer courtyard의 0.55 mm flare 1.5 mm, 이후 W=0.35 mm 직선 1.0 mm와 2.54×2.54 mm jog; SMA까지 centerline 26.762102 mm | A/B가 22 mm 평행이동으로 동일하고 SMA에 직선 진입; production file에서 폭/경로를 임의 조정하지 않음 |
| Slip-ring RF trace–M3 | RF 긴 직선과 H3/H4 중심 6.0 mm; trace edge–In1 plane void edge 약 3.9745 mm | 금속 head/washer의 실제 외경·장착 면은 별도 기구 승인 필요 |
| RJ45 pair-B layer change | 0.60/0.30 mm signal via 2개 | JLC 일반 via 능력 안쪽이지만 via discontinuity는 REF fixture baseline에 포함됨 |
| 나머지 signal via | 없음 | 양호 |
| GND stitching via | 0.60/0.30 mm | JLC 능력 안쪽 |
| RJ45 PTH pad | pad 1.30 / drill 0.90 mm, annular ring 0.20 mm | JLC 4층 1 oz 권장치와 같음; 여유를 더 줄이면 안 됨 |
| RJ45 PTH-to-escape trace | 최소 약 0.295 mm | JLC 최소 0.28 mm보다 0.015 mm 큼. 권장 0.35 mm에는 못 미쳐 CAM 변경 금지 |
| board outline | RJ45 80×74 mm; slip-ring 약 68×44 mm | 일반 outline tolerance 사용 가능. slip-ring 44 mm 변 때문에 JLC precision-outline 최소 조건을 주문 시 재확인 |

세 `.kicad_pro`의 net class는 `RF50 = 0.35 mm`, `ETH100 = 0.23 mm / gap 0.22 mm`이고 `.kicad_dru`가 이를 좁은 범위로 고정한다. Gerber가 아직 authority가 아니므로, release 때 반드시 zone refill 후 DRC와 CAM 측정을 다시 수행한다.

### RJ45 0.15 mm neckdown — 확정된 국부 discontinuity

RJ45 J1 PTH 탈출부에는 각 conductor마다 폭 `0.15 mm` neckdown이 있다. 길이는 한쪽이 약 `3.04 mm`, 다른 쪽이 약 `5.07 mm`라 pair 내에서도 대칭이 아니다. A/C/D의 neckdown 구간 gap은 약 `0.87 mm`, layer-change가 있는 B pair의 분리 구간은 약 `2.91 mm`다.

동일한 JLC outer-layer 조건으로 0.15 mm 폭을 계산하면 대략 다음과 같다.

- W/S `0.15/0.87 mm`: 약 `140.94 Ω differential`
- W/S `0.15/2.91 mm`: 약 `144.42 Ω differential`

따라서 이것은 100 Ω controlled section이 아니다. 다만 3.04/5.07 mm는 1–200 MHz에서 전기적으로 매우 짧다. `Er_eff≈3`, 100 Ω 선로 안에 141 Ω section 하나만 있다고 단순화한 계산에서는 그 section 자체의 return loss가 약 100 MHz `48/44 dB`, 200 MHz `42/38 dB`이므로, 이 숫자만으로 RJ45 보드를 폐기할 정도의 결함이라고 판단하지 않는다. 실제 connector pad, 두 conductor의 전이 위치 차이와 pair-to-pair coupling은 이 단순 모델에 없으므로 mode conversion과 NEXT/FEXT floor는 여전히 REF 반복측정으로 확인해야 한다.

현재 2-port balun 구성은 `Sdc/Scd`를 직접 측정할 수 없다. 첫 PCB에서는 golden RJ45 REF를 사용한 S11/S22/S21/S12 반복성, 방향 비대칭과 crosstalk floor를 확인하고, 4-port mixed-mode 장비가 나중에 확보된 경우에만 gated `Sdd/Sdc/Scd/Scc`를 추가한다. PTH clearance를 침범하면서 단순히 0.23 mm로 굵히면 안 되므로 이 문서에서는 CAD 자동 수정 대상으로 보지 않는다.

### Edge-launch SMA pad — 일반 edge clearance 예외

SMA center/ground launch pad는 connector가 routed board edge에 물리도록 의도적으로 Edge.Cuts까지 닿는다. JLC의 일반 routed-edge copper clearance 권고와 충돌하므로 CAM이 copper를 pull-back, trim 또는 재배치하면 RF launch와 납땜 형상이 망가진다.

- 주문 Remark에 이 예외를 명시한다.
- `Confirm Production File = Yes`를 선택한다.
- production file에서 모든 SMA pad가 원본처럼 board edge까지 도달하는지 확대 확인한다.
- `Gold Fingers = No`, `Castellated Holes = No`, `Edge Plating = No`로 주문한다.
- 승인되지 않은 pad/outline/trace 변경이 있으면 결제 후라도 생산 승인을 거절하고 engineering clarification을 요청한다.

### SMA slot과 완성 PCB 두께 — sample-fit 필요

선정 `A-SMA-KE-16.5A`의 권장 PCB 두께는 `1.6 ±0.05 mm`지만, JLCPCB의 일반 1.6 mm board thickness 허용 범위는 ±10%, 즉 약 `1.44–1.76 mm`다. nominal만 일치할 뿐 connector 권장 범위를 제조 공차 전체에서 만족한다고 보장할 수 없다.

첫 소량 주문에서 bare PCB와 loose SMA를 양쪽 thickness extreme 관점으로 sample-fit하고, 필요하면 JLC engineering에 완성 두께 tighter control 가능 여부를 서면 확인한다. 이 확인 전에는 대량 PCBA를 release하지 않는다.

## JLCPCB 주문 화면에 넣을 정확한 값

세 설계를 **각각 별도 PCB/PCBA 작업**으로 주문한다.

| 주문 항목 | 선택값 |
| --- | --- |
| Base Material | `FR-4` |
| Layers | `4` |
| Product Type | `Industrial/Consumer electronics` |
| Different Design | `1` |
| Delivery Format | `Single PCB` |
| PCB Thickness | `1.6 mm` |
| PCB Color / Silkscreen | `Green / White` |
| FR-4 material | `Nan Ya NP-155F` |
| Surface Finish | `ENIG` |
| Outer Copper Weight | `1 oz` |
| Inner Copper Weight | `0.5 oz` |
| Specify Stackup | `Yes` |
| Stackup | `JLC04161H-7628 (Standard)` |
| Controlled impedance | 2026-08-31 4층 quote UI에는 별도 label이 보이지 않았으므로 `Specify Stackup = Yes`와 Remark로 지정. 주문 시 별도 toggle이 표시되면 `Yes`; 50 Ω single-ended / 100 Ω differential, standard `±10%` |
| Min Via Hole/Size tier | `0.3 mm / (0.4/0.45 mm)` tier; 실제 via는 0.30/0.60 mm |
| Via Covering | `Tented` |
| Via Plating Method | `Not Specified` |
| Board Outline Tolerance | `Regular ±0.2 mm`; SMA fit은 first-article sample로 검증 |
| Gold Fingers / Castellated / Edge Plating | 모두 `No` |
| Blind Slots / Backdrill / Press-fit | 모두 `No` |
| Electrical Test | `Flying Probe Fully Test` |
| Confirm Production File | `Yes` |
| Mark on PCB | `Remove Mark` |

주문 화면의 표현이 바뀌면 같은 의미의 현행 항목을 선택하고 screenshot을 release 기록에 보관한다. `Specify Stackup = No`, JLC 추천 대체 stack, 임의 선폭 보정은 허용하지 않는다.

PCB Remark에는 세 작업 모두 아래 문장을 그대로 넣는다.

```text
Controlled impedance: 50 ohm single-ended W=0.35 mm and 100 ohm differential W/S=0.23/0.22 mm on L1/L4 referenced to L2/L3. Use JLC04161H-7628 only. Do not substitute stackup or modify controlled trace widths. Edge-launch SMA pads intentionally reach the routed board edge; do not pull back, trim, or move these pads. Please provide the production file for approval before fabrication.
```

Gerber ZIP 안의 README나 메모는 주문 지시로 취급되지 않을 수 있으므로 이 문장은 반드시 order Remark field에도 입력한다.

## Production release gate

1. KiCad에서 모든 zone을 refill하고 ERC/DRC를 통과시킨다.
2. `--check-zones`를 사용해 Gerber를 생성하고, In1/In2 Gerber에 실제 연속 GND polygon이 있는지 CAM에서 확인한다.
3. Gerber의 main width/gap `0.35`, `0.23/0.22 mm`, RJ45 neckdown `0.15 mm`, edge-launch SMA pad/outline 접촉을 측정한다.
4. 주문 시점 live calculator와 선택 stack 화면을 PDF 또는 screenshot으로 보관한다.
5. 주문 Remark를 입력하고 `Confirm Production File = Yes`를 선택한다.
6. JLC production file에서 stack 이름/층 두께/동박, outline, drill, SMA edge pad, neckdown, GND planes를 원본과 대조한다.
7. stack substitution, controlled width 변경, edge-pad pull-back가 하나라도 있으면 승인하지 않는다.
8. first article에서 PCB thickness를 여러 지점 측정하고 SMA sample-fit, continuity, 2-port golden-REF 반복성/fixture-floor 검사를 통과시킨 뒤 full build를 release한다. 4-port mixed-mode/TDR은 장비가 있을 때 추가 검증으로 수행한다.

## JLCPCB 공식 근거

- [JLCPCB PCB Impedance Calculator](https://jlcpcb.com/pcb-impedance-calculator/)
- [User Guide to the JLCPCB Impedance Calculator — 2026-06-15](https://jlcpcb.com/help/article/user-guide-to-the-jlcpcb-impedance-calculator)
- [JLCPCB Impedance Stackup](https://jlcpcb.com/impedance)
- [JLCPCB PCB Capabilities](https://jlcpcb.com/capabilities/pcb-capabilities)
- [JLCPCB PCB Thickness](https://jlcpcb.com/resources/pcb-thickness)
- [Gerber Files Preparation](https://jlcpcb.com/help/article/gerber-files-preparation)
- [How to Generate Gerber and Drill Files in KiCad](https://jlcpcb.com/help/article/how-to-generate-gerber-and-drill-files-in-kicad-6)
- [Instructions for Ordering](https://jlcpcb.com/help/article/instructions-for-ordering)
- [JLCPCB Instant Quote / live order form](https://cart.jlcpcb.com/quote)
