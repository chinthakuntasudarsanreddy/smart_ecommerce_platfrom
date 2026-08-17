
from decimal import Decimal

from pydantic import BaseModel


class CartAddRequest(BaseModel):
    product_id: int
    quantity: int = 1


class CartUpdateRequest(BaseModel):
    product_id: int
    quantity: int


class CartRemoveRequest(BaseModel):
    product_id: int


class CartItemResponse(BaseModel):
    product_id: int
    product_name: str
    price: Decimal
    quantity: int
    item_total: Decimal


class CartResponse(BaseModel):
    items: list[CartItemResponse]
    cart_total: Decimal
    tax: Decimal
    grand_total: Decimal