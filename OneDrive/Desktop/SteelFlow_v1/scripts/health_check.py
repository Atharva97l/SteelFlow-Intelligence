from pathlib import Path
import joblib

root = Path(__file__).parents[1]
required = [
    'late_delivery_best.joblib',
    'freight_cost_best.joblib',
    'demand_horizon_07_best.joblib',
    'demand_horizon_14_best.joblib',
    'demand_horizon_30_best.joblib',
    'credit_default_best.joblib',
    'inventory_stockout_best.joblib',
    'supplier_late_receipt_best.joblib',
    'customer_churn_90d_best.joblib',
]
for name in required:
    path = root / 'artifacts' / 'models' / name
    if not path.exists():
        raise SystemExit(f'Missing model artifact: {name}')
    model = joblib.load(path)
    if not hasattr(model, 'predict'):
        raise SystemExit(f'Invalid pipeline: {name}')
print(f'Health check passed for {len(required)} model pipelines')
