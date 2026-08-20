import stripe

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.stripe_config import (
    STRIPE_CURRENCY,
    FRONTEND_URL
)

from app.models.product import Product
from app.models.order import Order
from app.models.order_item import OrderItem
from app.models.payment import Payment

from app.schemas.checkout import (
    CheckoutRequest,
    CheckoutResponse
)

router = APIRouter(
    prefix="/checkout",
    tags=["Checkout"]
)


@router.post(
    "",
    response_model=CheckoutResponse
)
def checkout(
    checkout_data: CheckoutRequest,
    db: Session = Depends(get_db)
):
    if not checkout_data.items:
        raise HTTPException(
            status_code=400,
            detail="Cart is empty"
        )

    total = 0
    order_items = []

    # 1. Validate cart items
    for item in checkout_data.items:

        if item.quantity <= 0:
            raise HTTPException(
                status_code=400,
                detail="Quantity must be greater than zero"
            )

        product = (
            db.query(Product)
            .filter(Product.id == item.product_id)
            .first()
        )

        if not product:
            raise HTTPException(
                status_code=404,
                detail=f"Product {item.product_id} not found"
            )

        # Check stock
        if hasattr(product, "stock"):
            if product.stock < item.quantity:
                raise HTTPException(
                    status_code=400,
                    detail=f"Insufficient stock for {product.name}"
                )

        item_total = product.price * item.quantity

        total += item_total

        order_items.append({
            "product": product,
            "quantity": item.quantity,
            "price": product.price
        })

    # 2. Create order
    #
    # Replace this with the authenticated user's ID
    # when your authentication dependency is connected.
    user_id = 1

    order = Order(
        user_id=user_id,
        total=total,
        payment_status="pending",
        order_status="pending"
    )

    db.add(order)
    db.flush()

    # Create order items
    for item in order_items:

        order_item = OrderItem(
            order_id=order.id,
            product_id=item["product"].id,
            quantity=item["quantity"],
            price=item["price"]
        )

        db.add(order_item)

    db.flush()

    # 3. Create Stripe Payment Intent
    payment_intent = stripe.PaymentIntent.create(
        amount=int(total * 100),
        currency=STRIPE_CURRENCY,
        metadata={
            "order_id": str(order.id)
        }
    )

    # 4. Create Stripe Checkout Session
    line_items = []

    for item in order_items:

        product = item["product"]

        line_items.append({
            "price_data": {
                "currency": STRIPE_CURRENCY,
                "product_data": {
                    "name": product.name
                },
                "unit_amount": int(
                    item["price"] * 100
                )
            },
            "quantity": item["quantity"]
        })

    checkout_session = stripe.checkout.Session.create(
        payment_method_types=["card"],
        line_items=line_items,
        mode="payment",

        success_url=(
            f"{FRONTEND_URL}/payment-success"
            f"?session_id={{CHECKOUT_SESSION_ID}}"
        ),

        cancel_url=(
            f"{FRONTEND_URL}/payment-cancelled"
        ),

        metadata={
            "order_id": str(order.id)
        }
    )

    # 5. Create payment record
    payment = Payment(
        order_id=order.id,
        amount=total,
        payment_method="stripe",
        transaction_id=payment_intent.id,
        status="pending"
    )

    db.add(payment)

    db.commit()
    db.refresh(order)
    db.refresh(payment)

    return CheckoutResponse(
        order_id=order.id,
        payment_id=payment.id,
        checkout_url=checkout_session.url,
        amount=total,
        currency=STRIPE_CURRENCY,
        status="pending"
    )