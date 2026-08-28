import pandas as pd
import numpy as np

# Load data
df = pd.read_excel('saw_analysis_output/20000_BGTTV.xlsx', sheet_name='통합_불량데이터_20000')

df = df.dropna(subset=['SAW_Xbar_um', 'SAW_Range_um', 'SAW_SPC_Status'])

xbar_mean = df['SAW_Xbar_um'].mean()
xbar_std = df['SAW_Xbar_um'].std()

range_mean = df['SAW_Range_um'].mean()
range_std = df['SAW_Range_um'].std()

# Original 3-sigma rules for classification
df['Xbar_OOC_3sig'] = (df['SAW_Xbar_um'] > xbar_mean + 3*xbar_std) | (df['SAW_Xbar_um'] < xbar_mean - 3*xbar_std)
df['Range_OOC_3sig'] = (df['SAW_Range_um'] > range_mean + 3*range_std) | (df['SAW_Range_um'] < range_mean - 3*range_std)

def classify_ooc(row):
    if not (row['SAW_SPC_Status'] == 'Out_of_Control'):
        return 'Normal'
    if row['Xbar_OOC_3sig'] and row['Range_OOC_3sig']:
        return 'Both'
    elif row['Xbar_OOC_3sig']:
        return 'Xbar Only'
    elif row['Range_OOC_3sig']:
        return 'Range Only'
    else:
        return 'Unknown Rule'

df['OOC_Type_3sig'] = df.apply(classify_ooc, axis=1)

unknown_df = df[df['OOC_Type_3sig'] == 'Unknown Rule'].copy()
print(f"Total Unknown Rule OOCs (under 3-sigma assumption): {len(unknown_df)}")

# Now let's check these 'Unknown Rule' cases against 2-sigma and 1-sigma limits
for sig in [2, 1]:
    xbar_ooc = (unknown_df['SAW_Xbar_um'] > xbar_mean + sig*xbar_std) | (unknown_df['SAW_Xbar_um'] < xbar_mean - sig*xbar_std)
    range_ooc = (unknown_df['SAW_Range_um'] > range_mean + sig*range_std) | (unknown_df['SAW_Range_um'] < range_mean - sig*range_std)
    
    explained = (xbar_ooc | range_ooc).sum()
    pct = explained / len(unknown_df) * 100
    
    xbar_only = (xbar_ooc & ~range_ooc).sum()
    range_only = (~xbar_ooc & range_ooc).sum()
    both = (xbar_ooc & range_ooc).sum()
    
    print(f"\nIf we change the threshold to {sig}-Sigma:")
    print(f"Explained by {sig}-Sigma: {explained} / {len(unknown_df)} ({pct:.1f}%)")
    print(f"  - Xbar Out of {sig}s: {xbar_only}")
    print(f"  - Range Out of {sig}s: {range_only}")
    print(f"  - Both Out of {sig}s: {both}")
