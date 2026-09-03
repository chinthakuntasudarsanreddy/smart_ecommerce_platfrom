
from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class OrderResponse(BaseModel):
    id: int
    user_id: int
    total: float
    order_status: str
    payment_status: str
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class ReturnRequestCreate(BaseModel):
    reason: str


class ReturnRequestResponse(BaseModel):
    id: int
    order_id: int
    user_id: int
    reason: str
    status: str
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True