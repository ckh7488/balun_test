# Slip-ring comparison measurement worksheet

상태: `DRAFT` — 이 문서는 핀맵과 기준 연결물이 확정될 때 채워야 할 측정 기록 골격이다.

## 기준면과 비교 방식

- LibreVNA의 coax cable 끝에서 각 포트의 SOLT를 수행한다.
- 이 SOLT로 기준면이 Molex/M12 접점까지 이동하는 것은 아니다. 두 balun 보드, 커넥터와 fan-out은 fixture로 남는다.
- 먼저 두 지그 사이에 `REF/bypass`를 연결해 기준값을 저장하고, 같은 지그·케이블·설정에서 이를 슬립링으로 교체해 차이를 비교한다.
- 절대 differential S-parameter가 필요하면 별도로 검증한 2×thru/de-embedding 절차가 필요하다.

## REF/bypass 확정표

| 항목 | 값 |
| --- | --- |
| Molex 상대 커넥터 MPN | TBD |
| M12 female MPN/suffix | TBD |
| 총 연결 길이 | TBD mm |
| Pair A 핀/선재/꼬임 | TBD |
| Pair B 핀/선재/꼬임 | TBD |
| shield/drain 처리 | TBD |
| 제작물 식별번호 | TBD |

REF는 슬립링과 같은 양끝 커넥터 조합을 사용하되, 가운데는 알려진 짧은 100 Ω twisted pair로 직접 연결한다. 핀맵과 커넥터가 확정되기 전에는 REF도 제작하지 않는다.

## LibreVNA 공통 설정

| 항목 | 값 |
| --- | --- |
| 주파수 시작/끝 | TBD |
| point 수 | TBD |
| IFBW | TBD |
| source power | TBD dBm |
| averaging | TBD |
| calibration kit / calibration 파일 | TBD |
| coax cable 식별번호 | TBD |
| 외부 50 Ω terminator 식별번호 | TBD |

한 번 정한 설정은 REF, 정지 위치별 DUT와 회전 중 DUT 측정에 동일하게 적용한다.

## 2-port 연결표

| 측정 | VNA Port 1 | VNA Port 2 | 나머지 SMA | 주요 결과 |
| --- | --- | --- | --- | --- |
| Pair A 전송/반사 | Molex Pair A | M12 Pair A | Pair B 양끝 50 Ω | S11, S22, S21, phase/group delay |
| Pair B 전송/반사 | Molex Pair B | M12 Pair B | Pair A 양끝 50 Ω | S11, S22, S21, phase/group delay |
| A→B near-end crosstalk | 같은 쪽 Pair A | 같은 쪽 Pair B | 반대쪽 A/B 50 Ω | S21; 연결 방향 기록 |
| A→B far-end crosstalk | 한쪽 Pair A | 반대쪽 Pair B | 나머지 두 SMA 50 Ω | S21; 연결 방향 기록 |
| B→A near/far-end | 위 두 행에서 A/B 교환 |  | 모든 미사용 SMA 50 Ω | 방향 비대칭 확인 |

`NEXT/FEXT`라는 이름만 기록하지 말고 Port 1/2가 어느 보드의 어느 pair였는지 함께 기록한다. 2-port VNA이므로 조합을 순차 측정한다.

## 위치와 파일 이름

권장 파일명:

```text
YYYYMMDD_<REF|DUT>_<A|B|AtoB|BtoA>_<ILRL|NEXT|FEXT>_<000|090|180|270|ROT>deg_<run>.s2p
```

각 측정 세트에서 다음을 남긴다.

- REF/bypass
- DUT 0°, 90°, 180°, 270° 정지 상태
- 가능한 경우 저속 회전 중 반복 sweep
- RCT1/RCT2 조립 상태
- 미사용 SMA 네 곳의 종단 상태
- M12 체결 토크 또는 체결 상태
- 이상이 나타난 각도와 반복 가능 여부

## 완료 조건

- [`PINMAP.md`](PINMAP.md)의 continuity 및 pair 표 완료
- REF의 실제 MPN·길이·배선·사진 기록
- 모든 미사용 SMA에 50 Ω 종단
- calibration과 sweep 설정 저장
- REF와 DUT 파일이 동일 설정임을 확인
- 원본 Touchstone 파일은 수정하지 않고 별도 분석본을 생성
