import os
import stripe

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List

router = APIRouter()

stripe.api_key = os.getenv("STRIPE_SECRET_KEY")


class CartItem(BaseModel):
    product_id: int
    name: str
    price: float
    quantity: int


class CheckoutRequest(BaseModel):
    items: List[CartItem]


@router.post("/payment/create-checkout-session")
def create_checkout_session(data: CheckoutRequest):

    try:
        line_items = []

        for item in data.items:
            line_items.append({
                "price_data": {
                    "currency": "inr",
                    "product_data": {
                        "name": item.name,
                    },
                    "unit_amount": int(item.price * 100),
                },
                "quantity": item.quantity,
            })

        session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=line_items,
            mode="payment",
            success_url="http://localhost:5173/payment-success",
            cancel_url="http://localhost:5173/cart",
        )

        return {
            "checkout_url": session.url
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )