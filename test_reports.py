
from analysis import (
    load_transactions,
    account_wise_summary,
    monthly_transaction_summary,
)

df = load_transactions()

print("\n===== ACCOUNT-WISE SUMMARY =====")
account_report = account_wise_summary(df)
print(account_report.to_string(index=False))

print("\n===== MONTHLY TRANSACTION SUMMARY =====")
monthly_report = monthly_transaction_summary(df)
print(monthly_report.to_string(index=False))

# Save reports as CSV files
account_report.to_csv(
    "reports/account_wise_summary.csv",
    index=False,
)
monthly_report.to_csv(
    "reports/monthly_transaction_summary.csv",
    index=False,
)

print("\nReports saved in the reports folder.")
