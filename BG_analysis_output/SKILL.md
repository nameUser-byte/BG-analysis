---
name: bg-ooc-analysis
description: >
  반도체 후공정 BG(Back Grinding) 공정의 불량 원인 분석, PPTX 주장 타당성 검증,
  공선성 검사, 시각화(Seaborn), MathJax 및 Base64를 활용한 HTML 리포트 자동 생성 워크플로우.
---

# BG 공정 불량 분석 및 검증 스킬

## 1. 개요
사용자가 제시한 `BG 불량분석.pptx`의 주장을 실제 데이터셋(`20000_BGTTV.xlsx`)을 통해 교차 검증하고, 물리적 타당성(Preston's Equation)과 통계적 타당성(VIF 공선성 검사)을 모두 검토하여 인터랙티브 HTML 리포트로 출력하는 워크플로우입니다.

## 2. 사용 방법 (워크플로우)

### Phase 1. PPTX 데이터 추출 및 검증 계획 수립
1. `python-pptx`를 통해 사용자의 프레젠테이션 파일 텍스트 추출
2. 사용자의 핵심 주장 정리 (예: Crack 증가/Scratch 감소, TTV 3.0 이상 99.8% Fail, 상관계수 0.694)
3. 데이터셋과 비교하여 파라미터 누락 확인 (예: Feed Rate/RPM 등은 데이터에 없으나 결론에 포함된 경우)

### Phase 2. 데이터 통계 분석 및 VIF (공선성) 검증
1. `statsmodels`의 `variance_inflation_factor`를 활용해 BG 관련 변수(Crack Before, Scratch Before, TTV Before 등) 간 다중공선성(Multicollinearity) 검사 (기준: VIF < 10)
2. 각 주장에 대한 실제 수치 계산 및 타당성(Valid) 판정 테이블 작성

### Phase 3. 물리적 현상 해석
- **Preston's Equation ($MRR = K \cdot P \cdot V$)** 도입
- Rough Grinding(대량 연삭, SSD 유발)과 Fine Grinding(손상 제거)의 메커니즘을 통해, Scratch 감소와 Crack 증가 현상이 Fine 연삭 불량이 아닌 Rough 데미지의 잔류임을 물리적으로 설명
- 관련 논문 인용(예: *Pei et al. "Machining of silicon wafers"*)

### Phase 4. Seaborn 시각화 (Click to Enlarge)
아래 5가지 필수 시각화를 한글 폰트(`Malgun Gothic` 등)를 적용하여 생성 후, Base64로 변환.
- **Histogram**: TTV 분포 및 꼬리
- **Box + points (Stripplot)**: Tool 판정별 TTV 수치 차이
- **Scatter**: Crack과 TTV 상관관계
- **Line**: 시계열 LOT 단위 이동평균(Moving Average) Drift 분석
- **Heatmap**: 전체 변수 상관구조

### Phase 5. HTML 리포트 생성
- Bootstrap UI 적용
- MathJax CDN으로 방정식($MRR$) 렌더링
- Lightbox JS 적용하여 Base64 인코딩된 Seaborn 이미지의 클릭 확대 지원
- 검증 결과표 및 물리적 도메인 해석 포함

## 3. 실행 방법
프로젝트 루트 경로에서 아래 스크립트를 실행하면 `bg_analysis_report.html`이 자동 생성됩니다.

```bash
python bg_comprehensive_analysis.py
```

## 4. 시사점 및 한계 조치
데이터에 명시적으로 존재하지 않는 설비 파라미터(RPM, 가공 압력 등)를 도메인 지식으로 결론 내린 부분은 매우 훌륭하나, AI 모델 검증 시에는 **"현 데이터로 회귀분석 불가 및 향후 수집 필요 과제"**로 명확히 분리하여 리포팅해야 함을 명시.
