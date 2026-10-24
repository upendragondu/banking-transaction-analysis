
import matplotlib.pyplot as plt

from analysis import load_transactions


def create_charts():
    df = load_transactions()

    if df.empty:
        print("No transaction data available.")
        return

    # Create a folder for generated charts.
    import os
    os.makedirs("reports", exist_ok=True)

    # Chart 1: Total deposits vs withdrawals.
    totals = df.groupby("transaction_type")["amount"].sum()

    plt.figure(figsize=(8, 5))
    totals.plot(kind="bar")
    plt.title("Total Deposits vs Withdrawals")
    plt.xlabel("Transaction Type")
    plt.ylabel("Amount (₹)")
    plt.xticks(rotation=0)
    plt.tight_layout()
    plt.savefig("reports/deposits_vs_withdrawals.png")

    plt.close()

    # Chart 2: Transaction amounts over time.
    df = df.sort_values("transaction_date")

    plt.figure(figsize=(10, 5))
    plt.plot(
        df["transaction_date"],
        df["amount"],
        marker="o"
    )
    plt.title("Transaction Amounts Over Time")
    plt.xlabel("Transaction Date")
    plt.ylabel("Amount (₹)")
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig("reports/transaction_amounts_over_time.png")

    plt.close()

    # Chart 3: Transaction counts by type.
    counts = df["transaction_type"].value_counts()

    plt.figure(figsize=(7, 5))
    counts.plot(kind="bar")
    plt.title("Number of Transactions by Type")
    plt.xlabel("Transaction Type")
    plt.ylabel("Number of Transactions")
    plt.xticks(rotation=0)
    plt.tight_layout()
    plt.savefig("reports/transaction_counts.png")

    plt.close()

    print("Charts created successfully!")
    print("Check the reports folder in your project.")


if __name__ == "__main__":
    create_charts()
