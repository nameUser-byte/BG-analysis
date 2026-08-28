import re

html_path = 'C:/Users/chan/Documents/temp_project/index.html'
with open(html_path, 'r', encoding='utf-8') as f:
    html = f.read()

new_ui = """
<section id="advanced-visuals">
  <div class="shell">
    <div class="section-head">
      <span class="index">08 / ADVANCED GRAPHS</span>
      <div>
        <h2>고급 통계 그래프</h2>
        <p>파이썬 시각화 라이브러리를 통해 실무에 즉시 활용할 수 있는 다차원 통계 그래프입니다.</p>
      </div>
    </div>
    <div class="viz-grid">
      <article class="viz">
        <h3 style="margin-top:0; font-size:18px; color:var(--ink);">Violin Plot</h3>
        <p style="font-size:13px;color:var(--text-dim);margin-top:12px;line-height:1.6">Box plot과 데이터 밀도(KDE) 결합. 데이터의 쌍봉형 굴곡 등 쏠림(Skewness) 파악에 특화.</p>
      </article>
      <article class="viz">
        <h3 style="margin-top:0; font-size:18px; color:var(--ink);">Joint Plot</h3>
        <p style="font-size:13px;color:var(--text-dim);margin-top:12px;line-height:1.6">가운데의 상관관계(산점도)와 가장자리 분포(히스토그램)를 한눈에 동시에 스캔.</p>
      </article>
      <article class="viz">
        <h3 style="margin-top:0; font-size:18px; color:var(--ink);">Pair Plot</h3>
        <p style="font-size:13px;color:var(--text-dim);margin-top:12px;line-height:1.6">여러 변수를 NxN 행렬로 짝지어 다차원적 궁합(상관성)을 훑어보는 초기 분석에 최적.</p>
      </article>
      <article class="viz">
        <h3 style="margin-top:0; font-size:18px; color:var(--ink);">Parallel Coord</h3>
        <p style="font-size:13px;color:var(--text-dim);margin-top:12px;line-height:1.6">고위험 웨이퍼들의 복합적인 레시피 패턴(압력, 온도 등)을 추적선(Trace)으로 시각화.</p>
      </article>
      <article class="viz">
        <h3 style="margin-top:0; font-size:18px; color:var(--ink);">ECDF Plot</h3>
        <p style="font-size:13px;color:var(--text-dim);margin-top:12px;line-height:1.6">데이터를 0~100% 누적 선으로 그려 상위 10% 꼬리 부분의 미세한 불량률 차이를 수학적으로 비교.</p>
      </article>
    </div>
  </div>
</section>
"""

# Replace my old insertion
old_pattern = r'<section id="step8" class="section step-card" style="margin-top: 48px;">.*?</section>'
html = re.sub(old_pattern, new_ui.strip(), html, flags=re.DOTALL)

with open(html_path, 'w', encoding='utf-8') as f:
    f.write(html)

# Do the same for local file
local_html = 'C:/Users/chan/Documents/semiconductor-ai-project/초기설정/AI_주제.html'
try:
    with open(local_html, 'r', encoding='utf-8') as f:
        local = f.read()
    local = re.sub(old_pattern, new_ui.strip(), local, flags=re.DOTALL)
    with open(local_html, 'w', encoding='utf-8') as f:
        f.write(local)
except:
    pass

print("UI improved to match site theme.")
