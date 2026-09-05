# JLCPCB/LCSC 최종 구매·조립 가이드

> **2026-09-05 적용 범위 변경:** 아래의 구매·조립 조건과 날짜별 “최신” 안내는 이전 전용 balun 구성의 기록이다. 현재 설계는 [설계 검토 인계](DESIGN_REVIEW_HANDOFF.md), 새 어댑터 제작 조건은 [adapters/JLCPCB_BUILD](adapters/JLCPCB_BUILD.md)를 따른다. 이번 구성의 통합 발주 수량표/BOM은 아직 갱신하지 않았으며, 아래 수량을 그대로 합산하거나 발주에 사용하지 않는다. 기존 구매의 집행·취소 여부는 이 문서 변경으로 판단하지 않는다.

> **2026-09-03 최신 구매 상태:** PCB는 JLCPCB에서 미조립 제작, 부품은 DigiKey 한국 중심(국내 인두팁만 예외)으로 구매한다. 실사용 Molex 2 + RJ45 4 + LLC 2 = 8장, 제작 예산 3종×5장=15장. 슬립링 M12 암 보드/암커넥터는 기존 케이블→RJ45 개조로 제외하며 LLC M12 수커넥터는 사내품 사용이다. **사내 수커넥터의 PCB 삽입은 사용자 확인 완료**이고 전기적 핀맵/수량 확인은 별도다. Samtec SMA는 구매 후보이며 현 CAD/MyAntenna와 최종 두께·공차/제조파일 정합 승인 전이다. 아래 이전 PCBA/구매 수량·품번은 발주에 사용하지 말고 [최신 구매요청서](PURCHASE_REQUEST_FORM_DRAFT_2026-09-03.md)를 따른다. 이번에 PCB/회로/풋프린트는 변경하지 않았다.

> **최신 조립 방식: 사내 손납땜.** 아래 PCBA 구매 계획은 변경 전 기록이다. 미조립 PCB, 개별 부품 구매 링크, 사진으로 확인한 HAKKO 936/907용 팁 및 기존 goot BS-15의 PCB 사용 금지 사항은 [`HAND_ASSEMBLY_PURCHASE_2026-09-03.md`](HAND_ASSEMBLY_PURCHASE_2026-09-03.md)를 따른다. JLC 부품 Pre-order는 한국으로 받을 손납땜용 부품 구매 경로가 아니다. 기존 제조 HOLD는 그대로 유지한다.

> **2026-09-03 발주 범위 변경:** 최신 계획은 슬립링 2세트 4장 + RJ45 2세트 4장 + LLC 전용 M12 2장, 총 PCBA 10장이다. LLC 측정에는 기존 RJ45 보드를 공유한다. 부품 납땜은 업체에 맡기며 RSH1도 지정 상태로 조립해 납품하도록 요청한다. 현재 수량·조립 variant·승인 조건은 [`PCBA_PURCHASE_SCOPE_2026-09-03.md`](PCBA_PURCHASE_SCOPE_2026-09-03.md)가 우선한다. [LLC PCB DRAFT A](balun_llc16/README.md)는 수커넥터 선정, 배치·배선 및 ERC/DRC/parity 검증을 완료했지만 JLC 조달·조립과 패널 기구 승인은 HOLD이며 제조 Gerber/BOM/CPL은 아직 없다. 이 문서 아래의 4장 검산값과 수동 RSH1 작업 방식, 기존 합산 CSV 및 2026-09-01 RJ45 2장 견적은 신규 발주 자료가 아니다. 기존 Gerber/BOM/CPL을 무검토 재사용하지 않는다.

아래는 기존 4장 비교 구성의 기술·조달 참고 기록이다. [`JLCPCB_FINAL_BOM.csv`](JLCPCB_FINAL_BOM.csv)도 다음 4장 구성을 기준으로 한다.

PCB 적층, 실제 선폭/간격, JLC 공식 field-solver 결과와 주문 production-file 승인 기준은 [`JLCPCB_IMPEDANCE_VERIFICATION_2026-08-31.md`](JLCPCB_IMPEDANCE_VERIFICATION_2026-08-31.md)를 함께 따른다.

