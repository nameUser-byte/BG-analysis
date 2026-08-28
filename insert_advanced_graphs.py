import re

html_path = 'C:/Users/chan/Documents/temp_project/index.html'
with open(html_path, 'r', encoding='utf-8') as f:
    html = f.read()

new_section = """
<section id="step8" class="section step-card" style="margin-top: 48px;">
  <div class="section-head">
    <span class="kicker">08 / ADVANCED GRAPHS</span>
    <div>
      <h2>추가로 활용하기 좋은 고급 통계 그래프</h2>
      <p>이러한 고급 통계 그래프도 파이썬 데이터 시각화 라이브러리(Seaborn, Plotly 등)를 통해 언제든 활용할 수 있습니다.</p>
    </div>
  </div>
  <div class="detail-grid" style="display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 24px; margin-top: 24px;">
    <section class="detail-block" style="background: var(--surface); padding: 24px; border-radius: 12px; border: 1px solid var(--border);">
      <h4 style="margin-top:0; color: var(--text);">1. 바이올린 플롯 (Violin Plot)</h4>
      <p style="font-size: 14px; color: var(--text-dim);"><strong>특징:</strong> Box plot과 데이터의 밀도(KDE)를 양옆으로 데칼코마니처럼 합친 그래프입니다.</p>
      <p style="font-size: 14px; color: var(--text-dim); margin-bottom: 0;"><strong>활용처:</strong> 단순한 평균/분산뿐만 아니라 데이터가 쌍봉형(낙타 등 모양)인지, 한쪽으로 쏠렸는지(Skewness) 굴곡을 정확히 볼 수 있습니다. 예) 특정 Tool(설비)에서 불량 데이터가 특정 구간에 군집해 있는지 확인할 때 탁월합니다.</p>
    </section>
    <section class="detail-block" style="background: var(--surface); padding: 24px; border-radius: 12px; border: 1px solid var(--border);">
      <h4 style="margin-top:0; color: var(--text);">2. 조인트 플롯 / 마지널 산점도</h4>
      <p style="font-size: 14px; color: var(--text-dim);"><strong>특징:</strong> 가운데는 산점도나 헥스빈(Hexbin)을 두고, 위쪽과 오른쪽에 변수의 히스토그램을 덧붙인 형태입니다.</p>
      <p style="font-size: 14px; color: var(--text-dim); margin-bottom: 0;"><strong>활용처:</strong> 'RF Bias와 식각 선택비'처럼 두 변수의 상관관계(가운데)와 각각의 쏠림 현상(가장자리 분포)을 한눈에 파악하고 싶을 때 매우 효과적입니다.</p>
    </section>
    <section class="detail-block" style="background: var(--surface); padding: 24px; border-radius: 12px; border: 1px solid var(--border);">
      <h4 style="margin-top:0; color: var(--text);">3. 페어 플롯 (Pair Plot)</h4>
      <p style="font-size: 14px; color: var(--text-dim);"><strong>특징:</strong> 여러 개의 변수들을 NxN 행렬 형태로 모두 짝지어 산점도와 히스토그램을 한 번에 그려주는 그래프입니다.</p>
      <p style="font-size: 14px; color: var(--text-dim); margin-bottom: 0;"><strong>활용처:</strong> 가스량, 압력, 온도, RF 파워 등 주요 공정 변수 간의 다차원적 관계를 그물망처럼 스캔할 때 초기 분석용으로 최적입니다.</p>
    </section>
    <section class="detail-block" style="background: var(--surface); padding: 24px; border-radius: 12px; border: 1px solid var(--border);">
      <h4 style="margin-top:0; color: var(--text);">4. 평행 좌표계 플롯</h4>
      <p style="font-size: 14px; color: var(--text-dim);"><strong>특징:</strong> 여러 세로축(변수)을 가로로 나열하고, 하나의 웨이퍼 데이터를 하나의 선(Line)으로 연결하여 그리는 그래프입니다.</p>
      <p style="font-size: 14px; color: var(--text-dim); margin-bottom: 0;"><strong>활용처:</strong> "과식각 불량이 발생한 웨이퍼들은 압력이 높고, 온도가 낮고, 플라즈마 파워가 튄다" 같은 복합적인 불량 레시피 패턴을 추적선 형태로 찾아낼 때 직관적입니다.</p>
    </section>
    <section class="detail-block" style="background: var(--surface); padding: 24px; border-radius: 12px; border: 1px solid var(--border);">
      <h4 style="margin-top:0; color: var(--text);">5. 경험적 누적 분포 함수 (ECDF Plot)</h4>
      <p style="font-size: 14px; color: var(--text-dim);"><strong>특징:</strong> 막대(Bin) 크기에 따라 모양이 변하는 단점을 극복하고, 데이터를 순서대로 누적(0%~100%)하여 선으로 그린 그래프입니다.</p>
      <p style="font-size: 14px; color: var(--text-dim); margin-bottom: 0;"><strong>활용처:</strong> T01 설비와 T02 설비의 CD Bias 상위 10%가 정확히 어느 수치부터 갈라지는지 수학적으로 명확하게 비교할 때 쓰입니다.</p>
    </section>
  </div>
</section>
"""

# Find the end of 07 / VISUAL LANGUAGE section
pattern = r'(07 / VISUAL LANGUAGE.*?</section>)'
match = re.search(pattern, html, re.DOTALL)

if match:
    # Insert new section right after the match
    original_match = match.group(1)
    new_html = html.replace(original_match, original_match + '\n' + new_section)
    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(new_html)
    
    # Update the original project repo as well
    local_html = 'C:/Users/chan/Documents/semiconductor-ai-project/초기설정/AI_주제.html'
    try:
        with open(local_html, 'r', encoding='utf-8') as f:
            local = f.read()
        local_match = re.search(pattern, local, re.DOTALL)
        if local_match:
            local = local.replace(local_match.group(1), local_match.group(1) + '\n' + new_section)
            with open(local_html, 'w', encoding='utf-8') as f:
                f.write(local)
    except:
        pass

    print("Advanced graphs section added successfully.")
else:
    print("Could not find the target section to insert after.")
