import os

import stripe

from fastapi import (
    APIRouter,
    HTTPException,
    Depends
)

from pydantic import BaseModel
from typing import List

from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.order import Order
from app.models.payment import Payment
from app.models.user import User

from app.services.notification_service import create_notification


router = APIRouter()

stripe.api_key = os.getenv(
    "STRIPE_SECRET_KEY"
)


# =====================================================
# REQUEST MODELS
# =====================================================

class CartItem(BaseModel):

    product_id: int

    name: str

    price: float

    quantity: int


class CheckoutRequest(BaseModel):

    user_id: int

    items: List[CartItem]


# =====================================================
# CREATE CHECKOUT SESSION
# =====================================================

@router.post(
    "/payment/create-checkout-session"
)
def create_checkout_session(
    data: CheckoutRequest,
    db: Session = Depends(get_db)
):

    try:

        # ---------------------------------------------
        # Check user
        # ---------------------------------------------

        user = db.query(User).filter(
            User.id == data.user_id
        ).first()

        if not user:

            raise HTTPException(
                status_code=404,
                detail="User not found"
            )

        # ---------------------------------------------
        # Check cart
        # ---------------------------------------------

        if not data.items:

            raise HTTPException(
                status_code=400,
                detail="Cart is empty"
            )

        # ---------------------------------------------
        # Calculate total
        # ---------------------------------------------

        total = sum(
            item.price * item.quantity
            for item in data.items
        )

        # ---------------------------------------------
        # Create Order
        # ---------------------------------------------

        order = Order(

            user_id=data.user_id,

            total=total,

            payment_status="pending",

            order_status="pending"

        )

        db.add(order)

        db.commit()

        db.refresh(order)

        # ---------------------------------------------
        # Create Payment
        # ---------------------------------------------

        payment = Payment(

            order_id=order.id,

            amount=total,

            payment_method="stripe",

            status="pending"

        )

        db.add(payment)

        db.commit()

        db.refresh(payment)

        # ---------------------------------------------
        # Stripe line items
        # ---------------------------------------------

        line_items = []

        for item in data.items:

            line_items.append({

                "price_data": {

                    "currency": "inr",

                    "product_data": {

                        "name": item.name

                    },

                    "unit_amount": int(
                        item.price * 100
                    )

                },

                "quantity": item.quantity

            })

        # ---------------------------------------------
        # Create Stripe session
        # ---------------------------------------------

        session = stripe.checkout.Session.create(

            payment_method_types=["card"],

            line_items=line_items,

            mode="payment",

            metadata={

                "order_id": str(order.id),

                "payment_id": str(payment.id),

                "user_id": str(user.id)

            },

            success_url=(
                "http://localhost:5173/"
                "payment-success"
                "?session_id={CHECKOUT_SESSION_ID}"
            ),

            cancel_url=(
                "http://localhost:5173/cart"
            )

        )

        return {

            "checkout_url": session.url,

            "order_id": order.id,

            "payment_id": payment.id

        }

    except HTTPException:

        raise

    except Exception as e:

        db.rollback()

        raise HTTPException(

            status_code=500,

            detail=str(e)

        )


# =====================================================
# VERIFY STRIPE PAYMENT
# =====================================================

@router.get(
    "/payment/verify-session/{session_id}"
)
async def verify_payment_session(

    session_id: str,

    db: Session = Depends(get_db)

):

    try:

        # ---------------------------------------------
        # Get Stripe session
        # ---------------------------------------------

        session = stripe.checkout.Session.retrieve(
            session_id
        )

        # ---------------------------------------------
        # Get metadata
        # ---------------------------------------------

        metadata = session.metadata

        order_id = metadata.get(
            "order_id"
        )

        payment_id = metadata.get(
            "payment_id"
        )

        user_id = metadata.get(
            "user_id"
        )

        if not order_id:

            raise HTTPException(

                status_code=400,

                detail="Order ID missing from Stripe session"

            )

        # ---------------------------------------------
        # Get Order
        # ---------------------------------------------

        order = db.query(Order).filter(

            Order.id == int(order_id)

        ).first()

        if not order:

            raise HTTPException(

                status_code=404,

                detail="Order not found"

            )

        # ---------------------------------------------
        # Get Payment
        # ---------------------------------------------

        payment = None

        if payment_id:

            payment = db.query(
                Payment
            ).filter(

                Payment.id == int(payment_id)

            ).first()

        # =================================================
        # PAYMENT SUCCESS
        # =================================================

        if session.payment_status == "paid":

            # ---------------------------------------------
            # Update Order
            # ---------------------------------------------

            order.payment_status = "paid"
         
            db.commit()

            # ---------------------------------------------
            # Payment Failed Notification
            # ---------------------------------------------

            await create_notification(
                db=db,
                user_id=order.user_id,
                order_id=order.id,
                notification_type="payment_failed",
                message=(
                    f"Payment for order #{order.id} "
                    f"was unsuccessful."
                )
            )

            return {
                "success": False,
                "message": "Payment failed",
                "order_id": order.id
            }

    except HTTPException:
        raise

    except Exception as e:

        db.rollback()

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )
           