- `balun_eth_rj45` 2장
- `balun_slipring/molex_end` 1장
- `balun_slipring/m12_end` 1장
- 두 프로젝트가 공유하는 동일한 외부 50 Ω SMA 종단기 6개
- 두 VNA cable end를 잇는 SMA female-female calibration thru 1개

루트 CSV는 전체 구매 수량을 합친 표이지 **JLCPCB 업로드용 BOM이 아니다**. 세 PCB 설계는 Gerber, 좌표와 connector reference가 서로 다르므로 다음 세 PCBA 작업으로 나눠야 한다.

1. `balun_eth_rj45`: 동일 artwork 2장
2. `balun_slipring/molex_end`: 1장
3. `balun_slipring/m12_end`: 1장

각 작업에서 해당 설계의 Gerber, BOM, CPL을 따로 생성하고 검토한다. JLC BOM에는 최소한 Comment, Designator, Footprint, JLCPCB/LCSC part number가, CPL에는 Designator, X/Y, Rotation, Layer가 필요하다. 루트의 합산 CSV를 세 작업 중 어느 하나의 BOM으로 업로드하지 않는다.

재현 가능한 산출물은 [`export_jlc_release.ps1`](export_jlc_release.ps1)로 만든다. 기본 실행은 세 프로젝트의 staged ERC/DRC/parity를 모두 검사하되 RJ45 release candidate만 Gerber ZIP과 DNP-excluded JLC-format BOM/CPL을 생성하며, 두 slip-ring 프로젝트는 HOLD notice만 만든다. 자세한 사용법은 [`RELEASE_EXPORT.md`](RELEASE_EXPORT.md)를 따른다.

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
| `SF-SF50+` calibration thru | 1 |

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

Transformer는 반드시 RoHS `ADT2-1T+`와 JLC `C5223988` 조합으로 확인한다. Mini-Circuits의 `+` 없는 `ADT2-1T`는 2025 EOL 공지에서 `ADT2-1T+`로 교체된 모델이며, `ADT2-1T+` 자체는 2026-08-31 공식 페이지에서 current stock 1,000개 초과로 표시됐다. URL이나 BOM에서 `+`가 빠진 비RoHS 구형 모델과 혼동하지 않는다.

RSH1을 공통 PCBA BOM에서 제외하면 동일한 RJ45 artwork 두 장에 서로 다른 assembly variant를 억지로 섞지 않아도 된다. 나중에 `CT-GND`를 별도로 시험하려면 양 끝의 관련 RCT를 전부 동시에 장착하고 REF/bypass baseline부터 다시 측정하며, 결과를 다른 공통모드 경계조건으로 표시한다.

## 외부 50 Ω 종단기와 케이블

Mini-Circuits `ANNE-50+` SMA-male 종단기 동일품 6개를 사용한다. RJ45 지그 두 장에는 SMA jack이 총 8개이고 2-port VNA가 2개를 사용하므로 IL/RL, NEXT, FEXT 측정에서 나머지 6개를 모두 종단해야 한다. 슬립링 endpoint 두 장에는 SMA가 총 4개라 두 개만 필요하므로 동일한 6개 세트를 공유한다.

가장 안전한 구매 수량은 신규 동일품 6개다. 기존 종단기가 정품 `ANNE-50+`로 명확히 식별되고 손상 없이 측정 세트에 사용할 수 있다고 확인된 경우에만 신규 5개를 산다. 그 외에는 기존 미확인품을 예비품으로 두고 crosstalk 측정 세트에 섞지 않는다. 조회 시 LCSC `C6125302`는 재고 0이었고 Mini-Circuits direct는 1,000개 초과 재고를 표시했다.

검증된 coax 2개가 없다면 Mini-Circuits `CBL-2FT-SMSM+` 동일품 2개를 추가한다. 이는 PCB 부품이 아닌 선택형 계측 액세서리다. 조회 시 LCSC `C18117095`는 재고 0, Mini-Circuits direct는 100개 초과였다. NEXT/FEXT에서는 cable-to-cable leakage가 측정 바닥값이 될 수 있으므로 두 케이블의 배치, 간격, 굽힘과 connector torque를 REF/DUT 사이에 고정한다.

