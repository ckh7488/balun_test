# 설계 입력의 공개 출처

이번 어댑터의 핀맵과 부품 후보는 이 작업 전부터 공개되어 있던 저장소 커밋 `c9ee74f103a5f79e9ecf2f28fc48504b0bb64348`에서 가져왔다. 별도의 사내 파일이나 PC 폴더를 읽어 새 핀맵을 추출하지 않았다.

- 슬립링 M12/Molex 핀맵: [기존 공개 PINMAP.md](https://github.com/ckh7488/balun_test/blob/c9ee74f103a5f79e9ecf2f28fc48504b0bb64348/balun_slipring/PINMAP.md)
- LLC M12/RJ45 핀맵: [기존 공개 fixture_spec.json](https://github.com/ckh7488/balun_test/blob/c9ee74f103a5f79e9ecf2f28fc48504b0bb64348/balun_llc16/fixture_spec.json)
- RJ45 공통 지그: [기존 공개 PCB/README](https://github.com/ckh7488/balun_test/tree/c9ee74f103a5f79e9ecf2f28fc48504b0bb64348/balun_eth_rj45)
- 커넥터 풋프린트의 원본은 [출처표](FOOTPRINT_SOURCES.md)에 기록했다.

이번 변경은 위 공개 설계 입력을 사용하는 어댑터 CAD, 측정 절차와 합성 검증용 소프트웨어다. 실제 회사 측정 데이터, 구매 내역, 견적, 계정 정보 또는 개인 PC 경로를 새 산출물에 포함하지 않는다. 이전 구매 문서는 수정·복제하지 않고 기존 Git 이력으로 참조한다.
