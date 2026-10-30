
import pandas as pd
from pathlib import Path

# ==========================================
# PROJECT FILE PATHS
# ==========================================

BASE_DIR = Path(__file__).resolve().parent.parent

INPUT_FILE = BASE_DIR / "data" / "orders_sample.csv"

OUTPUT_FILE = BASE_DIR / "data" / "cleaned_orders.csv"


# ==========================================
# DATA CLEANING FUNCTION
# ==========================================

def clean_orders():

    print("\n========== DATA CLEANING ==========")

    # 1. Load original dataset
    df = pd.read_csv(INPUT_FILE)

    print("Original records:", len(df))

    # 2. Remove duplicate orders
    before = len(df)

    df = df.drop_duplicates(
        subset="order_id",
        keep="first"
    ).copy()

    print("Duplicates removed:", before - len(df))

    # 3. Standardise delivery status
    df["final_status"] = (
        df["final_status"]
        .astype(str)
        .str.strip()
        .str.upper()
        .str.replace(r"[\s-]+", "_", regex=True)
    )

    # 4. Keep completed orders only
    df = df[
        df["final_status"].isin([
            "DELIVERED",
            "RTO"
        ])
    ].copy()

    # 5. Convert order date
    df["order_datetime"] = pd.to_datetime(
        df["order_datetime"],
        errors="coerce"
    )

    # Remove invalid dates
    df = df.dropna(
        subset=["order_datetime"]
    ).copy()

    # 6. Extract date features
    df["order_hour"] = (
        df["order_datetime"].dt.hour
    )

    df["order_month"] = (
        df["order_datetime"].dt.month
    )

    df["order_dayofweek"] = (
        df["order_datetime"].dt.dayofweek
    )

    # 7. Create target variable
    # 0 = Delivered
    # 1 = RTO

    df["rto"] = (
        df["final_status"] == "RTO"
    ).astype(int)

    # 8. Select required columns
    # Keep order_datetime for chronological ML splitting.
    # Do not include private customer information.

    columns = [
        "order_id",
        "order_datetime",
        "order_value",
        "num_items",
        "customer_prior_orders",
        "customer_prior_rto",
        "order_hour",
        "order_month",
        "order_dayofweek",
        "city",
        "state",
        "utm_source",
        "courier",
        "rto"
    ]

    cleaned_df = df[columns].copy()

    # 9. Save cleaned dataset
    cleaned_df.to_csv(
        OUTPUT_FILE,
        index=False
    )

    # 10. Calculate summary
    total = len(cleaned_df)

    rto_count = int(
        cleaned_df["rto"].sum()
    )

    delivered_count = total - rto_count

    rto_percentage = (
        rto_count / total * 100
        if total > 0 else 0
    )

    # 11. Display results
    print("\n========== CLEANING SUMMARY ==========")

    print("Total completed orders:", total)

    print("Delivered orders:", delivered_count)

    print("RTO orders:", rto_count)

    print(
        "RTO percentage:",
        round(rto_percentage, 2),
        "%"
    )

    print("\nCleaned file saved successfully!")

    print("File location:", OUTPUT_FILE)

    print("\n======================================")


# ==========================================
# MAIN PROGRAM
# ==========================================

if __name__ == "__main__":

    clean_orders()
