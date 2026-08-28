import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Set style
plt.style.use('default')
sns.set_theme(style="whitegrid")
plt.rcParams['font.family'] = 'Malgun Gothic'
plt.rcParams['axes.unicode_minus'] = False

try:
    print("Loading data...")
    df = pd.read_excel('saw_analysis_output/20000_BGTTV.xlsx', sheet_name='통합_불량데이터_20000')
    
    df['SAW_Xbar_um'] = pd.to_numeric(df['SAW_Xbar_um'], errors='coerce')
    df['SAW_Range_um'] = pd.to_numeric(df['SAW_Range_um'], errors='coerce')
    df = df.dropna(subset=['SAW_Xbar_um', 'SAW_Range_um', 'SAW_SPC_Status'])
    
    # Calculate IC Control Limits
    ic_df = df[df['SAW_SPC_Status'] == 'In_Control']
    xbar_mean = ic_df['SAW_Xbar_um'].mean()
    xbar_std = ic_df['SAW_Xbar_um'].std()
    x_ucl = xbar_mean + 3 * xbar_std
    x_lcl = xbar_mean - 3 * xbar_std
    
    range_mean = ic_df['SAW_Range_um'].mean()
    range_std = ic_df['SAW_Range_um'].std()
    r_ucl = range_mean + 3 * range_std
    
    # Filter OOC data
    ooc_df = df[df['SAW_SPC_Status'] == 'Out_of_Control'].copy()
    
    # Categorize
    cond_x = (ooc_df['SAW_Xbar_um'] > x_ucl) | (ooc_df['SAW_Xbar_um'] < x_lcl)
    cond_r = (ooc_df['SAW_Range_um'] > r_ucl)
    
    def get_category(row):
        x_out = (row['SAW_Xbar_um'] > x_ucl) or (row['SAW_Xbar_um'] < x_lcl)
        r_out = (row['SAW_Range_um'] > r_ucl)
        if not x_out and not r_out: return 'Unknown Rule'
        if x_out and not r_out: return 'Xbar Only'
        if not x_out and r_out: return 'Range Only'
        return 'Both'
        
    ooc_df['OOC_Type'] = ooc_df.apply(get_category, axis=1)
    
    # Define colors matching user's PPT
    color_map = {
        'Unknown Rule': '#C0504D', # Red/Pink
        'Xbar Only': '#31859C',    # Teal/Dark Cyan
        'Range Only': '#7F7F7F',   # Gray
        'Both': '#1F497D'          # Dark Navy
    }
    
    plt.figure(figsize=(10, 7))
    
    # Plot each category
    for cat in ['Both', 'Range Only', 'Xbar Only', 'Unknown Rule']:
        subset = ooc_df[ooc_df['OOC_Type'] == cat]
        plt.scatter(subset['SAW_Xbar_um'], subset['SAW_Range_um'], 
                    c=color_map[cat], label=cat, alpha=0.7, edgecolors='white', linewidth=0.5, s=30)
                    
    # Draw control limits
    plt.axvline(x_lcl, color='blue', linestyle='--', alpha=0.5, label='Xbar LCL/UCL')
    plt.axvline(x_ucl, color='blue', linestyle='--', alpha=0.5)
    plt.axhline(r_ucl, color='red', linestyle='--', alpha=0.5, label='Range UCL')
    
    # Formatting
    plt.title('OOC 샘플 Xbar vs Range 산점도', fontsize=16, fontweight='bold', pad=15)
    plt.xlabel('SAW Xbar (μm)', fontsize=12)
    plt.ylabel('SAW Range (μm)', fontsize=12)
    
    # Order legend
    handles, labels = plt.gca().get_legend_handles_labels()
    # keep only one line for Xbar
    by_label = dict(zip(labels, handles))
    plt.legend(by_label.values(), by_label.keys(), loc='lower center', ncol=3, bbox_to_anchor=(0.5, -0.2))
    
    plt.tight_layout()
    output_path = 'saw_analysis_output/G24_ooc_scatter_matched.png'
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"Graph saved successfully to {output_path}")

except Exception as e:
    print(f"Error: {e}")
