import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

sns.set(style='whitegrid')
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
    os.makedirs("visuals", exist_ok=True)

    # --- Clean and prepare ---
    df = _prepare_data(df)
    df["Month_Year"] = df["Date"].dt.to_period("M").dt.to_timestamp()

    # --- Monthly Income vs Expense Trend ---
    monthly_trend = (
        df.groupby(["Month_Year", "Type"])["Amount"]
        .sum()
        .reset_index()
        .sort_values("Month_Year")
    )

    plt.figure(figsize=(9, 5))
    sns.lineplot(
        data=monthly_trend,
        x="Month_Year",
        y="Amount",
        hue="Type",
        marker="o"
    )
    plt.title("Monthly Income vs Expense Trend")
    plt.xlabel("Month")
    plt.ylabel("Amount (₹)")
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(os.path.join(VISUALS_DIR, "monthly_trend.png"))
    plt.close()

    # --- Expense Distribution ---
    expense_df = df[df["Type"].str.lower() == "expense"]
    plt.figure(figsize=(6, 4))
    sns.barplot(
        data=expense_df.groupby("Category")["Amount"].sum().reset_index(),
        x="Amount",
        y="Category",
        palette="mako"
    )
    plt.title("Expense Distribution by Category")
    plt.xlabel("Total Expense (₹)")
    plt.ylabel("Category")
    plt.tight_layout()
    plt.savefig(os.path.join(VISUALS_DIR, "expense_distribution.png"))
    plt.close()

    # --- Correlation Heatmap ---
    numeric = df[["Amount_Abs", "Day", "Month", "Year"]]
    corr = numeric.corr()
    plt.figure(figsize=(6, 5))
    sns.heatmap(corr, annot=True, fmt=".2f", cmap="coolwarm", square=True)
    plt.title("Feature Correlation Heatmap")
    plt.tight_layout()
    plt.savefig(os.path.join(VISUALS_DIR, "correlation_heatmap.png"))
    plt.close()

    print("✅ All analytics visuals generated in 'visuals/' folder.")


if __name__ == "__main__":
    print("Analytics for the Streamlit dashboard")
