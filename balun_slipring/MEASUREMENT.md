# Slip-ring comparison measurement worksheet

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
| REV-504 Ethernet housing | Molex `5055650501` 문서 확인; 실물 재확인 TBD |
| Molex PCB mate | `5055680571` 추론 후보; 체결 확인 TBD |
| M12 female | Finecables `MB12FBAFF08ST-3` 후면 실장 후보; suffix, mating view, A-key/pin-1 및 패널 기구 확인 TBD |
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
| 주파수 시작/끝 | TBD |
| point 수 | TBD |
| IFBW | TBD |
| source power | TBD dBm |
| averaging | TBD |
| calibration kit / calibration 파일 | TBD |
| coax cable 식별번호 | Mini-Circuits `CBL-2FT-SMSM+` 2개 또는 동급으로 검증된 동일 케이블 2개; 개별 ID TBD |
| 외부 50 Ω terminator 식별번호 | Mini-Circuits `ANNE-50+` 동일품 6개 공용 세트; LOAD-01–LOAD-06 실물 ID 부여 |

한 번 정한 설정은 REF, 정지 위치별 DUT와 회전 중 DUT 측정에 동일하게 적용한다.

RJ45 두 보드는 총 SMA 8개 중 VNA가 2개를 쓰므로 미사용 포트 종단용 `ANNE-50+`가 6개 필요하다. 슬립링 두 endpoint는 총 SMA 4개 중 2개만 미사용하므로 같은 6개 세트를 공유한다. 기존 종단기가 정확히 같은 정품 `ANNE-50+`로 확인되고 손상 없이 검증된 경우에만 신규 5개를 사고, 그 외에는 신규 동일품 6개를 구매해 미확인품을 측정 세트에 섞지 않는다.

NEXT/FEXT에서는 두 coax의 상호 결합이 측정 바닥값처럼 보일 수 있다. 두 케이블의 간격, 굽힘, 고정 위치와 connector torque를 REF/DUT 사이에 바꾸지 않는다. 구매 수량과 최신 조달 상태는 [`../JLCPCB_FINAL_BOM.csv`](../JLCPCB_FINAL_BOM.csv)를 따른다.

## Center-tap 조립 상태

| 상태 | Molex측 RCT1/RCT2 | M12측 RCT1/RCT2 | 용도 |
| --- | --- | --- | --- |
| `CT-FLOAT` | 모두 DNP | 모두 DNP | 기본 REF/DUT 비교 |
| `CT-GND` | 모두 0 Ω FIT | 모두 0 Ω FIT | 공통모드 민감도 확인용 별도 진단 |

기본 측정은 양단 네 개 RCT를 모두 비운 `CT-FLOAT`로 수행한다. `CT-GND`는 네 개를 동시에 장착한 별도 sweep으로만 수행한다. 양끝, TX/RX 또는 측정/미측정 pair 사이에 FIT/DNP 상태를 섞지 않는다. 미측정 pair의 SMA를 50 Ω로 종단해도 해당 pair의 RCT 상태는 다른 세 RCT와 같아야 한다.

`CT-GND`에서는 두 center tap이 LibreVNA의 공통 coax/chassis GND를 통해 연결된다. 실제 pair 불균형이나 mode conversion에서 발생한 공통모드 전류가 이 경로로 빠지면 일부 trace가 `CT-FLOAT`보다 좋아 보일 수 있으나, 이는 DUT 개선이 아니라 다른 공통모드 경계조건일 수 있다. REF와 DUT를 서로 다른 CT 상태로 비교하지 않는다.

## 2-port 연결표

| 측정 | VNA Port 1 | VNA Port 2 | 사용하지 않는 SMA | 주요 결과 |
| --- | --- | --- | --- | --- |
| Pair A 전송/반사 | Molex Pair A | M12 Pair A | Pair B 양끝 두 곳 50 Ω | S11, S22, S21, phase/group delay |
| Pair B 전송/반사 | Molex Pair B | M12 Pair B | Pair A 양끝 두 곳 50 Ω | S11, S22, S21, phase/group delay |
| A→B near-end crosstalk | 같은 쪽 Pair A | 같은 쪽 Pair B | 반대쪽 A/B 두 곳 50 Ω | S21; 포트 방향 기록 |
| A→B far-end crosstalk | 한쪽 Pair A | 반대쪽 Pair B | 나머지 두 곳 50 Ω | S21; 포트 방향 기록 |
| B→A near/far-end | 위 두 행에서 A/B 교환 |  | 나머지 두 곳 50 Ω | 방향 비대칭 확인 |

2-port 측정 한 조합은 SMA 두 곳을 사용하므로, 외부 50 Ω 종단이 필요한 미사용 SMA는 **나머지 두 곳**이다.

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
- 각 측정에서 미사용 SMA 두 곳을 50 Ω로 종단
- `ANNE-50+` LOAD ID와 사용 포트를 기록하고 REF/DUT 사이에 같은 종단 배치를 유지
- calibration과 sweep 설정 저장, REF와 DUT에 동일 설정 적용
- 원본 Touchstone 파일을 수정하지 않고 별도 분석본 생성

`RS422_Cable_Assembly_Spec.pptx`의 10핀 encoder 케이블 핀맵과 길이는 본 측정 구성에 적용하지 않는다.
