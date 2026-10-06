"""
app.py

Purpose: A Streamlit dashboard that reads from our DuckDB marts and displays
the pipeline's output visually -- overview metrics, monthly trends, category
breakdowns, customer segments, and flagged spending anomalies.

Run this from the project root folder with:
    streamlit run dashboard/app.py
"""

import duckdb
import pandas as pd
import streamlit as st
from pathlib import Path

# ---- Setup -------------------------------------------------------------
PROJECT_ROOT = Path(__file__).parent.parent
DB_PATH = PROJECT_ROOT / "scripts" / "bank_transactions.duckdb"

st.set_page_config(page_title="Bank Transaction Analytics", layout="wide")

st.title("Bank Transaction Analytics Dashboard")
st.caption("Built on a dbt + DuckDB + Prefect pipeline")


# ---- Data loading --------------------------------------------------------
@st.cache_data
def load_data():
    con = duckdb.connect(str(DB_PATH), read_only=True)

    dim_customers = con.execute("select * from main.dim_customers").df()
    fct_category_summary = con.execute("select * from main.fct_category_summary").df()
    fct_monthly_trends = con.execute("select * from main.fct_monthly_trends").df()
    fct_spending_anomalies = con.execute("select * from main.fct_spending_anomalies").df()

    con.close()

    return dim_customers, fct_category_summary, fct_monthly_trends, fct_spending_anomalies


dim_customers, fct_category_summary, fct_monthly_trends, fct_spending_anomalies = load_data()


# ---- Overview metrics ------------------------------------------------------
total_customers = len(dim_customers)
total_transactions = int(fct_category_summary["total_transactions"].sum())
total_amount = fct_category_summary["total_amount"].sum()
total_anomalies = len(fct_spending_anomalies)

col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Customers", f"{total_customers:,}")
col2.metric("Total Transactions", f"{total_transactions:,}")
col3.metric("Total Amount", f"${total_amount:,.2f}")
col4.metric("Flagged Anomalies", f"{total_anomalies:,}")

st.divider()


# ---- Monthly trends ------------------------------------------------------
st.subheader("Monthly Transaction Trends")
st.line_chart(
    fct_monthly_trends.set_index("transaction_month")[["total_amount"]]
)

st.divider()


# ---- Category breakdown ------------------------------------------------------
st.subheader("Spending by Transaction Type and Channel")
col1, col2 = st.columns(2)

with col1:
    st.bar_chart(
        fct_category_summary.groupby("transaction_type")["total_amount"].sum()
    )

with col2:
    st.bar_chart(
        fct_category_summary.groupby("channel")["total_amount"].sum()
    )

st.divider()


# ---- Customer segments ------------------------------------------------------
st.subheader("Customers by Age Group")
age_group_counts = dim_customers["age_group"].value_counts()
st.bar_chart(age_group_counts)

st.divider()


# ---- Flagged anomalies ------------------------------------------------------
st.subheader("Flagged Spending Anomalies")
st.caption("Transactions more than 2 standard deviations above that customer's own average")
st.dataframe(
    fct_spending_anomalies[
        ["transaction_id", "account_id", "transaction_amount", "transaction_date", "z_score"]
    ].sort_values("z_score", ascending=False),
    width="stretch"
)