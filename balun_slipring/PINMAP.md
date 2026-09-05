# Slip-ring pin map

상태: **문서 핀맵 확인 / continuity 실측 대기 / DO NOT FABRICATE**

> **LLC 케이블과 혼용 금지:** 아래는 슬립링 전용 핀맵이다. 추가 검토한 LLC-13M-1은 TX 8/2, RX 3/4, 전원 1/5/6/7로 다르다. 2026-09-03 사용자 확인에 따라 슬립링 지그는 **암**, LLC 지그는 **수** M12를 사용하며 LLC 암 cable-end는 실물 사진으로도 확인했다. 같은 M12 8핀이라는 이유로 이 보드를 재사용하지 않는다. [`../balun_llc16/README.md`](../balun_llc16/README.md)를 참조한다. 슬립링 M12 PCB의 표기는 `슬립링 / SLIPRING`이다.

아래 **핀 번호·선색·신호 매핑**은 `Docs/[인수인계] PALA720.pptx` 슬라이드 14의 PALA720 2세대 `REV-504` 연결도를 전사해 KiCad `DRAFT 1`에 반영한 값이다. 정확한 endpoint connector MPN까지 슬라이드 14에서 확인된 것은 아니며, 실물 슬립링에서 측정한 continuity 결과도 아니므로 제작 승인 전에 별도 실측해야 한다.

## 문서 핀맵

`PAIR_TX = Ethernet TX`, `PAIR_RX = Ethernet RX`로 정의한다.

| 지그 네트 | 신호 | Molex 5극 핀 (`5055650501` 후보) | 슬립링 선색 | M12 A-coded 8핀 (`MB12MBAFF08ST-0` 후보) |
| --- | --- | ---: | --- | ---: |
| `PAIR_TX_P` | Ethernet TX+ | 1 | YEL | 4 |
| `PAIR_TX_N` | Ethernet TX− | 2 | ORN | 3 |
| `PAIR_RX_P` | Ethernet RX+ | 3 | BRN | 2 |
| `PAIR_RX_N` | Ethernet RX− | 4 | BLK | 1 |
| NC | 문서상 배정 없음 | 5 | — | — |

`5055650501`은 슬라이드 15의 별도 4세대 케이블 표에서 확인되는 하우징을 2세대에도 적용해 본 교차 슬라이드 추론이다. PCB측 `5055680571`은 제조사가 공식적으로 `505565` series와 mate한다고 지정한 5극 header지만, 그 조합이 실제 `REV-504`라는 전제는 실물 체결과 BOM으로 검증해야 한다. `MB12MBAFF08ST-0`도 catalog에 존재하는 male 8P 후보일 뿐 실제 DUT MPN은 미확인이다. 기존 KiCad 초안의 4극 `5055680471`은 제거했다.

## M12 5–8번의 문서상 역할

| M12 핀 | 슬립링 선색 | PALA720 신호 | 이 VNA 지그 |
| ---: | --- | --- | --- |
| 5 | BLU | GPS RS232_RX | NC |
| 6 | VIO | GPS 1PPS | NC |
| 7 | GRY + WHT | 24VDC | NC |
| 8 | WHT-BLK + WHT-BRN | 24VDC GND | NC |

이 네 핀을 GND, shield, 50 Ω 종단 또는 서로에게 연결하지 않는다. 측정 전 DUT의 24VDC와 다른 활성 장비를 모두 분리한다.

## 실물 continuity 확인표

핀 번호는 각 제조사 도면의 mating-face 기준으로 기록하고, 사진에는 key와 pin 1을 표시한다. 문서 예상값과 다르면 측정을 중지하고 실물/BOM/도면을 우선해 원인을 확인한다.

| 신호 | Molex 예상 핀 | M12 예상 핀 | 정지 저항 | 실측 판정 |
| --- | ---: | ---: | ---: | --- |
| TX+ | 1 | 4 | TBD Ω | 미측정 |
| TX− | 2 | 3 | TBD Ω | 미측정 |
| RX+ | 3 | 2 | TBD Ω | 미측정 |
| RX− | 4 | 1 | TBD Ω | 미측정 |

| M12 핀 | 문서상 신호 | Ethernet 1–4와 연결 | shell과 연결 | 실측 판정 |
| ---: | --- | --- | --- | --- |
| 5 | GPS RS232_RX | TBD | TBD | 미측정 |
| 6 | GPS 1PPS | TBD | TBD | 미측정 |
| 7 | 24VDC | TBD | TBD | 미측정 |
| 8 | 24VDC GND | TBD | TBD | 미측정 |

## 회전 위치별 접촉 검사

| 회전 위치 | TX+ | TX− | RX+ | RX− | 순간 단선/변동 |
| ---: | ---: | ---: | ---: | ---: | --- |
| 0° | TBD | TBD | TBD | TBD | |
| 90° | TBD | TBD | TBD | TBD | |
| 180° | TBD | TBD | TBD | TBD | |
| 270° | TBD | TBD | TBD | TBD | |
| 저속 회전 중 | TBD | TBD | TBD | TBD | |

출하검사성적서의 두 기록값인 접촉회로 저항 241/248 mΩ 및 순간단선 양호는 해당 출하 LOT의 검사 결과일 뿐, 현재 보유한 개별 DUT와 각 핀의 실측값을 대신하지 않는다.

## PCB 반영 상태와 남은 검증

- Molex측: pin 1/2를 `PAIR_TX_P/N`, pin 3/4를 `PAIR_RX_P/N`에 연결하고 pin 5는 NC로 반영함
- M12측: pin 4/3을 `PAIR_TX_P/N`, pin 2/1을 `PAIR_RX_P/N`에 연결하고 pin 5–8은 NC로 반영함
- 두 보드 모두 shared-centerline W=0.23/G=0.22 mm 배선이며 네 쌍 모두 P/N이 F.Cu-only, signal via 0/0, 저장된 track skew 0.001 mm 미만임
- M12 J1은 제조사의 female 8P 권장 PCB 배열로 수정됐고 signal pin을 transformer 쪽으로 향하게 한 PCB B면 후보임; 한쪽 극성만 layer/via를 바꾸던 crossover는 제거했으나 A-key/pin-1 mating view, front-fastened 패널 방향과 실물 체결은 DNP 차단 항목임
- KiCad 10 검사: 두 회로도 ERC 0, 두 PCB DRC 0, 미연결 pad 0, schematic–PCB parity 0
- `5055680571`의 key/pin view와 `MB12FBAFF08ST-3`의 corrected 8P geometry는 도면에 대조했지만, 두 부품 모두 1:1 출력과 실제 기구 체결은 미검증

`RS422_Cable_Assembly_Spec.pptx`는 별도 EM2 encoder용 10핀 케이블 문서이므로 이 핀맵의 근거로 사용하지 않는다.
