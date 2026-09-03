
import os

import stripe

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List

from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.order import Order
from app.models.order_item import OrderItem
from app.models.payment import Payment
from app.models.product import Product
from app.models.user import User

from app.services.notification_service import (
    payment_success_notification,
    payment_failed_notification,
)


router = APIRouter()

stripe.api_key = os.getenv("STRIPE_SECRET_KEY")


# ============================================================
# REQUEST MODELS
# ============================================================

class CartItem(BaseModel):
    product_id: int
    name: str
    price: float
    quantity: int


class CheckoutRequest(BaseModel):
    user_id: int
    items: List[CartItem]


# ============================================================
# CREATE CHECKOUT SESSION
# ============================================================

@router.post("/payment/create-checkout-session")
def create_checkout_session(
    data: CheckoutRequest,
    db: Session = Depends(get_db)
):
    try:

        # ----------------------------------------------------
        # Stripe configuration
        # ----------------------------------------------------

        if not stripe.api_key:
            raise HTTPException(
                status_code=500,
                detail="Stripe secret key is not configured"
            )

        # ----------------------------------------------------
        # Check user
        # ----------------------------------------------------

        user = (
            db.query(User)
            .filter(User.id == data.user_id)
            .first()
        )

        if not user:
            raise HTTPException(
                status_code=404,
                detail="User not found"
            )

        # ----------------------------------------------------
        # Check cart
        # ----------------------------------------------------

        if not data.items:
            raise HTTPException(
                status_code=400,
                detail="Cart is empty"
            )

        # ====================================================
        # VALIDATE PRODUCTS
        # ====================================================

        validated_items = []

        for item in data.items:

            if item.quantity <= 0:
                raise HTTPException(
                    status_code=400,
                    detail=(
                        f"Invalid quantity for product "
                        f"{item.product_id}"
                    )
                )

            product = (
                db.query(Product)
                .filter(Product.id == item.product_id)
                .first()
            )

            if not product:
                raise HTTPException(
                    status_code=404,
                    detail=(
                        f"Product {item.product_id} "
                        f"not found"
                    )
                )

            if product.stock < item.quantity:
                raise HTTPException(
                    status_code=400,
                    detail=(
                        f"Insufficient stock for "
                        f"{product.name}. "
                        f"Available: {product.stock}"
                    )
                )

            # Always use database price
            database_price = float(product.price)

            validated_items.append({
                "product": product,
                "quantity": item.quantity,
                "price": database_price,
            })

        # ====================================================
        # CALCULATE TOTAL
        # ====================================================

        total = sum(
            item["price"] * item["quantity"]
            for item in validated_items
        )

        if total <= 0:
            raise HTTPException(
                status_code=400,
                detail="Order total must be greater than zero"
            )

        # ====================================================
        # CREATE ORDER
        # ====================================================

        order = Order(
            user_id=data.user_id,
            total=total,
            payment_status="pending",
            order_status="pending"
        )

        db.add(order)
        db.flush()

        # ====================================================
        # CREATE ORDER ITEMS
        # ====================================================

        for item in validated_items:

            order_item = OrderItem(
                order_id=order.id,
                product_id=item["product"].id,
                quantity=item["quantity"],
                price=item["price"]
            )

            db.add(order_item)

        # ====================================================
        # CREATE PAYMENT RECORD
        # ====================================================

        payment = Payment(
            order_id=order.id,
            amount=total,
            payment_method="stripe",
            status="pending",
            transaction_id=None
        )

        db.add(payment)

        # Make sure order/payment are persisted
        db.commit()

        db.refresh(order)
        db.refresh(payment)

        # ====================================================
        # STRIPE LINE ITEMS
        # ====================================================

        line_items = []

        for item in validated_items:

            product = item["product"]

            line_items.append({

                "price_data": {

                    "currency": "inr",

                    "product_data": {
                        "name": product.name
                    },

                    "unit_amount": int(
                        round(item["price"] * 100)
                    )
                },

                "quantity": item["quantity"]
            })

        # ====================================================
        # CREATE STRIPE CHECKOUT SESSION
        # ====================================================

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
            "session_id": session.id,
            "order_id": order.id,
            "payment_id": payment.id
        }

    except HTTPException:
        db.rollback()
        raise

    except stripe.error.StripeError as e:

        db.rollback()

        raise HTTPException(
            status_code=400,
            detail=f"Stripe error: {str(e)}"
        )

    except Exception as e:

        db.rollback()

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


