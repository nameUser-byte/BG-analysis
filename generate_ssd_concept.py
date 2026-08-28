import matplotlib.pyplot as plt
import numpy as np

plt.style.use('default')
plt.rcParams['font.family'] = 'Malgun Gothic'
plt.rcParams['axes.unicode_minus'] = False

# 가상의 X축 데이터
feed_rate = np.linspace(1, 5, 100)
spindle_rpm = np.linspace(2000, 6000, 100)

# 가상의 Y축 데이터 (논문 트렌드 반영)
# Feed rate가 증가할수록 SSD 깊이는 기하급수적으로 깊어짐
ssd_feed = 2 * (feed_rate ** 1.5) + 5
# RPM이 증가할수록 SSD 깊이는 점차 감소하여 안정화됨
ssd_rpm = 25 * np.exp(-0.0005 * spindle_rpm) + 5

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))

# 그래프 1: Feed Rate vs SSD
ax1.plot(feed_rate, ssd_feed, color='crimson', linewidth=3)
ax1.set_title('이송 속도(Feed Rate)에 따른 SSD 깊이 변화', fontsize=14, fontweight='bold')
ax1.set_xlabel('Feed Rate (㎛/s) \n [낮출수록 유리]', fontsize=12)
ax1.set_ylabel('Sub-Surface Damage (SSD) 깊이 (㎛)', fontsize=12)
ax1.grid(True, linestyle='--', alpha=0.7)
ax1.annotate('Crack 발생 임계점', xy=(3, 15), xytext=(1.5, 20),
             arrowprops=dict(facecolor='black', shrink=0.05), fontsize=11)
ax1.axvspan(1, 2.5, color='lightgreen', alpha=0.3, label='안전 영역 (Sweet Spot)')
ax1.legend()

# 그래프 2: Spindle Speed vs SSD
ax2.plot(spindle_rpm, ssd_rpm, color='royalblue', linewidth=3)
ax2.set_title('회전 속도(Spindle RPM)에 따른 SSD 깊이 변화', fontsize=14, fontweight='bold')
ax2.set_xlabel('Spindle Speed (RPM) \n [높일수록 유리]', fontsize=12)
ax2.set_ylabel('Sub-Surface Damage (SSD) 깊이 (㎛)', fontsize=12)
ax2.grid(True, linestyle='--', alpha=0.7)
ax2.axvspan(4500, 6000, color='lightgreen', alpha=0.3, label='안전 영역 (Sweet Spot)')
ax2.legend()

plt.suptitle('논문 검증: 주요 파라미터가 웨이퍼 표면하 손상(SSD)에 미치는 영향', fontsize=16, fontweight='bold', y=1.05)
plt.tight_layout()

plt.savefig('BG_analysis_output/17_ssd_concept_graph.png', dpi=300, bbox_inches='tight')
plt.close()
print("Concept graph saved.")
