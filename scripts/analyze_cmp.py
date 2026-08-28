import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import base64
import io
import os

def fig_to_base64(fig):
    buf = io.BytesIO()
    fig.savefig(buf, format='png', bbox_inches='tight')
    buf.seek(0)
    img_base64 = base64.b64encode(buf.read()).decode('utf-8')
    plt.close(fig)
    return img_base64

def analyze():
    # 1. 데이터 로드
    df = pd.read_csv('data/processed/cmp_A_train_processed.csv')
    
    # 제어 파라미터 및 타겟 파라미터 지정
    recipe_cols = ['down_force_psi', 'platen_speed_rpm', 'head_speed_rpm', 'slurry_flow_ml_min']
    quality_cols = ['wiwnu_proxy', 'dishing_nm', 'erosion_nm']
    productivity_col = 'removal_rate_proxy'
    
    # 2. 다목적 최적화 스코어 (Composite Score) 산출
    # Z-score 정규화
    numeric_df = df.select_dtypes(include=[np.number])
    df_z = (numeric_df - numeric_df.mean()) / numeric_df.std()
    
    # 가성비 스코어 = 생산성 Z - 품질 손실 Z 평균
    df['quality_loss_z_mean'] = df_z[quality_cols].mean(axis=1)
    df['productivity_z'] = df_z[productivity_col]
    df['composite_score'] = df['productivity_z'] - df['quality_loss_z_mean']
    
    # 상위 10% 레시피 마킹
    top_threshold = df['composite_score'].quantile(0.90)
    df['is_top_10'] = df['composite_score'] >= top_threshold

    # 3. 상관관계 분석 (히트맵)
    cols_to_corr = recipe_cols + [productivity_col] + quality_cols + ['pad_age_runs', 'pattern_density']
    corr = df[cols_to_corr].corr(method='spearman')
    
    fig_corr, ax_corr = plt.subplots(figsize=(10, 8))
    sns.heatmap(corr, annot=True, fmt=".2f", cmap='coolwarm', ax=ax_corr, vmin=-1, vmax=1)
    ax_corr.set_title('Spearman Correlation Heatmap')
    img_corr = fig_to_base64(fig_corr)

    # 4. 파레토 산점도 (Trade-off)
    fig_pareto, ax_pareto = plt.subplots(figsize=(8, 6))
    scatter = ax_pareto.scatter(df['quality_loss_z_mean'], df['productivity_z'], 
                                c=df['composite_score'], cmap='viridis', alpha=0.6)
    
    # 상위 10% 강조
    top_df = df[df['is_top_10']]
    ax_pareto.scatter(top_df['quality_loss_z_mean'], top_df['productivity_z'], 
                      facecolors='none', edgecolors='red', s=100, label='Top 10% Recipes')
    
    ax_pareto.set_xlabel('Quality Loss (Z-Score Mean) -> Lower is Better')
    ax_pareto.set_ylabel('Removal Rate (Z-Score) -> Higher is Better')
    ax_pareto.set_title('Pareto Frontier: Quality Loss vs Removal Rate')
    fig_pareto.colorbar(scatter, label='Composite Score')
    ax_pareto.legend()
    img_pareto = fig_to_base64(fig_pareto)

    # 5. 평행 좌표계 (레시피 특성 파악)
    fig_parallel, ax_parallel = plt.subplots(figsize=(10, 6))
    
    # 스케일링하여 평행좌표계에 그리기 쉽게 함 (Min-Max)
    df_minmax = (df[recipe_cols] - df[recipe_cols].min()) / (df[recipe_cols].max() - df[recipe_cols].min())
    df_minmax['is_top_10'] = df['is_top_10']
    
    pd.plotting.parallel_coordinates(df_minmax, 'is_top_10', color=['#AAAAAA', '#FF5555'], alpha=0.3, ax=ax_parallel)
    ax_parallel.set_title('Parallel Coordinates of Recipe Parameters (Red = Top 10%)')
    img_parallel = fig_to_base64(fig_parallel)

    # 6. 대안 가설 검증 (Rule 5)
    # 가설: "압력(down_force)이 높아서 Dishing이 커지는 것이 아니라, 패드 노후도(pad_age)가 높을 때 압력을 높여서 생긴 우연한 상관성일 수 있다."
    median_pad_age = df['pad_age_runs'].median()
    df_low_age = df[df['pad_age_runs'] <= median_pad_age]
    df_high_age = df[df['pad_age_runs'] > median_pad_age]
    
    corr_all = df['down_force_psi'].corr(df['dishing_nm'])
    corr_low = df_low_age['down_force_psi'].corr(df_low_age['dishing_nm'])
    corr_high = df_high_age['down_force_psi'].corr(df_high_age['dishing_nm'])
    
    alt_hypothesis_html = f"""
    <h3>대안 가설 검증 (Rule 5 준수)</h3>
    <p><b>가설:</b> 압력(Down Force)과 Dishing 간의 양의 상관관계가 인과관계를 보장하는가?</p>
    <p><b>대안 가설:</b> 패드 노후도(Pad Age)가 교란 변수일 수 있다. 즉, 패드가 오래될수록 압력을 높이는 레시피를 사용했고, 사실 Dishing의 주원인은 패드 노후도일 수 있다.</p>
    <ul>
        <li>전체 데이터의 압력 vs Dishing 상관계수: {corr_all:.3f}</li>
        <li>새 패드(Pad Age 낮음) 조건에서의 상관계수: {corr_low:.3f}</li>
        <li>오래된 패드(Pad Age 높음) 조건에서의 상관계수: {corr_high:.3f}</li>
    </ul>
    <p><b>결론:</b> 구간을 분리했을 때 상관계수가 낮아진다면 Pad Age의 교란 효과가 존재함을 의미합니다. (상관관계 != 인과관계)</p>
    """

    # Top 10% 레시피 통계
    top_stats = top_df[recipe_cols].describe().to_html(classes='table table-bordered')

    # 7. HTML 리포트 생성 (Rule 10)
    html_content = f"""
    <!DOCTYPE html>
    <html lang="ko">
    <head>
        <meta charset="UTF-8">
        <title>CMP Recipe Optimization Report</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 40px; line-height: 1.6; }}
            .graph-container {{ margin-bottom: 40px; }}
            img {{ max-width: 100%; height: auto; border: 1px solid #ddd; }}
            table {{ border-collapse: collapse; width: 100%; margin-top: 20px; }}
            th, td {{ border: 1px solid #ddd; padding: 8px; text-align: right; }}
            th {{ background-color: #f2f2f2; text-align: center; }}
        </style>
    </head>
    <body>
        <h1>CMP Recipe 최적화 및 Trade-off 분석 리포트</h1>
        <p>본 리포트는 생산성(제거율 극대화)과 품질(손실 최소화)을 동시에 만족하는 레시피를 찾기 위한 분석 결과입니다.</p>
        
        <div class="graph-container">
            <h2>1. 상관관계 분석 (Correlation)</h2>
            <img src="data:image/png;base64,{img_corr}" alt="Correlation Heatmap">
        </div>

        <div class="graph-container">
            <h2>2. 파레토 프론티어 (Trade-off 분석)</h2>
            <p>좌상단으로 갈수록 <b>'제거율 높음 & 품질 손실 적음'</b>을 의미합니다. 붉은 동그라미는 가성비 스코어 상위 10% 레시피입니다.</p>
            <img src="data:image/png;base64,{img_pareto}" alt="Pareto Scatter">
        </div>

        <div class="graph-container">
            <h2>3. 최적 레시피 궤적 (평행 좌표계)</h2>
            <p>상위 10% 성능을 내는 레시피(붉은 선)가 주로 어떤 제어 변수 대역에 위치하는지 보여줍니다. (Min-Max 정규화 됨)</p>
            <img src="data:image/png;base64,{img_parallel}" alt="Parallel Coordinates">
        </div>
        
        <div class="graph-container">
            <h2>4. 상위 10% 레시피 구체적 파라미터 범위 (Recommendation)</h2>
            {top_stats}
        </div>
        
        <div class="graph-container">
            {alt_hypothesis_html}
        </div>
    </body>
    </html>
    """
    
    report_path = '4. CMP/index.html'
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(html_content)
        
    print(f"분석 완료! 리포트가 생성되었습니다: {report_path}")

if __name__ == '__main__':
    analyze()
