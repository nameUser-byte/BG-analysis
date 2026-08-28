import pandas as pd
import numpy as np

file_path = "c:/Users/chan/Documents/semiconductor-ai-project/3.Dry Etch/dry_etch_A_train.csv"
df = pd.read_csv(file_path)

print("=== 1. 스키마 확인 ===")
print(df.info())
print("\n=== 2. 결측치 확인 ===")
print(df.isnull().sum()[df.isnull().sum() > 0])

print("\n=== 3. 중복 데이터 확인 ===")
print(f"중복 행 수: {df.duplicated().sum()}")

print("\n=== 4. 기초 통계량 (이상치 확인용) ===")
print(df.describe().T)

print("\n=== 5. Lot/설비 편중 확인 ===")
print("\nLot ID 분포:")
print(df['lot_id'].value_counts().head(10))
print("\nTool ID 분포:")
print(df['tool_id'].value_counts())
