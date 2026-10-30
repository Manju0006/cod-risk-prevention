
import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
RULES_FILE = BASE_DIR / "config" / "rules.json"


def load_rules():
    with open(RULES_FILE, "r", encoding="utf-8") as file:
        return json.load(file)


def create_message(customer_name, order_value, discount):
    prepaid_price = max(0, order_value - discount)

    return f"""
Hello {customer_name}! 👋

Thank you for ordering from us.

Your COD order worth ₹{order_value:.2f} is ready for confirmation.

Please reply:
YES - Confirm your COD order
NO - Cancel your order
PREPAID - Pay online and get ₹{discount} OFF

Prepaid amount: ₹{prepaid_price:.2f}

Please respond within 24 hours.
Thank you! ❤️
"""


def simulate_whatsapp():
    rules = load_rules()
    discount = rules["prepaid_discount"]

    print("\n========== WHATSAPP CONFIRMATION ==========")

    customer_name = input("Customer name: ").strip() or "Customer"

    try:
        order_value = float(input("Order value (₹): "))
        if order_value <= 0:
            raise ValueError
    except ValueError:
        print("Please enter a valid positive order value.")
        return

    message = create_message(customer_name, order_value, discount)

    print("\n---------- MESSAGE SENT ----------")
    print(message)

    print("----------------------------------")
    print("SIMULATE CUSTOMER RESPONSE")
    print("1. YES - Confirm COD")
    print("2. NO - Cancel order")
    print("3. PREPAID - Choose prepaid payment")
    print("4. RANDOM - Unclear response")
    print("5. NO REPLY - No response for 24 hours")

    choice = input("\nSelect response (1-5): ").strip()

    print("\n========== SIMULATION RESULT ==========")

    if choice == "1":
        print("Customer response: YES")
        print("Status: COD order confirmed")
        print("Next action: Ship the order")

    elif choice == "2":
        print("Customer response: NO")
        print("Status: Customer requested cancellation")
        print("Next action: Cancel after verification")

    elif choice == "3":
        prepaid_price = max(0, order_value - discount)
        print("Customer response: PREPAID")
        print(f"Original order value: ₹{order_value:.2f}")
        print(f"Prepaid discount: ₹{discount:.2f}")
        print(f"Final prepaid amount: ₹{prepaid_price:.2f}")
        print("Status: Awaiting online payment")
        print("Next action: Ship only after payment is successful")

    elif choice == "4":
        print("Customer response: Random / unclear")
        print("Status: Confirmation not received")
        print("Next action: Send one clarification message or route to Ops")

    elif choice == "5":
        print("Customer response: No reply")
        print("Simulated waiting period: 24 hours")
        print("Status: Confirmation timeout")
        print("Next action: Hold for manual review; do not auto-cancel")

    else:
        print("Invalid choice. Please run the simulator again.")

    print("=======================================")


if __name__ == "__main__":
    simulate_whatsapp()
