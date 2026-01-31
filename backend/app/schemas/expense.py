from __future__ import annotations
from datetime import datetime
from decimal import Decimal
from typing import Optional, List

from pydantic import BaseModel, ConfigDict, Field

class ExpenseCreate(BaseModel):
    amount: Decimal = Field(..., gt=0, description="Amount in currency (positive)")
    category: str
    description: Optional[str] = None
    date: datetime
    client_id: Optional[str] = Field(None, description="Optional client-side UUID to make requests idempotent")

class ExpenseUpdate(BaseModel):
    amount: Optional[Decimal] = Field(None, gt=0, description="Amount in currency (positive)")
    category: Optional[str] = None
    description: Optional[str] = None
    date: Optional[datetime] = None

class ExpenseRead(BaseModel):
    id: int
    user_id: int
    amount: Decimal
    category: str
    description: Optional[str]
    date: datetime
    created_at: datetime
    client_id: Optional[str]

    model_config = ConfigDict(from_attributes=True)

class ExpenseListResponse(BaseModel):
    items: List[ExpenseRead]
    total: Decimal
    count: int
