# LLC 케이블 VNA 지그 — 구동기 to RJ45

> **2026-09-05 이력 안내:** 아래는 LLC 커넥터 전용 balun 보드의 이전 설계·구매 기록이다. 현재 기본안은 [공통 RJ45 balun + 수동 어댑터](../adapters/README.md)이며, [설계 검토 인계](../DESIGN_REVIEW_HANDOFF.md)를 먼저 읽는다. 아래의 “최신 구매” 표기는 당시 기준이고 현 구성의 발주 지시가 아니다. 기존 B면 M12 보드와 새 F면 수동 어댑터는 별개 CAD다. 과거 커넥터 삽입 확인을 새 보드의 패널/체결 검증 완료로 확대 해석하지 않는다.

> **2026-09-03 최신 구매 상태:** PCB는 JLCPCB에서 미조립 제작, 부품은 DigiKey 한국 중심(국내 인두팁만 예외)으로 구매한다. 실사용 Molex 2 + RJ45 4 + LLC 2 = 8장, 제작 예산 3종×5장=15장. 슬립링 M12 암 보드/암커넥터는 기존 케이블→RJ45 개조로 제외하며 LLC M12 수커넥터는 사내품 사용이다. **사내 수커넥터의 PCB 삽입은 사용자 확인 완료**이고 전기적 핀맵/수량 확인은 별도다. Samtec SMA는 구매 후보이며 현 CAD/MyAntenna와 최종 두께·공차/제조파일 정합 승인 전이다. 아래 이전 PCBA/구매 수량·품번은 발주에 사용하지 말고 [최신 구매요청서](../PURCHASE_REQUEST_FORM_DRAFT_2026-09-03.md)를 따른다. 이번에 PCB/회로/풋프린트는 변경하지 않았다.

상태: **PCB DRAFT A (CAD Rev A-PCB) 배치·배선 및 ERC/DRC/parity 검증 완료 / JLC 조달·조립 및 기구 승인 대기 / DO NOT ORDER**

새 PCB는 [balun_llc16.kicad_pcb](balun_llc16.kicad_pcb)다. [앞·뒷면 및 내부 GND 면 검토 PDF](../../output/pdf/balun_llc16_pcb_review.pdf)와 [대응 회로도 PDF](../../output/pdf/balun_llc16_schematic.pdf)를 함께 제공한다. 기존 RJ45·슬립링 PCB는 이번 작업에서 수정하지 않았다.

검토 원본은 `../Docs/16. LLC16_13M_1. 케이블 조립체 전원 및 통신용.pdf` 1페이지다. 파일명은 LLC16_13M_1이지만 도면 제목란과 케이블 마킹은 **LLC-13M-1**, 작성일은 **2022-04-25**다. 사용자가 제시한 LLC 케이블의 설계자료로서 이 도면을 기준으로 회로와 PCB를 설계한다. 원본 PDF는 변경하지 않았다.

**설계 기준:** 도면의 핀 번호와 배선선을 기준으로 PCB까지 작성했다. 실물 continuity 측정은 설계 착수 조건이 아니라 최초 VNA 연결 전 확인 항목이다. 수커넥터는 제조사 자료를 기준으로 선정했으며, 추가 내부 배선 자료를 기다리지 않는다. 실제 조달·조립 가능 여부와 케이블 체결·패널 지지는 제조 승인 전에 확인한다.

## PCB 구성과 검증 결과

| 항목 | PCB DRAFT A |
| --- | --- |
| 외형 / 적층 | 68 x 44 mm, 4층, JLC04161H-7628, 주문 1.6 mm / CAD 1.5862 mm |
| J1 | Finecables `MB12MBAFF08ST-3`, M12 A-coded 8핀 수, PG9, B면 장착, 필수 FIT |
| 신호층 / 기준면 | 모든 RF·차동 신호 F.Cu, In1/In2 GND 면, 신호 비아 0개 |
| 목표 임피던스 | SMA 50 Ω: W0.35 mm / 차동 100 Ω: W0.23, gap0.22 mm |
| TX P/N 길이 | 약 30.487329 / 30.487329 mm |
| RX P/N 길이 | 약 25.454235 / 25.454237 mm |
| P/N 길이 차이 | 두 pair 모두 0.001 mm 미만, CAD 계산값이며 제조 공차가 아님 |
| 50 Ω A/B 경로 | 각각 26.762102 mm, 기존 RF launch와 같은 형상 |
| fan-in/out | TX 최대 9.393 mm / RX 최대 10.627 mm, native 11.2 mm 제한 유지 |
| 기본 실장 | J1/J2/J3/T1/T2 FIT, RCT1/RCT2 DNP |
| 전원 핀 | J1.1/5/6/7 모두 단독 NC, 신호/GND/plane/track 연결 없음 |
| 검사 | ERC 오류·경고 0, DRC 위반 0, 미연결 0, 회로도-PCB 불일치 0 |

