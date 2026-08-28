import pandas as pd

df = pd.read_csv('data/overlay_A_train.csv')

# Check reticle_id relation to lot_id or tool_id
print("--- Reticle ID vs Lot ID ---")
lot_reticle = df.groupby('lot_id')['reticle_id'].nunique()
print("Lots with more than 1 unique reticle_id:", lot_reticle[lot_reticle > 1].to_dict())

print("\n--- Outlier inspection for ambient_temp_c ---")
temp_outliers = df[(df['ambient_temp_c'] > 30) | (df['ambient_temp_c'] < 10)]
print(temp_outliers[['sample_id', 'ambient_temp_c']])

# Check if > 290 is Kelvin
print("\n--- Kelvin Hypothesis Check ---")
for val in temp_outliers['ambient_temp_c']:
    if val > 273.15:
        print(f"{val} K -> {val - 273.15:.2f} C")

