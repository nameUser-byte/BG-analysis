import pandas as pd
df = pd.read_csv('data/processed/overlay_A_train_cleaned.csv')
print("High align_quality points:")
print(df[df['align_quality'] > 1.5][['sample_id', 'align_quality', 'residual_nm']])
print("\nHigh residual points:")
print(df[df['residual_nm'] > 10][['sample_id', 'align_quality', 'residual_nm']])
