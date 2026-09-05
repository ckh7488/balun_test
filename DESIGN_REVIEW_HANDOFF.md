# 설계 의도와 검토 인계 — 2026-09-05

**검토의 출발점은 이 문서다.** 현재 방향은 공통 RJ45 balun 지그와 교체형 수동 어댑터를 사용하고, 어댑터 뒤 DUT 접속면까지 Python으로 보정하는 것이다. 기존 커넥터 전용 balun 보드와 과거 구매 문서가 함께 남아 있으므로, 파일이 존재한다는 이유만으로 모두 현재 제작 대상이라고 해석하지 않는다.

현재 성숙도는 **Python 합성 검증 + 배선된 어댑터 CAD 검증**이다. 공식 JLC 계산기 결과는 후속 패치로 반영했으나 실물 RF 정확도, 커넥터 호환·패널 기구, 생산 CAM/coupon은 미검증이며, O/S/L/T 표준의 전용 PCB도 아직 없다.

## 2026-09-05 후속 패치: 공식 계산기와 실제 주문 조건

이번 추가 요청은 “JLC 적층 기준 100Ω 여부를 검사·확정하고, 주문 옵션 전체와 이유를 실제 화면으로 남기기”다. [계산 증거](docs/jlcpcb/IMPEDANCE.md)와 [주문 가이드](docs/jlcpcb/README.md)가 이 패치의 기준이다.

- 공식 JLC 역산 결과를 반영해 네 활성 PCB의 차동 폭/간격을 **0.234/0.216 mm**, 공통 SMA 측 폭을 **0.357 mm**로 바꿨다. CAD·규칙·생성 스크립트를 함께 수정했다.
- M12 슬립링 B+ fanout 지점 하나를 0.05 mm 이동해 폭 증가로 드러난 clearance 문제를 해결했다. 중심선 길이 skew 약 0.002 mm를 허용했다.
- 네 보드 DRC/미연결/parity, 어댑터 3종 ERC/pinmap/NC 검사와 geometry audit를 통과했다. 이 변경은 문서만의 패치가 아니다.
- 실제 quote에서 NP-155F, 적층 지정, **별도 임피던스 제어**, ENIG와 제조 파일 확인을 선택해 기록했다. 가까운 비아의 Plugged 예외 및 SMA 완성 두께 공차는 CAM 확인 조건으로 남겼다.
- 측정 알고리즘·표준 PCB·패널·부품 선정은 이번 변경 대상이 아니다. 아래의 기존 설계 의도는 유지한다. 제조 release나 구매 집행을 완료했다고 해석하지 않는다.

## 1. 목적과 사용자 요구

목적은 일반 케이블과 전용 핀맵의 100BASE-TX 케이블·커넥터·슬립링 조립체가 실제 산업 환경에 투입될 후보인지 **정적 전송 품질부터 평가**하는 것이다. 대상은 100 Ω 차동 두 pair의 100BASE-TX이며, 단일 pair Ethernet이나 모든 M12 Ethernet 규격을 포괄하는 설계는 아니다.

| 요구 | 설계에 반영한 내용 |
| --- | --- |
| LibreVNA와 balun 기반으로 측정 | 2-port VNA와 공통 SMA–ADT2-1T+–RJ45 PCB 사용 |
| 정상 RJ45 및 특이한 커넥터 조립체를 같은 장비로 측정 | RJ45 접속을 공통으로 하고 커넥터별 수동 어댑터 교체 |
| 길이가 있는 M12 몸체·손배선의 영향을 가능한 한 보정 | 최종 기준면을 어댑터 뒤 DUT 접속면에 설정 |
| 자작 thru의 완전한 S-parameter를 먼저 측정해야 하는 순환 문제 회피 | reciprocal thru와 대략적인 위상/극성을 사용하는 UnknownThru/SOLR |
| 결과를 반복 처리 | 표준 7개로 보정계수 저장, 이후 DUT 파일에 재사용 |
| JLCPCB 제작, 가능한 곳은 손납땜 | 4층 어댑터, M12/RJ45 THT 중심; 작은 Molex SMT는 reflow 선택지 |
| 산업 사용 가능성의 1차 판단 | DC/IL/RL/반복성/필요 시 crosstalk를 평가하고 PHY·동적·환경 시험으로 연결 |

