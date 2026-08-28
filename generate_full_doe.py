import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import statsmodels.api as sm
from statsmodels.formula.api import ols
import scipy.stats as stats
from mpl_toolkits.mplot3d import Axes3D

# 한글 폰트 및 스타일 설정
plt.style.use('default')
sns.set_theme(style="whitegrid")
plt.rcParams['font.family'] = 'Malgun Gothic'
plt.rcParams['axes.unicode_minus'] = False

# 1. 2^3 Full Factorial Design 시뮬레이션 데이터 생성
np.random.seed(42)
feed_rate = [-1, 1] * 4
rpm = [-1, -1, 1, 1] * 2
pressure = [-1, -1, -1, -1, 1, 1, 1, 1]

doe_data = []
for rep in range(3):
    for f, r, p in zip(feed_rate, rpm, pressure):
        y = 3.5 + 1.2*f - 0.5*r + 1.8*p + 0.9*(f*p) - 0.2*(f*r) - 0.3*(r*p) + np.random.normal(0, 0.4)
        doe_data.append({'Feed_Rate': f, 'RPM': r, 'Pressure': p, 'Crack_Count': max(0, y)})

df_doe = pd.DataFrame(doe_data)
# 1. 디자인 매트릭스 저장
df_doe.to_csv('BG_analysis_output/12_doe_design_matrix.csv', index=False)

# OLS 모델 피팅
model = ols('Crack_Count ~ Feed_Rate * RPM * Pressure', data=df_doe).fit()

# 2. Pareto Chart of Standardized Effects
t_values = model.tvalues.drop('Intercept').abs().sort_values(ascending=True)
critical_t = stats.t.ppf(1 - 0.025, model.df_resid) # alpha=0.05, two-tailed

plt.figure(figsize=(10, 6))
bars = plt.barh(t_values.index, t_values.values, color='steelblue')
plt.axvline(x=critical_t, color='red', linestyle='--', label=f'유의수준 (t={critical_t:.2f})')
plt.title('파레토 차트 (Pareto Chart of the Standardized Effects)', fontsize=16, fontweight='bold')
plt.xlabel('표준화된 효과 (Absolute t-value)')
plt.ylabel('요인 및 교호작용')
plt.legend()
plt.tight_layout()
plt.savefig('BG_analysis_output/13_doe_pareto_chart.png', dpi=300)
plt.close()

# 3. Residual 4-in-1 Plots
fig = plt.figure(figsize=(12, 10))
fig.suptitle('잔차 분석도 (Residual 4-in-1 Plots)', fontsize=16, fontweight='bold')

# 정규확률도 (Normal Probability Plot)
ax1 = fig.add_subplot(221)
stats.probplot(model.resid, dist="norm", plot=ax1)
ax1.set_title("정규확률도 (Normal Probability Plot)")

# 잔차 대 적합치 (Residuals vs Fits)
ax2 = fig.add_subplot(222)
ax2.scatter(model.fittedvalues, model.resid, alpha=0.7)
ax2.axhline(0, color='red', linestyle='--')
ax2.set_xlabel("적합치 (Fitted Value)")
ax2.set_ylabel("잔차 (Residual)")
ax2.set_title("잔차 대 적합치 (Residuals vs Fits)")

# 잔차 히스토그램 (Histogram)
ax3 = fig.add_subplot(223)
sns.histplot(model.resid, kde=True, ax=ax3)
ax3.set_xlabel("잔차 (Residual)")
ax3.set_title("히스토그램 (Histogram)")

# 잔차 대 순서 (Residuals vs Order)
ax4 = fig.add_subplot(224)
ax4.plot(model.resid.index, model.resid, marker='o', linestyle='-', alpha=0.7)
ax4.axhline(0, color='red', linestyle='--')
ax4.set_xlabel("관측 순서 (Observation Order)")
ax4.set_ylabel("잔차 (Residual)")
ax4.set_title("잔차 대 순서 (Residuals vs Order)")

plt.tight_layout(rect=[0, 0.03, 1, 0.95])
plt.savefig('BG_analysis_output/14_doe_residual_plots.png', dpi=300)
plt.close()

# 4. Contour Plot (등고선도) - RPM은 최적값인 1(High)로 고정
f_grid = np.linspace(-1.5, 1.5, 100)
p_grid = np.linspace(-1.5, 1.5, 100)
F, P = np.meshgrid(f_grid, p_grid)
# 수식: 3.5 + 1.2*F - 0.5*(1) + 1.8*P + 0.9*(F*P) - 0.2*(F*1) - 0.3*(1*P)
# = 3.0 + 1.0*F + 1.5*P + 0.9*F*P
Z = 3.0 + 1.0*F + 1.5*P + 0.9*F*P

plt.figure(figsize=(8, 6))
contour = plt.contourf(F, P, Z, levels=15, cmap='coolwarm')
cbar = plt.colorbar(contour)
cbar.set_label('예상 Crack Count')
plt.title('등고선도 (Contour Plot of Crack Count)\n[Spindle RPM = High 고정]', fontsize=16, fontweight='bold')
plt.xlabel('Feed Rate (이송 속도, Coded)')
plt.ylabel('가공 압력 (Pressure, Coded)')
# 최적점 표시 (Feed=-1, Pressure=-1)
plt.plot(-1, -1, marker='*', color='yellow', markersize=15, markeredgecolor='black', label='최적 조건 (Sweet Spot)')
plt.legend(loc='upper left')
plt.tight_layout()
plt.savefig('BG_analysis_output/15_doe_contour_plot.png', dpi=300)
plt.close()

# 5. 3D Surface Plot (표면도)
fig = plt.figure(figsize=(10, 8))
ax = fig.add_subplot(111, projection='3d')
surf = ax.plot_surface(F, P, Z, cmap='coolwarm', edgecolor='none', alpha=0.9)
fig.colorbar(surf, shrink=0.5, aspect=5, label='예상 Crack Count')
ax.set_title('3D 표면도 (Surface Plot of Crack Count)', fontsize=16, fontweight='bold')
ax.set_xlabel('Feed Rate')
ax.set_ylabel('Pressure')
ax.set_zlabel('Crack Count')
# 시점 조정
ax.view_init(elev=25, azim=-45)
plt.tight_layout()
plt.savefig('BG_analysis_output/16_doe_surface_plot.png', dpi=300)
plt.close()

print("All advanced DOE figures generated successfully.")
