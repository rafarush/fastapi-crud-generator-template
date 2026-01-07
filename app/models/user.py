from typing import Optional, List

from app.models.abstractions.base_entity import BaseEntity
from sqlmodel import Field, Relationship
from pydantic import EmailStr

from app.models.auth.role import Role


class User(BaseEntity, table=True):
    email: EmailStr = Field(index=True, nullable=False, unique=True)
    password: str = Field(nullable=False)
    name: str = Field(nullable=False)
    last_name: str = Field(nullable=False)

    # Relación 1:1 con Role (un usuario un rol)
    role_id: Optional[int] = Field(default=None, foreign_key="role.id")
    role: Optional[Role] = Relationship(back_populates="users")

    @property
    def permissions(self) -> List[str]:
        """Permisos calculados del rol del usuario"""
        return [p.name for p in self.role.permissions] if self.role else []

