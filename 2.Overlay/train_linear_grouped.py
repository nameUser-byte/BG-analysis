import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.linear_model import HuberRegressor
from sklearn.metrics import mean_squared_error
import warnings

# Suppress convergence warnings for clean output
warnings.filterwarnings('ignore')

print("1. Loading Data...")
df = pd.read_csv('../data/processed/overlay_A_train_cleaned.csv')

# 2. Train-Test Split (70/30)
train_df, test_df = train_test_split(df, test_size=0.3, random_state=42)
print(f"Total Train size: {len(train_df)}, Total Test size: {len(test_df)}")

# 3. Train Grouped Linear Models (Huber) on 70% TRAIN SET
print("\n2. Training Grouped Linear Models (Tool + Reticle) on Train Set...")
models_x = {}
models_y = {}

groups = train_df.groupby(['tool_id', 'reticle_id'])

for (tool, reticle), group in groups:
    X_train = group[['field_x', 'field_y']]
    y_x_train = group['overlay_x_nm']
    y_y_train = group['overlay_y_nm']
    
    # We need at least 3 points to fit a plane. If less, fallback to a simple mean.
    if len(group) >= 3:
        model_x = HuberRegressor(epsilon=1.35).fit(X_train, y_x_train)
        model_y = HuberRegressor(epsilon=1.35).fit(X_train, y_y_train)
    else:
        # Dummy model that just predicts the mean
        class MeanModel:
            def __init__(self, mean_val): self.mean_val = mean_val
            def predict(self, X): return np.full(len(X), self.mean_val)
        model_x = MeanModel(y_x_train.mean())
        model_y = MeanModel(y_y_train.mean())
        
    models_x[(tool, reticle)] = model_x
    models_y[(tool, reticle)] = model_y

# 4. Predict and Evaluate on 30% TEST SET
print("3. Evaluating on Test Set...")
test_df = test_df.copy()
test_df['pred_x'] = 0.0
test_df['pred_y'] = 0.0
fallback_count = 0

for idx, row in test_df.iterrows():
    group_key = (row['tool_id'], row['reticle_id'])
    
    # If the group exists in training data, predict using its specific model
    if group_key in models_x:
        X_test = pd.DataFrame([[row['field_x'], row['field_y']]], columns=['field_x', 'field_y'])
        test_df.loc[idx, 'pred_x'] = models_x[group_key].predict(X_test)[0]
        test_df.loc[idx, 'pred_y'] = models_y[group_key].predict(X_test)[0]
    else:
        # Unseen group in test set (happens rarely in random split for sparse data)
        fallback_count += 1
        test_df.loc[idx, 'pred_x'] = train_df['overlay_x_nm'].mean()
        test_df.loc[idx, 'pred_y'] = train_df['overlay_y_nm'].mean()

if fallback_count > 0:
    print(f"Warning: {fallback_count} test points belonged to groups not seen in training data.")

# Calculate Test RMSE
test_rmse = np.sqrt(mean_squared_error(test_df['overlay_x_nm'], test_df['pred_x']) + 
                    mean_squared_error(test_df['overlay_y_nm'], test_df['pred_y']))

# Calculate Train RMSE for comparison (to check overfitting)
train_df['pred_x'] = 0.0
train_df['pred_y'] = 0.0
for (tool, reticle), group in groups:
    X_train = group[['field_x', 'field_y']]
    train_df.loc[group.index, 'pred_x'] = models_x[(tool, reticle)].predict(X_train)
    train_df.loc[group.index, 'pred_y'] = models_y[(tool, reticle)].predict(X_train)

train_rmse = np.sqrt(mean_squared_error(train_df['overlay_x_nm'], train_df['pred_x']) + 
                     mean_squared_error(train_df['overlay_y_nm'], train_df['pred_y']))

print("\n=== Validation Results (Grouped Linear Regression) ===")
print(f"Train RMSE (70%): {train_rmse:.3f} nm")
print(f"Test RMSE  (30%): {test_rmse:.3f} nm")
print("======================================================")
