import requests
import pandas as pd
import streamlit as st
from dashboard_utils import API_BASE_URL, format_inr, get_transaction_data, prepare_transactions
if st.button("← Home"):
    st.switch_page("pages/0_Home.py")
st.set_page_config(page_title="Transactions", page_icon="💳", layout="wide")
st.title("💳 Transactions")
st.write("Review transaction records and submit deposits or withdrawals through the existing Flask API.")

with st.expander("Record a deposit or withdrawal", expanded=True):
    try:
        account_response = requests.get(f"{API_BASE_URL}/accounts", timeout=10)
        account_response.raise_for_status()

        api_data = account_response.json()
        account_records = api_data.get("accounts", [])

        if not isinstance(account_records, list):
            account_records = []

        account_records = [
            account for account in account_records
            if isinstance(account, dict)
               and account.get("account_id") is not None
        ]

    except (requests.RequestException, ValueError) as error:
        account_records = []
        st.warning("Could not load account choices from Flask. You can still review transactions below.")
        st.caption(str(error))

    # Keep only valid account dictionaries
    if isinstance(account_records, list):
        account_records = [
            a for a in account_records
            if isinstance(a, dict)
        ]
    else:
        account_records = []

    if account_records:
        account_options = {
            f"Account {a.get('account_id')} — "
            f"{a.get('display_name', 'Customer')} "
            f"({a.get('account_type', 'Account')})": a.get("account_id")
            for a in account_records
            if a.get("account_id") is not None
        }

        if account_options:
            with st.form("record_transaction_form"):
                chosen_account = st.selectbox(
                    "Account",
                    list(account_options.keys())
                )
                transaction_type = st.selectbox(
                    "Transaction type",
                    ["Deposit", "Withdrawal"]
                )
                amount = st.number_input(
                    "Amount (₹)",
                    min_value=0.01,
                    step=100.0,
                    format="%.2f"
                )
                description = st.text_input(
                    "Description",
                    max_chars=255
                )
                submitted = st.form_submit_button("Submit Transaction")

            if submitted:
                payload = {
                    "account_id": int(account_options[chosen_account]),
                    "transaction_type": transaction_type,
                    "amount": round(float(amount), 2),
                    "description": description
                }

                try:
                    response = requests.post(
                        f"{API_BASE_URL}/transactions",
                        json=payload,
                        timeout=15
                    )

                    try:
                        result = response.json()
                    except ValueError:
                        result = {
                            "error": response.text
                                     or "The API returned a non-JSON response."
                        }

                    if response.status_code == 201:
                        st.success(
                            result.get(
                                "message",
                                "Transaction recorded successfully."
                            )
                        )

                        if result.get("previous_balance") is not None:
                            st.write(
                                "Previous balance:",
                                format_inr(result["previous_balance"])
                            )

                        if result.get("current_balance") is not None:
                            st.write(
                                "Updated balance:",
                                format_inr(result["current_balance"])
                            )

                        get_transaction_data.clear()
                        st.rerun()
                    else:
                        st.error(
                            result.get(
                                "error",
                                f"Transaction failed (HTTP {response.status_code})."
                            )
                        )

                except requests.RequestException as error:
                    st.error(
                        "Could not connect to Flask. Check that `python run.py` is running."
                    )
                    st.caption(str(error))
        else:
            st.info("No valid account IDs were returned by the API.")
    else:
        st.info(
            "No accounts were available from the API. "
            "Check that Flask is running and the accounts endpoint is returning data."
        )

    st.divider()

st.subheader("Transaction Records")
try:
    df = prepare_transactions(get_transaction_data())
except Exception as error:
    st.error("Unable to load transactions from MySQL.")
    st.caption(str(error))
    st.stop()

if df.empty:
    st.info("No transaction records found.")
    st.stop()

filtered = df.copy()
with st.expander("Filter transactions", expanded=True):
    if "transaction_type" in df.columns:
        types = sorted(df["transaction_type"].dropna().unique().tolist())
        selected_types = st.multiselect("Transaction type", types, default=types)
        filtered = filtered[filtered["transaction_type"].isin(selected_types)]
    if "display_name" in df.columns:
        names = sorted(df["display_name"].dropna().unique().tolist())
        selected_names = st.multiselect("Customer", names, default=names)
        filtered = filtered[filtered["display_name"].isin(selected_names)]
    if "transaction_date" in df.columns and df["transaction_date"].notna().any():
        min_date = df["transaction_date"].min().date()
        max_date = df["transaction_date"].max().date()
        date_range = st.date_input("Date range", value=(min_date, max_date), min_value=min_date, max_value=max_date)
        if isinstance(date_range, (tuple, list)) and len(date_range) == 2:
            filtered = filtered[filtered["transaction_date"].dt.date.between(date_range[0], date_range[1])]

show_reviews = st.checkbox("Show only transactions flagged for review")
if show_reviews and "review_flag" in filtered.columns:
    filtered = filtered[filtered["review_flag"] == "Review"]
if "transaction_date" in filtered.columns:
    filtered = filtered.sort_values("transaction_date", ascending=False)
columns = [c for c in ["transaction_id", "account_id", "display_name", "account_type", "transaction_date", "transaction_type", "amount", "description", "review_flag"] if c in filtered.columns]
st.caption(f"Showing {len(filtered):,} transaction(s).")
st.dataframe(filtered[columns], use_container_width=True, hide_index=True)
st.download_button("📥 Download displayed transactions as CSV", filtered[columns].to_csv(index=False).encode("utf-8"), file_name="banking_transactions.csv", mime="text/csv")
