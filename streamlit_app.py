
import streamlit as st
import pandas as pd

from analysis import (
    load_transactions,
    account_wise_summary,
    monthly_transaction_summary,
)


# ---------------- PAGE CONFIGURATION ----------------
st.set_page_config(
    page_title="Banking Transaction Analytics",
    page_icon="🏦",
    layout="wide"
)


# ---------------- HELPER FUNCTIONS ----------------
def format_inr(value):
    return f"₹{value:,.2f}"


# ---------------- LOAD DATA ----------------
@st.cache_data(ttl=30)
def get_transaction_data():
    return load_transactions()


# ---------------- SIDEBAR ----------------
st.sidebar.title("🏦 Banking Analytics")
st.sidebar.caption("Educational simulation")
st.sidebar.info(
    "This dashboard uses synthetic transaction data. "
    "It is not a real banking system."
)

if st.sidebar.button("🔄 Refresh data"):
    get_transaction_data.clear()


# ---------------- MAIN DASHBOARD ----------------
st.title("Banking Transaction Analysis")
st.write(
    "Explore transaction activity, financial summaries, "
    "and transactions flagged for review."
)

try:
    df = get_transaction_data()

except Exception as error:
    st.error("Unable to load transaction data from MySQL.")
    st.code(str(error))
    st.info(
        "Check your MySQL server, .env settings, "
        "and database connection."
    )
    st.stop()


if df.empty:
    st.warning("No transaction records found in the database.")
    st.stop()


# ---------------- DATA PREPARATION ----------------
df["amount"] = pd.to_numeric(df["amount"])
df["transaction_date"] = pd.to_datetime(df["transaction_date"])

deposits = df.loc[
    df["transaction_type"] == "Deposit", "amount"
]

withdrawals = df.loc[
    df["transaction_type"] == "Withdrawal", "amount"
]

total_deposits = deposits.sum()
total_withdrawals = withdrawals.sum()
net_flow = total_deposits - total_withdrawals
average_amount = df["amount"].mean()


# Flag large amounts for review using the same
# educational rule as the analysis module.
q1 = df["amount"].quantile(0.25)
q3 = df["amount"].quantile(0.75)
iqr = q3 - q1

review_threshold = max(20000.0, q3 + 1.5 * iqr)

df["review_flag"] = df["amount"].apply(
    lambda amount: (
        "Review" if amount >= review_threshold else "Normal"
    )
)


# ---------------- FILTERS ----------------
st.sidebar.subheader("Filter transactions")

transaction_types = st.sidebar.multiselect(
    "Transaction type",
    options=sorted(df["transaction_type"].unique()),
    default=sorted(df["transaction_type"].unique())
)

customers = st.sidebar.multiselect(
    "Customer",
    options=sorted(df["display_name"].unique()),
    default=sorted(df["display_name"].unique())
)

min_date = df["transaction_date"].min().date()
max_date = df["transaction_date"].max().date()

date_range = st.sidebar.date_input(
    "Transaction date range",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date
)

filtered_df = df[
    df["transaction_type"].isin(transaction_types)
    & df["display_name"].isin(customers)
].copy()

if len(date_range) == 2:
    start_date, end_date = date_range

    filtered_df = filtered_df[
        filtered_df["transaction_date"].dt.date.between(
            start_date, end_date
        )
    ]


# ---------------- SUMMARY METRICS ----------------
st.subheader("Overall Financial Summary")

col1, col2, col3, col4 = st.columns(4)

col1.metric(
    "Total Transactions",
    f"{len(df):,}"
)

col2.metric(
    "Total Deposits",
    format_inr(total_deposits)
)

col3.metric(
    "Total Withdrawals",
    format_inr(total_withdrawals)
)

col4.metric(
    "Net Transaction Flow",
    format_inr(net_flow)
)

col5, col6, col7 = st.columns(3)

col5.metric(
    "Average Transaction",
    format_inr(average_amount)
)

col6.metric(
    "Largest Transaction",
    format_inr(df["amount"].max())
)

