# M12 / 커넥터 끝 UnknownThru 보정 도구

대상: **LibreVNA full 2-port SMA SOLT가 이미 적용된** complex Touchstone. raw 측정, 포트별 SOL만 적용한 측정, 크기만 저장한 CSV에는 사용하지 않는다. 이름은 `m12_cal`이지만 양끝이 M12/RJ45/Molex인 경우도 해당 접속면의 표준과 핀맵을 정의하면 같은 방식이다.

## 설치

저장소 루트에서 실행한다. Python 3.10 이상을 사용한다.

```bash
python -m venv .venv
# Windows PowerShell: .venv\Scripts\Activate.ps1
# Linux/macOS: source .venv/bin/activate
python -m pip install -r requirements-analysis.txt
```

## 입력: 3 + 3 + 1, DUT는 별도

하나의 고정된 VNA 포트/지그/어댑터/차동 pair 조합마다 한 세트를 만든다.

| 기본 파일명 | 내용 |
| --- | --- |
| `p1_open.s1p`, `p1_short.s1p`, `p1_load.s1p` | Port 1에서 본 세 표준의 S11 |
| `p2_open.s1p`, `p2_short.s1p`, `p2_load.s1p` | Port 2에서 본 세 표준의 **S22를 단일 포트로 내보낸 값** |
| `thru.s2p` | 양 어댑터 사이 자작 thru의 S11/S21/S12/S22 |
| `dut_001.s2p` 등 | 같은 SMA 보정 상태의 DUT; 보정계수 생성에 사용하지 않음 |

Port 2의 잘못된 S11 내보내기를 피하려면 O/S/L도 `.s2p`로 저장하고 설정의 파일명을 바꿔도 된다. 코드는 `p1`에서는 S11, `p2`에서는 S22를 추출한다. 단일 `.s1p` 안에는 원래 어느 포트에서 왔는지 표준화된 정보가 없으므로 사용자가 확인해야 한다.

모든 파일은 같은 주파수 grid와 50 Ω SMA reference를 유지한다. 자동 보간하지 않는다. RI, MA, DB 형식은 Touchstone이 지원하는 복소 표현이면 읽을 수 있다. LibreVNA에서 보정을 켠 채 내보냈는지는 파일만으로 증명할 수 없으므로 세션 기록에 남긴다.

## 사용

```bash
python -m analysis.m12_cal init measurements/run01/session.json
```

생성된 `session.json` 옆에 일곱 표준 파일을 놓는다. `setup_id`, `reference_planes`, 표준 모델과 thru 극성/지연, 실제 핀 번호, 지그·어댑터·coax·load ID, CT/shield 상태, sweep 설정, SMA calibration ID를 기록한다. 파일 경로는 **설정 파일 위치 기준**이다.

```bash
python -m analysis.m12_cal calibrate measurements/run01/session.json --out measurements/run01/cal.npz
python -m analysis.m12_cal apply measurements/run01/cal.npz measurements/run01/dut_001.s2p --out results/run01
python -m analysis.m12_cal apply measurements/run01/cal.npz measurements/run01/dut_002.s2p measurements/run01/dut_003.s2p --out results/run01
```

출력 파일명은 `dut_001_m12.s2p/.csv/.png/.json`이다. 입력 원본은 수정하지 않으며 기존 결과와 보정 파일을 덮어쓰지 않는다. `.npz`에는 주파수·복소 보정계수·설정·표준 파일 SHA-256이 포함된다. pickle을 사용하지 않는다.

| 출력 | 의미 |
| --- | --- |
| `.s2p` | 최종 접속면에서 100 Ω으로 환산한 balanced effective two-port |
| `.csv` | RL1/RL2, IL21/IL12, 전달 위상, group delay, complex reciprocity 차이 |
| `.png` | 주파수별 IL/RL/위상/지연 |
| `.json` | 모델·세션·파일 hash, passivity 진단용 최대 singular value, 한계 |

IL/RL은 양의 loss 부호다. group delay/위상은 전달이 noise floor에 가까우면 의미가 약하다. 최대 singular value가 1을 넘는 현상은 수동 DUT에서 보정·노이즈·모델 문제를 조사할 단서다. 코드는 합격/불합격이나 절대 정확도를 자동 판정하지 않는다.

## O/S/L 모델

초기 설정은 이상적인 Open, Short, 100 Ω Load다. **실물 표준이 이상적이라는 검증 결과가 아니다.** 실제 제작에 맞는 추정·모델이 있으면 포트별로 독립 수정한다.

