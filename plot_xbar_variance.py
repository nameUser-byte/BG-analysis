import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

# Set style
plt.style.use('default')
sns.set_theme(style="whitegrid", palette="muted")
plt.rcParams['font.family'] = 'Malgun Gothic'
plt.rcParams['axes.unicode_minus'] = False

try:
    print("Loading data...")
    df = pd.read_excel('saw_analysis_output/20000_BGTTV.xlsx', sheet_name='통합_불량데이터_20000')
    
    # Data preprocessing
    df['SAW_Xbar_um'] = pd.to_numeric(df['SAW_Xbar_um'], errors='coerce')
    df['SAW_Range_um'] = pd.to_numeric(df['SAW_Range_um'], errors='coerce')
    
    # Map status for cleaner labels
    status_map = {'In_Control': 'IC (In-Control)', 'Out_of_Control': 'OOC (Out-of-Control)'}
    df['Status'] = df['SAW_SPC_Status'].map(status_map)
    df = df.dropna(subset=['SAW_Xbar_um', 'SAW_Range_um', 'Status'])
    
    # Calculate stats for annotations
    ic_xbar_std = df[df['SAW_SPC_Status'] == 'In_Control']['SAW_Xbar_um'].std()
    ooc_xbar_std = df[df['SAW_SPC_Status'] == 'Out_of_Control']['SAW_Xbar_um'].std()
    ic_range_mean = df[df['SAW_SPC_Status'] == 'In_Control']['SAW_Range_um'].mean()
    ooc_range_mean = df[df['SAW_SPC_Status'] == 'Out_of_Control']['SAW_Range_um'].mean()
    
    std_increase = (ooc_xbar_std / ic_xbar_std)
    range_increase = ((ooc_range_mean - ic_range_mean) / ic_range_mean) * 100
    
    # Create Figure
    fig, axes = plt.subplots(1, 2, figsize=(14, 6))
    fig.suptitle('OOC 발생 시 현상: Xbar 분산 폭증 및 Range(산포) 증가', fontsize=18, fontweight='bold', y=1.05)
    
    # Palette colors: IC = Blue, OOC = Red
    palette = {'IC (In-Control)': '#3498db', 'OOC (Out-of-Control)': '#e74c3c'}
    
    # 1. Left Plot: KDE plot for Xbar
    sns.kdeplot(data=df, x='SAW_Xbar_um', hue='Status', fill=True, alpha=0.5, 
                common_norm=False, palette=palette, ax=axes[0], linewidth=2)
    axes[0].set_title('Xbar 분포 (평균은 유지, 표준편차 폭증)', fontsize=14, fontweight='bold', pad=15)
    axes[0].set_xlabel('SAW Xbar (um)', fontsize=12)
    axes[0].set_ylabel('Density', fontsize=12)
    
    # Add annotation for Std increase
    axes[0].text(0.05, 0.95, f'IC Std: {ic_xbar_std:.2f}\nOOC Std: {ooc_xbar_std:.2f}\n→ OOC 시 변동성 {std_increase:.1f}배 폭증!', 
                 transform=axes[0].transAxes, fontsize=11, fontweight='bold', 
                 verticalalignment='top', bbox=dict(boxstyle='round,pad=0.5', fc='yellow', alpha=0.3))

    # 2. Right Plot: Boxplot for Range
    sns.boxplot(data=df, x='Status', y='SAW_Range_um', palette=palette, ax=axes[1], width=0.5, showfliers=False)
    # Add strip plot for details
    sns.stripplot(data=df.sample(min(2000, len(df))), x='Status', y='SAW_Range_um', 
                  color=".25", alpha=0.2, ax=axes[1], size=2)
    
    axes[1].set_title('Range 산포 변화 (단면의 거칠기 증가)', fontsize=14, fontweight='bold', pad=15)
    axes[1].set_xlabel('SPC Status', fontsize=12)
    axes[1].set_ylabel('SAW Range (um)', fontsize=12)
    
    # Add annotation for Range increase
    axes[1].text(0.05, 0.95, f'IC Mean: {ic_range_mean:.2f}\nOOC Mean: {ooc_range_mean:.2f}\n→ OOC 시 Range {range_increase:.1f}% 폭증!', 
                 transform=axes[1].transAxes, fontsize=11, fontweight='bold', 
                 verticalalignment='top', bbox=dict(boxstyle='round,pad=0.5', fc='yellow', alpha=0.3))

    plt.tight_layout()
    output_path = 'saw_analysis_output/G19_xbar_range_variance.png'
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"Graph saved successfully to {output_path}")

except Exception as e:
    print(f"Error: {e}")
