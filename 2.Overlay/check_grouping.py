import pandas as pd
from sklearn.linear_model import LinearRegression

df = pd.read_csv('data/processed/overlay_A_train_cleaned.csv')

print("--- Linear Model Coefficients by Tool ID ---")
for tool in df['tool_id'].unique():
    tool_df = df[df['tool_id'] == tool]
    if len(tool_df) < 5:
        continue
    X = tool_df[['field_x', 'field_y']]
    y_x = tool_df['overlay_x_nm']
    y_y = tool_df['overlay_y_nm']
    
    mx = LinearRegression().fit(X, y_x)
    my = LinearRegression().fit(X, y_y)
    print(f"[{tool}] Samples: {len(tool_df)} | Tx: {mx.intercept_:.2f}, Ty: {my.intercept_:.2f}, Sx: {mx.coef_[0]:.2f}, Sy: {my.coef_[1]:.2f}")

print("\n--- Linear Model Coefficients by Reticle ID (for Tool T01) ---")
t1_df = df[df['tool_id'] == 'T01']
for reticle in t1_df['reticle_id'].unique():
    r_df = t1_df[t1_df['reticle_id'] == reticle]
    if len(r_df) < 5:
        continue
    X = r_df[['field_x', 'field_y']]
    y_x = r_df['overlay_x_nm']
    y_y = r_df['overlay_y_nm']
    
    mx = LinearRegression().fit(X, y_x)
    my = LinearRegression().fit(X, y_y)
    print(f"[T01 - Reticle {reticle}] Samples: {len(r_df)} | Tx: {mx.intercept_:.2f}, Ty: {my.intercept_:.2f}, Sx: {mx.coef_[0]:.2f}, Sy: {my.coef_[1]:.2f}")
