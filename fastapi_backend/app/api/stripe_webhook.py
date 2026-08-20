import os
import stripe

from fastapi import APIRouter, Request, HTTPException
from sqlalchemy.orm import Session

from app.core.database import SessionLocal
from app.models.order import Order

router = APIRouter(
    prefix="/stripe",
    tags=["Stripe"]
)

stripe.api_key = os.getenv("STRIPE_SECRET_KEY")

STRIPE_WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET")


@router.post("/webhook")
async def stripe_webhook(request: Request):

    payload = await request.body()

    signature = request.headers.get("stripe-signature")

    try:
        event = stripe.Webhook.construct_event(
            payload,
            signature,
            STRIPE_WEBHOOK_SECRET
        )

    except ValueError:
        raise HTTPException(
            status_code=400,
            detail="Invalid payload"
        )

    except stripe.error.SignatureVerificationError:
        raise HTTPException(
            status_code=400,
            detail="Invalid Stripe signature"
        )

    if event["type"] == "checkout.session.completed":

        session = event["data"]["object"]

        order_id = session["metadata"].get("order_id")

        if order_id:

            db: Session = SessionLocal()

            try:
                order = db.query(Order).filter(
                    Order.id == int(order_id)
                ).first()

                if order:

                    order.payment_status = "paid"

                    db.commit()

            finally:
                db.close()

    return {"received": True}