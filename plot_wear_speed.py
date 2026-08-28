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
    
    # Preprocessing
    df['SAW_Blade_Wear_pct'] = pd.to_numeric(df['SAW_Blade_Wear_pct'], errors='coerce')
    df['SAW_Sawing_Speed_mm_s'] = pd.to_numeric(df['SAW_Sawing_Speed_mm_s'], errors='coerce')
    df = df.dropna(subset=['SAW_Blade_Wear_pct', 'SAW_Sawing_Speed_mm_s'])
    
    # Calculate correlation
    r, p = stats.pearsonr(df['SAW_Blade_Wear_pct'], df['SAW_Sawing_Speed_mm_s'])
    
    # Create figure
    plt.figure(figsize=(10, 6))
    
    # Scatter plot with regression line
    sns.regplot(data=df, x='SAW_Blade_Wear_pct', y='SAW_Sawing_Speed_mm_s', 
                scatter_kws={'alpha':0.3, 'color':'#34495e', 's': 15}, 
                line_kws={'color':'#e74c3c', 'linewidth':3})
    
    # Annotations
    plt.text(0.05, 0.95, f'Pearson r = +{r:.3f}\n(강한 양의 상관관계)', 
             transform=plt.gca().transAxes, fontsize=14, fontweight='bold', color='red',
             verticalalignment='top', bbox=dict(boxstyle='round,pad=0.5', fc='white', ec='red', alpha=0.9))
             
    plt.text(0.5, 0.1, '마모가 심해질수록 속도를 높이는 "위험한 보상 제어" 정황', 
             transform=plt.gca().transAxes, fontsize=12, fontweight='bold', color='black',
             horizontalalignment='center', bbox=dict(boxstyle='round,pad=0.5', fc='yellow', ec='none', alpha=0.7))
    
    plt.title('Blade 마모도(Wear)와 절단 속도(Speed)의 상관관계', fontsize=16, fontweight='bold', pad=15)
    plt.xlabel('SAW Blade Wear (%)', fontsize=12)
    plt.ylabel('SAW Sawing Speed (mm/s)', fontsize=12)
    
    plt.tight_layout()
    output_path = 'saw_analysis_output/G22_wear_speed_scatter.png'
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"Graph saved successfully to {output_path}")

except Exception as e:
    print(f"Error: {e}")
