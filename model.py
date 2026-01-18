import pandas as pd
import numpy as np
import xgboost as xgb
from sklearn.model_selection import KFold
from sklearn.metrics import mean_squared_error
from sklearn.preprocessing import LabelEncoder
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

def preprocess_best_logic(train_df, test_df, org_df):
    train = train_df.copy()
    test = test_df.copy()
    org = org_df.copy()
    
    # 기초 컬럼 정의
    target = cfg.target
    base_cols = [c for c in test.columns if c != 'id']
    cat_cols = ['gender', 'course', 'internet_access', 'sleep_quality', 'study_method', 'facility_rating', 'exam_difficulty']
    num_cols = ['age', 'study_hours', 'class_attendance', 'sleep_hours']

    # 1. Original Feature Mapping (원본 데이터를 '참고서'로 활용)
    for col in base_cols:
        # Mean mapping
        mean_map = org.groupby(col)[target].mean().rename(f"orig_mean_{col}")
        train = train.merge(mean_map, on=col, how='left')
        test = test.merge(mean_map, on=col, how='left')
        train[f"orig_mean_{col}"].fillna(org[target].mean(), inplace=True)
        test[f"orig_mean_{col}"].fillna(org[target].mean(), inplace=True)
        
        # Count mapping
        count_map = org.groupby(col).size().rename(f"orig_count_{col}")
        train = train.merge(count_map, on=col, how='left')
        test = test.merge(count_map, on=col, how='left')
        train[f"orig_count_{col}"].fillna(0, inplace=True)
        test[f"orig_count_{col}"].fillna(0, inplace=True)

    # 2. Digit Extraction (합성 데이터의 치트키: 소수점 추출)
    for k in range(1, 3):
        for df in [train, test]:
            df[f'digit_{k}'] = ((df['study_hours'] * 10**k) % 10).astype(int)

    # 3. Interaction & Math Features
    for df in [train, test]:
        df['study_intensity'] = df['study_hours'] * (df['class_attendance'] / 100)
        df['efficiency'] = (df['study_hours'] * df['class_attendance']) / (df['sleep_hours'] + 1)
        # 공식 기반 메타 피처
        df['meta_formula'] = (6*df.study_hours + 0.35*df.class_attendance + 1.5*df.sleep_hours)

    # 4. 범주형 변수 처리
    for col in cat_cols:
        le = LabelEncoder()
        train[col] = le.fit_transform(train[col].astype(str))
        test[col] = le.transform(test[col].astype(str))

    return train, test

def main():
    print("--- 8.58 로직 기반 전처리 시작 ---")
    train_df = pd.read_csv(os.path.join(cfg.data_dir, 'train.csv'))
    test_df = pd.read_csv(os.path.join(cfg.data_dir, 'test.csv'))
    org_df = pd.read_csv(cfg.org_path)

    train, test = preprocess_best_logic(train_df, test_df, org_df)
    
    features = [c for c in train.columns if c not in [cfg.target, 'id']]
    X = train[features]
    y = train[cfg.target]
    X_test = test[features]

    # 최적화된 XGBoost 파라미터 (GPU 활용 가능 시 적용)
    xgb_params = {
        'n_estimators': 10000,
        'learning_rate': 0.007,
        'max_depth': 7,
        'subsample': 0.8,
        'colsample_bytree': 0.3,
        'reg_lambda': 3.0,
        'objective': 'reg:squarederror',
        'eval_metric': 'rmse',
        'early_stopping_rounds': 200,
        'random_state': cfg.seed,
        'tree_method': 'hist', # 'gpu_hist' 사용 가능 시 변경 권장
        'device': 'cuda' if xgb.__version__ >= '2.0.0' else None 
    }

    kf = KFold(n_splits=cfg.n_splits, shuffle=True, random_state=cfg.seed)
    oof = np.zeros(len(train))
    preds = np.zeros(len(test))

    for fold, (t_idx, v_idx) in enumerate(kf.split(X, y), 1):
        print(f"Fold {fold} 학습 중...")
        xt, xv = X.iloc[t_idx], X.iloc[v_idx]
        yt, yv = y.iloc[t_idx], y.iloc[v_idx]

        model = xgb.XGBRegressor(**xgb_params)
        model.fit(xt, yt, eval_set=[(xv, yv)], verbose=False)
        
        oof[v_idx] = model.predict(xv)
        preds += model.predict(X_test) / cfg.n_splits

    score = np.sqrt(mean_squared_error(y, oof))
    print(f"\n✅ 전체 OOF RMSE: {score:.5f}")

    # 제출 파일 생성
    submission = pd.DataFrame({'id': test_df['id'], 'exam_score': preds})
    submission.to_csv('submission.csv', index=False)
    print("submission.csv 저장 완료")

if __name__ == "__main__":
    main()