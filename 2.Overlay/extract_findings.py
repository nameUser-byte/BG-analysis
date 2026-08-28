import pandas as pd
import numpy as np

df = pd.read_csv('data/processed/overlay_A_train_cleaned.csv')

# Use existing residual_nm to find the counterexample S00295
counter = df[df['sample_id'] == 'S00295']
print(counter[['sample_id', 'lot_id', 'field_x', 'field_y', 'align_quality', 'residual_nm', 'spec_pass']])

true_process_issues = df[(df['residual_nm'] > 12.0) & 
                         (df['align_quality'] >= 0.7) &
                         (df['align_quality'] <= 1.0)]

print(true_process_issues[['sample_id', 'field_x', 'field_y', 'align_quality', 'residual_nm', 'spec_pass']])

true_process_issues['is_edge'] = (abs(true_process_issues['field_x']) > 0.8) | (abs(true_process_issues['field_y']) > 0.8)
edge_ratio = true_process_issues['is_edge'].mean() * 100
print(f"Percentage of True Process Issues located at wafer Edge: {edge_ratio:.1f}%")
