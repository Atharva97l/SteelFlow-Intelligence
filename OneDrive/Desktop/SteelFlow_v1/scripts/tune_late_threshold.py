from pathlib import Path
import json
import joblib
import duckdb
import numpy as np
import pandas as pd
from sklearn.metrics import average_precision_score, f1_score, precision_score, recall_score

ROOT = Path(__file__).parents[1]
DATA = ROOT / 'data'
MODEL_DIR = ROOT / 'artifacts' / 'models'
con = duckdb.connect()
df = con.execute(f"SELECT * FROM read_parquet('{(DATA / 'dispatch_delay_model_dataset.parquet').as_posix()}')").fetchdf()
target = 'target_is_late'
drop = [target, 'shipment_id', 'dispatch_timestamp', 'dispatch_date', 'prediction_moment', 'synthetic_record']
X = df.drop(columns=[c for c in drop if c in df])
y = df[target].astype(int)
valid = df['split'].eq('VALIDATION')
model = joblib.load(MODEL_DIR / 'late_delivery_best.joblib')
probability = model.predict_proba(X[valid])[:, 1]
rows = []
for threshold in np.arange(0.20, 0.81, 0.05):
    prediction = probability >= threshold
    rows.append({'threshold': float(threshold), 'f1': float(f1_score(y[valid], prediction)), 'precision': float(precision_score(y[valid], prediction, zero_division=0)), 'recall': float(recall_score(y[valid], prediction)), 'pr_auc': float(average_precision_score(y[valid], probability))})
table = pd.DataFrame(rows)
best = table.sort_values(['f1', 'recall'], ascending=False).iloc[0].to_dict()
table.to_csv(MODEL_DIR / 'late_threshold_candidates.csv', index=False)
(MODEL_DIR / 'late_delivery_threshold.json').write_text(json.dumps(best, indent=2), encoding='utf-8')
print(table.to_string(index=False))
print('recommended:', best)
