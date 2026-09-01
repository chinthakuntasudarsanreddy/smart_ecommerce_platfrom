from datetime import datetime
from pydantic import BaseModel, ConfigDict


class ReturnRequestCreate(BaseModel):
    reason: str
    comment: str | None = None


class ReturnRequestResponse(BaseModel):
    id: int
    order_id: int
    user_id: int
    reason: str
    comment: str | None
    status: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)