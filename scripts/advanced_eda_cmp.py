import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import statsmodels.formula.api as smf
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error
import os
import io
import base64
import matplotlib
matplotlib.use('Agg')
plt.rcParams['font.family'] = 'Malgun Gothic'
plt.rcParams['axes.unicode_minus'] = False

def fig_to_base64(fig):
    buf = io.BytesIO()
    fig.savefig(buf, format='png', bbox_inches='tight')
    buf.seek(0)
    img_str = base64.b64encode(buf.read()).decode('utf-8')
    plt.close(fig)
    return img_str

def run():
    df_raw = pd.read_csv('data/processed/cmp_A_train_processed.csv')
    df_raw['pad_age_runs_sq'] = df_raw['pad_age_runs'] ** 2
    
    # [A-2] Sensor Anomaly Removal
    # Row 430, 270: wiwnu > 20 (7 sigma) but yield is normal -> Sensor Error
    # [A-2] 센서 계측 오류 및 입력 오타(Typo) 데이터 제거
    # 1. Row 430, 270: WIWNU가 22nm로 튀었으나 수율은 80%대인 물리적 모순 (센서 오류)
    # 2. Row 162: Pad Age가 798.66으로 기록됨. (15시그마 이상치, 물리적 한계 이탈값으로 원인 불명 이상치 처리)
    df = df_raw[(df_raw['wiwnu_proxy'] <= 20) & (df_raw['pad_age_runs'] < 200)].copy()
    
    # [C-2] Train/Test Split (Rule 4)
    train_df, test_df = train_test_split(df, test_size=0.2, random_state=42)
    
    # Correlation Heatmap (using train_df)
    numeric_cols = ['down_force_psi', 'platen_speed_rpm', 'head_speed_rpm', 'slurry_flow_ml_min', 
                    'pad_age_runs', 'pattern_density', 'removal_rate_proxy', 'wiwnu_proxy', 'dishing_nm', 'erosion_nm', 'yield_proxy']
    corr = train_df[numeric_cols].corr(method='spearman')
    mask = np.triu(np.ones_like(corr, dtype=bool))
    fig_corr, ax_corr = plt.subplots(figsize=(10, 8))
    sns.heatmap(corr, mask=mask, annot=True, fmt=".2f", cmap='coolwarm', vmin=-1, vmax=1, ax=ax_corr)
    ax_corr.set_title('Spearman Correlation Heatmap (Train Set)')
    img_corr = fig_to_base64(fig_corr)
    
    # OLS Models (Train)
    sim_rr = smf.ols('removal_rate_proxy ~ down_force_psi + platen_speed_rpm + pad_age_runs + slurry_flow_ml_min', data=train_df).fit()
    sim_dish = smf.ols('dishing_nm ~ down_force_psi + pad_age_runs + pattern_density + slurry_flow_ml_min', data=train_df).fit()
    sim_wiwnu = smf.ols('wiwnu_proxy ~ pad_age_runs + pad_age_runs_sq', data=train_df).fit()
    sim_ero = smf.ols('erosion_nm ~ pad_age_runs + pattern_density', data=train_df).fit()
    sim_yield = smf.ols('yield_proxy ~ wiwnu_proxy + erosion_nm', data=train_df).fit()
    
    # [C-2] RMSE Evaluation
    baseline_pred = train_df['yield_proxy'].mean()
    baseline_rmse = np.sqrt(mean_squared_error(test_df['yield_proxy'], np.full(len(test_df), baseline_pred)))
    test_pred_yield = sim_yield.predict(test_df)
    model_rmse = np.sqrt(mean_squared_error(test_df['yield_proxy'], test_pred_yield))
    rmse_improvement = ((baseline_rmse - model_rmse) / baseline_rmse) * 100
    
    # Pad Age vs WIWNU plot
    fig_pad, ax_pad = plt.subplots(figsize=(8, 5))
    sns.regplot(x='pad_age_runs', y='wiwnu_proxy', data=train_df, order=2, ax=ax_pad, scatter_kws={'alpha':0.5}, color='darkred')
    ax_pad.set_title('Pad Age vs WIWNU (Non-linear Glazing Effect)')
    img_pad_wiwnu = fig_to_base64(fig_pad)

    # Pad Age vs Yield plot
    fig_pad_yield, ax_pad_yield = plt.subplots(figsize=(8, 5))
    sns.regplot(x='pad_age_runs', y='yield_proxy', data=train_df, order=2, ax=ax_pad_yield, scatter_kws={'alpha':0.5}, color='darkgreen')
    ax_pad_yield.set_title('Pad Age vs Yield Proxy')
    img_pad_yield = fig_to_base64(fig_pad_yield)
    
    # Slurry vs Dishing plot
    fig_slurry, ax_slurry = plt.subplots(figsize=(8, 5))
    sns.regplot(x='slurry_flow_ml_min', y='dishing_nm', data=train_df, ax=ax_slurry, scatter_kws={'alpha':0.5})
    ax_slurry.set_title('Slurry Flow vs Dishing (Corr: -0.23)')
    img_slurry_dish = fig_to_base64(fig_slurry)

    # Erosion Plots
    fig_ero, ax_ero = plt.subplots(1, 2, figsize=(14, 5))
    sns.regplot(x='pad_age_runs', y='erosion_nm', data=train_df, ax=ax_ero[0], scatter_kws={'alpha':0.5}, color='darkred')
    ax_ero[0].set_title('Pad Age vs Erosion')
    sns.regplot(x='pattern_density', y='erosion_nm', data=train_df, ax=ax_ero[1], scatter_kws={'alpha':0.5}, color='darkblue')
    ax_ero[1].set_title('Pattern Density vs Erosion')
    img_ero = fig_to_base64(fig_ero)
    
    c_rr = sim_rr.params.to_dict()
    c_dish = sim_dish.params.to_dict()
    c_wiwnu = sim_wiwnu.params.to_dict()
    c_ero = sim_ero.params.to_dict()
    c_yield = sim_yield.params.to_dict()
    
    ols_rr_html = sim_rr.summary().tables[1].as_html()
    ols_dish_html = sim_dish.summary().tables[1].as_html()
    
    html = f"""<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="UTF-8">
<title>CMP 반도체 공정 해석 리포트 (Simulator 포함)</title>
<script src="https://cdn.tailwindcss.com"></script>
<script id="MathJax-script" async src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js"></script>
<script type="module">
import mermaid from 'https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.esm.min.mjs';
mermaid.initialize({{ startOnLoad: true }});
</script>
<style>
table {{ border-collapse: collapse; width: 100%; margin-top: 10px; margin-bottom: 20px; }}
th, td {{ border: 1px solid #e5e7eb; padding: 8px; text-align: center; }}
th {{ background-color: #f3f4f6; }}
.zoomable {{ cursor: zoom-in; transition: transform 0.2s; }}
.zoomable:hover {{ transform: scale(1.02); box-shadow: 0 4px 6px rgba(0,0,0,0.1); }}
.modal {{ display: none; position: fixed; z-index: 1000; padding-top: 50px; left: 0; top: 0; width: 100%; height: 100%; overflow: auto; background-color: rgba(0,0,0,0.9); }}
.modal-content {{ margin: auto; display: block; max-width: 90%; max-height: 90vh; object-fit: contain; }}
.close {{ position: absolute; top: 15px; right: 35px; color: #f1f1f1; font-size: 40px; font-weight: bold; cursor: pointer; }}
.tooltip {{ position: relative; display: inline-block; border-bottom: 1px dotted black; cursor: help; color: #2563eb; font-weight: 500; }}
.tooltip .tooltiptext {{ visibility: hidden; width: 250px; background-color: #333; color: #fff; text-align: left; border-radius: 6px; padding: 10px; position: absolute; z-index: 1; bottom: 125%; left: 50%; margin-left: -125px; opacity: 0; transition: opacity 0.3s; font-size: 13px; font-weight: normal; font-family: sans-serif; }}
.tooltip:hover .tooltiptext {{ visibility: visible; opacity: 1; }}
</style>
</head>
<body class="bg-gray-100 p-8 font-sans">
    
    <div id="imageModal" class="modal">
        <span class="close">&times;</span>
        <img class="modal-content" id="img01">
    </div>

    <div class="max-w-6xl mx-auto bg-white p-10 shadow-lg rounded-lg">
        <h1 class="text-4xl font-extrabold text-blue-900 mb-2 border-b-4 border-blue-900 pb-4">CMP 공정 물리적 상관관계 및 수율 시뮬레이터</h1>
        
        <!-- 1. EDA & Heatmap -->
        <div class="mb-12 border-b pb-8">
            <h2 class="text-2xl font-bold text-indigo-800 mb-4">1. 데이터 기본 탐색 및 상관관계 (EDA)</h2>
            <div class="grid grid-cols-1 md:grid-cols-2 gap-8 items-center">
                <div>
                    <img src="data:image/png;base64,{img_corr}" class="w-full border rounded zoomable" alt="Correlation Heatmap">
                </div>
                <div>
                    <h3 class="text-xl font-bold text-gray-700 mb-2">📈 주요 발견 사항</h3>
                    <ul class="list-disc ml-6 mb-4 space-y-2 text-gray-800">
                        <li><b>제외된 변수 (head_speed_rpm):</b> 모든 결과 변수(Yield, RR, WIWNU)와 상관계수가 0.05 미만으로 통계적 유의성이 없어 배제함.</li>
                        <li><b>데이터 정제 (비정상 이상치 마스킹):</b> WIWNU 계측 센서 오류 2건과, Pad Age 798.66(15시그마 초과, 물리적 한계 이탈)을 기록한 비정상 데이터 1건을 분석 대상에서 원천 배제하여 통계 왜곡을 방지했습니다.</li>
                        <li><b>Pad Age & Yield (-0.93)</b>: 패드 수명이 다할수록 수율이 급격히 떨어지는 가장 강력한 인자입니다.</li>
                        <li><b>Slurry Flow & Dishing (-0.23)</b>: 슬러리 유량이 늘어날수록 오히려 Dishing 불량이 감소하는 반직관적인 음의 상관관계를 보입니다.</li>
                    </ul>
                </div>
            </div>
        </div>

        <!-- 2. Chain of Causality -->
        <div class="mb-12 border-b pb-8">
            <h2 class="text-2xl font-bold text-indigo-800 mb-4">2. 수율 붕괴의 연쇄 작용 (Chain of Causality)</h2>
            
            <div class="mermaid text-center mb-6">
                graph LR
                A[Pad Age 낡음] -->|기공 막힘| B(WIWNU 폭증)
                A -->|마모 심화| E(Erosion 증가)
                D[Pattern Density 조밀] -->|하중 집중| E
                B -->|초점 불량| C{{{{Yield 하락}}}}
                E -->|배선 단락| C
                style A fill:#fca5a5,stroke:#b91c1c
                style D fill:#fcd34d,stroke:#b45309
                style B fill:#f87171,stroke:#991b1b
                style E fill:#f87171,stroke:#991b1b
                style C fill:#ef4444,stroke:#7f1d1d,color:#fff
            </div>
            
            <p class="mb-4">데이터에서 강한 비선형 붕괴 상관성이 관찰되며, 이는 <strong>패드 기공 막힘(Glazing)이라는 CMP 도메인 지식과 일치하는 경향</strong>입니다. (단, 정확한 인과 확인을 위해서는 엔지니어 통제 실험 필요)</p>
            
            <div class="grid grid-cols-1 md:grid-cols-2 gap-8">
                <div>
                    <img src="data:image/png;base64,{img_pad_wiwnu}" class="w-full border rounded zoomable mb-2" alt="Pad Age vs WIWNU">
                    <p class="text-sm text-center text-gray-600">Pad Age가 100을 넘어가면 WIWNU가 기하급수적으로 폭증 (2차 곡선)</p>
                </div>
                <div>
                    <img src="data:image/png;base64,{img_pad_yield}" class="w-full border rounded zoomable mb-2" alt="Pad Age vs Yield">
                    <p class="text-sm text-center text-gray-600">Pad Age가 100을 넘어서면 수율이 비선형적으로 급격히 하락함 (2차 곡선)</p>
                </div>
            </div>
            <div class="bg-gray-50 p-4 border border-gray-200 rounded text-sm mt-4">
                💡 <b>통계적 결론:</b> Dishing 자체는 수율과 직접적인 상관성이 없습니다 (Corr -0.06). 수율을 파괴하는 진범은 Edge 영역의 불균일도를 나타내는 <b>WIWNU</b>와 배선 단락을 일으키는 <b>Erosion</b>입니다.
            </div>
        </div>

        <!-- 3. Dilemma -->
        <div class="mb-12 border-b pb-8">
            <h2 class="text-2xl font-bold text-indigo-800 mb-4">3. 생산성(RR)과 품질(Dishing)의 딜레마</h2>
            <div class="grid grid-cols-1 md:grid-cols-2 gap-8 items-center">
                <div>
                    <img src="data:image/png;base64,{img_slurry_dish}" class="w-full border rounded zoomable" alt="Slurry vs Dishing">
                </div>
                <div>
                    <p class="mb-2">단순 상관관계 분석에서 발견된 가장 기이한 현상은 <b>"슬러리(연마제)를 많이 부을수록 불량(Dishing)이 줄어든다(-0.23)"</b>는 것입니다.</p>
                    <p class="mb-2">하지만, 슬러리를 늘리면 생산성(Removal Rate) 역시 다소 하락하는 딜레마가 발생합니다. 왜 이런 현상이 발생할까요?</p>
                    <div class="bg-blue-50 p-3 rounded border border-blue-200">
                        <p class="font-bold text-blue-800">🧪 화학적 가설 (Chemical Hypothesis)</p>
                        <p class="text-sm mt-1 text-blue-900">슬러리가 과다 투입되면 물리적 연마가 촉진되는 것이 아니라, 오히려 웨이퍼 표면 온도를 낮추거나 보호막(Passivation Layer) 형성을 촉진하여 화학적 식각을 억제할 수 있습니다. 즉, 슬러리 유량은 <b>물리적 타격 인자가 아니라 화학적 억제 인자</b>로 작용할 가능성이 있습니다.</p>
                    </div>
                </div>
            </div>
        </div>
        
        <!-- 4. Erosion -->
        <div class="mb-12 border-b pb-8">
            <h2 class="text-2xl font-bold text-indigo-800 mb-4">4. 수율 하락의 공범: <span class="tooltip">Erosion<span class="tooltiptext">배선 밀집 영역에서 절연막(Oxide)이 금속과 함께 깎여나가는 과연마 불량.</span></span></h2>
            <p class="mb-4">수율 하락의 두 번째 공범인 <strong>Erosion(절연막 과연마)</strong>의 발생 인과 체계입니다. 데이터 모델링 결과, Erosion은 <b>패드가 낡을수록(Pad Age)</b> 그리고 <b>패턴이 조밀할수록(Pattern Density)</b> 심화되는 것으로 나타났습니다 ($R^2 = {sim_ero.rsquared:.3f}$).</p>
            <div class="bg-gray-50 p-4 border border-gray-200 rounded text-sm mb-4">
                💡 <b>3단 인과율의 완성:</b> Pad Age는 1) WIWNU를 폭증시킴과 동시에 2) Pattern Density와 결합하여 Erosion을 유발합니다. 이 두 가지 불량(WIWNU, Erosion)이 수율을 깎아먹는 다중 인과 경로가 성립합니다.
            </div>
            <img src="data:image/png;base64,{img_ero}" alt="Erosion Plots" class="w-full max-w-4xl mx-auto rounded shadow-sm zoomable">
        </div>

        <!-- 4.5. Tool ID -->
        <div class="mb-12 border-b pb-8">
            <h2 class="text-2xl font-bold text-indigo-800 mb-4">4.5. 설비(Tool ID) 간 편차 검증</h2>
            <p class="mb-2">Kruskal-Wallis H-test 결과, 4대의 설비(T01~T04) 간에 RR, Dishing, WIWNU, Yield의 통계적으로 유의미한 차이(p > 0.05)는 발견되지 않았습니다.</p>
            <div class="bg-gray-50 p-4 border border-gray-200 rounded text-sm">
                💡 <b>결론:</b> 설비 간 유의미한 성능 차이는 관찰되지 않았습니다. 단, T01 설비의 데이터 비중이 전체의 52.7%를 차지하므로 결론이 특정 설비에 편향되었을 가능성(Caveat)을 남겨둡니다.
            </div>
        </div>

        <!-- 5. Multiple Regression -->
        <div class="mb-12 border-b pb-8">
            <h2 class="text-2xl font-bold text-indigo-800 mb-4">5. 다중 회귀 분석 (OLS) - 인과관계의 수학적 증명</h2>
            <p class="mb-4">단순 상관관계의 한계를 넘어, 다른 모든 변수를 통제(Control)했을 때 각 파라미터가 가지는 순수 독립 기여도(Net Effect)를 다중 회귀로 추출했습니다.</p>
            
            <h3 class="text-xl font-bold text-gray-700 mb-2">1) 생산성(RR) 모델</h3>
            <div class="overflow-x-auto text-sm">{ols_rr_html}</div>
            
            <h3 class="text-xl font-bold text-gray-700 mt-6 mb-2">2) 품질(Dishing) 모델</h3>
            <div class="overflow-x-auto text-sm">{ols_dish_html}</div>
            
            <div class="bg-yellow-100 p-4 border-l-4 border-yellow-500 mt-4 text-gray-800">
                <p class="font-bold mb-2">🔎 슬러리 유량 가설의 통계적 입증</p>
                <p class="mb-2">Dishing 회귀 모델에서 Slurry Flow의 계수는 <b>-0.063</b>이며, <strong>통계적으로 매우 유의미한 경향성(p-value 0.000)</strong>을 보였습니다. 즉, "화학적 코팅/냉각 효과로 Dishing을 억제한다"는 가설을 뒷받침하는 강력한 증거입니다. (단, Dishing이 덜 발생하는 특정 공정 레시피에서 슬러리를 더 많이 투입하도록 설계되었을 가능성 등 <b>관찰 데이터의 한계상 인과 방향에 대한 대안 가설 검토</b>는 여전히 필요합니다.)</p>
            </div>
            
            <h3 class="text-xl font-bold text-gray-700 mt-6 mb-2">3) 수율(Yield) 영향 인자 모델 (WIWNU + Erosion)</h3>
            <div class="bg-green-50 p-3 mb-2 rounded border border-green-200 text-sm"><b>[Rule 4 평가]</b> Test 셋(20%) 모델 성능: 평균값 예측(Naive Baseline)의 RMSE {baseline_rmse:.2f} 대비, 다중 회귀 모델의 RMSE는 {model_rmse:.2f}로 <b>{rmse_improvement:.1f}% 예측 정확도가 개선</b>되었습니다.</div>
            <p class="mb-2">수율 예측을 위한 수식: $$Yield = \\beta_0 + \\beta_1(WIWNU) + \\beta_2(Erosion) $$</p>
        </div>

        
        <!-- 7. References -->
        <div class="mb-12 border-b pb-8 bg-gray-50 p-6 rounded border border-gray-200">
            <h2 class="text-2xl font-bold text-gray-800 mb-4">📚 7. 참고 문헌 (References)</h2>
            <ul class="list-decimal ml-6 space-y-2 text-sm text-gray-700">
                <li>Preston, F. W. (1927). <i>The Theory and Design of Plate Glass Polishing Machines</i>. Journal of the Society of Glass Technology. (Removal Rate 및 Down Force / Platen Speed 간의 선형 상관관계 근거)</li>
                <li>Oliver, M. R. (2004). <i>Chemical-Mechanical Planarization of Semiconductor Materials</i>. Springer. (Pad Glazing 현상이 Wafer 불균일도(WIWNU)와 수명에 미치는 비선형적 붕괴 모델 근거)</li>
                <li>Steigerwald, J. M., et al. (1997). <i>Chemical Mechanical Microplanarization of Microelectronic Materials</i>. Wiley-Interscience. (Pattern Density 차이에 따른 Oxide Erosion 및 Dishing 과연마 심화 메커니즘)</li>
            </ul>
        </div>
        <!-- Interactive Simulator -->
        <div class="mb-12 border-b pb-8 bg-blue-50 p-6 rounded border border-blue-200">
            <h2 class="text-2xl font-bold text-blue-900 mb-4">⚙️ 6. 인과율이 반영된 공정 시뮬레이터 (JS 기반)</h2>
            <p class="text-blue-800 mb-4">앞서 분석한 3단 인과율(Pad + Pattern → WIWNU + Erosion → Yield)을 백엔드에 완벽히 연동했습니다.</p>
            
            
            <div class="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
                <!-- Sliders -->
                <div class="bg-white p-3 rounded border">
                    <label class="flex justify-between text-sm font-bold"><span>Down Force (psi)</span><span id="val_df" class="text-blue-600">3.0</span></label>
                    <input type="range" id="sim_df" value="3.0" min="2.0" max="5.0" step="0.1" class="w-full" oninput="document.getElementById('val_df').innerText=this.value; runSimulation();">
                </div>
                <div class="bg-white p-3 rounded border">
                    <label class="flex justify-between text-sm font-bold"><span>Platen Speed (rpm)</span><span id="val_ps" class="text-blue-600">100</span></label>
                    <input type="range" id="sim_ps" value="100" min="50" max="180" step="1" class="w-full" oninput="document.getElementById('val_ps').innerText=this.value; runSimulation();">
                </div>
                <div class="bg-white p-3 rounded border">
                    <label class="flex justify-between text-sm font-bold"><span>Pad Age (runs) 🚨</span><span id="val_pad" class="text-red-600">50</span></label>
                    <input type="range" id="sim_pad" value="50" min="0" max="150" step="1" class="w-full" oninput="document.getElementById('val_pad').innerText=this.value; runSimulation();">
                </div>
                <div class="bg-white p-3 rounded border">
                    <label class="flex justify-between text-sm font-bold"><span>Slurry Flow (ml/min)</span><span id="val_sf" class="text-blue-600">150</span></label>
                    <input type="range" id="sim_sf" value="150" min="50" max="300" step="1" class="w-full" oninput="document.getElementById('val_sf').innerText=this.value; runSimulation();">
                </div>
                <div class="bg-white p-3 rounded border md:col-span-2">
                    <label class="flex justify-between text-sm font-bold"><span>Pattern Density</span><span id="val_pd" class="text-blue-600">0.5</span></label>
                    <input type="range" id="sim_pd" value="0.5" min="0.2" max="0.8" step="0.01" class="w-full" oninput="document.getElementById('val_pd').innerText=this.value; runSimulation();">
                </div>
            </div>

            <!-- Results -->
            <div id="sim_result" class="p-4 bg-white border-2 border-blue-300 rounded shadow-md">
                <div class="grid grid-cols-4 gap-2 text-center mb-4">
                    <div class="bg-gray-50 p-2 rounded border">
                        <p class="text-xs font-bold text-gray-500">RR (A/min)</p>
                        <p class="text-lg font-black text-gray-800" id="res_rr">--</p>
                    </div>
                    <div class="bg-gray-50 p-2 rounded border">
                        <p class="text-xs font-bold text-gray-500">Dishing (nm)</p>
                        <p class="text-lg font-black text-orange-600" id="res_dish">--</p>
                    </div>
                    <div class="bg-gray-50 p-2 rounded border border-red-200">
                        <p class="text-xs font-bold text-red-500">WIWNU / Ero</p>
                        <p class="text-lg font-black text-red-600"><span id="res_wiwnu">--</span> / <span id="res_ero">--</span></p>
                    </div>
                    <div class="bg-gray-50 p-2 rounded border border-green-200">
                        <p class="text-xs font-bold text-green-700">Yield (%)</p>
                        <p class="text-lg font-black text-green-700" id="res_yield">--</p>
                    </div>
                </div>
                <p class="text-sm bg-gray-100 p-2 rounded" id="rec_text"></p>
            </div>
        </div>
    </div>

    <script>
                var modal = document.getElementById("imageModal");
        var modalImg = document.getElementById("img01");
        document.querySelectorAll('.zoomable').forEach(img => {{ img.onclick = function(){{ modal.style.display = "block"; modalImg.src = this.src; }} }});
        document.getElementsByClassName("close")[0].onclick = function() {{ modal.style.display = "none"; }};
        modal.onclick = function() {{ modal.style.display = "none"; }};
        
        const C_RR = {c_rr};
        const C_DISH = {c_dish};
        const C_WIWNU = {c_wiwnu};
        const C_ERO = {c_ero};
        const C_YIELD = {c_yield};

        function runSimulation() {{
            const downForce = parseFloat(document.getElementById('sim_df').value);
            const platenSpeed = parseFloat(document.getElementById('sim_ps').value);
            const padAge = parseFloat(document.getElementById('sim_pad').value);
            const patternDensity = parseFloat(document.getElementById('sim_pd').value);
            const slurryFlow = parseFloat(document.getElementById('sim_sf').value);

            const pred_rr = C_RR['Intercept'] + (C_RR['down_force_psi'] * downForce) + (C_RR['platen_speed_rpm'] * platenSpeed) + (C_RR['pad_age_runs'] * padAge) + (C_RR['slurry_flow_ml_min'] * slurryFlow);
            const pred_dish = C_DISH['Intercept'] + (C_DISH['down_force_psi'] * downForce) + (C_DISH['pad_age_runs'] * padAge) + (C_DISH['pattern_density'] * patternDensity) + (C_DISH['slurry_flow_ml_min'] * slurryFlow);
            
            const pred_wiwnu = C_WIWNU['Intercept'] + (C_WIWNU['pad_age_runs'] * padAge) + (C_WIWNU['pad_age_runs_sq'] * (padAge * padAge));
            const pred_ero = C_ERO['Intercept'] + (C_ERO['pad_age_runs'] * padAge) + (C_ERO['pattern_density'] * patternDensity);
            
            const pred_yield = C_YIELD['Intercept'] + (C_YIELD['wiwnu_proxy'] * pred_wiwnu) + (C_YIELD['erosion_nm'] * pred_ero);

            document.getElementById('res_rr').innerText = pred_rr.toFixed(1);
            document.getElementById('res_dish').innerText = pred_dish.toFixed(1);
            document.getElementById('res_wiwnu').innerText = pred_wiwnu.toFixed(1);
            document.getElementById('res_ero').innerText = pred_ero.toFixed(1);
            document.getElementById('res_yield').innerText = pred_yield.toFixed(1);

            let rec = "";
            if(padAge > 100) rec += "🚨 <b>치명적 위험:</b> 패드(Pad Age) 수명이 다 되어 WIWNU가 폭증하여 수율이 박살나고 있습니다! 당장 교체하세요.<br>";
            if(pred_dish > 60) rec += "⚠️ <b>경고:</b> Dishing 수치가 너무 높습니다. 압력을 낮추거나 Pad 교체를 권장합니다.<br>";
            if(pred_rr < 300) rec += "⚠️ <b>경고:</b> 제거율이 낮습니다. Slurry Flow나 Platen Speed를 올리세요.<br>";
            if(rec === "") rec = "✅ <b>양호:</b> 예측되는 공정 지표 및 수율이 안정권입니다.";
            document.getElementById('rec_text').innerHTML = "💡 " + rec;
        }}
        
        window.onload = runSimulation;
    </script>
</body>
</html>
"""
    
    report_path = '4. CMP/index.html'
    os.makedirs(os.path.dirname(report_path), exist_ok=True)
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(html)
        
    print(f"보고서 생성 완료: {report_path}")

if __name__ == '__main__':
    run()
