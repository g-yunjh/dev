import pandas as pd
import numpy as np
import warnings
from lightgbm import LGBMRegressor, early_stopping, log_evaluation
from catboost import CatBoostRegressor
from xgboost import XGBRegressor
from sklearn.model_selection import KFold
from sklearn.metrics import mean_squared_error
from sklearn.preprocessing import LabelEncoder
from scipy.optimize import minimize

warnings.filterwarnings('ignore')

# 1. 전처리 및 피처 엔지니어링
def preprocess(df):
    df = df.copy()
    
    # ID 제거
    if 'id' in df.columns:
        df = df.drop('id', axis=1)
    
    # 순서형 변수 수동 매핑 (Ordinal Encoding)
    ordinal_map = {
        'exam_difficulty': {'easy': 0, 'moderate': 1, 'hard': 2},
        'facility_rating': {'low': 0, 'medium': 1, 'high': 2},
        'sleep_quality': {'poor': 0, 'average': 1, 'good': 2}
    }
    for col, mapping in ordinal_map.items():
        if col in df.columns:
            df[col] = df[col].map(mapping)
    
    # 파생 변수 생성 (Interaction Features)
    df['study_performance'] = df['study_hours'] * (df['class_attendance'] / 100)
    df['log_study_hours'] = np.log1p(df['study_hours'])
    df['sleep_efficiency'] = df['sleep_hours'] * df['sleep_quality']
    df['total_wellbeing_idx'] = df['sleep_quality'] + df['facility_rating']
    
    # 범주형 변수 라벨 인코딩
    cat_cols = ['gender', 'course', 'internet_access', 'study_method']
    for col in cat_cols:
        if col in df.columns:
            le = LabelEncoder()
            df[col] = le.fit_transform(df[col].astype(str))
        
    return df

# 데이터 로드 및 적용 (사용자 환경의 train_df, test_df 기준)
train = preprocess(train_df)
test = preprocess(test_df)

X = train.drop('exam_score', axis=1)
y = train['exam_score']
X_test = test

# 2. Pseudo-Labeling (Teacher Model 생성)
print("--- Step 1: Pseudo-Labeling 실행 중 ---")
teacher = CatBoostRegressor(iterations=1000, depth=7, learning_rate=0.05, random_seed=42, verbose=0)
teacher.fit(X, y)
pseudo_y = teacher.predict(X_test)

# 학습 데이터 확장
X_extended = pd.concat([X, X_test], axis=0).reset_index(drop=True)
y_extended = np.concatenate([y, pseudo_y])

# 3. 3개 모델 앙상블 학습 (OOF 방식)
kf = KFold(n_splits=5, shuffle=True, random_state=42)

lgb_oof, cb_oof, xgb_oof = np.zeros(len(X_extended)), np.zeros(len(X_extended)), np.zeros(len(X_extended))
lgb_preds, cb_preds, xgb_preds = np.zeros(len(X_test)), np.zeros(len(X_test)), np.zeros(len(X_test))

print("--- Step 2: 3-Model (LGBM, CatBoost, XGBoost) 학습 시작 ---")
for fold, (train_idx, val_idx) in enumerate(kf.split(X_extended, y_extended), 1):
    xt, xv = X_extended.iloc[train_idx], X_extended.iloc[val_idx]
    yt, yv = y_extended[train_idx], y_extended[val_idx]
    
    # [Model 1] LightGBM
    lgb = LGBMRegressor(n_estimators=2500, learning_rate=0.02, max_depth=9, num_leaves=63, random_state=42)
    lgb.fit(xt, yt, eval_set=[(xv, yv)], eval_metric='rmse', 
            callbacks=[early_stopping(100), log_evaluation(0)])
    
    # [Model 2] CatBoost
    cb = CatBoostRegressor(iterations=2500, learning_rate=0.02, depth=9, random_seed=42, verbose=0)
    cb.fit(xt, yt, eval_set=(xv, yv), use_best_model=True)
    
    # [Model 3] XGBoost (최신 API 방식: 생성자에 early_stopping_rounds와 eval_metric 설정)
    xgb = XGBRegressor(n_estimators=2500, learning_rate=0.02, max_depth=9, tree_method='hist', 
                       early_stopping_rounds=100, eval_metric='rmse', random_state=42)
    xgb.fit(xt, yt, eval_set=[(xv, yv)], verbose=False)
    
    # 예측값 기록
    lgb_oof[val_idx] = lgb.predict(xv)
    cb_oof[val_idx] = cb.predict(xv)
    xgb_oof[val_idx] = xgb.predict(xv)
    
    lgb_preds += lgb.predict(X_test) / 5
    cb_preds += cb.predict(X_test) / 5
    xgb_preds += xgb.predict(X_test) / 5
    print(f"Fold {fold} 완료")

# 4. 가중치 최적화 (Optimization)
def objective(weights):
    w = weights / np.sum(weights)
    ensemble_pred = (w[0] * lgb_oof) + (w[1] * cb_oof) + (w[2] * xgb_oof)
    return np.sqrt(mean_squared_error(y_extended, ensemble_pred))

res = minimize(objective, [0.4, 0.4, 0.2], method='Nelder-Mead')
best_w = res.x / np.sum(res.x)

print(f"\n최적 가중치: LGBM={best_w[0]:.4f}, CatBoost={best_w[1]:.4f}, XGBoost={best_w[2]:.4f}")
print(f"최종 OOF RMSE: {res.fun:.4f}")

# 5. 최종 결과 생성
final_scores = (best_w[0] * lgb_preds) + (best_w[1] * cb_preds) + (best_w[2] * xgb_preds)

submission = pd.DataFrame({
    'id': test_df['id'],
    'exam_score': final_scores
})

submission.to_csv('submission.csv', index=False)
print("\n최종 submission.csv 생성 및 저장 완료.")