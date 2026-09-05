# Slip-ring comparison measurement worksheet

> **2026-09-05 이전 절차:** 이 문서는 전용 balun endpoint와 SMA 기준 REF 비교 구성의 이력이다. 현재 공통 RJ45 지그 + 어댑터 구성은 [VNA_TEST_PLAN](../VNA_TEST_PLAN.md)의 adapter-end O/S/L + UnknownThru 절차를 따른다. 미사용 SMA 수, 기준면, 표준과 조달 지시는 새 구성에 그대로 적용하지 않는다. 변경 이유는 [설계 검토 인계](../DESIGN_REVIEW_HANDOFF.md)에 있다.

상태: `DRAFT` — 문서 핀맵과 SMA land pattern은 반영했지만 REV-504 continuity, endpoint connector 기구, M12 실장 방향과 JLC wave-solder 승인이 미검증이므로 아직 제작하거나 측정에 사용하지 않는다.

## DUT와 안전 조건

- 대상: PALA720 2세대 `SRS1202-12CZ`, 100BASE-TX 2페어
- Pair A (`PAIR_TX`): TX+/- = Molex 1/2 ↔ M12 4/3
- Pair B (`PAIR_RX`): RX+/- = Molex 3/4 ↔ M12 2/1
- M12 5=GPS RS232_RX, 6=GPS 1PPS, 7=24VDC, 8=24VDC GND이며 지그에서는 모두 NC
- continuity와 VNA 측정 전 DUT를 24VDC, PoE 및 모든 활성 장비에서 분리

SRS1202 일반 자료의 정격은 100 rpm, 회로당 2 A, 동적 noise 50 mΩ max @ 100 rpm이다. 출하검사성적서의 절연 1.2 GΩ, 접촉회로 저항 241/248 mΩ 및 순간단선 양호는 외관·치수·DC 검사 범위이며 RF/Ethernet 합격 근거가 아니다.

## 기준면과 비교 방식

- LibreVNA의 coax cable 끝에서 각 포트의 SOLT를 수행한다.
- 이 SOLT로 기준면이 Molex/M12 접점까지 이동하지 않는다. 두 balun 보드, 커넥터와 fan-out은 fixture로 남는다.
- 먼저 두 지그 사이에 `REF/bypass`를 연결해 기준값을 저장하고, 같은 지그·케이블·설정에서 이를 슬립링으로 교체한다.
- 절대 differential S-parameter가 필요하면 별도로 검증한 2×thru/de-embedding 절차가 필요하다.

이 2-port 구성은 두 balun을 포함한 single-ended 비교 proxy이며 mixed-mode `Sdd/Sdc/Scd/Scc`를 각각 측정하지 못한다. 따라서 center tap 접지로 공통모드 escape path가 달라진 결과를 슬립링의 순수 differential 성능 변화로 해석하지 않는다. 절대 mixed-mode 분석에는 검증된 4-port 측정 또는 그에 맞는 fixture characterization/de-embedding이 필요하다.

## REF/bypass 확정표

| 항목 | 값 |
| --- | --- |
| REV-504 Ethernet housing | Molex `5055650501` 교차 슬라이드 추론 후보(정확한 MPN은 슬라이드 15의 별도 4세대 표); 2세대 실물 확인 TBD |
| Molex PCB mate | `5055680571`; 제조사상 `505565` series mate이나 실제 REV-504 체결 확인 TBD |
| M12 female | Finecables `MB12FBAFF08ST-3`; manufacturer female 8P PCB 배열을 적용한 PCB B면 후보이며 front-fastened 패널 기구, suffix, mating view와 A-key/pin-1 확인 TBD |
| REF Molex cable housing / contact | Molex `5055650501` (`C564750`) 1개 + matte-tin `5054311000` (`C385112`) 4개; 전용 압착 후 pull/continuity 검사 |
| REF M12 cable plug | NorComp `858FA08-103RAU1`, A-code 8-pin male, 4–6 mm cable gland; 실물 pin-1/key mating 확인 전 HOLD |
| REF cable | LAPP `2170284`, 2×2×AWG26/7, nominal 100 Ω Cat.5e SF/UTP; 완성 길이는 DUT connector-to-connector 실측 후 확정 |
| conductor/crimp 적합성 | cable core Ø 약 0.95 mm(최신 자료 max 1.04 mm), terminal 허용 Ø0.78–1.02 mm이므로 양산 전 실선 4가닥 압착·pull test 필수 |
| Pair A / Pair B | cable의 두 twisted pair를 각각 하나의 pair로 사용; connector 앞에서 필요한 최소 길이만 untwist |
| shield/drain 처리 | `CT-FLOAT` baseline에서 양단 모두 미접속·절연; 임의 chassis 연결 금지 |
| 제작물 식별번호 | TBD |