동봉된 Open/Short/50 Ω Load는 각각 하나씩이어도 Port 1과 Port 2에 순차 재사용할 수 있다. 그러나 두 SMA-male cable end의 thru 측정이 빠지면 full 2-port SOLT가 아니므로 Mini-Circuits `SF-SF50+` 같은 SMA female-female thru 1개를 추가한다. LibreVNA에서는 `SOLT_12`를 활성화한다. 측정 중 unused balanced port는 각 balun을 통해 SMA 쪽 50 Ω load가 nominal 100 Ω differential termination으로 보이므로 별도 100 Ω 종단기를 자작할 필요가 없다.

## 해제해야 할 차단 항목

### 선정 SMA의 PCBA 검토

모든 보드의 SMA 12개는 MyAntenna `A-SMA-KE-16.5A`, JLC/LCSC `C22467617`로 통일한다. 권장 PCB 두께 `1.6 ±0.05 mm`는 nominal 1.5862 mm 적층과는 맞지만, JLCPCB의 일반 1.6 mm 완성 두께 공차 `±10%`(약 1.44–1.76 mm)는 connector 권장 범위보다 훨씬 넓다. 따라서 nominal 일치만으로 slot fit을 승인하지 말고 첫 소량 bare PCB와 loose SMA를 sample-fit하며, 필요하면 JLC engineering에 tighter thickness control 가능 여부를 확인한다. catalog 정격은 50 Ω / DC–6 GHz다. JLC에는 Standard-PCBA-only, wave solder, assembly difficulty High로 등록되어 있으며 조회 재고는 491개였다.

세 PCBA 작업에서 checked-in footprint/launch가 제조사 land pattern과 같은지, body가 routed board edge에 제대로 안착하는지, connector가 모두 바깥쪽을 향하는지, JLC가 wave-solder fixture/engineering 비고를 승인하는지 확인한다. 자동 대체품은 승인하지 않는다. 기존 Amphenol `132289` / `C3172723`은 PCB 두께 상한 1.57 mm가 선정 적층보다 작으므로 최종 BOM에서 제외한 legacy 부품이다.

### 슬립링 connector와 핀맵

Molex `5055680571` / `C585386`은 catalog와 footprint가 정의된 5핀 header이고 제조사 도면은 `505565` series와의 mating을 명시한다. 다만 `5055650501`이라는 정확한 housing MPN은 2세대 핀맵 슬라이드 14가 아니라 별도 4세대 표인 슬라이드 15에서 확인되므로, 이를 `REV-504`에 적용한 것은 **교차 슬라이드 추론**이다. endpoint PCBA 전에 loose sample로 실제 REV-504와의 체결, key 방향, pin 1, pad numbering과 1:1 footprint 출력을 확인한다.

Finecables `MB12FBAFF08ST-3` / `C22378785`는 조회 시 JLC 재고 0이라 global sourcing 또는 preorder가 필요하다. 제조사 female 8P 권장 PCB 배열은 로컬 footprint에 반영했지만, 조달 전에 정확한 suffix, mating-face view, A-key와 pin 1, PCB B면 배치와 제조사의 front-fastened panel/nut 접근, cable exit를 실물 DUT에 대조한다. `balun_slipring/PINMAP.md`의 Ethernet 4선 continuity 측정도 완료한다. 따라서 transformer와 SMA를 조달할 수 있더라도 이 두 검증 전에는 슬립링 PCBA 두 작업 모두 HOLD다.

REF/bypass harness는 Molex `5055650501` housing, `5054311000` contact 4개, NorComp `858FA08-103RAU1` M12 A-code male plug과 LAPP `2170284` 2-pair 100 Ω Cat.5e cable로 선정했다. Cable OD 5.6 ±0.3 mm는 M12 plug의 4–6 mm gland에 들어가지만, cable core 최대 Ø1.04 mm가 Molex terminal 상한 Ø1.02 mm보다 0.02 mm 큰 최악 공차가 있다. 따라서 최소 4개 contact는 sample crimp/pull/단면 또는 치수 검증에 쓰고, 최종 harness 4개와 재작업 spare를 별도로 확보한다(권장 사용계획 8–12개; 판매 MOQ 100개면 수량상 충족). 완성 cable 길이는 DUT의 connector-to-connector 실측 후 정하고, 전체 shield/drain은 CT-FLOAT baseline에서 양단 모두 절연한다.

