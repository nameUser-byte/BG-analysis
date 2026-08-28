import pandas as pd
df = pd.read_csv('data/processed/overlay_A_train_grouped_residuals.csv')
print(df[df['sample_id'] == 'S00295'][['sample_id', 'align_quality', 'calc_residual_nm', 'overlay_x_nm', 'overlay_y_nm']])
