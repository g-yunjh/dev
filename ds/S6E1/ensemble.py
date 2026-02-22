import numpy as np
import pandas as pd
from sklearn.metrics import mean_squared_error
from scipy.optimize import minimize

test_df = pd.read_csv('./data/test.csv') 
y_true = pd.read_csv('./data/train.csv')['exam_score'].values

# npy 로드 (CB 대신 NN 사용)
oof_xgb = np.load('oof_xgb.npy')
oof_lgb = np.load('oof_lgb.npy')
oof_nn = np.load('oof_nn.npy')

preds_xgb = np.load('preds_xgb.npy')
preds_lgb = np.load('preds_lgb.npy')
preds_nn = np.load('preds_nn.npy')

def objective(w):
    w = w / np.sum(w)
    ensemble = w[0]*oof_xgb + w[1]*oof_lgb + w[2]*oof_nn
    return np.sqrt(mean_squared_error(y_true, ensemble))

res = minimize(objective, [0.6, 0.3, 0.1], method='Nelder-Mead')
best_w = res.x / np.sum(res.x)

print(f"\n🏆 최종 가중치: XGB={best_w[0]:.4f}, LGB={best_w[1]:.4f}, NN={best_w[2]:.4f}")
print(f"최종 최적화 OOF RMSE: {res.fun:.5f}")

final_preds = (best_w[0] * preds_xgb) + (best_w[1] * preds_lgb) + (best_w[2] * preds_nn)
final_preds = np.clip(final_preds, 19.5, 100.0)

pd.DataFrame({'id': test_df['id'], 'exam_score': final_preds}).to_csv('submission.csv', index=False)