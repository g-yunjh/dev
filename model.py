import pandas as pd
import numpy as np
import warnings
from lightgbm import LGBMRegressor, early_stopping, log_evaluation
from catboost import CatBoostRegressor
from xgboost import XGBRegressor
from sklearn.model_selection import KFold
from sklearn.linear_model import Ridge
from sklearn.metrics import mean_squared_error
from sklearn.preprocessing import LabelEncoder

warnings.filterwarnings('ignore')

# 1. 전처리 및 피처 엔진니어링 (안정성 중심)
def preprocess(df):
    df = df.copy()
    if 'id' in df.columns:
        df = df.drop('id', axis=1)
    
    # 범주형 변수 처리 (Ordinal)
    ord_map = {
        'exam_difficulty': {'easy': 0, 'moderate': 1, 'hard': 2},
        'facility_rating': {'low': 0, 'medium': 1, 'high': 2},
        'sleep_quality': {'poor': 0, 'average': 1, 'good': 2}
    }
    for col, mapping in ord_map.items():
        df[col] = df[col].map(mapping)
        
    # 명목형 변수 라벨 인코딩
    nom_cols = ['gender', 'course', 'internet_access', 'study_method']
    for col in nom_cols:
        le = LabelEncoder()
        df[col] = le.fit_transform(df[col].astype(str))
    
    # 핵심 파생 변수 (산술 조합)
    # study_hours(0.76) 중심 결합
    df['study_total'] = df['study_hours'] * (df['class_attendance'] / 100)
    df['rest_ratio'] = df['sleep_hours'] / (df['study_hours'] + 1)
    df['input_index'] = df['study_hours'] + (df['class_attendance'] / 10)
    
    return df

def main():
    # 데이터 로드
    train_df = pd.read_csv('data/train.csv')
    test_df = pd.read_csv('data/test.csv')
    
    train = preprocess(train_df)
    test = preprocess(test_df)
    
    X = train.drop('exam_score', axis=1)
    y = train['exam_score']
    X_test = test

    # 스태킹 설정
    kf = KFold(n_splits=10, shuffle=True, random_state=42) # 10-Fold로 안정성 강화
    
    # 1단계 모델 예측값 저장 (Meta-features)
    lgb_oof, cb_oof, xgb_oof = np.zeros(len(X)), np.zeros(len(X)), np.zeros(len(X))
    lgb_test, cb_test, xgb_test = np.zeros(len(X_test)), np.zeros(len(X_test)), np.zeros(len(X_test))

    print("--- Level 1: Base Models Training ---")
    for fold, (t_idx, v_idx) in enumerate(kf.split(X, y), 1):
        xt, xv = X.iloc[t_idx], X.iloc[v_idx]
        yt, yv = y.iloc[t_idx], y.iloc[v_idx]
        
        # LGBM
        lgb = LGBMRegressor(n_estimators=5000, learning_rate=0.01, max_depth=10, num_leaves=63, 
                            colsample_bytree=0.8, subsample=0.8, n_jobs=-1, random_state=42)
        lgb.fit(xt, yt, eval_set=[(xv, yv)], eval_metric='rmse', callbacks=[early_stopping(100), log_evaluation(0)])
        
        # CatBoost
        cb = CatBoostRegressor(iterations=5000, learning_rate=0.01, depth=8, random_seed=42, verbose=0)
        cb.fit(xt, yt, eval_set=(xv, yv), use_best_model=True)
        
        # XGBoost
        xgb = XGBRegressor(n_estimators=5000, learning_rate=0.01, max_depth=10, tree_method='hist', 
                           early_stopping_rounds=100, eval_metric='rmse', random_state=42)
        xgb.fit(xt, yt, eval_set=[(xv, yv)], verbose=False)
        
        # OOF 저장
        lgb_oof[v_idx] = lgb.predict(xv)
        cb_oof[v_idx] = cb.predict(xv)
        xgb_oof[v_idx] = xgb.predict(xv)
        
        # Test 예측 (평균)
        lgb_test += lgb.predict(X_test) / kf.get_n_splits()
        cb_test += cb.predict(X_test) / kf.get_n_splits()
        xgb_test += xgb.predict(X_test) / kf.get_n_splits()
        
        print(f"Fold {fold} 완료")

    # --- Level 2: Stacking (Meta-Model) ---
    print("\n--- Level 2: Meta-Model Training ---")
    # OOF 예측값을 피처로 결합
    X_meta = np.column_stack([lgb_oof, cb_oof, xgb_oof])
    X_test_meta = np.column_stack([lgb_test, cb_test, xgb_test])
    
    # 메타 모델: Ridge Regression (과적합 방지 효과)
    meta_model = Ridge(alpha=1.0)
    meta_model.fit(X_meta, y)
    
    final_preds = meta_model.predict(X_test_meta)
    
    # 3. Post-processing
    # 타겟 분포 20~100점 제한
    final_preds = np.clip(final_preds, 19.5, 100.0)
    
    # 제출
    submission = pd.DataFrame({'id': test_df['id'], 'exam_score': final_preds})
    submission.to_csv('submission.csv', index=False)
    print(f"최종 스태킹 모델 완료. 메타모델 계수: {meta_model.coef_}")

if __name__ == "__main__":
    main()