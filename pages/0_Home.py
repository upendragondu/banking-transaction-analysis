
import pandas as pd
import streamlit as st

from analysis import load_transactions
from dashboard_utils import format_inr, prepare_transactions

st.title("🏦 Banking Transaction Analysis")
st.write(
    "Explore banking transactions, financial summaries, "
    "customer accounts, and analytical reports."
)


@st.cache_data(ttl=30)
def load_dashboard_data():
    data = load_transactions()
    return pd.DataFrame() if data is None else data.copy()


try:
    transactions = prepare_transactions(load_dashboard_data())
except Exception as error:
    st.error("Could not load dashboard data.")
    st.caption("Check that Flask and MySQL are running.")
    st.code(str(error))
    transactions = pd.DataFrame()


st.subheader("📊 Overall Financial Summary")

if transactions.empty:
    st.warning(
        "No transaction data is available. "
        "Check your database connection and Flask backend."
    )
else:
    if "amount" not in transactions.columns:
        transactions["amount"] = 0

    transactions["amount"] = pd.to_numeric(
        transactions["amount"], errors="coerce"
    ).fillna(0)

    if "transaction_type" not in transactions.columns:
        transactions["transaction_type"] = ""

    transaction_types = (
        transactions["transaction_type"]
        .astype(str)
        .str.strip()
        .str.lower()
    )

    deposits = transactions.loc[
        transaction_types == "deposit", "amount"
    ].sum()

    withdrawals = transactions.loc[
        transaction_types == "withdrawal", "amount"
    ].sum()

    average_amount = transactions["amount"].mean()
    largest_amount = transactions["amount"].max()

    if "review_flag" in transactions.columns:
        review_values = (
            transactions["review_flag"]
            .astype(str)
            .str.strip()
            .str.lower()
        )

        flagged_count = int(
            review_values.isin(["review", "flagged", "true", "yes", "1"]).sum()
        )
    else:
        flagged_count = 0

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Total Transactions", f"{len(transactions):,}")
    col2.metric("Total Deposits", format_inr(deposits))
    col3.metric("Total Withdrawals", format_inr(withdrawals))
    col4.metric(
        "Net Transaction Flow",
        format_inr(deposits - withdrawals),
    )

    col5, col6, col7 = st.columns(3)

    col5.metric("Average Transaction", format_inr(average_amount))
    col6.metric("Largest Transaction", format_inr(largest_amount))
    col7.metric("Flagged for Review", f"{flagged_count:,}")

    st.divider()

    chart1, chart2 = st.columns(2)

    with chart1:
        st.subheader("Deposits vs Withdrawals")
        st.bar_chart(
            pd.Series(
                {
                    "Deposits": deposits,
                    "Withdrawals": withdrawals,
                }
            )
        )

    with chart2:
        st.subheader("Transaction Types")
        st.bar_chart(transactions["transaction_type"].value_counts())


st.divider()
st.header("🚀 Explore Banking Features")
st.write("Choose a section to open its separate page.")

col1, col2 = st.columns(2, gap="large")

with col1:
    with st.container(border=True):
        st.subheader("👥 Customer Management")
        st.write("Search customers and view transaction histories.")

        if st.button("Open Customer Management →", use_container_width=True):
            st.switch_page("pages/1_Customer_Management.py")

with col2:
    with st.container(border=True):
        st.subheader("🏦 Account Management")
        st.write("Browse bank accounts and review account balances.")

        if st.button("Open Account Management →", use_container_width=True):
            st.switch_page("pages/2_Account_Management.py")

col3, col4 = st.columns(2, gap="large")

with col3:
    with st.container(border=True):
        st.subheader("💳 Transactions")
        st.write("Review, filter, record, and export transactions.")

        if st.button("Open Transactions →", use_container_width=True):
            st.switch_page("pages/3_Transactions.py")

with col4:
    with st.container(border=True):
        st.subheader("📈 Analytics & Reports")
        st.write("Explore monthly trends and financial reports.")

        if st.button("Open Analytics & Reports →", use_container_width=True):
            st.switch_page("pages/4_Analytics_Reports.py")

st.divider()
st.caption(
    "Banking Transaction Analysis | Python · Streamlit · Pandas · MySQL"
)