내층 GND는 native refill 후 저장되어 있으며 각 층의 단일 연결 polygon을 확인했다. 두 pair의 전체 길이는 서로 다르므로 TX와 RX가 같은 지연을 갖는다는 뜻은 아니다. 임피던스는 기존 [지정 적층 검증](../JLCPCB_IMPEDANCE_VERIFICATION_2026-08-31.md)의 geometry를 적용한 **설계 목표**이며, 새 M12 전이부의 3D EM 해석·실측 보증이나 정식 Ethernet 적합성 인증을 수행한 것은 아니다. 짧은 비결합 fan-out과 커넥터 응답은 REF/DUT 지그 비교에 포함된다.

### 수커넥터 풋프린트와 장착

[Finecables 제품 도면 p259](https://www.finecables.com/uploadfiles/2022/06/259%20M12%20A_coding%20Straight%20Connector%2C%20Panel%20Mount%2C%20PCB%20Type%2C%20Front%20fastened.pdf) 및 [2025 제조사 카탈로그](https://www.finecables.com/uploadfiles/2025/09/2025_Finecables_Industrial_Connector_Catalogue.pdf)의 p293/p415를 직접 확인했다. p415의 **Male recommended PCB layout**으로 별도 `llc16.pretty/Finecables_MB12MBAFF08ST-3.kicad_mod`를 만들었다.

- pin 8 중앙, 외곽 pin 1~7의 PCD 5.5 mm, key 기준 ±33° 및 나머지 49° 간격.
- 제조사 권장 finished hole Ø1.0 mm, pad Ø1.8 mm. 암 풋프린트 이름만 변경한 것이 아니라 수커넥터 PCB-view의 번호를 확인한 좌표다.
- J1은 보드 뒷면에서 아래로 돌출한다. 중심은 (32,42) mm, 회전 0°이며 key는 위에서 투영하면 보드 위쪽을 향한다. 반대쪽 면에서 보면 좌우가 바뀌므로 조립 도면의 면을 확인한다.
- 본체/너트 공간은 보수적으로 Ø20 mm envelope와 Ø21 mm courtyard로 예약했다. 커넥터는 **PG9 패널 고정형**이므로 납땜 핀만으로 케이블 체결 하중을 받게 하지 않는다. 패널 cut-out, 보드-패널 거리, standoff와 케이블 굽힘 공간은 아직 기구 승인 대상이다.
- 이 부품에는 earth/shield pin이 없다. shell을 VNA GND에 임의 연결하지 않고 실제 fixture의 shield 조건을 측정 기록에 남긴다.
- 정확한 JLC/LCSC 번호, 재고와 Standard PCBA 공정 승인은 미확인이다. 부품이 없으면 업체 사급/조달을 확인하거나 새 후보를 별도 검증한다. 자동 대체·사용자 손납땜을 가정하지 않는다.
- M12 상세 3D STEP 모델은 아직 연결하지 않았다. KiCad 3D 화면에서 본체가 생략되더라도 J1은 필수 실장 대상이다.

## 수량과 공유 방식

- 기존 슬립링 2세트: Molex 2장 + 슬립링 M12 2장 = 4장.
- 기존 RJ45 2세트: RJ45 보드 4장.
- LLC 측정용: **LLC 전용 M12 보드 2장 추가**, 기존 RJ45 보드 중 2장을 번갈아 공유.
- 요청 조립품 합계는 **10장**이다. 세 종류 DUT용 지그를 모두 독립된 두 세트씩 상시 구성하려면 RJ45 보드도 2장 더 있어야 하므로 그때는 12장이다.
- 전부 JLC PCBA를 목표로 하며, 커넥터·RF 부품의 사용자 손납땜을 전제로 하지 않는다. 아직 10장 확정 견적이나 제조 승인은 없다.

## 원본 배선선과 핀 번호로 확인한 매핑

| 신호 | LLC M12 P1 | RJ45 P2 | 기존 RJ45 지그 포트 | LLC 지그 네트 |
| --- | ---: | ---: | --- | --- |
| TX+ | 8 | 1 | J2 / A, + | PAIR_TX_P |
| TX- | 2 | 2 | J2 / A, - | PAIR_TX_N |
| RX+ | 3 | 3 | J3 / B, + | PAIR_RX_P |
| RX- | 4 | 6 | J3 / B, - | PAIR_RX_N |
| P24 / P242 | 1 | RJ45로 연결되지 않음, 전원 꼬리선 | 연결 금지 | NC |
| P24 / P242-1 | 7 | RJ45로 연결되지 않음, 전원 꼬리선 | 연결 금지 | NC |
| N24 / N242 | 5 | RJ45로 연결되지 않음, 전원 꼬리선 | 연결 금지 | NC |
| N24 / N242-1 | 6 | RJ45로 연결되지 않음, 전원 꼬리선 | 연결 금지 | NC |

도면은 RJ45 핀 이름 표에서 4번을 BD-, 6번을 CD-로 기입하지만, 실제 RX- 배선선은 **RJ45 6번**에 닿는다. 초안은 핀 이름 표가 아니라 연속된 배선선과 숫자 1/2/3/6을 기준으로 한다. 실측에서 RX-가 4번으로 나오면 기존 RJ45 A/B 지그를 그대로 사용할 수 없으므로 중지하고 케이블 도면/결선을 다시 확인한다. 핀 번호를 임의로 보정하거나 케이블을 개조하지 않는다.

## 기존 슬립링 M12 보드를 그대로 쓰면 안 되는 이유

| 용도 | TX+ / TX- | RX+ / RX- | 지그에서 NC로 둘 핀 |
| --- | --- | --- | --- |
| 기존 슬립링 | M12 4 / 3 | M12 2 / 1 | 5, 6, 7, 8 |
| LLC-13M-1 도면 | M12 8 / 2 | M12 3 / 4 | 1, 5, 6, 7 |

특히 M12 **1번은 기존 슬립링의 RX-지만 LLC에서는 P24**, 8번은 기존 슬립링에서 NC인 전원 귀로지만 LLC에서는 TX+다. 같은 모양이라는 이유로 실크만 바꿔 재사용하지 않는다. 모든 측정은 전원을 분리한 수동 케이블에만 수행한다.

도면 BOM은 P1을 **NorComp / T4112012081-000**으로 적지만, 이 정확한 부품번호의 [TE Connectivity 공식 페이지](https://www.te.com/en/product-T4112012081-000.html)는 **M12 A-code, 8핀, female/socket, right-angle**로 설명한다.

**2026-09-03 확인:** 사용자가 제공한 LLC 실물 정면 사진에서 socket 접점인 암커넥터를 확인했고, 사용자도 LLC 지그에는 수커넥터, 슬립링 지그에는 암커넥터가 필요함을 확인했다. 앞서 남겼던 암수 방향의 불확실성은 해소되었다.

| 용도 | DUT 측 | PCB 지그 측 | 확인 근거 |
| --- | --- | --- | --- |
| LLC / 구동기 to RJ45 | 암 / socket | **수 / pin** | 이번 실물 사진 + 사용자 확인 |
| 슬립링 | 수 / pin | **암 / socket** | 사용자 확인 + 기존 설계 조건 |

사진 원본은 `C:/Users/artzy/Documents/DaouMessenger 4.0/4ebb4012-2e32-4099-8901-afd8052dfe48.jpg`이며 변경하지 않았다. 사진만으로 정확한 MPN, 치수, 핀 번호별 내부 배선까지 확인된 것은 아니다. 제조사/부품번호 표기의 불일치와 실제 continuity 검증은 별도로 남는다. 기존 슬립링 PCB의 Finecables `MB12FBAFF08ST-3`는 암 후보이므로 LLC에는 위의 수커넥터를 별도 선정했으며, 단순 반전 배치로 같은 footprint를 재사용하지 않았다.

## CAD 및 표기 상태

- `balun_llc16.kicad_sch`, revision **A-PCB**: 기존 SMA/발룬 TX·RX 연결을 유지하고 선정한 J1 MPN/footprint를 반영했다. M12 논리 핀맵, 케이블 연결표 및 주의사항은 A4 1페이지에 유지했다. 전원 핀 J1.1/5/6/7은 모두 명시적 NC다. RCT1/RCT2는 모두 DNP다.
- J1은 **필수 실장할 수커넥터**다(`dnp no`). MPN/footprint는 위와 같이 선정했으며 LCSC 번호와 JLC 조립 승인은 미확인이다. 제조 보류는 Assembly 속성과 도면 상태로 표시하며 커넥터를 빼고 납품한다는 뜻이 아니다.
- `CT_A`, `CT_B`는 각 발룬 5번과 DNP 저항만 연결한다. 기본 조립에서 중심탭은 GND와 연결되지 않는다. 발룬 2번은 라이브러리 정의상 NC이며 배선하지 않는다.
- 확인용 PDF는 저장소 루트의 `output/pdf/balun_llc16_schematic.pdf`다. KiCad에서 직접 출력한 회로도이며 원본 schematic과 전기 연결이 동일하다.
- `.kicad_pcb`, `.kicad_dru` 및 대응 프로젝트 설정을 만들었다. 제조 Gerber/BOM/CPL은 **아직 내보내지 않았다**. ERC/DRC 통과만으로 제조 승인하지 않는다.
- 기존 슬립링 M12 보드의 실제 F.Silkscreen 제목은 **`슬립링 / SLIPRING`**으로 구분했다. 전기 연결은 변경하지 않았다.
- LLC PCB F.SilkS에 **`구동기 to RJ45`**, `LLC-13M-1 / M12 MALE`, `TX 8/2 RX 3/4`와 전원 NC 경고를 넣었다. 실제 한글 font가 native PDF에 출력되는지도 확인했다.
- 성별이 다르더라도 실제 부품/어댑터로 오접속될 수 있으므로, 두 지그는 각각 `SR-01/02`와 `LLC-01/02`로 식별한다.

회로도 재생성은 KiCad 10 번들 Python으로 `generate_schematic.py --output-directory <비어 있는 검토 폴더>`를 실행한다. 기존 파일은 기본적으로 덮어쓰지 않으며, 검토한 자동 생성 파일에 한해 `--replace-generated-sha256 <기존 파일의 SHA-256>`를 지정할 수 있다. 저장 직전에도 hash를 재검사해 동시 수정 내용을 덮어쓰지 않는다. `layout_schematic.py`는 LLC 도면 배치만 담당하며 공유 슬립링 생성기나 기존 슬립링/RJ45 회로·PCB는 이번 회로도 정리에서 수정하지 않았다.

### PCB 재생성과 검증 기록

KiCad 10 번들 Python으로 먼저 `generate_schematic.py --output-directory <검토 폴더>`, 이어서 `generate_pcb.py --output-directory <동일 검토 폴더>`를 실행한다. PCB 명령은 그 폴더의 회로도에서 native XML을 내보낸 뒤 LLC 배치·배선을 만들고 zone refill/save, ERC, DRC와 schematic parity를 검사한다. live 프로젝트 폴더로 직접 생성하지 못하게 했으며, 기존 PCB 덮어쓰기는 일치하는 `--replace-generated-sha256`이 있어야 한다. 검토 폴더의 기존 자동 생성 보조 파일은 갱신될 수 있으므로 수작업 파일이 없는 전용 폴더를 사용한다.

`verify_pcb.py <검토 폴더 또는 live 프로젝트 폴더>`는 저장된 PCB의 전체 pad/net 일치, male 핀 좌표·홀, 전원 핀 절연, FIT/DNP, GND fill, 신호 경로 및 길이를 추가 검사한다. 같은 폴더의 최신 native `balun_llc16.xml`과 `drc.json`이 필요하다. [verification.json](verification.json), [drc.json](drc.json), [erc.rpt](erc.rpt), [routing_metrics.json](routing_metrics.json)에 이번 결과를 보존했다.

수정 전 LLC 회로도·설정·생성기는 `../../outputs/balun-llc16-pcb-20260903/before/`, 검토용 CAD는 같은 경로의 `stage/`에 보존했다. 기존 세 PCB는 이번 작업에서 수정하지 않았다.

최종 live CAD에서 native XML/ ERC/DRC를 다시 출력하고 `verify_pcb.py`를 통과했다. 검사 전후 PCB·회로도 hash와 검토용 CAD 일치를 확인했다. PCB 생성기의 무승인/틀린 hash 덮어쓰기와 live 폴더 직접 생성도 모두 거부되는 것을 확인했으며 이 검사로 검토 파일은 바뀌지 않았다. `../verify_schematic_refresh.py` 회귀 검사에서 기존 3종의 새 회로도-PCB 일치, ERC/DRC, 기존 PCB·규칙 파일 무변경 및 LLC 회로도 재생성 일치도 통과했다.

### 회로도 검증 이력

KiCad 10의 native ERC는 **오류 0 / 경고 0**이다. `verify_schematic.py <KiCad XML netlist>` 검산은 전체 7개 부품/15개 net, M12 8개 핀의 실제 net membership, 양쪽 발룬/SMA 경로, primary GND, CT 경로, 전원 핀·발룬 2번의 단독 NC, 필수 부품 FIT 및 RCT DNP, 10장 구성과 LLC load 4개를 확인한다. 이는 문서 전사와 회로 연결 검사이지 실제 케이블의 RF 성능이나 부품 체결을 검증한 결과가 아니다.

추가 회귀 검사에서 동일 회로도의 재생성 일치, 무승인/틀린 hash 덮어쓰기 거부를 확인했다. 핀 2/4 교환, 전원 핀의 신호 net 연결, RCT 오실장, 필수 J1의 DNP 처리라는 4개 변조 netlist도 모두 검산에서 거부되었다. PDF는 최종 출력을 렌더링해 한글, 주석, 부품명 방향 및 페이지 잘림을 확인했다. 이전 회로도는 `../../outputs/balun-llc16-review-20260903/before-schematic-a/balun_llc16.kicad_sch`에 보존했다.

표기만 변경한 기존 슬립링 M12 PCB는 zone refill과 schematic parity를 포함한 native DRC에서 위반 0 / 미연결 0이었다. 원본 커넥터 후보·기구·임피던스 release HOLD는 그대로 유지한다.

## 남은 작업의 구분

### 설계·제조 준비

1. 선정한 `MB12MBAFF08ST-3`의 업체 공급·조립, 실제 mating, 패널 cut-out/지지·장착 높이와 접근 공간을 승인한다.
2. 작성된 4층 PCB를 제조 시점의 stack-up/임피던스, SMA 두께 fit 및 CAM 자료와 대조한다. 이후 PCB를 수정하면 ERC/DRC/parity와 NC 검사를 다시 수행한다.
3. 부품 조달·JLC 조립·생산파일과 최종 견적을 검토한 후 제조 승인한다. 도면의 브랜드/핀 이름 불일치는 위에 기록한 해석을 유지하며 미해결 실측 대기라는 이유로 설계 자체를 중단하지 않는다.

### 최초 VNA 연결 전 실물 검사

1. 암수 확인용 정면 사진은 이미 수령했다. 실제 케이블의 마킹/개정과 key/pin 1을 가능한 범위에서 기록한다.
2. 전원과 활성 장비를 모두 분리하고, M12 8→RJ45 1, 2→2, 3→3, 4→6 및 전원선 1/5/6/7의 분리를 검사한다. 특히 도면의 RX- 배선은 숫자 6번을 사용한다.
3. shell/shield 관계를 확인해 REF와 DUT의 차폐 조건을 고정한다. 실물이 도면과 다르면 연결을 중단하고 원인을 확인한다.

측정 연결표와 종단 수량은 [`MEASUREMENT.md`](MEASUREMENT.md), 전체 구매 범위는 [`../PCBA_PURCHASE_SCOPE_2026-09-03.md`](../PCBA_PURCHASE_SCOPE_2026-09-03.md)를 따른다.
