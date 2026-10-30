from pathlib import Path
import joblib
import duckdb
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import average_precision_score, roc_auc_score

ROOT = Path(__file__).parents[1]
DATA = ROOT / 'data'
OUT = ROOT / 'artifacts' / 'models'
OUT.mkdir(parents=True, exist_ok=True)
con = duckdb.connect()
cutoff = pd.Timestamp('2023-12-31')
future_end = cutoff + pd.Timedelta(days=180)

orders = con.execute(f"SELECT * FROM read_parquet('{(DATA / 'customer_orders.parquet').as_posix()}')").fetchdf()
orders['order_date'] = pd.to_datetime(orders['order_date'])
history = orders[orders.order_date <= cutoff]
features = history.groupby('customer_id').agg(last_event_date=('order_date', 'max'), order_count=('order_id', 'nunique'), revenue=('order_value_ex_gst', 'sum'), weight_kg=('ordered_weight_kg', 'sum'), avg_order_value=('order_value_ex_gst', 'mean'), avg_payment_delay=('expected_payment_delay_days_at_check', 'mean')).reset_index()
features['recency_days'] = (cutoff - features.last_event_date).dt.days
future_customers = orders[(orders.order_date > cutoff) & (orders.order_date <= future_end)].customer_id.unique()
features['inactive_180d'] = (~features.customer_id.isin(future_customers)).astype(int)

def train(df, target, name):
    X = df.drop(columns=[target, 'customer_id', 'last_event_date', 'date'], errors='ignore')
    y = df[target]
    if y.nunique() < 2:
        return {'task': name, 'positive_rate': float(y.mean()), 'status': 'skipped_single_class_target'}
    numeric = X.columns.tolist()
    pre = ColumnTransformer([('num', Pipeline([('impute', SimpleImputer(strategy='median')), ('scale', StandardScaler())]), numeric)])
    pipe = Pipeline([('pre', pre), ('model', LogisticRegression(max_iter=1000, class_weight='balanced'))])
    pipe.fit(X, y)
    probability = pipe.predict_proba(X)[:, 1]
    metrics = {'task': name, 'positive_rate': float(y.mean()), 'pr_auc_in_sample': float(average_precision_score(y, probability)), 'roc_auc_in_sample': float(roc_auc_score(y, probability))}
    joblib.dump(pipe, OUT / f'{name}_best.joblib')
    return metrics

results = [train(features, 'inactive_180d', 'customer_inactivity')]
defaults = con.execute(f"SELECT * FROM read_parquet('{(DATA / 'customer_default_events.parquet').as_posix()}')").fetchdf()
defaults['default_date'] = pd.to_datetime(defaults.default_date)
credit = con.execute(f"SELECT * FROM read_parquet('{(DATA / 'customer_credit_state.parquet').as_posix()}')").fetchdf()
credit['date'] = pd.to_datetime(credit.date)
state = credit[credit.date <= cutoff].sort_values('date').groupby('customer_id').tail(1).copy()
state['credit_utilization'] = state.outstanding_balance_inr / state.credit_limit_inr.clip(lower=1)
state['last_event_date'] = state['date']
state['default_180d'] = state.customer_id.isin(defaults[(defaults.default_date > cutoff) & (defaults.default_date <= future_end)].customer_id).astype(int)
results.append(train(state, 'default_180d', 'credit_default'))
pd.DataFrame(results).to_csv(OUT / 'customer_credit_risk_metrics.csv', index=False)
print(pd.DataFrame(results).to_string(index=False))
