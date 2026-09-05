# balun_slipring

2026-09-03: Molex측·M12측 회로도를 각각 A4 한 장으로 재배치했다. 연결·부품·DNP와 PCB는 그대로이며, [가독성 정리 결과 및 PDF](../SCHEMATIC_READABILITY_2026-09-03.md)를 참고한다.

PALA720 2세대 슬립링의 100BASE-TX 전송 특성을 LibreVNA 2포트로 비교 측정하기 위한 지그 프로젝트다.

`Docs/[인수인계] PALA720.pptx` 슬라이드 14에서 2세대 Ethernet 논리 핀맵을 확인하고, KiCad `DRAFT 1` 회로도와 두 PCB의 connector fan-out에 반영했다. 다만 이 표는 인수인계 문서의 전사값이며 실물 `REV-504`의 continuity 측정값은 아니다. 커넥터 기구와 SMA/stack-up도 아직 차단 항목이므로 **DO NOT FABRICATE** 상태다.

## 문서에서 확인한 2세대 핀맵

슬라이드 14는 2세대의 Ethernet 4선 핀 번호와 선색을 보여 주지만 5극 하우징의 정확한 MPN을 직접 적지 않는다. Molex `5055650501`은 슬라이드 15의 별도 4세대 케이블 표에 명시된 부품을 2세대에도 적용해 본 **교차 슬라이드 추론 후보**다. PCB측 `5055680571`은 Molex가 공식적으로 `505565` series와 맞물린다고 지정한 같은 Micro-Lock Plus 1.25 mm 5극 header지만, 두 부품이 실제 `REV-504` 조합이라는 점은 라벨·BOM·실물 체결로 확인해야 한다.

| 신호 | Molex 5극 핀 (`5055650501` 후보) | 슬립링 선색 | M12 핀 |
| --- | ---: | --- | ---: |
| Ethernet TX+ | 1 | YEL | 4 |
| Ethernet TX− | 2 | ORN | 3 |
| Ethernet RX+ | 3 | BRN | 2 |
| Ethernet RX− | 4 | BLK | 1 |
| 지그 NC | 5 | 문서상 배정 없음 | — |

최종 지그 네트는 `PAIR_TX_* = TX`, `PAIR_RX_* = RX`로 정의한다.

| 지그 네트 | Molex측 J1 | M12측 J1 |
| --- | --- | --- |
| `PAIR_TX_P` / TX+ | pin 1 | pin 4 |
| `PAIR_TX_N` / TX− | pin 2 | pin 3 |
| `PAIR_RX_P` / RX+ | pin 3 | pin 2 |
| `PAIR_RX_N` / RX− | pin 4 | pin 1 |

M12 5–8번은 빈 핀이 아니다. 같은 슬라이드에서 5번은 GPS RS232_RX, 6번은 GPS 1PPS, 7번은 24VDC, 8번은 24VDC GND로 지정된다. 이 측정 지그에서는 네 핀 모두 **NC**로 두며 GND, shield 또는 종단에 연결하지 않는다. 특히 DUT에 전원이 연결된 상태에서 VNA 지그를 체결하지 않는다.

## 커넥터 판단

| 위치 | 부품 번호 | 판단 |
| --- | --- | --- |
| REV-504 Ethernet 케이블 하우징 | Molex `5055650501` 후보 | 슬라이드 15의 4세대 표에서 확인한 MPN을 2세대에 교차 적용한 추론; 실물 확인 필요 |
| Molex측 지그 PCB | Molex `5055680571` | 제조사가 `505565` series mate로 지정한 5극 PCB header; 실제 REV-504 체결·키·pin 1 확인 전 DNP |
| 슬립링 M12측 | Finecables `MB12MBAFF08ST-0` 후보 | catalog에 존재하는 8핀 A-coded male이지만 실제 DUT의 정확한 MPN은 미확인 |
| M12측 지그 PCB | Finecables `MB12FBAFF08ST-3` | catalog상 front-fastened 8핀 A-coded female 후보; suffix, 패널 구조, pin view와 구매 가능성 확인 전 DNP |

기존 4극 `5055680471`은 문서 연결과 맞지 않아 KiCad에서 제거했다. `5055680571`은 제조사 도면 기반 로컬 풋프린트다. `MB12FBAFF08ST-3`은 제조사의 female 8P 권장 PCB 배열(Ø5.5 원주, 중앙 pin 8, key축 기준 pin 1/2 ±33°)로 바로잡아 배치·배선했다. 도면상 pad geometry를 반영했어도 실제 체결, PCB면/패널 방향과 1:1 출력 검증은 남아 있으므로 둘 다 계속 DNP다.

