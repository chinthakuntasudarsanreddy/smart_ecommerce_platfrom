from pydantic import BaseModel
from typing import List


class CheckoutItem(BaseModel):
    product_id: int
    quantity: int


class CheckoutRequest(BaseModel):
    items: List[CheckoutItem]


class CheckoutResponse(BaseModel):
    order_id: int
    payment_id: int
    checkout_url: str
    amount: float
    currency: str
    status: str