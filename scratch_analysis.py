import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os

# Set output directory
out_dir = "C:/Users/chan/.gemini/antigravity/brain/096d8107-72a1-4639-b057-0688c98b6723"
data_path = "c:/Users/chan/Documents/semiconductor-ai-project/3.Dry Etch/dry_etch_A_train_clean.csv"

# Load Data
df = pd.read_csv(data_path)

# Set style
sns.set_theme(style="whitegrid")
plt.rcParams['font.family'] = 'sans-serif' # Avoid missing font warnings for CJK if not configured

# 1. Correlation Matrix
plt.figure(figsize=(10, 8))
corr_cols = ['rf_source_w', 'rf_bias_w', 'pressure_mtorr', 'gas_flow_sccm', 'esc_temp_c', 
             'chamber_age_runs', 'oes_peak_ratio', 'endpoint_slope', 'endpoint_time_s', 
             'cd_bias_nm', 'selectivity', 'overetch_risk']
corr = df[corr_cols].corr()
sns.heatmap(corr, annot=True, cmap='coolwarm', fmt=".2f", vmin=-1, vmax=1)
plt.title("Correlation Matrix of Process Parameters")
plt.tight_layout()
plt.savefig(f"{out_dir}/corr_matrix.png")
plt.close()

# 2. Tool-to-Tool Matching (Boxplot)
plt.figure(figsize=(10, 4))
plt.subplot(1, 2, 1)
sns.boxplot(data=df, x='tool_id', y='cd_bias_nm', order=['T01', 'T02', 'T03', 'T04'])
plt.title("CD Bias by Tool")
plt.subplot(1, 2, 2)
sns.boxplot(data=df, x='tool_id', y='selectivity', order=['T01', 'T02', 'T03', 'T04'])
plt.title("Selectivity by Tool")
plt.tight_layout()
plt.savefig(f"{out_dir}/tool_matching.png")
plt.close()

# 3. Chamber Age vs CD Bias (Drift Analysis)
plt.figure(figsize=(6, 5))
sns.scatterplot(data=df, x='chamber_age_runs', y='cd_bias_nm', hue='tool_id', alpha=0.6)
sns.regplot(data=df, x='chamber_age_runs', y='cd_bias_nm', scatter=False, color='black')
plt.title("Chamber Age vs CD Bias")
plt.tight_layout()
plt.savefig(f"{out_dir}/chamber_age_drift.png")
plt.close()

# 4. RF Bias vs Selectivity
plt.figure(figsize=(6, 5))
sns.scatterplot(data=df, x='rf_bias_w', y='selectivity', hue='tool_id', alpha=0.6)
sns.regplot(data=df, x='rf_bias_w', y='selectivity', scatter=False, color='red')
plt.title("RF Bias Power vs Selectivity")
plt.tight_layout()
plt.savefig(f"{out_dir}/rf_selectivity.png")
plt.close()

# 5. Endpoint Slope vs Overetch Risk
plt.figure(figsize=(6, 5))
sns.scatterplot(data=df, x='endpoint_slope', y='overetch_risk', hue='tool_id', alpha=0.6)
plt.title("EPD Slope vs Overetch Risk")
plt.tight_layout()
plt.savefig(f"{out_dir}/epd_overetch.png")
plt.close()

# Output Key Findings for AI to read
print("=== CORRELATION HIGHLIGHTS ===")
print("Strong correlations with cd_bias_nm:")
print(corr['cd_bias_nm'].sort_values(key=abs, ascending=False).head(5))
print("\nStrong correlations with selectivity:")
print(corr['selectivity'].sort_values(key=abs, ascending=False).head(5))
print("\nStrong correlations with overetch_risk:")
print(corr['overetch_risk'].sort_values(key=abs, ascending=False).head(5))

print("\n=== TOOL DIFFERENCES (Mean) ===")
print(df.groupby('tool_id')[['cd_bias_nm', 'selectivity', 'overetch_risk']].mean())

print("\n=== ALTERNATIVE HYPOTHESIS CHECK ===")
# Is the correlation between Chamber Age and CD Bias just a Tool bias?
for tool in df['tool_id'].unique():
    subset = df[df['tool_id'] == tool]
    if len(subset) > 10:
        c = subset['chamber_age_runs'].corr(subset['cd_bias_nm'])
        print(f"Tool {tool} - Chamber Age vs CD Bias Corr: {c:.2f}")

print("\nPlots generated successfully in out_dir.")