## SRS1202-12CZ 근거와 한계

`Docs/05. 회전구동장치_슬립링(SRS1202-12CZ).pdf`의 SRS1202 Series 자료는 다음을 명시한다.

- 6/12/18회로, 회로당 2 A, 220 VDC/240 VAC
- precious-metal 접점, noise 50 mΩ max @ 100 rpm
- 절연저항 1000 MΩ @ 250 VDC, 내전압 시험 누설전류 0.1 mA 미만 @ 250 VAC
- CW/CCW 연속 회전, 정격 100 rpm, −30~80 °C
- 30 AWG Teflon lead, rotor/stator 각 200 mm
- 12회로형 본체 길이 `L=21 mm`, Ø24 flange, 3×Ø3.5 THRU on Ø18 PCD

이 일반 자료에는 100 Ω, twisted pair, Ethernet 대역폭, insertion/return loss 또는 crosstalk 보증이 없다. 또한 일반 색상표의 11/12번 `Pink/Silver`와 2세대 조립도상의 `WHT-BLK/WHT-BRN`이 다르므로 `-12CZ` 실제 연결에는 슬라이드 14를 우선한다.

`Docs/로텍_슬립링_SRS1202-12CZ_검사성적서.pdf`는 2022-11-14 출하 LOT 8 EA에 대한 외관·치수·DC 검사다. 기록된 두 시료는 절연 1.2 GΩ, 접촉회로 저항 241/248 mΩ, 순간단선 양호 및 합격이다. 이는 RF/Ethernet 성능 검증이 아니며, 접촉회로 저항과 데이터시트의 동적 noise 50 mΩ 사양은 같은 측정항목으로 해석하지 않는다.

`Docs/RS422_Cable_Assembly_Spec.pptx`는 EM2 Encoder Interposer와 Control Board 사이의 별도 10핀 RS-422 케이블 문서다. 그 핀맵, 부품번호와 길이는 이 슬립링 지그의 설계 근거에서 제외한다.

## 측정 및 PCB 전제

- 대상 신호: 100BASE-TX, 100 Ω 차동 2페어
- 구성: 슬립링 양 끝에 서로 다른 balun 지그 보드 1장씩
- 각 보드: SMA 2개와 임피던스비 1:2 `ADT2-1T+` 2개
- 동일 커넥터와 짧은 100 Ω twisted pair로 REF/bypass를 별도 제작
- 측정하지 않는 한 페어의 양끝 SMA 두 곳은 외부 50 Ω로 종단
- 최종 fan-out에는 점퍼 매트릭스를 두지 않고 짧고 대칭적인 고정 배선을 사용

센터탭 조립 기준은 다음 두 상태로 제한한다.

- `CT-FLOAT` — **기본 상태**. Molex측 `RCT1/RCT2`와 M12측 `RCT1/RCT2`, 즉 양단의 네 저항을 모두 DNP로 둔다.
- `CT-GND` — 공통모드 민감도를 확인하는 별도 진단 상태. 네 저항을 모두 0 Ω로 동시에 장착한다.

양끝 또는 TX/RX 사이에 RCT 상태를 섞지 않는다. 측정하지 않고 SMA를 50 Ω로 종단한 페어도 예외가 아니다. `CT-GND`에서는 양끝 secondary center tap이 LibreVNA의 공통 coax/chassis GND에 연결되어, pair 불균형과 mode conversion으로 생긴 공통모드 전류가 chassis로 빠지는 추가 경로가 생긴다. 이 때문에 insertion/return loss 또는 crosstalk가 더 좋아 보일 수 있지만, 이는 슬립링 자체가 개선된 것이 아니라 측정 경계조건이 바뀐 결과일 수 있다. REF와 DUT는 반드시 같은 CT 상태로 비교하고 상태를 결과에 기록한다.

두 보드의 각 P/N은 `balun_eth_rj45`와 같은 shared-centerline 방식으로 생성한다. 공통 중심선에서 P/N을 각각 ±0.225 mm offset해 W=0.23 mm, center spacing=0.45 mm, edge gap=0.22 mm를 유지하고, 커넥터와 transformer 바로 앞의 짧은 fan-in/out에서만 쌍을 연다. 모든 Ethernet trace는 F.Cu이며 signal via는 네 쌍 모두 0/0이다. 선택 조립용 중앙탭 0 Ω 저항은 B.Cu에 배치해 차동 트렁크를 가로막지 않으며, `CT-FLOAT` 기본 조립에서는 비운다.

