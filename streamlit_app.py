
import streamlit as st

st.set_page_config(
    page_title="Banking Transaction Analysis",
    page_icon="🏦",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# Hide Streamlit's default sidebar and navigation.
st.markdown(
    """
    <style>
    section[data-testid="stSidebar"] {
        display: none;
    }

    [data-testid="stSidebarNav"] {
        display: none;
    }

    [data-testid="collapsedControl"] {
        display: none;
    }

    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# Register all five pages explicitly.
home_page = st.Page(
    "pages/0_Home.py",
    title="Home",
    icon="🏦",
    default=True,
    visibility="hidden",
)

customer_page = st.Page(
    "pages/1_Customer_Management.py",
    title="Customer Management",
    icon="👥",
    visibility="hidden",
)

account_page = st.Page(
    "pages/2_Account_Management.py",
    title="Account Management",
    icon="🏦",
    visibility="hidden",
)

transactions_page = st.Page(
    "pages/3_Transactions.py",
    title="Transactions",
    icon="💳",
    visibility="hidden",
)

analytics_page = st.Page(
    "pages/4_Analytics_Reports.py",
    title="Analytics & Reports",
    icon="📊",
    visibility="hidden",
)

# Use hidden navigation; the homepage supplies the four buttons.
page = st.navigation(
    [
        home_page,
        customer_page,
        account_page,
        transactions_page,
        analytics_page,
    ],
    position="hidden",
)

page.run()
