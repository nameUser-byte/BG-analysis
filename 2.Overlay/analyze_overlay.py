import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression
import os

# Create artifacts directory for images if it doesn't exist
artifact_dir = r'C:\Users\chan\.gemini\antigravity\brain\1c047f30-a8c7-4f6f-829a-34f88253bc02'
os.makedirs(artifact_dir, exist_ok=True)

# 1. Load Cleaned Data
df = pd.read_csv('data/processed/overlay_A_train_cleaned.csv')

# Step 1: Linear Overlay Modeling
# Model: 
# overlay_x = Tx + Sx * X - Rx * Y
# overlay_y = Ty + Sy * Y + Ry * X
X_features = df[['field_x', 'field_y']]
y_x = df['overlay_x_nm']
y_y = df['overlay_y_nm']

model_x = LinearRegression().fit(X_features, y_x)
model_y = LinearRegression().fit(X_features, y_y)

df['pred_x'] = model_x.predict(X_features)
df['pred_y'] = model_y.predict(X_features)

df['calc_residual_x'] = df['overlay_x_nm'] - df['pred_x']
df['calc_residual_y'] = df['overlay_y_nm'] - df['pred_y']
df['calc_residual_nm'] = np.sqrt(df['calc_residual_x']**2 + df['calc_residual_y']**2)

print("--- Linear Model Coefficients ---")
print(f"Tx (X Translation): {model_x.intercept_:.3f} nm")
print(f"Sx (X Scaling): {model_x.coef_[0]:.3f}")
print(f"Rx (X Rotation term, -coef_y): {-model_x.coef_[1]:.3f}")
print(f"Ty (Y Translation): {model_y.intercept_:.3f} nm")
print(f"Sy (Y Scaling): {model_y.coef_[1]:.3f}")
print(f"Ry (Y Rotation term, coef_x): {model_y.coef_[0]:.3f}")

# Step 2: Wafer Map 시각화 (Quiver Plot)
# Pick a specific Lot, e.g., 'L0036'
lot_id_target = df['lot_id'].value_counts().index[0] # Pick the most frequent lot
lot_df = df[df['lot_id'] == lot_id_target]

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
# Plot Raw Overlay
ax1.quiver(lot_df['field_x'], lot_df['field_y'], lot_df['overlay_x_nm'], lot_df['overlay_y_nm'], 
           angles='xy', scale_units='xy', scale=30, color='r', width=0.005)
ax1.scatter(lot_df['field_x'], lot_df['field_y'], color='black', s=10)
ax1.set_title(f'Raw Overlay Vector Map (Lot {lot_id_target})')
ax1.set_xlim([-1.2, 1.2])
ax1.set_ylim([-1.2, 1.2])
ax1.grid(True, linestyle='--', alpha=0.6)

# Plot Residual Overlay
ax2.quiver(lot_df['field_x'], lot_df['field_y'], lot_df['calc_residual_x'], lot_df['calc_residual_y'], 
           angles='xy', scale_units='xy', scale=30, color='b', width=0.005)
ax2.scatter(lot_df['field_x'], lot_df['field_y'], color='black', s=10)
ax2.set_title(f'Residual Vector Map After Linear Correction (Lot {lot_id_target})')
ax2.set_xlim([-1.2, 1.2])
ax2.set_ylim([-1.2, 1.2])
ax2.grid(True, linestyle='--', alpha=0.6)

plt.tight_layout()
plt.savefig(os.path.join(artifact_dir, 'wafer_map.png'), dpi=300)
plt.close()

# Step 3: 반례 Field 탐색 (Residual vs Align Quality)
# Use original residual_nm or our calc_residual_nm. We'll use our calc_residual_nm for accuracy.
fig, ax = plt.subplots(figsize=(8, 6))
scatter = ax.scatter(df['align_quality'], df['calc_residual_nm'], c=(df['spec_pass']=='FAIL'), cmap='coolwarm', alpha=0.6)
ax.set_xlabel('Align Quality')
ax.set_ylabel('Calculated Residual (nm)')
ax.set_title('Residual vs Align Quality (Red=FAIL, Blue=PASS)')
ax.grid(True, linestyle='--', alpha=0.6)
plt.savefig(os.path.join(artifact_dir, 'align_quality_vs_residual.png'), dpi=300)
plt.close()

# Find Counterexamples: High Residual (> 10nm) BUT Bad Align Quality (e.g., > 2 or < 0.6)
# Standard align_quality is around 0.86 (from EDA). Outliers might be > 1.5.
bad_metrology_threshold = 1.5 
high_residual_threshold = 10.0

counter_examples = df[(df['calc_residual_nm'] > high_residual_threshold) & 
                      (df['align_quality'] > bad_metrology_threshold)]

print("\n--- Counterexamples: High Residual due to Bad Metrology Quality ---")
print(f"Found {len(counter_examples)} counterexamples.")
print(counter_examples[['sample_id', 'lot_id', 'field_x', 'field_y', 'align_quality', 'calc_residual_nm', 'spec_pass']])

# Step 4: 추가 계측 제안 탐색
# High Residual BUT GOOD Align Quality (True Process Issue)
good_metrology_threshold_low = 0.7
good_metrology_threshold_high = 1.1

true_process_issues = df[(df['calc_residual_nm'] > high_residual_threshold) & 
                         (df['align_quality'] >= good_metrology_threshold_low) &
                         (df['align_quality'] <= good_metrology_threshold_high)]

print("\n--- True Process Issues: High Residual with GOOD Metrology Quality ---")
print(f"Found {len(true_process_issues)} points.")
# Let's see if these happen at specific edges (high abs(field_x) or abs(field_y))
true_process_issues['is_edge'] = (abs(true_process_issues['field_x']) > 0.8) | (abs(true_process_issues['field_y']) > 0.8)
edge_ratio = true_process_issues['is_edge'].mean() * 100
print(f"Percentage of True Process Issues located at wafer Edge: {edge_ratio:.1f}%")

