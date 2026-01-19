import pandas as pd
import numpy as np
import xgboost as xgb
import lightgbm as lgb
from catboost import CatBoostRegressor
from sklearn.model_selection import KFold
from sklearn.metrics import mean_squared_error
from sklearn.preprocessing import LabelEncoder, QuantileTransformer
from scipy.optimize import minimize
import os
import warnings

warnings.filterwarnings("ignore")

class Config:
    data_dir = './data'
    org_path = './data/Exam_Score_Prediction.csv'
    seed = 42
    target = 'exam_score'
    n_splits = 5

cfg = Config()

def preprocess_ultimate(train_df, test_df, org_df):
    train, test, org = train_df.copy(), test_df.copy(), org_df.copy()
    target = cfg.target
    
    # 1. 원본 데이터 통계 매핑 (8.63의 성공 로직)
    base_cols = [c for c in test.columns if c != 'id']
    for col in base_cols:
        mean_map = org.groupby(col)[target].mean().rename(f"orig_mean_{col}")
        train = train.merge(mean_map, on=col, how='left', sort=False)
        test = test.merge(mean_map, on=col, how='left', sort=False)
        train[f"orig_mean_{col}"].fillna(org[target].mean(), inplace=True)
        test[f"orig_mean_{col}"].fillna(org[target].mean(), inplace=True)

    # 2. 소수점 추출 (Digit Extraction)
    for k in range(1, 3):
        for df in [train, test]:
            df[f'digit_{k}'] = ((df['study_hours'] * 10**k) % 10).astype(int)

    # 3. 수치형 변수 정규화 (Quantile Transformation)
    num_cols = ['age', 'study_hours', 'class_attendance', 'sleep_hours']
    qt = QuantileTransformer(output_distribution='normal', random_state=cfg.seed)
    train[num_cols] = qt.fit_transform(train[num_cols])
    test[num_cols] = qt.transform(test[num_cols])

    # 4. Golden Features (상호작용 변수)
    for df in [train, test]:
        df['study_intensity'] = df['study_hours'] * df['class_attendance']
        df['efficiency'] = df['study_hours'] / (df['sleep_hours'] + 1)

    # 5. 범주형 인코딩
    cat_cols = ['gender', 'course', 'internet_access', 'sleep_quality', 'study_method', 'facility_rating', 'exam_difficulty']
    for col in cat_cols:
        le = LabelEncoder()
        train[col] = le.fit_transform(train[col].astype(str))
        test[col] = le.transform(test[col].astype(str))

    return train, test

def main():
    train_df = pd.read_csv(os.path.join(cfg.data_dir, 'train.csv'))
    test_df = pd.read_csv(os.path.join(cfg.data_dir, 'test.csv'))
    org_df = pd.read_csv(cfg.org_path)

    train, test = preprocess_ultimate(train_df, test_df, org_df)
    features = [c for c in train.columns if c not in [cfg.target, 'id']]
    X, y, X_test = train[features], train[cfg.target], test[features]

    kf = KFold(n_splits=cfg.n_splits, shuffle=True, random_state=cfg.seed)
    model_names = ['xgb', 'lgb', 'cb']
    oofs = {name: np.zeros(len(X)) for name in model_names}
    preds = {name: np.zeros(len(X_test)) for name in model_names}

    for fold, (t_idx, v_idx) in enumerate(kf.split(X, y), 1):
        print(f"--- Fold {fold} 학습 시작 ---")
        xt, xv = X.iloc[t_idx], X.iloc[v_idx]
        yt, yv = y.iloc[t_idx], y.iloc[v_idx]

        # Model 1: XGBoost (에러 수정: 생성자에 early_stopping_rounds 포함)
        m_xgb = xgb.XGBRegressor(
            n_estimators=10000, 
            learning_rate=0.007, 
            max_depth=7, 
            subsample=0.8, 
            colsample_bytree=0.3, 
            random_state=cfg.seed, 
            tree_method='hist',
            device='cuda',
            early_stopping_rounds=200 # 여기에 위치해야 함
        )
        m_xgb.fit(xt, yt, eval_set=[(xv, yv)], verbose=False)
        oofs['xgb'][v_idx] = m_xgb.predict(xv)
        preds['xgb'] += m_xgb.predict(X_test) / cfg.n_splits

        # Model 2: LightGBM
        m_lgb = lgb.LGBMRegressor(n_estimators=10000, learning_rate=0.007, max_depth=10, num_leaves=127, subsample=0.8, colsample_bytree=0.3, random_state=cfg.seed)
        m_lgb.fit(xt, yt, eval_set=[(xv, yv)], callbacks=[lgb.early_stopping(200), lgb.log_evaluation(0)])
        oofs['lgb'][v_idx] = m_lgb.predict(xv)
        preds['lgb'] += m_lgb.predict(X_test) / cfg.n_splits

        # Model 3: CatBoost
        m_cb = CatBoostRegressor(iterations=10000, learning_rate=0.007, depth=8, random_seed=cfg.seed, verbose=0, early_stopping_rounds=200)
        m_cb.fit(xt, yt, eval_set=(xv, yv))
        oofs['cb'][v_idx] = m_cb.predict(xv)
        preds['cb'] += m_cb.predict(X_test) / cfg.n_splits

    # 가중치 최적화 (Nelder-Mead)
    def objective(w):
        if np.any(w < 0): return 1e9
        w = w / np.sum(w)
        ensemble = w[0]*oofs['xgb'] + w[1]*oofs['lgb'] + w[2]*oofs['cb']
        return np.sqrt(mean_squared_error(y, ensemble))

    res = minimize(objective, [0.7, 0.15, 0.15], method='Nelder-Mead')
    best_w = res.x / np.sum(res.x)
    print(f"\n최적 가중치: XGB={best_w[0]:.4f}, LGB={best_w[1]:.4f}, CB={best_w[2]:.4f}")
    
    # 최종 결과 합산 및 후처리
    final_preds = best_w[0]*preds['xgb'] + best_w[1]*preds['lgb'] + best_w[2]*preds['cb']
    final_preds = np.clip(final_preds, 19.5, 100.0)

    # 제출 파일 생성
    submission = pd.DataFrame({'id': test_df['id'], 'exam_score': final_preds})
    submission.to_csv('submission.csv', index=False)
    print(f"--- submission 완료 (OOF RMSE: {res.fun:.5f}) ---")

if __name__ == "__main__":
    main()