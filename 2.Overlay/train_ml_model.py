import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import HuberRegressor
from sklearn.metrics import mean_squared_error, mean_absolute_error
from sklearn.preprocessing import OneHotEncoder
import os

print("1. Loading Data...")
df = pd.read_csv('../data/processed/overlay_A_train_cleaned.csv')

# Features and Targets
features = ['tool_id', 'reticle_id', 'field_x', 'field_y', 'align_quality', 'ambient_temp_c']
target_x = 'overlay_x_nm'
target_y = 'overlay_y_nm'

# One-Hot Encoding for categorical features
categorical_cols = ['tool_id', 'reticle_id']
df = pd.get_dummies(df, columns=categorical_cols, drop_first=False)

# Get new feature names
feature_cols = [col for col in df.columns if col not in ['sample_id', 'lot_id', 'sequence', 'overlay_x_nm', 'overlay_y_nm', 'residual_nm', 'spec_pass']]

print("2. Splitting Data (70% Train, 30% Test)...")
X = df[feature_cols]
y_x = df[target_x]
y_y = df[target_y]

X_train, X_test, y_x_train, y_x_test, y_y_train, y_y_test = train_test_split(
    X, y_x, y_y, test_size=0.3, random_state=42
)
print(f"Train size: {len(X_train)}, Test size: {len(X_test)}")

print("\n3. Training ML Model (Random Forest)...")
rf_x = RandomForestRegressor(n_estimators=100, random_state=42)
rf_y = RandomForestRegressor(n_estimators=100, random_state=42)

rf_x.fit(X_train, y_x_train)
rf_y.fit(X_train, y_y_train)

# Predict
rf_pred_x = rf_x.predict(X_test)
rf_pred_y = rf_y.predict(X_test)
rf_rmse = np.sqrt(mean_squared_error(y_x_test, rf_pred_x) + mean_squared_error(y_y_test, rf_pred_y))

print("\n4. Training Baseline Model (Huber Regression)...")
# To compare fairly, we must run Huber on the exact same train/test split.
# Huber doesn't natively handle one-hot encoded categorical variables as well as grouped fitting.
# But for simplicity as a baseline, we'll fit Huber on the same feature matrix.
huber_x = HuberRegressor(epsilon=1.35).fit(X_train, y_x_train)
huber_y = HuberRegressor(epsilon=1.35).fit(X_train, y_y_train)

huber_pred_x = huber_x.predict(X_test)
huber_pred_y = huber_y.predict(X_test)
huber_rmse = np.sqrt(mean_squared_error(y_x_test, huber_pred_x) + mean_squared_error(y_y_test, huber_pred_y))

print("\n=== Evaluation Results (RMSE) ===")
print(f"Baseline (Huber Linear): {huber_rmse:.3f} nm")
print(f"Machine Learning (Random Forest): {rf_rmse:.3f} nm")

# Feature Importance
print("\n=== ML Feature Importance (X-axis) ===")
importances = pd.Series(rf_x.feature_importances_, index=feature_cols).sort_values(ascending=False)
print(importances.head(10))

# Save results for reporting
results = pd.DataFrame({
    'Metric': ['RMSE', 'RMSE'],
    'Model': ['Baseline (Huber)', 'Machine Learning (RF)'],
    'Value': [huber_rmse, rf_rmse]
})
results.to_csv('../data/processed/ml_evaluation_results.csv', index=False)
print("\nResults saved successfully.")
