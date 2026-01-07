from typing import Optional

from pydantic import Field

from app.models.abstractions.base_entity import BaseEntity


class RolePermission(BaseEntity, table=True):
    role_id: Optional[int] = Field(foreign_key="role.id", primary_key=True, nullable=False)
    permission_id: Optional[int] = Field(foreign_key="permission.id", primary_key=True, nullable=False)

