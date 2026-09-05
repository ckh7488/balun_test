# LLC-13M-1 비교 측정 초안

상태: **핀맵 문서 기반 계획 / 커넥터 및 PCB 검증 전 / 측정 실행 승인 아님**

LLC 케이블 측 암 / PCB 지그 측 수 방향은 2026-09-03 실물 사진과 사용자 확인으로 확정했다. 이는 아래 continuity와 전원 분리 검사를 대체하지 않는다.

아래 실물 검사는 **최초 VNA 연결 전** 절차이며 PCB 설계 시작의 선행 조건은 아니다. 설계는 제공된 PDF의 숫자 핀 번호와 배선선을 기준으로 진행한다.

## 안전과 입고 확인

- 구동기, 제어반, Ethernet 활성 장비, PoE 및 전원 꼬리선을 모두 분리한다. 전원 꼬리선은 한 가닥씩 절연해 서로 또는 금속물에 닿지 않게 고정한다.
- M12 1/7은 P24, 5/6은 N24다. 네 핀 모두 VNA 지그에서는 NC로 남긴다. N24를 VNA GND나 shell에 임의 접속하지 않는다.
- VNA 연결 전 전원과 잔류 전압이 없음을 확인한 뒤 아래 continuity/절연 관계를 검증한다. 발룬의 DC 절연을 전원 오접속 보호회로로 간주하지 않는다.
- 원본 도면의 500 VDC 절연 시험은 케이블 단독 검사 항목이며 VNA 측정이 아니다. VNA와 발룬 지그를 연결한 상태에서 절연저항계/내전압 시험을 하지 않는다.

| 검사 | 도면 예상 | 실측 기록 |
| --- | --- | --- |
| M12 8 | RJ45 1에 연결 | TBD |
| M12 2 | RJ45 2에 연결 | TBD |
| M12 3 | RJ45 3에 연결 | TBD |
| M12 4 | RJ45 6에 연결 | TBD |
| M12 1 / 7 | 각 P24 전원 꼬리선, Ethernet과 분리 | TBD |
| M12 5 / 6 | 각 N24 전원 꼬리선, Ethernet과 분리 | TBD |
| RJ45 4 / 5 / 7 / 8 | 도면상 신호 배선 없음 | TBD |
| M12 shell ↔ RJ45 shield ↔ 전원선 | 도면만으로 확정하지 않음 | TBD |

실제 핀 번호와 key를 사진에 함께 표시한다. 예상과 다른 회로를 기존 지그에 맞춰 억지로 연결하지 않는다.

## RJ45 공유와 기준면

한 번에 LLC M12 지그 1장과 기존 RJ45 지그 1장을 사용한다. RJ45의 A(J2, 핀 1/2)와 B(J3, 핀 3/6)가 측정 채널이다. C(J4)와 D(J5)는 DUT에서 사용하지 않지만 지그 측 SMA는 매번 50 Ω으로 종단한다.

기본 RCT는 양쪽 모두 DNP이며 RJ45의 사용하지 않는 C/D RCT도 DNP를 유지한다. RJ45 SHIELD-BONDED 또는 SHIELD-FLOAT 중 사용할 보드를 식별하고 REF/DUT 사이에 바꾸지 않는다. 실제 shell/shield continuity와 새 M12 기구의 접지 경로를 확인한 뒤 사용할 shield 상태를 고정한다. 두 기존 RJ45 assembly variant를 공유하므로 기본적으로 추가 저항 손납땜이 필요하지 않다.

동봉 O/S/L을 두 coax cable end에서 순차 재사용하고 F-F THRU로 full two-port SOLT를 수행한다. 이 교정은 M12와 RJ45 접점까지 기준면을 옮기지 않으며 발룬/PCB/커넥터 특성은 결과에 남는다.

LLC용 REF는 같은 M12/RJ45 커넥터 조합과 8→1, 2→2, 3→3, 4→6 결선의 알려진 짧은 100 Ω twisted-pair 하네스가 필요하다. 슬립링 Molex↔M12 REF와는 다르다. 완성 하네스 외주/조달을 별도로 검토하고 사용자 소형 커넥터 손작업을 가정하지 않는다. 짧은 REF 대비 13 m급 케이블 손실 증가는 길이 차이도 포함하므로 이를 결함으로 단정하지 않는다.

## S-parameter / NEXT / FEXT 연결표

`M_A/M_B`는 LLC M12 지그 J2/J3, `R_A/R_B/R_C/R_D`는 RJ45 지그 J2/J3/J4/J5다. 각 행에서 S11/S21/S12/S22를 함께 저장한다.

| 측정 | VNA Port 1 | VNA Port 2 | 50 Ω으로 종단할 SMA |
| --- | --- | --- | --- |
| A pair 전송·반사 | M_A | R_A | M_B, R_B, R_C, R_D |
| B pair 전송·반사 | M_B | R_B | M_A, R_A, R_C, R_D |
| M12 측 NEXT | M_A | M_B | R_A, R_B, R_C, R_D |
| RJ45 측 NEXT | R_A | R_B | M_A, M_B, R_C, R_D |
| FEXT 대각 1 | M_A | R_B | M_B, R_A, R_C, R_D |
| FEXT 대각 2 | M_B | R_A | M_A, R_B, R_C, R_D |

6개 coax 중 VNA가 2개를 사용하므로 **LLC 측정은 외부 load 4개**가 필요하다. 기존 공용 load 6개와 THRU 1개로 충분하며, 지그를 2개 보유한다는 이유만으로 종단·교정 부속을 배수 구매하지 않는다. 한 VNA로 순차 측정하는 조건이다.

## 측정 해석

- 기존 비교 설정의 1–200 MHz sweep부터 시작하고 sweep/IFBW/power/평균 횟수는 REF와 DUT에서 동일하게 유지한다. 주파수 상한을 늘리면 지그 자체 응답과 누설 바닥값부터 다시 확인한다.
- S11/S22의 반사, S21/S12의 전송·삽입손실, 필요 시 phase/group delay, 양단 NEXT/FEXT를 비교한다. 동축 케이블의 위치·굽힘·토크와 전원 꼬리선의 배치를 기록한다.
- 케이블 길이(도면의 13,000/13,500 mm 치수), 커넥터, 두 발룬과 두 PCB의 영향을 포함한 비교 측정이다. 혼합 M12+RJ45 지그의 응답을 기존 RJ45+RJ45 기준으로 단순 대체하지 않는다.
- 두 LLC 지그는 각자 동일 REF로 baseline을 확보해 지그 편차와 DUT 편차를 구분한다.
- 결과는 full mixed-mode Sdd/Sdc/Scd/Scc 또는 정식 Ethernet 인증 결과가 아니다. 정확한 기준면 이동에는 별도 fixture characterization/de-embedding이 필요하다.
- 판정 대역, insertion/return-loss 및 NEXT/FEXT 한계, 반복성 허용차와 noise-floor margin이 정해지기 전에는 PASS/FAIL로 표기하지 않는다.
