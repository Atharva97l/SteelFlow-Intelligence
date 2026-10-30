from pathlib import Path
import json
import joblib
import pandas as pd
import streamlit as st

ROOT = Path(__file__).parent
MODEL_DIR = ROOT / "artifacts" / "models"
KPI_DIR = ROOT / "artifacts" / "kpis"

st.set_page_config(page_title="SteelFlow Operations", page_icon="🏭", layout="wide", initial_sidebar_state="expanded")
st.markdown("""
<style>
.block-container {padding-top: 2rem; padding-bottom: 3rem; max-width: 1400px;}
.hero {padding: 1.25rem 1.5rem; border-radius: 16px; background: linear-gradient(120deg,#12355b,#1f6f8b); color: white; margin-bottom: 1.25rem;}
.hero h1 {margin: 0; font-size: 2.3rem;} .hero p {margin: .4rem 0 0; opacity: .9;}
[data-testid="stMetricValue"] {font-size: 1.5rem;}
</style>
""", unsafe_allow_html=True)

def load_model(name):
    path = MODEL_DIR / name
    return joblib.load(path) if path.exists() else None

def required_columns(model):
    return list(model.named_steps["pre"].feature_names_in_)

def input_frame(model, task):
    cols = required_columns(model)
    row = {c: 0 for c in cols}
    defaults = {
        "Late delivery": {"carrier_id":"CARRIER_001","route_id":"ROUTE_001","route_type":"REGIONAL","booking_type":"CONTRACT","distance_km":250.0,"shipment_weight_kg":10000,"vehicle_capacity_kg":20000,"load_utilization":0.5,"over_capacity":False,"spot_surcharge_multiplier":1.0,"expected_booking_cost_inr":7000.0,"quoted_freight_cost_inr":7500.0,"route_congestion_index_0_1":0.3,"route_difficulty_index":0.3,"rain_forecast_severity_0_1":0.1,"known_disruption_severity_0_1":0.0,"capacity_pressure_0_1":0.3,"is_monsoon_season":False,"carrier_event_active":False,"carrier_event_severity_0_1":0.0,"carrier_base_delay_risk":0.2,"carrier_historical_late_rate_90d":0.2,"carrier_historical_shipments_90d":20,"carrier_route_historical_late_rate_90d":0.2,"carrier_route_historical_shipments_90d":10},
        "Freight cost": {"booking_type":"CONTRACT","spot_surcharge_multiplier":1.0,"expected_booking_cost_inr":7000.0,"quoted_freight_cost_inr":7500.0,"carrier_id":"CARRIER_001","route_id":"ROUTE_001","route_type":"REGIONAL","distance_km":250.0,"shipment_weight_kg":10000,"vehicle_capacity_kg":20000,"route_congestion_index_0_1":0.3,"route_difficulty_index":0.3,"rain_forecast_severity_0_1":0.1,"known_disruption_severity_0_1":0.0,"capacity_pressure_0_1":0.3,"is_monsoon_season":False,"carrier_base_delay_risk":0.2},
        "Credit default": {"outstanding_balance_inr":50000.0,"credit_limit_inr":200000.0,"available_credit_inr":150000.0,"is_credit_blocked":False,"payment_terms_days":30,"days_since_last_payment":20,"credit_utilization":0.25},
        "Inventory stockout": {"node_id":"NODE_001","sku_id":"SKU_001","node_type":"WAREHOUSE","quantity_kg":10000.0,"open_reserved_quantity_kg":2500.0},
        "Supplier late receipt": {"supplier_id":"SUPPLIER_001","material_id":"MAT_001","receipt_lot_count":10,"po_line_count":12,"received_quantity_kg":100000.0,"accepted_quantity_kg":98000.0,"rejected_quantity_kg":2000.0,"rejection_rate":0.02},
        "Customer churn (90-day)": {"order_count":5,"revenue":500000.0,"weight_kg":25000.0,"avg_order_value":100000.0,"avg_payment_delay":15.0,"recency_at_snapshot":30},
    }
    if task.startswith("Demand"):
        defaults[task] = {"demand_centre_id":"CENTRE_001","demand_centre_region":"NORTH","sku_id":"SKU_001","product_family":"STRUCTURAL","horizon_days":int(task.split("-")[0].split("(")[-1]),"seasonal_naive_lag_kg":1000,"seasonal_lag_available":1,"origin_weekday":1,"target_weekday":1,"target_month":6,"target_is_monsoon":True,"lag_1d_demand_kg":1000,"lag_1d_available":1,"lag_7d_demand_kg":1000,"lag_7d_available":1,"lag_14d_demand_kg":1000,"lag_14d_available":1,"lag_28d_demand_kg":1000,"lag_28d_available":1,"trailing_7d_mean_demand_kg":1000,"trailing_7d_median_demand_kg":1000,"trailing_7d_std_demand_kg":100,"trailing_7d_sample_days":7,"trailing_14d_mean_demand_kg":1000,"trailing_14d_median_demand_kg":1000,"trailing_14d_std_demand_kg":100,"trailing_14d_sample_days":14,"trailing_28d_mean_demand_kg":1000,"trailing_28d_median_demand_kg":1000,"trailing_28d_std_demand_kg":100,"trailing_28d_sample_days":28}
    row.update({k:v for k,v in defaults.get(task, {}).items() if k in row})
    return pd.DataFrame([row], columns=cols)

