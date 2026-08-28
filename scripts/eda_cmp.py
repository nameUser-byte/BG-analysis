import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import base64
import io
import os
from statsmodels.stats.outliers_influence import variance_inflation_factor

def fig_to_base64(fig):
    buf = io.BytesIO()
    fig.savefig(buf, format='png', bbox_inches='tight', dpi=100)
    buf.seek(0)
    img_base64 = base64.b64encode(buf.read()).decode('utf-8')
    plt.close(fig)
    return img_base64

def generate_eda():
    # 1. 데이터 로드
    df = pd.read_csv('data/processed/cmp_A_train_processed.csv')
    
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    recipe_cols = ['down_force_psi', 'platen_speed_rpm', 'head_speed_rpm', 'slurry_flow_ml_min']
    env_cols = ['pad_age_runs', 'pattern_density']
    
    # 2. 상관관계 히트맵
    fig_corr, ax_corr = plt.subplots(figsize=(12, 10))
    corr = df[numeric_cols].corr(method='spearman')
    sns.heatmap(corr, annot=True, fmt=".2f", cmap='coolwarm', ax=ax_corr, vmin=-1, vmax=1)
    ax_corr.set_title('Spearman Correlation Heatmap (Numeric Variables)')
    img_corr = fig_to_base64(fig_corr)

    # 3. 다중공선성(VIF) 검증
    vif_features = recipe_cols + env_cols
    vif_data = df[vif_features].dropna()
    vif_df = pd.DataFrame()
    vif_df["Feature"] = vif_features
    
    from statsmodels.tools.tools import add_constant
    vif_data_const = add_constant(vif_data)
    
    vifs = []
    for i in range(1, vif_data_const.shape[1]): # 상수항 제외
        vif = variance_inflation_factor(vif_data_const.values, i)
        vifs.append(vif)
    vif_df["VIF"] = vifs
    vif_df = vif_df.sort_values(by="VIF", ascending=False)
    
    vif_html = vif_df.to_html(classes='table table-bordered table-hover', index=False)

    # 4. Tool ID (설비) 간 편차 분석 (Box Plot)
    fig_tool, axes_tool = plt.subplots(1, 2, figsize=(16, 6))
    if 'tool_id' in df.columns:
        sns.boxplot(x='tool_id', y='removal_rate_proxy', data=df, ax=axes_tool[0])
        axes_tool[0].set_title('Removal Rate Distribution by Tool')
        
        sns.boxplot(x='tool_id', y='dishing_nm', data=df, ax=axes_tool[1])
        axes_tool[1].set_title('Dishing Distribution by Tool')
    img_tool = fig_to_base64(fig_tool)

    # 5. 교란 변수 통제 분석 (Rule 5)
    fig_alt, ax_alt = plt.subplots(figsize=(8, 6))
    median_age = df['pad_age_runs'].median()
    df['pad_age_group'] = np.where(df['pad_age_runs'] <= median_age, 'Low Age (New)', 'High Age (Old)')
    
    sns.scatterplot(x='down_force_psi', y='dishing_nm', hue='pad_age_group', data=df, alpha=0.6, ax=ax_alt)
    ax_alt.set_title('Down Force vs Dishing (Controlled by Pad Age)')
    img_alt = fig_to_base64(fig_alt)

    # 6. HTML 리포트 생성
    html_content = f"""
    <!DOCTYPE html>
    <html lang="ko">
    <head>
        <meta charset="UTF-8">
        <title>CMP 공정 데이터 탐색적 분석 (EDA) 리포트</title>
        <style>
            body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin: 40px; line-height: 1.6; color: #333; }}
            .container {{ max-width: 1200px; margin: auto; }}
            .section {{ margin-bottom: 50px; padding: 20px; background: #fff; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
            h1 {{ border-bottom: 2px solid #2c3e50; padding-bottom: 10px; color: #2c3e50; }}
            h2 {{ color: #34495e; }}
            img {{ max-width: 100%; height: auto; border: 1px solid #ddd; border-radius: 4px; }}
            table {{ border-collapse: collapse; width: 50%; margin-top: 20px; }}
            th, td {{ border: 1px solid #ddd; padding: 12px; text-align: left; }}
            th {{ background-color: #f8f9fa; font-weight: bold; }}
            .highlight {{ color: #e74c3c; font-weight: bold; }}
        </style>
    </head>
    <body style="background-color: #f4f6f9;">
        <div class="container">
            <h1>CMP 공정 데이터 탐색적 분석 (EDA) 및 공선성 검증</h1>
            
            <div class="section">
                <h2>1. 상관관계 분석 (Spearman Correlation)</h2>
                <p>수치형 변수들 간의 상관관계를 시각화했습니다. 1에 가까울수록 강한 양의 상관관계, -1에 가까울수록 강한 음의 상관관계를 의미합니다.</p>
                <img src="data:image/png;base64,{img_corr}" alt="Correlation Heatmap">
            </div>

            <div class="section">
                <h2>2. 다중공선성 검증 (Variance Inflation Factor)</h2>
                <p>제어 및 환경 파라미터 간의 다중공선성을 검증합니다. 일반적으로 <span class="highlight">VIF > 10</span> 인 경우 강한 공선성이 존재하여 모델링 시 불안정성을 유발할 수 있습니다.</p>
                {vif_html}
                <p><small>* 수치가 모두 10 미만이라면 제어 변수들이 서로 독립적으로 잘 설정되어 있음을 의미합니다.</small></p>
            </div>

            <div class="section">
                <h2>3. 설비 편차 분석 (Tool Bias)</h2>
                <p>동일한 공정이라도 설비(Tool ID)에 따라 성능(제거율)이나 품질(Dishing)의 차이가 있는지 확인합니다.</p>
                <img src="data:image/png;base64,{img_tool}" alt="Tool Bias Boxplot">
            </div>

            <div class="section">
                <h2>4. 대안 가설 및 교란 변수 점검 (Rule 5 준수)</h2>
                <p>상관관계가 높은 두 변수 (예: 압력과 Dishing) 간의 관계가, 제어할 수 없는 환경 변수(Pad Age)에 의해 교란된 것인지 그룹을 나누어 확인합니다.</p>
                <img src="data:image/png;base64,{img_alt}" alt="Alternative Hypothesis">
                <ul>
                    <li>만약 색상(그룹)별로 뚜렷한 높낮이 차이가 보인다면, Dishing의 주요 원인 중 하나는 압력보다도 'Pad Age(패드 노후도)'일 가능성이 큽니다.</li>
                    <li>이는 <b>상관관계가 인과관계를 보장하지 않는다</b>는 핵심 원칙을 뒷받침합니다.</li>
                </ul>
            </div>
        </div>
    </body>
    </html>
    """
    
    report_path = '4. CMP/index.html'
    os.makedirs(os.path.dirname(report_path), exist_ok=True)
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(html_content)
        
    print(f"EDA 리포트 생성 완료: {report_path}")

if __name__ == '__main__':
    generate_eda()
