# balun_slipring

회사 전용 슬립링의 100BASE-TX 전송 특성을 LibreVNA 2포트로 비교 측정하기 위한 지그 프로젝트다.

현재 `PINMAP TBD` 초안까지 진행했다. 두 보드의 공통 SMA/balun RF 코어는 배치·배선했지만, 커넥터 RAW 핀과 balun 차동 핀 사이는 의도적으로 연결하지 않았다. 핀맵과 M12 female의 정확한 부품 번호가 확정되기 전에는 제작하면 안 된다.

## 측정 전제

- 대상 신호: 100BASE-TX, 100 Ω 차동 2페어
- 구성: 슬립링 양 끝에 서로 다른 지그 보드 1장씩
- 각 보드: SMA 2개 + 임피던스비 1:2 balun 2개 (`50 Ω single-ended ↔ 100 Ω balanced`)
- 지그 손실을 비교하기 위한 동일 커넥터 조합의 REF/bypass 연결물도 별도로 준비
- 최종 핀맵이 확인되기 전에는 차동 팬아웃을 확정하지 않는다.

## 현재 KiCad 초안

두 프로젝트는 KiCad 10 기준의 독립 프로젝트다.

| 보드 | 현재 구현 | 의도적으로 남긴 작업 |
| --- | --- | --- |
| [`molex_end/balun_slipring_molex.kicad_pro`](molex_end/balun_slipring_molex.kicad_pro) | `5055680471`, SMA 2개, `ADT2-1T+` 2개, RCT 0 Ω 2개, 공통 50 Ω 배선 | `MOL_RAW1..4`와 두 차동 페어 사이 매핑/배선 |
| [`m12_end/balun_slipring_m12.kicad_pro`](m12_end/balun_slipring_m12.kicad_pro) | SMA 2개, `ADT2-1T+` 2개, RCT 0 Ω 2개, 공통 50 Ω 배선, M12 기구 예약 영역 | 정확한 female 풋프린트·위치, 사용 핀 4개와 두 차동 페어 사이 매핑/배선 |

핀 실측값은 [`PINMAP.md`](PINMAP.md)에 기록하고, 현재 조달 상태는 [`balun_slipring_draft_bom.csv`](balun_slipring_draft_bom.csv)를 확인한다. REF와 LibreVNA 설정·포트 연결·파일명은 [`MEASUREMENT.md`](MEASUREMENT.md)에 기록한다.

현재 공개 체크포인트에는 실제 핀맵이나 측정 데이터가 없다. 이후 회사 전용 정보 추가 전에는 [`LICENSE-NOTICE.md`](LICENSE-NOTICE.md)의 공개 범위를 확인한다.

공통 보드 초안은 68 × 44 mm이며, 동일한 RF 코어 위치와 배선을 사용한다. 보드 외곽과 M3 홀은 핀맵 확정 전의 검토용 값이다. M12측은 정확한 부품 도면을 받으면 왼쪽 기구부가 달라질 수 있다.

- 4층 JLCPCB `JLC04161H-7628`: 주문 두께 1.6 mm, KiCad stack model 합계 1.5862 mm
- L1 신호, L2/L3 연속 GND plane, L4는 현재 신호 없음
- L1/L4 blanket GND pour 없음
- SMA측 50 Ω: 외층 폭 0.35 mm
- 최종 차동측 100 Ω 목표: 폭 0.23 mm, gap 0.22 mm
- 측정하지 않는 채널은 SMA에 외부 50 Ω 종단
- 4×4 점퍼 매트릭스는 open stub와 채널별 비대칭을 만들므로 넣지 않음

`PINMAP TBD` 구역은 빈 공간으로만 예약했다. continuity 확인 후 네 개의 짧고 대칭적인 고정 배선으로 완성한다. 매트릭스나 긴 점퍼선을 최종 VNA 측정 경로에 남기지 않는다.

검사 상태:

- 두 PCB 모두 KiCad 10 DRC: 오류/경고 0개. 이는 현재 공통 RF 코어와 예약 형상에 대한 결과이며, 아직 없는 connector fan-out을 검증했다는 뜻은 아니다.
- 두 프로젝트 모두 회로도–PCB parity: 0개
- Molex 회로도 ERC: 오류 0개, 의도적으로 단독 보존한 RAW/PAIR 라벨 경고 8개
- M12 회로도 ERC: 오류 0개, 의도적으로 단독 보존한 RAW/PAIR 라벨 경고 12개
- fabrication/Gerber 파일은 생성하지 않음

