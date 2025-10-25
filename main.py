import streamlit as st
import pandas as pd
import random
import time
from faker import Faker
from datetime import datetime
import analysis
import os
from streamlit_autorefresh import st_autorefresh

def generate_description(category, txn_type):
    income_descriptions = {
        "Salary": ["Monthly Salary", "Bonus Payment", "Freelance Project Income"],
        "Investment": ["Stock Dividend", "Interest from Savings", "Crypto Profit"],
        "Gift": ["Birthday Gift Received", "Cashback Reward", "Refund from Amazon"]
    }

    expense_descriptions = {
        "Food": ["Dinner at restaurant", "Groceries from supermarket", "Coffee shop bill"],
        "Transport": ["Cab fare", "Fuel payment", "Bus ticket"],
        "Rent": ["Monthly house rent", "Office space rent"],
        "Entertainment": ["Movie tickets", "Music subscription", "Weekend outing"],
        "Utilities": ["Electricity bill", "Mobile recharge", "Internet bill"],
        "Shopping": ["Online purchase", "Mall shopping", "Clothing and accessories"]
    }

    if txn_type.lower() == "income":
        options = income_descriptions.get(category, ["Income received"])
    else:
        options = expense_descriptions.get(category, ["Expense made"])

    return random.choice(options)

fake = Faker()

st.set_page_config(page_title="Dynamic Personal Finance Dashboard", layout="wide")
st.title("Dynamic Personal Finance Dashboard")

# Initialize session state
if "df" not in st.session_state:
    st.session_state.df = pd.DataFrame(columns=["Date", "Category", "Description", "Amount", "Type", "Payment_Method"])
if "streaming" not in st.session_state:
    st.session_state.streaming = False

# Sidebar controls
st.sidebar.header("Controls")

start_stop = st.sidebar.button("Start Streaming" if not st.session_state.streaming else "Stop Streaming")
if start_stop:
    st.session_state.streaming = not st.session_state.streaming

refresh_sec = st.sidebar.slider("Refresh every (seconds)", 1, 10, 3)
persist = st.sidebar.checkbox("Save generated data to CSV", value=False)
run_analysis = st.sidebar.button("Run Analysis Now")


if persist and not os.path.exists("data"):
    os.makedirs("data")

# Manual add form
st.sidebar.subheader("Add Manual Transaction")
with st.sidebar.form("manual_txn"):
    d = st.date_input("Date", value=datetime.now())
    cat = st.selectbox("Category", ["Food", "Transport", "Groceries", "Entertainment", "Rent", "Investment", "Salary"])
    desc = st.text_input("Description", "Manual entry")
    amt = st.number_input("Amount", min_value=1, value=100)
    ttype = st.selectbox("Type", ["Expense", "Income"])
    method = st.selectbox("Payment Method", ["UPI", "Credit Card", "Debit Card", "Bank Transfer"])
    submit = st.form_submit_button("Add")
    if submit:
        new = {"Date": pd.to_datetime(d), "Category": cat, "Description": desc, "Amount": amt, "Type": ttype, "Payment_Method": method}
        st.session_state.df = pd.concat([st.session_state.df, pd.DataFrame([new])], ignore_index=True)
        st.success("Transaction added.")

# Streaming simulation
if st.session_state.streaming:
    st_autorefresh(interval=int(refresh_sec * 1000), key="data_refresh")
    income_categories = ["Salary", "Investment", "Gift"]
    expense_categories = ["Food", "Transport", "Groceries", "Entertainment", "Rent", "Utilities", "Shopping"]

    txn_type = random.choices(["Expense", "Income"], weights=[0.3, 0.7])[0]
    category = random.choice(income_categories if txn_type == "Income" else expense_categories)

    new = {
        "Date": datetime.now(),
        "Category": category,
        "Type": txn_type,
        "Description": generate_description(category, txn_type),
        "Amount": random.randint(100, 5000),
        "Payment_Method": random.choice(["UPI", "Credit Card", "Debit Card", "Bank Transfer"])
    }

    st.session_state.df = pd.concat([st.session_state.df, pd.DataFrame([new])], ignore_index=True)

    if persist:
        st.session_state.df.to_csv("data/historical_data.csv", index=False)

# KPIs
st.subheader("Overview")
df = st.session_state.df.copy()
if not df.empty:
    df["Amount"] = pd.to_numeric(df["Amount"], errors="coerce").fillna(0)
    income = df[df["Type"].str.lower() == "income"]["Amount"].sum()
    expense = df[df["Type"].str.lower() == "expense"]["Amount"].sum()
    savings = income - expense


    c1, c2, c3 = st.columns(3)
    c1.metric("Total Income", f"₹{income:,.0f}")
    c2.metric("Total Expense", f"₹{expense:,.0f}")
    c3.metric("Net Savings", f"₹{savings:,.0f}")


    st.markdown("---")
    st.subheader("Recent Transactions")
    st.dataframe(df.tail(10).sort_values(by="Date", ascending=False))
else:
    st.info("No data yet. Start streaming or add a transaction manually.")

# Run offline analysis
if run_analysis:
    if df.empty:
        st.warning("No data available for analysis.")
    else:
        st.info("Generating analysis visuals...")
        files = analysis.generate_analytics(df)
        if files:
            st.success(f"Generated: {', '.join([os.path.basename(f) for f in files])}")



# Show visuals if available
st.markdown("---")
st.subheader("Visual Insights")
cols = st.columns(3)
visuals = ["monthly_trend.png", "expense_distribution.png", "correlation_heatmap.png"]
for i, vis in enumerate(visuals):
    path = os.path.join("visuals", vis)
    if os.path.exists(path):
        cols[i % 3].image(path, caption=vis)
    else:
        cols[i % 3].info(f"Run analysis to generate {vis}.")


# Auto-refresh
if st.session_state.streaming:
    time.sleep(refresh_sec)
    