import pandas as pd
import numpy as np
from sklearn.linear_model import HuberRegressor
import warnings

warnings.filterwarnings('ignore')

print("1. Loading Data...")
# Load full training data
train_df = pd.read_csv('../data/processed/overlay_A_train_cleaned.csv')

# Load holdout features
holdout_df = pd.read_csv('../data/overlay_A_holdout_features.csv')
print(f"Train size: {len(train_df)}, Holdout size: {len(holdout_df)}")

# Fix reticle_id typos in holdout if they exist (Rule 3)
typo_mask_3 = holdout_df['reticle_id'] == 0.3
typo_mask_4 = holdout_df['reticle_id'] == 0.4
holdout_df.loc[typo_mask_3, 'reticle_id'] = 3.0
holdout_df.loc[typo_mask_4, 'reticle_id'] = 4.0

print("\n2. Training Grouped Linear Models (100% Train Set)...")
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

print("3. Predicting on Holdout Set...")
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
output_path = '../data/processed/overlay_A_holdout_predictions.csv'
holdout_df[['sample_id', 'pred_overlay_x_nm', 'pred_overlay_y_nm']].to_csv(output_path, index=False)
print(f"\n4. Predictions saved to: {output_path}")
print("Prediction preview:")
print(holdout_df[['sample_id', 'tool_id', 'reticle_id', 'pred_overlay_x_nm', 'pred_overlay_y_nm']].head())
