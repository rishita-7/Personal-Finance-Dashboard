import os
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import seaborn as sns
import numpy as np

sns.set_theme(style='whitegrid')
VISUALS_DIR = "visuals"
os.makedirs(VISUALS_DIR, exist_ok=True)

def _prepare_data(df):
    df = df.copy()
    if not pd.api.types.is_datetime64_any_dtype(df["Date"]):
        df["Date"] = pd.to_datetime(df["Date"])
    df["Amount"] = pd.to_numeric(df["Amount"], errors="coerce").fillna(0)

    df["Day"] = df["Date"].dt.day
    df["Month"] = df["Date"].dt.month
    df["Year"] = df["Date"].dt.year
    df["Amount_Abs"] = df["Amount"].abs()
    return df

def generate_analytics(df):
    os.makedirs(VISUALS_DIR, exist_ok=True)

    # --- Clean and prepare ---
    df = _prepare_data(df)
    df["Month_Year"] = df["Date"].dt.to_period("M").dt.to_timestamp()

    # --- Monthly Income vs Expense Trend ---
    # monthly_trend = (
    #     df.groupby(['Month_Year', 'Type'])['Amount']
    #     .sum()
    #     .unstack(fill_value=0)
    #     .sort_index()
    #     .reset_index()
    # )

    # plt.figure(figsize=(10, 6))
    # ax = sns.lineplot(
    #     data=monthly_trend.melt(id_vars='Month_Year', value_vars=['Income','Expense']),
    #     x="Month_Year",
    #     y="value",
    #     hue="Type",
    #     marker="o",
    #     palette={'Income': '#2ecc71', 'Expense': '#e74c3c'}
    # )
    # ax.set_title("Income vs Expense trend", fontsize=16)
    # ax.set_xlabel("Month", fontsize=12)
    # ax.set_ylabel("Amount (₹)", fontsize=12)

    # ax.xaxis.set_major_locator(mdates.MonthLocator(interval=1))
    # ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))
    # plt.xticks(rotation=45)


    # plt.tight_layout()
    # plt.savefig(os.path.join(VISUALS_DIR, "income_expense_tracker.png"))
    # plt.close()
    plt.figure(figsize=(5,5))
    barplot = sns.barplot(
        data=df.groupby('Type')['Amount'].sum().reset_index(),  # group first to plot totals
        x='Type',
        y='Amount',
        palette={'Income': '#2ecc71', 'Expense': '#e74c3c'}  # color coding income green, expense red
    )
    plt.title("Income vs Expense", fontsize=14)
    plt.xlabel("Type", fontsize=12)
    plt.ylabel("Amount", fontsize=12)
    plt.tight_layout()
    plt.savefig(os.path.join(VISUALS_DIR, "income_vs_expense.png"))
    plt.close()

    # --- Income Distribution ---
    income_df = df[df["Type"].str.lower() == "income"]
    income_data = income_df.groupby("Category")["Amount"].sum().reset_index()
    income_data = income_data.sort_values(by="Amount", ascending=False)

    plt.figure(figsize=(5,5))
    barplot = sns.barplot(
        data=income_data,
        y="Amount",
        x="Category",
        palette=sns.color_palette("mako", n_colors=len(income_data))
    )
    plt.title("Income Distribution by Category", fontsize=14)
    plt.xlabel("Total Income (₹)", fontsize=12)
    plt.ylabel("Category", fontsize=12)

    # Add text labels to bars
    for index, row in income_data.iterrows():
        barplot.text(row["Amount"] + max(income_data["Amount"])*0.01, index, f'₹{row["Amount"]:,.0f}', va='center')

    plt.tight_layout()
    plt.savefig(os.path.join(VISUALS_DIR, "income_distribution.png"))
    plt.close()

    # --- Expense breakdown pie-chart ---

    expense_df = df[df["Type"].str.lower() == "expense"]
    expense_data = expense_df.groupby("Category")["Amount"].sum().reset_index()
    expense_data = expense_data.sort_values(by="Amount", ascending=False)


    expense_data = df[df["Type"].str.lower() == "expense"].groupby("Category")["Amount"].sum()
    plt.figure(figsize=(6, 6))
    plt.pie(expense_data, labels=expense_data.index, autopct='%1.1f%%', startangle=140, colors=sns.color_palette('pastel'))
    plt.title("Expense Breakdown by Category")
    plt.tight_layout()
    plt.savefig(os.path.join(VISUALS_DIR, "expense_breakdown_pie.png"))
    plt.close()

    print("✅ All analytics visuals generated in 'visuals/' folder.")

    files = [
        os.path.join(VISUALS_DIR, "income_vs_expense.png"),
        os.path.join(VISUALS_DIR, "income_distribution.png"),
        os.path.join(VISUALS_DIR, "expense_breakdown_pie.png")
    ]
    return files

if __name__ == "__main__":
    print("Analytics for the Streamlit dashboard")
