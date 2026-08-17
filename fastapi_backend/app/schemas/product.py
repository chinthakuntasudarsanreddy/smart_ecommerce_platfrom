from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict


class ProductCreate(BaseModel):
    name: str
    description: str | None = None
    category: str
    price: Decimal
    stock: int = 0
    popularity: int = 0
    image_url: str | None = None


class ProductResponse(BaseModel):
    id: int
    name: str
    description: str | None
    category: str
    price: Decimal
    stock: int
    popularity: int
    image_url: str | None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)