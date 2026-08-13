# balun_slipring

PALA720 2세대 슬립링의 100BASE-TX 전송 특성을 LibreVNA 2포트로 비교 측정하기 위한 지그 프로젝트다.

`Docs/[인수인계] PALA720.pptx` 슬라이드 14에서 2세대 Ethernet 논리 핀맵을 확인하고, KiCad `DRAFT 1` 회로도와 두 PCB의 connector fan-out에 반영했다. 다만 이 표는 인수인계 문서의 전사값이며 실물 `REV-504`의 continuity 측정값은 아니다. 커넥터 기구와 SMA/stack-up도 아직 차단 항목이므로 **DO NOT FABRICATE** 상태다.

## 문서에서 확인한 2세대 핀맵

슬라이드 14의 Ethernet용 5극 케이블 하우징은 Molex `5055650501`로 식별된다. PCB측 상대물 `5055680571`은 같은 Micro-Lock Plus 1.25 mm 계열과 5극 구성을 근거로 한 **추론 후보**일 뿐 문서에 직접 적힌 MPN이 아니다. 실제 `REV-504`의 라벨·BOM·체결 상태와 제조사 도면으로 확인해야 한다.

| 신호 | `5055650501` 하우징 핀 | 슬립링 선색 | M12 핀 |
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
| REV-504 Ethernet 케이블 하우징 | Molex `5055650501` | 슬라이드 14에서 확인한 5극 하우징 |
| Molex측 지그 PCB | Molex `5055680571` | 위 하우징의 PCB 상대물로 추론한 후보; 실물 체결·키 방향·pin 1 확인 전 DNP |
| 슬립링 M12측 | Finecables `MB12MBAFF08ST-0` | 확인된 8핀 A-coded male DUT 부품 |
| M12측 지그 PCB | Finecables `MB12FBAFF08ST-3` | 8핀 A-coded female 후보; suffix, 패널 구조, pin view와 구매 가능성 확인 전 DNP |

기존 4극 `5055680471`은 문서 연결과 맞지 않아 KiCad에서 제거했다. 현재는 `5055680571`과 `MB12FBAFF08ST-3`의 제조사 도면 기반 로컬 후보 풋프린트를 배치·배선했지만, 둘 다 실물 체결과 1:1 출력 검증 전 DNP다.

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

M12 J1은 pin 1–4가 transformer 쪽을 향하도록 **후면 실장 electrical-layout 후보**로 배치했다. 덕분에 이전의 한쪽 극성만 B.Cu/via를 쓰던 비대칭 crossover가 없어졌다. M12의 P/N은 모두 동일한 connector PTH barrel을 지나 F.Cu로 나오며, 별도 routing via는 0/0이다. 다만 실제 A-key/pin-1 mating view, 패널 너트 접근과 케이블 방향이 반대로 바뀔 수 있으므로 이 기구 결정을 실물로 확인하기 전에는 J1을 계속 DNP로 둔다.

| 보드 / pair | P 길이 | N 길이 | P–N 차이 | 0.22 mm 결합 트렁크 최소 | Signal via P/N |
| --- | ---: | ---: | ---: | ---: | ---: |
| Molex TX | 31.082091 mm | 31.082091 mm | <0.000001 mm | 20.292153 mm | 0 / 0 |
| Molex RX | 31.910806 mm | 31.910806 mm | <0.000001 mm | 21.120867 mm | 0 / 0 |
| M12 TX | 27.622513 mm | 27.622513 mm | <0.000001 mm | 16.726222 mm | 0 / 0 |
| M12 RX | 26.916536 mm | 26.916536 mm | <0.000001 mm | 16.061861 mm | 0 / 0 |

