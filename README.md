# ENDLESS Legend 2 — Tidefall Mayhem

게임 시작과 매 Tidefall마다 후보 3개 중 1개를 골라 영구 효과를 쌓는 BepInEx 모드입니다. 현재 버전은 **0.5.0**, 증강은 **36계열 × 3등급 = 108종**입니다.

- 플레이어에게만 적용됩니다.
- 실버 / 골드 / 프리즘 등장 확률: 40% / 40% / 20%.
- 골드 효과는 실버의 2배, 프리즘은 3배입니다.
- 같은 증강과 서로 다른 등급의 효과가 영구 누적됩니다.
- 한국어와 영어 설명을 제공합니다.

## 설치

기준 게임 버전: **1.0.197**. 사용한 로더: **BepInEx 5.4.23.5**.

1. 게임을 종료합니다.
2. ENDLESS Legend 2에 호환되는 BepInEx 5를 설치합니다. 이 저장소에는 로더를 포함하지 않습니다.
3. 이 저장소의 `BepInEx` 폴더를 게임 설치 폴더에 복사합니다. 기존 모드를 사용 중이면 먼저 백업합니다.
4. `BepInEx/plugins/TidefallMayhem/TidefallMayhem.dll`과 그 옆 `Assets` 폴더가 있는지 확인합니다.
5. 게임을 시작합니다. 새 게임에서 첫 증강 선택을 확인하세요.

배포 ZIP은 동일한 폴더 구조이므로 게임 설치 폴더에 압축을 풀어도 됩니다. `Mods` 폴더는 개발용이며, 일반 설치에는 필요하지 않습니다.

## 2026-11-02 밸런스

아래 수치는 실버 기준입니다. 골드 2배, 프리즘 3배가 적용됩니다.

| 증강 | 효과 |
| --- | --- |
| 정예 훈련소 | 신규 유닛 시작 경험치 +3000 |
| 백전노장 | 경험치 획득 배율 +200%p |
| 전격전 | 지상 이동력 +1, 피해 보너스 +30%p |
| 원정의 베테랑 | 지상 이동력 +1, 경험치 획득 배율 +75%p |
| 천리안 | 시야 +4.5, 지상 이동력 +2, 경험치 획득 배율 +25%p, 피해 보너스 +15%p |

전체 목록: [augments.csv](BepInEx/plugins/TidefallMayhem/augments.csv). 상세 규칙: [한국어 설명서](BepInEx/plugins/TidefallMayhem/README.ko.md).

## 개발

- `Mods/TidefallMayhem.Plugin`: C# 플러그인 소스, 증강 정의, 생성기와 검사 스크립트.
- `Mods/TidefallMayhem`: 생성기에 필요한 템플릿만 보관합니다.
- `BepInEx/plugins/TidefallMayhem`: 설치 가능한 플러그인과 생성된 데이터.

Python 3와 .NET SDK가 필요합니다. 저장소의 `Mods` 폴더를 게임 설치 폴더에 복사한 뒤, **게임 설치 폴더에서** 다음을 실행합니다. C# 컴파일은 설치된 게임과 BepInEx의 DLL을 참조합니다.

```powershell
python Mods/TidefallMayhem.Plugin/build_assets.py
powershell -NoProfile -File Mods/TidefallMayhem.Plugin/build.ps1
python Mods/TidefallMayhem.Plugin/test_catalog.py
python Mods/TidefallMayhem.Plugin/test_always_on.py
```

`augments.json`이 효과 원본입니다. 기본 정의에는 공통 1.5배 보정을 적용하며, 개별 `effect_multiplier=1.0` 정의는 실버 수치를 직접 지정합니다. `tiers.py`가 등급 배율을 적용합니다. CSV는 조회용입니다.

`validate_assets.py`는 로컬로 내보낸 `ModWork/Vanilla` 게임 데이터가 추가로 필요합니다. 게임 원본, 로더 DLL, 개인 로그, 세이브와 작업 백업은 이 저장소에 포함하지 않습니다.

## 검증 범위

108종의 효과·등급 배율·CSV·한영 설명, 4,544개 JSON의 참조·직렬화 구조, 1,728개 중첩 효과를 검증했습니다. 실제 게임 내 UI와 저장/불러오기는 이번 변경 후 재확인하지 않았습니다. 게임을 재실행해야 수정된 데이터가 반영됩니다.
