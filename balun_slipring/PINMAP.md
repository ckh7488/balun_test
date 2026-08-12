# Slip-ring pin map worksheet

상태: `TBD` — 아래 표를 실측하기 전에는 두 PCB의 `RAW` 신호와 `PAIR_*_TBD` 신호를 연결하지 않는다.

## 기준면과 기록 규칙

- 모든 핀 번호는 제조사 도면의 **mating face** 기준으로 기록한다.
- 사진을 찍을 때 connector key/latch가 보이게 하고, 사진 위에 pin 1을 표시한다.
- `Pair A/B`는 측정 지그 내부 채널 이름일 뿐이다. 실제 장비의 TX/RX 이름은 별도로 확인한다.
- pair의 P/N 반전은 IL 크기에는 큰 영향을 주지 않지만 위상과 실제 링크 동작에는 영향을 주므로 끝까지 기록한다.
- M12에서 사용하지 않는 네 핀을 임의로 GND 또는 종단에 연결하지 않는다.

## 정적 continuity

저항 측정 전 슬립링이 어떤 활성 장비나 PoE에도 연결되지 않았는지 확인한다.

| Molex `5055680471` 핀 | M12 `MB12MBAFF08ST-0` 핀 | 정지 저항 | 판정/비고 |
| --- | --- | ---: | --- |
| 1 | TBD | TBD Ω | |
| 2 | TBD | TBD Ω | |
| 3 | TBD | TBD Ω | |
| 4 | TBD | TBD Ω | |

M12 잔여 핀 확인:

| M12 핀 | Molex 1–4와 연결 | shell과 연결 | 판정/비고 |
| --- | --- | --- | --- |
| 1 | TBD | TBD | |
| 2 | TBD | TBD | |
| 3 | TBD | TBD | |
| 4 | TBD | TBD | |
| 5 | TBD | TBD | |
| 6 | TBD | TBD | |
| 7 | TBD | TBD | |
| 8 | TBD | TBD | |

## 회전 위치별 접촉 검사

각 위치에서 확정된 네 신호의 저항을 반복 측정한다. 가능하면 최소값/최대값뿐 아니라 회전 중 순간 단선도 기록한다.

| 회전 위치 | 신호 1 | 신호 2 | 신호 3 | 신호 4 | 순간 단선/변동 |
| ---: | ---: | ---: | ---: | ---: | --- |
| 0° | TBD | TBD | TBD | TBD | |
| 90° | TBD | TBD | TBD | TBD | |
| 180° | TBD | TBD | TBD | TBD | |
| 270° | TBD | TBD | TBD | TBD | |
| 회전 중 | TBD | TBD | TBD | TBD | |

## 실제 pair 확인

continuity만으로는 어떤 두 선이 물리적으로 꼬인 pair인지 알 수 없다. 기존 하네스 도면, 색상, 분해 관찰 또는 VNA crosstalk 결과로 아래를 확정한다.

| 지그 채널 | Molex 핀 | M12 핀 | 극성 | 근거 |
| --- | --- | --- | --- | --- |
| Pair A P | TBD | TBD | TBD | |
| Pair A N | TBD | TBD | TBD | |
| Pair B P | TBD | TBD | TBD | |
| Pair B N | TBD | TBD | TBD | |

4선의 가능한 pair 묶음은 `1–2 / 3–4`, `1–3 / 2–4`, `1–4 / 2–3` 세 종류다. 최종 측정 PCB에 4×4 점퍼 매트릭스를 넣어 탐색하지 않고, 저주파 breakout 또는 별도 짧은 시험 연결로 묶음을 확인한다.

## PCB 확정 시 반영할 내용

- 두 보드의 `RAW` 네트와 `PAIR_A/B_*_TBD` 네트를 네 개의 짧은 고정 배선으로 연결
- 한 pair의 P/N에 동일한 via 수, layer transition 수와 fan-out 구조 적용
- M12 female의 정확한 MPN·suffix·패널 체결 방향 및 footprint 반영
- M12 shell/drain이 실제로 존재할 때만 shield 연결 옵션 검토
- 연결 후 ERC 단독 라벨 경고 제거, PCB DRC 및 schematic parity 재실행
- 1:1 footprint 출력물에 실제 커넥터를 올려 key 방향과 pin 1 재검증
