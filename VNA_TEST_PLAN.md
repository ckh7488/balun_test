# 산업용 100BASE-TX 정적 평가와 커넥터 끝 보정

설계 변경의 이유, 구현 범위와 다른 검토자에게 요청할 질문은 [설계 검토 인계](DESIGN_REVIEW_HANDOFF.md)를 참고한다. 이 문서는 현재 측정 절차이며, 과거 전용 지그의 `MEASUREMENT.md`보다 우선한다.

상태: **구현 및 합성 검증 단계 / 실제 지그·표준 정확도 검증 전**. 우선 목적은 정상 케이블과 사내 커넥터·슬립링 조립체의 정적 전송 품질을 확인하는 것이다. 산업현장 사용 가능성의 1차 평가이며, 정식 인증이나 동적 신뢰성 시험을 대신하지 않는다.

## 1. 기준면과 구성

공통 `SMA–ADT2-1T+–RJ45` PCB 두 장을 사용한다. DUT 종류에 맞춰 RJ45–M12/Molex 어댑터를 교체한다. PCB 어댑터의 RJ45 jack까지 잇는 짧은 공장제 patch cable도 고정 fixture에 포함된다.

| 단계 | 포함되는 것 | 기준면 |
| --- | --- | --- |
| LibreVNA full 2-port SOLT | VNA와 두 coax 오차 보정 | 50 Ω coax 끝 |
| M12 등에서 표준 측정 | balun PCB, RJ45 연결, 어댑터를 통과한 O/S/L/T 데이터 | 아직 SMA 기준 데이터 |
| Python UnknownThru 적용 | 고정된 두 fixture의 오차를 표준 모델로 추정·제거 | 어댑터 뒤 DUT 접속면 |
| 최종 출력 | 그 사이 DUT의 유효 차동 two-port | 100 Ω balanced |

양끝이 서로 다른 커넥터여도 된다. 일반 RJ45 케이블은 RJ45 접속면에서 표준을 측정한다. **커넥터별 표준을 바꾸지 않고 어댑터만 교체해 같은 보정값을 쓰면 안 된다.**

측정하려는 커넥터가 보정 기준면보다 fixture 쪽에 있으면 그 특성도 보정에 흡수된다. 특정 커넥터 자체를 평가하려면 DUT 안에 그 커넥터/체결부를 포함하고, 기준면은 그 바깥에 둔다. 체결 접점의 fixture/DUT 경계는 표준 정의와 함께 기록한다. 케이블 포함 조립체 측정과 커넥터 단품 손실 분리를 혼동하지 않는다.

## 2. O/S/L과 자작 thru

O/S/L은 한 **차동 pair의 두 선 사이** 표준이다. SMA 외부 50 Ω load와 용도가 다르다.

| 표준 | M12 암 어댑터의 예 | 모델/제작에서 중요한 것 |
| --- | --- | --- |
| O | 어댑터를 비워 둔 상태 | 개방단 C와 주변 금속/손/다른 핀; 덮개·배치 고정 |
| S | mating 수 커넥터의 해당 pair를 최대한 짧게 연결 | 핀 길이, loop 면적, 직렬 L/R, 기준면에서의 지연 |
| L | 같은 pair 사이에 100 Ω 저항 | 짧은 SMD 저항 접속, 실측 저항값, lead/pad의 L/C |
| T | 양 어댑터에 맞는 mating 커넥터를 짧은 pair로 연결 | reciprocal, 충분한 전달, P/N 극성과 대략적인 편도 지연 |

Short나 Load를 shell/GND로 연결하지 않는다. 사용하지 않는 신호·전원 핀은 DUT 핀맵에 맞게 분리한다. 전원이 포함된 사내 케이블은 전원·활성 장비를 분리하고 무전압을 확인한 수동 상태에서 측정한다.

Open은 별도 부품 없이 가능하다. 다만 빈 암 Open과 수 플러그 끝에서 만든 S/L은 전기적 길이가 다를 수 있다. 이를 모델의 offset/기생성분에 반영한다. OSL 자체의 오차는 그 OSL을 사용한 보정으로 사라지지 않는다.

자작 thru의 전체 S-parameter를 미리 알아야 하는 일반 SOLT 대신 **UnknownThru/SOLR**를 사용한다. reciprocal 특성과 대략적인 위상/극성으로 전달 부호를 정한다. 180°로 떨어진 두 해를 구분할 수 있도록 예상 위상 오차를 90°보다 충분히 작게 유지한다. 모델 입력은 [analysis/README.md](analysis/README.md)를 따른다.

