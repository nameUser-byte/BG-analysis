# Photo PR CD Prediction & Quality Analysis

이 프로젝트는 반도체 제조 공정 중 노광(Photo) 공정의 PR(Photo Resist) 데이터를 기반으로, Critical Dimension(CD)을 예측하고 수율(Pass/Fail)을 판별하기 위한 데이터 분석 및 머신러닝 모델링 파이프라인입니다.

## 📂 프로젝트 구조 (Directory Structure)

```text
Photo PR/
├── train.csv               # 원본 학습 데이터셋 (공정 변수 및 CD, 불량 확률 포함)
├── holdout_features.csv    # 검증을 위한 신규 Raw 데이터셋 (CD 미포함)
├── index.html              # 📊 최종 분석 보고서 (시각화 이미지 Base64 내장, 단일 파일)
├── readme.md               # 📖 현재 문서 (프로젝트 개요 및 실행 방법)
└── skill.md                # 🤖 데이터 전처리 및 모델링 룰셋 (재현성을 위한 가이드)
```
*(참고: 중간 생성 데이터 정제 파일 및 임시 파이썬 스크립트는 분석 시스템의 scratch 환경에 별도 저장되어 있습니다.)*

## 🛠️ 요구 사항 (Requirements)

파이썬 환경에서 다음의 라이브러리가 필요합니다.
```bash
pip install pandas numpy scikit-learn statsmodels matplotlib seaborn xgboost lightgbm
```

## 🚀 실행 흐름 및 파이프라인 (Pipeline)

본 분석은 다음과 같은 순서로 진행되었습니다. 상세한 전처리 규칙은 `skill.md`를 참고하십시오.

1. **데이터 탐색 및 전처리 (EDA & Preprocessing)**
   - `pr_tone` 결측치 제거, 중복열 제거.
   - `exposure_dose_mj_cm2` > 300, `peb_temp_c` > 300 등의 물리적 불가치 교정.
   - 결측치 처리: `pr_tone`과 `tool_id` 기준의 그룹별 중앙값(Median) 대체.
2. **다중공선성(Collinearity) 및 회귀분석**
   - VIF 측정 결과, `normalized_dose_pct` 변수가 심각한 공선성을 유발하여 제외.
   - 나머지 변수는 VIF 1.0 수준으로 독립성 확인.
3. **머신러닝 모델 학습 및 평가 (CD 예측)**
   - 선형 회귀분석의 한계를 극복하기 위해 `Random Forest`, `XGBoost`, `LightGBM`, `SVR` 적용.
   - 70:30 Train-Test Random Split을 통해 성능 비교.
   - **NEGATIVE PR 최적 모델**: Random Forest
   - **POSITIVE PR 최적 모델**: LightGBM
4. **Hold-out 데이터 검증**
   - 최적 모델을 활용하여 `holdout_features.csv`의 CD 값을 예측.
   - 기존 학습 데이터 기준 정상 규격(PASS Limits: 43.65 ~ 56.22)에 기반하여 수율을 판별.
5. **최종 보고서 생성 (Report Generation)**
   - 분석 결과, 모식도, 수식, 변수 중요도 및 상관관계 차트를 포함한 `index.html` 단일 파일로 렌더링.