이 요구와 아래의 구현 선택을 구분한다. **4층 구성, 특정 커넥터 MPN, 선폭/간격, 길이 보정 형상, shield 처리, 표준의 단순 모델은 검토·수정 가능한 설계안**이다. 사용자가 그 수치나 RF 성능을 확정했다는 뜻이 아니다.

## 2. 패치 범위와 이전 설계와의 차이

구현 패치는 [3b11656](https://github.com/ckh7488/balun_test/commit/3b11656c7db1514880bdfb173876c14c57d90c0c)이며, [직전 c9ee74f와의 비교](https://github.com/ckh7488/balun_test/compare/c9ee74f103a5f79e9ecf2f28fc48504b0bb64348...3b11656c7db1514880bdfb173876c14c57d90c0c)로 코드/CAD 변경을 볼 수 있다. 이 인계 문서를 추가하는 후속 패치는 문서 정합성 정리이며 회로·PCB·분석 알고리즘 변경을 포함하지 않는다.

| 항목 | 이전 방향 | 현재 방향 / 실제 변경 |
| --- | --- | --- |
| 지그 구성 | 커넥터마다 balun을 포함한 전용 PCB | 공통 RJ45 Rev B 유지 + 수동 어댑터 PCB 3종 추가 |
| 기준면 | SMA에서 보정한 fixture 포함 응답과 REF 비교 | SMA full SOLT 후 adapter-end UnknownThru 보정 |
| 자작 T | 이상적인 thru로 취급하면 모델 오차 발생 | 전체 S를 알려진 값으로 입력하지 않고 reciprocal 조건 사용 |
| O/S/L | SMA 보정 키트 중심 | SMA 표준과 별도로 DUT 접속면의 pair 간 표준 정의 |
| 데이터 처리 | SMA 기준 비교 계획 | Python 보정 저장/재사용, 100 Ω 결과와 provenance 출력 |
| 공통 RJ45 CAD | Rev B | 기존 회로/동박 유지, 검토와 현재 절차 설명 갱신 |
| 전용 balun CAD | `balun_slipring/`, `balun_llc16/` | 이력 자산으로 보존; 새 어댑터 CAD와 별개 |
| 구매·제조 산출물 | 여러 날짜의 수량·BOM·export 계획 | 최신 전체 발주 수량/BOM/Gerber 패키지는 아직 재작성하지 않음 |

**새 어댑터를 추가했다는 것과 발주 가능한 완성 세트를 만들었다는 것은 다른 상태다.** 보정 표준, 패널/브래킷, 최신 전체 수량표와 어댑터 제조 export는 남아 있다. 과거 주문의 집행·취소 여부도 이 패치에서 확인하거나 변경하지 않았다.

## 3. 어느 문서를 기준으로 읽을 것인가

| 범위 | 현재 기준 | 과거 자료의 사용 범위 |
| --- | --- | --- |
| 목적·설계 선택·남은 검토 | 이 문서, [루트 README](README.md) | 날짜가 붙은 이전 리뷰는 당시 상태 |
| 측정·기준면·표준 제작 개념 | [VNA_TEST_PLAN](VNA_TEST_PLAN.md) | 전용 지그의 `MEASUREMENT.md`는 이전 구성 설명 |
| 파일 형식·계산 동작 | [analysis/README](analysis/README.md), `analysis/m12_cal.py`, tests | 문서와 코드가 다르면 검토 finding으로 기록 |
| 공통 balun 보드 | [balun_eth_rj45/README](balun_eth_rj45/README.md), 같은 폴더의 Rev B CAD | [FAB_NOTES](balun_eth_rj45/JLCPCB_FAB_NOTES.md)는 해당 보드의 nominal 제작값 |
| 새 어댑터 | [adapters/README](adapters/README.md), 각 native KiCad 파일 | 기존 전용 balun 보드의 크기·실장면·BOM을 복사하지 않음 |
| 새 어댑터 제작 조건 | [adapters/JLCPCB_BUILD](adapters/JLCPCB_BUILD.md) | 루트 구매 문서는 이번 구성의 수량표가 아님 |
| 커넥터 핀맵 근거 | [PUBLIC_SOURCE_PROVENANCE](adapters/PUBLIC_SOURCE_PROVENANCE.md), [FOOTPRINT_SOURCES](adapters/FOOTPRINT_SOURCES.md) | 기존 공개 PINMAP/spec는 근거로 유지; 실물 확인은 별도 |
| 이전 설계/구매/export | [이력 자료 목록](docs/legacy/README.md) | 원문을 보존하며 현재 구성에 대한 자동 발주 지시로 사용하지 않음 |

각 문서의 역할을 구분하기 위한 표다. 기존 검사 결과나 CAD와 설명의 모순을 이 표만으로 덮지 말고, 실제 파일과 근거를 대조한다.

## 4. 측정 경계와 데이터 흐름

양쪽 fixture는 `coax 끝 → 공통 balun PCB → 짧고 고정된 shielded RJ45 patch → 수동 어댑터`다. 그 뒤가 DUT 접속면이다. 일반 RJ45 DUT는 어댑터 없이 공통 PCB의 RJ45 접속면에서 같은 절차를 수행한다. 양끝의 어댑터 종류가 달라도 된다.

**무엇을 DUT로 부를지 먼저 기록한다.** 목표가 케이블 전체이면 두 기준면 사이의 케이블 조립체를 측정한다. 특정 M12 체결부 자체의 성능을 보고 싶다면 그 체결부가 기준면 사이에 포함되도록 시험편을 구성해야 한다. 보정에 흡수된 어댑터 쪽 커넥터의 손실을 다시 DUT 커넥터 단독 손실이라고 부를 수 없다. 빈 암 Open과 플러그 S/L의 서로 다른 offset도 이 경계 정의와 연결된다.

| 단계 | 입력/행동 | 결과와 의미 |
| --- | --- | --- |
| 1 | LibreVNA 두 coax 끝에서 알려진 SMA 표준으로 full 2-port 50 Ω SOLT | 이후 취득 전체에 이 보정을 켜 둠 |
| 2 | 고정 fixture에서 p1 O/S/L, p2 O/S/L, 자작 T 취득 | **3 + 3 + 1 = 7개** SMA 기준 복소 Touchstone |
| 3 | `calibrate session.json --out cal.npz` | 표준 모델과 7개 파일로 반복 사용 가능한 계수 저장 |
| 4 | 같은 SMA 보정과 fixture에서 DUT 취득 | DUT 1개라면 총 취득 파일은 **3 + 3 + 1 + 1 = 8개** |
| 5 | `apply cal.npz dut.s2p --out …` | DUT 접속면 기준 100 Ω effective balanced `.s2p`, CSV, PNG, JSON |

LibreVNA GUI는 SMA 기준으로 남는다. Python의 보정 결과와 계수 파일은 저장되지만 LibreVNA에 두 번째 보정으로 자동 업로드하지 않는다. DUT는 계수 추정에 사용하지 않는다. 다른 DUT에도 계수를 재사용할 수 있으나 pair/포트 할당, adapter, patch/coax 상태, CT/shield/종단 상태 또는 첫 SMA 보정이 바뀌면 해당 구성의 7개 표준을 다시 취득한다.

## 5. 보정 구현에서 반드시 검토할 가정

### O/S/L과 T

Open은 빈 어댑터로 만들 수 있고, Short와 100 Ω Load는 mating 커넥터의 **pair 두 핀 사이**에 구성한다. 짧은 S/L 배선도 R/L/C와 전기적 offset을 가진다. 보정 표준의 자체 S-parameter를 무시하는 것이 아니라, **간단한 물리 모델로 근사하고 그 근사가 용도에 충분한지 검증**하는 접근이다. 표준의 전체 S를 다른 VNA로 반드시 먼저 측정해야 한다는 요구는 없다.

현재 모델은 Open의 shunt C, Short의 series R/L, Load의 series R/L와 shunt C, 종단 앞 lossless offset line을 지원한다. 초기 ideal O/S/100 Ω L 설정은 실물 검증 결과가 아니다. 보정에 사용한 표준을 다시 이상적인 값으로 만드는 것만으로는 정확도가 입증되지 않는다. 독립 저항/선로, 반복 체결, R/L/C/offset 민감도 비교가 필요하다.

UnknownThru는 상호성 `S21 = S12`와 충분한 전달을 전제로 한다. 알고리즘의 180° 떨어진 두 전달 해를 선택하려면 실제 P/N 극성과 대략적인 편도 지연이 필요하다. 예상 위상 오차를 대역 전체에서 90°보다 충분히 작게 유지하는 짧은 T가 출발점이다. **T의 정확한 손실·반사 전체를 알고 있어야 하는 일반 SOLT와 구분한다.**

### 임피던스와 error box

- 입력 파일은 SMA 보정된 50 Ω 데이터다. Port 2 표준은 S22를 사용한다. `.s1p`의 실제 취득 포트나 SMA 보정 활성 여부는 파일만으로 확정할 수 없다.
- scikit-rf 계산에서 measured/ideal의 numerical reference를 50 Ω으로 일치시킨다. 이 단계의 실제 100 Ω Load 모델은 `Γ = (100−50)/(100+50) = 1/3`이다.
- 보정 후 DUT를 `Network.renormalize(100)`으로 변환한다. 원본 Touchstone의 `R 50`을 `R 100`으로 바꾸는 방식은 아니다.
- 첫 full 2-port SMA SOLT가 switching/source/load match를 보정했다는 전제에서, 두 번째 단계는 고정 fixture 두 error box와 **zero switch terms**를 사용한다. 첫 보정의 잔차까지 없어지는 것은 아니다. LibreVNA raw 데이터에 곧바로 이 가정을 적용하지 않는다.
- 별도 취득한 양쪽 O/S/L을 diagonal reflective two-port로 합치는 구현은 표준 측정 사이의 추가 coupling을 무시한다. fixture 사이 직접 누설, 다른 pair 및 common mode와의 강한 결합은 모델의 적용성 문제다.
- 모델화 가능한 안정된 mismatch/loss/delay는 보정할 수 있어도 손실로 낮아진 SNR, 형상 변화, mode conversion이나 누설이 자동 복구되지는 않는다. 결과는 full mixed-mode 측정이 아니다.

수학과 적용성은 [scikit-rf UnknownThru](https://scikit-rf.readthedocs.io/en/latest/api/calibration/generated/skrf.calibration.calibration.UnknownThru.html), [검증 버전 1.8.0 소스](https://github.com/scikit-rf/scikit-rf/blob/v1.8.0/skrf/calibration/calibration.py), [LibreVNA calibration 구현](https://github.com/jankae/LibreVNA/blob/master/Software/PC_Application/LibreVNA-GUI/Calibration/calibration.cpp)과 대조한다. 코드의 수치적 zero guard는 실측 정확도나 불확도 보증 범위가 아니다.

## 6. PCB 설계 선택과 검토 지점

| 선택 | 목적 | 남은 검토 |
| --- | --- | --- |
| 기존 공통 RJ45 Rev B 재사용 | balun 설계를 공유하고 커넥터별 변경 비용 감소 | 실제 balun 대역·손실·balance·fixture coupling |
| RJ45 jack + 공장제 patch | 손제작 plug보다 연결/고정 방식 반복 가능 | 추가 접점·patch 손실과 재체결 변화; 표준/DUT 취득 시 고정 |
| 수동 어댑터 3종, 고정 핀맵 | 움직이는 untwist를 PCB 형상으로 고정, 설정 착오 감소 | PCB용 M12와 보유 커넥터 호환; 범용 M12 핀맵으로 오해 금지 |
| 66 × 40 mm, 4층, A/B 외층 분리 | 반복 가능한 배선과 각 신호층의 인접 reference plane | 더 작은 보드/짧은 fanout의 장점과 조립 공간 비교 |
| L2/L3 SHIELD, TP1 body/패널 접속점 | shield 경계 설정 가능 | common balun GND plane과 동일 조건이 아님; floating/bonded 조건과 접점 모델 |
| W 0.234 / gap 0.216 mm trunk | 공식 JLC 역산 결과를 반영한 100Ω 목표 치수 | 생산 CAM/coupon; escape/fanout은 목표 보장 범위 밖 |
| P/N track 합계 길이 일치 | 배선 skew 감소 의도 | 커넥터 내부 길이·via·실제 전기적 대칭까지 보장하지 않음 |
| M12 THT + 패널 지지 | 손납땜 접근성과 체결 하중 분리 | 부품 높이, PG9 panel, nut 접근, standoff, hole 공차 |
| Molex 1.25 mm SMT | 기존 공개 케이블 후보와 연결 | 실제 mating과 pin 1, 납땜 접근성; reflow 권장 선택지 |

**fanout은 우선 검토 항목이다.** 현재 길이 보정에 넓게 벌어진 절선이 있으며, 특히 M12 LLC의 pair A에서 “track 길이 동일”을 얻는 대신 pair 간격과 loop가 커질 수 있다. 이 형태가 작은 skew를 허용한 더 짧고 밀접한 배선보다 낫다고 검증하지 않았다. 기존 CAD를 방어하기보다 uncoupled 길이·loop·plane에 대한 대칭을 함께 비교해 수정안을 제시한다. 현재 DRC와 길이 표만으로 mode conversion이나 100 Ω을 입증하지 않는다.

기본 CT-FLOAT 및 한쪽 shield bond는 초기 시험 조건이다. 새 어댑터 내층, patch shield, M12 body/패널을 포함한 실제 경계를 명시해야 한다. “SHIELD라는 net 이름이 있으므로 적절히 접지된다”거나 “기준면 보정이므로 shield 상태는 무관하다”는 해석은 부정확하다.

## 7. 완료한 검증과 아직 없는 증거

아래는 구현 당시와 후속 임피던스 패치의 검증 범위다. 공식 계산기와 CAD 검사를 수행했으며 실물 RF 검증은 추가하지 않았다.

| 영역 | 증거 | 입증하지 않는 것 |
| --- | --- | --- |
| Python | `tests/test_m12_cal.py` **7 cases 통과**, scikit-rf 1.8.0 | 실측 LibreVNA/표준 정확도 |
| 합성 회복 | 비대칭·손실·부정합 fixture, 50↔100 Ω 변환, nonideal OSL, unknown reciprocal T, 극성 ±, 저장 계수 재사용 | 실제 mode conversion·coupling이 two-error-box로 충분한지 |
| 입력/출력 | p2 S22 추출, 주파수/reference 불일치 거부, 원본 보존, 출력 형식 | 잘못 기록된 하드웨어 상태의 자동 탐지 |
| 기존 공통 지그 | [fixture_drc.json](adapters/fixture_drc.json): DRC/미연결/parity 0 | 회로 변경이나 실물 성능 승인 |
| 어댑터 3종 | [verification.json](adapters/verification.json): native DRC/ERC/parity 0, 결선/NC 확인, CAD SHA-256 | 제조사 도면의 해석·실물 mating·최종 임피던스 |
| 육안 CAD 검토 | 각 어댑터 layout/plane SVG와 native 회로도 | EM 해석 또는 제조 샘플 검증 |

DRC 0은 저장된 검사 설정에서의 결과다. 각 `drc.json`의 `ignored_checks`도 함께 검토한다. SHA-256은 검사한 파일과의 일치 확인용이며, 별도 제3자 인증이나 전자서명을 의미하지 않는다.

아직 없는 산출물은 **전용 O/S/L/T 표준 PCB, 실제 표준 모델의 측정/추정 근거, 불확도 예산, 실측 DUT 결과, JLC 생산 CAM/coupon, 패널 제작 도면, 새 구성의 통합 구매 수량표와 어댑터 제조 release**다. 기존 `export_jlc_release.ps1`는 새 `adapters/`를 export하지 않는다.

## 8. 다른 검토자에게 요청할 작업

| 우선순위 | 검토 질문 | 원하는 결과 |
| --- | --- | --- |
| 1 | 첫 full SMA SOLT 이후의 8-term/zero-switch-term 가정과 50→100 Ω 처리가 타당한가? | 코드/원문 근거, 독립 계산 또는 재현 예제; 적용 범위와 반례 |
| 1 | 실제 평가하려는 커넥터가 DUT 경계 안에 들어가는가? 빈 Open과 mating S/L의 offset을 정의할 수 있는가? | 접속면·표준의 치수/모델 정의와 필요한 변경 |
| 1 | 기존 공개 핀맵이 PCB로 정확히 전사되고 NC가 유지되는가? 실장면/성별/key/mating이 맞는가? | 제조사 도면·CAD 위치와 대조한 finding; 실물 필요 항목 구분 |
| 2 | fanout, loop, plane, CT/shield, signal/return via가 balance와 재현성에 적합한가? | 단순 길이 일치보다 유리한 구체적 배선 수정안 |
| 2 | JLC nominal geometry와 손납땜/기구 설계가 실제 제작 가능한가? | 확인된 값과 미확인 값 분리; 필요한 stack/부품/패널 수정 |
| 2 | 실물 OSL/T를 어떤 방식으로 만들고 어느 정확도까지 주장할 수 있는가? | 간단한 제작안, 독립 check와 모델 민감도 시험; 필요 시 표준 PCB 설계 |
| 3 | 초기 1–100 MHz 정적 측정으로 목적에 필요한 결함을 찾을 수 있는가? | 최소 실측 순서, 정상 REF 비교, 반복성/누설 floor, 이후 PHY 시험 연결 |

finding은 **영향도 → 파일/위치 또는 출처 → 재현/계산 근거 → 수정 제안 → 확인이 필요한 항목** 순서로 작성한다. 확인된 오류와 설계상 추정/실물 미확인을 구분한다. 현재 구현도 검토 대상이며, DRC 통과나 이 문서의 결론 자체를 타당성의 근거로 삼지 않는다.

수정안을 제시할 때는 목적과 기준면을 유지하면서 어떤 가정을 바꾸는지 설명한다. 대안으로 SMA-only 비교나 다른 calibration을 제안할 수 있으나, 그 경우 DUT 경계/남는 fixture 오차/필요한 추가 장비와 표준을 함께 설명한다. 사용자에게 자작 T의 전체 S를 이미 알고 오라고 요구하는 것으로 해결을 대신하지 않는다.

## 9. 재현과 다음 실측 단계

저장소 루트에서 Python 3.10 이상으로 실행한다. 상세 CLI 예시는 [analysis/README](analysis/README.md)를 따른다.

```bash
python -m pip install -r requirements-analysis.txt pytest
python -m pytest tests/test_m12_cal.py -q
python -m analysis.synthetic_demo measurements/review_demo
python -m analysis.m12_cal calibrate measurements/review_demo/session.json --out measurements/review_demo/cal.npz
python -m analysis.m12_cal apply measurements/review_demo/cal.npz measurements/review_demo/dut.s2p --out results/review_demo
```

출력은 예제의 `expected_dut_100ohm.s2p`와 비교한다. 도구는 기존 파일을 덮어쓰지 않으므로 재실행 때 새 출력 경로를 사용한다.

KiCad 검증은 **검토용 별도 checkout**에서 KiCad 10.0.6과 필요한 라이브러리를 사용한다. 아래 스크립트는 zone refill/save와 보고서·SVG 갱신을 수행하므로 읽기 전용 검사가 아니다.

```bash
python adapters/verify_adapters.py --kicad-cli /path/to/kicad-cli
```

최초 실측은 조립체 continuity/각 선 저항 확인, full SMA SOLT, 한 pair의 O/S/L/T 취득, 독립 check standard, 정상 REF와 DUT, 반복 체결, 표준 모델 민감도 순서로 진행한다. 1–100 MHz를 시작 대역으로 쓰되 정확도와 판정 기준은 실제 check/floor/용도에 따라 정한다. NEXT/FEXT는 별도 포트 조합의 보정과 누설 바닥값이 필요하다.

이후의 완료 기준은 “그래프가 나온다”가 아니라 **DUT 차이가 반복성·표준 모델 변화·fixture floor보다 충분히 구분되고, 그 판단 범위를 기록할 수 있는가**다. VNA 정적 결과만으로 산업 환경의 EMC, 회전 중 순간단선, 온도/진동, PHY 오류율이나 장기 수명을 판정하지 않는다.
