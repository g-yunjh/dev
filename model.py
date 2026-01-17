import pandas as pd
import numpy as np
import xgboost as xgb
import lightgbm as lgb
from catboost import CatBoostRegressor
from sklearn.model_selection import KFold
from sklearn.metrics import mean_squared_error
from sklearn.base import BaseEstimator, TransformerMixin
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
                X_transformed[new_col_name] = X[col].map(self.mappings_[col][agg_func])
                X_transformed[new_col_name].fillna(self.global_stats_[agg_func], inplace=True)
        if self.drop_original:
            X_transformed.drop(columns=self.cols_to_encode, inplace=True)
        return X_transformed

    def fit_transform(self, X, y):
        self.fit(X, y)
        encoded_features = pd.DataFrame(index=X.index)
        kf = KFold(n_splits=self.cv, shuffle=True, random_state=42)
        for train_idx, val_idx in kf.split(X, y):
            xt, yt = X.iloc[train_idx], y.iloc[train_idx]
            xv = X.iloc[val_idx]
            temp_df_train = xt.copy()
            temp_df_train['target'] = yt
            for col in self.cols_to_encode:
                for agg_func in self.aggs:
                    new_col_name = f'TE_{col}_{agg_func}'
                    fold_global_stat = yt.agg(agg_func)
                    mapping = temp_df_train.groupby(col)['target'].agg(agg_func)
                    if agg_func == 'mean':
                        counts = temp_df_train.groupby(col)['target'].count()
                        m = 1.0 # Smoothing factor
                        smoothed_mapping = (counts * mapping + m * fold_global_stat) / (counts + m)
                        encoded_features.loc[xv.index, new_col_name] = xv[col].map(smoothed_mapping).fillna(fold_global_stat)
                    else:
                        encoded_features.loc[xv.index, new_col_name] = xv[col].map(mapping).fillna(fold_global_stat)
        X_transformed = X.copy()
        for col in encoded_features.columns:
            X_transformed[col] = encoded_features[col]
        return X_transformed

def apply_feature_engineering(train, test, org):
    cat_cols = [col for col in test.columns if test[col].dtype == 'O']
    num_cols = [col for col in test.columns if test[col].dtype in ['float64', 'int64'] and col != 'id']
    base_cols = [col for col in test.columns if col != 'id']

    # 이상치 처리
    for col in num_cols:
        lower, upper = train[col].quantile(0.01), train[col].quantile(0.99)
        train[col], test[col] = train[col].clip(lower, upper), test[col].clip(lower, upper)

    # 원본 데이터 매핑
    for col in base_cols:
        mean_map = org.groupby(col)[cfg.target].mean().rename(f"orig_mean_{col}")
        train = train.merge(mean_map, on=col, how='left')
        test = test.merge(mean_map, on=col, how='left')
        train[f"orig_mean_{col}"].fillna(org[cfg.target].mean(), inplace=True)
        test[f"orig_mean_{col}"].fillna(org[cfg.target].mean(), inplace=True)

    # Rounding & Digits
    for k in range(1, 3):
        train[f"round{k}"] = train["study_hours"].round(k)
        test[f"round{k}"] = test["study_hours"].round(k)
        train[f'digit_{k}'] = ((train['study_hours']*10**k)%10).fillna(-1).astype("int8")
        test[f"digit_{k}"]  = ((test['study_hours']*10**k)%10).fillna(-1).astype('int8')

    # Combinational
    for col in cat_cols:
        comb = pd.concat([train[col], test[col]], axis=0)
        tmp, _ = pd.factorize(comb)
        train[col], test[col] = tmp[:len(train)], tmp[len(train):]

    # Math Features
    for df in [train, test]:
        df['study_att'] = df['study_hours'] * df['class_attendance']
        df['efficiency'] = (df['study_hours'] * df['class_attendance']) / (df['sleep_hours'] + 1)
        df['meta_0'] = (6*df.study_hours + 0.35*df.class_attendance + 1.5*df.sleep_hours)

    return train, test, cat_cols, num_cols

