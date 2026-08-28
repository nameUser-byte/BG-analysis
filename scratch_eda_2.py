import pandas as pd
import numpy as np

file_path = "c:/Users/chan/Documents/semiconductor-ai-project/3.Dry Etch/dry_etch_A_train.csv"
df = pd.read_csv(file_path)

print("=== 1. 결측치 확인 ===")
missing_cols = df.isnull().sum()[df.isnull().sum() > 0]
print(missing_cols)

print("\n=== 2. 중복 데이터 심층 분석 ===")
# 전체 열 기준 중복
total_duplicates = df[df.duplicated(keep=False)].sort_values(by=['sample_id'])
print(f"전체 열 기준 중복 행 개수: {len(total_duplicates)}")

# 메타데이터 기준 중복
meta_cols = ['sample_id', 'lot_id', 'tool_id', 'sequence']
meta_duplicates = df[df.duplicated(subset=meta_cols, keep=False)].sort_values(by=['sample_id'])
print(f"\n메타데이터({', '.join(meta_cols)}) 기준 중복 행 개수: {len(meta_duplicates)}")

if len(meta_duplicates) > 0:
    print("\n[메타데이터 기준 중복 데이터 샘플 (최대 10개)]")
    print(meta_duplicates[meta_cols + ['oes_peak_ratio', 'endpoint_time_s']].head(10))
    
    # 완전히 동일한지 확인
    is_fully_identical = len(total_duplicates) == len(meta_duplicates)
    print(f"\n-> 메타데이터가 동일한 데이터는 모든 측정값도 완전히 동일합니까? {'예' if is_fully_identical else '아니오'}")

print("\n=== 3. 이상치 세부 탐색 (IQR 기준) ===")
# 주요 수치형 변수에 대해 극단적인 이상치 확인
num_cols = ['oes_peak_ratio', 'pressure_mtorr', 'gas_flow_sccm', 'esc_temp_c']
for col in num_cols:
    if col in df.columns:
        Q1 = df[col].quantile(0.25)
        Q3 = df[col].quantile(0.75)
        IQR = Q3 - Q1
        upper_bound = Q3 + 1.5 * IQR
        lower_bound = Q1 - 1.5 * IQR
        
        outliers = df[(df[col] > upper_bound) | (df[col] < lower_bound)]
        extreme_outliers = df[(df[col] > Q3 + 3 * IQR) | (df[col] < Q1 - 3 * IQR)]
        
        print(f"\n[{col}]")
        print(f"- 정상 범위 (1.5 IQR): {lower_bound:.2f} ~ {upper_bound:.2f}")
        print(f"- 1.5 IQR 이상치 개수: {len(outliers)}")
        print(f"- 극단적 3.0 IQR 이상치 개수: {len(extreme_outliers)}")
        if len(extreme_outliers) > 0:
            print(f"- 극단적 이상치 샘플값 (Top 3): {extreme_outliers[col].nlargest(3).tolist()}")
