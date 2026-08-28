---
name: saw-ooc-analysis
description: >
  반도체 후공정 SAW(Dicing Saw) 공정의 SPC Out-of-Control 원인 분석 워크플로우.
  공선성 검증, 통계 모델링, Cpk 분석, 시계열 분석, PPT 주장 타당성 점검,
  시각화(14종), HTML 리포트 생성, README·SKILL 문서화를 포함한 종합 분석 스킬.
  데이터: 20000_BGTTV.xlsx (20,000건, 합성 시뮬레이션)
---

# SAW 공정 SPC OOC 원인 분석 스킬

## 사용 조건
- SAW 공정 데이터 (Blade Wear, Sawing Speed, Coolant Flow, Xbar, Range, SPC_Status) 포함 xlsx/csv
- Python 3.10+, pandas, numpy, scipy, statsmodels, scikit-learn, shap, matplotlib, seaborn, openpyxl

## 설치

```bash
pip install pandas numpy scipy statsmodels scikit-learn shap matplotlib seaborn openpyxl python-pptx
```

## 분석 단계 (워크플로우)

### Phase 0. 데이터 확인
1. xlsx 시트 목록 확인 (`pd.ExcelFile`)
2. 메인 시트 로드 및 컬럼 파악
3. 결측치 확인 (SAW 관련 컬럼)
4. BG 불량 기준 확인 (BG_Crack_Count_After > 3 OR BG_Scratch_Count_After > 3)

### Phase 1. 탐색적 데이터 분석 (EDA)
1. SPC Status 현황 및 OOC 비율 계산
2. IC군 3σ 기반 Control Limits 역추정 (UCL/LCL)
3. OOC 판정 유형 분류 (Xbar Only / Range Only / Both / Unknown Rule)
4. 공정 파라미터 IC vs OOC t-검정
5. BG 불량 × SAW OOC 층화 분석 (카이제곱 검정)
6. Blade Wear 구간별, Sawing Speed 구간별 OOC율

### Phase 2. 공선성 심층 검증
1. VIF (분산팽창인수) 계산 — 기준: VIF < 10
2. 조건수(Condition Number) 계산 — 기준: < 30
3. OLS vs Ridge 계수 안정성 비교
4. Pearson 상관행렬

```python
from statsmodels.stats.outliers_influence import variance_inflation_factor
import statsmodels.api as sm

X_sm = sm.add_constant(X_scaled)
vif = [variance_inflation_factor(X_sm.values, i) for i in range(X_sm.shape[1])]
eigenvalues = np.linalg.eigvalsh(X_scaled.T @ X_scaled)
cond_number = np.sqrt(eigenvalues[-1] / eigenvalues[0])
```

### Phase 3. 통계 모델링
1. Logistic Regression (5-fold CV AUC) — 사용 가능 기준: AUC > 0.65
2. Random Forest + SHAP (5-fold CV AUC)
3. OLS 회귀 (Range ~ 파라미터) — 사용 가능 기준: R² > 0.1
4. 모델 사용 가능성 판정

### Phase 4. Cpk 계산
```python
def cpk(series, lsl, usl):
    mu, sigma = series.mean(), series.std(ddof=1)
    return min((usl-mu)/(3*sigma), (mu-lsl)/(3*sigma))

# Speed: LSL=27, USL=34 mm/s
# Coolant: LSL=1.5, USL=1.7 L/min
```

### Phase 5. 시계열 분석
- LOT 순번별 Range 이동평균
- n구간별 OOC율 분포 → 랜덤 vs 트렌드 판별

### Phase 6. 그래프 생성 (14종)
| 코드 | 그래프 | Seaborn 함수 |
|---|---|---|
| G01 | SPC Status 파이 + OOC 유형 | plt.pie, ax.bar |
| G02 | Xbar/Range 히스토그램 + 꼬리 | sns.histplot |
| G03 | Box + Swarm (IC vs OOC) | sns.boxplot + sns.stripplot |
| G04 | Blade Wear vs Speed Scatter | ax.scatter + np.polyfit |
| G05 | LOT 시계열 Range + OOC | ax.plot + ax.scatter |
| G06 | 상관계수 히트맵 | sns.heatmap |
| G07 | 결측치 히트맵 | sns.heatmap |
| G08 | 2D OOC율 히트맵 | sns.heatmap |
| G09 | Cpk 시각화 | stats.norm.pdf + fill_between |
| G10 | Blade Wear 100% 분석 | sns.histplot + ax.bar |
| G11 | Feature Importance + SHAP | ax.barh |
| G12 | VIF + 조건수 | ax.barh + ax.bar |
| G13 | OOC 유형 분류 | ax.bar + ax.scatter |
| G14 | Cpk 비교 막대 | ax.bar |

### Phase 7. HTML 리포트 생성
- Base64 이미지 인라인 임베딩
- MathJax CDN으로 LaTeX 수식 렌더링
- Noto Sans KR (Google Fonts CDN) 한글 폰트
- Lightbox JS (클릭 확대)
- SVG 인라인 (공정 흐름도, Fishbone 4M1E)
- PPT 주장 타당성 점검 테이블

### Phase 8. 문서화
- README.md (프로젝트 개요, 실행 방법, 결과 요약)
- SKILL.md (이 파일)

## 핵심 결론 (20000_BGTTV.xlsx 기준)

| 항목 | 결과 |
|---|---|
| OOC 비율 | 6.83% |
| OOC 주원인 | Range(산포) 증가 (+61%, p≈0) |
| 공선성 | VIF < 10, 조건수 < 30 → 없음 |
| 모델 AUC | ≈ 0.51 → 사용 불가 |
| Speed Cpk | 0.587 (목표 1.33 미달) |
| Coolant Cpk | 0.611 (목표 1.33 미달) |
| BG-SAW 연관 | χ²=0.081, p=0.776 → 독립 |

## 한글 폰트 설정
```python
# Windows 환경
for fname in ["NanumGothic", "Malgun Gothic", "Gulim", "Batang"]:
    try:
        fm.findfont(fm.FontProperties(family=fname), fallback_to_default=False)
        plt.rcParams["font.family"] = fname
        break
    except Exception:
        pass
plt.rcParams["axes.unicode_minus"] = False
```

## 주의사항
- 원본 데이터 수정 금지 (읽기 전용)
- Control Limits는 IC군 3σ 역추정값 (공식 UCL/LCL 아님)
- 합성 데이터 기반 — 실제 공정 적용 전 재검증 필요
- SHAP 사용 시 shap 패키지 버전 호환성 확인
- 참고문헌 중 [UNVERIFIED] 항목은 직접 확인 후 인용
- random_state=42 고정으로 재현성 보장
