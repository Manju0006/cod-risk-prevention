
import json
import joblib
import pandas as pd

from pathlib import Path


# ==========================================
# PROJECT PATHS
# ==========================================

BASE_DIR = Path(__file__).resolve().parent.parent

MODEL_FILE = BASE_DIR / "models" / "rto_model.pkl"

RULES_FILE = BASE_DIR / "config" / "rules.json"


# ==========================================
# LOAD MODEL AND BUSINESS RULES
# ==========================================

def load_model():

    if not MODEL_FILE.exists():
        raise FileNotFoundError(
            "Trained model not found. "
            "Run python src/train_model.py first."
        )

    return joblib.load(MODEL_FILE)


def load_rules():

    if not RULES_FILE.exists():
        raise FileNotFoundError(
            "Business rules file not found."
        )

    with open(RULES_FILE, "r") as file:
        rules = json.load(file)

    thresholds = rules["risk_thresholds"]

    values = [
        thresholds["ship_as_is"],
        thresholds["ship_after_confirmation"],
        thresholds["nudge_to_prepaid"]
    ]

    if not all(0 <= value <= 1 for value in values):
        raise ValueError("Risk thresholds must be between 0 and 1.")

    if values != sorted(values):
        raise ValueError("Risk thresholds must be in ascending order.")

    return rules


# ==========================================
# DECISION ENGINE
# ==========================================

def decide_order(order):

    model = load_model()
    rules = load_rules()

    thresholds = rules["risk_thresholds"]

    # Required model features
    required_features = [
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
        "courier"
    ]

    # Check missing fields
    missing = [
        feature for feature in required_features
        if feature not in order
    ]

    if missing:
        raise ValueError(
            f"Missing order details: {missing}"
        )

    # Validate customer history
    prior_orders = int(order["customer_prior_orders"])
    prior_rto = int(order["customer_prior_rto"])

    if prior_orders < 0 or prior_rto < 0:
        raise ValueError("Customer history cannot be negative.")

    if prior_rto > prior_orders:
        raise ValueError(
            "Previous RTO count cannot exceed previous orders."
        )

    # Prepare model input
    input_df = pd.DataFrame(
        [{
            feature: order[feature]
            for feature in required_features
        }]
    )

    # Predict RTO probability
    probability = model.predict_proba(input_df)[0][1]

    risk_percentage = round(probability * 100, 2)

    # ======================================
    # BUSINESS DECISION RULES
    # ======================================

    first_time = prior_orders == 0

    repeat_rto_limit = rules["repeat_rto_limit"]

    # Extreme-risk cases are held for manual review.
    # Automatic cancellation is disabled by default.

    if (
        probability >= thresholds["nudge_to_prepaid"]
        and prior_rto >= repeat_rto_limit
    ):

        action = "Hold / cancel"

        reason = (
            "Very high predicted RTO risk combined with "
            "multiple previous returned orders. "
            "Hold for manual review before cancellation."
        )

    elif probability < thresholds["ship_as_is"]:

        action = "Ship as-is"

        reason = (
            "The predicted RTO risk is relatively low. "
            "The order can proceed without additional confirmation."
        )

    elif probability < thresholds["ship_after_confirmation"]:

        action = "Ship after confirmation"

        reason = (
            "The order has some delivery risk. "
            "Ask the customer to confirm through WhatsApp "
            "before shipping."
        )

    elif probability < thresholds["nudge_to_prepaid"]:

        action = "Nudge to prepaid"

        reason = (
            "The order has elevated delivery risk. "
            "Offer the customer a prepaid payment option "
            "with a small discount."
        )

    else:

        action = "Hold / cancel"

        reason = (
            "The predicted RTO risk is extremely high. "
            "Hold the order for manual review."
        )

    # Protect first-time customers from automatic cancellation.
    if first_time and rules["first_time_customer_protection"]:

        if action == "Hold / cancel":

            action = "Nudge to prepaid"

            reason = (
                "This is a first-time customer. "
                "Automatic cancellation is avoided. "
                "Offer prepaid payment and review the order."
            )

    # Final cancellation is never automatic in this version.
    if action == "Hold / cancel":

        if not rules["auto_cancel_enabled"]:

            reason += (
                " Automatic cancellation is disabled; "
                "operations approval is required."
            )

    # ======================================
    # RETURN DECISION
    # ======================================

    result = {
        "action": action,
        "rto_probability": risk_percentage,
        "risk_level": (
            "Low" if probability < thresholds["ship_as_is"]
            else "Medium" if probability < thresholds["nudge_to_prepaid"]
            else "High"
        ),
        "reason": reason,
        "prepaid_discount": (
            rules["prepaid_discount"]
            if action == "Nudge to prepaid"
            else 0
        ),
        "customer_first_order": first_time
    }

    return result


# ==========================================
# TEST THE DECISION ENGINE
# ==========================================

if __name__ == "__main__":

    sample_order = {

        "order_value": 649,

        "num_items": 2,

        "customer_prior_orders": 1,

        "customer_prior_rto": 0,

        "order_hour": 14,

        "order_month": 10,

        "order_dayofweek": 4,

        "city": "Hyderabad",

        "state": "Telangana",

        "utm_source": "meta_ads",

        "courier": "Delhivery"
    }

    print("\n========== COD DECISION ENGINE ==========")

    result = decide_order(sample_order)

    print("\nORDER DECISION")

    print("Action:", result["action"])

    print(
        "Predicted RTO Risk:",
        str(result["rto_probability"]) + "%"
    )

    print("Risk Level:", result["risk_level"])

    print("Reason:", result["reason"])

    print(
        "Prepaid Discount:",
        "₹" + str(result["prepaid_discount"])
    )

    print(
        "First-time Customer:",
        result["customer_first_order"]
    )

    print("\n=========================================")
