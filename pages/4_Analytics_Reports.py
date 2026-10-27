import pandas as pd
import streamlit as st
from analysis import account_wise_summary, monthly_transaction_summary
from dashboard_utils import format_inr, get_transaction_data, prepare_transactions
if st.button("← Home"):
    st.switch_page("pages/0_Home.py")
st.set_page_config(page_title="Analytics & Reports", page_icon="📊", layout="wide")
st.title("📊 Analytics & Reports")
st.write("Explore account-wise summaries, monthly trends, and transactions flagged for review.")
try:
    df = prepare_transactions(get_transaction_data())
except Exception as error:
    st.error("Unable to load transaction data from MySQL.")
    st.caption(str(error))
    st.stop()

if df.empty:
    st.info("No transaction records are available for analytics yet.")
    st.stop()

if "amount" in df.columns and "transaction_type" in df.columns:
    deposits = df.loc[df["transaction_type"] == "Deposit", "amount"].sum()
    withdrawals = df.loc[df["transaction_type"] == "Withdrawal", "amount"].sum()
    a, b, c, d = st.columns(4)
    a.metric("Transactions", f"{len(df):,}")
    b.metric("Total Deposits", format_inr(deposits))
    c.metric("Total Withdrawals", format_inr(withdrawals))
    d.metric("Net Flow", format_inr(deposits - withdrawals))

st.divider()
st.subheader("Account-Wise Summary")
try:
    account_report = account_wise_summary(df)
    if account_report is None or account_report.empty:
        st.info("No account-wise report data available.")
    else:
        st.dataframe(account_report, use_container_width=True, hide_index=True)
        st.download_button("📥 Download Account-Wise Report (CSV)", account_report.to_csv(index=False).encode("utf-8"), file_name="account_wise_summary.csv", mime="text/csv", key="download_account_report")
except Exception as error:
    st.error("Could not create the account-wise report.")
    st.caption(str(error))

st.divider()
st.subheader("Monthly Transaction Report")
try:
    monthly_report = monthly_transaction_summary(df)
    if monthly_report is None or monthly_report.empty:
        st.info("No monthly report data available.")
    else:
        st.dataframe(monthly_report, use_container_width=True, hide_index=True)
        st.download_button("📥 Download Monthly Report (CSV)", monthly_report.to_csv(index=False).encode("utf-8"), file_name="monthly_transaction_summary.csv", mime="text/csv", key="download_monthly_report")
        if {"month", "total_deposits", "total_withdrawals"}.issubset(monthly_report.columns):
            st.subheader("Monthly Deposits vs Withdrawals")
            chart = monthly_report.set_index("month")[["total_deposits", "total_withdrawals"]]
            st.bar_chart(chart)
except Exception as error:
    st.error("Could not create the monthly report.")
    st.caption(str(error))

st.divider()
st.subheader("Transactions Flagged for Review")
if "review_flag" in df.columns:
    flagged = df[df["review_flag"] == "Review"].copy()
    st.caption("A review flag is a simple statistical indicator, not proof of fraud.")
    if flagged.empty:
        st.success("No transactions meet the current review threshold.")
    else:
        cols = [c for c in ["transaction_id", "display_name", "account_type", "transaction_date", "transaction_type", "amount", "description", "review_flag"] if c in flagged.columns]
        st.dataframe(flagged[cols].sort_values("amount", ascending=False), use_container_width=True, hide_index=True)
        st.download_button("📥 Download review list (CSV)", flagged[cols].to_csv(index=False).encode("utf-8"), file_name="transactions_for_review.csv", mime="text/csv")
else:
    st.info("Review flags could not be calculated because the amount column is unavailable.")