# ============================================================
# VERIFY STRIPE PAYMENT
# ============================================================

@router.get("/payment/verify-session/{session_id}")
async def verify_payment_session(
    session_id: str,
    db: Session = Depends(get_db)
):

    try:

        if not stripe.api_key:
            raise HTTPException(
                status_code=500,
                detail="Stripe secret key is not configured"
            )

        # ----------------------------------------------------
        # Retrieve Stripe session
        # ----------------------------------------------------

        session = stripe.checkout.Session.retrieve(
            session_id
        )

        # ----------------------------------------------------
        # Metadata
        # ----------------------------------------------------

        metadata = session.metadata

        order_id = metadata.get("order_id")
        payment_id = metadata.get("payment_id")

        if not order_id:
            raise HTTPException(
                status_code=400,
                detail="Order ID missing from Stripe session"
            )

        # ----------------------------------------------------
        # Get order
        # ----------------------------------------------------

        order = (
            db.query(Order)
            .filter(Order.id == int(order_id))
            .first()
        )

        if not order:
            raise HTTPException(
                status_code=404,
                detail="Order not found"
            )

        # ----------------------------------------------------
        # Get payment
        # ----------------------------------------------------

        payment = None

        if payment_id:

            payment = (
                db.query(Payment)
                .filter(Payment.id == int(payment_id))
                .first()
            )

        # ====================================================
        # PAYMENT SUCCESS
        # ====================================================

        if session.payment_status == "paid":

            # ------------------------------------------------
            # Stripe PaymentIntent
            # ------------------------------------------------

            payment_intent_id = session.payment_intent

            # ------------------------------------------------
            # SAFETY FIX:
            # If payment record is missing, create it.
            # ------------------------------------------------

            if not payment:

                payment = Payment(
                    order_id=order.id,
                    amount=float(order.total),
                    payment_method="stripe",
                    transaction_id=payment_intent_id,
                    status="paid"
                )

                db.add(payment)

            else:

                if payment_intent_id:
                    payment.transaction_id = (
                        payment_intent_id
                    )

                payment.status = "paid"

            # ------------------------------------------------
            # Update order
            # ------------------------------------------------

            order.payment_status = "paid"

            db.commit()

            db.refresh(payment)

            # ------------------------------------------------
            # Success notification
            # ------------------------------------------------

            try:

                await payment_success_notification(
                    db=db,
                    order_id=order.id,
                    user_id=order.user_id
                )

            except Exception:
                pass

            return {
                "success": True,
                "message": "Payment successful",
                "order_id": order.id,
                "payment_id": payment.id,
                "payment_status": payment.status,
                "transaction_id": payment.transaction_id
            }

        # ====================================================
        # PAYMENT NOT COMPLETED
        # ====================================================

        if payment:

            payment.status = "failed"

        order.payment_status = "failed"

        db.commit()

        # ----------------------------------------------------
        # Failed notification
        # ----------------------------------------------------

        try:

            await payment_failed_notification(
                db=db,
                order_id=order.id,
                user_id=order.user_id
            )

        except Exception:
            pass

        return {
            "success": False,
            "message": "Payment failed or was not completed",
            "order_id": order.id,
            "payment_status": order.payment_status
        }

    except HTTPException:
        raise

    except stripe.error.StripeError as e:

        db.rollback()

        raise HTTPException(
            status_code=400,
            detail=f"Stripe error: {str(e)}"
        )

    except Exception as e:

        db.rollback()

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )
