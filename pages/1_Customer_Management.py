
import requests
import pandas as pd
import streamlit as st
from dashboard_utils import API_BASE_URL, format_inr, get_transaction_data, prepare_transactions

st.set_page_config(
    page_title="Customer Management",
    page_icon="👥",
    layout="wide"
)

if st.button("← Home"):
    st.switch_page("pages/0_Home.py")

st.title("👥 Customer Management")

st.write("Browse customer records and inspect each customer's transaction history.")

try:
    response = requests.get(f"{API_BASE_URL}/customers", timeout=10)
    response.raise_for_status()

    api_data = response.json()
    customers = pd.DataFrame(api_data.get("customers", []))

except (requests.RequestException, ValueError) as error:
    st.error("Could not load customers from Flask. Make sure `python run.py` is running.")
    st.caption(str(error))
    st.stop()

if customers.empty:
    st.info("No customer records were returned by the API.")
    st.stop()

st.subheader("Add New Customer")

with st.form("add_customer_form", clear_on_submit=True):
    customer_name = st.text_input(
        "Customer Name",
        placeholder="Enter customer name"
    )
    submitted = st.form_submit_button("➕ Add Customer")

    if submitted:
        if not customer_name.strip():
            st.error("Please enter a customer name.")
        else:
            try:
                response = requests.post(
                    f"{API_BASE_URL}/customers",
                    json={"display_name": customer_name.strip()},
                    timeout=10
                )

                if response.status_code == 201:
                    st.success("Customer added successfully!")
                    st.rerun()
                else:
                    error_message = response.json().get(
                        "error", "Could not add customer."
                    )
                    st.error(error_message)

            except requests.RequestException as error:
                st.error("Could not connect to Flask.")
                st.caption(str(error))

st.subheader("Customer List")
search = st.text_input("Search by customer name or ID")
shown = customers.copy()
if search.strip():
    mask = pd.Series(False, index=shown.index)
    if "display_name" in shown.columns:
        mask |= shown["display_name"].astype(str).str.contains(search, case=False, na=False)
    if "customer_id" in shown.columns:
        mask |= shown["customer_id"].astype(str).str.contains(search, case=False, na=False)
    shown = shown[mask]
st.dataframe(shown, use_container_width=True, hide_index=True)

if customers.empty:
    st.warning("No customer data is available.")
    st.stop()

if "display_name" not in customers.columns:
    st.warning(
        "Customer names are unavailable. "
        "Please check the customers API response."
    )
    st.stop()

options = customers.to_dict("records")
def label(row):
    return f"{row.get('customer_id', '?')} — {row.get('display_name', 'Unnamed customer')}"
selected_label = st.selectbox("Choose a customer to view history", [label(row) for row in options])
selected = options[[label(row) for row in options].index(selected_label)]

try:
    df = prepare_transactions(get_transaction_data())
except Exception as error:
    st.error("Customer records loaded, but transaction history could not be loaded.")
    st.caption(str(error))
    st.stop()

if df.empty or "display_name" not in df.columns:
    st.info("No transaction history is available yet.")
    st.stop()

customer_df = df[df["display_name"].astype(str) == str(selected["display_name"])].copy()
st.divider()
st.subheader(f"Transaction History — {selected.get('display_name', 'Customer')}")
if customer_df.empty:
    st.info("No transactions found for this customer.")
else:
    deposits = customer_df.loc[customer_df["transaction_type"] == "Deposit", "amount"].sum() if "transaction_type" in customer_df else 0
    withdrawals = customer_df.loc[customer_df["transaction_type"] == "Withdrawal", "amount"].sum() if "transaction_type" in customer_df else 0
    a, b, c = st.columns(3)
    a.metric("Total Transactions", len(customer_df))
    b.metric("Total Deposits", format_inr(deposits))
    c.metric("Total Withdrawals", format_inr(withdrawals))
    if "transaction_date" in customer_df.columns:
        customer_df = customer_df.sort_values("transaction_date", ascending=False)
    columns = [col for col in ["transaction_id", "account_id", "account_type", "transaction_date", "transaction_type", "amount", "description"] if col in customer_df.columns]
    st.dataframe(customer_df[columns], use_container_width=True, hide_index=True)
    st.download_button("📥 Download Customer Transactions", customer_df.to_csv(index=False).encode("utf-8"), file_name="customer_transactions.csv", mime="text/csv")
