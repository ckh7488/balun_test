# 기존 BALUN 회로도 가독성 정리

2026-09-03, 기존 세 회로도의 **표현만 정리**했다. 부품 선정, 핀맵, 조립 상태, PCB 배선 및 제조 승인 상태를 변경하는 작업이 아니다.

## 결과 파일

| 지그 | 편집 가능한 KiCad 원본 | 확인용 PDF | 용지 |
| --- | --- | --- | --- |
| RJ45 4-pair | [회로도](balun_eth_rj45/balun_eth_rj45.kicad_sch) | [PDF](../output/pdf/balun_eth_rj45_schematic.pdf) | A3 가로, 1쪽 |
| 슬립링 Molex측 | [회로도](balun_slipring/molex_end/balun_slipring_molex.kicad_sch) | [PDF](../output/pdf/balun_slipring_molex_schematic.pdf) | A4 가로, 1쪽 |
| 슬립링 M12측 | [회로도](balun_slipring/m12_end/balun_slipring_m12.kicad_sch) | [PDF](../output/pdf/balun_slipring_m12_schematic.pdf) | A4 가로, 1쪽 |

- RF 경로는 SMA -> balun -> 차동 pair 순서로 정렬했다. 같은 이름의 네트 라벨은 서로 전기적으로 연결된다.
- 커넥터의 논리 핀 번호, 슬립링 양단 핀맵, CT 미실장 조건, 차폐 옵션과 외부 종단 주의사항을 별도 영역으로 나눴다.
- 기존 `ETH100` / `RF50`의 `schematic_color` 알파값이 `0.000`이라 PDF에서 해당 선과 라벨이 투명해졌다. 각 프로젝트에서 이 두 표시값만 `1.000`으로 수정했다. 기존 RGB와 `pcb_color`, 임피던스 관련 선폭/간격, netclass 배정 및 모든 PCB 설정은 유지했다.
- symbol/pin UUID, 모든 부품 속성값, MPN, footprint, FIT/DNP, BOM/position-file 포함 여부와 정확한 네트 이름 및 핀 연결을 보존했다. 도면의 배치, 표시 글자, 주석, 날짜 및 용지 크기는 달라졌다.
- LLC 회로도와 PCB 파일은 수정하지 않았다. 슬립링 생성기는 새 배치를 사용하도록 연결하고, RF 원본의 배치에 의존하지 않도록 수정했다.

## 검증

| 지그 | 부품 / 네트 | ERC 오류·경고 | DRC / 미연결 / 회로도-PCB 불일치 |
| --- | --- | --- | --- |
| RJ45 | 17 / 22 | 0 / 0 | 0 / 0 / 0 |
| 슬립링 Molex | 7 / 12 | 0 / 0 | 0 / 0 / 0 |
| 슬립링 M12 | 7 / 15 | 0 / 0 | 0 / 0 / 0 |

KiCad 10 네이티브 XML netlist의 부품 정보와 네트/핀 목록을 변경 전후 정확히 비교했다. 실제 반영 파일도 다시 검사했다. DRC는 `--refill-zones --schematic-parity`로 실행하되 `--save-board` 없이 수행했으며, `.kicad_pcb`와 `.kicad_dru`의 SHA-256은 원본과 같다. 프로젝트 JSON은 위의 표시 색상 두 필드만 다르다.

새 RJ45 회로도를 원본으로 슬립링 두 회로도 및 LLC 회로도를 별도 검증 폴더에 재생성해 기존 연결과 부품 정보가 유지되는지 확인했다. LLC의 M12 핀맵, 전원 핀 NC, 커넥터 필수 FIT와 CT DNP 검사도 통과했다. PDF 세 장은 이미지로 렌더링해 배선·라벨 표시, 글자 겹침 및 잘림을 확인했다.

원본 백업과 검증 보고서는 [`../outputs/balun-schematic-refresh-20260903/`](../outputs/balun-schematic-refresh-20260903/)에 있다. 각 프로젝트의 `before/`가 수정 전 CAD 백업이며, `verification.json`과 `regression.json`에 검사 결과를 기록했다.

## 유지보수

KiCad 10의 Python으로 다음을 실행한다.

```powershell
& 'C:\Program Files\KiCad\10.0\bin\python.exe' 'balun\refresh_schematic_layouts.py'
& 'C:\Program Files\KiCad\10.0\bin\python.exe' 'balun\refresh_schematic_layouts.py' --apply
& 'C:\Program Files\KiCad\10.0\bin\python.exe' 'balun\verify_schematic_refresh.py'
```

첫 명령은 후보 회로도와 PDF만 생성한다. `--apply`는 검증 후 세 회로도와 해당 표시 색상만 반영한다. 변경 전 백업 또는 마지막 반영본과 현재 파일의 해시가 다르면 사용자 편집을 덮어쓰지 않고 중단한다. 마지막 명령은 실제 CAD와 재생성 결과를 검사하며 현재 PCB를 저장하거나 재생성하지 않는다. 이 날짜의 백업에 기반한 정리 도구이므로 이후 전기적 설계가 바뀌면 이전 백업으로 강제 되돌려 사용하지 않는다.

KiCad에서 기존 파일을 열어 둔 경우, 오래된 화면을 다시 저장하지 말고 프로젝트와 회로도를 다시 열어 갱신된 배치를 확인한다.

## 제조 상태는 그대로

- 슬립링 J1 후보의 기존 DNP/HOLD와 `DO NOT FABRICATE`를 유지했다. 커넥터를 빼고 주문하라는 뜻이 아니다.
- RJ45 공통 CAD의 RSH1/CSH1 DNP를 유지했다. 업체가 조립할 SHIELD-BONDED / SHIELD-FLOAT 구분은 [기존 구매 범위 문서](PCBA_PURCHASE_SCOPE_2026-09-03.md)를 따른다.
- 검사 통과는 이번 표현 변경이 전기적 연결을 바꾸지 않았다는 확인이지, RF 성능 보증이나 제조 승인 선언이 아니다.
