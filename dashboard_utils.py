"""Shared helpers for the Banking Transaction Analysis Streamlit dashboard."""
import pandas as pd
import streamlit as st
from analysis import load_transactions

API_BASE_URL = "http://127.0.0.1:5000"


def format_inr(value):
    try:
        return f"₹{float(value):,.2f}"
    except (TypeError, ValueError):
        return "₹0.00"


@st.cache_data(ttl=30)
def get_transaction_data():
    """Load transaction data from the existing analysis/database layer."""
    df = load_transactions()
    if df is None:
        return pd.DataFrame()
    return df.copy()


def prepare_transactions(df):
    """Return a copy with consistent numeric/date types and review flags."""
    if df is None or df.empty:
        return pd.DataFrame() if df is None else df.copy()

    result = df.copy()
    if "amount" in result.columns:
        result["amount"] = pd.to_numeric(result["amount"], errors="coerce").fillna(0)
    if "transaction_date" in result.columns:
        result["transaction_date"] = pd.to_datetime(result["transaction_date"], errors="coerce")

    if "amount" in result.columns:
        q3 = result["amount"].quantile(0.75)
        q1 = result["amount"].quantile(0.25)
        threshold = max(20000.0, float(q3 + 1.5 * (q3 - q1)))
        result["review_flag"] = result["amount"].apply(
            lambda amount: "Review" if amount >= threshold else "Normal"
        )
    return result
