
import pandas as pd
import numpy as np

from database import get_connection


def load_transactions():
    """Load transaction records from MySQL into a Pandas DataFrame."""

    connection = None
    cursor = None

    try:
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)

        cursor.execute("""
            SELECT
                t.transaction_id,
                t.account_id,
                c.display_name,
                a.account_type,
                t.transaction_date,
                t.transaction_type,
                t.amount,
                t.description
            FROM transactions AS t
            JOIN accounts AS a
                ON t.account_id = a.account_id
            JOIN customers AS c
                ON a.customer_id = c.customer_id
            ORDER BY t.transaction_date
        """)

        records = cursor.fetchall()
        df = pd.DataFrame(records)

        if not df.empty:
            df["amount"] = pd.to_numeric(df["amount"])
            df["transaction_date"] = pd.to_datetime(
                df["transaction_date"]
            )

        return df

    finally:
        if cursor is not None:
            cursor.close()

        if connection is not None and connection.is_connected():
            connection.close()


def analyze_transactions(df):
    """Calculate transaction summaries and flag large amounts for review."""

    if df.empty:
        print("No transaction records found.")
        return

    deposits = df.loc[
        df["transaction_type"] == "Deposit", "amount"
    ]

    withdrawals = df.loc[
        df["transaction_type"] == "Withdrawal", "amount"
    ]

    total_deposits = deposits.sum()
    total_withdrawals = withdrawals.sum()
    net_flow = total_deposits - total_withdrawals

    print("\n========== TRANSACTION ANALYSIS ==========")

    print(f"Total transactions : {len(df)}")
    print(f"Total deposits     : ₹{total_deposits:,.2f}")
    print(f"Total withdrawals  : ₹{total_withdrawals:,.2f}")
    print(f"Net transaction flow: ₹{net_flow:,.2f}")

    print(f"\nAverage amount     : ₹{df['amount'].mean():,.2f}")
    print(f"Minimum amount     : ₹{df['amount'].min():,.2f}")
    print(f"Maximum amount     : ₹{df['amount'].max():,.2f}")

    print("\nTransaction counts:")
    print(df["transaction_type"].value_counts().to_string())

    print("\n========== REVIEW FLAGS ==========")

    # Calculate an outlier threshold using the IQR method.
    q1 = df["amount"].quantile(0.25)
    q3 = df["amount"].quantile(0.75)
    iqr = q3 - q1

    statistical_threshold = q3 + 1.5 * iqr

    # Also flag transactions of ₹20,000 or more for this demo.
    threshold = max(20000.0, statistical_threshold)

    df["review_flag"] = np.where(
        df["amount"] >= threshold,
        "Review",
        "Normal"
    )

    flagged = df[df["review_flag"] == "Review"]

    print(f"Review threshold: ₹{threshold:,.2f}")
    print(f"Transactions flagged: {len(flagged)}")

    if flagged.empty:
        print("No transactions flagged for review.")
    else:
        print(
            flagged[
                [
                    "transaction_id",
                    "display_name",
                    "transaction_type",
                    "amount",
                    "review_flag"
                ]
            ].to_string(index=False)
        )

    print("\nAnalysis completed.")

def account_wise_summary(df):
    """Summarize deposits, withdrawals, and net flow for each account."""
    columns = [
        "account_id",
        "display_name",
        "account_type",
        "total_deposits",
        "total_withdrawals",
        "net_flow",
        "transaction_count",
    ]

    if df.empty:
        return pd.DataFrame(columns=columns)

    # Separate deposit and withdrawal amounts
    work = df.copy()
    work["deposit_amount"] = np.where(
        work["transaction_type"] == "Deposit",
        work["amount"],
        0,
    )
    work["withdrawal_amount"] = np.where(
        work["transaction_type"] == "Withdrawal",
        work["amount"],
        0,
    )

    summary = (
        work.groupby(
            ["account_id", "display_name", "account_type"],
            as_index=False,
        )
        .agg(
            total_deposits=("deposit_amount", "sum"),
            total_withdrawals=("withdrawal_amount", "sum"),
            transaction_count=("transaction_id", "count"),
        )
    )

    summary["net_flow"] = (
        summary["total_deposits"] - summary["total_withdrawals"]
    )

    return summary[columns].sort_values("account_id")


def monthly_transaction_summary(df):
    """Summarize transaction activity for each calendar month."""
    columns = [
        "month",
        "total_deposits",
        "total_withdrawals",
        "net_flow",
        "transaction_count",
    ]

    if df.empty:
        return pd.DataFrame(columns=columns)

    work = df.copy()
    work["transaction_date"] = pd.to_datetime(
        work["transaction_date"]
    )
    work["month"] = (
        work["transaction_date"].dt.to_period("M").astype(str)
    )

    work["deposit_amount"] = np.where(
        work["transaction_type"] == "Deposit",
        work["amount"],
        0,
    )
    work["withdrawal_amount"] = np.where(
        work["transaction_type"] == "Withdrawal",
        work["amount"],
        0,
    )

    summary = (
        work.groupby("month", as_index=False)
        .agg(
            total_deposits=("deposit_amount", "sum"),
            total_withdrawals=("withdrawal_amount", "sum"),
            transaction_count=("transaction_id", "count"),
        )
        .sort_values("month")
    )

    summary["net_flow"] = (
        summary["total_deposits"] - summary["total_withdrawals"]
    )

    return summary[columns]

def account_wise_summary(df):
    """Summarize deposits and withdrawals by account."""
    columns = [
        "account_id",
        "display_name",
        "account_type",
        "total_deposits",
        "total_withdrawals",
        "net_flow",
        "transaction_count",
    ]

    if df.empty:
        return pd.DataFrame(columns=columns)

    work = df.copy()
    work["deposit_amount"] = np.where(
        work["transaction_type"] == "Deposit", work["amount"], 0
    )
    work["withdrawal_amount"] = np.where(
        work["transaction_type"] == "Withdrawal", work["amount"], 0
    )

    summary = work.groupby(
        ["account_id", "display_name", "account_type"],
        as_index=False,
    ).agg(
        total_deposits=("deposit_amount", "sum"),
        total_withdrawals=("withdrawal_amount", "sum"),
        transaction_count=("transaction_id", "count"),
    )

    summary["net_flow"] = (
        summary["total_deposits"] - summary["total_withdrawals"]
    )

    return summary[columns].sort_values("account_id")


def monthly_transaction_summary(df):
    """Summarize transactions by calendar month."""
    columns = [
        "month",
        "total_deposits",
        "total_withdrawals",
        "net_flow",
        "transaction_count",
    ]

    if df.empty:
        return pd.DataFrame(columns=columns)

    work = df.copy()
    work["transaction_date"] = pd.to_datetime(work["transaction_date"])
    work["month"] = work["transaction_date"].dt.to_period("M").astype(str)

    work["deposit_amount"] = np.where(
        work["transaction_type"] == "Deposit", work["amount"], 0
    )
    work["withdrawal_amount"] = np.where(
        work["transaction_type"] == "Withdrawal", work["amount"], 0
    )

    summary = work.groupby("month", as_index=False).agg(
        total_deposits=("deposit_amount", "sum"),
        total_withdrawals=("withdrawal_amount", "sum"),
        transaction_count=("transaction_id", "count"),
    ).sort_values("month")

    summary["net_flow"] = (
        summary["total_deposits"] - summary["total_withdrawals"]
    )

    return summary[columns]


if __name__ == "__main__":
    transactions_df = load_transactions()
    analyze_transactions(transactions_df)