REF는 슬립링과 같은 양끝 커넥터 조합을 사용하고, 가운데는 알려진 짧은 100 Ω twisted pair로 직접 연결한다. 커넥터와 pin view를 실물로 확인하기 전에는 REF도 제작하지 않는다.

## LibreVNA 공통 설정

| 항목 | 값 |
| --- | --- |
| 주파수 시작/끝 | 기본 characterization `1–200 MHz`; `200–450 MHz`는 exploratory 별도 sweep |
| point 수 | 기본 `1001` 또는 `1601`; qualification 고정값 TBD |
| IFBW | IL/RL `100 Hz`, NEXT/FEXT `10–30 Hz`; qualification 고정값 TBD |
| source power | 기본 `−10 dBm`; `−20 dBm` 반복으로 선형성 확인; qualification 고정값 TBD |
| averaging | IL/RL `8`, NEXT/FEXT `16–64`; qualification 고정값 TBD |
| calibration kit / calibration 파일 | 두 cable end에서 O/S/L을 순차 재사용하고 SMA F-F thru를 측정한 LibreVNA `SOLT_12`; kit/thru ID와 calibration 파일명 TBD |
| coax cable 식별번호 | Mini-Circuits `CBL-2FT-SMSM+` 2개 또는 동급으로 검증된 동일 케이블 2개; 개별 ID TBD |
| 외부 50 Ω terminator 식별번호 | Mini-Circuits `ANNE-50+` 동일품 6개 공용 세트; LOAD-01–LOAD-06 실물 ID 부여 |

한 번 정한 설정은 REF, 정지 위치별 DUT와 회전 중 DUT 측정에 동일하게 적용한다.

ADT2-1T+ catalog의 사용 범위는 0.4–450 MHz이지만 1 dB transformer band는 1–200 MHz다. 따라서 목적이 상대 characterization이면 1–200 MHz를 우선 기본 대역 후보로 검토하고, 200–450 MHz는 REF fixture의 return-loss/crosstalk floor와 반복성을 먼저 측정한 뒤 exploratory 구간으로 분리한다. 정식 100BASE-TX 적합 판정이 목적이면 적용할 표준·limit와 fixture 제거 방법을 별도로 정해야 하며, 위 설정과 아래 합격선이 `TBD`인 동안 결과를 `PASS/FAIL`로 표시하지 않는다.

## 사용 전 확정할 판정 기준

| 항목 | 판정값 |
| --- | --- |
| REF 대비 insertion-loss 증가 허용치와 평가 대역 | TBD dB / TBD MHz |
| return-loss 최소치 또는 REF 대비 열화 허용치 | TBD dB |
| NEXT/FEXT 최대치와 fixture noise-floor margin | TBD dB |
| 0°/90°/180°/270° 간 최대 변동 | TBD dB / TBD ps |
| 회전 중 허용 dropout·접촉 변동과 검출 bandwidth | TBD |
| 반복 탈착/재측정 허용 편차와 반복 횟수 | TBD |

이 표를 채우기 전 절차는 비교 데이터 취득용 worksheet이지 재현 가능한 qualification 규격이 아니다.

RJ45 두 보드는 총 SMA 8개 중 VNA가 2개를 쓰므로 미사용 포트 종단용 `ANNE-50+`가 6개 필요하다. 슬립링 두 endpoint는 총 SMA 4개 중 2개만 미사용하므로 같은 6개 세트를 공유한다. 기존 종단기가 정확히 같은 정품 `ANNE-50+`로 확인되고 손상 없이 검증된 경우에만 신규 5개를 사고, 그 외에는 신규 동일품 6개를 구매해 미확인품을 측정 세트에 섞지 않는다.

NEXT/FEXT에서는 두 coax의 상호 결합이 측정 바닥값처럼 보일 수 있다. 두 케이블의 간격, 굽힘, 고정 위치와 connector torque를 REF/DUT 사이에 바꾸지 않는다. 구매 수량과 최신 조달 상태는 [`../JLCPCB_FINAL_BOM.csv`](../JLCPCB_FINAL_BOM.csv)를 따른다.

## Center-tap 조립 상태

| 상태 | Molex측 RCT1/RCT2 | M12측 RCT1/RCT2 | 용도 |
| --- | --- | --- | --- |
| `CT-FLOAT` | 모두 DNP | 모두 DNP | 기본 REF/DUT 비교 |
| `CT-GND` | 모두 0 Ω FIT | 모두 0 Ω FIT | 공통모드 민감도 확인용 별도 진단 |

기본 측정은 양단 네 개 RCT를 모두 비운 `CT-FLOAT`로 수행한다. `CT-GND`는 네 개를 동시에 장착한 별도 sweep으로만 수행한다. 양끝, TX/RX 또는 측정/미측정 pair 사이에 FIT/DNP 상태를 섞지 않는다. 미측정 pair의 SMA를 50 Ω로 종단해도 해당 pair의 RCT 상태는 다른 세 RCT와 같아야 한다.

