import pandas as pd
import numpy as np
from sklearn.linear_model import HuberRegressor
import warnings
import os

warnings.filterwarnings('ignore')

print("1. Loading Overlay B Data...")
train_df = pd.read_csv('../data/overlay_B_train.csv')
holdout_df = pd.read_csv('../data/overlay_B_holdout_features.csv')

print(f"Initial Train size: {len(train_df)}, Holdout size: {len(holdout_df)}")

print("\n2. Cleaning Train Data (Applying our validated rules)...")
# Drop rows with missing critical values in Train
initial_len = len(train_df)
train_df.dropna(subset=['field_x', 'field_y', 'overlay_x_nm', 'overlay_y_nm'], inplace=True)
print(f"Removed {initial_len - len(train_df)} rows with missing NaN values from Train.")

# Rule 1: Fix Reticle Typos
for df in [train_df, holdout_df]:
    df.loc[df['reticle_id'] == 0.3, 'reticle_id'] = 3.0
    df.loc[df['reticle_id'] == 0.4, 'reticle_id'] = 4.0

# Rule 2: Remove Coordinate Outliers (> 1.2)
outlier_mask = (train_df['field_x'].abs() > 1.2) | (train_df['field_y'].abs() > 1.2)
print(f"Removed {outlier_mask.sum()} coordinate outliers from Train.")
train_df = train_df[~outlier_mask]

# Rule 3: Remove Metrology Errors (Fake errors)
fake_error_mask = train_df['align_quality'] > 1.5
print(f"Removed {fake_error_mask.sum()} metrology fake errors from Train.")
train_df = train_df[~fake_error_mask]

print(f"Cleaned Train size: {len(train_df)}")

print("\n3. Training Grouped Linear Models (Huber) on Cleaned B Train Set...")
models_x = {}
models_y = {}

groups = train_df.groupby(['tool_id', 'reticle_id'])
for (tool, reticle), group in groups:
    X_train = group[['field_x', 'field_y']]
    y_x_train = group['overlay_x_nm']
    y_y_train = group['overlay_y_nm']
    
    if len(group) >= 3:
        model_x = HuberRegressor(epsilon=1.35).fit(X_train, y_x_train)
        model_y = HuberRegressor(epsilon=1.35).fit(X_train, y_y_train)
    else:
        class MeanModel:
            def __init__(self, mean_val): self.mean_val = mean_val
            def predict(self, X): return np.full(len(X), self.mean_val)
        model_x = MeanModel(y_x_train.mean())
        model_y = MeanModel(y_y_train.mean())
        
    models_x[(tool, reticle)] = model_x
    models_y[(tool, reticle)] = model_y

print("\n4. Predicting on Holdout Set...")
holdout_df['pred_overlay_x_nm'] = 0.0
holdout_df['pred_overlay_y_nm'] = 0.0
fallback_count = 0
nan_count = 0

for idx, row in holdout_df.iterrows():
    group_key = (row['tool_id'], row['reticle_id'])
    
    # Handle NaN in coordinates
    if pd.isna(row['field_x']) or pd.isna(row['field_y']):
        nan_count += 1
        holdout_df.loc[idx, 'pred_overlay_x_nm'] = train_df['overlay_x_nm'].mean()
        holdout_df.loc[idx, 'pred_overlay_y_nm'] = train_df['overlay_y_nm'].mean()
        continue
        
    if group_key in models_x:
        X_test = pd.DataFrame([[row['field_x'], row['field_y']]], columns=['field_x', 'field_y'])
        holdout_df.loc[idx, 'pred_overlay_x_nm'] = models_x[group_key].predict(X_test)[0]
        holdout_df.loc[idx, 'pred_overlay_y_nm'] = models_y[group_key].predict(X_test)[0]
    else:
        fallback_count += 1
        holdout_df.loc[idx, 'pred_overlay_x_nm'] = train_df['overlay_x_nm'].mean()
        holdout_df.loc[idx, 'pred_overlay_y_nm'] = train_df['overlay_y_nm'].mean()

if fallback_count > 0:
    print(f"Warning: {fallback_count} holdout points belonged to unseen Tool+Reticle groups.")
if nan_count > 0:
    print(f"Warning: {nan_count} holdout points had missing spatial coordinates (NaN). Predicted global mean.")

# Save predictions
output_dir = '../data/processed'
os.makedirs(output_dir, exist_ok=True)
output_path = os.path.join(output_dir, 'overlay_B_holdout_predictions.csv')
holdout_df[['sample_id', 'pred_overlay_x_nm', 'pred_overlay_y_nm']].to_csv(output_path, index=False)

print(f"\n5. Predictions saved to: {output_path}")
print("Prediction preview:")
print(holdout_df[['sample_id', 'tool_id', 'reticle_id', 'pred_overlay_x_nm', 'pred_overlay_y_nm']].head())
