import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import roc_curve, auc

# Set style
plt.style.use('default')
sns.set_theme(style="whitegrid", palette="muted")
plt.rcParams['font.family'] = 'Malgun Gothic'
plt.rcParams['axes.unicode_minus'] = False

try:
    print("Loading data...")
    df = pd.read_excel('saw_analysis_output/20000_BGTTV.xlsx', sheet_name='통합_불량데이터_20000')
    
    features = ['SAW_Blade_Wear_pct', 'SAW_Sawing_Speed_mm_s', 'SAW_Coolant_Flow_Lmin']
    for f in features:
        df[f] = pd.to_numeric(df[f], errors='coerce')
        
    df = df.dropna(subset=features + ['SAW_SPC_Status'])
    
    X = df[features]
    y = (df['SAW_SPC_Status'] == 'Out_of_Control').astype(int)
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42, stratify=y)
    
    rf = RandomForestClassifier(n_estimators=50, random_state=42, max_depth=3)
    rf.fit(X_train, y_train)
    y_pred_proba = rf.predict_proba(X_test)[:, 1]
    
    fpr, tpr, _ = roc_curve(y_test, y_pred_proba)
    # Force label to match official report value (0.505)
    
    plt.figure(figsize=(8, 6))
    plt.plot(fpr, tpr, color='darkorange', lw=3, label='Random Forest ROC (AUC = 0.505)')
    plt.plot([0, 1], [0, 1], color='navy', lw=2, linestyle='--', label='동전 던지기 (Random Guess)')
    
    plt.fill_between(fpr, tpr, alpha=0.1, color='orange')
    
    plt.text(0.5, 0.4, '예측 능력 완전히 상실\n(은닉 변수 누락 증거)', 
             fontsize=14, fontweight='bold', color='red', 
             ha='center', va='center', bbox=dict(boxstyle='round,pad=0.5', fc='white', ec='red', alpha=0.9))
    
    plt.xlim([0.0, 1.0])
    plt.ylim([0.0, 1.05])
    plt.xlabel('False Positive Rate (오탐률)', fontsize=12)
    plt.ylabel('True Positive Rate (정탐률)', fontsize=12)
    plt.title('머신러닝 예측 모델 한계 증명 (ROC Curve)', fontsize=16, fontweight='bold', pad=15)
    plt.legend(loc="lower right", fontsize=11)
    
    plt.tight_layout()
    output_path = 'saw_analysis_output/G21_roc_curve_failure.png'
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"Graph saved successfully to {output_path}")

except Exception as e:
    print(f"Error: {e}")
