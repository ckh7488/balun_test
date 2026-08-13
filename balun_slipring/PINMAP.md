# Slip-ring pin map

상태: **문서 핀맵 확인 / continuity 실측 대기 / DO NOT FABRICATE**

아래 핀맵은 `Docs/[인수인계] PALA720.pptx` 슬라이드 14의 PALA720 2세대 `REV-504` 연결도를 전사해 KiCad `DRAFT 1`에 반영한 값이다. 실물 슬립링에서 측정한 continuity 결과가 아니므로 제작 승인 전에 별도 실측해야 한다.

## 문서 핀맵

`PAIR_TX = Ethernet TX`, `PAIR_RX = Ethernet RX`로 정의한다.

| 지그 네트 | 신호 | Molex `5055650501` 하우징 핀 | 슬립링 선색 | M12 `MB12MBAFF08ST-0` 핀 |
| --- | --- | ---: | --- | ---: |
| `PAIR_TX_P` | Ethernet TX+ | 1 | YEL | 4 |
| `PAIR_TX_N` | Ethernet TX− | 2 | ORN | 3 |
| `PAIR_RX_P` | Ethernet RX+ | 3 | BRN | 2 |
| `PAIR_RX_N` | Ethernet RX− | 4 | BLK | 1 |
| NC | 문서상 배정 없음 | 5 | — | — |

PCB측 상대물 `5055680571`은 `5055650501`의 계열·극수에 따른 **추론 후보**다. 해당 부품의 pin 1–5가 위 하우징 핀과 그대로 맞물린다는 전제는 실제 `REV-504` 체결과 제조사 mating drawing으로 검증해야 한다. 기존 KiCad 초안의 4극 `5055680471`은 제거했다.

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
- M12 J1은 signal pin을 transformer 쪽으로 향하게 한 후면 실장 후보임; 한쪽 극성만 layer/via를 바꾸던 crossover는 제거했으나 A-key/pin-1 mating view와 패널 방향은 실물 검증 전 DNP임
- KiCad 10 검사: 두 회로도 ERC 0, 두 PCB DRC 0, 미연결 pad 0, schematic–PCB parity 0
- `5055680571`과 `MB12FBAFF08ST-3`의 key 방향, pin view, 1:1 출력과 실제 기구 체결은 미검증

`RS422_Cable_Assembly_Spec.pptx`는 별도 EM2 encoder용 10핀 케이블 문서이므로 이 핀맵의 근거로 사용하지 않는다.
