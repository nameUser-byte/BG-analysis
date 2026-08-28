import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.linear_model import HuberRegressor
import os

artifact_dir = r'C:\Users\chan\.gemini\antigravity\brain\1c047f30-a8c7-4f6f-829a-34f88253bc02'

# 1. Load Data
df = pd.read_csv('../data/processed/overlay_A_train_cleaned.csv')

# 2. Group by Tool and Reticle for accurate modeling
df['pred_x'] = 0.0
df['pred_y'] = 0.0

groups = df.groupby(['tool_id', 'reticle_id'])
print(f"Total modeling groups (tool + reticle combinations): {len(groups)}")

for (tool, reticle), group in groups:
    if len(group) < 3: # Not enough points to fit reliably
        df.loc[group.index, 'pred_x'] = group['overlay_x_nm']
        df.loc[group.index, 'pred_y'] = group['overlay_y_nm']
        continue
        
    X = group[['field_x', 'field_y']]
    y_x = group['overlay_x_nm']
    y_y = group['overlay_y_nm']
    
    model_x = HuberRegressor(epsilon=1.35).fit(X, y_x)
    model_y = HuberRegressor(epsilon=1.35).fit(X, y_y)
    
    df.loc[group.index, 'pred_x'] = model_x.predict(X)
    df.loc[group.index, 'pred_y'] = model_y.predict(X)

# 3. Calculate grouped residuals
df['calc_residual_x'] = df['overlay_x_nm'] - df['pred_x']
df['calc_residual_y'] = df['overlay_y_nm'] - df['pred_y']
df['calc_residual_nm'] = np.sqrt(df['calc_residual_x']**2 + df['calc_residual_y']**2)

# Save the new DataFrame with grouped residuals
df.to_csv('../data/processed/overlay_A_train_grouped_residuals.csv', index=False)

# 4. Visualization
lot_id_target = df['lot_id'].value_counts().index[0]
lot_df = df[df['lot_id'] == lot_id_target]

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
ax1.quiver(lot_df['field_x'], lot_df['field_y'], lot_df['overlay_x_nm'], lot_df['overlay_y_nm'], 
           angles='xy', scale_units='xy', scale=30, color='r', width=0.005)
ax1.scatter(lot_df['field_x'], lot_df['field_y'], color='black', s=10)
ax1.set_title(f'Raw Overlay Vector Map (Lot {lot_id_target})')
ax1.set_xlim([-1.2, 1.2])
ax1.set_ylim([-1.2, 1.2])
ax1.grid(True, linestyle='--', alpha=0.6)

ax2.quiver(lot_df['field_x'], lot_df['field_y'], lot_df['calc_residual_x'], lot_df['calc_residual_y'], 
           angles='xy', scale_units='xy', scale=30, color='b', width=0.005)
ax2.scatter(lot_df['field_x'], lot_df['field_y'], color='black', s=10)
ax2.set_title(f'Grouped Residual Vector Map (Lot {lot_id_target})')
ax2.set_xlim([-1.2, 1.2])
ax2.set_ylim([-1.2, 1.2])
ax2.grid(True, linestyle='--', alpha=0.6)

plt.tight_layout()
plt.savefig(os.path.join(artifact_dir, 'wafer_map_grouped.png'), dpi=300)
plt.close()

fig, ax = plt.subplots(figsize=(8, 6))
scatter = ax.scatter(df['align_quality'], df['calc_residual_nm'], c=(df['spec_pass']=='FAIL'), cmap='coolwarm', alpha=0.6)
ax.set_xlabel('Align Quality')
ax.set_ylabel('Calculated Residual (nm)')
ax.set_title('Grouped Residual vs Align Quality (Red=FAIL, Blue=PASS)')
ax.grid(True, linestyle='--', alpha=0.6)
plt.savefig(os.path.join(artifact_dir, 'align_quality_vs_residual_grouped.png'), dpi=300)
plt.close()

# 5. Extract Findings based on New Residuals
print("\n--- Counterexamples: High Grouped Residual (> 10nm) BUT Bad Align Quality (> 2.0) ---")
counter_examples = df[(df['calc_residual_nm'] > 10.0) & (df['align_quality'] > 2.0)]
print(f"Found {len(counter_examples)} counterexamples.")
print(counter_examples[['sample_id', 'tool_id', 'reticle_id', 'field_x', 'field_y', 'align_quality', 'calc_residual_nm']])

print("\n--- True Process Issues: High Grouped Residual (> 10nm) WITH GOOD Metrology Quality (0.7 ~ 1.1) ---")
true_process_issues = df[(df['calc_residual_nm'] > 10.0) & 
                         (df['align_quality'] >= 0.7) &
                         (df['align_quality'] <= 1.1)]
print(f"Found {len(true_process_issues)} points.")
if len(true_process_issues) > 0:
    true_process_issues['is_edge'] = (abs(true_process_issues['field_x']) > 0.8) | (abs(true_process_issues['field_y']) > 0.8)
    edge_ratio = true_process_issues['is_edge'].mean() * 100
    print(f"Percentage located at wafer Edge: {edge_ratio:.1f}%")

