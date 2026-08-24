import os
from email.message import EmailMessage

import aiosmtplib


async def send_email(
    recipient: str,
    subject: str,
    body: str
):
    message = EmailMessage()

    message["From"] = os.getenv("EMAIL_FROM")
    message["To"] = recipient
    message["Subject"] = subject

    message.set_content(body)

    await aiosmtplib.send(
        message,
        hostname=os.getenv("SMTP_HOST"),
        port=int(os.getenv("SMTP_PORT", 587)),
        username=os.getenv("SMTP_USERNAME"),
        password=os.getenv("SMTP_PASSWORD"),
        start_tls=True
    )


# --------------------------------------------------
# ORDER CONFIRMATION EMAIL
# --------------------------------------------------

async def send_order_confirmation_email(
    recipient: str,
    order_id: int,
    total: float
):
    await send_email(
        recipient=recipient,
        subject=f"Order #{order_id} Confirmed",
        body=f"""
Hello,

Your order #{order_id} has been confirmed successfully.

Order Total: ₹{total}

Thank you for shopping with us.

Smart E-Commerce Platform
"""
    )


# --------------------------------------------------
# PAYMENT SUCCESS EMAIL
# --------------------------------------------------

async def send_payment_success_email(
    recipient: str,
    order_id: int,
    total: float
):
    await send_email(
        recipient=recipient,
        subject=f"Payment Successful - Order #{order_id}",
        body=f"""
Hello,

Your payment for order #{order_id} was successful.

Amount Paid: ₹{total}

Thank you for shopping with us.

Smart E-Commerce Platform
"""
    )


# --------------------------------------------------
# PAYMENT FAILURE EMAIL
# --------------------------------------------------

async def send_payment_failed_email(
    recipient: str,
    order_id: int
):
    await send_email(
        recipient=recipient,
        subject=f"Payment Failed - Order #{order_id}",
        body=f"""
Hello,

Unfortunately, the payment for order #{order_id} failed.

Please try again to complete your payment.

Smart E-Commerce Platform
"""
    )


# --------------------------------------------------
# ORDER SHIPPED EMAIL
# --------------------------------------------------

async def send_shipping_email(
    recipient: str,
    order_id: int
):
    await send_email(
        recipient=recipient,
        subject=f"Order #{order_id} Shipped",
        body=f"""
Hello,

Your order #{order_id} has been shipped successfully.

You will receive another notification when your order is delivered.

Thank you for shopping with us.

Smart E-Commerce Platform
"""
    )


# --------------------------------------------------
# ORDER DELIVERED EMAIL
# --------------------------------------------------

async def send_delivery_email(
    recipient: str,
    order_id: int
):
    await send_email(
        recipient=recipient,
        subject=f"Order #{order_id} Delivered",
        body=f"""
Hello,

Your order #{order_id} has been delivered successfully.

Thank you for shopping with us.

Smart E-Commerce Platform
"""
    )