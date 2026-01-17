import pandas as pd
import numpy as np
import xgboost as xgb
import lightgbm as lgb
from catboost import CatBoostRegressor
from sklearn.model_selection import KFold
from sklearn.metrics import mean_squared_error
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.preprocessing import LabelEncoder
import os
import warnings

warnings.filterwarnings("ignore")

# --- Configuration ---
class Config:
    data_dir = './data'  # 로컬 환경 데이터 경로
    org_path = './data/Exam_Score_Prediction.csv' # 원본 데이터 경로
    seed = 42
    target = 'exam_score'
    n_splits = 5

cfg = Config()

# --- Target Encoder Class (Original Logic) ---
class TargetEncoder(BaseEstimator, TransformerMixin):
    def __init__(self, cols_to_encode, aggs=['mean'], cv=5, smooth='auto', drop_original=False):
        self.cols_to_encode = cols_to_encode
        self.aggs = aggs
        self.cv = cv
        self.smooth = smooth
        self.drop_original = drop_original
        self.mappings_ = {}
        self.global_stats_ = {}

    def fit(self, X, y):
        temp_df = X.copy()
        temp_df['target'] = y
        for agg_func in self.aggs:
            self.global_stats_[agg_func] = y.agg(agg_func)
        for col in self.cols_to_encode:
            self.mappings_[col] = {}
            for agg_func in self.aggs:
                mapping = temp_df.groupby(col)['target'].agg(agg_func)
                self.mappings_[col][agg_func] = mapping
        return self

    def transform(self, X):
        X_transformed = X.copy()
        for col in self.cols_to_encode:
            for agg_func in self.aggs:
                new_col_name = f'TE_{col}_{agg_func}'
                map_series = self.mappings_[col][agg_func]
                X_transformed[new_col_name] = X[col].map(map_series)
                X_transformed[new_col_name].fillna(self.global_stats_[agg_func], inplace=True)
        if self.drop_original:
            X_transformed.drop(columns=self.cols_to_encode, inplace=True)
        return X_transformed

    def fit_transform(self, X, y):
        self.fit(X, y)
        encoded_features = pd.DataFrame(index=X.index)
        kf = KFold(n_splits=self.cv, shuffle=True, random_state=42)
        for train_idx, val_idx in kf.split(X, y):
            X_train, y_train = X.iloc[train_idx], y.iloc[train_idx]
            X_val = X.iloc[val_idx]
            temp_df_train = X_train.copy()
            temp_df_train['target'] = y_train
            for col in self.cols_to_encode:
                for agg_func in self.aggs:
                    new_col_name = f'TE_{col}_{agg_func}'
                    fold_global_stat = y_train.agg(agg_func)
                    mapping = temp_df_train.groupby(col)['target'].agg(agg_func)
                    if agg_func == 'mean':
                        counts = temp_df_train.groupby(col)['target'].count()
                        m = self.smooth
                        if self.smooth == 'auto':
                            variance_between = mapping.var()
                            avg_variance_within = temp_df_train.groupby(col)['target'].var().mean()
                            m = avg_variance_within / variance_between if variance_between > 0 else 0
                        smoothed_mapping = (counts * mapping + m * fold_global_stat) / (counts + m)
                        encoded_values = X_val[col].map(smoothed_mapping)
                    else:
                        encoded_values = X_val[col].map(mapping)
                    encoded_features.loc[X_val.index, new_col_name] = encoded_values.fillna(fold_global_stat)
        X_transformed = X.copy()
        for col in encoded_features.columns:
            X_transformed[col] = encoded_features[col]
        if self.drop_original:
            X_transformed.drop(columns=self.cols_to_encode, inplace=True)
        return X_transformed

# --- Feature Engineering Functions ---
def apply_feature_engineering(train, test, org):
    # 1. 수치형/범주형 정의
    cat_cols = [col for col in test.columns if test[col].dtype == 'O']
    num_cols = [col for col in test.columns if test[col].dtype in ['float64', 'int64']]
    base_cols = [col for col in train.columns if col != cfg.target]

    # 2. 이상치 클리핑 (누수 방지 위해 train 기준)
    for col in num_cols:
        lower, upper = train[col].quantile(0.01), train[col].quantile(0.99)
        train[col], test[col] = train[col].clip(lower, upper), test[col].clip(lower, upper)

    # 3. 원본 데이터 통계량 병합
    for col in base_cols:
        mean_map = org.groupby(col)[cfg.target].mean().rename(f"orig_mean_{col}")
        train = train.merge(mean_map, on=col, how='left')
        test = test.merge(mean_map, on=col, how='left')
        train[f"orig_mean_{col}"].fillna(org[cfg.target].mean(), inplace=True)
        test[f"orig_mean_{col}"].fillna(org[cfg.target].mean(), inplace=True)

    # 4. Rounding 및 Digit Extraction
    for k in range(1, 3):
        train[f"round{k}"] = train["study_hours"].round(k)
        test[f"round{k}"] = test["study_hours"].round(k)
        train[f'digit_{k}'] = ((train['study_hours']*10**k)%10).fillna(-1).astype("int8")
        test[f"digit_{k}"]  = ((test['study_hours']*10**k)%10).fillna(-1).astype('int8')

    # 5. Combinational Features
    for col in cat_cols:
        comb = pd.concat([train[col], test[col]], axis=0)
        tmp, _ = pd.factorize(comb)
        train[col], test[col] = tmp[:len(train)], tmp[len(train):]
        train[f"{col}_sh"] = train[col]*100 + train['study_hours']
        test[f"{col}_sh"] = test[col]*100 + test['study_hours']

    # 6. Distance/Math Features (공개 커널 공식 반영)
    for df in [train, test]:
        eps = 1e-5
        df['_study_hours_sin'] = np.sin(2*np.pi*df['study_hours']/12)
        df['study_att'] = df['study_hours'] * df['class_attendance']
        df['efficiency'] = (df['study_hours'] * df['class_attendance']) / (df['sleep_hours'] + 1)
        df['study_over_sleep'] = df['study_hours'] / (df['sleep_hours'] + eps)

    # 7. Meta Formula
    def formula(df):
        return (6*df.study_hours + 0.35*df.class_attendance + 1.5*df.sleep_hours)
    train['meta_0'], test['meta_0'] = formula(train), formula(test)

    return train, test, cat_cols, num_cols

