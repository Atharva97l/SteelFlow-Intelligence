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

ROOT = Path(__file__).parents[1]; DATA = ROOT / 'data'; OUT = ROOT / 'artifacts' / 'models'; OUT.mkdir(parents=True, exist_ok=True)
con = duckdb.connect()
orders = con.execute(f"SELECT * FROM read_parquet('{(DATA / 'customer_orders.parquet').as_posix()}')").fetchdf()
orders['order_date'] = pd.to_datetime(orders.order_date)
orders['order_month'] = orders.order_date.dt.to_period('M').dt.to_timestamp()
monthly = orders.groupby(['customer_id', 'order_month']).agg(order_count=('order_id', 'nunique'), revenue=('order_value_ex_gst', 'sum'), weight_kg=('ordered_weight_kg', 'sum'), avg_order_value=('order_value_ex_gst', 'mean'), avg_payment_delay=('expected_payment_delay_days_at_check', 'mean')).reset_index()
monthly['next_order_date'] = monthly.groupby('customer_id').order_month.shift(-1)
monthly['churn_90d'] = monthly.next_order_date.isna() | (monthly.next_order_date > monthly.order_month + pd.Timedelta(days=90))
monthly['recency_at_snapshot'] = (monthly.order_month - monthly.order_month).dt.days
monthly = monthly.dropna(subset=['churn_90d'])
cutoff = monthly.order_month.quantile(0.8)
train = monthly.order_month <= cutoff; test = monthly.order_month > cutoff
X = monthly.drop(columns=['churn_90d', 'customer_id', 'order_month', 'next_order_date']); y = monthly.churn_90d.astype(int)
cat = X.select_dtypes(include=['object', 'bool']).columns.tolist(); num = [c for c in X.columns if c not in cat]
pre = ColumnTransformer([('num', Pipeline([('impute', SimpleImputer(strategy='median')), ('scale', StandardScaler())]), num), ('cat', Pipeline([('impute', SimpleImputer(strategy='most_frequent')), ('onehot', OneHotEncoder(handle_unknown='ignore'))]), cat)])
results = []; best = None
for name, estimator in {'logistic': LogisticRegression(max_iter=1000, class_weight='balanced'), 'random_forest': RandomForestClassifier(n_estimators=80, min_samples_leaf=5, class_weight='balanced', random_state=42, n_jobs=-1)}.items():
    pipe = Pipeline([('pre', pre), ('model', estimator)]); pipe.fit(X[train], y[train]); probability = pipe.predict_proba(X[test])[:, 1]
    row = {'task': 'customer_churn_90d', 'model': name, 'train_end': str(cutoff.date()), 'test_rows': int(test.sum()), 'test_positive_rate': float(y[test].mean()), 'test_pr_auc': float(average_precision_score(y[test], probability)), 'test_roc_auc': float(roc_auc_score(y[test], probability))}; results.append(row)
    if best is None or row['test_pr_auc'] > best[0]: best = (row['test_pr_auc'], pipe)
joblib.dump(best[1], OUT / 'customer_churn_90d_best.joblib')
pd.DataFrame(results).to_csv(OUT / 'customer_churn_metrics.csv', index=False)
print(pd.DataFrame(results).to_string(index=False))
