# SteelFlow project status

## Completed

- Profiled 69 Parquet tables and documented table inventory, domains, grain, and initial data flow.
- Added EDA notebooks for inventory, demand, delivery/freight, and wider commercial/supply-chain analysis.
- Added KPI generation for carriers, routes, customers, warehouses, and supplier-material performance.
- Added baseline ML comparison for late delivery and freight cost.
- Added saved late-delivery and freight-cost pipelines under `artifacts/models`.
- Added a Streamlit prediction UI in `app.py`.
- Added chronology and cutoff-date checks for forecasting features.

## Current modeling state

- Late delivery: Logistic Regression currently leads validation PR-AUC.
- Freight cost: Ridge currently leads validation MAE.
- Demand forecasting: seasonal-naive, Ridge, and Random Forest training workflow is prepared for 7-, 14-, and 30-day horizons.
- Inventory stockout and supplier late-receipt models now use next-period targets rather than same-period labels.
- Late-delivery alert threshold is calibrated from the validation split at 0.45.
- Future-period holdout validation: inventory stockout Random Forest PR-AUC is approximately 0.994; supplier late-receipt models are near 0.68–0.69 PR-AUC with only 261 holdout rows and should remain experimental.

## Next implementation order

1. Complete demand horizon training and compare against seasonal-naive baselines.
2. Tune late-delivery decision thresholds and calibrate probabilities.
3. Build customer inactivity/churn-risk target and model.
4. Expand credit/default-risk validation to a chronological holdout.
5. Expand stockout/inventory-risk and supplier-performance validation to chronological holdouts.
6. Register selected pipelines, metrics, feature versions, and model metadata.
7. Connect demand and risk models to the Streamlit UI.
8. Add deployment monitoring for input drift, prediction drift, and delayed ground-truth performance.
