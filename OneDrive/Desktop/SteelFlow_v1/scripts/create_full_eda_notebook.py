from pathlib import Path
import json

root = Path(__file__).parents[1]
cells = []
def add(kind, text):
    cell = {'cell_type': kind, 'metadata': {}, 'source': text.splitlines(True)}
    if kind == 'code':
        cell.update({'execution_count': None, 'outputs': []})
    cells.append(cell)

add('markdown', '# SteelFlow full EDA and KPI analysis\n\nA business-facing workbook with reusable KPIs, trends, segments, quality checks, and modeling implications.')
add('code', '''from pathlib import Path
import duckdb
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
ROOT = Path.cwd().parent if Path.cwd().name == "notebooks" else Path.cwd()
DATA = ROOT / "data"
con = duckdb.connect()
sns.set_theme(style="whitegrid")''')
add('markdown', '## 1. Data quality and grain\n\nCheck table scale, date coverage, column roles, duplicate samples, and missingness before joins.')
add('code', '''files = sorted(DATA.glob("*.parquet"))
rows = []
for path in files:
    schema = con.execute(f"DESCRIBE SELECT * FROM read_parquet('{path.as_posix()}')").fetchdf()
    count = con.execute(f"SELECT count(*) FROM read_parquet('{path.as_posix()}')").fetchone()[0]
    rows.append({'table': path.stem, 'rows': count, 'columns': len(schema), 'date_columns': int(schema.column_name.str.contains('date|time|month', case=False, regex=True).sum())})
catalog = pd.DataFrame(rows).sort_values('rows', ascending=False)
display(catalog.head(30))''')
add('markdown', '## 2. Sales and customer KPIs\n\nOrders, revenue, weight, average order value, fulfilment, cancellations, backorders, channel mix, and customer concentration.')
add('code', '''orders = con.execute(f"SELECT * FROM read_parquet('{(DATA/'customer_orders.parquet').as_posix()}')").fetchdf()
lines = con.execute(f"SELECT * FROM read_parquet('{(DATA/'customer_order_lines.parquet').as_posix()}')").fetchdf()
orders.order_date = pd.to_datetime(orders.order_date)
orders['month'] = orders.order_date.dt.to_period('M').dt.to_timestamp()
display(pd.DataFrame({'metric':['orders','customers','revenue_ex_gst','ordered_weight_kg','avg_order_value','avg_lines_per_order'],'value':[orders.order_id.nunique(),orders.customer_id.nunique(),orders.order_value_ex_gst.sum(),orders.ordered_weight_kg.sum(),orders.order_value_ex_gst.mean(),orders.line_count.mean()]}))
display(orders.groupby('month').agg(orders=('order_id','nunique'),customers=('customer_id','nunique'),revenue=('order_value_ex_gst','sum'),weight_kg=('ordered_weight_kg','sum')).tail(24))
display(pd.DataFrame({'metric':['requested_kg','ordered_kg','shipped_kg','cancelled_kg','backorder_kg','fulfilment_rate'],'value':[lines.requested_quantity_kg.sum(),lines.ordered_quantity_kg.sum(),lines.shipped_quantity_kg.sum(),lines.cancelled_quantity_kg.sum(),lines.open_backorder_quantity_kg.sum(),lines.shipped_quantity_kg.sum()/lines.ordered_quantity_kg.sum()]}))''')
add('markdown', '## 3. Demand and seasonality\n\nMeasure month, weekday, monsoon, product-family, SKU, centre, volatility, and top demand combinations.')
add('code', '''demand = con.execute(f"SELECT * FROM read_parquet('{(DATA/'daily_demand_by_sku_centre.parquet').as_posix()}')").fetchdf()
demand.target_date = pd.to_datetime(demand.target_date)
demand['month'] = demand.target_date.dt.month
display(pd.DataFrame({'metric':['date_min','date_max','centres','skus','total_demand_kg','mean_row_demand_kg','std_row_demand_kg'],'value':[demand.target_date.min(),demand.target_date.max(),demand.demand_centre_id.nunique(),demand.sku_id.nunique(),demand.demand_kg.sum(),demand.demand_kg.mean(),demand.demand_kg.std()]}))
display(demand.groupby(['month','is_monsoon_season']).demand_kg.agg(['sum','mean','std']))
display(demand.groupby(['product_family','sku_id','demand_centre_id']).demand_kg.sum().sort_values(ascending=False).head(20).to_frame('demand_kg'))''')
add('markdown', '## 4. Logistics and carrier KPIs\n\nLate rate, delay hours, short-delivery rate, cost per kg, carrier concentration, route risk, and seasonal disruption effects.')
add('code', '''ship = con.execute(f"SELECT * FROM read_parquet('{(DATA/'outbound_shipments.parquet').as_posix()}')").fetchdf()
ship['short_delivery'] = ship.short_quantity_kg.gt(0)
ship['cost_per_kg'] = ship.quoted_freight_cost_inr / ship.shipment_weight_kg.clip(lower=1)
display(pd.DataFrame({'metric':['shipments','carriers','routes','late_rate','avg_delay_hours','short_delivery_rate','avg_cost_per_kg'],'value':[len(ship),ship.carrier_id.nunique(),ship.route_id.nunique(),ship.is_late.mean(),ship.delay_hours_vs_promised.mean(),ship.short_delivery.mean(),ship.cost_per_kg.mean()]}))
display(ship.groupby('carrier_id').agg(shipments=('shipment_id','size'),late_rate=('is_late','mean'),delay_hours=('delay_hours_vs_promised','mean'),cost_per_kg=('cost_per_kg','mean')).sort_values('late_rate',ascending=False).head(20))
display(ship.groupby('is_monsoon_season').agg(late_rate=('is_late','mean'),delay_hours=('delay_hours_vs_promised','mean'),cost_per_kg=('cost_per_kg','mean')))''')
add('markdown', '## 5. Factory and production\n\nInspect production batch scale, quality inspections, allocation choices, downtime, and factory capability coverage before creating allocation or yield targets.')
add('code', '''for name in ['production_batches','quality_inspections','factory_allocation_decisions','factory_capacity_downtime_events']:
    path = DATA / f'{name}.parquet'
    schema = con.execute(f"DESCRIBE SELECT * FROM read_parquet('{path.as_posix()}')").fetchdf()
    print(name, con.execute(f"SELECT count(*) FROM read_parquet('{path.as_posix()}')").fetchone()[0], 'rows')
    display(schema[['column_name','column_type']].head(20))''')
