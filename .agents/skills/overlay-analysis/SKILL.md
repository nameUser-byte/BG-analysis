---
name: overlay-analysis
description: "반도체 노광(Lithography) 공정의 Overlay 데이터 전처리, 그룹화된 선형 회귀 잔차 분석 및 HTML 리포트 생성 스킬"
---

# Overlay Data Analysis Skill

이 스킬은 반도체 오버레이(Overlay) 계측 데이터에 대해 선형 보정 모델을 적용하고, 설비/레티클별 그룹화를 통해 진짜 공정 잔차(True Process Residual)와 계측 불량(Metrology Error)을 정밀하게 분리하는 워크플로우를 정의합니다.

## 핵심 원칙 (Required Rules)
1. **Raw 데이터 보존:** `data/raw/` (또는 원본) 데이터를 수정하지 않으며 모든 제외·보정은 Python 코드로만 수행한다.
2. **Kelvin 단위 예외 처리:** `ambient_temp_c`에서 270도 이상의 극단적 고온은 센서 오류가 아닌 Kelvin 단위 오기입으로 가정하고 섭씨로 자동 보정한다.
3. **그룹핑 선형 모델(Grouped Linear Model):** `tool_id`와 `reticle_id` 조합별로 반드시 그룹화하여 선형 회귀(Linear Regression) 모델을 독립적으로 구축해야 가짜 잔차(False Residual)를 막을 수 있다.
4. **계측 품질 필터링:** 잔차가 높다고 무조건 공정 문제로 단정짓지 말고, `align_quality` 변수 등을 기반으로 계측 불량을 분리해 반례를 탐색한다.
5. **보안 규칙:** 웹 리포트 작성 시 `polyfill.io` CDN은 절대 포함하지 않는다.

## 주요 파이프라인 (Execution Pipeline)

### 1. Data Preprocessing (`preprocess_overlay.py`)
- **결측치 처리:** `field_x`, `field_y`, `reticle_id` 결측치가 포함된 행은 Drop
- **대체(Imputation):** `align_quality`, `ambient_temp_c` 결측치는 소속 `tool_id` 그룹의 중앙값(Median)으로 대체
- **단위 보정:** 온도 270도 이상 시 `- 273.15` 연산

### 2. Grouped Linear Modeling (`analyze_overlay_grouped.py`)
- 독립 변수: `field_x`, `field_y`
- 종속 변수: `overlay_x_nm`, `overlay_y_nm`
- **로직:** `df.groupby(['tool_id', 'reticle_id'])` 로 분리된 데이터셋 각각에 `LinearRegression` 피팅 수행
- **잔차 도출:** 실제 오버레이 오차 - 선형 예측 모델 보정값 = `calc_residual_nm`

### 3. Report Generation (`generate_report.py`)
- `seaborn` 및 `matplotlib`을 활용하여 계측 불량 공간 분포 밀도(KDE plot), 그룹화 전후 Wafer Vector Map 비교 생성.
- 로컬 브라우저 구동 편의성을 위해 Base64로 인코딩하여 `index.html` 내부에 직접 포함시킴.
- MathJax 및 Mermaid.js를 사용하여 물리적 모식도와 수식 표현 포함.

## 참고 자료 (References)
- "Impact of Reticle and Scanner Fingerprints on Overlay": Tool/Reticle 그룹화 분산 분석의 당위성
- "Wafer Edge Effect and High-Order Distortion Modeling": Edge 영역의 다점(Dense) 샘플링 제안 근거
