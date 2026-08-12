# JLCPCB fabrication notes — balun_eth_rj45 Rev B

이 문서는 JLCPCB 주문 화면에서 선택해야 할 값과 임피던스 기준을 고정한다. 임의 대체 stack-up은 허용하지 않는다.

## 주문 선택값

| 항목 | 선택값 |
|---|---|
| Layers | 4 |
| PCB thickness | 1.6 mm |
| Outer copper | 1 oz |
| Inner copper | 0.5 oz |
| Material type | FR-4 TG155 / Nan Ya NP-155F |
| Impedance control | Yes |
| Stack-up | `JLC04161H-7628 (Standard)` |
| Solder mask | Green |
| Surface finish | ENIG |
| Impedance coupon/test | 가능한 경우 precision/paid impedance test 선택 |

JLC의 주문 두께 표기는 1.6 mm이고 이 stack-up의 nominal 합계는 약 1.5862 mm다. 1.2 mm 보드보다 0.062 inch급 Amphenol `132289` edge-launch SMA에 훨씬 가깝지만, connector의 공식 PCB 최대 두께 1.57 mm보다 nominal이 0.0162 mm 두껍다. 시제품에서는 흔히 맞는 조합이지만 공차까지 포함한 보장은 아니다. 가능하면 실제 완성 두께를 1.57 mm 부근으로 관리할 수 있는지 JLC에 확인하고, 첫 connector를 dry-fit한 뒤 나머지를 조립한다.

## 고정 적층

| 위에서 아래 | 재료 | 두께 | Dk |
|---|---|---:|---:|
| L1 copper | Cu | 0.0350 mm | — |
| Prepreg 7628 | NP-155F | 0.2104 mm | 4.40 |
| L2 copper | Cu | 0.0152 mm | — |
| Core | NP-155F | 1.0650 mm | 4.36 |
| L3 copper | Cu | 0.0152 mm | — |
| Prepreg 7628 | NP-155F | 0.2104 mm | 4.40 |
| L4 copper | Cu | 0.0350 mm | — |

L1은 L2, L4는 L3를 기준면으로 사용한다. L1/L4 blanket GND pour를 제거했으므로 JLC calculator에서 coplanar 구조가 아닌 일반 outer microstrip 구조를 선택한다.

## 임피던스 geometry

| Net class | 목표 | Width | Edge gap | 기준면 |
|---|---:|---:|---:|---|
| RF50 | 50 Ω single-ended | 0.35 mm | — | L2 또는 L3 |
| ETH100 | 100 Ω differential | 0.23 mm | 0.22 mm | L2 또는 L3 |

JLC 계산기 nominal 결과는 약 50 Ω와 100 Ω다. KiCad rule tolerance는 RF 폭 0.34–0.36 mm, differential 폭 0.22–0.24 mm로 고정했다. 결합 gap은 최소 0.21 mm / 권장 0.22 mm이며, connector/transformer fan-out 길이는 별도의 uncoupled-length 규칙으로 제한한다.

RJ45 PTH pin field의 `0.15 mm` neck-down은 connector 내부의 매우 짧은 escape 구간이며 100 Ω 계산 geometry가 아니다. 이 구간을 늘리지 않는다.

## CAM/DFM 확인표

- L1/L4에 blanket copper zone이 없어야 한다.
- L2와 L3에는 끊김 없는 `/GND` zone만 있어야 한다.
- L2/L3에 signal track이 없어야 한다.
- RF track은 모두 0.35 mm여야 한다.
- 결합 differential trunk는 0.23/0.22 mm여야 한다.
- J1 signal PTH는 1.30/0.90 mm이고 annular ring은 0.20 mm다.
- via는 0.60/0.30 mm다.
- pair B만 signal via를 사용하며 P/N 각각 1개다.
- pair B signal via 주변의 GND return via 네 개는 각 signal via에서 중심 간 `1.355 mm`로 대칭 배치한다.
- unused SMA에는 PCB 부품이 아니라 측정 시 외부 50 Ω terminator를 장착한다.
- fabrication ZIP 이름에 `Rev A` 또는 `HOLD`가 있으면 발주하지 않는다.

주문 업로드 후 JLC engineering이 stack-up, 선폭 또는 간격 변경을 제안하면 자동 승인하지 않는다. 변경된 수치를 JLC impedance calculator로 다시 계산한 뒤 KiCad 규칙과 배선을 함께 갱신해야 한다.
