---
name: bg-process-analysis-workflow
description: 반도체 후공정 BG(Back Grinding) 공정의 데이터 검증, 통계 분석, 머신러닝 모델링 및 물리적 해석을 통한 종합 HTML 리포트 생성 워크플로우.
---

# BG Process Analysis Workflow Skill

본 스킬은 반도체 Back Grinding(BG) 공정 데이터(`.xlsx`)가 주어졌을 때, 에이전트가 수행해야 할 종합 분석 파이프라인과 물리적 해석 가이드라인을 정의합니다.

## 1. 전제 조건 및 데이터 구조
- **입력 파일**: BG 공정 전/후의 Crack, Scratch, TTV 데이터가 포함된 엑셀 파일 (예: `20000_BGTTV.xlsx`).
- **타겟 변수**: 출하 TTV(`BG_TTV_After_um` > 3.0μm 일 경우 불량) 및 파생된 불량 여부.

## 2. 핵심 분석 단계

### Step 1: Fact Check (기존 가설 및 수치 검증)
- 평균 Crack 및 Scratch 변화량 산출.
- TTV USL 초과 건수 및 최종 Fail 비율 계산.
- Crack ↔ TTV 간 피어슨 상관계수 산출.

### Step 2: 다중공선성(VIF) 검증
- 입력 변수(`BG_Crack_Count_Before`, `BG_Scratch_Count_Before`, `BG_TTV_Before_um`) 간의 VIF(Variance Inflation Factor)를 측정하여 5 미만인지 확인합니다. VIF가 낮아야 모델 해석(특성 중요도)의 신뢰성이 보장됩니다.

### Step 3: 공정능력평가 (Cpk) 및 예측 모델링 (ML)
- **Cpk 계산**: `(USL - Mean) / (3 * Sigma)` 공식을 통해 Cpk를 산출하고 통상적 합격선인 1.33과 비교합니다.
- **Random Forest**: 불량(Target) 여부를 분류하는 트리를 학습시키고 **Feature Importance**를 추출하여 가장 지분이 큰 불량 원인(예: 입고 TTV)을 특정합니다.

### Step 4: 시각화 및 다차원 EDA
- **KDE Plot**: 공정 전/후 분포 겹침 밀도도 시각화.
- **Drift/Trend (Moving Average)**: 생산 시계열(Wafer Order)에 따른 센서 데이터 열화 현상 시각화.
- **Heatmap (Pearson)**: 변수 간 1:1 선형 상관관계 히트맵 도출 (0.0 기준점 컬러맵 조절 필수).

## 3. 물리적 도메인 해석 (Red Team 접근)
데이터 분석 결과를 도출했다면, 반드시 반도체 물리적 도메인 지식(Preston 방정식 등)을 결합해 해석해야 합니다.

- **모순점 발견**: Scratch가 줄었는데 Crack이 늘어났다면, 얕은 연마(Fine Grinding)는 정상이나 초기 거친 연마(Rough Grinding)의 과부하로 인한 Sub-Surface Damage(SSD)가 원인일 수 있습니다.
- **인과관계 확립**: 입고 TTV가 불량할수록 거친 연마의 충격을 견디지 못합니다.
- **엔지니어링 제언(DOE)**: 단순히 Fine Grinding을 늘리는 대안을 기각하고, **"Rough Grinding의 압력(P)과 속도(V) 하향 제어 및 최적화"**라는 근본적 프로젝트 방향성을 제시해야 합니다.

## 4. 리포트 생성 표준
- 분석 결과는 정적 HTML 리포트로 출력해야 하며, 시각화를 위한 플롯은 `base64` 이미지로 내장하여 단일 파일 공유가 가능하게 만듭니다.
- **대시보드 UI**: 수치 KPI, 넘버링된 섹션 구조, Alert 박스 등을 활용하여 공학/통계 지식이 부족한 실무진도 직관적으로 결론을 이해할 수 있게 포팅합니다. (참조 양식: `saw_ooc_report_v3.html` 기반의 CSS 구조 사용).
