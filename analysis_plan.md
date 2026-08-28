# 고급 통계 기반 CMP 데이터 분석(EDA) 계획서

## 1. 분석 목적
단순 기초 통계(단변량/상관관계)를 넘어, 반도체 CMP 공정의 물리적 특성(Preston 방정식 등)과 가설 검정 기법을 결합한 **고도화된 통계 분석**을 수행하여 리포팅(`index.html`)합니다.

## User Review Required
> [!IMPORTANT]
> **이상치/정규성 가정**
> ANOVA나 OLS 회귀 분석은 정규성 가정을 요구합니다. 정규성 검정 결과 분포가 심하게 치우쳐 있을 경우, 비모수 검정(Kruskal-Wallis)을 메인으로 채택하는 것에 동의하십니까?

## Proposed Changes

### [MODIFY] [analysis_plan.md](file:///c:/Users/chan/Documents/semiconductor-ai-project/analysis_plan.md)
기존 EDA 계획에 심화 통계(가설 검정, 회귀, 상호작용 등) 기법을 대폭 추가합니다.

#### 1. 정규성 및 등분산성 검정 (Distribution Stats)
- **Shapiro-Wilk Test**: 주요 타겟 변수(제거율, Dishing 등)가 정규 분포를 따르는지 p-value로 검정.
- **KDE 밀도 추정 시각화**: 커널 밀도 추정을 통해 데이터의 실제 분포 곡선과 첨도/왜도 확인.

#### 2. 범주형 변수의 통계적 유의성 검증 (ANOVA)
- **가설**: "설비(Tool ID) 및 랏(Lot ID)에 따라 공정 품질(제거율, 디싱)에 유의미한 차이가 있는가?"
- **방법론**: One-way ANOVA (정규성 만족 시) 또는 Kruskal-Wallis Test (정규성 위배 시)를 수행하여 p-value < 0.05 인지 확인.

#### 3. Preston's Equation 기반 상호작용 효과 검증 (Interaction Effect)
- **물리적 도메인 반영**: CMP 제거율은 압력(P)과 속도(V)의 곱에 비례한다는 프레스턴 공식(RR = K * P * V)을 통계적으로 검증합니다.
- **OLS 회귀 모델 (statsmodels)**: `removal_rate ~ down_force + platen_speed + (down_force * platen_speed)` 형태의 다중 회귀를 돌려 상호작용 항의 p-value와 설명력(Adj R²) 산출.

#### 4. 편상관계수(Partial Correlation) 및 다중공선성(VIF)
- **VIF 검증**: 변수 간 독립성 확인 (기존 완료).
- **수학적 교란 변수 통제**: 앞서 육안(산점도)으로만 보았던 Rule 5(Pad Age의 교란 효과)를, `pingouin` 패키지 등의 편상관계수(Partial Correlation) 공식을 활용해 Pad Age의 영향을 수학적으로 제거한 순수 '압력-Dishing' 상관계수(r)로 도출.

#### 5. 고급 시각화 차트 추가
- **Hexbin Scatter**: 데이터가 뭉쳐서 안 보이는 산점도 대신, 육각형 밀도(Hexbin) 차트를 적용하여 데이터 집중 구역 파악.
- **lmplot (선형 회귀선 포함 산점도)**: 변수 간 트렌드 라인 및 신뢰구간(Confidence Interval 95%) 함께 시각화.
- **수식 표기**: HTML 내에 MathJax를 활용하여 회귀 방정식과 프레스턴 공식을 수학적으로 아름답게 표기.

## Verification Plan
### Automated Tests
- `statsmodels.api.OLS`를 통해 도출된 Summary의 F-statistic이 유의미한지 검증.
### Manual Verification
- HTML 리포트에서 각 통계 검정 결과(p-value)가 직관적으로 해석되도록 색상(유의미하면 Green, 아니면 Red) 처리되어 있는지 확인.
