
import json
from pathlib import Path

import joblib
import pandas as pd
import streamlit as st

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_FILE = BASE_DIR / "data" / "cleaned_orders.csv"
MODEL_FILE = BASE_DIR / "models" / "rto_model.pkl"
RULES_FILE = BASE_DIR / "config" / "rules.json"

st.set_page_config(
    page_title="COD Risk Dashboard",
    page_icon="📦",
    layout="wide"
)


@st.cache_data
def load_data():
    df = pd.read_csv(DATA_FILE)
    df["order_datetime"] = pd.to_datetime(
        df["order_datetime"], errors="coerce"
    )
    return df.dropna(subset=["order_datetime"])


@st.cache_resource
def load_model():
    return joblib.load(MODEL_FILE)


def load_rules():
    with open(RULES_FILE, "r", encoding="utf-8") as file:
        return json.load(file)


def classify_action(row, thresholds, repeat_limit):
    risk = row["predicted_risk"]
    prior_orders = int(row["customer_prior_orders"])
    prior_rto = int(row["customer_prior_rto"])

    if risk < thresholds["ship_as_is"]:
        return "Ship as-is"

    if risk < thresholds["ship_after_confirmation"]:
        return "Ship after confirmation"

    if risk < thresholds["nudge_to_prepaid"]:
        return "Nudge to prepaid"

    if prior_orders == 0:
        return "Nudge to prepaid"

    if prior_rto >= repeat_limit:
        return "Hold for manual review"

    return "Hold for manual review"


st.title("📦 COD Risk Prevention Dashboard")
st.caption("Founder view | Cash on Delivery risk and decision impact")

if not DATA_FILE.exists():
    st.error("Cleaned data not found. Run: python src/data_cleaning.py")
    st.stop()

if not MODEL_FILE.exists():
    st.error("Trained model not found. Run: python src/train_model.py")
    st.stop()

df = load_data()
model = load_model()
rules = load_rules()

features = [
    "order_value",
    "num_items",
    "customer_prior_orders",
    "customer_prior_rto",
    "order_hour",
    "order_month",
    "order_dayofweek",
    "city",
    "state",
    "utm_source",
    "courier"
]

missing = [column for column in features if column not in df.columns]
if missing:
    st.error(f"Missing model features: {missing}")
    st.stop()

thresholds = rules["risk_thresholds"]

df["predicted_risk"] = model.predict_proba(df[features])[:, 1]

df["decision"] = df.apply(
    lambda row: classify_action(
        row, thresholds, rules["repeat_rto_limit"]
    ),
    axis=1
)

st.sidebar.header("Dashboard settings")

available_dates = sorted(df["order_datetime"].dt.date.unique())

selected_date = st.sidebar.date_input(
    "Select order date",
    value=available_dates[-1],
    min_value=available_dates[0],
    max_value=available_dates[-1]
)

st.sidebar.divider()
st.sidebar.subheader("Business assumptions")

rto_cost = st.sidebar.number_input(
    "Estimated cost per RTO (₹)",
    min_value=0.0,
    value=169.40,
    step=5.0
)

prepaid_rto_rate = st.sidebar.slider(
    "Prepaid RTO rate (%)",
    min_value=0.0,
    max_value=20.0,
    value=4.0
) / 100

prepaid_conversion = st.sidebar.slider(
    "Nudge-to-prepaid conversion (%)",
    min_value=0,
    max_value=100,
    value=35
) / 100

discount = st.sidebar.number_input(
    "Prepaid discount (₹)",
    min_value=0.0,
    value=float(rules["prepaid_discount"]),
    step=5.0
)

genuine_cancel_rate = st.sidebar.slider(
    "Estimated genuine customers lost from holds (%)",
    min_value=0,
    max_value=100,
    value=5
) / 100

daily = df[df["order_datetime"].dt.date == selected_date].copy()

if daily.empty:
    st.warning("No orders are available for this date.")
    st.stop()

st.subheader(f"Order summary — {selected_date}")
st.caption(
    "Historical demonstration using the selected date. "
    "Live yesterday data requires a connected order source."
)

total_orders = len(daily)
actual_rto = int(daily["rto"].sum())
actual_delivered = total_orders - actual_rto
actual_rto_rate = actual_rto / total_orders if total_orders else 0

col1, col2, col3, col4 = st.columns(4)

col1.metric("Total orders", total_orders)
col2.metric("Actual RTO", actual_rto)
col3.metric("Delivered", actual_delivered)
col4.metric("Actual RTO rate", f"{actual_rto_rate:.1%}")

st.divider()
st.subheader("Orders by recommended action")

bucket_order = [
    "Ship as-is",
    "Ship after confirmation",
    "Nudge to prepaid",
    "Hold for manual review"
]

bucket_counts = (
    daily["decision"]
    .value_counts()
    .reindex(bucket_order, fill_value=0)
)

bucket_columns = st.columns(4)

for column, action in zip(bucket_columns, bucket_order):
    column.metric(action, int(bucket_counts[action]))

st.bar_chart(bucket_counts)

st.divider()
st.subheader("Estimated business impact")

nudge_orders = int(bucket_counts["Nudge to prepaid"])
hold_orders = int(bucket_counts["Hold for manual review"])

expected_conversions = nudge_orders * prepaid_conversion

rto_rate_difference = max(0, 0.2843 - prepaid_rto_rate)

avoided_rto_cost = (
    expected_conversions * rto_rate_difference * rto_cost
)

discount_cost = expected_conversions * discount

net_prepaid_savings = avoided_rto_cost - discount_cost

estimated_lost_genuine = hold_orders * genuine_cancel_rate

impact1, impact2, impact3 = st.columns(3)

impact1.metric(
    "Expected prepaid conversions",
    f"{expected_conversions:.1f}"
)

impact2.metric(
    "Estimated RTO cost avoided",
    f"₹{avoided_rto_cost:,.0f}"
)

impact3.metric(
    "Estimated net prepaid impact",
    f"₹{net_prepaid_savings:,.0f}"
)

st.metric(
    "Potential genuine customers affected by holds",
    f"{estimated_lost_genuine:.1f}"
)

st.caption(
    "Estimates, not realized savings. The calculation assumes a "
    "28.43% baseline COD RTO rate, the selected prepaid RTO rate, "
    "and the conversion and discount assumptions in the sidebar. "
    "It does not include lost sales, payment fees, or operational costs. "
    "The genuine-customer estimate is an assumption, not an observed count."
)

st.divider()
st.subheader("Order-level decision log")

display_columns = [
    "order_id",
    "order_datetime",
    "order_value",
    "predicted_risk",
    "decision",
    "rto"
]

display_df = daily[display_columns].copy()
display_df["predicted_risk"] = (
    display_df["predicted_risk"] * 100
).round(2)

display_df = display_df.rename(columns={
    "order_id": "Order ID",
    "order_datetime": "Order date",
    "order_value": "Order value (₹)",
    "predicted_risk": "Predicted RTO risk (%)",
    "decision": "Recommended action",
    "rto": "Actual RTO (1 = Yes)"
})

st.dataframe(display_df, use_container_width=True)

st.info(
    "Prototype limitation: this dashboard uses historical completed "
    "orders. A production dashboard should score new COD orders and "
    "update outcomes as delivery results arrive."
)
