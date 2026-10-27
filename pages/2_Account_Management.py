import requests
import pandas as pd
import streamlit as st
from dashboard_utils import API_BASE_URL, format_inr
if st.button("← Home"):
    st.switch_page("pages/0_Home.py")
st.set_page_config(page_title="Account Management", page_icon="🏦", layout="wide")
st.title("🏦 Account Management")
st.write("Browse account records returned by your Flask API. This page does not create or edit accounts.")

try:
    response = requests.get(f"{API_BASE_URL}/accounts", timeout=10)
    response.raise_for_status()

    api_data = response.json()
    accounts = pd.DataFrame(api_data.get("accounts", []))

except (requests.RequestException, ValueError) as error:
    st.error("Could not load accounts from Flask. Make sure `python run.py` is running.")
    st.caption(str(error))
    st.stop()

if accounts.empty:
    st.info("No account records were returned by the API.")
    st.stop()

if "account_id" in accounts.columns:
    accounts["account_id"] = accounts["account_id"].astype(str)
search = st.text_input("Search by account ID, customer name, or account type")
shown = accounts.copy()
if search.strip():
    mask = pd.Series(False, index=shown.index)
    for column in ["account_id", "customer_id", "display_name", "account_type"]:
        if column in shown.columns:
            mask |= shown[column].astype(str).str.contains(search, case=False, na=False)
    shown = shown[mask]

m1, m2 = st.columns(2)
m1.metric("Accounts returned", f"{len(accounts):,}")
if "account_type" in accounts.columns:
    m2.metric("Account types", f"{accounts['account_type'].nunique():,}")
else:
    m2.metric("Account types", "—")

st.subheader("Account Records")
st.dataframe(shown, use_container_width=True, hide_index=True)

balance_column = "current_balance" if "current_balance" in accounts.columns else ("opening_balance" if "opening_balance" in accounts.columns else None)
if balance_column:
    accounts[balance_column] = pd.to_numeric(accounts[balance_column], errors="coerce")
    st.subheader("Balance Summary")
    st.caption(f"Summary uses `{balance_column}` as returned by the API.")
    st.metric("Total shown balance", format_inr(accounts[balance_column].fillna(0).sum()))
else:
    st.info("The API did not return a current_balance or opening_balance column, so a balance summary cannot be displayed.")

st.download_button("📥 Download Accounts CSV", accounts.to_csv(index=False).encode("utf-8"), file_name="bank_accounts.csv", mime="text/csv")
