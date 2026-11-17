import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path

st.set_page_config(page_title="BankGuard | Transaction Analytics", page_icon="🏦", layout="wide")


@st.cache_data
def load_data():
    path = Path(__file__).parent / "bank_transactions_synthetic.csv"
    data = pd.read_csv(path, parse_dates=["transaction_datetime"])
    return data


df = load_data()
st.title("🏦 BankGuard")
st.subheader("Bank Transaction Analytics & Fraud Risk Detection")
st.caption("Academic demonstration using synthetic data. Risk flags are indicators for review, not proof of fraud.")

with st.sidebar:
    st.header("Dashboard Filters")
    date_min = df["transaction_datetime"].min().date()
    date_max = df["transaction_datetime"].max().date()
    date_range = st.date_input("Transaction date range", value=(date_min, date_max), min_value=date_min, max_value=date_max)
    types = st.multiselect("Transaction type", sorted(df["transaction_type"].unique()), default=sorted(df["transaction_type"].unique()))
    risk = st.multiselect("Risk category", ["Low","Medium","High"], default=["Low","Medium","High"])
    locations = st.multiselect("Location", sorted(df["location"].unique()), default=sorted(df["location"].unique()))

if isinstance(date_range, tuple) and len(date_range) == 2:
    start_date, end_date = date_range
else:
    start_date, end_date = date_min, date_max

filtered = df[
    (df["transaction_datetime"].dt.date >= start_date) &
    (df["transaction_datetime"].dt.date <= end_date) &
    (df["transaction_type"].isin(types)) &
    (df["risk_category"].isin(risk)) &
    (df["location"].isin(locations))
].copy()

total_txn = len(filtered)
fraud_cases = int(filtered["is_fraud"].sum()) if total_txn else 0
fraud_rate = (fraud_cases / total_txn * 100) if total_txn else 0
total_amount = filtered["amount_inr"].sum() if total_txn else 0
high_risk_count = int((filtered["risk_category"] == "High").sum()) if total_txn else 0

c1,c2,c3,c4 = st.columns(4)
c1.metric("Transactions", f"{total_txn:,}")
c2.metric("Transaction Value", f"₹{total_amount:,.0f}")
c3.metric("Labelled Fraud Cases", f"{fraud_cases:,}", f"{fraud_rate:.2f}% of filtered transactions")
c4.metric("High-Risk Flags", f"{high_risk_count:,}")

st.divider()
left, right = st.columns(2)
with left:
    st.markdown("### Transaction Volume by Type")
    if total_txn:
        g = filtered.groupby("transaction_type", as_index=False).size().rename(columns={"size":"transactions"})
        fig = px.bar(g, x="transaction_type", y="transactions", color="transaction_type", title=None)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No transactions match the selected filters.")
with right:
    st.markdown("### Risk Category Distribution")
    if total_txn:
        g = filtered.groupby("risk_category", as_index=False).size().rename(columns={"size":"transactions"})
        fig = px.pie(g, names="risk_category", values="transactions", hole=.45)
        st.plotly_chart(fig, use_container_width=True)

left, right = st.columns(2)
with left:
    st.markdown("### Transaction Value Over Time")
    if total_txn:
        g = filtered.assign(month=filtered["transaction_datetime"].dt.to_period("M").astype(str)).groupby("month", as_index=False)["amount_inr"].sum()
        fig = px.line(g, x="month", y="amount_inr", markers=True, labels={"amount_inr":"Value (INR)","month":"Month"})
        st.plotly_chart(fig, use_container_width=True)
with right:
    st.markdown("### Labelled Fraud Cases by Channel")
    if total_txn:
        g = filtered.groupby("channel", as_index=False)["is_fraud"].sum().rename(columns={"is_fraud":"labelled_fraud_cases"})
        fig = px.bar(g, x="channel", y="labelled_fraud_cases", color="channel")
        st.plotly_chart(fig, use_container_width=True)

st.markdown("### Transaction Review Table")
show_cols = ["transaction_id","transaction_datetime","customer_id","transaction_type","amount_inr","location","channel","device_status","risk_score","risk_category","is_fraud"]
if total_txn:
    view = filtered.sort_values(["risk_score","amount_inr"], ascending=False)[show_cols]
    st.dataframe(view, use_container_width=True, hide_index=True)
    csv = view.to_csv(index=False).encode("utf-8")
    st.download_button("Download filtered transactions (CSV)", csv, "bankguard_filtered_transactions.csv", "text/csv")
else:
    st.info("No data to display.")

st.markdown("### Methodology & Limitations")
st.write("""
- Risk score is a transparent, illustrative rule-based score using transaction amount, device status, time of day and transaction type.
- The `is_fraud` field is a synthetic teaching label generated for this academic project.
- A high-risk flag does not establish criminal activity. Real investigations require additional context, customer due diligence and human review.
- This project is not connected to any real bank or payment network.
""")
