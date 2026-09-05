# 공통 RJ45 balun 지그 검토 — 2026-09-05

결론: **현재 RJ45 Rev B를 공통 플랫폼으로 사용하는 것이 적합한 출발점이다.** 새 측정 방향은 지그 이후 기준면 보정을 추가하는 변경이며, 이를 위해 balun PCB 회로를 새로 설계할 필요는 없다. 커넥터별 전용 balun PCB 대신 수동 어댑터 PCB를 교체한다.

## 실제 CAD에서 확인한 것

KiCad 10.0.6으로 기존 `balun_eth_rj45.kicad_pcb`를 검사했다. 표준 라이브러리를 연결한 환경에서 **DRC 0, 미연결 0, 회로도 parity 0**이다. 이 검토로 기존 PCB copper나 회로도 net을 변경하지 않았다.

| Pair | P / N track 길이 | P / N signal via |
| --- | ---: | ---: |
| A | 44.9649 / 44.9649 mm | 0 / 0 |
| B | 32.9301 / 32.9301 mm | 1 / 1 |
| C | 32.8357 / 32.8357 mm | 0 / 0 |
| D | 43.6677 / 43.6677 mm | 0 / 0 |

- 내층 In1/In2는 실제 fill이 저장된 GND plane이다. pair 아래 기준면을 두는 구조다.
- differential track은 0.23 mm trunk와 0.15 mm RJ45 escape로 구성된다. 0.15 mm 구간을 100 Ω 전송선으로 간주하지 않는다.
- ADT2-1T+의 nominal 1:2 impedance ratio는 50 Ω SMA와 100 Ω differential의 연결 목적에 맞는다.
- dot은 primary 3 / secondary 6이며 기존 P=4, N=6이므로 지그 한 장의 명명상 극성 반전을 기억해야 한다. 자작 thru 모델은 실제 DUT 접속면 P/N 정의로 정한다.
- 미사용 SMA 6개에 연결할 외부 50 Ω load는 계속 필요하다. 이 load는 커넥터 끝 OSL의 100 Ω 표준과 별개다.

## 측정상 한계와 대응

| 한계 | 이번 방향에서의 대응 |
| --- | --- |
| 두 balun·PCB·adapter 손실/부정합 | 고정한 상태에서 adapter-end OSL + UnknownThru로 보정 |
| 수작업 fanout/untwist 변화 | PCB 어댑터와 짧은 고정 patch cable로 재현성 개선 |
| balun 대역·손실·noise | 1–100 MHz부터 검증, 100–200 MHz 확장 관찰; 깊은 notch/낮은 전달은 주의하여 해석 |
| pair 간 fixture coupling | 각 crosstalk 연결의 floor와 반복성 측정; 단순 two-error-box 보정으로 제거된다고 가정하지 않음 |
| common mode / balance | CT/shield 상태 고정; full mixed-mode 또는 산업 EMI 적합성은 별도 시험 |
| 반복 체결·온도 drift | 독립 check standard와 재체결 기록; 유의 변화 시 재보정 |
| JLC nominal geometry | manufacturer solver/coupon 확인 후 최종 임피던스 승인 |

따라서 **PCB 어댑터 + 임피던스 제어는 권장하지만 SOLR가 모든 오차를 없애는 것은 아니다.** PCB 길이를 무조건 짧게 하는 것보다 대칭성·고정 형상·기준면·표준 모델을 함께 관리한다. 커넥터 몸체와 pad field의 mode conversion, OSL 기생성분 정확도는 실측에서 검증해야 한다.

## 이번에 만든 어댑터의 검사 범위

세 보드의 native DRC/ERC/parity, 정확한 pair 결선과 power/NC 핀 분리를 확인했다. 저장된 CAD hash와 검사 결과는 [verification.json](verification.json)에 있다. 각 보드의 inner SHIELD plane fill과 레이어/회로도 SVG를 생성했다.

이것은 CAD 검증이다. 아직 실제 JLC 제작품, PCB용 M12의 사내 케이블 체결, 실제 표준과 DUT 데이터는 없다. 임피던스 정밀도나 industrial-use PASS/FAIL을 이 단계에서 단정하지 않는다.

근거: [ADT2-1T+ datasheet](https://www.minicircuits.com/pdfs/ADT2-1T%2B.pdf), [JLC stack-up](https://jlcpcb.com/impedance), 저장소의 KiCad 설계와 위 검사 결과.
