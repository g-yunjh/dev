import numpy as np
import pandas as pd
from sklearn.metrics import mean_squared_error
from scipy.optimize import minimize

# 1. 데이터 로드
# 원본 ID 순서를 유지하기 위해 index_col 없이 로드
test_df = pd.read_csv('./data/test.csv') 
y_true = pd.read_csv('./data/train.csv')['exam_score'].values

# npy 파일 로드
oof_xgb = np.load('oof_xgb.npy')
oof_lgb = np.load('oof_lgb.npy')
oof_cb = np.load('oof_cb.npy')

preds_xgb = np.load('preds_xgb.npy')
preds_lgb = np.load('preds_lgb.npy')
preds_cb = np.load('preds_cb.npy')

# 2. 가중치 최적화 (Nelder-Mead)
def objective(weights):
    w = weights / np.sum(weights)
    ensemble_oof = (w[0] * oof_xgb) + (w[1] * oof_lgb) + (w[2] * oof_cb)
    return np.sqrt(mean_squared_error(y_true, ensemble_oof))

# XGB의 성능이 우수하므로 가중치 시작점을 조절
res = minimize(objective, [0.6, 0.2, 0.2], method='Nelder-Mead')
best_w = res.x / np.sum(res.x)

print(f"\n🏆 최적 가중치 산출 완료!")
print(f"XGB: {best_w[0]:.4f} | LGB: {best_w[1]:.4f} | CB: {best_w[2]:.4f}")
print(f"최종 최적화 OOF RMSE: {res.fun:.5f}")

# 3. 최종 예측 및 제출 파일 생성 (ID 유실 방지)
final_preds = (best_w[0] * preds_xgb) + (best_w[1] * preds_lgb) + (best_w[2] * preds_cb)

# Post-processing: 점수 범위를 0~100 사이로 제한
final_preds = np.clip(final_preds, 0, 100)

submission = pd.DataFrame({
    'id': test_df['id'], # test.csv의 원본 ID를 그대로 사용
    'exam_score': final_preds
})

submission.to_csv('submission.csv', index=False)
print("\n🚀 submission.csv 가 생성되었습니다. 행 개수:", len(submission))