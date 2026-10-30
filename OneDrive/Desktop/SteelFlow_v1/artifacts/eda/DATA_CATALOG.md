# SteelFlow data catalog

Generated from `C:\Users\Sunil\OneDrive\Desktop\SteelFlow_v1\data`. Tables profiled: **69**.

## Table inventory

| Table | Rows | Columns | Null cells |
|---|---:|---:|---:|
| `accounts_payable` | 1,446 | 14 | 0 |
| `accounts_receivable` | 64,554 | 23 | 65,896 |
| `backorders_cancellations_returns` | 110,196 | 14 | 634,345 |
| `bad_debt_writeoffs` | 319 | 7 | 0 |
| `business_events` | 5 | 6 | 0 |
| `carrier_events` | 30 | 8 | 0 |
| `carrier_rate_cards` | 1,011 | 16 | 0 |
| `carrier_route_eligibility` | 1,080 | 5 | 0 |
| `carrier_route_month_performance` | 22,833 | 12 | 0 |
| `carriers` | 15 | 8 | 0 |
| `cash_receipts` | 85,968 | 8 | 0 |
| `credit_notes` | 1,626 | 12 | 0 |
| `customer_credit_state` | 410,850 | 8 | 0 |
| `customer_default_events` | 18 | 11 | 0 |
| `customer_invoices` | 64,554 | 17 | 0 |
| `customer_order_lines` | 92,751 | 48 | 0 |
| `customer_orders` | 40,000 | 27 | 0 |
| `customer_payment_behaviour_monthly` | 13,500 | 14 | 0 |
| `customers` | 225 | 9 | 0 |
| `daily_demand_by_sku_centre` | 876,480 | 11 | 0 |
| `delivery_outcomes` | 64,554 | 16 | 0 |
| `demand_centres` | 12 | 6 | 0 |
| `dispatch_delay_model_dataset` | 64,554 | 30 | 0 |
| `dispute_events` | 1,281 | 10 | 0 |
| `factories` | 2 | 10 | 0 |
| `factory_allocation_decisions` | 92,751 | 12 | 0 |
| `factory_capacity_downtime_events` | 6 | 6 | 0 |
| `factory_product_capabilities` | 80 | 7 | 0 |
| `feature_manifest` | 74 | 9 | 0 |
| `finished_goods_inventory_movements` | 212,421 | 10 | 0 |
| `finished_goods_inventory_snapshots` | 525,840 | 7 | 0 |
| `forecast_features_horizon_07` | 873,120 | 39 | 0 |
| `forecast_features_horizon_14` | 869,760 | 39 | 0 |
| `forecast_features_horizon_30` | 862,080 | 39 | 0 |
| `freight_cost_benchmarks` | 64,554 | 20 | 604 |
| `freight_cost_model_dataset` | 64,554 | 24 | 0 |
| `freight_invoice_anomaly_audit` | 64,554 | 8 | 64,093 |
| `freight_invoices` | 64,554 | 16 | 64,093 |
| `goods_receipts` | 3,730 | 18 | 0 |
| `gst_payable` | 62 | 8 | 0 |
| `holidays` | 25 | 4 | 0 |
| `internal_transfers` | 19,799 | 13 | 0 |
| `materials` | 4 | 6 | 0 |
| `monthly_market_indices` | 60 | 5 | 0 |
| `outbound_shipments` | 64,554 | 62 | 101,217 |
| `product_material_recipes` | 50 | 6 | 0 |
| `production_batches` | 44,435 | 17 | 0 |
| `production_planning_diagnostics` | 146,080 | 21 | 80 |
| `products` | 40 | 12 | 0 |
| `purchase_order_lines` | 1,446 | 21 | 0 |
| `purchase_orders` | 1,329 | 13 | 0 |
| `quality_inspections` | 3,730 | 7 | 2,776 |
| `raw_ingestion_customer_orders` | 40,000 | 30 | 3,186 |
| `raw_ingestion_freight_invoices` | 64,554 | 19 | 65,704 |
| `raw_material_inventory_movements` | 58,158 | 9 | 0 |
| `raw_material_inventory_snapshots` | 17,528 | 4 | 0 |
| `reservations` | 129,108 | 8 | 0 |
| `route_conditions_daily` | 131,472 | 9 | 0 |
| `routes` | 72 | 7 | 0 |
| `scheduler_daily_runs` | 1,826 | 3 | 0 |
| `scrap_sales` | 44,435 | 8 | 0 |
| `supplier_cash_payments` | 1,446 | 9 | 0 |
| `supplier_events` | 150 | 8 | 0 |
| `supplier_material_month_performance` | 1,368 | 12 | 0 |
| `supplier_materials` | 87 | 8 | 0 |
| `suppliers` | 30 | 8 | 0 |
| `vehicle_classes` | 5 | 4 | 0 |
| `warehouse_stock_snapshots` | 350,560 | 7 | 0 |
| `warehouses` | 4 | 8 | 0 |

