
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class ReturnRequestInfo(BaseModel):
    id: int
    reason: str
    comment: str | None = None
    status: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class OrderResponse(BaseModel):
    id: int
    user_id: int
    status: str
    total_amount: float | None = None
    created_at: datetime
    delivered_at: datetime | None = None
    return_request: ReturnRequestInfo | None = None

    model_config = ConfigDict(from_attributes=True)
