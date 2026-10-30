"""Generate a lightweight, reproducible SteelFlow Parquet data profile."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import duckdb


def sql_path(path: Path) -> str:
    return str(path).replace("'", "''")


def profile(data_dir: Path, output_dir: Path) -> None:
    files = sorted(data_dir.glob("*.parquet"))
    if not files:
        raise SystemExit(f"No Parquet files found in {data_dir}")
    output_dir.mkdir(parents=True, exist_ok=True)
    con = duckdb.connect()
    catalog: list[dict] = []
    for path in files:
        source = sql_path(path)
        columns = con.execute(
            f"DESCRIBE SELECT * FROM read_parquet('{source}')"
        ).fetchall()
        row_count = con.execute(
            f"SELECT count(*) FROM read_parquet('{source}')"
        ).fetchone()[0]
        nulls = con.execute(
            f"SELECT * FROM read_parquet('{source}') LIMIT 0"
        ).description
        null_expr = ", ".join(
            f"count(*) - count(\"{col[0]}\") AS \"{col[0]}\"" for col in nulls
        )
        null_counts = con.execute(
            f"SELECT {null_expr} FROM read_parquet('{source}')"
        ).fetchone()
        catalog.append(
            {
                "table": path.stem,
                "file": path.name,
                "rows": row_count,
                "columns": [
                    {"name": c[0], "type": c[1], "nullable": c[2]}
                    for c in columns
                ],
                "null_counts": dict(zip((c[0] for c in columns), null_counts)),
            }
        )
    (output_dir / "table_catalog.json").write_text(
        json.dumps(catalog, indent=2, default=str), encoding="utf-8"
    )
    lines = [
        "# SteelFlow data catalog",
        "",
        f"Generated from `{data_dir}`. Tables profiled: **{len(catalog)}**.",
        "",
        "## Table inventory",
        "",
        "| Table | Rows | Columns | Null cells |",
        "|---|---:|---:|---:|",
    ]
    for item in catalog:
        null_cells = sum(item["null_counts"].values())
        lines.append(
            f"| `{item['table']}` | {item['rows']:,} | {len(item['columns'])} | {null_cells:,} |"
        )
    lines += [
        "",
        "## Initial findings",
        "",
        "- `daily_demand_by_sku_centre` covers 1 January 2022 through 31 December 2026, with 12 demand centres and 40 SKUs.",
        "- `forecast_features_horizon_07` contains explicit `origin_date`, `feature_cutoff_date`, `target_date`, and `split` fields. The seven-day horizon is partitioned chronologically into TRAIN (2022–2024), VALIDATION (2025), and TEST (2026).",
        "- `dispatch_delay_model_dataset` contains the same chronological split pattern and an approximately 25.7% late-delivery rate in train, validation, and test; accuracy alone will therefore be insufficient for model selection.",
        "- `freight_cost_model_dataset` provides a continuous billed-cost target and the same prediction-time split, making it a strong candidate for a regression benchmark after leakage review.",
        "",
        "## Modeling domains",
        "",
        "- **Demand and sales forecasting:** `customer_orders`, `customer_order_lines`, `daily_demand_by_sku_centre`, `forecast_features_horizon_07`, `forecast_features_horizon_14`, `forecast_features_horizon_30`.",
        "- **Factory planning and allocation:** `factories`, `factory_product_capabilities`, `factory_capacity_downtime_events`, `factory_allocation_decisions`, `production_batches`, `production_planning_diagnostics`.",
        "- **Logistics and delivery:** `outbound_shipments`, `delivery_outcomes`, `dispatch_delay_model_dataset`, `routes`, `route_conditions_daily`, `carrier_events`, `carrier_route_month_performance`.",
        "- **Finance and credit:** `customer_invoices`, `accounts_receivable`, `cash_receipts`, `customer_credit_state`, `customer_default_events`, `freight_invoices`, `freight_cost_model_dataset`.",
        "- **Inventory and materials:** `finished_goods_inventory_snapshots`, `finished_goods_inventory_movements`, `warehouse_stock_snapshots`, `raw_material_inventory_snapshots`, `reservations`, `materials`, `products`.",
        "",
        "## Recommended data flow",
        "",
        "1. **Master data** (`customers`, `products`, `factories`, `warehouses`, `carriers`, `routes`) provides stable entity attributes.",
        "2. **Events and transactions** (orders, shipments, production, inventory, invoices, payments) provide time-stamped facts.",
        "3. **Outcome tables** (`delivery_outcomes`, `customer_credit_state`, `production_planning_diagnostics`) define supervised learning targets.",
        "4. **Feature tables** (`forecast_features_horizon_*`, `dispatch_delay_model_dataset`, `freight_cost_model_dataset`) are candidate modeling marts and must be checked for leakage before training.",
        "",
        "## EDA principles",
        "",
        "- Confirm row grain and key uniqueness before joining tables.",
        "- Use time-based train/validation/test splits for forecasting and operational prediction.",
        "- Treat prebuilt feature tables as derived data; trace each feature back to its source and availability timestamp.",
        "- Compare models with task-specific metrics: WAPE/MAE for demand, RMSE/MAE for continuous targets, and PR-AUC/recall plus calibration for late-delivery classification.",
    ]
    (output_dir / "DATA_CATALOG.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Profiled {len(catalog)} tables into {output_dir}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--data-dir", type=Path, default=Path(__file__).parents[1] / "data")
    parser.add_argument("--output-dir", type=Path, default=Path(__file__).parents[1] / "artifacts" / "eda")
    args = parser.parse_args()
    profile(args.data_dir, args.output_dir)
