import pandas as pd
import numpy as np
import xgboost as xgb
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score
import os

def run_ml_pipeline():
    print("=== CMP 수율 예측 머신러닝 파이프라인 시작 ===")
    
    # 1. 데이터 로드 및 이상치 정제
    train_path = 'data/processed/cmp_A_train_processed.csv'
    holdout_path = 'data/cmp_A_holdout_features.csv'
    
    df_train_raw = pd.read_csv(train_path)
    df_holdout = pd.read_csv(holdout_path)
    
    # [데이터 정제] 센서 오류 및 Pad Age 15시그마 이상치 제거
    df_train = df_train_raw[(df_train_raw['wiwnu_proxy'] <= 20) & (df_train_raw['pad_age_runs'] < 200)].copy()
    print(f"학습 데이터 정제 완료: {len(df_train_raw)} -> {len(df_train)} 건")
    
    # 2. 특징(Feature) 및 타겟 설정
    features = [
        'down_force_psi', 
        'platen_speed_rpm', 
        'head_speed_rpm', 
        'slurry_flow_ml_min', 
        'pad_age_runs', 
        'pattern_density'
    ]
    target = 'yield_proxy'
    
    X = df_train[features]
    y = df_train[target]
    
    # 3. Train / Test 분리 (Rule 4 준수)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    # 4. 베이스라인 모델 (단순 평균)
    baseline_pred = np.full(len(y_test), y_train.mean())
    baseline_rmse = np.sqrt(mean_squared_error(y_test, baseline_pred))
    baseline_r2 = r2_score(y_test, baseline_pred)
    
    # 5. XGBoost 모델 훈련 (트리 모델이므로 비선형성/결측치 자동 처리)
    xgb_model = xgb.XGBRegressor(
        n_estimators=200,
        learning_rate=0.05,
        max_depth=4,
        subsample=0.8,
        colsample_bytree=0.8,
        random_state=42
    )
    xgb_model.fit(X_train, y_train)
    
    # 6. 테스트 셋 평가
    y_pred = xgb_model.predict(X_test)
    model_rmse = np.sqrt(mean_squared_error(y_test, y_pred))
    model_r2 = r2_score(y_test, y_pred)
    improvement = ((baseline_rmse - model_rmse) / baseline_rmse) * 100
    
    print("\n[모델 평가 결과]")
    print(f"- Naive Baseline RMSE: {baseline_rmse:.4f} (R2: {baseline_r2:.4f})")
    print(f"- XGBoost RMSE:        {model_rmse:.4f} (R2: {model_r2:.4f})")
    print(f"-> 베이스라인 대비 예측 오차(RMSE) {improvement:.1f}% 개선 달성!")
    
    # 7. 변수 중요도 분석 (Feature Importance)
    importances = xgb_model.feature_importances_
    feat_imp = pd.DataFrame({'Feature': features, 'Importance': importances}).sort_values('Importance', ascending=False)
    print("\n[변수 중요도 (XGBoost)]")
    for idx, row in feat_imp.iterrows():
        print(f"{row['Feature']:20s} : {row['Importance']:.4f}")
    
    # 8. 최종 모델 재학습 (전체 데이터) 및 Holdout 예측
    print("\n전체 학습 데이터로 최종 모델 훈련 중...")
    final_model = xgb.XGBRegressor(
        n_estimators=200,
        learning_rate=0.05,
        max_depth=4,
        subsample=0.8,
        colsample_bytree=0.8,
        random_state=42
    )
    final_model.fit(X, y)
    
    X_holdout = df_holdout[features]
    holdout_preds = final_model.predict(X_holdout)
    
    # 예측 결과 저장
    df_holdout['yield_proxy_pred'] = holdout_preds
    submission = df_holdout[['sample_id', 'yield_proxy_pred']]
    
    out_dir = 'data/processed'
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, 'cmp_A_holdout_predictions.csv')
    submission.to_csv(out_path, index=False)
    
    print(f"\n[SUCCESS] Holdout 예측 완료! 총 {len(submission)}건의 수율 예측값이 저장되었습니다.")
    print(f"-> 저장 경로: {out_path}")
    print("=== 파이프라인 종료 ===")

if __name__ == '__main__':
    run_ml_pipeline()
