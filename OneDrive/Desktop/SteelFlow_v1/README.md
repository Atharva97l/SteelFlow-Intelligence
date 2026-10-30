# SteelFlow ML Operations

SteelFlow is a synthetic steel-company analytics and machine-learning project covering demand, sales, factories, inventory, logistics, delivery, suppliers, receivables, and customer risk.

## Included

- KPI-first EDA notebooks and rendered HTML reports
- Parquet data profiling and data-flow documentation
- Demand forecasting for 7-, 14-, and 30-day horizons
- Late-delivery classification with calibrated alert threshold
- Freight-cost regression
- Credit-default, inventory-stockout, supplier-late-receipt, and customer-inactivity risk models
- Streamlit prediction dashboard with KPI tables
- Saved preprocessing pipelines, metrics, registry, Dockerfile, and health checks

## Setup

```powershell
cd C:\Users\Sunil\OneDrive\Desktop\SteelFlow_v1
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

The Parquet files must be present in `data/`.

## EDA and KPIs

```powershell
python scripts/profile_data.py
python scripts/build_kpis.py
```

Open `artifacts/eda/index.html` for the catalog, KPI outputs, rendered EDA, and model results.

## Train models

```powershell
python scripts/train_models.py
python scripts/train_demand_models.py
python scripts/train_customer_credit_risk.py
python scripts/train_inventory_supplier_models.py
python scripts/train_churn_model.py
python scripts/tune_late_threshold.py
python scripts/build_registry.py
python scripts/health_check.py
```

Existing `.joblib` files in `artifacts/models/` can be used without retraining.

## Run the website

```powershell
streamlit run app.py
```

Open `http://localhost:8501`. The dashboard provides KPI tables, dropdowns populated from actual Parquet values, predictions, estimated delivery delay days, and model-performance tables.

## Docker deployment

```powershell
docker build -t steelflow-ml .
docker run --rm -p 8501:8501 steelflow-ml
```

Then open `http://localhost:8501`.

Validate the deployment artifacts with:

```powershell
python scripts/health_check.py
```

## Evaluation

Forecasting uses chronological origin, cutoff, and target dates. Classification uses PR-AUC, ROC-AUC, recall, precision, F1, and calibration. Regression uses MAE, RMSE, and WAPE. Metrics are stored under `artifacts/models/`.

Supplier late-receipt and customer-churn models are experimental because their future holdout signal is weak.
