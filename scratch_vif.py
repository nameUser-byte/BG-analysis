import pandas as pd
import numpy as np
from statsmodels.stats.outliers_influence import variance_inflation_factor
from statsmodels.tools.tools import add_constant

# 데이터 로드
data_path = "c:/Users/chan/Documents/semiconductor-ai-project/3.Dry Etch/dry_etch_A_train_clean.csv"
df = pd.read_csv(data_path)

# 독립 변수(Feature) 선택 (타겟 변수 제외)
# 모델 학습에 사용할 수치형 입력 파라미터만 선택
feature_cols = ['rf_source_w', 'rf_bias_w', 'pressure_mtorr', 'gas_flow_sccm', 
                'esc_temp_c', 'chamber_age_runs', 'oes_peak_ratio', 'endpoint_slope', 'endpoint_time_s']

X = df[feature_cols].copy()
# VIF 계산을 위해 상수항 추가
X_const = add_constant(X)

# VIF 계산
vif_data = pd.DataFrame()
vif_data["Feature"] = X_const.columns
vif_data["VIF"] = [variance_inflation_factor(X_const.values, i) for i in range(X_const.shape[1])]

# 결과 출력 (상수항 제외)
vif_result = vif_data[vif_data["Feature"] != "const"].sort_values(by="VIF", ascending=False)
print("=== 다중공선성(Multicollinearity) 검증 결과 (VIF) ===")
print(vif_result.to_string(index=False))

# VIF가 10 이상인 높은 공선성 변수 식별
high_vif = vif_result[vif_result["VIF"] >= 10]
if len(high_vif) > 0:
    print(f"\n[경고] VIF 10 이상으로 강한 공선성을 띠는 변수가 발견되었습니다:")
    print(high_vif.to_string(index=False))
else:
    print("\n모든 변수의 VIF가 10 미만으로 심각한 다중공선성은 관찰되지 않습니다.")