재고가 있는 CAZN `M12-S8A-GPB M12` / `C19108981`은 drop-in 대안이 아니다. 조회 재고는 JLC 31개/LCSC 30개였지만, 이 부품은 straight PCB front-mount M12x1/D-cut/ring 구조이고 현재 Finecables 후보의 PG9/front-fastened panel 및 PCB B면 후보 기구와 footprint가 다르며 지원 PCB 두께도 명시되지 않았다. 기구 방향을 먼저 결정한 뒤 필요하면 loose sample 1개만 구매해 **재설계 후보**로 평가한다. 현재 BOM/CPL에서 Finecables 부품 대신 자동 매칭하거나 실장하지 않는다.

### Controlled impedance와 최종 DFM

상세 근거와 계산값은 [`JLCPCB_IMPEDANCE_VERIFICATION_2026-08-31.md`](JLCPCB_IMPEDANCE_VERIFICATION_2026-08-31.md)를 따른다. 각 제작 작업의 JLC 주문 화면에는 아래 값을 고정한다.

| 항목 | 주문값 |
| --- | --- |
| Layers / PCB Thickness | `4 / 1.6 mm` |
| FR-4 material | `Nan Ya NP-155F` |
| Outer / Inner Copper | `1 oz / 0.5 oz` |
| Surface Finish | `ENIG` |
| Specify Stackup | `Yes` |
| Stackup | `JLC04161H-7628 (Standard)` |
| Controlled impedance | `Impedance Control = ±10% (±5Ω if value≤50Ω)`; `Specify Stackup = Yes`와 아래 Remark도 함께 유지 |
| Via Covering | released Gerber는 via mask coverage의 최종 권위. 2026-09-01 quote UI에서 `Tented`가 disabled이고 `Plugged`가 자동 선택되므로, 그 상태에서는 `Plugged`를 유지하되 `Confirm Production File`에서 모든 stitching via가 solder-mask covered인지 확인. `Plugged`는 tented + solder-mask ink-filled 공정이며 이 보드의 RF 기능 변경 사유가 아님 |
| Electrical Test | `Flying Probe Fully Test` |
| Confirm Production File | `Yes` |
| Gold Fingers / Castellated / Edge Plating | 모두 `No` |

공개 JLC guide의 solder-mask 조건에서는 50 Ω `W=0.35 mm`가 `49.9328 Ω`, 100 Ω 차동 `W/S=0.23/0.22 mm`가 `100.1103 Ω`다. 2026-08-31 live API의 다른 mask snapshot에서도 각각 `49.9955 Ω`, `100.2795 Ω`로 사실상 같은 결론이다. 다만 실제 주문 시점 live calculator와 승인된 stack snapshot이 최종 authority이므로 결과 화면/PDF와 stack revision을 release 자료에 보관한다.

저장된 중앙 core Dk 4.36은 공식 공개 guide 4.43 및 당시 live template API 4.38과 서로 다르다. 현재 외층 전송선 계산에는 중앙 core가 직접 들어가지 않고 공식 값끼리도 일치하지 않으므로 CAD를 임의 수정하지 않는다. 다른 stack으로의 자동 대체, controlled 선폭 변경, stack 이름이 없는 production file은 승인하지 않는다.

PCB Remark에는 세 작업 모두 아래 문장을 그대로 입력한다. Gerber ZIP 내부 메모만으로 대신하지 않는다.

```text
Controlled impedance: 50 ohm single-ended W=0.35 mm and 100 ohm differential W/S=0.23/0.22 mm on L1/L4 referenced to L2/L3. Use JLC04161H-7628 only. Do not substitute stackup or modify controlled trace widths. Edge-launch SMA pads intentionally reach the routed board edge; do not pull back, trim, or move these pads. Please provide the production file for approval before fabrication.
```

Gerber는 모든 작업에서 zone refill을 강제하는 `--check-zones` 옵션으로 생성하고, In1/In2 Gerber에 실제 GND region polygon이 있는지 CAM에서 확인한다. DRC 보고서가 0이어도 미충전 zone outline만 저장된 PCB에서 옵션 없이 Gerber를 내보내면 plane 없는 파일이 성공 코드로 생성될 수 있다.

