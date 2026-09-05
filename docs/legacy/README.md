# 이전 설계·측정·구매 자료의 적용 범위

현재 설계 방향은 [설계 검토 인계](../../DESIGN_REVIEW_HANDOFF.md), 측정 절차는 [VNA_TEST_PLAN](../../VNA_TEST_PLAN.md), 수동 어댑터 제작 초안은 [JLCPCB_BUILD](../../adapters/JLCPCB_BUILD.md)를 따른다. 아래 자료는 추적 가능한 이력을 위해 원래 경로에 보존한다. 문서 본문의 “최신”, “최종”, “구매 확정”은 **작성 당시 구성**을 가리키며, 현재 기본안의 전체 발주 지시로 해석하지 않는다.

| 이력 자료 | 계속 참고할 수 있는 내용 | 현재 구성에 그대로 적용하지 않는 내용 |
| --- | --- | --- |
| [이전 VNA_TEST_PLAN](https://github.com/ckh7488/balun_test/blob/c9ee74f103a5f79e9ecf2f28fc48504b0bb64348/VNA_TEST_PLAN.md) | SMA 기준 REF 비교의 이전 의도 | 현재 최종 기준면과 보정 절차 |
| [balun_slipring](../../balun_slipring/README.md), [측정 문서](../../balun_slipring/MEASUREMENT.md) | 전용 balun CAD, 공개 PINMAP·풋프린트 근거 | 새 수동 어댑터의 회로/실장, 미사용 load 수, SMA-only 절차 |
| [balun_llc16](../../balun_llc16/README.md), [측정 문서](../../balun_llc16/MEASUREMENT.md) | 전용 balun CAD와 기존 fixture_spec 핀맵 | 새 수동 어댑터의 실장면·패널 기구·제작 수량 |
| [JLCPCB_ORDER_GUIDE](../../JLCPCB_ORDER_GUIDE.md), [JLCPCB_FINAL_BOM.csv](../../JLCPCB_FINAL_BOM.csv) | 당시 부품/조달 검토 기록 | 현재 공통 지그+어댑터 세트의 통합 BOM/수량 |
| [PCBA_PURCHASE_SCOPE_2026-09-03](../../PCBA_PURCHASE_SCOPE_2026-09-03.md) | 이전 PCBA 구성과 조립 variant | 현재 총수량과 “사용자 손납땜 없음” 전제 |
| [HAND_ASSEMBLY_PURCHASE_2026-09-03](../../HAND_ASSEMBLY_PURCHASE_2026-09-03.md), [PURCHASE_REQUEST_FORM_DRAFT_2026-09-03](../../PURCHASE_REQUEST_FORM_DRAFT_2026-09-03.md) | 당시 bare PCB/부품 구매 검토 | 예전 보드 구성·수량·M12 제외 여부를 새 어댑터에 자동 적용 |
| [RELEASE_EXPORT](../../RELEASE_EXPORT.md), [export_jlc_release.ps1](../../export_jlc_release.ps1) | 기존 export 대상과 실행 동작 | 새 `adapters/` 지원 또는 현재 전체 제조 release 완료 |
| [REVIEW_2026-08-31](../../REVIEW_2026-08-31.md), [SCHEMATIC_READABILITY_2026-09-03](../../SCHEMATIC_READABILITY_2026-09-03.md) | 당시 리뷰·회로도 가독성 변경 이력 | 현재 전체 프로젝트 검토 완료 |
| [JLCPCB_IMPEDANCE_VERIFICATION_2026-08-31](../../JLCPCB_IMPEDANCE_VERIFICATION_2026-08-31.md) | 기존 geometry/승인 상태의 기록 | 새 어댑터의 field-solver/coupon 확인 완료 |

공통 [balun_eth_rj45](../../balun_eth_rj45/README.md) Rev B 자체는 현재도 재사용한다. 그 [FAB_NOTES](../../balun_eth_rj45/JLCPCB_FAB_NOTES.md)의 nominal 적층과 land pattern은 유효한 설계 참고이며, 이력 구매 문서와 함께 모두 폐기한 것이 아니다. 다만 실제 제조사의 stack/solver, 조립 방식과 부품 안착은 현재 제작 건에 맞춰 확인한다.

과거 설계·구매 기록을 삭제하거나 주문을 취소한 것이 아니다. 새 구성의 통합 수량표, 표준 부품/PCB, 패널 도면과 어댑터 제조 export가 작성되면 해당 문서를 현재 기준으로 연결한다.

현재 제조 옵션 및 치수는 [2026-09-05 주문 화면 가이드](../jlcpcb/README.md)와 [임피던스 증거](../jlcpcb/IMPEDANCE.md)가 우선한다.