이 구성의 2-port VNA 결과는 두 balun을 거친 single-ended 전송의 비교 proxy다. 차동·공통모드 성분을 독립적으로 분리하는 mixed-mode `Sdd/Sdc/Scd/Scc` 측정은 아니므로, `CT-GND` 결과를 본래의 differential 특성으로 해석하지 않는다. 절대 mixed-mode 특성이 필요하면 검증된 4-port 측정 또는 별도의 fixture characterization/de-embedding 절차가 필요하다.

ADT2-1T+의 dot은 primary pin 3과 secondary pin 6이다. 현재 P/N 이름은 secondary pin 4/6을 각각 P/N으로 두므로 **지그 한 장만 보면 한 번의 극성 반전**이 있다. 동일한 두 지그를 back-to-back으로 쓰는 비교 측정에서는 두 번 반전되어 전달 극성이 복구되지만, 단일 지그 de-embedding이나 절대 mixed-mode 위상 부호에는 이 convention을 반드시 반영한다.

M12 J1은 pin 1–4가 transformer 쪽을 향하도록 **PCB B면 electrical-layout 후보**로 배치했다. 제조사가 말하는 `front fastened`는 패널 체결 방식이고, KiCad의 B면 배치는 PCB 실장면이므로 서로 같은 용어가 아니다. 이 배치에서는 이전의 한쪽 극성만 B.Cu/via를 쓰던 비대칭 crossover가 없고, 모든 P/N이 connector PTH barrel 뒤 F.Cu에서 별도 routing via 0/0으로 진행한다. 실제 A-key/pin-1 mating view, PCB의 어느 면이 장비 외부를 향하는지, 패널 너트 접근과 케이블 방향은 실물로 확인하기 전까지 J1 DNP 차단 항목이다.

| 보드 / pair | P 길이 | N 길이 | P–N 차이 | 0.22 mm 결합 트렁크 최소 | Signal via P/N |
| --- | ---: | ---: | ---: | ---: | ---: |
| Molex TX | 31.082091 mm | 31.082091 mm | <0.000001 mm | 20.292153 mm | 0 / 0 |
| Molex RX | 31.910806 mm | 31.910806 mm | <0.000001 mm | 21.120867 mm | 0 / 0 |
| M12 TX | 28.060990 mm | 28.060991 mm | 0.000001 mm | 18.759529 mm | 0 / 0 |
| M12 RX | 27.579764 mm | 27.579765 mm | 0.000001 mm | 18.110302 mm | 0 / 0 |

생성기는 source geometry에서 skew ≤0.01 mm, 결합 트렁크 ≥16 mm와 fan-in/out ≤11 mm를 검사하고, 저장된 KiCad track에서 다시 skew ≤0.01 mm, F.Cu-only와 P/N via 0/0을 검사한다. KiCad가 꺾임에서 산출한 최대 uncoupled는 11.1474 mm이며, DRU는 gap 0.21/0.22/0.23 mm min/opt/max, uncoupled ≤11.20 mm, skew ≤0.10 mm, signal via 0개로 제한한다. 이는 기준 보드의 uncoupled 16/16.5 mm보다 더 엄격하다.

두 KiCad 초안은 68 × 44 mm, 4층 JLCPCB `JLC04161H-7628` 기준이며 core εr은 기준 보드와 같은 4.36으로 통일했다. W=0.23/G=0.22 mm는 이 stack, 외층 1 oz, green soldermask, non-coplanar 조건의 nominal 100 Ω 발주 geometry다. 저장소에는 JLC field-solver 결과 원본이 없으므로 실제 주문 전 JLC impedance calculator와 impedance-control/coupon으로 다시 승인해야 한다. SMA는 1.6 ±0.05 mm 권장 두께의 MyAntenna `A-SMA-KE-16.5A` (`C22467617`, 50 Ω / DC–6 GHz)로 통일한다. 기존 Amphenol `132289`는 1.57 mm 두께 상한 때문에 최종 BOM에서 제외했다. 새 SMA는 JLC Standard PCBA 전용 wave-solder/high-difficulty 품목이므로 두 endpoint 작업에서 land pattern, board-edge 안착, 방향과 fixture/engineering 비고를 각각 승인해야 한다.

