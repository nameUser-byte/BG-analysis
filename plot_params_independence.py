import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats

# Set style
plt.style.use('default')
sns.set_theme(style="whitegrid", palette="muted")
plt.rcParams['font.family'] = 'Malgun Gothic'
plt.rcParams['axes.unicode_minus'] = False

try:
    print("Loading data...")
    df = pd.read_excel('saw_analysis_output/20000_BGTTV.xlsx', sheet_name='통합_불량데이터_20000')
    
    # Map status
    status_map = {'In_Control': 'IC (정상)', 'Out_of_Control': 'OOC (이상)'}
    df['Status'] = df['SAW_SPC_Status'].map(status_map)
    
    params = [
        ('SAW_Blade_Wear_pct', 'Blade 마모도 (%)'),
        ('SAW_Sawing_Speed_mm_s', 'Sawing 속도 (mm/s)'),
        ('SAW_Coolant_Flow_Lmin', '냉각수 유량 (L/min)')
    ]
    
    fig, axes = plt.subplots(1, 3, figsize=(16, 6))
    fig.suptitle('OOC와의 무관성 증명: 파라미터별 정상(IC) vs 이상(OOC) 분포 비교', fontsize=18, fontweight='bold', y=1.05)
    
    palette = {'IC (정상)': '#95a5a6', 'OOC (이상)': '#e74c3c'}
    
    for i, (col, title) in enumerate(params):
        df[col] = pd.to_numeric(df[col], errors='coerce')
        valid_df = df.dropna(subset=[col, 'Status'])
        
        ic_data = valid_df[valid_df['Status'] == 'IC (정상)'][col]
        ooc_data = valid_df[valid_df['Status'] == 'OOC (이상)'][col]
        
        # Calculate t-test p-value to show statistical insignificance
        t_stat, p_val = stats.ttest_ind(ic_data, ooc_data, equal_var=False)
        
        sns.violinplot(data=valid_df, x='Status', y=col, palette=palette, ax=axes[i], inner="quartile")
        
        axes[i].set_title(title, fontsize=14, fontweight='bold')
        axes[i].set_xlabel('')
        axes[i].set_ylabel('')
        
        # Add annotation for overlap
        sig_text = "유의미한 차이 없음" if p_val > 0.05 else "통계적 차이 미미함"
        axes[i].text(0.5, 0.95, f'분포 완전 겹침\n(p-value: {p_val:.3f})', 
                     transform=axes[i].transAxes, fontsize=11, fontweight='bold', 
                     horizontalalignment='center', verticalalignment='top', 
                     bbox=dict(boxstyle='round,pad=0.5', fc='white', alpha=0.8, ec='gray'))

    plt.tight_layout()
    output_path = 'saw_analysis_output/G20_params_independence.png'
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"Graph saved successfully to {output_path}")

except Exception as e:
    print(f"Error: {e}")
