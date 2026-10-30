from pathlib import Path
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
con = duckdb.connect()

def evaluate(df, target, date_col, task, drops):
    df = df.dropna(subset=[target]).sort_values(date_col)
    if len(df) > 120000:
        df = df.sample(120000, random_state=42).sort_values(date_col)
    cutoff = df[date_col].quantile(0.8)
    train = df[date_col] <= cutoff
    test = ~train
    X = df.drop(columns=[target] + drops, errors='ignore')
    y = df[target].astype(int)
    cat = X.select_dtypes(include=['object', 'bool']).columns.tolist()
    num = [c for c in X.columns if c not in cat]
    pre = ColumnTransformer([('num', Pipeline([('impute', SimpleImputer(strategy='median')), ('scale', StandardScaler())]), num), ('cat', Pipeline([('impute', SimpleImputer(strategy='most_frequent')), ('onehot', OneHotEncoder(handle_unknown='ignore'))]), cat)])
    rows = []
    for name, estimator in {'logistic': LogisticRegression(max_iter=1000, class_weight='balanced'), 'random_forest': RandomForestClassifier(n_estimators=50, min_samples_leaf=5, class_weight='balanced', random_state=42, n_jobs=-1)}.items():
        pipe = Pipeline([('pre', pre), ('model', estimator)])
        pipe.fit(X[train], y[train])
        probability = pipe.predict_proba(X[test])[:, 1]
        rows.append({'task': task, 'model': name, 'train_end': str(cutoff.date()), 'test_rows': int(test.sum()), 'test_positive_rate': float(y[test].mean()), 'test_pr_auc': float(average_precision_score(y[test], probability)), 'test_roc_auc': float(roc_auc_score(y[test], probability))})
    return rows

inventory = con.execute(f"SELECT * FROM read_parquet('{(DATA / 'finished_goods_inventory_snapshots.parquet').as_posix()}')").fetchdf()
inventory['snapshot_date'] = pd.to_datetime(inventory.snapshot_date)
inventory = inventory.sort_values(['node_id', 'sku_id', 'snapshot_date'])
inventory['future_stockout_7d'] = inventory.groupby(['node_id', 'sku_id']).atp_kg.shift(-1).le(0).astype('float')
results = evaluate(inventory, 'future_stockout_7d', 'snapshot_date', 'inventory_stockout', ['atp_kg', 'snapshot_date'])

supplier = con.execute(f"SELECT * FROM read_parquet('{(DATA / 'supplier_material_month_performance.parquet').as_posix()}')").fetchdf()
supplier['receipt_month'] = pd.to_datetime(supplier.receipt_month)
supplier = supplier.sort_values(['supplier_id', 'material_id', 'receipt_month'])
supplier['future_late_receipt'] = supplier.groupby(['supplier_id', 'material_id']).late_receipt_count.shift(-1).gt(0).astype('float')
results += evaluate(supplier, 'future_late_receipt', 'receipt_month', 'supplier_late_receipt', ['late_receipt_count', 'late_receipt_rate', 'receipt_month', 'synthetic_record'])
pd.DataFrame(results).to_csv(OUT / 'inventory_supplier_holdout_metrics.csv', index=False)
print(pd.DataFrame(results).to_string(index=False))