def load_kpis():
    names = ["carrier_kpis.csv", "route_kpis.csv", "customer_kpis.csv", "supplier_material_kpis.csv"]
    return [pd.read_csv(KPI_DIR / n) if (KPI_DIR / n).exists() else pd.DataFrame() for n in names]

@st.cache_data(show_spinner=False)
def value_options(task, column):
    source = {
        "Late delivery": "dispatch_delay_model_dataset.parquet",
        "Freight cost": "freight_cost_model_dataset.parquet",
        "Inventory stockout": "finished_goods_inventory_snapshots.parquet",
        "Supplier late receipt": "supplier_material_month_performance.parquet",
        "Customer churn (90-day)": "customer_orders.parquet",
    }.get(task, "forecast_features_horizon_07.parquet")
    path = ROOT / "data" / source
    try:
        values = pd.read_parquet(path, columns=[column])[column].dropna().drop_duplicates().tolist()
        return sorted(values, key=str)[:250]
    except Exception:
        return []

def render_inputs(model, task):
    defaults = input_frame(model, task).iloc[0].to_dict()
    values = {}
    columns = list(defaults)
    for start in range(0, len(columns), 3):
        group = st.columns(3)
        for slot, column in zip(group, columns[start:start + 3]):
            default = defaults[column]
            with slot:
                if isinstance(default, bool):
                    values[column] = st.checkbox(column.replace('_', ' ').title(), value=default, key=f"{task}_{column}")
                elif isinstance(default, str):
                    options = value_options(task, column)
                    if default not in options:
                        options = [default] + options
                    values[column] = st.selectbox(column.replace('_', ' ').title(), options, key=f"{task}_{column}")
                else:
                    values[column] = st.number_input(column.replace('_', ' ').title(), value=float(default), key=f"{task}_{column}")
    return pd.DataFrame([values], columns=columns)

st.markdown('<div class="hero"><h1>SteelFlow Operations</h1><p>Forecast demand, predict operational risk, and monitor the supply chain from one workspace.</p></div>', unsafe_allow_html=True)
dashboard, predictor, performance = st.tabs(["📊 KPI dashboard", "🔮 Predictions", "📈 Model performance"])
carrier, route, customer, supplier = load_kpis()

