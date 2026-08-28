import pandas as pd
import numpy as np
import logging

# 로깅 설정
logging.basicConfig(
    filename='data/processed/preprocessing.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filemode='w' # 덮어쓰기
)

def main():
    input_path = 'data/cmp_A_train.csv'
    output_path = 'data/processed/cmp_A_train_processed.csv'
    
    logging.info(f"--- Preprocessing Start: {input_path} ---")
    df = pd.read_csv(input_path)
    initial_rows = len(df)
    logging.info(f"0. 원본 데이터 행 수: {initial_rows}")
    
    # 1. 중복 데이터 제거
    df = df.drop_duplicates()
    step1_rows = len(df)
    logging.info(f"1. 완전 일치 중복 데이터 {initial_rows - step1_rows}건 제거. (남은 행: {step1_rows})")
    
    # 2. 수율(yield_proxy) 100% 초과 행 삭제
    yield_outliers = df[df['yield_proxy'] > 100.0]
    df = df[df['yield_proxy'] <= 100.0]
    step2_rows = len(df)
    logging.info(f"2. 수율 100% 초과 데이터 {len(yield_outliers)}건 제거. (남은 행: {step2_rows})")

    # 3. 파라미터별 극단적 이상치 (상/하위 1% 밖) 행 삭제
    outlier_cols = ['down_force_psi', 'platen_speed_rpm', 'head_speed_rpm', 'slurry_flow_ml_min']
    before_outlier_rows = len(df)
    
    for col in outlier_cols:
        # 상위 1% / 하위 1% 기준값 계산 (해당 컬럼의 결측치 제외하고 계산)
        p01 = df[col].quantile(0.01)
        p99 = df[col].quantile(0.99)
        
        # 극단적 이상치가 아닌 정상 데이터이거나, 결측치인 행만 남김
        # (결측치는 다음 단계에서 대체할 것이므로 이상치 판별에서 지우지 않음)
        df = df[(df[col].isna()) | ((df[col] >= p01) & (df[col] <= p99))]
        
    step3_rows = len(df)
    logging.info(f"3. 극단적 이상치 (상/하위 1% 밖) 데이터 {before_outlier_rows - step3_rows}건 제거. (남은 행: {step3_rows})")

    # 4. 결측치(NaN) 중간값 대체
    # 결측치가 있는 수치형 피처 확인
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    null_counts = df[numeric_cols].isnull().sum()
    cols_with_nulls = null_counts[null_counts > 0].index
    
    for col in cols_with_nulls:
        median_val = df[col].median()
        null_count_for_col = df[col].isnull().sum()
        df[col] = df[col].fillna(median_val)
        logging.info(f"4. '{col}' 결측치 {null_count_for_col}건 -> 중간값({median_val:.4f}) 대체 완료.")

    # 5. 전처리된 데이터 저장
    df.to_csv(output_path, index=False)
    logging.info(f"--- 전처리 완료! 최종 저장: {output_path} (최종 행 수: {len(df)}) ---")

if __name__ == '__main__':
    main()
