import pandas as pd

file_path = 'data/overlay_A_train.csv'
df = pd.read_csv(file_path)

# Find rows that are exact duplicates across all columns
duplicate_mask = df.duplicated(keep=False)
duplicates_all_cols = df[duplicate_mask].sort_values(by=['sample_id', 'lot_id'])

print("--- Completely identical rows across ALL columns ---")
print(f"Total rows involved: {len(duplicates_all_cols)}")
print(duplicates_all_cols[['sample_id', 'lot_id', 'tool_id', 'sequence', 'ambient_temp_c', 'spec_pass']].to_string())

# Also, let's check if there are duplicated sample_ids that might have different values in other columns
sample_id_duplicates = df[df.duplicated(subset=['sample_id'], keep=False)].sort_values(by=['sample_id'])

print("\n--- Rows with duplicated sample_id (ignoring other columns) ---")
print(f"Total rows involved: {len(sample_id_duplicates)}")
print(sample_id_duplicates[['sample_id', 'lot_id', 'tool_id', 'sequence', 'ambient_temp_c', 'spec_pass']].to_string())