# --- Main Logic ---
def main():
    # 데이터 로드
    train = pd.read_csv(os.path.join(cfg.data_dir, 'train.csv'), index_col='id')
    test = pd.read_csv(os.path.join(cfg.data_dir, 'test.csv'), index_col='id')
    org = pd.read_csv(cfg.org_path)

    # 전처리 적용
    train, test, cat_cols, num_cols = apply_feature_engineering(train, test, org)
    
    # 학습 준비
    features = [c for c in train.columns if c != cfg.target]
    X, y = train[features], train[cfg.target]
    X_test = test[features]

    # 모델 정의
    models_info = {
        'xgb': {'params': {'objective': 'reg:squarederror', 'learning_rate': 0.007, 'max_depth': 7, 'subsample': 0.8, 'device': 'cuda', 'enable_categorical': True}},
        'lgb': {'params': {'objective': 'regression', 'metric': 'rmse', 'learning_rate': 0.007, 'max_depth': 9, 'num_leaves': 63, 'subsample': 0.8, 'verbosity': -1}},
        'cb':  {'params': {'loss_function': 'RMSE', 'learning_rate': 0.007, 'depth': 8, 'random_seed': 42, 'verbose': False}}
    }

    # OOF/Preds 저장을 위한 딕셔너리
    oofs = {name: np.zeros(len(train)) for name in models_info.keys()}
    preds = {name: np.zeros(len(test)) for name in models_info.keys()}

    kf = KFold(n_splits=cfg.n_splits, shuffle=True, random_state=cfg.seed)
    stats = ["mean", "std", "count", "nunique"]

    for fold, (train_idx, val_idx) in enumerate(kf.split(X, y)):
        print(f"\n#### FOLD {fold+1} 시작 ####")
        x_train, y_train = X.iloc[train_idx], y.iloc[train_idx]
        x_val, y_val = X.iloc[val_idx], y.iloc[val_idx]
        x_t = X_test.copy()

        # Target Encoding 적용
        te = TargetEncoder(cols_to_encode=num_cols + cat_cols, cv=5, smooth=1.0, aggs=stats)
        x_train = te.fit_transform(x_train, y_train)
        x_val = te.transform(x_val)
        x_t = te.transform(x_t)

        # 1. XGBoost 학습
        dtrain = xgb.DMatrix(x_train, label=y_train, enable_categorical=True)
        dval = xgb.DMatrix(x_val, label=y_val, enable_categorical=True)
        m_xgb = xgb.train(models_info['xgb']['params'], dtrain, num_boost_round=5000, evals=[(dval, 'val')], early_stopping_rounds=100, verbose_eval=1000)
        oofs['xgb'][val_idx] = m_xgb.predict(dval)
        preds['xgb'] += m_xgb.predict(xgb.DMatrix(x_t)) / cfg.n_splits

        # 2. LightGBM 학습
        m_lgb = lgb.LGBMRegressor(**models_info['lgb']['params'], n_estimators=5000)
        m_lgb.fit(x_train, y_train, eval_set=[(x_val, y_val)], callbacks=[lgb.early_stopping(100), lgb.log_evaluation(1000)])
        oofs['lgb'][val_idx] = m_lgb.predict(x_val)
        preds['lgb'] += m_lgb.predict(x_t) / cfg.n_splits

        # 3. CatBoost 학습
        m_cb = CatBoostRegressor(**models_info['cb']['params'], iterations=5000)
        m_cb.fit(x_train, y_train, eval_set=(x_val, y_val), early_stopping_rounds=100)
        oofs['cb'][val_idx] = m_cb.predict(x_val)
        preds['cb'] += m_cb.predict(x_t) / cfg.n_splits

    # 결과 저장 및 스코어 출력
    for name in models_info.keys():
        score = np.sqrt(mean_squared_error(y, oofs[name]))
        print(f"-> {name.upper()} Overall RMSE: {score:.5f}")
        np.save(f'oof_{name}.npy', oofs[name])
        np.save(f'preds_{name}.npy', preds[name])

    # Simple Ensemble Submission
    final_preds = (preds['xgb'] + preds['lgb'] + preds['cb']) / 3
    pd.DataFrame({'id': test.index, 'exam_score': final_preds}).to_csv('submission.csv', index=False)
    print("\n최종 submission.csv 및 npy 파일 생성 완료.")

if __name__ == "__main__":
    main()