col7.metric(
    "Flagged for Review",
    f"{(df['review_flag'] == 'Review').sum():,}"
)


# ---------------- FILTERED RESULTS ----------------
st.divider()
st.subheader("Filtered Transaction Analysis")

st.caption(
    f"Showing {len(filtered_df)} of {len(df)} transactions "
    "based on your selected filters."
)

if filtered_df.empty:
    st.warning("No transactions match the selected filters.")

else:
    # Charts based on filtered transactions
    chart_col1, chart_col2 = st.columns(2)

    with chart_col1:
        st.markdown("#### Deposits vs Withdrawals")

        totals = (
            filtered_df
            .groupby("transaction_type")["amount"]
            .sum()
        )

        st.bar_chart(totals)

    with chart_col2:
        st.markdown("#### Transaction Counts")

        counts = (
            filtered_df["transaction_type"]
            .value_counts()
            .rename_axis("Transaction Type")
            .to_frame("Count")
        )

        st.bar_chart(counts)

    st.markdown("#### Transaction Amounts Over Time")

    daily_totals = (
        filtered_df
        .assign(
            transaction_day=filtered_df["transaction_date"].dt.date
        )
        .groupby(["transaction_day", "transaction_type"])["amount"]
        .sum()
        .unstack(fill_value=0)
        .sort_index()
    )

    st.line_chart(daily_totals)

    # ---------------- TRANSACTION TABLE ----------------
    st.divider()
    st.subheader("Transaction Records")

    show_reviews_only = st.checkbox(
        "Show only transactions flagged for review"
    )

    display_df = filtered_df.copy()

    if show_reviews_only:
        display_df = display_df[
            display_df["review_flag"] == "Review"
        ]

    display_df = display_df.sort_values(
        "transaction_date",
        ascending=False
    )

    display_columns = [
        "transaction_id",
        "display_name",
        "account_type",
        "transaction_date",
        "transaction_type",
        "amount",
        "description",
        "review_flag"
    ]

    st.dataframe(
        display_df[display_columns],
        use_container_width=True,
        hide_index=True
    )

    # ---------------- DOWNLOAD ----------------
    csv_data = display_df[display_columns].to_csv(index=False).encode(
        "utf-8"
    )

    st.download_button(
        label="📥 Download displayed transactions as CSV",
        data=csv_data,
        file_name="banking_transactions.csv",
        mime="text/csv"
    )

    # ==========================================
    # ACCOUNT-WISE AND MONTHLY REPORTS
    # ==========================================

    st.header("Account-Wise Summary")

    account_report = account_wise_summary(df)

    if account_report.empty:
        st.info("No transaction data available for account-wise analysis.")
    else:
        st.dataframe(account_report, use_container_width=True)

        st.download_button(
            label="Download Account-Wise Report (CSV)",
            data=account_report.to_csv(index=False).encode("utf-8"),
            file_name="account_wise_summary.csv",
            mime="text/csv",
            key="download_account_report",
        )

    st.header("Monthly Transaction Report")

    monthly_report = monthly_transaction_summary(df)

    if monthly_report.empty:
        st.info("No transaction data available for monthly analysis.")
    else:
        st.dataframe(monthly_report, use_container_width=True)

        st.download_button(
            label="Download Monthly Report (CSV)",
            data=monthly_report.to_csv(index=False).encode("utf-8"),
            file_name="monthly_transaction_summary.csv",
            mime="text/csv",
            key="download_monthly_report",
        )

        st.subheader("Monthly Deposits vs Withdrawals")

        monthly_chart_data = monthly_report.set_index("month")[
            ["total_deposits", "total_withdrawals"]
        ]

        st.bar_chart(monthly_chart_data)

# ---------------- FOOTER ----------------
st.divider()
st.caption(
    "Banking Transaction Analysis System | "
    "Python · Streamlit · Pandas · NumPy · MySQL"
)
st.caption(
    "Review flags identify transactions meeting a simple "
    "statistical threshold. They do not establish fraud."
)
