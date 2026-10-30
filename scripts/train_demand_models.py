"""Train leakage-safe seasonal demand models for all forecast horizons."""
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
from sklearn.linear_model import Ridge
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error

ROOT = Path(__file__).parents[1]
DATA = ROOT / 'data'
OUT = ROOT / 'artifacts' / 'models'
OUT.mkdir(parents=True, exist_ok=True)
con = duckdb.connect()
all_results = []

for horizon in (7, 14, 30):
    path = DATA / f'forecast_features_horizon_{horizon:02d}.parquet'
    df = con.execute(f"SELECT * FROM read_parquet('{path.as_posix()}')").fetchdf()
    for c in ('origin_date', 'feature_cutoff_date', 'target_date'):
        df[c] = pd.to_datetime(df[c])
    # The target is never used as a feature. Dates are represented by known-at-origin calendar fields.
    target = 'target_demand_kg'
    drop = ['forecast_row_id', 'origin_date', 'prediction_moment', 'feature_cutoff_date', 'target_date', target, 'split', 'synthetic_record']
    X = df.drop(columns=[c for c in drop if c in df]); y = df[target].astype(float)
    cat = X.select_dtypes(include=['object', 'bool']).columns.tolist()
    num = [c for c in X.columns if c not in cat]
    pre = ColumnTransformer([
        ('num', Pipeline([('impute', SimpleImputer(strategy='median')), ('scale', StandardScaler())]), num),
        ('cat', Pipeline([('impute', SimpleImputer(strategy='most_frequent')), ('onehot', OneHotEncoder(handle_unknown='ignore'))]), cat),
    ])
    train = df['split'].eq('TRAIN'); valid = df['split'].eq('VALIDATION'); test = df['split'].eq('TEST')
    # Seasonal-naive is the business baseline when a 7-day lag is available.
    baseline = df.loc[valid, 'seasonal_naive_lag_kg'].fillna(df.loc[valid, 'trailing_7d_mean_demand_kg'])
    all_results.append({'task': f'demand_horizon_{horizon:02d}', 'model': 'seasonal_naive', 'validation_mae_kg': mean_absolute_error(y[valid], baseline), 'validation_rmse_kg': mean_squared_error(y[valid], baseline) ** .5})
    fit_idx = df.index[train]
    if len(fit_idx) > 150000:
        fit_idx = df.loc[train].sample(n=150000, random_state=42).index
    candidates = {'ridge': Ridge(alpha=10), 'random_forest': RandomForestRegressor(n_estimators=30, min_samples_leaf=5, n_jobs=-1, random_state=42)}
    best = None
    for name, estimator in candidates.items():
        pipe = Pipeline([('pre', pre), ('model', estimator)])
        pipe.fit(X.loc[fit_idx], y.loc[fit_idx])
        pred = np.maximum(pipe.predict(X[valid]), 0)
        mae = mean_absolute_error(y[valid], pred)
        row = {'task': f'demand_horizon_{horizon:02d}', 'model': name, 'validation_mae_kg': mae, 'validation_rmse_kg': mean_squared_error(y[valid], pred) ** .5, 'validation_wape': np.abs(y[valid] - pred).sum() / np.abs(y[valid]).sum()}
        all_results.append(row)
        if best is None or mae < best[0]: best = (mae, name, pipe)
    _, name, pipe = best
    fit_all = df.index[train | valid]
    if len(fit_all) > 180000:
        fit_all = df.loc[train | valid].sample(n=180000, random_state=42).index
    pipe.fit(X.loc[fit_all], y.loc[fit_all])
    pred = np.maximum(pipe.predict(X[test]), 0)
    all_results.append({'task': f'demand_horizon_{horizon:02d}', 'model': name, 'split': 'TEST', 'test_mae_kg': mean_absolute_error(y[test], pred), 'test_rmse_kg': mean_squared_error(y[test], pred) ** .5, 'test_wape': np.abs(y[test] - pred).sum() / np.abs(y[test]).sum()})
    joblib.dump(pipe, OUT / f'demand_horizon_{horizon:02d}_best.joblib')

pd.DataFrame(all_results).to_csv(OUT / 'demand_model_metrics.csv', index=False)
(OUT / 'demand_model_metrics.json').write_text(json.dumps(all_results, indent=2, default=float), encoding='utf-8')
print(pd.DataFrame(all_results).to_string(index=False))