add('markdown', '## 6. Inventory, receivables, and suppliers\n\nInventory KPIs include ATP, stockout rate, reserved ratio, node/SKU concentration, and volatility. Finance KPIs include balance, utilization, blocked rate, and payment delay. Supplier KPIs include acceptance, rejection, late receipt, and concentration.')
add('code', '''inventory = con.execute(f"SELECT * FROM read_parquet('{(DATA/'finished_goods_inventory_snapshots.parquet').as_posix()}')").fetchdf()
inventory['stockout'] = inventory.atp_kg.le(0)
inventory['reserved_ratio'] = inventory.open_reserved_quantity_kg / inventory.quantity_kg.clip(lower=1)
display(pd.DataFrame({'metric':['snapshots','nodes','skus','atp_kg','stockout_rate','reserved_ratio'],'value':[len(inventory),inventory.node_id.nunique(),inventory.sku_id.nunique(),inventory.atp_kg.sum(),inventory.stockout.mean(),inventory.reserved_ratio.mean()]}))
credit = con.execute(f"SELECT * FROM read_parquet('{(DATA/'customer_credit_state.parquet').as_posix()}')").fetchdf()
credit['utilization'] = credit.outstanding_balance_inr / credit.credit_limit_inr.clip(lower=1)
display(pd.DataFrame({'metric':['credit_states','customers','outstanding_inr','blocked_rate','avg_utilization','avg_days_since_payment'],'value':[len(credit),credit.customer_id.nunique(),credit.outstanding_balance_inr.sum(),credit.is_credit_blocked.mean(),credit.utilization.mean(),credit.days_since_last_payment.mean()]}))
supplier = con.execute(f"SELECT * FROM read_parquet('{(DATA/'supplier_material_month_performance.parquet').as_posix()}')").fetchdf()
supplier['acceptance_rate'] = supplier.accepted_quantity_kg / supplier.received_quantity_kg.clip(lower=1)
display(supplier.groupby('supplier_id').agg(received_kg=('received_quantity_kg','sum'),acceptance_rate=('acceptance_rate','mean'),rejection_rate=('rejection_rate','mean'),late_rate=('late_receipt_rate','mean')).sort_values('late_rate',ascending=False).head(20))''')
add('markdown', '## Modeling handoff\n\nUse chronological splits for every future outcome. Compare each model with a business baseline. Report PR-AUC/recall/precision for risk, MAE/RMSE/WAPE for forecasts and cost, and retain the feature cutoff and row grain in every model artifact.')

out = root / 'notebooks' / '00_full_eda_kpi_analysis.ipynb'
out.write_text(json.dumps({'cells': cells, 'metadata': {'kernelspec': {'display_name':'Python 3','language':'python','name':'python3'}}, 'nbformat': 4, 'nbformat_minor': 5}, indent=1), encoding='utf-8')
print(out)
