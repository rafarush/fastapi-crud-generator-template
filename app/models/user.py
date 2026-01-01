from app.models.abstractions.base_entity import BaseEntity
from sqlmodel import Field
from pydantic import EmailStr


class User(BaseEntity, table=True):
    email: EmailStr = Field(index=True, nullable=False, unique=True)
    password: str = Field(nullable=False)
    name: str = Field(nullable=False)
    last_name: str = Field(nullable=False)

