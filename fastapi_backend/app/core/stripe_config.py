import os
import stripe

stripe.api_key = os.getenv("STRIPE_SECRET_KEY")

STRIPE_CURRENCY = os.getenv(
    "STRIPE_CURRENCY",
    "inr"
)

FRONTEND_URL = os.getenv(
    "FRONTEND_URL",
    "http://localhost:5173"
)