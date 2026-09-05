# JLCPCB fabrication notes — balun_eth_rj45 Rev B

**2026-09-05 적용 범위:** 현재도 사용하는 공통 RJ45 Rev B 한 보드의 nominal 적층/geometry 참고다. 전체 시스템 수량과 조립 방식은 [설계 검토 인계](../DESIGN_REVIEW_HANDOFF.md), 새 수동 어댑터는 [adapters/JLCPCB_BUILD](../adapters/JLCPCB_BUILD.md)를 따른다. 현재 CAD의 SMA 부품은 유지했으나 기존 PCBA 공정 설명을 손납땜 금지 조건으로 해석하지 않는다.

최신 실제 화면별 선택과 이유, 비아 예외는 [주문 가이드](../docs/jlcpcb/README.md)를 우선한다. 이 문서는 공통 지그의 적층·geometry 참고다. 임의 대체 stack-up은 허용하지 않는다. 아래 Dk는 설계 당시 입력값이며 현재 주문 solver의 supplier 보증값으로 간주하지 않는다.

## 주문 선택값

| 항목 | 선택값 |
|---|---|
| Layers | 4 |
| PCB thickness | 1.6 mm |
| Outer copper | 1 oz |
| Inner copper | 0.5 oz |
| Material type | FR-4 TG155 / Nan Ya NP-155F |
| Impedance control | 별도 `±10% (±5Ω if value≤50Ω)` 옵션 선택 |
| Stack-up | `JLC04161H-7628 (Standard)` |
| Solder mask | Green |
| Surface finish | ENIG |
| Impedance coupon/test | 비고로 coupon/성적서 요청, 제공 여부 CAM 확인 |

JLC의 주문 두께 표기는 1.6 mm이고 이 stack-up의 nominal 합계는 약 1.5862 mm다. SMA는 MyAntenna `A-SMA-KE-16.5A` (`C22467617`)로 통일했으며, 제조사 권장 PCB 두께 `1.6 ±0.05 mm`에 nominal stack은 들어가지만 일반 JLC 완성 두께 ±10%가 그 공차를 보장하지는 않는다. 생산 두께 확인이 필요하다. 기존 Amphenol `132289`는 PCB 두께 상한 1.57 mm 때문에 최종 BOM에서 제외했다. `C22467617`은 JLC Standard PCBA의 wave-solder/high-difficulty 품목이므로, 주문 시 제조사 land pattern, routed edge 안착, 바깥쪽 방향과 fixture/engineering 비고를 반드시 확인한다.

## 고정 적층

| 위에서 아래 | 재료 | 두께 | Dk |
|---|---|---:|---:|
| L1 copper | Cu | 0.0350 mm | — |
| Prepreg 7628 | NP-155F | 0.2104 mm | 4.40 (설계 입력) |
| L2 copper | Cu | 0.0152 mm | — |
| Core | NP-155F | 1.0650 mm | 4.36 (설계 입력) |
| L3 copper | Cu | 0.0152 mm | — |
| Prepreg 7628 | NP-155F | 0.2104 mm | 4.40 (설계 입력) |
| L4 copper | Cu | 0.0350 mm | — |

L1은 L2, L4는 L3를 기준면으로 사용한다. L1/L4 blanket GND pour를 제거했으므로 JLC calculator에서 coplanar 구조가 아닌 일반 outer microstrip 구조를 선택한다.

## 임피던스 geometry

| Net class | 목표 | Width | Edge gap | 기준면 |
|---|---:|---:|---:|---|
| RF50 | 50 Ω single-ended | 0.357 mm | — | L2 또는 L3 |
| ETH100 | 100 Ω differential | 0.234 mm | 0.216 mm | L2 또는 L3 |

[2026-09-05 공식 계산기 결과와 화면](../docs/jlcpcb/IMPEDANCE.md)을 반영한 치수다. 제조 CAM/coupon은 아직 확인하지 않았다. KiCad rule 폭은 RF 0.356–0.358 mm(권장 0.357), differential 0.233–0.235 mm(권장 0.234)다. 결합 gap 최소 0.21 mm / 권장 0.216 mm이며 connector/transformer fanout은 균일 선로 계산 범위에서 제외한다.

RJ45 PTH pin field의 `0.15 mm` neck-down은 connector 내부의 매우 짧은 escape 구간이며 100 Ω 계산 geometry가 아니다. 이 구간을 늘리지 않는다.

## CAM/DFM 확인표

- L1/L4에 blanket copper zone이 없어야 한다.
- L2와 L3에는 끊김 없는 `/GND` zone만 있어야 한다.
- L2/L3에 signal track이 없어야 한다.
- RF track은 모두 0.357 mm여야 한다.
- 결합 differential trunk는 0.234/0.216 mm여야 한다.
- J1 signal PTH는 1.30/0.90 mm이고 annular ring은 0.20 mm다.
- via는 0.60/0.30 mm다.
- pair B만 signal via를 사용하며 P/N 각각 1개다.
- pair B signal via 주변의 GND return via 네 개는 각 signal via에서 중심 간 `1.355 mm`로 대칭 배치한다.
- unused SMA에는 PCB 부품이 아니라 측정 시 외부 50 Ω terminator를 장착한다.
- Keystone `5001` 권장 mounting hole은 1.02 mm이고 현재 KiCad standard footprint drill은 1.00 mm다. JLC finished-hole 공차와 snap-fit retention을 확인하거나 첫 샘플을 실제 삽입해 승인한다.
- 공통 RJ45 보드 한 장의 SMA 4개는 현 CAD의 MyAntenna `A-SMA-KE-16.5A` / `C22467617` 기준이다. 다른 부품을 사용하면 land pattern과 두께/안착 조건을 함께 검토한다. 과거 전체 구성의 SMA 12개 합계를 현재 신규 발주량으로 사용하지 않는다.
- `C22467617`의 패드가 board edge에 맞닿고 connector body가 보드 밖쪽을 향하는지 JLC placement/DFM 화면에서 확인한다.
- fabrication ZIP 이름에 `Rev A` 또는 `HOLD`가 있으면 발주하지 않는다.
- Gerber는 `--check-zones`로 생성하고 In1/In2 각각에 실제 `/GND` plane region polygon이 있는지 CAM에서 확인한다.

주문 업로드 후 JLC engineering이 stack-up, 선폭 또는 간격 변경을 제안하면 자동 승인하지 않는다. 변경된 수치를 JLC impedance calculator로 다시 계산한 뒤 KiCad 규칙과 배선을 함께 갱신해야 한다.
