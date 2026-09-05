# Balun fixture VNA test plan

상태: `CHARACTERIZATION PLAN` — 이 절차는 2-port LibreVNA와 balun fixture로 golden REF와 DUT의 차이를 비교하기 위한 것이다. 적용 표준, 수치 limit와 검증된 fixture de-embedding이 확정되기 전에는 정식 Ethernet qualification 또는 `PASS/FAIL` 절차로 사용하지 않는다.

## 핵심 결론

- ADT2-1T+의 nominal impedance ratio는 1:2다. SMA primary를 50 Ω로 종단하면 balanced secondary에서는 이상적으로 100 Ω differential termination으로 보인다. 따라서 사용자가 RJ45, Molex 또는 M12 쪽에 100 Ω 종단기를 자작할 필요가 없다.
- calibration kit의 Open, Short, 50 Ω Load는 각각 한 개만 있어도 양쪽 cable end에서 순차 재사용할 수 있다. 단, full 2-port calibration에는 두 cable end를 잇는 SMA female-female thru가 필요하며 LibreVNA에서 thru measurement를 포함한 `SOLT_12`를 활성화해야 한다.
- slip-ring endpoint fixture에는 측정 중 외부 50 Ω terminator 2개가 동시에 필요하고, RJ45 fixture에는 6개가 동시에 필요하다. 동일한 SMA-male 50 Ω terminator 6개를 공용 세트로 사용한다.
- 측정값은 coax reference plane 뒤의 balun, PCB routing, connector와 DUT를 모두 포함한 differential-mode proxy다. 절대 `Sdd/Sdc/Scd/Scc` 또는 정식 cable-certifier 결과가 아니다.

ADT2-1T+의 catalog 범위는 0.4–450 MHz지만 1 dB insertion-loss band는 1–200 MHz다. 기본 characterization 대역은 1–200 MHz로 두고 200–450 MHz는 fixture floor와 반복성을 먼저 검증한 exploratory 대역으로 분리한다.

공식 참고자료:

