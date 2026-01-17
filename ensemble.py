import numpy as np
import pandas as pd
from sklearn.metrics import mean_squared_error
from scipy.optimize import minimize

# 1. 데이터 로드 (ID 복구를 위해 원본 테스트 파일 필요)
test_df = pd.read_csv('./data/test.csv') # index_col 없이 로드
y_true = pd.read_csv('./data/train.csv')['exam_score'].values

# 저장된 OOF(Out-of-Fold) 파일 로드
oof_xgb = np.load('oof_xgb.npy')
oof_lgb = np.load('oof_lgb.npy')
oof_cb = np.load('oof_cb.npy')

# 저장된 Test 예측 파일 로드
preds_xgb = np.load('preds_xgb.npy')
preds_lgb = np.load('preds_lgb.npy')
preds_cb = np.load('preds_cb.npy')

# 2. Hill Climbing (최적 가중치 찾기)
def objective(weights):
    # 가중치 합이 1이 되도록 정규화
    w = weights / np.sum(weights)
    ensemble_oof = (w[0] * oof_xgb) + (w[1] * oof_lgb) + (w[2] * oof_cb)
    return np.sqrt(mean_squared_error(y_true, ensemble_oof))

# 초기 가중치 [XGB, LGB, CB]
initial_weights = [0.6, 0.2, 0.2]

# 최적화 수행
res = minimize(objective, initial_weights, method='Nelder-Mead')
best_weights = res.x / np.sum(res.x)

print(f"\n✅ 최적 가중치 발견!")
print(f"XGB: {best_weights[0]:.4f}, LGB: {best_weights[1]:.4f}, CB: {best_weights[2]:.4f}")
print(f"최적화된 OOF RMSE: {res.fun:.5f}")

# 3. 최종 예측 및 ID 정렬 제출
final_preds = (best_weights[0] * preds_xgb) + \
              (best_weights[1] * preds_lgb) + \
              (best_weights[2] * preds_cb)

# 에러 방지용: ID를 원본 테스트 파일에서 정확히 가져옴
submission = pd.DataFrame({
    'id': test_df['id'],  # 원본 id 보존
    'exam_score': final_preds
})

submission.to_csv('submission_final.csv', index=False)
print("\n🚀 submission_final.csv 생성 완료!")