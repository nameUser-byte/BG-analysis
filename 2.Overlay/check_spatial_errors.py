import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os

artifact_dir = r'C:\Users\chan\.gemini\antigravity\brain\1c047f30-a8c7-4f6f-829a-34f88253bc02'
df = pd.read_csv('data/processed/overlay_A_train_grouped_residuals.csv')

df['is_edge'] = (abs(df['field_x']) > 0.8) | (abs(df['field_y']) > 0.8)

threshold = df['align_quality'].quantile(0.95)
print(f"95th percentile of align_quality: {threshold:.2f}")

bad_align = df[df['align_quality'] > threshold]

# 1. Spatial Scatter Plot of Align Quality
plt.figure(figsize=(10, 8))
plt.scatter(df['field_x'], df['field_y'], c='lightgray', alpha=0.5, label='Normal Quality', s=10)
scatter = plt.scatter(bad_align['field_x'], bad_align['field_y'], 
                      c=bad_align['align_quality'], cmap='Reds', 
                      edgecolors='black', s=50, label='Poor Quality (Error)')
plt.colorbar(scatter, label='Align Quality Score')
plt.title('Spatial Distribution of Metrology Errors (Poor Align Quality)')
plt.xlabel('field_x')
plt.ylabel('field_y')
plt.xlim([-1.2, 1.2])
plt.ylim([-1.2, 1.2])
plt.grid(True, linestyle='--', alpha=0.6)
plt.legend()
plt.tight_layout()
plt.savefig(os.path.join(artifact_dir, 'spatial_metrology_errors.png'), dpi=300)
plt.close()

# 2. Check if edge has more errors
edge_error_rate = df[df['is_edge']]['align_quality'].mean()
center_error_rate = df[~df['is_edge']]['align_quality'].mean()

print(f"Average Align Quality at Edge: {edge_error_rate:.3f}")
print(f"Average Align Quality at Center: {center_error_rate:.3f}")

severe_edge = len(bad_align[bad_align['is_edge']])
severe_center = len(bad_align[~bad_align['is_edge']])
print(f"Severe errors at Edge: {severe_edge} (out of {len(df[df['is_edge']])} edge points)")
print(f"Severe errors at Center: {severe_center} (out of {len(df[~df['is_edge']])} center points)")

# 3. Hexbin plot for all data continuous
plt.figure(figsize=(10, 8))
hb = plt.hexbin(df['field_x'], df['field_y'], C=df['align_quality'], gridsize=15, cmap='YlOrRd', reduce_C_function=np.mean)
plt.colorbar(hb, label='Mean Align Quality')
plt.title('Heatmap of Mean Align Quality across Wafer')
plt.xlabel('field_x')
plt.ylabel('field_y')
plt.xlim([-1.2, 1.2])
plt.ylim([-1.2, 1.2])
plt.tight_layout()
plt.savefig(os.path.join(artifact_dir, 'spatial_align_heatmap.png'), dpi=300)
plt.close()
