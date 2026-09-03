from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class RefundCreate(BaseModel):
    order_id: int
    amount: float
    refund_method: str = "original_payment"


class RefundStatusUpdate(BaseModel):
    status: str


class RefundResponse(BaseModel):
    id: int
    order_id: int
    user_id: int
    amount: float
    refund_method: str
    transaction_id: Optional[str] = None
    status: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)