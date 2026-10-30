from pathlib import Path
import joblib
import duckdb
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import average_precision_score, roc_auc_score

ROOT = Path(__file__).parents[1]
DATA = ROOT / 'data'
OUT = ROOT / 'artifacts' / 'models'
OUT.mkdir(parents=True, exist_ok=True)
con = duckdb.connect()

def fit(df, target, name, drops):
    df = df.dropna(subset=[target]).sample(min(len(df), 150000), random_state=42)
    if df[target].nunique() < 2:
        return [{'task': name, 'status': 'skipped_single_class_target'}]
    X = df.drop(columns=[target] + drops, errors='ignore')
    y = df[target].astype(int)
    cat = X.select_dtypes(include=['object', 'bool']).columns.tolist()
    num = [c for c in X.columns if c not in cat]
    pre = ColumnTransformer([('num', Pipeline([('impute', SimpleImputer(strategy='median')), ('scale', StandardScaler())]), num), ('cat', Pipeline([('impute', SimpleImputer(strategy='most_frequent')), ('onehot', OneHotEncoder(handle_unknown='ignore'))]), cat)])
    results = []
    best = None
    for model_name, estimator in {'logistic': LogisticRegression(max_iter=1000, class_weight='balanced'), 'random_forest': RandomForestClassifier(n_estimators=60, min_samples_leaf=5, class_weight='balanced', random_state=42, n_jobs=-1)}.items():
        pipe = Pipeline([('pre', pre), ('model', estimator)])
        pipe.fit(X, y)
        probability = pipe.predict_proba(X)[:, 1]
        row = {'task': name, 'model': model_name, 'positive_rate': float(y.mean()), 'pr_auc_in_sample': float(average_precision_score(y, probability)), 'roc_auc_in_sample': float(roc_auc_score(y, probability))}
        results.append(row)
        if best is None or row['pr_auc_in_sample'] > best[0]:
            best = (row['pr_auc_in_sample'], pipe)
    joblib.dump(best[1], OUT / f'{name}_best.joblib')
    return results

inventory = con.execute(f"SELECT * FROM read_parquet('{(DATA / 'finished_goods_inventory_snapshots.parquet').as_posix()}')").fetchdf()
inventory['snapshot_date'] = pd.to_datetime(inventory['snapshot_date'])
inventory = inventory.sort_values(['node_id', 'sku_id', 'snapshot_date'])
inventory['future_stockout_7d'] = inventory.groupby(['node_id', 'sku_id'])['atp_kg'].shift(-1).le(0).astype('float')
results = fit(inventory, 'future_stockout_7d', 'inventory_stockout', ['atp_kg', 'snapshot_date'])

supplier = con.execute(f"SELECT * FROM read_parquet('{(DATA / 'supplier_material_month_performance.parquet').as_posix()}')").fetchdf()
supplier['receipt_month'] = pd.to_datetime(supplier['receipt_month'])
supplier = supplier.sort_values(['supplier_id', 'material_id', 'receipt_month'])
supplier['future_late_receipt'] = supplier.groupby(['supplier_id', 'material_id'])['late_receipt_count'].shift(-1).gt(0).astype('float')
results += fit(supplier, 'future_late_receipt', 'supplier_late_receipt', ['late_receipt_count', 'late_receipt_rate', 'receipt_month', 'synthetic_record'])

flat = []
for value in results:
    flat.extend(value if isinstance(value, list) else [value])
pd.DataFrame(flat).to_csv(OUT / 'inventory_supplier_metrics.csv', index=False)
print(pd.DataFrame(flat).to_string(index=False))
