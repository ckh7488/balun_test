# 풋프린트 출처와 확인 범위

새 어댑터는 저장소의 기존 custom connector footprint를 복사해 사용한다. footprint pin 번호를 임의로 재정의하지 않았고, LLC M12만 부품 전체를 180° 회전 배치했다. schematic과 PCB가 같은 핀 번호로 연결되는지는 native parity 및 netlist 검사로 확인했다.

| 로컬 footprint | 기존 출처 | 제조사 자료 |
| --- | --- | --- |
| RJ45_Amphenol_RJE59-188-5401 | balun_eth_rj45.pretty | [Amphenol drawing](https://cdn.amphenol-cs.com/media/wysiwyg/files/drawing/rje591885x01.pdf) |
| Finecables_MB12FBAFF08ST-3 | balun_slipring/common.pretty | [Finecables PCB panel type](https://www.finecables.com/uploadfiles/2022/06/259%20M12%20A_coding%20Straight%20Connector%2C%20Panel%20Mount%2C%20PCB%20Type%2C%20Front%20fastened.pdf) |
| Finecables_MB12MBAFF08ST-3 | balun_llc16/llc16.pretty | [Finecables catalogue, 기존 설계 근거 p415](https://www.finecables.com/uploadfiles/2025/09/2025_Finecables_Industrial_Connector_Catalogue.pdf) |
| Molex_5055680571 | balun_slipring/common.pretty | [Molex product](https://www.molex.com/en-us/products/part-detail/5055680571), [drawing](https://www.molex.com/content/dam/molex/molex-dot-com/products/automated/en-us/salesdrawingpdf/505/505568/5055680571_sd.pdf) |
| Shield_SolderPoint | 이번 설계 | Ø3.0 mm pad / Ø1.2 mm PTH, 부품 없는 solder point |

Finecables의 금속 body/cable-side mating과 component-side PCB pin view는 구분한다. 기존 footprint가 저장되어 있다는 사실만으로 사내 커넥터와의 실제 체결이 증명되지는 않는다. supplier drawing과 샘플로 exact suffix, 성별, pin 1/key, finished-hole, panel seating을 확인한다. 이 확인 전에는 커넥터의 최종 기구 승인으로 표시하지 않는다.
