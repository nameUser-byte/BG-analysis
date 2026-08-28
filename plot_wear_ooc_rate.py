import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from scipy.stats import chi2_contingency

plt.style.use('default')
sns.set_theme(style="whitegrid", palette="muted")
plt.rcParams['font.family'] = 'Malgun Gothic'
plt.rcParams['axes.unicode_minus'] = False

try:
    print("Loading data...")
    df = pd.read_excel('saw_analysis_output/20000_BGTTV.xlsx', sheet_name='통합_불량데이터_20000')
    
    df['SAW_Blade_Wear_pct'] = pd.to_numeric(df['SAW_Blade_Wear_pct'], errors='coerce')
    df = df.dropna(subset=['SAW_Blade_Wear_pct', 'SAW_SPC_Status'])
    
    df['Is_OOC'] = (df['SAW_SPC_Status'] == 'Out_of_Control').astype(int)
    
    bins = [30, 60, 90, 100, np.inf]
    labels = ['30~60%', '60~90%', '90~100%', '100% 초과']
    df['Wear_Bin'] = pd.cut(df['SAW_Blade_Wear_pct'], bins=bins, labels=labels, right=False)
    
    # Drop NaNs created by dropping the 0-30% range
    df = df.dropna(subset=['Wear_Bin'])
    
    grouped = df.groupby('Wear_Bin', observed=False).agg(
        Total_Count=('Is_OOC', 'count'),
        OOC_Count=('Is_OOC', 'sum')
    ).reset_index()
    
    # Remove empty bins to avoid chi-square error
    grouped = grouped[grouped['Total_Count'] > 0].copy()
    
    grouped['OOC_Rate'] = (grouped['OOC_Count'] / grouped['Total_Count']) * 100
    grouped['IC_Count'] = grouped['Total_Count'] - grouped['OOC_Count']
    
    contingency_table = grouped[['OOC_Count', 'IC_Count']].values
    
    try:
        chi2, p_val, dof, expected = chi2_contingency(contingency_table)
        sig_text = "유의미한 차이 없음" if p_val > 0.05 else "구간별 차이 유의미함"
        color = "black" if p_val > 0.05 else "red"
        p_val_text = f"p-value = {p_val:.3f}"
    except Exception as e:
        p_val_text = "p-value = N/A (표본 부족)"
        sig_text = ""
        color = "black"
    
    plt.figure(figsize=(10, 6))
    ax = sns.barplot(data=grouped, x='Wear_Bin', y='OOC_Rate', color='#3498db', edgecolor='black')
    
    for i, p in enumerate(ax.patches):
        ax.annotate(f"{grouped['OOC_Rate'].iloc[i]:.1f}%\n(n={grouped['Total_Count'].iloc[i]})", 
                    (p.get_x() + p.get_width() / 2., p.get_height()), 
                    ha='center', va='bottom', fontsize=11, fontweight='bold', color='black', xytext=(0, 5), textcoords='offset points')
                    
    plt.title('Blade 마모 구간별 OOC율 비교', fontsize=16, fontweight='bold', pad=20)
    plt.xlabel('Blade 마모도 (Wear %) 구간', fontsize=12)
    plt.ylabel('OOC 발생률 (%)', fontsize=12)
    
    plt.ylim(0, grouped['OOC_Rate'].max() * 1.6)
    
    plt.text(0.05, 0.95, f'Chi-square 검정\n{p_val_text}\n({sig_text})', 
             transform=plt.gca().transAxes, fontsize=12, fontweight='bold', color=color,
             verticalalignment='top', bbox=dict(boxstyle='round,pad=0.5', fc='white', ec=color, alpha=0.9))
             
    overall_rate = df['Is_OOC'].mean() * 100
    plt.axhline(overall_rate, color='red', linestyle='--', alpha=0.7)
    plt.text(-0.4, overall_rate + 0.3, f'전체 평균 OOC율: {overall_rate:.1f}%', 
             color='red', fontweight='bold', ha='left', va='bottom',
             bbox=dict(boxstyle='round,pad=0.3', fc='white', ec='none', alpha=0.8))

    plt.tight_layout()
    output_path = 'saw_analysis_output/G23_wear_ooc_rate.png'
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"Graph saved successfully to {output_path}")

except Exception as e:
    print(f"Error: {e}")
