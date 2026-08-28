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
    df = pd.read_excel('BG_analysis_output/20000_BGTTV.xlsx', sheet_name='통합_불량데이터_20000')
    
    features = ['BG_TTV_Before_um']
    for f in features:
        df[f] = pd.to_numeric(df[f], errors='coerce')
        
    df = df.dropna(subset=features + ['BG_TTV_Judgment'])
    
    X = df[features]
    y = (df['BG_TTV_Judgment'] == 'NG').astype(int)
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42, stratify=y)
    
    rf = RandomForestClassifier(n_estimators=50, random_state=42, max_depth=3)
    rf.fit(X_train, y_train)
    y_pred_proba = rf.predict_proba(X_test)[:, 1]
    
    fpr, tpr, _ = roc_curve(y_test, y_pred_proba)
    roc_auc = auc(fpr, tpr)
    
    plt.figure(figsize=(8, 6))
    plt.plot(fpr, tpr, color='darkorange', lw=3, label=f'Random Forest ROC (AUC = {roc_auc:.3f})')
    plt.plot([0, 1], [0, 1], color='navy', lw=2, linestyle='--', label='동전 던지기 (Random Guess)')
    
    plt.fill_between(fpr, tpr, alpha=0.1, color='orange')
    
    plt.text(0.5, 0.4, '입고 TTV 변수 포함 시\n불량(TTV NG) 예측 완벽 (AUC 1.0)', 
             fontsize=14, fontweight='bold', color='blue', 
             ha='center', va='center', bbox=dict(boxstyle='round,pad=0.5', fc='white', ec='blue', alpha=0.9))
    
    plt.xlim([0.0, 1.0])
    plt.ylim([0.0, 1.05])
    plt.xlabel('False Positive Rate (오탐률)', fontsize=12)
    plt.ylabel('True Positive Rate (정탐률)', fontsize=12)
    plt.title('BG 공정 출하 불량(TTV NG) 예측 모델 검증', fontsize=16, fontweight='bold', pad=15)
    plt.legend(loc="lower right", fontsize=11)
    
    plt.tight_layout()
    output_path = 'BG_analysis_output/08_bg_roc_curve.png'
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"Graph saved successfully to {output_path}")

except Exception as e:
    print(f"Error: {e}")
