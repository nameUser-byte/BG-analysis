import pandas as pd
df = pd.read_csv('data/processed/overlay_A_train_grouped_residuals.csv')
bad_align = df[df['align_quality'] > 0.95]
print(f"Number of points with align_quality > 0.95: {len(bad_align)}")

edge = bad_align[(abs(bad_align['field_x']) > 0.8) | (abs(bad_align['field_y']) > 0.8)]
center = bad_align[~((abs(bad_align['field_x']) > 0.8) | (abs(bad_align['field_y']) > 0.8))]

print(f"Errors (>0.95) at Edge: {len(edge)}")
print(f"Errors (>0.95) at Center: {len(center)}")

# Let's check quadrant
quad1 = len(bad_align[(bad_align['field_x'] > 0) & (bad_align['field_y'] > 0)])
quad2 = len(bad_align[(bad_align['field_x'] < 0) & (bad_align['field_y'] > 0)])
quad3 = len(bad_align[(bad_align['field_x'] < 0) & (bad_align['field_y'] < 0)])
quad4 = len(bad_align[(bad_align['field_x'] > 0) & (bad_align['field_y'] < 0)])
print(f"Q1 (Top-Right): {quad1}, Q2 (Top-Left): {quad2}, Q3 (Bottom-Left): {quad3}, Q4 (Bottom-Right): {quad4}")