`CT-GND`에서는 두 center tap이 LibreVNA의 공통 coax/chassis GND를 통해 연결된다. 실제 pair 불균형이나 mode conversion에서 발생한 공통모드 전류가 이 경로로 빠지면 일부 trace가 `CT-FLOAT`보다 좋아 보일 수 있으나, 이는 DUT 개선이 아니라 다른 공통모드 경계조건일 수 있다. REF와 DUT를 서로 다른 CT 상태로 비교하지 않는다.

## 2-port 전체 6개 연결표

`M`은 Molex endpoint, `C`는 M12 endpoint, Pair A는 TX, Pair B는 RX다. 각 연결에서 LibreVNA가 source 방향을 전환하므로 `S11`, `S21`, `S12`, `S22` 네 complex trace를 모두 `.s2p`로 저장한다. S12를 얻기 위해 cable을 물리적으로 뒤집지 않는다.

| ID | VNA Port 1 | VNA Port 2 | 사용하지 않는 SMA | 주요 결과 |
| --- | --- | --- | --- | --- |
| `A_THRU` | Molex Pair A (`A_M`) | M12 Pair A (`A_C`) | `B_M`, `B_C` 50 Ω | A의 S11/S22/S21/S12, phase/group delay |
| `B_THRU` | Molex Pair B (`B_M`) | M12 Pair B (`B_C`) | `A_M`, `A_C` 50 Ω | B의 S11/S22/S21/S12, phase/group delay |
| `NEXT_M` | `A_M` | `B_M` | `A_C`, `B_C` 50 Ω | Molex 쪽 NEXT; S21=A→B, S12=B→A |
| `NEXT_C` | `A_C` | `B_C` | `A_M`, `B_M` 50 Ω | M12 쪽 NEXT; S21=A→B, S12=B→A |
| `FEXT_ACROSS_1` | `A_M` | `B_C` | `A_C`, `B_M` 50 Ω | A_M→B_C와 reverse diagonal FEXT |
| `FEXT_ACROSS_2` | `B_M` | `A_C` | `B_C`, `A_M` 50 Ω | B_M→A_C와 reverse diagonal FEXT |

네 logical port의 모든 unordered port-pair는 `C(4,2)=6`개이므로 위 표가 전체 연결이다. 한 조합은 SMA 두 곳을 사용하며 외부 50 Ω 종단이 필요한 미사용 SMA는 **나머지 두 곳**이다. ADT2-1T+의 nominal 1:2 impedance ratio 때문에 SMA의 50 Ω load는 balanced 쪽에서 이상적으로 100 Ω differential termination으로 보이며 별도 100 Ω 종단 자작은 필요하지 않다.

전체 계산식, RJ45 28개 연결 체계, fixture-floor 판정과 권장 설정의 근거는 [`../VNA_TEST_PLAN.md`](../VNA_TEST_PLAN.md)를 따른다. DUT crosstalk가 fixture+REF floor보다 최소 10 dB, 가능하면 20 dB 이상 크지 않으면 정량 결과로 승인하지 않는다. 10 dB 미만은 `measurement-floor limited`, 6 dB 이내는 upper bound로 기록한다.

## 위치와 파일 이름

```text
YYYYMMDD_<REF|DUT>_<CTFLOAT|CTGND>_<A|B|AtoB|BtoA>_<ILRL|NEXT|FEXT>_<000|090|180|270|ROT>deg_<run>.s2p
```

각 측정 세트에 다음을 기록한다.

- REF/bypass와 DUT 식별번호
- DUT 0°, 90°, 180°, 270° 정지 상태와 가능한 경우 저속 회전 중 반복 sweep
- `CT-FLOAT` 또는 `CT-GND` 상태와 양쪽 보드 네 RCT의 육안/continuity 확인 결과
- 미사용 SMA 두 곳의 50 Ω 종단 상태
- M12 체결 상태와 회전 속도
- 이상이 나타난 각도와 반복 가능 여부

## 완료 조건

- [`PINMAP.md`](PINMAP.md)의 문서 예상값과 별도로 continuity 및 회전 접촉표 완료
- 두 커넥터의 실제 MPN, key/pin view와 기구 체결 확인
- REF의 실제 MPN·길이·배선·사진 기록
- 양 endpoint의 M3 head/washer 외경·재질·장착 면을 기록하고 RF trace/solder mask 비접촉 확인
- 각 측정에서 미사용 SMA 두 곳을 50 Ω로 종단
- `ANNE-50+` LOAD ID와 사용 포트를 기록하고 REF/DUT 사이에 같은 종단 배치를 유지
- calibration과 sweep 설정 저장, REF와 DUT에 동일 설정 적용
- 원본 Touchstone 파일을 수정하지 않고 별도 분석본 생성

`RS422_Cable_Assembly_Spec.pptx`의 10핀 encoder 케이블 핀맵과 길이는 본 측정 구성에 적용하지 않는다.
