from pathlib import Path
import duckdb

ROOT = Path(__file__).parents[1]
DATA = ROOT / 'data'
OUT = ROOT / 'artifacts' / 'kpis'
OUT.mkdir(parents=True, exist_ok=True)
con = duckdb.connect()

queries = {
    'carrier_kpis': """SELECT carrier_id, count(*) AS shipments,
        sum(shipment_weight_kg) AS shipment_weight_kg,
        avg(CAST(is_late AS INTEGER)) AS late_rate,
        avg(delay_hours_vs_promised) AS avg_delay_hours,
        sum(quoted_freight_cost_inr) / NULLIF(sum(shipment_weight_kg), 0) AS quoted_cost_per_kg
        FROM read_parquet('{}/outbound_shipments.parquet') GROUP BY carrier_id""",
    'route_kpis': """SELECT route_id, route_type, count(*) AS shipments,
        avg(CAST(is_late AS INTEGER)) AS late_rate,
        avg(actual_transit_hours) AS avg_transit_hours,
        sum(quoted_freight_cost_inr) / NULLIF(sum(shipment_weight_kg), 0) AS quoted_cost_per_kg
        FROM read_parquet('{}/outbound_shipments.parquet') GROUP BY route_id, route_type""",
    'customer_kpis': """SELECT customer_id, count(*) AS orders,
        max(order_date) AS last_order_date,
        sum(order_value_ex_gst) AS revenue_ex_gst,
        sum(ordered_weight_kg) AS ordered_weight_kg,
        avg(order_value_ex_gst) AS avg_order_value,
        avg(expected_payment_delay_days_at_check) AS avg_expected_payment_delay_days
        FROM read_parquet('{}/customer_orders.parquet') GROUP BY customer_id""",
    'warehouse_kpis': """SELECT warehouse_id, count(*) AS snapshot_rows
        FROM read_parquet('{}/warehouse_stock_snapshots.parquet') GROUP BY warehouse_id""",
    'supplier_material_kpis': """SELECT * FROM read_parquet('{}/supplier_material_month_performance.parquet')""",
}

for name, template in queries.items():
    path = template.format(DATA.as_posix())
    con.execute(f"COPY ({path}) TO '{(OUT / (name + '.parquet')).as_posix()}' (FORMAT PARQUET)")
    con.execute(f"COPY ({path}) TO '{(OUT / (name + '.csv')).as_posix()}' (HEADER, DELIMITER ',')")
    print(name)
