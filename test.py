import pandas as pd
try:
    df = pd.read_excel('saw_analysis_output/20000_BGTTV.xlsx', sheet_name='통합_불량데이터_20000')
    
    ic = df[df['SAW_SPC_Status'] == 'In_Control']['SAW_Xbar_um'].dropna()
    ooc = df[df['SAW_SPC_Status'] == 'Out_of_Control']['SAW_Xbar_um'].dropna()
    
    print(f"IC count: {len(ic)}, OOC count: {len(ooc)}")
    if len(ic) > 0 and len(ooc) > 0:
        print(f"IC Xbar Mean: {ic.mean():.4f}, Std: {ic.std():.4f}")
        print(f"OOC Xbar Mean: {ooc.mean():.4f}, Std: {ooc.std():.4f}")
        print(f"IC Xbar Min: {ic.min():.4f}, Max: {ic.max():.4f}")
        print(f"OOC Xbar Min: {ooc.min():.4f}, Max: {ooc.max():.4f}")
except Exception as e:
    print(f"Error: {e}")
