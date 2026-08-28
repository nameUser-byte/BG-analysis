import pandas as pd
import numpy as np

file_path = "c:/Users/chan/Documents/semiconductor-ai-project/3.Dry Etch/dry_etch_A_train.csv"
df = pd.read_csv(file_path)

print("=== [1] 보정 전 결측치/중복 행/데이터 수 ===")
print(f"데이터 수: {len(df)}")
print(f"중복 행 수: {df.duplicated().sum()}")
print(f"총 결측치 수: {df.isnull().sum().sum()}")

# 1. 중복 데이터 1개만 남기고 삭제
df.drop_duplicates(inplace=True)

# 2. 이상치 단위 보정
# 온도가 100도 이상인 경우 Kelvin으로 간주하고 273.15를 뺌
df.loc[df['esc_temp_c'] > 100, 'esc_temp_c'] -= 273.15

# 가스 유량이 500 이상인 경우 1/10 스케일링
df.loc[df['gas_flow_sccm'] > 500, 'gas_flow_sccm'] *= 0.1

# 압력이 100 이상인 경우 1/10 스케일링
df.loc[df['pressure_mtorr'] > 100, 'pressure_mtorr'] *= 0.1

print("\n=== [2] 보정 후 확인 ===")
print(f"데이터 수: {len(df)}")
print(f"남은 중복 행 수: {df.duplicated().sum()}")

print("\n=== [3] 결측치 확인 ===")
missing = df.isnull().sum()[df.isnull().sum() > 0]
if len(missing) > 0:
    print(missing)
else:
    print("결측치가 없습니다.")

print("\n=== [4] 남은 이상치 확인 (1.5 IQR 기준) ===")
num_cols = df.select_dtypes(include=[np.number]).columns
num_cols = [c for c in num_cols if c not in ['sequence']]

for col in num_cols:
    Q1 = df[col].quantile(0.25)
    Q3 = df[col].quantile(0.75)
    IQR = Q3 - Q1
    upper_bound = Q3 + 1.5 * IQR
    lower_bound = Q1 - 1.5 * IQR
    
    outliers = df[(df[col] > upper_bound) | (df[col] < lower_bound)]
    extreme_outliers = df[(df[col] > Q3 + 3 * IQR) | (df[col] < Q1 - 3 * IQR)]
    
    if len(outliers) > 0:
        print(f"[{col}]")
        print(f"  - 1.5 IQR 이상치: {len(outliers)}개, 3.0 IQR 이상치: {len(extreme_outliers)}개")
        if len(extreme_outliers) > 0:
            print(f"  - 극단적(3.0) 이상치 샘플값: {extreme_outliers[col].head(3).tolist()}")
