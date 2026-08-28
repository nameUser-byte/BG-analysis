# Semiconductor Overlay AI Analytics

본 프로젝트는 반도체 노광(Lithography) 공정의 오버레이(Overlay) 데이터를 분석하고 계측 불량 및 진짜 공정 불량을 판별하는 데이터 파이프라인입니다. `AGENTS.md`의 필수 규칙을 철저히 준수하여 재현 가능하고 안전하게 개발되었습니다.

## 🚀 프로젝트 목표
- **원인 분리:** 오버레이 오차가 설비/레티클의 하드웨어적 편차인지, 순수 공정 휨인지, 계측기 측정 불량인지 명확히 분리
- **잔차(Residual) 정밀 계산:** 데이터 전체를 뭉뚱그려 해석하지 않고 `tool_id`, `reticle_id` 조합별로 독립된 선형 회귀(Linear Model)를 적용하여 정교한 잔차 도출
- **시각화 리포트:** 100% 독립 실행형(Standalone) `index.html` 리포트로 결과물 제공 (Seaborn, Base64 이미지 내장, MathJax 수식 지원)

## 📁 디렉토리 구조 및 주요 파일
- `data/`: 원본 데이터 파일 (수정 금지 원칙 준수)
- `data/processed/`: 전처리 스크립트를 거친 정제된 데이터 및 잔차 결과 파일
- `preprocess_overlay.py`: 결측치, 온도 이상치(Kelvin 변환 등)를 정제하는 1차 전처리 스크립트
- `analyze_overlay_grouped.py`: `tool_id`, `reticle_id` 기반 그룹핑 선형 회귀 및 잔차를 계산하는 핵심 로직
- `generate_report.py`: `index.html` 결과 보고서 자동 생성 스크립트 (한글 깨짐 방지 적용)
- `index.html`: 분석 시각화 및 검증 증거가 포함된 최종 산출물 리포트

## ⚙️ 실행 방법 (Reproducibility)
해당 분석을 처음부터 재현하기 위한 파이프라인은 아래와 같이 실행합니다.

```bash
# 1. 원본 데이터 정제 및 이상치 보정
python preprocess_overlay.py

# 2. 설비 및 레티클 그룹별 선형 오버레이 모델 피팅 & 잔차 계산
python analyze_overlay_grouped.py

# 3. HTML 최종 종합 보고서 생성
python generate_report.py
```

## ⚠️ 분석 한계점 및 향후 과제 (Limitations)
- **High-Order(비선형) 모델의 부재:** 현재 1차 선형 보정(Linear Model) 파라미터만 분리하고 있습니다. Zernike 다항식 등을 이용한 렌즈 수차 보정 모델을 결합하면 오차율을 더 낮출 수 있습니다.
- **Sparse Sampling 제약:** 웨이퍼 Edge 부근에서 진성 공정 불량이 집중되고 있으나, 데이터 특성 상 샷(Field) 내 여러 포인트가 측정되지 않아 왜곡 형상을 추정하기 힘듭니다. 향후 Intra-field 다점 계측(Dense Sampling) 데이터가 필요합니다.
