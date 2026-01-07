from typing import Optional, List

from pydantic import Field
from sqlmodel import Relationship

from app.models.abstractions.base_entity import BaseEntity
from app.models.auth.permission import Permission
from app.models.auth.role_permission import RolePermission


class Role(BaseEntity, table=True):
    name: str = Field(unique=True, max_length=30, nullable=False)
    description: Optional[str] = Field(default_factory=lambda: None, nullable=True)

    permissions: List[Permission] = Relationship(
        back_populates="roles",
        link_model=RolePermission
    )


