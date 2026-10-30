"""Create simple distribution-drift checks for key operational features."""
from pathlib import Path
import duckdb
import pandas as pd

ROOT = Path(__file__).parents[1]
DATA = ROOT / 'data'
OUT = ROOT / 'artifacts' / 'monitoring'
OUT.mkdir(parents=True, exist_ok=True)
con = duckdb.connect()
df = con.execute(f"SELECT * FROM read_parquet('{(DATA/'dispatch_delay_model_dataset.parquet').as_posix()}')").fetchdf()
train = df[df.split == 'TRAIN']
test = df[df.split == 'TEST']
rows = []
for col in ['distance_km', 'shipment_weight_kg', 'route_congestion_index_0_1', 'capacity_pressure_0_1', 'carrier_historical_late_rate_90d']:
    rows.append({'feature': col, 'train_mean': float(train[col].mean()), 'test_mean': float(test[col].mean()), 'relative_change': float((test[col].mean() - train[col].mean()) / (abs(train[col].mean()) + 1e-9)), 'train_missing': float(train[col].isna().mean()), 'test_missing': float(test[col].isna().mean())})
pd.DataFrame(rows).to_csv(OUT / 'feature_drift_report.csv', index=False)
print(pd.DataFrame(rows).to_string(index=False))