### 표준 오차의 크기 감각

다음은 100 Ω 기준의 단순 예시이며 실제 M12 기생성분 측정값이 아니다.

| 가정 | 100 MHz에서 표준 자체의 영향 |
| --- | --- |
| Load가 실제 101 Ω 순저항 | reflection 약 0.005, RL 약 46 dB |
| 100 Ω Load에 직렬 10 nH | 표준 RL 약 30 dB |
| Short에 직렬 10 nH | 이상적 Short와 반사 위상 약 7.2° 차이 |
| Open에 병렬 1 pF | 이상적 Open과 반사 위상 약 7.2° 차이 |

이 수치를 최종 DUT의 오차 막대와 동일시하지 않는다. 모델을 달리했을 때의 DUT 변화와 독립 검증 표준으로 신뢰 범위를 판단한다.

## 3. 어댑터 2 cm untwist는 보정되는가

항상 같은 형상의 선형·안정된 two-port로 보이는 반사, 지연과 손실은 커넥터 끝 보정에 포함될 수 있다. 3–4 cm 커넥터 몸체나 2 cm untwist만으로 불가능하다고 판단하지 않는다. 그러나 다음은 별개다.

- 움직이거나 다시 체결해 형상이 달라진 부분은 저장된 보정과 달라진다.
- 손실이 크면 보정 후에도 signal-to-noise와 dynamic range가 복구되지 않는다.
- pair 간 누설과 differential↔common-mode 변환은 단순 두 error box에서 완전히 제거되지 않는다.

양선 간격·길이 대칭, 작은 loop, strain relief와 기계 고정이 중요하다. 반복 측정용으로는 **PCB 어댑터를 우선** 검토한다. 임피던스 제어는 일정한 pair 구간을 개선하며 커넥터 pin field나 solder fillet까지 정확히 100 Ω으로 만들지는 않는다.

## 4. 실제 데이터 취득 순서

1. warm-up 뒤 실제 측정할 두 coax 끝에서 O/S/L과 알려진 SMA thru로 full 2-port SOLT를 수행한다. LibreVNA에서는 `SOLT_12` 등 실제 활성화된 양방향 보정을 확인한다. 포트별 SOL 두 개로 대체하지 않는다.
2. 두 포트에서 독립 50 Ω load/짧은 thru를 확인하고 VNA 설정·calibration 파일을 보관한다.
3. balun PCB와 patch cable, 어댑터, 미사용 SMA 50 Ω load, CT/shield 상태를 고정한다.
4. Port 1 O/S/L 3개, Port 2 O/S/L 3개, 자작 thru 1개를 complex Touchstone으로 저장한다. 한 O/S/L 세트를 순차 재사용해도 각 포트 측정 파일은 따로 필요하다.
5. Python으로 **7개 입력만** 사용해 `cal.npz`를 만든다.
6. 같은 full SMA SOLT를 켠 채 DUT를 연결해 `.s2p`를 저장한다. Python으로 `cal.npz`를 적용한다.
7. DUT를 바꿀 때마다 6번을 반복한다. 초기 검증 후에도 독립 check standard를 재측정한다.

모든 취득은 같은 frequency grid를 사용한다. 지그/adapter/coax 접속·배치·포트/pair·CT/shield·부하 상태 변경, SMA 재보정 또는 유의한 drift가 있으면 해당 구성의 표준 측정을 다시 한다. DUT 교체만 했어도 접속 반복성이 허용범위인지 확인한다.

## 5. 권장 초기 sweep

| 항목 | 시작값 |
| --- | --- |
| 주 평가 대역 | 1–100 MHz |
| 확장 관찰 | 100–200 MHz; 같은 sweep에서 분리 해석 가능 |
| points | 1001 또는 1601; 세션 전체 동일 |
| source | −10 dBm; 최초 −20 dBm과 비교하여 선형성 확인 |
| IFBW / 평균 | IL/RL 100 Hz / 8; 누설은 필요 시 더 좁은 IFBW와 반복 |
| CT / shield | CT-FLOAT 기본, 선택한 shield 경계를 표준·DUT 모두 동일하게 유지 |

이는 시험 시작 조건이며 Ethernet 표준 합격선을 정의하지 않는다. ADT2-1T+ 대역과 실제 fixture 특성을 함께 확인한다.

## 6. 정적 평가 항목

