import pandas as pd
import numpy as np
import xgboost as xgb
import lightgbm as lgb
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, TensorDataset
from sklearn.model_selection import KFold
from sklearn.metrics import mean_squared_error
from sklearn.preprocessing import StandardScaler, OrdinalEncoder
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

# --- 1. 피처 엔지니어링 (공유해주신 로직 통합) ---
def add_engineered_features(df):
    df = df.copy()
    # 1. Sine features
    df['_study_hours_sin'] = np.sin(2 * np.pi * df['study_hours'] / 12)
    df['_class_attendance_sin'] = np.sin(2 * np.pi * df['class_attendance'] / 12)
    
    # 2. Golden Formula (가장 중요한 피처)
    df['feature_formula'] = (
        5.9051 * df['study_hours'] + 
        0.3454 * df['class_attendance'] + 
        1.4234 * df['sleep_hours'] + 4.7819
    )
    
    # 3. Frequency Encoding
    for col in df.select_dtypes(include=['object']).columns:
        freq_map = df[col].value_counts().to_dict()
        df[f"{col}_freq"] = df[col].map(freq_map)
        
    return df

# --- 2. 신경망(NN) 정의 (ResNet 구조) ---
class SimpleResNet(nn.Module):
    def __init__(self, input_dim):
        super().__init__()
        self.layer1 = nn.Sequential(nn.Linear(input_dim, 256), nn.ReLU(), nn.BatchNorm1d(256))
        self.layer2 = nn.Sequential(nn.Linear(256, 256), nn.ReLU(), nn.BatchNorm1d(256))
        self.head = nn.Linear(256, 1)
        
    def forward(self, x):
        x1 = self.layer1(x)
        x2 = self.layer2(x1)
        return self.head(x1 + x2).squeeze() # Residual Connection

def main():
    train_df = pd.read_csv(os.path.join(cfg.data_dir, 'train.csv'))
    test_df = pd.read_csv(os.path.join(cfg.data_dir, 'test.csv'))
    
    # 전처리
    train = add_engineered_features(train_df)
    test = add_engineered_features(test_df)
    
    # 범주형 인코딩
    cat_cols = train_df.select_dtypes(include=['object']).columns.tolist()
    oe = OrdinalEncoder(handle_unknown='use_encoded_value', unknown_value=-1)
    train[cat_cols] = oe.fit_transform(train[cat_cols].astype(str))
    test[cat_cols] = oe.transform(test[cat_cols].astype(str))
    
    features = [c for c in train.columns if c not in [cfg.target, 'id']]
    X, y, X_test = train[features], train[cfg.target], test[features]
    
    # NN용 스케일링
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X.fillna(0))
    X_test_scaled = scaler.transform(X_test.fillna(0))

    kf = KFold(n_splits=cfg.n_splits, shuffle=True, random_state=cfg.seed)
    model_names = ['xgb', 'lgb', 'nn']
    oofs = {name: np.zeros(len(X)) for name in model_names}
    preds = {name: np.zeros(len(X_test)) for name in model_names}

    for fold, (t_idx, v_idx) in enumerate(kf.split(X, y), 1):
        print(f"--- Fold {fold} 학습 시작 ---")
        xt, xv = X.iloc[t_idx], X.iloc[v_idx]
        yt, yv = y.iloc[t_idx], y.iloc[v_idx]
        
        # 1. XGBoost
        m_xgb = xgb.XGBRegressor(n_estimators=8000, learning_rate=0.01, max_depth=7, subsample=0.8, colsample_bytree=0.3, tree_method='hist', device='cuda', early_stopping_rounds=200)
        m_xgb.fit(xt, yt, eval_set=[(xv, yv)], verbose=False)
        oofs['xgb'][v_idx] = m_xgb.predict(xv)
        preds['xgb'] += m_xgb.predict(X_test) / cfg.n_splits

        # 2. LightGBM (공유해주신 V11 참고 파라미터)
        m_lgb = lgb.LGBMRegressor(n_estimators=8000, learning_rate=0.01, num_leaves=31, max_depth=-1, feature_fraction=0.9, bagging_fraction=0.8, bagging_freq=5, random_state=cfg.seed)
        m_lgb.fit(xt, yt, eval_set=[(xv, yv)], callbacks=[lgb.early_stopping(200), lgb.log_evaluation(0)])
        oofs['lgb'][v_idx] = m_lgb.predict(xv)
        preds['lgb'] += m_lgb.predict(X_test) / cfg.n_splits

        # 3. NN (PyTorch)
        device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        model_nn = SimpleResNet(X.shape[1]).to(device)
        optimizer = optim.AdamW(model_nn.parameters(), lr=1e-3, weight_decay=1e-4)
        criterion = nn.MSELoss()
        
        train_ds = TensorDataset(torch.tensor(X_scaled[t_idx], dtype=torch.float32), torch.tensor(yt.values, dtype=torch.float32))
        train_loader = DataLoader(train_ds, batch_size=512, shuffle=True)
        
        model_nn.train()
        for epoch in range(30): # 에폭 최적화
            for bx, by in train_loader:
                bx, by = bx.to(device), by.to(device)
                optimizer.zero_grad(); loss = criterion(model_nn(bx), by); loss.backward(); optimizer.step()
        
        model_nn.eval()
        with torch.no_grad():
            oofs['nn'][v_idx] = model_nn(torch.tensor(X_scaled[v_idx], dtype=torch.float32).to(device)).cpu().numpy()
            preds['nn'] += model_nn(torch.tensor(X_test_scaled, dtype=torch.float32).to(device)).cpu().numpy() / cfg.n_splits

    for name in model_names:
        score = np.sqrt(mean_squared_error(y, oofs[name]))
        print(f"-> {name.upper()} RMSE: {score:.5f}")
        np.save(f'oof_{name}.npy', oofs[name])
        np.save(f'preds_{name}.npy', preds[name])

if __name__ == "__main__":
    main()