제작 전 차단 항목:

- 현재 지정한 Amphenol `132289`의 제조사 PCB 두께 상한은 1.57 mm다. 현재 stack model 1.5862 mm가 이미 이를 0.0162 mm 초과하며, 1.6 mm 주문 공차까지 포함하면 기계적 체결을 보장할 수 없다. 최종판에서는 1.6 mm 대응 end-launch SMA로 MPN/footprint를 바꾸거나, 더 얇은 JLC stack-up과 그에 맞는 50/100 Ω geometry를 다시 확정해야 한다.
- M12 female의 정확한 suffix·풋프린트와 슬립링 핀맵이 모두 미확정이다.
- 위 항목이 해결되기 전에는 BOM의 `CONFIRMED`가 전기 부품 선정만 뜻하며, 전체 보드가 제작 승인됐다는 뜻이 아니다.

[`generate_pinmap_tbd_drafts.py`](generate_pinmap_tbd_drafts.py)는 이 초기 초안의 재현용이며 KiCad 번들 Python으로 실행한다.

```powershell
& 'C:\Program Files\KiCad\10.0\bin\python.exe' `
  'balun_slipring\generate_pinmap_tbd_drafts.py'
```

현재 PC의 KiCad 10 설치 경로와 형제 프로젝트 `balun_eth_rj45`를 원본으로 사용하므로 독립·이식형 생성기는 아니다. 기본 실행은 기존 파일을 덮어쓰지 않는다. `--force`도 회로도와 PCB에 `DRAFT 0` 및 `DO NOT FABRICATE` 표식이 모두 남아 있을 때만 허용되며, 재생성 후 오래된 DRC/ERC 보고서를 제거한다. 핀맵 확정 후 수동 설계를 시작하면 이 생성기를 폐기한다.

## 커넥터 요약

| 위치 | 부품 번호 | 현재 판단 |
| --- | --- | --- |
| Molex측 지그 보드 | `5055680471` | 사용자가 기존 지그 BOM에서 확인한 부품 |
| 슬립링의 Molex측 상대 커넥터 | 정확한 MPN 미확인 | 제조사 도면상 `505565` 또는 `214526` 계열 |
| 슬립링의 M12측 | `MB12MBAFF08ST-0` | 확인된 DUT 부품 |
| M12측 지그 보드 | 미확정 | M12 A-coded 8핀 female 필요 |
| 사용하지 않을 Molex 후보 | `5055700401` | 피치와 계열이 달라 현재 구성과 불일치 |

## Molex측: 5055680471

사용자가 기존 지그 BOM에서 확인해 제공한 정확한 부품 번호다. 이 저장소에는 그 사내 BOM 원본을 포함하지 않으며, 부품 번호를 성별에 대한 구두 표현보다 우선한다.

- 계열: Molex Micro-Lock Plus
- 피치: 1.25 mm
- 회로 수: 4핀, 1열
- PCB 장착: vertical SMD header
- 제조사 표기 접점 성별: male
- 상대물: `505565` 또는 TPA형 `214526` receptacle housing 계열

회사 내부에서 이 부품을 “암 커넥터”라고 불렀더라도 제조사 분류상으로는 male header다. 실제 조립품과 체결되는 것이 확인되어 있다면 그 물리적 체결 결과와 정확한 BOM 번호를 기준으로 한다.

`5055700401`은 Micro-Lock Plus 2.00 mm receptacle housing이다. `5055680471`의 1.25 mm 계열과 직접 체결되지 않으므로 이 지그의 상대 커넥터로 사용하지 않는다. 슬립링 쪽 정확한 하우징 MPN은 추후 라벨, BOM 또는 실물로 다시 확인한다.

자료:

- [Molex 5055680471 제품 페이지](https://www.molex.com/en-us/products/part-detail/5055680471)
- [Molex 5055680471 도면](https://www.molex.com/content/dam/molex/molex-dot-com/products/automated/en-us/2ddrawingdxfadobe2d/505/505568/5055680471.pdf?inline=)
- [5055680471 sales drawing 및 505565/214526 상대물 정보](https://www.molex.com/content/dam/molex/molex-dot-com/products/automated/en-us/salesdrawingpdf/505/505568/5055680471_sd.pdf)

## M12측: MB12MBAFF08ST-0

슬립링에 장착된 것으로 확인된 Finecables 부품이다.

- 규격: M12 A-coded
- 핀 수: 8핀
- 성별: male
- 형태: straight, panel-mount PCB type, front-fastened
- 제조사 자료상 shield 없음
- 일반 A-coded 커넥터이며, 제조사 자료에 100 Ω 차동 임피던스 보장은 없다.

따라서 M12 커넥터와 그 팬아웃도 측정 기준물에 포함되는 지그 오차로 취급한다. 지그 보드에는 맞물리는 M12 A-coded 8핀 female 커넥터가 필요하다.

직접 PCB 장착 후보는 Finecables `MB12FBAFF08ST-X` 계열이다. `MB12FBAFF08ST-3`가 후보로 확인됐지만, 정확한 체결 나사/패널 구조와 구매 가능 여부를 확인한 뒤 suffix와 풋프린트를 확정한다. 재고가 없으면 female field-wireable 커넥터와 매우 짧은 트위스티드 페어 피그테일을 대안으로 검토한다.

자료:

- [Finecables `MB12MBAFF08ST-0` male/unshielded 자료](https://www.finecables.com/uploadfiles/2022/06/260%20M12%20A_coding%20Straight%20Connector%2C%20Panel%20Mount%2C%20PCB%20Type%2C%20Front%20fastened.pdf)
- [Finecables `MB12FBAFF08ST-2/-3` female 후보 자료](https://www.finecables.com/uploadfiles/2022/06/259%20M12%20A_coding%20Straight%20Connector%2C%20Panel%20Mount%2C%20PCB%20Type%2C%20Front%20fastened.pdf)
- [JLCPCB 후보 MB12FBAFF08ST-3](https://jlcpcb.com/partdetail/FINECABLES-MB12FBAFF08ST3/C22378785)

## 확인해야 할 핀맵

핀 번호는 반드시 각 제조사 도면의 mating-face 기준으로 기록한다. 100BASE-TX의 두 페어를 임의로 `1-2`, `3-4`라고 가정하지 않는다.

| Molex 5055680471 핀 | M12 핀 | 페어 | 극성 | 확인 상태 |
| --- | --- | --- | --- | --- |
| 1 | TBD | TBD | TBD | 미확인 |
| 2 | TBD | TBD | TBD | 미확인 |
| 3 | TBD | TBD | TBD | 미확인 |
| 4 | TBD | TBD | TBD | 미확인 |

추가 확인 항목:

- Molex 4핀 중 실제 트위스트된 두 페어
- M12 8핀 중 사용하는 4개 핀과 미사용 핀
- 각 페어의 P/N 극성
- 슬립링 회전 위치 0°, 90°, 180°, 270°에서 연속성과 접촉 불량 여부
- M12 체결 토크가 PCB 납땜부에 전달되지 않도록 할 기계적 고정 방법

## 다음 설계 단계

아래 입력을 얻은 뒤 현재 두 초안을 최종화한다.

1. Molex 1–4번과 M12 1–8번의 continuity 표
2. 실제로 꼬인 두 페어의 묶음 및 P/N
3. 사용하지 않는 M12 4핀의 NC/내부 연결 상태
4. 지그측 M12 A-coded 8핀 female의 전체 MPN과 기구 도면
5. M12 shell/drain의 실제 연결 여부
6. 두 커넥터의 mating-face/key 방향 사진
7. M12 female의 STEP, 허용 panel thickness와 front/back fastening 방향

핀맵이 확정되면 RAW/PAIR 라벨 사이를 직접 연결하고, 두 차동선의 길이·비아·팬아웃을 대칭으로 맞춘 뒤 다시 ERC/DRC와 1:1 풋프린트 출력을 확인한다.

측정은 먼저 두 지그 사이의 REF/bypass를 측정하고, 같은 조건에서 이를 슬립링으로 교체해 차이를 비교하는 방식으로 시작한다.