생성기는 source geometry에서 skew ≤0.01 mm, 결합 트렁크 ≥16 mm와 fan-in/out ≤11 mm를 검사하고, 저장된 KiCad track에서 다시 skew ≤0.01 mm, F.Cu-only와 P/N via 0/0을 검사한다. KiCad가 꺾임에서 산출한 최대 uncoupled는 11.1474 mm이며, DRU는 gap 0.21/0.22/0.23 mm min/opt/max, uncoupled ≤11.20 mm, skew ≤0.10 mm, signal via 0개로 제한한다. 이는 기준 보드의 uncoupled 16/16.5 mm보다 더 엄격하다.

두 KiCad 초안은 68 × 44 mm, 4층 JLCPCB `JLC04161H-7628` 기준이며 core εr은 기준 보드와 같은 4.36으로 통일했다. W=0.23/G=0.22 mm는 이 stack, 외층 1 oz, green soldermask, non-coplanar 조건의 nominal 100 Ω 발주 geometry다. 저장소에는 JLC field-solver 결과 원본이 없으므로 실제 주문 전 JLC impedance calculator와 impedance-control/coupon으로 다시 승인해야 한다. 현재 stack model은 1.5862 mm이고 SMA는 Amphenol `132289`로 지정되어 있으나, 이 SMA의 제조사 PCB 두께 상한 1.57 mm를 초과한다. 1.6 mm 대응 SMA로 바꾸거나 stack-up과 50/100 Ω geometry를 다시 확정해야 한다.

## 제작 전 차단 항목

1. `REV-504` 실물에서 Molex housing MPN, 1–4 ↔ M12 4–1 continuity, pin 1과 key 방향을 확인한다.
2. 추론 후보 `5055680571`의 실제 체결성, pad numbering과 footprint를 확인한다.
3. M12 female 후보 `MB12FBAFF08ST-3`의 suffix, mating view, 후면 실장 시 A-key/pin-1 방향, 패널 체결과 기구 간섭을 확인한다.
4. SMA/PCB 두께 불일치를 해소하고 stack-up에 맞춰 임피던스를 재계산한다.
5. 커넥터/SMA 또는 stack-up을 바꾼 뒤 ERC, DRC, schematic–PCB parity와 1:1 실물 대조를 다시 수행한다.

현재 문서 매핑 초안은 KiCad 10에서 두 회로도 ERC 0, 두 PCB DRC 0, 미연결 pad 0, schematic–PCB parity 0을 통과했다. 이는 전기적 CAD 정합성 검사 결과이며 실물 핀 방향, 체결성 또는 RF 성능을 승인한 결과는 아니다.

## 재생성과 검사

역사적인 파일명은 유지했지만 [`generate_pinmap_tbd_drafts.py`](generate_pinmap_tbd_drafts.py)는 이제 문서 매핑 `DRAFT 1` 두 프로젝트와 로컬 후보 풋프린트를 재생성한다. KiCad 번들 Python으로 `--force` 실행하면 기존 검증 보고서를 무효화하므로, 뒤이어 ERC/DRC를 다시 실행해야 한다. 수동으로 후속 설계를 시작해 draft 표식을 제거하면 생성기는 덮어쓰기를 거부한다.

KiCad 10 Windows의 Python zone filler가 생성기 안에서 불안정해 inner GND zone은 미충전 상태로 저장된다. PCB Editor에서 처음 열었을 때 보이는 GND ratsnest는 `B`로 zone을 채워 확인한다. 저장된 DRC 보고서는 native `kicad-cli pcb drc --refill-zones`로 별도 검사한 결과다.

```powershell
& 'C:\Program Files\KiCad\10.0\bin\python.exe' `
  'balun_slipring\generate_pinmap_tbd_drafts.py' --force
```

위 항목이 끝나기 전에는 BOM의 개별 전기부품 상태와 무관하게 전체 설계는 **DO NOT FABRICATE**다. 핀맵의 근거와 실측 기록은 [`PINMAP.md`](PINMAP.md), 측정 절차는 [`MEASUREMENT.md`](MEASUREMENT.md), 조달 판단은 [`balun_slipring_draft_bom.csv`](balun_slipring_draft_bom.csv)를 따른다.