## Initial findings

- `daily_demand_by_sku_centre` covers 1 January 2022 through 31 December 2026, with 12 demand centres and 40 SKUs.
- `forecast_features_horizon_07` contains explicit `origin_date`, `feature_cutoff_date`, `target_date`, and `split` fields. The seven-day horizon is partitioned chronologically into TRAIN (2022–2024), VALIDATION (2025), and TEST (2026).
- `dispatch_delay_model_dataset` contains the same chronological split pattern and an approximately 25.7% late-delivery rate in train, validation, and test; accuracy alone will therefore be insufficient for model selection.
- `freight_cost_model_dataset` provides a continuous billed-cost target and the same prediction-time split, making it a strong candidate for a regression benchmark after leakage review.

## Modeling domains

- **Demand and sales forecasting:** `customer_orders`, `customer_order_lines`, `daily_demand_by_sku_centre`, `forecast_features_horizon_07`, `forecast_features_horizon_14`, `forecast_features_horizon_30`.
- **Factory planning and allocation:** `factories`, `factory_product_capabilities`, `factory_capacity_downtime_events`, `factory_allocation_decisions`, `production_batches`, `production_planning_diagnostics`.
- **Logistics and delivery:** `outbound_shipments`, `delivery_outcomes`, `dispatch_delay_model_dataset`, `routes`, `route_conditions_daily`, `carrier_events`, `carrier_route_month_performance`.
- **Finance and credit:** `customer_invoices`, `accounts_receivable`, `cash_receipts`, `customer_credit_state`, `customer_default_events`, `freight_invoices`, `freight_cost_model_dataset`.
- **Inventory and materials:** `finished_goods_inventory_snapshots`, `finished_goods_inventory_movements`, `warehouse_stock_snapshots`, `raw_material_inventory_snapshots`, `reservations`, `materials`, `products`.

## Recommended data flow

1. **Master data** (`customers`, `products`, `factories`, `warehouses`, `carriers`, `routes`) provides stable entity attributes.
2. **Events and transactions** (orders, shipments, production, inventory, invoices, payments) provide time-stamped facts.
3. **Outcome tables** (`delivery_outcomes`, `customer_credit_state`, `production_planning_diagnostics`) define supervised learning targets.
4. **Feature tables** (`forecast_features_horizon_*`, `dispatch_delay_model_dataset`, `freight_cost_model_dataset`) are candidate modeling marts and must be checked for leakage before training.

## EDA principles

- Confirm row grain and key uniqueness before joining tables.
- Use time-based train/validation/test splits for forecasting and operational prediction.
- Treat prebuilt feature tables as derived data; trace each feature back to its source and availability timestamp.
- Compare models with task-specific metrics: WAPE/MAE for demand, RMSE/MAE for continuous targets, and PR-AUC/recall plus calibration for late-delivery classification.
