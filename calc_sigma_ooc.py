import pandas as pd
import numpy as np

# Load data
df = pd.read_excel('saw_analysis_output/20000_BGTTV.xlsx', sheet_name=1)

# Drop missing values for these columns to be safe
df = df.dropna(subset=['SAW_Xbar_um', 'SAW_Range_um', 'SAW_SPC_Status'])

# Calculate Mean and Std
xbar_mean = df['SAW_Xbar_um'].mean()
xbar_std = df['SAW_Xbar_um'].std()

range_mean = df['SAW_Range_um'].mean()
range_std = df['SAW_Range_um'].std()

def get_ooc_count(sigma_level):
    xbar_ooc = (df['SAW_Xbar_um'] > xbar_mean + sigma_level * xbar_std) | (df['SAW_Xbar_um'] < xbar_mean - sigma_level * xbar_std)
    range_ooc = (df['SAW_Range_um'] > range_mean + sigma_level * range_std) | (df['SAW_Range_um'] < range_mean - sigma_level * range_std)
    combined_ooc = xbar_ooc | range_ooc
    return combined_ooc.sum(), (combined_ooc.sum() / len(df)) * 100

print(f"Total valid rows: {len(df)}")
original_ooc = (df['SAW_SPC_Status'] == 'Out_of_Control').sum()
print(f"Original OOC Count (from column): {original_ooc} ({original_ooc/len(df)*100:.2f}%)")

for sig in [3, 2, 1]:
    cnt, rate = get_ooc_count(sig)
    print(f"{sig}-Sigma OOC Count: {cnt} ({rate:.2f}%)")

# Let's also check if "Blade Wear" correlation with OOC changes across these sigmas!
# Since the story was "Blade wear doesn't cause OOC directly (p=0.615)", does that change if OOC threshold is tighter?

bins = [30, 60, 90, 100, np.inf]
labels = ['30~60%', '60~90%', '90~100%', '100% 초과']
df['Wear_Bin'] = pd.cut(df['SAW_Blade_Wear_pct'], bins=bins, labels=labels, right=False)

from scipy.stats import chi2_contingency

for sig in [3, 2, 1]:
    xbar_ooc = (df['SAW_Xbar_um'] > xbar_mean + sig * xbar_std) | (df['SAW_Xbar_um'] < xbar_mean - sig * xbar_std)
    range_ooc = (df['SAW_Range_um'] > range_mean + sig * range_std) | (df['SAW_Range_um'] < range_mean - sig * range_std)
    df[f'OOC_{sig}sig'] = xbar_ooc | range_ooc

    grouped = df.dropna(subset=['Wear_Bin']).groupby('Wear_Bin', observed=False).agg(
        Total_Count=(f'OOC_{sig}sig', 'count'),
        OOC_Count=(f'OOC_{sig}sig', 'sum')
    )
    grouped = grouped[grouped['Total_Count'] > 0]
    grouped['IC_Count'] = grouped['Total_Count'] - grouped['OOC_Count']
    contingency_table = grouped[['OOC_Count', 'IC_Count']].values
    chi2, p_val, dof, expected = chi2_contingency(contingency_table)
    print(f"  {sig}-Sigma Chi-square p-value across Wear Bins: {p_val:.4f}")