with dashboard:
    st.subheader("Operational overview")
    c1,c2,c3,c4 = st.columns(4)
    c1.metric("Carriers tracked", f"{len(carrier):,}"); c2.metric("Routes tracked", f"{len(route):,}"); c3.metric("Customers tracked", f"{len(customer):,}"); c4.metric("Supplier-material rows", f"{len(supplier):,}")
    left, right = st.columns(2)
    with left:
        st.markdown("#### Carrier service risk")
        if not carrier.empty: st.dataframe(carrier.sort_values("late_rate", ascending=False).head(10), use_container_width=True, hide_index=True)
    with right:
        st.markdown("#### Route service risk")
        if not route.empty: st.dataframe(route.sort_values("late_rate", ascending=False).head(10), use_container_width=True, hide_index=True)
    st.markdown("#### Customer value and supplier performance")
    a,b = st.columns(2)
    with a:
        if not customer.empty: st.dataframe(customer.sort_values("revenue_ex_gst", ascending=False).head(10), use_container_width=True, hide_index=True)
    with b:
        if not supplier.empty: st.dataframe(supplier.head(10), use_container_width=True, hide_index=True)

tasks = ["Late delivery", "Freight cost", "Demand (7-day)", "Demand (14-day)", "Demand (30-day)", "Credit default", "Inventory stockout", "Supplier late receipt", "Customer churn (90-day)"]
model_names = {"Late delivery":"late_delivery_best.joblib", "Freight cost":"freight_cost_best.joblib", "Demand (7-day)":"demand_horizon_07_best.joblib", "Demand (14-day)":"demand_horizon_14_best.joblib", "Demand (30-day)":"demand_horizon_30_best.joblib", "Credit default":"credit_default_best.joblib", "Inventory stockout":"inventory_stockout_best.joblib", "Supplier late receipt":"supplier_late_receipt_best.joblib", "Customer churn (90-day)":"customer_churn_90d_best.joblib"}
with predictor:
    task = st.selectbox("Choose a prediction", tasks)
    model = load_model(model_names[task])
    if model is None:
        st.error("This model artifact is missing. Run the training script first.")
    else:
        st.caption("Edit the scenario values, then run the selected model.")
        edited = render_inputs(model, task)
        if st.button("Run prediction", type="primary"):
            if task == "Late delivery":
                probability = float(model.predict_proba(edited)[:,1][0]); threshold_file = MODEL_DIR / "late_delivery_threshold.json"; threshold = json.loads(threshold_file.read_text()).get("threshold", 0.5) if threshold_file.exists() else 0.5
                outcome = pd.read_parquet(ROOT / "data" / "outbound_shipments.parquet", columns=["is_late","delay_hours_vs_promised"]); late_rows = outcome[outcome.is_late]; delay_base = float(late_rows.delay_hours_vs_promised.clip(lower=0).mean()) if not late_rows.empty else 0.0
                estimated_days = probability * delay_base / 24
                x,y,z = st.columns(3); x.metric("Late probability", f"{probability:.1%}"); y.metric("Estimated delay", f"{estimated_days:.1f} days"); z.metric("Decision", "Alert" if probability >= threshold else "No alert")
                st.progress(min(max(probability,0.0),1.0)); st.caption(f"Alert threshold: {threshold:.2f}. Delay is estimated from historical late-shipment delay hours.")
            elif task == "Freight cost": st.metric("Estimated freight cost", f"₹{float(model.predict(edited)[0]):,.0f}")
            elif task.startswith("Demand"): st.metric("Forecast demand", f"{max(float(model.predict(edited)[0]),0):,.0f} kg")
            else:
                probability = float(model.predict_proba(edited)[:,1][0]); st.metric("Risk probability", f"{probability:.1%}"); st.progress(min(max(probability,0.0),1.0))

with performance:
    st.subheader("Validated model performance")
    for filename in ["model_metrics.csv","demand_model_metrics.csv","inventory_supplier_holdout_metrics.csv","customer_churn_metrics.csv"]:
        path = MODEL_DIR / filename
        if path.exists():
            st.markdown(f"#### {filename.replace('_',' ').replace('.csv','').title()}")
            st.dataframe(pd.read_csv(path), use_container_width=True, hide_index=True)

st.divider(); st.caption("SteelFlow models use time-aware splits and saved preprocessing pipelines. Risk outputs support operational decisions and should be monitored after deployment.")