def main():
    train = pd.read_csv(os.path.join(cfg.data_dir, 'train.csv'))
    test = pd.read_csv(os.path.join(cfg.data_dir, 'test.csv'))
    org = pd.read_csv(cfg.org_path)

    train, test, cat_cols, num_cols = apply_feature_engineering(train, test, org)
    
    features = [c for c in test.columns if c != 'id']
    X, y = train[features], train[cfg.target]
    X_test = test[features]

    # 공격적인 하이퍼파라미터 설정 (8.5x 목표)
    models_info = {
        'xgb': {'params': {'objective': 'reg:squarederror', 'learning_rate': 0.005, 'max_depth': 8, 'subsample': 0.8, 'colsample_bytree': 0.8, 'reg_lambda': 5.0, 'device': 'cuda', 'enable_categorical': True}},
        'lgb': {'params': {'objective': 'regression', 'metric': 'rmse', 'learning_rate': 0.005, 'max_depth': 10, 'num_leaves': 127, 'subsample': 0.8, 'colsample_bytree': 0.8, 'verbosity': -1}},
        'cb':  {'params': {'loss_function': 'RMSE', 'learning_rate': 0.005, 'depth': 10, 'l2_leaf_reg': 7.0, 'random_seed': cfg.seed, 'verbose': False}}
    }

    oofs = {name: np.zeros(len(train)) for name in models_info.keys()}
    preds = {name: np.zeros(len(test)) for name in models_info.keys()}

    kf = KFold(n_splits=cfg.n_splits, shuffle=True, random_state=cfg.seed)
    stats = ["mean", "std", "count"]

    for fold, (train_idx, val_idx) in enumerate(kf.split(X, y)):
        print(f"\n#### FOLD {fold+1} 시작 ####")
        x_train, y_train = X.iloc[train_idx], y.iloc[train_idx]
        x_val, y_val = X.iloc[val_idx], y.iloc[val_idx]
        x_t = X_test.copy()

        te = TargetEncoder(cols_to_encode=num_cols + cat_cols, cv=5, smooth=1.0, aggs=stats)
        x_train = te.fit_transform(x_train, y_train)
        x_val = te.transform(x_val)
        x_t = te.transform(x_t)

        # 1. XGBoost
        dtrain = xgb.DMatrix(x_train, label=y_train, enable_categorical=True)
        dval = xgb.DMatrix(x_val, label=y_val, enable_categorical=True)
        m_xgb = xgb.train(models_info['xgb']['params'], dtrain, num_boost_round=10000, evals=[(dval, 'val')], early_stopping_rounds=200, verbose_eval=1000)
        oofs['xgb'][val_idx] = m_xgb.predict(dval)
        preds['xgb'] += m_xgb.predict(xgb.DMatrix(x_t)) / cfg.n_splits

        # 2. LightGBM
        m_lgb = lgb.LGBMRegressor(**models_info['lgb']['params'], n_estimators=10000)
        m_lgb.fit(x_train, y_train, eval_set=[(x_val, y_val)], callbacks=[lgb.early_stopping(200), lgb.log_evaluation(1000)])
        oofs['lgb'][val_idx] = m_lgb.predict(x_val)
        preds['lgb'] += m_lgb.predict(x_t) / cfg.n_splits

        # 3. CatBoost
        m_cb = CatBoostRegressor(**models_info['cb']['params'], iterations=10000)
        m_cb.fit(x_train, y_train, eval_set=(x_val, y_val), early_stopping_rounds=200)
        oofs['cb'][val_idx] = m_cb.predict(x_val)
        preds['cb'] += m_cb.predict(x_t) / cfg.n_splits

    for name in models_info.keys():
        score = np.sqrt(mean_squared_error(y, oofs[name]))
        print(f"-> {name.upper()} Overall RMSE: {score:.5f}")
        np.save(f'oof_{name}.npy', oofs[name])
        np.save(f'preds_{name}.npy', preds[name])

if __name__ == "__main__":
    main()