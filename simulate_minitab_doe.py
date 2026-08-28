import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import statsmodels.api as sm
from statsmodels.formula.api import ols

# Set up matplotlib for Korean font and style
plt.style.use('default')
sns.set_theme(style="whitegrid")
plt.rcParams['font.family'] = 'Malgun Gothic'
plt.rcParams['axes.unicode_minus'] = False

# 1. 2^3 Full Factorial Design 시뮬레이션 데이터 생성 (가상의 Minitab DOE 환경)
np.random.seed(42)

# Factors (Low=-1, High=1)
feed_rate = [-1, 1] * 4
rpm = [-1, -1, 1, 1] * 2
pressure = [-1, -1, -1, -1, 1, 1, 1, 1]

# Replications (e.g., 3 reps)
doe_data = []
for rep in range(3):
    for f, r, p in zip(feed_rate, rpm, pressure):
        # Y (Crack Count) = Base + Main Effects + Interactions + Noise
        # Assume Pressure and Feed Rate increase crack, RPM decreases slightly.
        # Strong interaction between Pressure and Feed Rate.
        y = 3.5 + 1.2*f - 0.5*r + 1.8*p + 0.9*(f*p) - 0.2*(f*r) - 0.3*(r*p) + np.random.normal(0, 0.4)
        doe_data.append({'Feed_Rate': f, 'RPM': r, 'Pressure': p, 'Crack_Count': max(0, y)})

df_doe = pd.DataFrame(doe_data)

# Convert coded to actual values for visualization
actual_mapping = {
    'Feed_Rate': {-1: 'Low (1.0)', 1: 'High (3.0)'},
    'RPM': {-1: 'Low (3000)', 1: 'High (5000)'},
    'Pressure': {-1: 'Low (10)', 1: 'High (30)'}
}

# 2. ANOVA (분산분석)
model = ols('Crack_Count ~ Feed_Rate * RPM * Pressure', data=df_doe).fit()
anova_table = sm.stats.anova_lm(model, typ=2)

# 3. Main Effects Plot (주효과도)
fig, axes = plt.subplots(1, 3, figsize=(15, 5))
fig.suptitle('Minitab 스타일 주효과도 (Main Effects Plot for Crack)', fontsize=16, fontweight='bold', y=1.05)

for i, factor in enumerate(['Feed_Rate', 'RPM', 'Pressure']):
    sns.pointplot(x=factor, y='Crack_Count', data=df_doe, ax=axes[i], capsize=.1, color='blue', errorbar=None)
    axes[i].set_title(f'{factor} 주효과')
    axes[i].set_ylabel('평균 Crack Count')
    axes[i].set_xticks([0, 1])
    axes[i].set_xticklabels([actual_mapping[factor][-1], actual_mapping[factor][1]])

plt.tight_layout()
plt.savefig('BG_analysis_output/09_doe_main_effects.png', dpi=300, bbox_inches='tight')
plt.close()

# 4. Interaction Plot (교호작용도 - Pressure vs Feed Rate)
plt.figure(figsize=(8, 6))
sns.pointplot(x='Feed_Rate', y='Crack_Count', hue='Pressure', data=df_doe, dodge=True, markers=['o', 's'], capsize=.1, palette='Set1', errorbar=None)
plt.title('Minitab 스타일 교호작용도 (Interaction: Feed Rate * Pressure)', fontsize=16, fontweight='bold')
plt.xticks([0, 1], [actual_mapping['Feed_Rate'][-1], actual_mapping['Feed_Rate'][1]])
plt.ylabel('평균 Crack Count')
L = plt.legend(title='가공 압력 (Pressure)')
L.get_texts()[0].set_text(actual_mapping['Pressure'][-1])
L.get_texts()[1].set_text(actual_mapping['Pressure'][1])
plt.savefig('BG_analysis_output/10_doe_interaction.png', dpi=300, bbox_inches='tight')
plt.close()

# 5. Prediction / Optimization (반응 표면 최적화 예측)
# Best combination to minimize crack: Feed Rate (-1), RPM (1), Pressure (-1)
best_y = 3.5 + 1.2*(-1) - 0.5*(1) + 1.8*(-1) + 0.9*(-1*-1) - 0.2*(-1*1) - 0.3*(1*-1)
print(f"Optimal Prediction (Crack Count): {best_y:.2f}")

with open('BG_analysis_output/11_doe_anova_result.txt', 'w') as f:
    f.write("=== Minitab Style ANOVA Results ===\n")
    f.write(anova_table.to_string())
    f.write(f"\n\n=== Response Optimizer ===\n")
    f.write(f"최적 조건: Feed_Rate=Low(1.0), RPM=High(5000), Pressure=Low(10)\n")
    f.write(f"예상 불량수(Crack): 평균 {best_y:.2f}개 (기존 평균 3.5개 대비 대폭 감소)\n")

print("DOE analysis simulation completed.")
