from typing import Optional, List

from pydantic import Field
from sqlmodel import Relationship

from app.models.abstractions.base_entity import BaseEntity


class Permission(BaseEntity, table=True):
    name: str = Field(unique=True, nullable=False)
    description: Optional[str] = Field(default_factory=lambda: None, nullable=True)