| 표준 | 설정 | 모델 |
| --- | --- | --- |
| Open | `capacitance_pf` | pair 사이 병렬 C |
| Short | `resistance_ohm`, `inductance_nh` | 직렬 R+L |
| Load | `resistance_ohm`, `inductance_nh`, `capacitance_pf` | 직렬 R+L 전체에 병렬 C |
| 공통 | `offset_delay_ns`, `offset_z0_ohm` | 종단 앞 lossless 선로의 **편도** 지연과 차동 특성 임피던스; 기본 0 ns, 100 Ω |

M12 수 플러그의 핀과 배선이 만드는 길이는 offset/기생성분의 일부다. 빈 암 커넥터 Open과 수 커넥터 Short/Load를 모두 지연 0으로 가정하면 그 차이가 오차로 남는다. 여기의 lumped/단일 선로 모델은 복잡한 커넥터 모드 변환을 표현하지 못한다.

표준을 보정한 결과가 정확히 이상적으로 보이는 것은 **그 모델을 강제한 결과**다. 모델 검증에는 다른 저항(예: 별도 제작 150 Ω), 다른 짧은 선로, 재체결 반복과 모델 민감도 비교를 사용한다. 예시 수치를 실제 M12의 측정값으로 취급하지 않는다.

## 자작 thru

필요한 것은 reciprocal 연결과 대략적인 전달 위상/극성이다. 완전한 S-parameter 파일을 미리 알 필요가 없다. 두 핀쌍의 P→P/N→N을 기준으로 `polarity=1`, 한쪽이 교차되면 `-1`이다. `delay_ns`에는 대략적인 **편도** 지연을 넣는다. 두 해의 전달 위상은 180° 차이이므로 예상 위상 오차를 각 주파수에서 90°보다 충분히 작게 유지한다. 길이가 짧고 극성이 확인된 thru가 실용적이다.

UnknownThru는 비상호 thru나 추가적인 mode conversion을 해결하지 못한다. 잘못된 극성으로도 그럴듯한 IL/RL이 나올 수 있으며, 결과 그래프만으로 올바른 부호를 자동 보장할 수 없다.

## 50 Ω / 100 Ω 처리와 switch terms

scikit-rf는 measured/ideal의 z0 일치를 요구한다. 따라서 보정 계산 자체를 **50 Ω 기준으로 일관되게** 수행한다. 균형 포트의 실제 100 Ω Load 모델은 이 단계에서 `Γ=(100−50)/(100+50)=1/3`이다. 보정된 DUT를 얻은 다음 `Network.renormalize(100)`으로 파동 기준을 변환한다. 원본의 `R 50`을 `R 100`으로 바꾸거나 보정 전에 입력을 임의 환산하지 않는다.

SMA의 첫 full SOLT가 장비의 source/load match와 switching 효과를 보정했다는 전제에서 두 번째 단계는 고정 fixture 두 error box만 추정하고 switch terms를 0으로 둔다. LibreVNA raw 데이터의 switch terms를 0이라고 가정하는 방식이 아니다. 초기 보정 잔차, fixture 간 직접 누설, 다른 pair와의 결합·공통모드 경로는 이 단순 모델 밖이다.

## 합성 데이터로 실행 확인

```bash
python -m analysis.synthetic_demo measurements/synthetic
python -m analysis.m12_cal calibrate measurements/synthetic/session.json --out measurements/synthetic/cal.npz
python -m analysis.m12_cal apply measurements/synthetic/cal.npz measurements/synthetic/dut.s2p --out results/synthetic
python -m pip install pytest
python -m pytest tests/test_m12_cal.py -q
```

합성 예제는 비대칭·손실·부정합 fixture, 50↔100 Ω 변환, 서로 다른 OSL 기생성분과 부정합 thru를 포함한다. `expected_dut_100ohm.s2p`가 정답이다. 이 검증은 파일 입출력·수학·기준 임피던스 처리를 확인하며 실측 정확도를 인증하지 않는다.

## 구현 근거

- [scikit-rf UnknownThru](https://scikit-rf.readthedocs.io/en/latest/api/calibration/generated/skrf.calibration.calibration.UnknownThru.html)
- [검증한 scikit-rf 1.8.0 소스](https://github.com/scikit-rf/scikit-rf/blob/v1.8.0/skrf/calibration/calibration.py)
- [LibreVNA calibration 구현](https://github.com/jankae/LibreVNA/blob/master/Software/PC_Application/LibreVNA-GUI/Calibration/calibration.cpp)
- [Keysight calibration standard 모델 설명](https://helpfiles.keysight.com/csg/e5080a/s3_cals/calibration_standards.htm)
