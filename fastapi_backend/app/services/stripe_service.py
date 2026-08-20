import os
import stripe
from dotenv import load_dotenv

load_dotenv()

stripe.api_key = os.getenv("STRIPE_SECRET_KEY")


def create_checkout_session(
    order_id: int,
    amount: float,
    currency: str = "inr"
):
    session = stripe.checkout.Session.create(
        payment_method_types=["card"],
        line_items=[
            {
                "price_data": {
                    "currency": currency,
                    "product_data": {
                        "name": f"Order #{order_id}",
                    },
                    "unit_amount": int(amount * 100),
                },
                "quantity": 1,
            }
        ],
        mode="payment",
        success_url="http://localhost:5173/payment-success",
        cancel_url="http://localhost:5173/payment-cancel",
        metadata={
            "order_id": str(order_id)
        }
    )

    return session