- [Mini-Circuits ADT2-1T+](https://www.minicircuits.com/pdfs/ADT2-1T%2B.pdf)
- [LibreVNA 양 포트 SOLT 설명](https://github.com/jankae/LibreVNA/discussions/237)
- [Rohde & Schwarz balanced/NEXT/FEXT measurement note](https://scdn.rohde-schwarz.com/ur/pws/dl_downloads/dl_application/application_notes/1ez53/1EZ53_0E.pdf)
- [Keysight fixture de-embedding note](https://www.keysight.com/zz/en/assets/7018-06806/application-notes/5980-2784.pdf)

## Calibration과 준비물

### 가진 O/S/L 한 세트 사용법

1. LibreVNA와 coax cable을 충분히 warm-up한다.
2. 실제 측정에 사용할 두 coax의 최종 cable end를 움직이지 않을 위치에 고정한다.
3. Port 1 cable end에서 같은 Open, Short, Load를 순차 측정한다.
4. Port 2 cable end에서 같은 Open, Short, Load를 순차 측정한다.
5. 두 cable end를 SMA female-female thru로 연결해 thru를 측정한다. 사용한 thru의 성별과 식별번호를 기록한다.
6. LibreVNA에서 `SOLT_12`를 활성화하고 calibration을 저장한다. Port 1/2에 각각 별도 SOL만 켠 상태는 full 2-port calibration이 아니다.
7. 검증용 50 Ω load를 각 port에 연결했을 때 Smith chart 중심과 양호한 return loss를 보이는지 확인한다.
8. thru 재연결 시 S21/S12가 0 dB 부근에서 매끄럽고 reciprocity가 양호한지 확인한다.

O/S/L은 순차 calibration에 재사용할 수 있지만, DUT의 unused port는 측정 중 동시에 종단되어야 한다. 따라서 calibration load 한 개만으로 실제 측정을 진행할 수는 없다.

### 최소 추가품

| 품목 | 최소 수량 | 요구사항 |
| --- | ---: | --- |
| 외부 50 Ω terminator | 6 | SMA-male, 동일 모델, 최소 DC–500 MHz/권장 DC–1 GHz 이상, 1–200 MHz return loss 25–30 dB 이상 |
| Calibration thru | 1 | 두 coax 끝이 SMA male이면 SMA female-female, 식별번호 기록 |
| SMA torque wrench | 1 | 모든 calibration/fixture connection에 동일 torque 적용 |
| Coax 고정구 | 1 set | NEXT/FEXT에서 cable 간격·굽힘·위치를 고정 |

입고 후 6개 terminator의 S11을 같은 cable end에서 각각 측정해 불량과 편차를 확인한다. `LOAD-01`–`LOAD-06`으로 표기하고, REF와 DUT 사이에는 같은 physical port에 같은 load를 유지한다.

## S-parameter와 표시값

LibreVNA는 한 번의 2-port 연결에서 source 방향을 전환해 `S11`, `S21`, `S12`, `S22`를 모두 측정한다. 매 구성마다 네 complex trace가 들어 있는 원본 `.s2p`를 저장한다.

| 표시값 | 정의 |
| --- | --- |
| Port 1 return loss | `RL1 = -20 log10(|S11|)` dB |
| Port 2 return loss | `RL2 = -20 log10(|S22|)` dB |
| Forward insertion loss | `IL21 = -20 log10(|S21|)` dB |
| Reverse insertion loss | `IL12 = -20 log10(|S12|)` dB |
| NEXT/FEXT coupling loss | `XT = -20 log10(|Scoupled|)` dB; S21 또는 S12 사용 |
| Reciprocity error | complex `S21-S12` 또는 magnitude/phase 차이 |

FEXT는 raw IO-FEXT와 aggressor through loss를 제거한 ELFEXT를 함께 기록한다.

```text
IO_FEXT_loss = -20 log10(|S_coupled|)
aggressor_IL = -20 log10(|S_aggressor_through|)
ELFEXT_loss  = IO_FEXT_loss - aggressor_IL
```

예를 들어 FEXT trace가 −60 dB이고 같은 방향 aggressor through가 −10 dB이면 IO-FEXT loss는 60 dB, ELFEXT loss는 50 dB다. Trace math로는 `S_coupled / S_aggressor_through`의 magnitude를 loss 부호로 변환한 값과 같다.

## Slip-ring endpoint: 전체 6개 연결

`M`은 Molex endpoint, `C`는 M12 endpoint, `A`는 TX pair, `B`는 RX pair다. 네 logical differential port는 `A_M`, `B_M`, `A_C`, `B_C`이며, 네 port에서 가능한 모든 unordered port-pair는 `C(4,2)=6`개다.

| ID | VNA Port 1 | VNA Port 2 | 외부 50 Ω terminator | 해석 |
| --- | --- | --- | --- | --- |
| `A_THRU` | `A_M` | `A_C` | `B_M`, `B_C` | A의 S11/S22/S21/S12, phase, group delay |
| `B_THRU` | `B_M` | `B_C` | `A_M`, `A_C` | B의 S11/S22/S21/S12, phase, group delay |
| `NEXT_M` | `A_M` | `B_M` | `A_C`, `B_C` | Molex 쪽 NEXT; S21=A→B, S12=B→A |
| `NEXT_C` | `A_C` | `B_C` | `A_M`, `B_M` | M12 쪽 NEXT; S21=A→B, S12=B→A |
| `FEXT_ACROSS_1` | `A_M` | `B_C` | `A_C`, `B_M` | A_M→B_C와 reverse diagonal FEXT |
| `FEXT_ACROSS_2` | `B_M` | `A_C` | `B_C`, `A_M` | B_M→A_C와 reverse diagonal FEXT |

S12를 얻기 위해 cable을 물리적으로 뒤집지 않는다. 한 연결의 S21/S12는 같은 두 physical port 사이의 양방향 결과다. 위 여섯 연결이 네 logical port의 모든 pairwise 조합을 완전히 덮는다.

## RJ45 4-pair fixture: 전체 28개 연결

RJ45 pair와 SMA 이름은 다음과 같다.

| Pair | SMA | RJ45 pins |
| --- | --- | --- |
| A | J2 | 1–2 |
| B | J3 | 3–6 |
| C | J4 | 4–5 |
| D | J5 | 7–8 |

두 fixture의 side를 `L`과 `R`로 부르면 logical port는 `A_L`…`D_L`, `A_R`…`D_R` 총 8개다. 각 연결에서 VNA가 두 port를 쓰고 나머지 여섯 port에는 50 Ω terminator를 장착한다.

### 4개 through 연결

```text
A_L ↔ A_R
B_L ↔ B_R
C_L ↔ C_R
D_L ↔ D_R
```

### 24개 crosstalk 연결

unordered pair 조합 `AB`, `AC`, `AD`, `BC`, `BD`, `CD` 각각에 대해 아래 네 연결을 수행한다. `X`, `Y`는 해당 pair 조합의 두 pair다.

```text
NEXT_L:       X_L ↔ Y_L
NEXT_R:       X_R ↔ Y_R
FEXT_DIAG_1:  X_L ↔ Y_R
FEXT_DIAG_2:  Y_L ↔ X_R
```

따라서 `4 through + C(4,2) × 4 crosstalk = 4 + 24 = 28`개의 `.s2p` 연결이 된다. 각 파일은 S11/S21/S12/S22를 모두 포함한다. 이 28개는 나머지 port가 nominally matched되어 있다는 조건에서 8 logical differential-proxy port의 모든 unordered port-pair를 덮는다.

## REF, fixture floor와 신뢰 가능한 dynamic range

Coax SOLT 기준면은 cable end이며 RJ45/Molex/M12 접점까지 이동하지 않는다. 따라서 보드, balun, connector와 fan-out이 측정에 포함된다.

1. 두 coax에 50 Ω load를 직접 연결하고 실제 측정과 같은 cable 위치에서 instrument+cable isolation floor를 저장한다.
2. 두 fixture 사이에 high-isolation golden REF/bypass를 연결하고 모든 unused port를 종단한 뒤 같은 6개 또는 28개 연결을 저장한다.
3. cable 위치, 굽힘, board 방향, connector torque와 load assignment를 바꾸지 않고 DUT로 교체한다.
4. DUT crosstalk가 fixture+REF floor보다 최소 10 dB, 가능하면 20 dB 이상 큰 경우에만 수치 결과로 보고한다.
5. margin이 10 dB 미만이면 `measurement-floor limited`, 6 dB 이내이면 수치 대신 upper bound로 표시한다.

NEXT/FEXT는 fixture와 DUT의 coupling이 complex vector로 더해져 상쇄될 수도 있다. 따라서 REF와 DUT의 crosstalk dB를 단순 감산하지 않는다. 원본 complex Touchstone을 보존하고, 반복 탈착과 cable-layout 반복으로 위상·magnitude 안정성을 확인한다.

LibreVNA의 optional isolation calibration은 움직이지 않은 setup에서 floor를 낮출 수 있지만 cable이나 fixture를 조금만 움직여도 개선분이 사라질 수 있다. 기본 결과는 물리적 floor 측정과 반복성으로 검증하고 isolation correction에만 의존하지 않는다.

Insertion loss는 REF 대비 complex normalization 또는 dB 차이가 실용적인 1차 비교가 된다. 반면 return loss는 fixture와 DUT 사이 multiple reflection 때문에 REF의 dB를 단순히 빼서 de-embed할 수 없다. 절대 balanced reference-plane 결과가 필요하면 검증된 2x-thru/fixture model과 vector de-embedding이 필요하다.

## 지그 자체의 확인된 한계

- ADT2-1T+ 단품의 typical insertion loss / input return loss는 100 MHz에서 약 `0.48 / 18.91 dB`, 200 MHz에서 `0.69 / 13.40 dB`, 400 MHz에서 `1.25 / 8.18 dB`다. Through 측정에는 balun 두 개가 들어가므로 PCB와 DUT 전부터 typical loss가 약 `0.96 dB @100 MHz`, `1.38 dB @200 MHz` 누적될 수 있고, 고주파 return-loss ripple도 커진다.
- RJ45 connector 바로 앞에는 0.15 mm neckdown이 약 3.04/5.07 mm 존재한다. 국부 impedance는 약 141–144 Ω지만 1–200 MHz에서는 전기적으로 짧아 단독으로 치명적이라고 보지는 않는다. pair 내 비대칭과 connector pin field는 mode conversion 및 crosstalk floor에 포함된다.
- 같은 층의 서로 다른 pair 사이 최소 동박 간격은 RJ45 약 0.67 mm, Molex 약 1.02 mm, M12 약 2.05 mm다. Transformer, connector fan-out, coax 두 개의 배치가 낮은 NEXT/FEXT의 측정 바닥값이 될 수 있다.
- 현재 보드에는 SMA launch와 balun만 분리 검증하는 true 2x-thru/isolation coupon이 없다. 따라서 당장은 각 연결별 golden REF와 반복 탈착 측정이 authority다.

추가 주문을 허용한다면 별도 `fixture_qa` coupon을 만드는 것이 가장 직접적이다. 한 채널은 `SMA → ADT2 → 짧은 100 Ω pair → ADT2 → SMA`로 balun/launch baseline을 만들고, 다른 두 채널은 secondary를 JLC 조립 100 Ω 정밀저항으로 종단해 board-level isolation floor를 확인한다. 이는 유용하지만 새 PCB와 조립비가 드는 설계 확장이므로 현재 release에 자동 포함하지 않는다.

## 측정 가능한 항목과 한계

### 현재 fixture로 가능한 것

- 각 pair의 S11/S22 return-loss proxy
- S21/S12 insertion loss, phase, group delay와 reciprocity
- matched unused-port 조건의 NEXT/FEXT 및 ELFEXT proxy
- golden REF 대비 slip-ring 열화
- 0°/90°/180°/270° 등 정지 각도별 변화
- RJ45 4-pair의 전체 28개 pairwise proxy matrix

### 비교 또는 proxy로만 해석할 것

- 절대 differential insertion/return loss
- 절대 NEXT/FEXT
- 100 Ω differential impedance profile
- connector reference plane에서의 phase/group delay

### 현재 2-port balun 구성으로 측정할 수 없는 것

- mixed-mode `Sdd/Sdc/Scd/Scc`의 독립 분리
- differential↔common-mode conversion, TCL/LCL/TCTL/LCTL
- common-mode return loss와 common-mode impedance
- 정식 Ethernet cable-certifier compliance
- swept VNA보다 짧은 순간단선/dropout의 보장된 검출

Balun secondary center tap을 float하면 common mode가 open에 가깝고, 0 Ω로 접지하면 common mode를 short하는 별도 경계조건이 된다. `CT-FLOAT`와 `CT-GND`는 같은 상태의 REF/DUT끼리만 비교하며, CT-GND 결과가 좋아진 것을 DUT 자체 개선으로 해석하지 않는다.

## 권장 공통 sweep 설정

| 항목 | 기본 IL/RL | NEXT/FEXT |
| --- | --- | --- |
| 주파수 | 1–200 MHz | 1–200 MHz |
| Point 수 | 1001 또는 1601 | 1001 또는 1601 |
| Source power | −10 dBm | −10 dBm |
| IFBW | 100 Hz | 10–30 Hz |
| Averaging | 8 | 16–64 |
| Calibration | cable end `SOLT_12` | 동일 calibration |

첫 측정에서 source를 −20 dBm으로 낮춘 결과도 한 번 저장해 선형성과 leakage floor를 확인한다. 이후 REF와 모든 DUT sweep에서는 설정을 고정한다. 200–450 MHz는 별도 파일명과 exploratory 표식을 사용한다.

## 회전 중 측정

Full frequency sweep 중에는 주파수와 회전 각도가 동시에 변하므로 한 sweep의 notch를 특정 각도나 순간단선으로 직접 해석할 수 없다.

- full S-parameter는 0°/90°/180°/270° 또는 더 촘촘한 정지 각도에서 측정한다.
- 회전 중에는 10/31.25/62.5/100 MHz 등 미리 정한 대표 주파수에서 fixed-frequency/time trace를 별도로 취득한다. 최종 주파수 목록은 실제 spectrum과 REF 결과에 따라 확정한다.
- LibreVNA의 update interval보다 짧은 dropout은 놓칠 수 있다. 짧은 순간단선 qualification에는 Ethernet BERT, oscilloscope/TDR 또는 별도 continuity transient detector가 필요하다.
- 회전 속도, 방향, trigger/update rate와 최소 검출 가능 dropout 시간을 결과에 기록한다.

## 파일명과 완료 조건

```text
YYYYMMDD_<REF|DUT>_<CTFLOAT|CTGND>_<CONFIG>_<000|090|180|270|ROT>deg_<run>.s2p
```

완료 조건:

- O/S/L/thru와 `SOLT_12` calibration 파일 보관
- 6개 terminator의 S11 입고 검사와 `LOAD-01`–`LOAD-06` 배치표 보관
- REF와 DUT에 동일한 fixture, CT/shield 상태, cable 위치와 load assignment 적용
- slip-ring 6개 또는 RJ45 28개 연결별 원본 S11/S21/S12/S22 Touchstone 보관
- instrument floor, fixture+REF floor와 DUT-to-floor margin 기록
- 실제 qualification limit는 별도 승인 전까지 `TBD`