| 항목 | 보는 문제 / 결과 |
| --- | --- |
| continuity, 각 선 DC 저항과 pair 불균형 | 핀맵 오류, 납땜/접촉 불량; VNA 전에 확인 |
| pair A/B 각각 S11/S22 | 양쪽 반사, 임피던스 불연속 |
| S21/S12 | 삽입손실, notch, 방향 대칭성 |
| 전달 위상/group delay | 이상 지연·분산; 기준면과 thru 부호 모델에 의존 |
| 반복 체결·고정 재측정 | fixture와 커넥터 반복성 |
| 실제 전체 길이 조립체 | 사용 길이의 손실·반사 누적 |
| 필요 시 정지 각도별 반복 | 슬립링 접촉 상태의 각도 의존성 |
| NEXT/FEXT | 두 pair 사이 결합; 별도 연결과 누설 검증 |

적용할 커넥터/케이블/채널 규격, 길이, 주파수별 limit와 불확도를 정한 후 판단한다. 단일 `RL > 20 dB` 같은 임의 기준을 산업용 합격선으로 쓰지 않는다. 정상 REF 비교는 유용하지만 REF 차이를 dB로 빼는 것이 RL de-embedding은 아니다.

### NEXT/FEXT 연결과 제한

2-pair의 네 logical port `A_L, B_L, A_R, B_R`에 대해 아래 여섯 연결을 사용한다. S12를 얻으려고 같은 연결을 물리적으로 뒤집을 필요는 없다.

| 연결 | Port 1 | Port 2 |
| --- | --- | --- |
| A transmission | A_L | A_R |
| B transmission | B_L | B_R |
| NEXT_L | A_L | B_L |
| NEXT_R | A_R | B_R |
| FEXT_1 | A_L | B_R |
| FEXT_2 | B_L | A_R |

공통 4-pair RJ45 PCB 두 장은 VNA가 SMA 2개를 쓰고 나머지 **6개**에 외부 50 Ω load가 필요하다. 이 load는 nominally 100 Ω balanced 종단을 제공하는 용도이며 **DUT 접속면 OSL의 100 Ω Load 표준을 대체하지 않는다.**

각 연결의 error box 조합이 달라지므로 IL/RL pair A용 `cal.npz`를 NEXT/FEXT에 그대로 적용하지 않는다. 각 연결별 OSL/전달 경로 보정과 fixture floor를 확보한다. 다른 pair와 common mode가 강하게 결합하면 2-port 모델로 부족하다. 현재 Python 도구는 한 연결의 correction을 제공하며 전체 crosstalk matrix나 규격 판정을 자동화하지 않는다.

4-pair 케이블은 through 4개와 pair 조합 6개 × NEXT/FEXT 4개 = 총 28개 연결이다. 모든 미사용 포트가 nominally matched라는 조건에서의 pairwise 취득이다.

누설은 complex vector로 상쇄될 수 있다. fixture+REF floor와 가까운 결과에는 수치 합격을 부여하지 말고 floor-limited로 기록한다. floor보다 DUT 결합이 10–20 dB 큰 것은 실무상 유용한 여유지만 엄밀한 불확도 계산이나 보장된 upper bound를 대신하지 않는다.

## 7. 보정 후 확인

- 독립적으로 만든 다른 저항/선로를 확인한다. 보정에 쓴 O/S/L을 다시 이상적으로 만드는 것만으로 정확도를 입증하지 않는다.
- 자작 thru와 DUT의 방향/극성, 유효 대역 reciprocity와 passivity를 확인한다.
- 반복 탈착 분산, drift, 표준 모델 민감도를 기록한다.
- SMA 원본과 보정 후 결과를 함께 보존한다. 기준면과 출력 100 Ω reference를 확인한다.

balun 기반 two-port는 full mixed-mode Sdd/Sdc/Scd/Scc나 TCL/ELTCTL을 독립 측정하지 못한다. 이는 산업 EMI 관점에서 남는 항목이다. 정적 결과 이후 실제 PHY 트래픽·오류율, 회전 중 순간단선, 온도/진동/EMC 시험으로 연결한다. swept VNA가 짧은 dropout을 모두 검출한다고 가정하지 않는다.

## 근거와 이력

- [Mini-Circuits ADT2-1T+](https://www.minicircuits.com/pdfs/ADT2-1T%2B.pdf)
- [scikit-rf UnknownThru](https://scikit-rf.readthedocs.io/en/latest/api/calibration/generated/skrf.calibration.calibration.UnknownThru.html)
- [Keysight standard 모델](https://helpfiles.keysight.com/csg/e5080a/s3_cals/calibration_standards.htm)
- [JLCPCB impedance stack-up](https://jlcpcb.com/impedance)
- 종전 SMA-only 비교 문서는 [legacy 기록](docs/legacy/README.md)에 보존했다.