모든 SMA launch pad는 connector가 routed edge에 끼워지도록 의도적으로 Edge.Cuts까지 닿는다. 일반 copper-to-edge cleanup으로 pull-back/trim하면 안 된다. `Confirm Production File = Yes`로 받은 CAM에서 edge pad, outline, GND plane, drill과 controlled widths를 확대 대조하고, 차이가 있으면 승인하지 않는다.

RJ45, M12, SMA와 test point는 wave solder/fixture 비용이 생길 수 있다. JLC 3D/placement viewer에서 side와 rotation을 직접 검토하고 모든 part match를 수동 확인한다. catalog 재고가 있다는 사실만으로 local footprint, 실장면과 방향이 승인되는 것은 아니다.

네 보드에는 각각 NPTH M3 hole이 4개 있지만 fixture plate와 필요한 standoff 높이가 정해지지 않았다. 따라서 나사·spacer는 전기 BOM에서 임의 선정하지 않고 mechanical HOLD로 남긴다. 기구가 확정되면 nylon 등 비도전성 부품을 우선 사용해 의도하지 않은 chassis/ground 경로가 생기지 않도록 한다.

## 권장 주문 순서

1. `ANNE-50+` 6개와 `SF-SF50+` thru 1개를 주문한다. 기존 종단기가 위의 exact-part 예외를 만족할 때만 신규 load를 5개로 줄인다. 필요하면 `CBL-2FT-SMSM+` 2개도 주문한다.
2. `A-SMA-KE-16.5A` 12개와 JLC 견적이 계산한 attrition을 reserve하고 Standard PCBA의 wave 방향·fixture 비고를 명시적으로 검토한다.
3. RJ45 작업의 stack, impedance, design-specific BOM/CPL을 확인하고 RCT/CSH/RSH는 모두 PCBA DNP로 둔다. 위 PCB Remark를 입력하고 `Confirm Production File = Yes`를 선택한다.
4. Molex `5055680571`은 1–3개 loose validation sample을 확보하고, Finecables M12는 기구 도면 검토 뒤 최소 1개 sample/preorder를 확보해 REV-504/M12 continuity와 기구 검증을 완료한다. 완료 전에는 PCBA 수량이나 대체품을 확정하지 않는다.
5. REF harness의 contact/cable sample crimp 4개 이상과 M12 mating/pin-1을 통과시킨 뒤 DUT 실측 길이로 제작한다.
6. 각 HOLD를 해제한 뒤 해당 설계의 Gerber/BOM/CPL을 다시 생성하고 ERC, DRC, schematic–PCB parity와 JLC placement/DFM을 결제 전에 재확인한다. JLC production file에서 `JLC04161H-7628`, 선폭/간격, SMA edge pad와 plane을 확인하고 자동 대체 또는 CAM 수정을 승인하지 않는다.
7. 첫 소량 bare PCB에서 완성 두께를 측정하고 `A-SMA-KE-16.5A`를 sample-fit한다. fit 또는 edge launch가 불안정하면 full PCBA 전에 JLC engineering 및 connector 대안을 검토한다.
8. 입고 후 첫 조립품을 continuity 검사하고, 표시한 RJ45 Port-1 지그에만 `RSH1`을 수동 장착한 뒤 `CT-FLOAT` REF baseline을 만든다.

CSV의 재고는 **2026-08-13 KST** 조회 스냅샷이다. 주문 직전 다시 확인해야 하며, JLC가 실제 FIT 수량에 component attrition을 더할 수 있다.

## 선정 부품과 발주 자료

- [JLCPCB 적층·임피던스 제조 검증 — 2026-08-31](JLCPCB_IMPEDANCE_VERIFICATION_2026-08-31.md)
- [JLCPCB PCB Impedance Calculator](https://jlcpcb.com/pcb-impedance-calculator/)
- [JLCPCB Impedance Calculator Guide](https://jlcpcb.com/help/article/user-guide-to-the-jlcpcb-impedance-calculator)
- [JLCPCB Impedance Stackup](https://jlcpcb.com/impedance)
- [JLCPCB PCB Capabilities](https://jlcpcb.com/capabilities/pcb-capabilities)
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
- [Mini-Circuits SF-SF50+ SMA female-female thru](https://www.minicircuits.com/WebStore/dashboard.html?model=SF-SF50%2B)
