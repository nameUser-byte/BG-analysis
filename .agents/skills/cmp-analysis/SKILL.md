---
name: cmp-analysis
description: "반도체 CMP 공정 데이터 분석, 고급 통계 리포트 생성(한글, Base64 이미지, 수식, 모식도, 시뮬레이터 포함)"
---

# CMP 공정 분석 특화 스킬 (cmp-analysis)

이 스킬은 반도체 CMP(Chemical Mechanical Polishing) 데이터를 정제하고 통계 분석을 수행하여, 엔지니어가 실시간으로 사용할 수 있는 **시뮬레이터가 내장된 고급 HTML 리포트(index.html)**를 자동 생성하는 표준화된 작업 절차입니다.

## 📝 필수 생성 규칙 (무조건 지켜야 하는 사항)

1. **단일 HTML (Base64 임베딩):** 생성된 모든 시각화 플롯(Matplotlib, Seaborn 등) 이미지는 디스크에 따로 저장하지 않고, 반드시 Base64 문자열로 인코딩하여 HTML `<img>` 태그 내부에 직접 삽입(`src="data:image/png;base64,..."`)해야 합니다.
2. **한글 폰트(Seaborn) 적용:** 파이썬 코드 상단에 반드시 아래 코드를 삽입하여 한글 깨짐을 방지해야 합니다.
   ```python
   import matplotlib.pyplot as plt
   import seaborn as sns
   plt.rc('font', family='Malgun Gothic')
   plt.rcParams['axes.unicode_minus'] = False
   sns.set_theme(style="whitegrid", font="Malgun Gothic", rc={"axes.unicode_minus": False})
   ```
3. **물리적 수식 (MathJax):** 리포트 HTML 내에 `<script id="MathJax-script" async src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js"></script>`를 추가하고, Preston 방정식($RR = K \times P \times V$) 등 물리적 해석을 수학 수식으로 렌더링해야 합니다.
4. **공정 모식도 (Mermaid.js):** HTML에 Mermaid 스크립트를 추가하고, 패드-슬러리-웨이퍼 간의 물리적/화학적 상호작용 메커니즘을 Flowchart로 삽입해야 합니다.
5. **이미지 확대(Zoom) 기능:** `<img>` 태그를 클릭하면 사진이 커지도록 하는 JS Modal 로직과 CSS(`.zoomable`)를 반드시 HTML 템플릿에 추가해야 합니다.
6. **주석/툴팁 (Tooltips):** Dishing, WIWNU, Pad Age, Pattern Density 등 전문 용어에 CSS Hover 시 설명을 보여주는 툴팁(Tooltip)을 추가해야 합니다.
7. **참고 문헌 (References):** 분석 내용의 학술적 근거를 뒷받침하는 실제 논문(예: Preston 1927, Oliver 2004 등) 인용 리스트를 HTML 하단에 첨부해야 합니다.
8. **공정 시뮬레이터 (JS Simulator):** (가장 중요) 파이썬에서 학습된 OLS 다중 회귀 모델의 회귀 계수(Coefficient) 값들을 HTML JS 코드 블록으로 넘겨주어야 합니다. 사용자가 브라우저에서 '압력, 속도, 패드수명' 등의 파라미터를 입력하면 즉석에서 **제거율, Dishing, 수율을 예측**하고 AI 추천(조치사항)을 내리는 JavaScript 로직과 폼(Input)이 무조건 포함되어야 합니다.
9. **저장 위치:** 분석 리포트는 반드시 공정 번호 폴더(예: `4. CMP/index.html`)에 저장해야 하며, 분석 스크립트는 `scripts/` 디렉토리에 저장해야 합니다.

## 🚀 적용 대상
* 사용자가 CMP 공정 분석을 요구하거나, 파라미터 최적화(추천) 리포트를 만들라고 지시할 때.
* 사용자가 "물리적 의미 해석", "시뮬레이터 추가", "한글 깨짐 방지" 등을 요구할 때.
