# LibreVNA balun Ethernet 측정

산업용 100BASE-TX 케이블·커넥터·슬립링의 **정적 전송 품질을 먼저 평가**하기 위한 프로젝트다. 일반 RJ45 케이블과 사내 전용 핀맵의 케이블을 같은 플랫폼에서 측정한다.

## 현재 기본 구성

양쪽에 `LibreVNA coax → SMA–balun–RJ45 PCB → 고정 RJ45 연결 → 교체형 커넥터 어댑터 → DUT`를 사용한다. 일반 RJ45 DUT는 어댑터 없이 연결한다. 최종 보정 기준면은 **어댑터 뒤의 DUT 접속면**이다. M12와 Molex 조합처럼 양끝 커넥터가 달라도 같은 원리를 사용한다.

1. LibreVNA에서 두 coax 끝의 **50 Ω full 2-port SOLT**를 수행하고 계속 활성화한다.
2. 지그와 어댑터를 고정하고 양쪽 DUT 접속면에서 O/S/L 각 3개와 자작 reciprocal thru 1개를 **측정·저장**한다.
3. Python `UnknownThru`가 이 **7개 표준 데이터**로 커넥터 끝 보정계수를 만든다.
4. 같은 SMA 보정 상태로 측정한 DUT `.s2p`에 저장된 계수를 적용한다. 결과는 **100 Ω balanced effective two-port** `.s2p`, CSV, 그래프다.

LibreVNA 화면은 SMA 기준으로 남는다. 자작 thru를 이상적인 0 ps thru로 등록해 LibreVNA에서 두 번째 SOLT를 켜는 절차가 아니다. 보정에 DUT 파일을 포함하지 않는다.

## 읽는 순서

| 문서/경로 | 내용 |
| --- | --- |
| [VNA_TEST_PLAN.md](VNA_TEST_PLAN.md) | 목적, 기준면, 표준 제작, 측정·검증 순서 |
| [analysis/README.md](analysis/README.md) | 설치, 3+3+1 파일 입력, 보정 저장과 DUT 처리 |
| [balun_eth_rj45](balun_eth_rj45/README.md) | 공통 SMA–RJ45 balun PCB |
| [adapters](adapters/README.md) | JLCPCB용 교체형 어댑터와 지그 검토 |
| [docs/legacy](docs/legacy/README.md) | 종전 SMA 기준 비교 계획; 변경 이력용 |

`balun_slipring/`과 `balun_llc16/`의 커넥터 전용 balun PCB는 기존 설계 자산이다. 현재 기본안은 **공통 RJ45 balun PCB + 커넥터별 수동 어댑터 PCB**이며, 기존 PCBA 10장 구매 문서는 이 기본안의 최신 발주 수량표가 아니다. 기존 설계·BOM을 삭제하거나 이미 주문한 물량을 취소한 것은 아니다.

## 결과의 의미

OSL의 모델 오차, 재체결 변화, 지그 간 누설과 mode conversion은 남는다. 소프트웨어의 합성 데이터 검증은 실제 커넥터 정확도 검증과 구분한다. 보정된 IL/RL이 좋아도 산업 환경의 EMC·회전 중 순간단선·장기 수명을 보장하지 않는다. 먼저 실제 길이의 수동 조립체를 평가하고, 이후 동작·환경 시험으로 이어간다.

실측 데이터와 결과는 기본적으로 `measurements/`, `results/`에 두며 Git에서 제외한다. 이 공개 저장소에는 코드와 설계·절차를 관리한다.