2026-09-01에 두 RF50 launch는 transformer의 0.55 mm flare 뒤 0.35 mm로 바뀐 다음 1.0 mm 직진하고, 2.54×2.54 mm 45° jog를 거쳐 SMA 중심선으로 곧게 진입하는 형상으로 통일했다. A/B는 정확한 22 mm 평행이동 관계이고 각 centerline 길이는 `26.762102 mm`다. 긴 직선은 각각 `y=31/53 mm`라 H3/H4 중심에서 모두 6.0 mm 떨어지며, 채워진 In1 plane void edge와 trace copper edge 사이 계산 여유는 약 `3.9745 mm`다. 이는 기존 상단 경로가 금속 M3 head/washer와 가까워지는 문제를 피하기 위한 fixture 조립 변경이다. 그래도 실제 head/washer 외경, 장착 면과 조임 공구 영역은 1:1 실물 대조 전까지 provisional이다.

## 제작 전 차단 항목

1. `REV-504` 실물에서 Molex housing MPN, 1–4 ↔ M12 4–1 continuity, pin 1과 key 방향을 확인한다.
2. 추론 후보 `5055680571`의 실제 체결성, pad numbering과 footprint를 확인한다.
3. M12 female 후보 `MB12FBAFF08ST-3`의 suffix, mating view, PCB B면 배치 시 A-key/pin-1 방향, 제조사의 front-fastened 패널 체결과 기구 간섭을 확인한다. 권장 PCB 배열은 CAD에 반영했지만 1:1 출력과 실부품 삽입으로 재확인한다.
4. 새 SMA `A-SMA-KE-16.5A`의 제조사 land pattern과 board-edge 안착, 바깥쪽 방향, JLC wave-solder fixture/engineering 비고를 두 보드에서 확인한다.
5. 실제 M3 head/washer 외경과 장착 면을 기록하고, 상면 hardware가 RF trace 또는 solder mask를 누르거나 조임 공구가 SMA/transformer와 간섭하지 않는지 확인한다.
6. 커넥터/SMA 또는 stack-up을 바꾼 뒤 ERC, DRC, schematic–PCB parity와 1:1 실물 대조를 다시 수행한다.

현재 문서 매핑 초안은 KiCad 10에서 두 회로도 ERC 0, 두 PCB DRC 0, 미연결 pad 0, schematic–PCB parity 0을 통과했다. 이는 전기적 CAD 정합성 검사 결과이며 실물 핀 방향, 체결성 또는 RF 성능을 승인한 결과는 아니다.

## 재생성과 검사

역사적인 파일명은 유지했지만 [`generate_pinmap_tbd_drafts.py`](generate_pinmap_tbd_drafts.py)는 이제 문서 매핑 `DRAFT 1` 두 프로젝트와 로컬 후보 풋프린트를 재생성한다. 각 variant를 임시 sibling directory에서 완전히 생성한 뒤 회로도/PCB/project/rule 파일을 교체하므로 중간 계산 실패가 live 회로도만 먼저 바꾸지 않는다. KiCad 번들 Python으로 `--force` 실행하면 기존 검증 보고서를 무효화하므로, 뒤이어 ERC/DRC를 다시 실행해야 한다. `--variant molex` 또는 `--variant m12`로 한 endpoint만 선택할 수 있다. 수동으로 후속 설계를 시작해 draft 표식을 제거하면 생성기는 덮어쓰기를 거부한다.

KiCad 10 Windows의 Python zone filler는 생성기 안에서 사용하지 않는다. 대신 staged board에 native `kicad-cli pcb drc --refill-zones --save-board --schematic-parity`를 강제해 두 inner GND plane의 fill을 실제 PCB 파일에 저장하고, 위반이 있으면 live 파일 교체 전에 중단한다. 제작용 Gerber export에도 반드시 `--check-zones`를 사용하고 In1/In2 Gerber에 plane polygon이 존재하는지 확인한다. 이후 회로/보드를 수동 수정하면 새 ERC/DRC 보고서를 다시 생성해야 한다.

```powershell
& 'C:\Program Files\KiCad\10.0\bin\python.exe' `
  'balun_slipring\generate_pinmap_tbd_drafts.py' --force
```

위 항목이 끝나기 전에는 BOM의 개별 전기부품 상태와 무관하게 전체 설계는 **DO NOT FABRICATE**다. 핀맵의 근거와 실측 기록은 [`PINMAP.md`](PINMAP.md), 측정 절차는 [`MEASUREMENT.md`](MEASUREMENT.md), 보드별 조달 판단은 [`balun_slipring_draft_bom.csv`](balun_slipring_draft_bom.csv), 전체 구매 수량은 [`../JLCPCB_FINAL_BOM.csv`](../JLCPCB_FINAL_BOM.csv)와 [`../JLCPCB_ORDER_GUIDE.md`](../JLCPCB_ORDER_GUIDE.md)를 따른다.
