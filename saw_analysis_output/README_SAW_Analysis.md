# SAW 공정 SPC Out-of-Control 원인 분석

## 개요
반도체 후공정 Sawing(SAW) 공정에서 SPC Out-of-Control(OOC) 비율(6.83%)의 원인을 분석하고,
공정 파라미터 개선 권고안을 도출하는 데이터 분석 프로젝트입니다.

## 데이터
- **파일**: `20000_BGTTV.xlsx` (합성/시뮬레이션 데이터)
- **시트**: `통합_불량데이터_20000` — 20,000행 × 44열
- **SAW 관련 컬럼**:
  - 파라미터: `SAW_Blade_Wear_pct`, `SAW_Sawing_Speed_mm_s`, `SAW_Coolant_Flow_Lmin`
  - 결과값: `SAW_Xbar_um`, `SAW_Range_um`, `SAW_SPC_Status`

## 분석 결과 요약

| 지표 | 값 |
|---|---|
| OOC 비율 | 6.83% |
| Range 증가 (IC→OOC) | 61.9% |
| 최대 VIF | 3.93 (허용 범위) |
| 조건수 | 3.69 (허용 범위) |
| RF AUC | 0.5058 (사용 불가) |
| Speed Cpk | 0.587 (개선 필요) |
| Coolant Cpk | 0.611 (개선 필요) |

## 실행 방법

### 환경 요구사항
```bash
pip install pandas numpy scipy statsmodels scikit-learn shap matplotlib seaborn openpyxl python-pptx
```

### Python 버전
Python 3.10+ (테스트: Python 3.14)

### 실행
```bash
cd C:\Users\chan\Documents\semiconductor-ai-project
python saw_ooc_analysis_v2.py
```

### 출력물
```
saw_analysis_output/
├── saw_ooc_report_v2.html      # 메인 HTML 리포트 (base64, MathJax)
├── G01_spc_overview.png        # SPC Status 파이 + OOC 유형
├── G02_histogram_tails.png     # Xbar/Range 분포 히스토그램
├── G03_box_swarm.png           # Box + Swarm Plot
├── G04_scatter_blade_speed.png # Blade Wear vs Speed Scatter
├── G05_timeseries_drift.png    # LOT 시계열 + Drift
├── G06_corr_heatmap.png        # 상관계수 히트맵
├── G07_missing_heatmap.png     # 결측치 히트맵
├── G08_ooc_heatmap_2d.png      # 2D OOC율 히트맵
├── G09_cpk_visualization.png   # Cpk 공정 능력 시각화
├── G10_blade_wear_100pct.png   # Blade Wear 100% 분석
├── G11_feature_shap.png        # Feature Importance + SHAP
├── G12_vif_condition.png       # VIF + 조건수
├── G13_ooc_type_analysis.png   # OOC 유형 분류
└── G14_cpk_bar.png             # Cpk 비교 막대
```

## 핵심 발견사항

1. **OOC 주원인 = Range(산포) 증가**: Xbar는 IC/OOC 무관. Range만 OOC 시 61.9% 상승 (p≈0.00e+00)
2. **공선성 없음**: 최대 VIF=3.93 < 10, 조건수=3.69 < 30. 단 Blade Wear ↔ Speed r=0.863
3. **모델 사용 불가**: AUC≈0.5, R²≈0. 미수집 변수(Spindle Run-out 등)가 실제 원인
4. **BG 불량 포함**: BG 불량과 SAW OOC 독립 (χ²=0.081, p=0.7763)
5. **Cpk 부족**: Speed Cpk=0.587, Coolant Cpk=0.611 (목표 1.33 미달)

## 권고사항

1. 공식 SPC 룰 및 UCL/LCL 값 확보
2. Blade 교체 기준 90%로 표준화
3. Speed/Coolant Cpk 개선 (PM 주기 단축, closed-loop 제어)
4. Spindle Run-out 정기 측정 및 이력 DB화
5. Blade ID별 이력 관리 시스템 구축

## 가정 및 한계

- 데이터는 합성/시뮬레이션 데이터 (README 시트)
- Control Limits는 IC군 3σ로 역추정 (공식값 아님)
- OOC 판정 SPC 룰 미파악 (OOC의 82.6%가 3σ 이탈로 설명 불가)
- 실제 공정 적용 전 실측 데이터로 재검증 필요

## 파일 구조

```
semiconductor-ai-project/
├── 20000_BGTTV.xlsx                    # 원본 데이터 (읽기 전용)
├── saw_ooc_analysis.py                 # v1 분석 스크립트
├── saw_ooc_analysis_v2.py              # v2 종합 분석 스크립트 (현재)
├── saw_analysis_output/
│   ├── saw_ooc_report_v2.html         # 메인 리포트
│   ├── Saw.pptx                        # 팀 PPT (참고용)
│   └── G01~G14_*.png                  # 그래프 14종
└── .agents/skills/saw-ooc-analysis/
    └── SKILL.md                        # 에이전트 스킬 문서
```

## 재현성
- `random_state=42` 고정
- 원본 데이터 수정 없음 (읽기 전용)
- 모든 전처리는 분석 스크립트 내에서 재현 가능
