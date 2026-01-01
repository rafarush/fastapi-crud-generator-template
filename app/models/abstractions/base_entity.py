from datetime import datetime, timezone
from typing import Optional
import uuid

from sqlalchemy import null
from sqlmodel import Field, SQLModel


class BaseEntity(SQLModel):
    id: uuid.UUID = Field(default_factory=lambda: uuid.uuid4(), primary_key=True, nullable=False, index=True)
    date_created: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), nullable=False)
    date_updated: Optional[datetime] = Field(default_factory=lambda: None, nullable=True)
    is_deleted: Optional[bool] = Field(default_factory=lambda: False, nullable=True)
