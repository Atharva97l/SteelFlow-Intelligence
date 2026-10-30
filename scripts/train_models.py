"""Train Stage 2 SteelFlow models and save validation metrics/artifacts."""
from pathlib import Path
import json
import joblib
import duckdb
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression, Ridge
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.metrics import average_precision_score, roc_auc_score, f1_score, mean_absolute_error, mean_squared_error

ROOT = Path(__file__).parents[1]
DATA = ROOT / 'data'
OUT = ROOT / 'artifacts' / 'models'
OUT.mkdir(parents=True, exist_ok=True)
con = duckdb.connect()
results = []

def prep(X):
    cat = X.select_dtypes(include=['object', 'bool']).columns.tolist()
    num = [c for c in X.columns if c not in cat]
    return ColumnTransformer([
        ('num', Pipeline([('impute', SimpleImputer(strategy='median')), ('scale', StandardScaler())]), num),
        ('cat', Pipeline([('impute', SimpleImputer(strategy='most_frequent')), ('onehot', OneHotEncoder(handle_unknown='ignore'))]), cat),
    ])

def run_classification():
    path = DATA / 'dispatch_delay_model_dataset.parquet'
    df = con.execute(f"SELECT * FROM read_parquet('{path.as_posix()}')").fetchdf()
    df['load_utilization'] = df['shipment_weight_kg'] / df['vehicle_capacity_kg'].clip(lower=1)
    df['over_capacity'] = df['shipment_weight_kg'] > df['vehicle_capacity_kg']
    target = 'target_is_late'
    drop = [target, 'shipment_id', 'dispatch_timestamp', 'dispatch_date', 'prediction_moment', 'synthetic_record', 'split']
    X = df.drop(columns=[c for c in drop if c in df]); y = df[target].astype(int)
    train, valid, test = df['split'].eq('TRAIN'), df['split'].eq('VALIDATION'), df['split'].eq('TEST')
    candidates = {'logistic_regression': LogisticRegression(max_iter=1000, class_weight='balanced'), 'random_forest': RandomForestClassifier(n_estimators=80, min_samples_leaf=5, class_weight='balanced', n_jobs=-1, random_state=42)}
    best = None
    for name, estimator in candidates.items():
        pipe = Pipeline([('pre', prep(X)), ('model', estimator)])
        pipe.fit(X[train], y[train]); p = pipe.predict_proba(X[valid])[:, 1]
        row = {'task': 'late_delivery', 'model': name, 'validation_pr_auc': average_precision_score(y[valid], p), 'validation_roc_auc': roc_auc_score(y[valid], p), 'validation_f1': f1_score(y[valid], p >= .5)}
        results.append(row)
        if best is None or row['validation_pr_auc'] > best[0]: best = (row['validation_pr_auc'], name, pipe)
    _, name, pipe = best
    pipe.fit(X[train | valid], y[train | valid]); p = pipe.predict_proba(X[test])[:, 1]
    results.append({'task': 'late_delivery', 'model': name, 'split': 'TEST', 'test_pr_auc': average_precision_score(y[test], p), 'test_roc_auc': roc_auc_score(y[test], p), 'test_f1': f1_score(y[test], p >= .5)})
    joblib.dump(pipe, OUT / 'late_delivery_best.joblib')

def run_freight():
    path = DATA / 'freight_cost_model_dataset.parquet'
    df = con.execute(f"SELECT * FROM read_parquet('{path.as_posix()}')").fetchdf()
    target = 'target_actual_billed_freight_cost_inr_ex_gst'
    drop = [target, 'freight_invoice_id', 'shipment_id', 'quote_timestamp', 'prediction_moment', 'synthetic_record']
    X = df.drop(columns=[c for c in drop if c in df]); y = df[target]
    train, valid, test = df['split'].eq('TRAIN'), df['split'].eq('VALIDATION'), df['split'].eq('TEST')
    candidates = {'ridge': Ridge(alpha=10), 'random_forest': RandomForestRegressor(n_estimators=60, min_samples_leaf=5, n_jobs=-1, random_state=42)}
    best = None
    for name, estimator in candidates.items():
        pipe = Pipeline([('pre', prep(X)), ('model', estimator)])
        pipe.fit(X[train], y[train]); pred = pipe.predict(X[valid])
        row = {'task': 'freight_cost', 'model': name, 'validation_mae': mean_absolute_error(y[valid], pred), 'validation_rmse': mean_squared_error(y[valid], pred) ** .5}
        results.append(row)
        if best is None or row['validation_mae'] < best[0]: best = (row['validation_mae'], name, pipe)
    _, name, pipe = best
    pipe.fit(X[train | valid], y[train | valid]); pred = pipe.predict(X[test])
    results.append({'task': 'freight_cost', 'model': name, 'split': 'TEST', 'test_mae': mean_absolute_error(y[test], pred), 'test_rmse': mean_squared_error(y[test], pred) ** .5})
    joblib.dump(pipe, OUT / 'freight_cost_best.joblib')

run_classification()
run_freight()
pd.DataFrame(results).to_csv(OUT / 'model_metrics.csv', index=False)
(OUT / 'model_metrics.json').write_text(json.dumps(results, indent=2, default=float), encoding='utf-8')
print(pd.DataFrame(results).to_string(index=False))
