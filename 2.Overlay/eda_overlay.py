import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import json

file_path = 'data/overlay_A_train.csv'
df = pd.read_csv(file_path)

results = {}

# 1. Schema
results['schema'] = {col: str(dtype) for col, dtype in df.dtypes.items()}

# 2. Missing values
missing = df.isnull().sum()
results['missing_values'] = missing[missing > 0].to_dict()

# 3. Duplicates
results['duplicates'] = int(df.duplicated().sum())

# 4. Outliers (using IQR for numeric columns)
numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
outliers = {}
for col in numeric_cols:
    Q1 = df[col].quantile(0.25)
    Q3 = df[col].quantile(0.75)
    IQR = Q3 - Q1
    lower_bound = Q1 - 1.5 * IQR
    upper_bound = Q3 + 1.5 * IQR
    outliers[col] = int(((df[col] < lower_bound) | (df[col] > upper_bound)).sum())
results['outliers_iqr'] = outliers

# 5. Lot/Tool bias (distribution)
results['lot_distribution'] = df['lot_id'].value_counts().to_dict()
results['tool_distribution'] = df['tool_id'].value_counts().to_dict()

# 6. Basic statistics
results['statistics'] = df.describe().to_dict()

# 7. Target variable distribution
if 'spec_pass' in df.columns:
    results['target_distribution'] = df['spec_pass'].value_counts().to_dict()

with open('eda_results.json', 'w') as f:
    json.dump(results, f, indent=4)

print("EDA analysis completed and saved to eda_results.json")
