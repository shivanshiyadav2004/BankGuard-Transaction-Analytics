import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path

st.set_page_config(page_title="BankGuard | Transaction Analytics", page_icon="🏦", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
<style>
:root { --navy:#142D4E; --canvas:#F3F6FB; }
.stApp { background:var(--canvas); color:#172B4D; }
[data-testid="stHeader"] { background:rgba(243,246,251,.92); }
[data-testid="stAppViewContainer"] > .main .block-container { max-width:1500px; padding-top:2rem; padding-bottom:3rem; }
[data-testid="stSidebar"] { background:linear-gradient(180deg,#142D4E 0%,#1D426B 100%); }
[data-testid="stSidebar"] * { color:#F8FAFC !important; }
[data-testid="stSidebar"] [data-baseweb="select"] > div, [data-testid="stSidebar"] [data-baseweb="input"] > div { background:#FFFFFF !important; border-color:#D7E0EC !important; }
[data-testid="stSidebar"] [data-baseweb="select"] input, [data-testid="stSidebar"] [data-baseweb="input"] input { color:#172B4D !important; }
[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p { color:#E2EAF5 !important; }
.hero { background:linear-gradient(115deg,#142D4E 0%,#245B91 100%); padding:1.65rem 1.9rem; border-radius:18px; margin-bottom:1.35rem; box-shadow:0 8px 24px rgba(20,45,78,.12); }
.hero h1 { color:#FFFFFF !important; margin:0; font-size:2.15rem; }
.hero p { color:#DCEBFA !important; margin:.45rem 0 0 0; font-size:1rem; }
.eyebrow { color:#BFDBFE !important; text-transform:uppercase; letter-spacing:.12em; font-size:.72rem; font-weight:700; margin-bottom:.5rem; }
.section-title { color:#183B63; font-size:1.12rem; font-weight:750; margin:.7rem 0 .8rem 0; }
div[data-testid="stMetric"] { background:#FFFFFF; border:1px solid #E4EAF2; border-radius:15px; padding:1rem 1.1rem; box-shadow:0 3px 12px rgba(25,55,90,.045); }
div[data-testid="stMetricLabel"] p { color:#64748B !important; font-weight:600; }
div[data-testid="stMetricValue"] { color:#173B63 !important; }
div[data-testid="stPlotlyChart"], div[data-testid="stDataFrame"] { background:#FFFFFF; border:1px solid #E4EAF2; border-radius:14px; padding:.45rem; }
.stButton button, .stDownloadButton button { border-radius:9px; font-weight:650; }
hr { border-color:#DFE7F0; }
footer { visibility:hidden; }
</style>
""", unsafe_allow_html=True)

@st.cache_data
def load_data():
    csv_path = Path(__file__).parent / "bank_transactions_synthetic.csv"
    return pd.read_csv(csv_path, parse_dates=["transaction_datetime"])

df = load_data()

with st.sidebar:
    st.markdown("## 🏦 BankGuard")
    st.caption("TRANSACTION INTELLIGENCE")
    st.divider()
    st.markdown("### Dashboard Filters")
    date_min = df["transaction_datetime"].min().date()
    date_max = df["transaction_datetime"].max().date()
    date_range = st.date_input("Transaction date range", value=(date_min, date_max), min_value=date_min, max_value=date_max)
    types = st.multiselect("Transaction type", sorted(df["transaction_type"].unique()), default=sorted(df["transaction_type"].unique()))
    risk = st.multiselect("Risk category", ["Low", "Medium", "High"], default=["Low", "Medium", "High"])
    locations = st.multiselect("Location", sorted(df["location"].unique()), default=sorted(df["location"].unique()))
    st.divider()
    st.caption("Academic prototype • Synthetic data only")

if isinstance(date_range, tuple) and len(date_range) == 2:
    start_date, end_date = date_range
else:
    start_date, end_date = date_min, date_max

filtered = df[
    (df["transaction_datetime"].dt.date >= start_date)
    & (df["transaction_datetime"].dt.date <= end_date)
    & (df["transaction_type"].isin(types))
    & (df["risk_category"].isin(risk))
    & (df["location"].isin(locations))
].copy()

total_txn = len(filtered)
fraud_cases = int(filtered["is_fraud"].sum()) if total_txn else 0
fraud_rate = fraud_cases / total_txn * 100 if total_txn else 0
total_amount = filtered["amount_inr"].sum() if total_txn else 0
high_risk_count = int((filtered["risk_category"] == "High").sum()) if total_txn else 0

st.markdown("""
<div class="hero">
  <div class="eyebrow">FINANCIAL DATA • RISK MONITORING</div>
  <h1>🏦 BankGuard</h1>
  <p>Bank Transaction Analytics &amp; Fraud Risk Detection</p>
</div>
""", unsafe_allow_html=True)
st.caption("Academic demonstration using synthetic data. Risk flags are indicators for review, not proof of fraud.")

st.markdown('<div class="section-title">Executive Overview</div>', unsafe_allow_html=True)
c1, c2, c3, c4 = st.columns(4)
c1.metric("Total Transactions", f"{total_txn:,}")
c2.metric("Transaction Value", f"₹{total_amount:,.0f}")
c3.metric("Synthetic Labelled Cases", f"{fraud_cases:,}", f"{fraud_rate:.2f}% of filtered transactions")
c4.metric("High-Risk Flags", f"{high_risk_count:,}")

plotly_layout = dict(template="plotly_white", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="#FFFFFF", font=dict(family="Arial, sans-serif", color="#334155"), margin=dict(l=20, r=20, t=45, b=20), legend_title_text="")

st.markdown('<div class="section-title">Transaction Insights</div>', unsafe_allow_html=True)
left, right = st.columns(2)
with left:
    if total_txn:
        g = filtered.groupby("transaction_type", as_index=False).size().rename(columns={"size":"transactions"})
        fig = px.bar(g, x="transaction_type", y="transactions", color="transaction_type", title="Transaction Volume by Type", color_discrete_sequence=["#2563EB", "#60A5FA", "#0F766E", "#F59E0B", "#8B5CF6"])
        fig.update_layout(**plotly_layout, showlegend=False, xaxis_title="", yaxis_title="Transactions")
        st.plotly_chart(fig, width="stretch")
    else:
        st.info("No transactions match the selected filters.")
with right:
    if total_txn:
        g = filtered.groupby("risk_category", as_index=False).size().rename(columns={"size":"transactions"})
        fig = px.pie(g, names="risk_category", values="transactions", title="Risk Category Distribution", hole=.58, color="risk_category", color_discrete_map={"Low":"#16A34A", "Medium":"#F59E0B", "High":"#DC2626"})
        fig.update_layout(**plotly_layout)
        fig.update_traces(textposition="inside", textinfo="percent")
        st.plotly_chart(fig, width="stretch")
    else:
        st.info("No transactions match the selected filters.")

left, right = st.columns(2)
with left:
    if total_txn:
        monthly = filtered.assign(month=filtered["transaction_datetime"].dt.to_period("M").astype(str)).groupby("month", as_index=False)["amount_inr"].sum()
        fig = px.line(monthly, x="month", y="amount_inr", markers=True, title="Transaction Value Over Time", labels={"amount_inr":"Value (INR)", "month":"Month"})
        fig.update_traces(line_color="#2563EB", marker_color="#1D4ED8", line_width=3)
        fig.update_layout(**plotly_layout)
        st.plotly_chart(fig, width="stretch")
    else:
        st.info("No transactions match the selected filters.")
with right:
    if total_txn:
        channel_data = filtered.groupby("channel", as_index=False)["is_fraud"].sum().rename(columns={"is_fraud":"labelled_fraud_cases"})
        fig = px.bar(channel_data, x="channel", y="labelled_fraud_cases", title="Synthetic Labelled Cases by Channel", color="channel", color_discrete_sequence=["#2563EB", "#0F766E", "#F59E0B", "#8B5CF6"])
        fig.update_layout(**plotly_layout, showlegend=False, xaxis_title="", yaxis_title="Labelled cases")
        st.plotly_chart(fig, width="stretch")
    else:
        st.info("No transactions match the selected filters.")

st.markdown('<div class="section-title">Transaction Review</div>', unsafe_allow_html=True)
show_cols = ["transaction_id", "transaction_datetime", "customer_id", "transaction_type", "amount_inr", "location", "channel", "device_status", "risk_score", "risk_category", "is_fraud"]
if total_txn:
    view = filtered.sort_values(["risk_score", "amount_inr"], ascending=False)[show_cols]
    with st.expander("Open transaction records", expanded=False):
        st.dataframe(view, width="stretch", hide_index=True)
        csv = view.to_csv(index=False).encode("utf-8")
        st.download_button("Download filtered transactions (CSV)", csv, "bankguard_filtered_transactions.csv", "text/csv")
else:
    st.info("No data to display.")

with st.expander("Methodology & limitations"):
    st.markdown("""
    - Risk score is a transparent, illustrative rule-based score using transaction amount, device status, time of day and transaction type.
    - The is_fraud field is a synthetic teaching label generated for this academic project.
    - A high-risk flag does not establish criminal activity. Real investigations require additional context, customer due diligence and human review.
    - This project is not connected to any real bank or payment network.
    """)
